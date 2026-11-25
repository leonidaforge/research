#!/usr/bin/env python3
"""Describe the structure of a line-oriented ASCII payload.

The tool reports offsets, lengths and character classes. It does not print the
payload text. Inputs are read-only and every path comes from the command line.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

CRLF = b"\r\n"
SPACE = b" "
KEY_RE = re.compile(rb"[A-Z_]+")
VALUE_RE = re.compile(rb"[0-9]+(?:\.[0-9]+)?")


def is_text_byte(byte: int) -> bool:
    return 0x20 <= byte <= 0x7E or byte in (0x0A, 0x0D)


def split_records(data: bytes) -> list[tuple[int, bytes, bool]]:
    """Split on CRLF. A trailing CRLF does not create an empty record."""
    records: list[tuple[int, bytes, bool]] = []
    start = 0
    while start < len(data):
        end = data.find(CRLF, start)
        if end < 0:
            records.append((start, data[start:], False))
            break
        records.append((start, data[start:end], True))
        start = end + len(CRLF)
    return records


def describe_record(offset: int, content: bytes, terminated: bool) -> dict:
    parts = content.split(SPACE)
    record = {
        "offset": f"0x{offset:04x}",
        "content_length": len(content),
        "terminated_with_crlf": terminated,
        "empty": not content,
        "field_count": 0 if not content else len(parts),
        "leading_or_trailing_space": bool(content) and (
            content.startswith(SPACE) or content.endswith(SPACE)
        ),
    }
    if not content:
        return record

    record["contains_tab"] = 0x09 in content
    if len(parts) != 2:
        return record

    key, value = parts
    record.update(
        {
            "key_length": len(key),
            "value_length": len(value),
            "key_segment_lengths": [len(segment) for segment in key.split(b"_")],
            "key_is_uppercase_or_underscore": bool(KEY_RE.fullmatch(key)),
            "value_is_decimal": bool(VALUE_RE.fullmatch(value)),
            "key_starts_with_label_segment": key.startswith(b"PTFX_"),
        }
    )
    return record


def describe(data: bytes) -> dict:
    if not data:
        raise ValueError("payload is empty")

    records = split_records(data)
    described = [describe_record(*record) for record in records]
    non_empty = [record for record in described if not record["empty"]]
    crlf_count = data.count(CRLF)
    lf_count = data.count(b"\n")
    cr_count = data.count(b"\r")
    nul_count = data.count(b"\x00")
    non_text_offsets = [
        offset for offset, byte in enumerate(data) if not is_text_byte(byte)
    ]
    final_blank_line = bool(records) and records[-1][2] and not records[-1][1]

    checks = {
        "all_bytes_printable_or_crlf": not non_text_offsets,
        "no_nul": nul_count == 0,
        "starts_with_ptfx_label": data.startswith(b"PTFX"),
        "label_is_first_key_segment": data.startswith(b"PTFX_"),
        "crlf_only_line_endings": crlf_count > 0
        and lf_count == crlf_count
        and cr_count == crlf_count,
        "final_blank_line": final_blank_line,
        "every_non_empty_record_has_two_fields": bool(non_empty)
        and all(record["field_count"] == 2 for record in non_empty),
        "every_key_is_uppercase_or_underscore": bool(non_empty)
        and all(
            record.get("key_is_uppercase_or_underscore", False) for record in non_empty
        ),
        "every_value_is_decimal": bool(non_empty)
        and all(record.get("value_is_decimal", False) for record in non_empty),
    }

    return {
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "byte_counts": {
            "cr": cr_count,
            "lf": lf_count,
            "crlf": crlf_count,
            "nul": nul_count,
            "non_text": len(non_text_offsets),
        },
        "first_bytes": data[:4].hex(" "),
        "non_text_offsets": [f"0x{offset:04x}" for offset in non_text_offsets[:8]],
        "document": {
            "record_count": len(records),
            "non_empty_record_count": len(non_empty),
            "blank_record_count": sum(1 for record in described if record["empty"]),
            "final_blank_line": final_blank_line,
            "field_delimiter": "0x20" if checks["every_non_empty_record_has_two_fields"] else None,
        },
        "records": described,
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("payload", type=Path, help="decoded payload to describe")
    args = parser.parse_args()
    result = describe(args.payload.read_bytes())
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
