#!/usr/bin/env python3
"""Build synthetic RBF0 documents for the parser tests.

Every name index is allocated in definition order, so the builders produce
documents that satisfy the name-table rule in the format document. Fixtures are
original synthetic data; they contain no game content.
"""

from __future__ import annotations

import argparse
import os
import struct

MAGIC = b"RBF0"
VERSION_MARKER = 0xFFFB
TEXT_TOKEN = 0xFFFD
CLOSE_TOKEN = 0xFFFF


def u16(value: int) -> bytes:
    return struct.pack("<H", value)


def u32(value: int) -> bytes:
    return struct.pack("<I", value)


class Builder:
    def __init__(self) -> None:
        self.names: list[bytes] = []

    def name_token(self, code: int, name: bytes) -> bytes:
        index = len(self.names)
        self.names.append(name)
        return u16((code << 12) | index) + u16(len(name)) + name

    def value(self, code: int, name: bytes, payload: bytes) -> bytes:
        return self.name_token(code, name) + payload

    def value_existing(self, code: int, index: int, payload: bytes) -> bytes:
        return u16((code << 12) | index) + payload

    def element(self, name: bytes, attributes=(), body=()) -> bytes:
        head = self.name_token(0, name)
        attribute_bytes = b"".join(build() for build in attributes)
        body_bytes = b"".join(build() for build in body)
        return (
            head
            + u32(0)
            + u16(len(attributes))
            + attribute_bytes
            + body_bytes
            + u16(CLOSE_TOKEN)
        )

    def text(self, value: bytes) -> bytes:
        return u16(TEXT_TOKEN) + u32(len(value)) + value


def versioned(root, version: int = 1) -> bytes:
    return MAGIC + u16(VERSION_MARKER) + u16(version) + root


def versionless(root) -> bytes:
    return MAGIC + root


def all_value_types() -> bytes:
    b = Builder()

    def attribute(code: int, name: bytes, payload: bytes):
        return lambda: b.value(code, name, payload)

    def body_value(code: int, name: bytes, payload: bytes):
        return lambda: b.value(code, name, payload)

    root = b.element(
        b"root",
        attributes=[
            attribute(1, b"number_attr", b"\x01\x00\x00\x00\x00\x00\x00\x00"),
            attribute(2, b"flag_true", b""),
            attribute(3, b"flag_false", b""),
            attribute(4, b"float_attr", b"\x00\x00\x00\x00\x00\x00\xf0\x3f"),
            attribute(5, b"vector_attr", b"\x00" * 12),
            attribute(6, b"bytes_attr", u16(3) + b"abc"),
        ],
        body=[
            body_value(1, b"number", b"\x2a\x00\x00\x00\x00\x00\x00\x00"),
            body_value(2, b"true_value", b""),
            body_value(3, b"false_value", b""),
            body_value(4, b"float", b"\x00\x00\x00\x00\x00\x00\x00\x40"),
            body_value(5, b"vector", b"\x00" * 12),
            body_value(6, b"bytes", u16(4) + b"data"),
            lambda: b.text(b"text value"),
            lambda: b.element(
                b"child",
                body=[
                    lambda: b.text(b"nested"),
                    lambda: b.value(1, b"child_number", b"\x07\x00\x00\x00\x00\x00\x00\x00"),
                ],
            ),
        ],
    )
    return versioned(root)


def versionless_document() -> bytes:
    b = Builder()
    root = b.element(
        b"root",
        body=[
            lambda: b.value(1, b"number", b"\x01\x00\x00\x00"),
            lambda: b.value(4, b"float", b"\x00\x00\x00\x00"),
            lambda: b.text(b"text"),
        ],
    )
    return versionless(root)


def name_reuse_document() -> bytes:
    b = Builder()
    root = b.element(
        b"root",
        body=[
            lambda: b.value(1, b"number", b"\x01\x00\x00\x00\x00\x00\x00\x00"),
            lambda: b.value_existing(1, 1, b"\x02\x00\x00\x00\x00\x00\x00\x00"),
        ],
    )
    return versioned(root)


def nested_document(depth: int) -> bytes:
    b = Builder()

    def level(index: int) -> bytes:
        if index == depth:
            return b.element(f"level_{index}".encode())
        return b.element(f"level_{index}".encode(), body=[lambda: level(index + 1)])

    return versioned(level(0))


def malformed(kind: str) -> bytes:
    if kind == "truncated_token":
        b = Builder()
        return (
            MAGIC
            + u16(VERSION_MARKER)
            + u16(1)
            + u16(0)
            + u16(1)
            + b"r"
            + u32(0)
            + u16(1)
            + b"\x01"
        )
    if kind == "truncated_version":
        return MAGIC + u16(VERSION_MARKER)
    if kind == "name_length_past_end":
        b = Builder()
        return MAGIC + u16(VERSION_MARKER) + u16(1) + u16(0) + u16(100) + b"short"
    if kind == "text_length_past_end":
        b = Builder()
        root = b.element(b"root", body=[lambda: u16(TEXT_TOKEN) + u32(100) + b"short"])
        return versioned(root)
    if kind == "type6_length_past_end":
        b = Builder()
        root = b.element(b"root", body=[lambda: b.value(6, b"bytes", u16(100) + b"short")])
        return versioned(root)
    if kind == "name_index_past_table":
        b = Builder()
        return MAGIC + u16(VERSION_MARKER) + u16(1) + u16(1) + u16(1) + b"x" + u32(0) + u16(0) + u16(CLOSE_TOKEN)
    if kind == "unterminated_element":
        data = all_value_types()
        return data[:-2]
    if kind == "unsupported_token":
        b = Builder()
        root = b.element(b"root", body=[lambda: u16(0x7000)])
        return versioned(root)
    if kind == "trailing_bytes":
        return all_value_types() + b"\x00\x00"
    if kind == "bad_magic":
        return b"NOPE" + all_value_types()[4:]
    raise ValueError(f"unknown fixture {kind}")


FIXTURES = {
    "versioned_all_types": all_value_types,
    "versionless": versionless_document,
    "name_reuse": name_reuse_document,
    "malformed_truncated_token": lambda: malformed("truncated_token"),
    "malformed_truncated_version": lambda: malformed("truncated_version"),
    "malformed_name_length": lambda: malformed("name_length_past_end"),
    "malformed_text_length": lambda: malformed("text_length_past_end"),
    "malformed_type6_length": lambda: malformed("type6_length_past_end"),
    "malformed_name_index": lambda: malformed("name_index_past_table"),
    "malformed_unterminated": lambda: malformed("unterminated_element"),
    "malformed_unsupported_token": lambda: malformed("unsupported_token"),
    "malformed_trailing_bytes": lambda: malformed("trailing_bytes"),
    "malformed_bad_magic": lambda: malformed("bad_magic"),
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Write synthetic RBF0 fixtures.")
    parser.add_argument("directory", help="output directory for the fixtures")
    args = parser.parse_args()
    os.makedirs(args.directory, exist_ok=True)
    for name, build in sorted(FIXTURES.items()):
        path = os.path.join(args.directory, name + ".rbf0")
        with open(path, "wb") as handle:
            handle.write(build())
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
