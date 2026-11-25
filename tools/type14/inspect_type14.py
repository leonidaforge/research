#!/usr/bin/env python3
"""Describe the internal tables of a decoded type 14 payload.

The tool reports offsets, sizes, counts and name lengths. It does not print the
payload text. Inputs are read-only and every path comes from the command line.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

HEADER_END = 0x2C
RECORD_HEADER_BYTES = 6
MIN_STRIDE = 8
MAX_STRIDE = 0x80


def u16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def nul_strings(data: bytes) -> list[bytes]:
    parts = data.split(b"\x00")
    if parts and not parts[-1]:
        parts.pop()
    return parts


def valid_name(name: bytes) -> bool:
    return bool(name) and all(0x20 <= byte < 0x7F for byte in name)


def record_candidates(data: bytes, count: int) -> list[dict]:
    """Find strides that make a ``count``-record table end at the payload end."""
    candidates = []
    if count <= 0:
        return candidates
    for stride in range(MIN_STRIDE, MAX_STRIDE + 1):
        start = len(data) - count * stride
        if start < 0 or start + RECORD_HEADER_BYTES > len(data):
            continue
        records = []
        for index in range(count):
            offset = start + index * stride
            name_length = u16(data, offset + 4)
            if not 1 <= name_length <= stride - RECORD_HEADER_BYTES:
                break
            name = data[offset + RECORD_HEADER_BYTES : offset + RECORD_HEADER_BYTES + name_length]
            padding = data[offset + RECORD_HEADER_BYTES + name_length : offset + stride]
            if not valid_name(name) or any(padding):
                break
            records.append(
                {
                    "offset": f"0x{offset:04x}",
                    "id": f"0x{u32(data, offset):08x}",
                    "name_length": name_length,
                }
            )
        if len(records) == count:
            candidates.append({"stride": stride, "start": start, "records": records})
    return candidates


def describe(data: bytes) -> dict:
    if len(data) < HEADER_END:
        raise ValueError(f"payload is shorter than the observed header: {len(data)} bytes")

    header_u16 = [
        {"offset": f"0x{offset:04x}", "value": u16(data, offset)}
        for offset in range(0, HEADER_END, 2)
    ]
    header_u32 = [
        {"offset": f"0x{offset:04x}", "value": u32(data, offset)}
        for offset in range(0, HEADER_END - 3, 4)
    ]

    string_offset = u16(data, 0x00)
    string_length = u16(data, 0x0C)
    count = u16(data, 0x18)
    string_end = string_offset + string_length
    string_table = {
        "offset": string_offset,
        "length": string_length,
        "count_field": count,
        "within_payload": string_end <= len(data),
        "string_count": None,
        "lengths": [],
        "encoded_length": None,
    }
    if string_table["within_payload"]:
        strings = nul_strings(data[string_offset:string_end])
        string_table["string_count"] = len(strings)
        string_table["lengths"] = [len(value) for value in strings]
        string_table["encoded_length"] = sum(len(value) + 1 for value in strings)

    candidates = record_candidates(data, count)
    return {
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "header_u16": header_u16,
        "header_u32": header_u32,
        "string_table": string_table,
        "record_table_candidates": candidates,
        "checks": {
            "string_offset_matches_fields_0x00_and_0x0E": u16(data, 0x00) == u16(data, 0x0E),
            "payload_size_matches_field_0x04": u32(data, 0x04) == len(data),
            "string_length_matches_field_0x0C": string_table["encoded_length"] == string_length,
            "string_count_matches_field_0x18": string_table["string_count"] == count,
            "single_record_stride_candidate": len(candidates) == 1,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("payload", type=Path, help="decoded type 14 payload")
    args = parser.parse_args()
    result = describe(args.payload.read_bytes())
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
