#!/usr/bin/env python3
"""Probe the EDUP trailing blob with bounded width and decoder tests.

The tool reads EDUP payloads read-only. It computes the blob length, entropy,
fixed-width record tests, common divisors and a fixed decoder set. It does not
print key values or payload bytes.
"""

from __future__ import annotations

import argparse
import bz2
import json
import lzma
import math
import os
import sys
import tempfile
import zlib

import edup_inspect

DEFAULT_MAX_BYTES = 2 * 1024 * 1024 * 1024
WIDTH_LIMIT = 64
MAX_OUTPUT = 4 * 1024 * 1024


def entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = [0] * 256
    for byte in data:
        counts[byte] += 1
    size = len(data)
    return -sum((count / size) * math.log2(count / size) for count in counts if count)


def bounded_zlib(data: bytes, wbits: int) -> tuple:
    stream = zlib.decompressobj(wbits)
    output = stream.decompress(data, MAX_OUTPUT)
    return output, bool(stream.eof and not stream.unused_data)


def bounded_bz2(data: bytes) -> tuple:
    stream = bz2.BZ2Decompressor()
    output = stream.decompress(data, max_length=MAX_OUTPUT)
    return output, bool(stream.eof)


def bounded_lzma(data: bytes, fmt: int) -> tuple:
    stream = lzma.LZMADecompressor(format=fmt)
    output = stream.decompress(data, max_length=MAX_OUTPUT)
    return output, bool(stream.eof)


def decoder_results(blob: bytes) -> dict:
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
        try:
            output, complete = function(blob)
            results[name] = {
                "ok": bool(output and complete),
                "output_nonempty": bool(output),
                "complete": complete,
                "output_length": len(output),
                "error": None,
            }
        except Exception as error:  # decoder errors are the expected negative case
            results[name] = {
                "ok": False,
                "output_nonempty": False,
                "complete": False,
                "output_length": 0,
                "error": type(error).__name__,
            }
    return results


def strict_stream_results(blob: bytes) -> dict:
    results = {}
    try:
        output, complete = bounded_zlib(blob, -15)
        results["deflate_raw"] = {
            "complete": complete,
            "output_length": len(output),
        }
    except Exception as error:
        results["deflate_raw"] = {"complete": False, "error": type(error).__name__}
    try:
        output, complete = bounded_lzma(blob, lzma.FORMAT_AUTO)
        results["lzma_auto"] = {
            "complete": complete,
            "output_length": len(output),
        }
    except Exception as error:
        results["lzma_auto"] = {"complete": False, "error": type(error).__name__}
    return results


def signature_results(blob: bytes) -> dict:
    return {
        "zlib": len(blob) >= 2 and blob[0] == 0x78,
        "gzip": blob[:2] == b"\x1f\x8b",
        "bz2": blob[:3] == b"BZh",
        "xz": blob[:6] == b"\xfd7zXZ\x00",
        "zstd": blob[:4] == b"\x28\xb5\x2f\xfd",
        "lz4": blob[:4] == b"\x04\x22\x4d\x18",
    }


def width_results(blob: bytes, count: int, distinct_second: int) -> list:
    results = []
    for width in range(1, WIDTH_LIMIT + 1):
        if len(blob) % width:
            continue
        records = len(blob) // width
        results.append(
            {
                "width": width,
                "records": records,
                "matches_entry_count": records == count,
                "matches_distinct_second": records == distinct_second,
            }
        )
    return results


def probe_document(data: bytes, label: str, store_keys: dict | None = None) -> dict:
    report = edup_inspect.inspect_bytes(data, label=label)
    blob = edup_inspect.blob_bytes(data)
    sixteen = [blob[index:index + 16] for index in range(0, len(blob) - 15, 16)]
    words_le = [
        int.from_bytes(blob[index:index + 8], "little")
        for index in range(0, len(blob) - 7, 8)
    ]
    words_be = [
        int.from_bytes(blob[index:index + 8], "big")
        for index in range(0, len(blob) - 7, 8)
    ]
    store_hits = store_hits_be = None
    if store_keys is not None:
        union = set()
        for keyset in store_keys.values():
            union |= keyset
        store_hits = sum(1 for value in words_le if value in union)
        store_hits_be = sum(1 for value in words_be if value in union)
    return {
        "label": label,
        "size": len(data),
        "count": report["count"],
        "distinct_second": report["stored_key_multiplicity"]["distinct"],
        "blob_length": len(blob),
        "entropy": round(entropy(blob), 3),
        "signatures": signature_results(blob),
        "decoders": decoder_results(blob),
        "strict_streams": strict_stream_results(blob),
        "sixteen_byte_records": len(sixteen),
        "sixteen_byte_distinct": len(set(sixteen)),
        "store_key_hits": store_hits,
        "store_key_hits_be": store_hits_be,
        "width_checks": width_results(
            blob, report["count"], report["stored_key_multiplicity"]["distinct"]
        ),
    }


