#!/usr/bin/env python3
"""Probe PMAP PSCH values and block bodies with bounded width and stream tests.

The tool reads extracted PMAP payloads read-only. It reports counts, width
divisibility, compression signatures and a fixed decoder set. It does not print
value bytes or block contents.
"""

from __future__ import annotations

import argparse
import bz2
import hashlib
import json
import lzma
import os
import struct
import sys
import tempfile
import zlib

import psin_inspect

WIDTH_LIMIT = 64
MAX_OUTPUT = 4 * 1024 * 1024
DEFAULT_MAX_BYTES = 2 * 1024 * 1024 * 1024


def path_inside(target: str, directory: str) -> bool:
    target_path = os.path.realpath(os.path.abspath(target))
    directory_path = os.path.realpath(os.path.abspath(directory))
    return target_path == directory_path or target_path.startswith(directory_path + os.sep)


def section_body(data: bytes, tag: str) -> bytes:
    for section_tag, _, _, body in psin_inspect._walk_sections(data):
        if section_tag == tag:
            return body
    raise psin_inspect.PsinError(f"no {tag} section")


def psch_values(data: bytes) -> list:
    return psch_values_body(section_body(data, "PSCH"))


def psch_values_body(body: bytes) -> list:
    if len(body) < 4:
        raise psin_inspect.PsinError("PSCH body is shorter than 4 bytes")
    count = struct.unpack_from(">I", body, 0)[0]
    table = 4 + 8 * count
    if table + 8 > len(body):
        raise psin_inspect.PsinError("PSCH table is truncated")
    offsets = [struct.unpack_from(">I", body, 8 + 8 * index)[0] for index in range(count)]
    values = []
    for index, offset in enumerate(offsets):
        end = offsets[index + 1] if index + 1 < count else len(body)
        values.append(body[offset:end])
    return values


def pmap_blocks(data: bytes) -> list:
    report = psin_inspect.inspect_bytes(data)
    if report["family"] != "PMAP":
        raise psin_inspect.PsinError("not a PMAP payload")
    blocks = []
    for block in report["family_data"]["blocks"]:
        start = block["offset"]
        blocks.append(data[start:start + block["length"]])
    return blocks


def bounded_zlib(data: bytes, wbits: int) -> tuple:
    stream = zlib.decompressobj(wbits)
    output = stream.decompress(data, MAX_OUTPUT)
    complete = bool(stream.eof and not stream.unused_data)
    return output, complete


def bounded_bz2(data: bytes) -> tuple:
    stream = bz2.BZ2Decompressor()
    output = stream.decompress(data, max_length=MAX_OUTPUT)
    return output, bool(stream.eof)


def bounded_lzma(data: bytes, fmt: int) -> tuple:
    stream = lzma.LZMADecompressor(format=fmt)
    output = stream.decompress(data, max_length=MAX_OUTPUT)
    return output, bool(stream.eof)


def decode_results(chunks: list) -> dict:
    decoders = {
        "zlib": lambda value: bounded_zlib(value, 15),
        "deflate_raw": lambda value: bounded_zlib(value, -15),
        "gzip": lambda value: bounded_zlib(value, 31),
        "bz2": bounded_bz2,
        "xz": lambda value: bounded_lzma(value, lzma.FORMAT_XZ),
        "lzma_alone": lambda value: bounded_lzma(value, lzma.FORMAT_ALONE),
    }
    results = {}
    for name, function in decoders.items():
        ok = 0
        for chunk in chunks:
            try:
                output, complete = function(chunk)
                if complete and output:
                    ok += 1
            except Exception:
                pass
        results[name] = ok
    return results


def strict_results(chunks: list) -> dict:
    deflate = 0
    lzma_complete = 0
    for chunk in chunks:
        try:
            output, complete = bounded_zlib(chunk, -15)
            if complete and output:
                deflate += 1
        except Exception:
            pass
        try:
            output, complete = bounded_lzma(chunk, lzma.FORMAT_AUTO)
            if complete and output:
                lzma_complete += 1
        except Exception:
            pass
    return {"deflate_raw_complete": deflate, "lzma_auto_complete": lzma_complete}


def signatures(chunks: list) -> dict:
    counts = {
        "zlib": 0,
        "gzip": 0,
        "bz2": 0,
        "xz": 0,
        "zstd": 0,
        "lz4": 0,
    }
    for chunk in chunks:
        counts["zlib"] += int(len(chunk) >= 2 and chunk[0] == 0x78)
        counts["gzip"] += int(chunk[:2] == b"\x1f\x8b")
        counts["bz2"] += int(chunk[:3] == b"BZh")
        counts["xz"] += int(chunk[:6] == b"\xfd7zXZ\x00")
        counts["zstd"] += int(chunk[:4] == b"\x28\xb5\x2f\xfd")
        counts["lz4"] += int(chunk[:4] == b"\x04\x22\x4d\x18")
    return counts


def width_summary(chunks: list) -> dict:
    lengths = [len(chunk) for chunk in chunks]
    divisors = [
        width for width in range(1, WIDTH_LIMIT + 1)
        if lengths and all(length % width == 0 for length in lengths)
    ]
    return {
        "count": len(chunks),
        "length_min": min(lengths) if lengths else None,
        "length_max": max(lengths) if lengths else None,
        "common_divisors_1_to_64": divisors,
        "divisors_above_8": [width for width in divisors if width > 8],
    }


