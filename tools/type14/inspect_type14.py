#!/usr/bin/env python3
"""Describe a decoded type 14 payload and verify its record identifiers.

The tool reports offsets, sizes, counts and name lengths. It does not print the
payload text. The verification mode prints only match counts, never names,
hashes or identifiers. Inputs are read-only and every path comes from the
command line.
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


def joaat(value: bytes) -> int:
    result = 0
    for byte in value:
        result = (result + byte) & 0xFFFFFFFF
        result = (result + (result << 10)) & 0xFFFFFFFF
        result ^= result >> 6
    result = (result + (result << 3)) & 0xFFFFFFFF
    result ^= result >> 11
    result = (result + (result << 15)) & 0xFFFFFFFF
    return result


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
                    "offset": offset,
                    "id": u32(data, offset),
                    "name": name,
                    "name_length": name_length,
                }
            )
        if len(records) == count:
            candidates.append({"stride": stride, "start": start, "records": records})
    return candidates


def _parse(data: bytes) -> dict:
    if len(data) < HEADER_END:
        raise ValueError(f"payload is shorter than the observed header: {len(data)} bytes")

    string_offset = u16(data, 0x00)
    string_length = u16(data, 0x0C)
    count = u16(data, 0x18)
    string_end = string_offset + string_length
    if string_end > len(data):
        raise ValueError("string table extends past the payload end")
    strings = nul_strings(data[string_offset:string_end])
    candidates = record_candidates(data, count)
    if len(candidates) != 1:
        raise ValueError(f"expected one record table candidate, found {len(candidates)}")
    return {
        "string_offset": string_offset,
        "string_length": string_length,
        "count": count,
        "strings": strings,
        "candidate": candidates[0],
        "candidates": candidates,
    }


def describe(data: bytes) -> dict:
    parsed = _parse(data)
    header_u16 = [
        {"offset": f"0x{offset:04x}", "value": u16(data, offset)}
        for offset in range(0, HEADER_END, 2)
    ]
    header_u32 = [
        {"offset": f"0x{offset:04x}", "value": u32(data, offset)}
        for offset in range(0, HEADER_END - 3, 4)
    ]
    strings = parsed["strings"]
    string_table = {
        "offset": parsed["string_offset"],
        "length": parsed["string_length"],
        "count_field": parsed["count"],
        "within_payload": True,
        "string_count": len(strings),
        "lengths": [len(value) for value in strings],
        "encoded_length": sum(len(value) + 1 for value in strings),
    }
    candidates = []
    for candidate in parsed["candidates"]:
        candidates.append(
            {
                "stride": candidate["stride"],
                "start": candidate["start"],
                "records": [
                    {
                        "offset": f"0x{record['offset']:04x}",
                        "name_length": record["name_length"],
                    }
                    for record in candidate["records"]
                ],
            }
        )
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
            "string_length_matches_field_0x0C": string_table["encoded_length"] == parsed["string_length"],
            "string_count_matches_field_0x18": string_table["string_count"] == parsed["count"],
            "single_record_stride_candidate": len(candidates) == 1,
        },
    }


def _hash_matches(identifier: int, value: bytes, lower: bool, terminator: bool,
                  big_endian: bool) -> bool:
    source = value.lower() if lower else value
    if terminator:
        source += b"\x00"
    digest = joaat(source)
    if big_endian:
        digest = struct.unpack("<I", struct.pack(">I", digest))[0]
    return digest == identifier


def _count_matches(records: list[dict], values: list[bytes], lower: bool,
                   terminator: bool, big_endian: bool) -> int:
    return sum(
        1
        for record, value in zip(records, values)
        if _hash_matches(record["id"], value, lower, terminator, big_endian)
    )


def verify_ids(data: bytes) -> dict:
    parsed = _parse(data)
    records = parsed["candidate"]["records"]
    strings = parsed["strings"]
    if len(records) != len(strings):
        raise ValueError("record and string-table counts differ")
    variants = {}
    for lower in (False, True):
        for terminator in (False, True):
            for big_endian in (False, True):
                key = (
                    ("folded_lower" if lower else "case_sensitive")
                    + ("_with_terminator" if terminator else "_no_terminator")
                    + ("_big_endian" if big_endian else "")
                )
                variants[key] = _count_matches(
                    records, strings, lower, terminator, big_endian
                )
    record_name_variants = {
        "folded_lower_no_terminator": _count_matches(
            records, [record["name"] for record in records], True, False, False
        ),
        "case_sensitive_no_terminator": _count_matches(
            records, [record["name"] for record in records], False, False, False
        ),
    }
    return {
        "records": len(records),
        "string_entries": len(strings),
        "matches": variants,
        "record_name_matches": record_name_variants,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("payload", type=Path, help="decoded type 14 payload")
    parser.add_argument(
        "--verify-ids",
        action="store_true",
        help="print identifier match counts only, never names, hashes or ids",
    )
    args = parser.parse_args()
    data = args.payload.read_bytes()
    if args.verify_ids:
        print(json.dumps(verify_ids(data), indent=2, sort_keys=True))
    else:
        print(json.dumps(describe(data), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