def aggregate(reports: list) -> dict:
    lengths = [report["blob_length"] for report in reports]
    common = [
        width for width in range(1, WIDTH_LIMIT + 1)
        if lengths and all(length % width == 0 for length in lengths)
    ]
    width_matches = [
        {
            "blob_length": report["blob_length"],
            "width": check["width"],
            "records": check["records"],
            "matches_entry_count": check["matches_entry_count"],
            "matches_distinct_second": check["matches_distinct_second"],
        }
        for report in reports for check in report["width_checks"]
        if check["matches_entry_count"] or check["matches_distinct_second"]
    ]
    return {
        "samples": len(reports),
        "blob_lengths": lengths,
        "common_divisors_1_to_64": common,
        "common_divisors_above_16": [width for width in common if width > 16],
        "width_matches": width_matches,
        "any_entry_count_match": any(
            item["matches_entry_count"] for item in width_matches
        ),
        "any_distinct_second_match": any(
            item["matches_distinct_second"] for item in width_matches
        ),
        "decoder_any_ok": {
            name: any(report["decoders"][name]["ok"] for report in reports)
            for name in ("zlib", "deflate_raw", "gzip", "bz2", "xz", "lzma_alone")
        },
        "strict_any_complete": {
            name: any(report["strict_streams"][name]["complete"] for report in reports)
            for name in ("deflate_raw", "lzma_auto")
        },
        "signature_any": {
            name: any(report["signatures"][name] for report in reports)
            for name in ("zlib", "gzip", "bz2", "xz", "zstd", "lz4")
        },
        "store_key_hits": {
            "test_run": any(report["store_key_hits"] is not None for report in reports),
            "little_endian": sum(report["store_key_hits"] or 0 for report in reports),
            "big_endian": sum(report["store_key_hits_be"] or 0 for report in reports),
        },
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Probe the EDUP trailing blob.")
    parser.add_argument("samples", nargs="+", help="EDUP payload files")
    parser.add_argument("--store", action="append", default=[], help="RDS5/ETPF store file")
    parser.add_argument("--store-dir", action="append", default=[], help="directory of .ttpf stores")
    parser.add_argument("--json", action="store_true", help="print JSON instead of text")
    parser.add_argument("--output", help="write JSON atomically to this file")
    parser.add_argument(
        "--max-bytes", type=int, default=DEFAULT_MAX_BYTES,
        help="refuse an EDUP sample larger than this many bytes",
    )
    parser.add_argument(
        "--label-size", action="store_true",
        help="label samples by blob length instead of file path",
    )
    args = parser.parse_args(argv)

    reports = []
    try:
        store_keys = (
            edup_inspect.load_stores(args.store + args.store_dir)
            if (args.store or args.store_dir) else None
        )
        for path in args.samples:
            if os.path.getsize(path) > args.max_bytes:
                raise edup_inspect.EdError(f"{path}: larger than the {args.max_bytes}-byte cap")
            with open(path, "rb") as handle:
                data = handle.read()
            label = path
            if args.label_size:
                label = str(len(edup_inspect.blob_bytes(data)))
            reports.append(probe_document(data, label, store_keys))
    except (OSError, edup_inspect.EdError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    document = {"reports": reports, "summary": aggregate(reports)}
    rendered = json.dumps(document, indent=2) + "\n"
    if args.output:
        target = os.path.abspath(args.output)
        for path in args.samples:
            if os.path.abspath(path) == target:
                print("error: output path equals an input path", file=sys.stderr)
                return 1
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
        print(f"blob lengths: {summary['blob_lengths']}")
        print(f"common divisors 1..64: {summary['common_divisors_1_to_64']}")
        print(f"any entry-count match: {summary['any_entry_count_match']}")
        print(f"any distinct-second match: {summary['any_distinct_second_match']}")
        print(f"decoder any ok: {summary['decoder_any_ok']}")
        print(f"strict any complete: {summary['strict_any_complete']}")
        print(f"signature any: {summary['signature_any']}")
        print(f"store key hits: {summary['store_key_hits']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
