#!/usr/bin/env python3
"""Structural inspector for RBF0 payloads.

The inspector reports bounds, tags, widths and terminators. It does not print
field names or text values. Names are identified by length and SHA-256 prefix.

Standard library only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from dataclasses import dataclass, field
from typing import Optional

MAGIC = b"RBF0"
HEADER_MARKER = 0xFFFB
ROOT_TERMINATOR = 0xFFFF
STRING_VALUE_TAG = 0xFFFD
FIXED8_FIELD = 0x1006
OBJECT_FIELD_IDS = frozenset((0x0001, 0x0002))
STRING_FIELD_IDS = frozenset(range(0x0004, 0x000B))
ATTRIBUTE_FIELD_IDS = frozenset((0x6003, 0x6004))


class ParseError(Exception):
    def __init__(self, offset: int, message: str) -> None:
        super().__init__(f"0x{offset:08X}: {message}")
        self.offset = offset
        self.message = message


@dataclass
class Report:
    size: int = 0
    header: dict = field(default_factory=dict)
    counts: dict = field(default_factory=dict)
    unsupported: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    definitions: list = field(default_factory=list)


class Reader:
    def __init__(self, data: bytes) -> None:
        self.data = data
        self.pos = 0

    def take(self, count: int, what: str) -> bytes:
        end = self.pos + count
        if count < 0 or end > len(self.data):
            raise ParseError(self.pos, f"truncated {what}: need {count} bytes, have {len(self.data) - self.pos}")
        chunk = self.data[self.pos:end]
        self.pos = end
        return chunk

    def u16(self, what: str) -> int:
        return struct.unpack("<H", self.take(2, what))[0]

    def u32(self, what: str) -> int:
        return struct.unpack("<I", self.take(4, what))[0]

    def expect_u16(self, value: int, what: str) -> None:
        offset = self.pos
        actual = self.u16(what)
        if actual != value:
            raise ParseError(offset, f"expected {what} 0x{value:04X}, found 0x{actual:04X}")


class Inspector:
    def __init__(self, data: bytes) -> None:
        self.reader = Reader(data)
        self.report = Report(size=len(data))
        self.field_names: dict[int, bytes] = {}
        self.report.counts = {
            "objects": 0,
            "fields": 0,
            "attributes": 0,
            "string_fields": 0,
            "fixed8_fields": 0,
            "object_fields": 0,
            "string_values": 0,
        }

    def run(self) -> Report:
        self.read_header()
        self.parse_object("root")
        if self.reader.pos != len(self.reader.data):
            raise ParseError(self.reader.pos, f"trailing {len(self.reader.data) - self.reader.pos} bytes")
        return self.report

    def read_header(self) -> None:
        magic = self.reader.take(4, "magic")
        if magic != MAGIC:
            raise ParseError(0, f"bad magic {magic!r}")
        marker = self.reader.u16("header marker")
        value = self.reader.u32("header value")
        name_len = self.reader.u16("root name length")
        name = self.reader.take(name_len, "root name")
        self.report.header = {
            "marker": marker,
            "value": value,
            "root_name_length": name_len,
            "root_name_sha256": hashlib.sha256(name).hexdigest(),
        }
        if marker != HEADER_MARKER:
            self.report.unsupported.append(
                {"offset": 4, "tag": marker, "reason": "unrecognised header marker"}
            )

    def parse_object(self, label: str) -> None:
        self.report.counts["objects"] += 1
        reserved = self.reader.u32(f"{label} reserved")
        attribute_count = self.reader.u16(f"{label} attribute count")
        if reserved != 0:
            self.report.unsupported.append(
                {"offset": self.reader.pos - 6, "tag": reserved, "reason": "non-zero object reserved word"}
            )

        for _ in range(attribute_count):
            self.parse_attribute()

        while True:
            if self.reader.pos + 2 > len(self.reader.data):
                raise ParseError(self.reader.pos, f"{label} missing terminator")
            field_id = self.reader.u16(f"{label} field id")
            if field_id == ROOT_TERMINATOR:
                return
            self.parse_field(field_id)

    def parse_attribute(self) -> None:
        self.report.counts["attributes"] += 1
        offset = self.reader.pos
        field_id = self.reader.u16("attribute id")
        if field_id not in ATTRIBUTE_FIELD_IDS:
            self.report.unsupported.append(
                {"offset": offset, "tag": field_id, "reason": "unsupported attribute id"}
            )
            raise ParseError(offset, f"unsupported attribute id 0x{field_id:04X}")
        self.read_definition(field_id)
        value_len = self.reader.u16("attribute value length")
        self.reader.take(value_len, "attribute value")

    def parse_field(self, field_id: int) -> None:
        self.report.counts["fields"] += 1
        self.read_definition(field_id)

        if field_id in OBJECT_FIELD_IDS:
            self.report.counts["object_fields"] += 1
            self.parse_object(f"field 0x{field_id:04X}")
            return

        if field_id == FIXED8_FIELD:
            self.report.counts["fixed8_fields"] += 1
            self.reader.take(8, "fixed 8-byte value")
            return

        if field_id in STRING_FIELD_IDS:
            self.report.counts["string_fields"] += 1
            reserved = self.reader.u32("field reserved")
            zero = self.reader.u16("field zero")
            value_tag = self.reader.u16("field value tag")
            if reserved != 0 or zero != 0:
                self.report.unsupported.append(
                    {
                        "offset": self.reader.pos - 8,
                        "tag": field_id,
                        "reason": "non-zero field value header",
                    }
                )
            if value_tag != STRING_VALUE_TAG:
                self.report.unsupported.append(
                    {
                        "offset": self.reader.pos - 2,
                        "tag": value_tag,
                        "reason": "unsupported value tag",
                    }
                )
                raise ParseError(self.reader.pos - 2, f"unsupported value tag 0x{value_tag:04X}")
            value_len = self.reader.u32("string value length")
            self.reader.take(value_len, "string value")
            self.report.counts["string_values"] += 1
            self.reader.expect_u16(ROOT_TERMINATOR, "string value terminator")
            return

        if field_id & 0xF000 == 0x6000:
            reason = "attribute identifier in field stream; attribute position is unresolved"
        else:
            reason = "unsupported field id"
        self.report.unsupported.append(
            {"offset": self.reader.pos - 2, "tag": field_id, "reason": reason}
        )
        raise ParseError(self.reader.pos - 2, f"unsupported field id 0x{field_id:04X}")

    def read_definition(self, field_id: int) -> None:
        if field_id in self.field_names:
            return
        name_offset = self.reader.pos
        name_len = self.reader.u16("field name length")
        name = self.reader.take(name_len, "field name")
        self.field_names[field_id] = name
        self.report.definitions.append(
            {
                "offset": name_offset,
                "field_id": field_id,
                "class": field_id & 0xF000,
                "index": field_id & 0x0FFF,
                "name_length": len(name),
                "name_sha256": hashlib.sha256(name).hexdigest(),
            }
        )


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Report the structure of one RBF0 payload.")
    parser.add_argument("path", help="RBF0 payload to inspect")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of text")
    args = parser.parse_args(argv)

    try:
        with open(args.path, "rb") as handle:
            data = handle.read()
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    inspector = Inspector(data)
    try:
        report = inspector.run()
    except ParseError as exc:
        report = inspector.report
        report.errors.append({"offset": exc.offset, "message": exc.message})

    if args.json:
        print(json.dumps(report.__dict__, indent=2, sort_keys=True))
    else:
        header = report.header
        print(f"size: {report.size}")
        print(f"header marker: 0x{header.get('marker', 0):04X}")
        print(f"header value: {header.get('value')}")
        print(f"root name: length {header.get('root_name_length')}, sha256 {header.get('root_name_sha256')}")
        for key in sorted(report.counts):
            print(f"{key}: {report.counts[key]}")
        for entry in report.unsupported:
            print(f"unsupported: offset 0x{entry['offset']:X}, tag 0x{entry['tag']:04X}, {entry['reason']}")
        for entry in report.errors:
            print(f"error: offset 0x{entry['offset']:X}, {entry['message']}")

    return 2 if report.errors or report.unsupported else 0


if __name__ == "__main__":
    raise SystemExit(main())
