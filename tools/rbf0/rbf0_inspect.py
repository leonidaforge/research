#!/usr/bin/env python3
"""Token parser and inspector for RBF0 payloads.

The parser implements the grammar documented in
formats/metadata/rbf0/README.md. It reads one payload read-only and reports
structure only: no field names or text values are printed.

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
VERSION_MARKER = 0xFFFB
TEXT_TOKEN = 0xFFFD
CLOSE_TOKEN = 0xFFFF
DEFAULT_MAX_DEPTH = 256

VALUE_WIDTH_CLASSES = {
    1: "number",
    2: "zero",
    3: "zero",
    4: "number",
    5: "vector12",
    6: "bytes16",
}


def token_class(token: int) -> str:
    if token == CLOSE_TOKEN:
        return "close"
    if token == TEXT_TOKEN:
        return "text"
    code = token >> 12
    if code == 0:
        return "element"
    if 1 <= code <= 6:
        return f"value_{code}"
    return f"unsupported_type_{code}"


class ParseError(Exception):
    def __init__(self, offset: int, token: str, message: str) -> None:
        super().__init__(f"0x{offset:08X} [{token}]: {message}")
        self.offset = offset
        self.token = token
        self.message = message


@dataclass
class Report:
    size: int = 0
    header: dict = field(default_factory=dict)
    counts: dict = field(default_factory=dict)
    definitions: list = field(default_factory=list)
    errors: list = field(default_factory=list)


class Reader:
    def __init__(self, data: bytes) -> None:
        self.data = data
        self.pos = 0

    def take(self, count: int, what: str, token: str = "truncated") -> bytes:
        end = self.pos + count
        if count < 0 or end > len(self.data):
            raise ParseError(
                self.pos,
                token,
                f"truncated {what}: need {count} bytes, have {len(self.data) - self.pos}",
            )
        chunk = self.data[self.pos:end]
        self.pos = end
        return chunk

    def u16(self, what: str, token: str = "truncated") -> int:
        return struct.unpack("<H", self.take(2, what, token))[0]

    def u32(self, what: str, token: str = "truncated") -> int:
        return struct.unpack("<I", self.take(4, what, token))[0]

    def peek_u16(self, offset: int) -> Optional[int]:
        if offset + 2 > len(self.data):
            return None
        return struct.unpack_from("<H", self.data, offset)[0]


class Parser:
    def __init__(self, data: bytes, max_depth: int = DEFAULT_MAX_DEPTH) -> None:
        self.reader = Reader(data)
        self.max_depth = max_depth
        self.report = Report(size=len(data))
        self.names: list[bytes] = []
        self.report.counts = {
            "elements": 0,
            "attributes": 0,
            "text_nodes": 0,
            "name_definitions": 0,
            "max_depth": 0,
            "values_by_type": {},
        }

    def parse(self) -> Report:
        self.read_header()
        token_offset = self.reader.pos
        token = self.reader.u16("root token", "truncated_token")
        if token == CLOSE_TOKEN or token == TEXT_TOKEN or token >> 12 != 0:
            raise ParseError(
                token_offset,
                token_class(token),
                f"expected an element token, found 0x{token:04X}",
            )
        self.parse_element(token, token_offset, 1)
        if self.reader.pos != len(self.reader.data):
            raise ParseError(
                self.reader.pos,
                "trailing",
                f"trailing {len(self.reader.data) - self.reader.pos} bytes after the root element",
            )
        return self.report

    def read_header(self) -> None:
        magic_offset = self.reader.pos
        magic = self.reader.take(4, "magic", "magic")
        if magic != MAGIC:
            raise ParseError(magic_offset, "magic", f"bad magic {magic!r}")
        marker_offset = self.reader.pos
        marker = self.reader.peek_u16(marker_offset)
        if marker == VERSION_MARKER:
            self.reader.take(2, "version marker", "header")
            version = self.reader.u16("version", "header")
            variant = "versioned"
            number_width = 8
            token_start = self.reader.pos
        else:
            version = None
            variant = "versionless"
            number_width = 4
            token_start = marker_offset
        self.report.header = {
            "variant": variant,
            "version": version,
            "number_width": number_width,
            "token_start": token_start,
        }

    def parse_element(self, token: int, token_offset: int, depth: int) -> None:
        if depth > self.max_depth:
            raise ParseError(
                token_offset,
                "depth",
                f"nesting depth {depth} exceeds the {self.max_depth} limit",
            )
        self.report.counts["elements"] += 1
        self.report.counts["max_depth"] = max(self.report.counts["max_depth"], depth)
        self.resolve_name(token & 0x0FFF, token_offset)
        reserved_offset = self.reader.pos
        reserved = self.reader.u32("element reserved word", "element")
        attribute_count = self.reader.u16("attribute count", "element")
        if reserved != 0:
            self.report.header.setdefault("nonzero_reserved", []).append(
                {"offset": reserved_offset, "value": reserved}
            )

        for _ in range(attribute_count):
            attribute_offset = self.reader.pos
            attribute = self.reader.u16("attribute token", "truncated_token")
            code = attribute >> 12
            if code == 0 or code > 6:
                raise ParseError(
                    attribute_offset,
                    token_class(attribute),
                    f"attribute token 0x{attribute:04X} is not a value token",
                )
            self.report.counts["attributes"] += 1
            self.resolve_name(attribute & 0x0FFF, attribute_offset)
            self.read_value(code, attribute_offset)

        body_offset = self.reader.pos
        while True:
            if self.reader.pos + 2 > len(self.reader.data):
                raise ParseError(
                    body_offset,
                    "unterminated",
                    "element has no closing 0xFFFF token before the end of the payload",
                )
            offset = self.reader.pos
            body_token = self.reader.u16("body token", "truncated_token")
            if body_token == CLOSE_TOKEN:
                return
            if body_token == TEXT_TOKEN:
                length = self.reader.u32("text length", "text")
                self.reader.take(length, "text bytes", "text")
                self.report.counts["text_nodes"] += 1
                continue
            code = body_token >> 12
            if code == 0:
                self.parse_element(body_token, offset, depth + 1)
            elif 1 <= code <= 6:
                self.resolve_name(body_token & 0x0FFF, offset)
                self.read_value(code, offset)
            else:
                raise ParseError(
                    offset,
                    token_class(body_token),
                    f"unsupported token 0x{body_token:04X}",
                )

    def resolve_name(self, index: int, token_offset: int) -> bytes:
        if index == len(self.names):
            length_offset = self.reader.pos
            length = self.reader.u16("name length", "name")
            name = self.reader.take(length, "name bytes", "name")
            self.names.append(name)
            self.report.counts["name_definitions"] += 1
            self.report.definitions.append(
                {
                    "offset": length_offset,
                    "token_offset": token_offset,
                    "name_index": index,
                    "name_length": len(name),
                    "name_sha256": hashlib.sha256(name).hexdigest(),
                }
            )
            return name
        if index > len(self.names):
            raise ParseError(
                token_offset,
                "name",
                f"name index {index} is beyond the table length {len(self.names)}",
            )
        return self.names[index]

    def read_value(self, code: int, token_offset: int) -> bytes:
        width = VALUE_WIDTH_CLASSES.get(code)
        if width == "number":
            value = self.reader.take(
                self.report.header["number_width"], f"type {code} number", f"value_{code}"
            )
        elif width == "zero":
            value = b""
        elif width == "vector12":
            value = self.reader.take(12, "type 5 value", "value_5")
        elif width == "bytes16":
            length = self.reader.u16("type 6 length", "value_6")
            value = self.reader.take(length, "type 6 bytes", "value_6")
        else:
            raise ParseError(
                token_offset, token_class((code << 12) | 0), f"unsupported value type {code}"
            )
        counts = self.report.counts["values_by_type"]
        counts[code] = counts.get(code, 0) + 1
        return value


def inspect_bytes(data: bytes, max_depth: int = DEFAULT_MAX_DEPTH) -> Report:
    return Parser(data, max_depth=max_depth).parse()


def _print_text(report: Report, stream) -> None:
    header = report["header"] if isinstance(report, dict) else report.header
    counts = report["counts"] if isinstance(report, dict) else report.counts
    definitions = report["definitions"] if isinstance(report, dict) else report.definitions
    size = report["size"] if isinstance(report, dict) else report.size

    print(f"size: {size}", file=stream)
    if "variant" in header:
        print(
            "header:"
            f" variant={header['variant']}"
            f" version={header['version']}"
            f" number_width={header['number_width']}"
            f" token_start=0x{header['token_start']:X}",
            file=stream,
        )
    else:
        print("header: not read", file=stream)
    for key in ("elements", "attributes", "text_nodes", "name_definitions", "max_depth"):
        print(f"{key}: {counts.get(key, 0)}", file=stream)
    for code in sorted(counts.get("values_by_type", {})):
        print(f"value_type_{code}: {counts['values_by_type'][code]}", file=stream)
    print(f"definitions: {len(definitions)}", file=stream)
    for entry in definitions:
        print(
            "  definition:"
            f" offset=0x{entry['offset']:X}"
            f" index={entry['name_index']}"
            f" name_length={entry['name_length']}"
            f" name_sha256={entry['name_sha256']}",
            file=stream,
        )


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Report the token structure of one RBF0 payload.")
    parser.add_argument("path", help="RBF0 payload to inspect")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of text")
    parser.add_argument(
        "--max-depth",
        type=int,
        default=DEFAULT_MAX_DEPTH,
        help=f"maximum element nesting depth (default {DEFAULT_MAX_DEPTH})",
    )
    args = parser.parse_args(argv)

    try:
        with open(args.path, "rb") as handle:
            data = handle.read()
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    try:
        parser_instance = Parser(data, max_depth=args.max_depth)
        report = parser_instance.parse()
    except ParseError as exc:
        report = parser_instance.report
        report.errors.append(
            {"offset": exc.offset, "token": exc.token, "message": exc.message}
        )

    if args.json:
        payload = {
            "size": report.size,
            "header": report.header,
            "counts": report.counts,
            "definitions": report.definitions,
            "errors": report.errors,
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        _print_text(
            {
                "size": report.size,
                "header": report.header,
                "counts": report.counts,
                "definitions": report.definitions,
            },
            sys.stdout,
        )
        for entry in report.errors:
            print(
                f"error: offset 0x{entry['offset']:X}"
                f" token {entry['token']}: {entry['message']}"
            )

    return 2 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
