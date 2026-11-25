#!/usr/bin/env python3
"""Report the observed SGD5 header, block chain and data-region prefix.

The tool is a bounded structural sampler, not a format validator. It reads
each input read-only, never writes into an input directory, and prints only
header fields, sizes and counts.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import struct
import sys
from collections import Counter

MAGIC = b"SGD5"
HEADER_SIZE = 0x2C
BLOCK_HEADER_SIZE = 24
DEFAULT_MAX_BYTES = 2 * 1024 * 1024 * 1024
DEFAULT_MAX_BLOCKS = 100_000
DEFAULT_DATA_RECORDS = 1_000_000


class Sgd5Error(ValueError):
    pass


def _u32(data, offset):
    if offset + 4 > len(data):
        raise Sgd5Error(f"read past end at 0x{offset:x}")
    return struct.unpack_from("<I", data, offset)[0]


def _entry(data, offset):
    return struct.unpack_from("<IHH", data, offset)


def _printable_run(data, offset, window=256):
    """Return the longest printable run in a small window, capped."""
    best = 0
    current = 0
    for byte in data[offset:offset + window]:
        if 0x20 <= byte <= 0x7E:
            current += 1
            best = max(best, current)
        else:
            current = 0
    return best


def inspect_bytes(data: bytes, label: str = "<memory>", max_blocks: int = DEFAULT_MAX_BLOCKS,
                  max_data_records: int = DEFAULT_DATA_RECORDS) -> dict:
    size = len(data)
    if size < HEADER_SIZE:
        raise Sgd5Error(f"{label}: shorter than the {HEADER_SIZE}-byte header")
    if data[0:4] != MAGIC:
        raise Sgd5Error(f"{label}: magic is {data[0:4].hex(' ')}, not SGD5")

    header = {
        "field_04": _u32(data, 0x04),
        "field_08": _u32(data, 0x08),
        "declared_table_blocks": _u32(data, 0x0C),
        "first_block_length": _u32(data, 0x10),
    }
    declared = header["declared_table_blocks"]
    if declared > max_blocks:
        raise Sgd5Error(f"{label}: declared table block count {declared} exceeds the cap")

    blocks = []
    offset = 0x10
    for index in range(declared):
        if offset + 4 + BLOCK_HEADER_SIZE > size:
            raise Sgd5Error(f"{label}: table block {index} header at 0x{offset:x} is truncated")
        length = _u32(data, offset)
        if length < BLOCK_HEADER_SIZE:
            raise Sgd5Error(f"{label}: table block {index} length {length} is below the 24-byte header")
        payload_offset = offset + 4 + BLOCK_HEADER_SIZE
        payload_end = offset + 4 + length
        if payload_end > size:
            raise Sgd5Error(f"{label}: table block {index} ends past the file at 0x{payload_end:x}")
        zero = _u32(data, offset + 4 + 20)
        if zero != 0:
            raise Sgd5Error(f"{label}: table block {index} trailing word is 0x{zero:x}, not zero")
        payload_length = length - BLOCK_HEADER_SIZE
        if payload_length % 8 != 0:
            raise Sgd5Error(f"{label}: table block {index} payload {payload_length} is not a multiple of 8")

        entries = payload_length // 8
        sequential = True
        kinds = Counter()
        values = []
        for entry_index in range(entries):
            value, kind, stored_index = _entry(data, payload_offset + entry_index * 8)
            if stored_index != entry_index:
                sequential = False
            kinds[kind] += 1
            values.append(value)

        blocks.append({
            "index": index,
            "offset": offset,
            "length": length,
            "entries": entries,
            "descriptor": data[offset + 4:offset + 24].hex(),
            "indices_sequential": sequential,
            "kinds": {f"0x{kind:04x}": count for kind, count in sorted(kinds.items())},
            "entry_values": {
                "distinct": len(set(values)),
                "min": min(values) if values else None,
                "max": max(values) if values else None,
                "equal_to_file_size": sum(1 for value in values if value == size),
                "above_file_size": sum(1 for value in values if value > size),
            },
        })
        offset = payload_end

    if offset + 4 + BLOCK_HEADER_SIZE > size:
        raise Sgd5Error(f"{label}: the block after the table list is truncated at 0x{offset:x}")
    data_header_length = _u32(data, offset)
    data_header_zero = _u32(data, offset + 4 + 20)
    data_offset = offset + 4 + BLOCK_HEADER_SIZE
    data_header = {
        "offset": offset,
        "length": data_header_length,
        "descriptor": data[offset + 4:offset + 24].hex(),
        "trailing_zero": data_header_zero == 0,
        "remaining_file_bytes": size - data_offset,
        "length_equals_remaining_file_bytes": data_header_length == size - data_offset,
    }

    fixed_stride_records = 0
    record_offset = data_offset
    kinds = Counter()
    while record_offset + 24 <= size and fixed_stride_records < max_data_records:
        first = _u32(data, record_offset)
        second = _u32(data, record_offset + 4)
        if first != second:
            break
        kind, stored_index = struct.unpack_from("<HH", data, record_offset + 8)
        kinds[kind] += 1
        fixed_stride_records += 1
        record_offset += 24

    data_region = {
        "offset": data_offset,
        "fixed_stride_records": fixed_stride_records,
        "stride_break_offset": record_offset,
        "printable_run_near_break": _printable_run(data, record_offset),
        "record_kinds": {f"0x{kind:04x}": count for kind, count in sorted(kinds.items())},
    }

    return {
        "label": label,
        "size": size,
        "sha256": hashlib.sha256(data).hexdigest(),
        "magic": "SGD5",
        "header": header,
        "table_blocks": blocks,
        "table_block_count": len(blocks),
        "checks": {
            "declared_matches_parsed": len(blocks) == declared,
            "field_10_equals_first_block_length": blocks[0]["length"] == header["first_block_length"] if blocks else False,
            "all_table_indices_sequential": all(block["indices_sequential"] for block in blocks),
            "all_table_lengths_match_entries": all(block["length"] == BLOCK_HEADER_SIZE + 8 * block["entries"] for block in blocks),
        },
        "data_header": data_header,
        "data_region": data_region,
    }


def _print_text(report: dict, stream) -> None:
    print(f"sample: {report['label']}", file=stream)
    print(f"size: {report['size']} bytes", file=stream)
    print(f"sha256: {report['sha256']}", file=stream)
    header = report["header"]
    print(
        "header:"
        f" field_04=0x{header['field_04']:08x}"
        f" field_08=0x{header['field_08']:08x}"
        f" declared_table_blocks={header['declared_table_blocks']}"
        f" first_block_length={header['first_block_length']}",
        file=stream,
    )
    print(f"table blocks: {report['table_block_count']}", file=stream)
    for block in report["table_blocks"]:
        kinds = " ".join(f"{kind}:{count}" for kind, count in block["kinds"].items())
        values = block["entry_values"]
        maximum = f"0x{values['max']:08x}" if values["max"] is not None else "none"
        print(
            f"  [{block['index']}] offset=0x{block['offset']:x} length={block['length']}"
            f" entries={block['entries']} sequential={block['indices_sequential']}"
            f" values={values['distinct']} distinct, max={maximum}"
            f" kinds={kinds}",
            file=stream,
        )
    checks = report["checks"]
    print(
        "checks:"
        f" declared_matches_parsed={checks['declared_matches_parsed']}"
        f" field_10_equals_first_block_length={checks['field_10_equals_first_block_length']}"
        f" all_table_indices_sequential={checks['all_table_indices_sequential']}"
        f" all_table_lengths_match_entries={checks['all_table_lengths_match_entries']}",
        file=stream,
    )
    data_header = report["data_header"]
    print(
        f"block after tables: offset=0x{data_header['offset']:x}"
        f" length={data_header['length']}"
        f" length_equals_remaining_file_bytes={data_header['length_equals_remaining_file_bytes']}"
        f" trailing_zero={data_header['trailing_zero']}",
        file=stream,
    )
    data_region = report["data_region"]
    print(
        f"data region: offset=0x{data_region['offset']:x}"
        f" fixed_stride_records={data_region['fixed_stride_records']}"
        f" stride_break_offset=0x{data_region['stride_break_offset']:x}"
        f" printable_run_near_break={data_region['printable_run_near_break']}",
        file=stream,
    )


def _output_is_inside_input(output: str, inputs: list[str]) -> bool:
    output_dir = os.path.realpath(os.path.dirname(os.path.abspath(output)) or ".")
    for path in inputs:
        input_dir = os.path.realpath(os.path.dirname(os.path.abspath(path)) or ".")
        if output_dir == input_dir or output_dir.startswith(input_dir + os.sep):
            return True
    return False


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Report observed SGD5 structural fields.")
    parser.add_argument("samples", nargs="+", help="SGD5 payload files")
    parser.add_argument("--json", action="store_true", help="print JSON instead of text")
    parser.add_argument("--output", help="write output to this file instead of stdout")
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES,
                        help="refuse a sample larger than this many bytes")
    parser.add_argument("--max-blocks", type=int, default=DEFAULT_MAX_BLOCKS,
                        help="refuse a declared table block count above this")
    args = parser.parse_args(argv)

    if args.output and _output_is_inside_input(args.output, args.samples):
        parser.error("refusing to write output inside an input directory")

    reports = []
    try:
        for path in args.samples:
            if os.path.getsize(path) > args.max_bytes:
                raise Sgd5Error(f"{path}: larger than the {args.max_bytes}-byte cap")
            with open(path, "rb") as handle:
                data = handle.read()
            reports.append(inspect_bytes(data, label=path, max_blocks=args.max_blocks))
    except (OSError, Sgd5Error) as error:
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