def probe(data: bytes, label: str) -> dict:
    values = psch_values(data)
    blocks = pmap_blocks(data)
    return {
        "label": label,
        "values": {
            "lengths": [len(value) for value in values],
            "width": width_summary(values),
            "signatures": signatures(values),
            "decoders": decode_results(values),
            "strict": strict_results(values),
        },
        "blocks": {
            "lengths": [len(block) for block in blocks],
            "width": width_summary(blocks),
            "signatures": signatures(blocks),
            "decoders": decode_results(blocks),
            "strict": strict_results(blocks),
        },
    }


def aggregate(reports: list) -> dict:
    value_lengths = [length for report in reports for length in report["values"]["lengths"]]
    block_lengths = [length for report in reports for length in report["blocks"]["lengths"]]
    return {
        "samples": len(reports),
        "value_counts": [report["values"]["width"]["count"] for report in reports],
        "block_counts": [report["blocks"]["width"]["count"] for report in reports],
        "value_common_divisors_1_to_64": [
            width for width in range(1, WIDTH_LIMIT + 1)
            if value_lengths and all(length % width == 0 for length in value_lengths)
        ],
        "block_common_divisors_1_to_64": [
            width for width in range(1, WIDTH_LIMIT + 1)
            if block_lengths and all(length % width == 0 for length in block_lengths)
        ],
        "value_length_min": min(value_lengths) if value_lengths else None,
        "value_length_max": max(value_lengths) if value_lengths else None,
        "value_decoder_any": {
            name: sum(report["values"]["decoders"][name] for report in reports)
            for name in ("zlib", "deflate_raw", "gzip", "bz2", "xz", "lzma_alone")
        },
        "block_decoder_any": {
            name: sum(report["blocks"]["decoders"][name] for report in reports)
            for name in ("zlib", "deflate_raw", "gzip", "bz2", "xz", "lzma_alone")
        },
        "value_strict_any": {
            name: sum(report["values"]["strict"][name] for report in reports)
            for name in ("deflate_raw_complete", "lzma_auto_complete")
        },
        "block_strict_any": {
            name: sum(report["blocks"]["strict"][name] for report in reports)
            for name in ("deflate_raw_complete", "lzma_auto_complete")
        },
        "value_signature_any": {
            name: sum(report["values"]["signatures"][name] for report in reports)
            for name in ("zlib", "gzip", "bz2", "xz", "zstd", "lz4")
        },
        "block_signature_any": {
            name: sum(report["blocks"]["signatures"][name] for report in reports)
            for name in ("zlib", "gzip", "bz2", "xz", "zstd", "lz4")
        },
    }


def load_directory(directory: str, max_bytes: int = DEFAULT_MAX_BYTES) -> list:
    reports = []
    seen = set()
    for name in sorted(os.listdir(directory)):
        path = os.path.join(directory, name)
        if not os.path.isfile(path) or not name.lower().endswith(".bin"):
            continue
        if os.path.getsize(path) > max_bytes:
            raise psin_inspect.PsinError(f"{name}: larger than the {max_bytes}-byte cap")
        with open(path, "rb") as handle:
            data = handle.read()
        if data[:4] != b"PSIN":
            continue
        digest = hashlib.sha256(data).digest()
        if digest in seen:
            continue
        seen.add(digest)
        try:
            report = psin_inspect.inspect_bytes(data)
        except psin_inspect.PsinError:
            continue
        if report["family"] != "PMAP":
            continue
        reports.append(probe(data, name[:-4]))
    return reports


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Probe PMAP values and blocks.")
    parser.add_argument("--samples", required=True, help="directory of extracted .bin payloads")
    parser.add_argument("--json", action="store_true", help="print JSON")
    parser.add_argument("--summary-only", action="store_true", help="omit per-payload reports")
    parser.add_argument("--output", help="write JSON atomically to this file")
    parser.add_argument(
        "--max-bytes", type=int, default=DEFAULT_MAX_BYTES,
        help="refuse a sample larger than this many bytes",
    )
    args = parser.parse_args(argv)

    if args.output and path_inside(args.output, args.samples):
        print("error: output path is inside the sample directory", file=sys.stderr)
        return 1
    try:
        reports = load_directory(args.samples, args.max_bytes)
    except (OSError, psin_inspect.PsinError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    if not reports:
        print("error: no PMAP payloads found", file=sys.stderr)
        return 1
    document = {"reports": reports, "summary": aggregate(reports)}
    if args.summary_only:
        document = {"summary": document["summary"]}
    rendered = json.dumps(document, indent=2) + "\n"
    if args.output:
        target = os.path.abspath(args.output)
        directory = os.path.dirname(target) or "."
        handle = tempfile.NamedTemporaryFile("w", delete=False, dir=directory, encoding="utf-8")
        try:
            handle.write(rendered)
            handle.close()
            os.replace(handle.name, target)
        finally:
            if not handle.closed:
                handle.close()
            if os.path.exists(handle.name):
                os.remove(handle.name)
        return 0
    if args.json:
        sys.stdout.write(rendered)
    else:
        summary = document["summary"]
        print(f"samples: {summary['samples']}")
        print(f"value counts: {summary['value_counts']}")
        print(f"block counts: {summary['block_counts']}")
        print(f"value decoder hits: {summary['value_decoder_any']}")
        print(f"block decoder hits: {summary['block_decoder_any']}")
        print(f"value strict: {summary['value_strict_any']}")
        print(f"block strict: {summary['block_strict_any']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
