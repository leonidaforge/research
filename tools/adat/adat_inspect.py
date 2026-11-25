#!/usr/bin/env python3
"""Inspect the ADAT header and its 8-byte chunk records.

The tool reads each input read-only, refuses to write output inside an input
directory, and reports offsets, counts, type bytes and sizes. It does not print
payload text and assigns no codec or stream semantics.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import struct
import sys

MAGIC = b"ADAT"
VERSION = 1
VARIANTS = {0xFF02, 0xFF21, 0xFF25, 0xFF61}
RECORD_BYTES = 8
DEFAULT_MAX_BYTES = 64 * 1024 * 1024


class AdatError(ValueError):
    pass


def _u16(data, offset, limit=None):
    boundary = len(data) if limit is None else limit
    if offset + 2 > boundary:
        raise AdatError(f"read past end at 0x{offset:x}")
    return struct.unpack_from("<H", data, offset)[0]


def _u32(data, offset, limit=None):
    boundary = len(data) if limit is None else limit
    if offset + 4 > boundary:
        raise AdatError(f"read past end at 0x{offset:x}")
    return struct.unpack_from("<I", data, offset)[0]


def _u64(data, offset):
    if offset + 8 > len(data):
        raise AdatError(f"read past end at 0x{offset:x}")
    return struct.unpack_from("<Q", data, offset)[0]


def record_start(variant: int, streams: int) -> int:
    """Return the first record offset for an observed variant."""
    if variant == 0xFF02:
        return 0x10 + 4 * streams
    if variant == 0xFF61:
        return 0x18 + 10 * streams
    return 0x14 + 10 * streams


def _record_type(value: int) -> int:
    return (value >> 56) & 0xFF


def _record_size(value: int) -> int:
    return (value >> 28) & 0xFFFFFFF


def _record_offset(value: int) -> int:
    return value & 0xFFFFFFF


def inspect_bytes(data: bytes, label: str = "<memory>") -> dict:
    size = len(data)
    if size < 0x10:
        raise AdatError(f"{label}: shorter than the ADAT header")
    if data[0:4] != MAGIC:
        raise AdatError(f"{label}: magic is {data[0:4].hex(' ')}, not ADAT")

    flags = _u32(data, 0x04)
    version = flags & 0xFFFF
    variant = flags >> 16
    if version != VERSION:
        raise AdatError(f"{label}: version is {version}, not {VERSION}")
    if variant not in VARIANTS:
        raise AdatError(f"{label}: variant 0x{variant:04x} is not in the observed set")
    streams = _u32(data, 0x08)
    data_offset = _u32(data, 0x0C)
    if streams == 0:
        raise AdatError(f"{label}: stream count is zero")
    if data_offset > size:
        raise AdatError(f"{label}: data offset {data_offset} is past the payload end")
    if data_offset < 0x10:
        raise AdatError(f"{label}: data offset {data_offset} overlaps the header")

    per_stream_start = 0x14 if variant == 0xFF61 else 0x10
    if per_stream_start + 2 * streams > data_offset:
        raise AdatError(f"{label}: the per-stream table crosses the data offset")

    start = record_start(variant, streams)
    if start > data_offset:
        raise AdatError(f"{label}: the record run starts past the data offset")
    remainder = (data_offset - start) % RECORD_BYTES
    if remainder:
        raise AdatError(
            f"{label}: record run length {data_offset - start} leaves a"
            f" {remainder}-byte remainder"
        )

    if start == data_offset:
        raise AdatError(f"{label}: record run is empty")

    records = []
    position = start
    while position < data_offset:
        value = _u64(data, position)
        record_type = _record_type(value)
        record_size = _record_size(value)
        record_offset = _record_offset(value)
        if record_size == 0:
            raise AdatError(f"{label}: record at 0x{position:x} has size zero")
        if record_offset < data_offset:
            raise AdatError(
                f"{label}: record at 0x{position:x} points before the data offset"
            )
        if record_offset + record_size > size:
            raise AdatError(
                f"{label}: record at 0x{position:x} overruns the payload"
                f" (0x{record_offset:x} + {record_size} > {size})"
            )
        records.append(
            {
                "offset": position,
                "type": record_type,
                "size": record_size,
                "data_offset": record_offset,
            }
        )
        position += RECORD_BYTES

    type_counts = {}
    for record in records:
        key = f"0x{record['type']:02x}"
        type_counts[key] = type_counts.get(key, 0) + 1

    report = {
        "label": label,
        "size": size,
        "sha256": hashlib.sha256(data).hexdigest(),
        "header": {
            "magic": "ADAT",
            "flags": f"0x{flags:08x}",
            "version": version,
            "variant": f"0x{variant:04x}",
            "streams": streams,
            "data_offset": data_offset,
        },
        "layout": {
            "per_stream_start": per_stream_start,
            "record_start": start,
            "record_count": len(records),
            "record_bytes": len(records) * RECORD_BYTES,
            "remainder": remainder,
        },
        "records": {
            "types": type_counts,
            "first_type": f"0x{records[0]['type']:02x}" if records else None,
            "last_type": f"0x{records[-1]['type']:02x}" if records else None,
            "min_size": min((record["size"] for record in records), default=None),
            "max_size": max((record["size"] for record in records), default=None),
        },
        "checks": {
            "flags_packing": flags == ((variant << 16) | VERSION),
            "record_run_ends_at_data_offset": start + len(records) * RECORD_BYTES == data_offset,
            "nonzero_sizes": all(record["size"] for record in records),
            "extents_within_payload": all(
                record["data_offset"] + record["size"] <= size for record in records
            ),
            "last_record_type_matches_prefix_byte": bool(records)
            and records[-1]["type"] == data[data_offset - 1],
        },
    }

    if variant == 0xFF02:
        chunk_values = [_u32(data, 0x10 + 4 * index) for index in range(streams)]
        chunk_counts = [value >> 29 for value in chunk_values]
        expected = 0x10 + 4 * streams + 8 * sum(chunk_counts)
        if expected != data_offset:
            raise AdatError(
                f"{label}: FF02 data offset is {data_offset}, the chunk formula gives {expected}"
            )
        report["ff02"] = {
            "chunk_counts": chunk_counts,
            "chunk_sum": sum(chunk_counts),
            "expected_data_offset": expected,
            "formula_matches": expected == data_offset,
            "uniform_chunk_count": len(set(chunk_counts)) == 1,
        }
    elif variant == 0xFF61:
        report["ff61"] = {"second_offset": _u32(data, 0x10)}

    return report


def _print_text(report: dict, stream) -> None:
    header = report["header"]
    layout = report["layout"]
    records = report["records"]
    print(f"sample: {report['label']}", file=stream)
    print(f"size: {report['size']} bytes", file=stream)
    print(f"sha256: {report['sha256']}", file=stream)
    print(
        f"header: flags={header['flags']} version={header['version']}"
        f" variant={header['variant']} streams={header['streams']}"
        f" data_offset={header['data_offset']}",
        file=stream,
    )
    print(
        f"records: start=0x{layout['record_start']:x}"
        f" count={layout['record_count']} bytes={layout['record_bytes']}"
        f" remainder={layout['remainder']}"
        f" first_type={records['first_type']} last_type={records['last_type']}"
        f" types={records['types']}",
        file=stream,
    )
    if "ff02" in report:
        section = report["ff02"]
        print(
            f"ff02: chunk_sum={section['chunk_sum']}"
            f" expected_data_offset={section['expected_data_offset']}"
            f" formula_matches={section['formula_matches']}"
            f" uniform_chunk_count={section['uniform_chunk_count']}",
            file=stream,
        )
    if "ff61" in report:
        print(f"ff61: second_offset={report['ff61']['second_offset']}", file=stream)


def _output_is_inside_input(output: str, inputs: list[str]) -> bool:
    output_dir = os.path.realpath(os.path.dirname(os.path.abspath(output)) or ".")
    for path in inputs:
        input_dir = os.path.realpath(os.path.dirname(os.path.abspath(path)) or ".")
        if output_dir == input_dir or output_dir.startswith(input_dir + os.sep):
            return True
    return False


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Inspect an ADAT header and chunk records.")
    parser.add_argument("samples", nargs="+", help="stored ADAT payload files")
    parser.add_argument("--json", action="store_true", help="print JSON instead of text")
    parser.add_argument("--output", help="write output to this file instead of stdout")
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES,
                        help="refuse a sample larger than this many bytes")
    args = parser.parse_args(argv)

    if args.output and _output_is_inside_input(args.output, args.samples):
        parser.error("refusing to write output inside an input directory")

    reports = []
    try:
        for path in args.samples:
            label = os.path.basename(path)
            if os.path.getsize(path) > args.max_bytes:
                raise AdatError(f"{label}: larger than the {args.max_bytes}-byte cap")
            with open(path, "rb") as handle:
                data = handle.read()
            reports.append(inspect_bytes(data, label=label))
    except (OSError, AdatError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    if args.json:
        text = json.dumps(reports, indent=2) + "\n"
    else:
        buffer = io.StringIO()
        for report in reports:
            _print_text(report, buffer)
            buffer.write("\n")
        text = buffer.getvalue()

    if args.output:
        with open(args.output, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
