#!/usr/bin/env python3
"""Synthetic tests for the RBF0 structural inspector."""

from __future__ import annotations

import contextlib
import io
import os
import struct
import tempfile
import unittest

import rbf0_inspect as inspect


def u16(value: int) -> bytes:
    return struct.pack("<H", value)


def u32(value: int) -> bytes:
    return struct.pack("<I", value)


def name(value: bytes) -> bytes:
    return u16(len(value)) + value


def string_value(value: bytes) -> bytes:
    return u32(0) + u16(0) + u16(0xFFFD) + u32(len(value)) + value + u16(0xFFFF)


def attribute(field_id: int, field_name: bytes, value: bytes) -> bytes:
    return u16(field_id) + name(field_name) + u16(len(value)) + value


def object_body(attribute_count: int, attributes: bytes, fields: bytes) -> bytes:
    return u32(0) + u16(attribute_count) + attributes + fields + u16(0xFFFF)


def build_document() -> bytes:
    root_name = b"doc"
    header = b"RBF0" + u16(0xFFFB) + u32(1) + name(root_name)
    inner_item = object_body(
        0,
        b"",
        u16(4)
        + name(b"text")
        + string_value(b"x\x00")
        + u16(0x1006)
        + name(b"number")
        + b"\xff" * 8,
    )
    second_item = object_body(0, b"", b"")
    first_item = object_body(
        1,
        attribute(0x6003, b"kind", b"item"),
        u16(2) + inner_item + u16(2) + second_item,
    )
    container = object_body(0, b"", u16(2) + name(b"item") + first_item)
    root = object_body(0, b"", u16(1) + name(b"list") + container)
    return header + root


class InspectorTests(unittest.TestCase):
    def test_counts_and_header(self) -> None:
        report = inspect.Inspector(build_document()).run()
        self.assertEqual(report.header["marker"], 0xFFFB)
        self.assertEqual(report.header["value"], 1)
        self.assertEqual(report.header["root_name_length"], 3)
        self.assertEqual(report.counts["attributes"], 1)
        self.assertEqual(report.counts["string_values"], 1)
        self.assertEqual(report.counts["fixed8_fields"], 1)
        self.assertEqual(len(report.definitions), 5)

    def test_field_definitions_are_local_and_ordered(self) -> None:
        report = inspect.Inspector(build_document()).run()
        ids = [entry["field_id"] for entry in report.definitions]
        self.assertEqual(ids, [1, 2, 0x6003, 4, 0x1006])
        self.assertEqual([entry["index"] for entry in report.definitions], [1, 2, 3, 4, 6])

    def test_unsupported_value_tag_is_reported(self) -> None:
        data = bytearray(build_document())
        marker = data.find(u16(0xFFFD))
        data[marker:marker + 2] = u16(0xFFFE)
        inspector = inspect.Inspector(bytes(data))
        with self.assertRaises(inspect.ParseError):
            inspector.run()
        self.assertTrue(inspector.report.unsupported)
        self.assertEqual(inspector.report.unsupported[0]["tag"], 0xFFFE)

    def test_truncated_payload_is_an_error(self) -> None:
        data = build_document()[:-4]
        with self.assertRaises(inspect.ParseError):
            inspect.Inspector(data).run()

    def test_cli_exit_codes(self) -> None:
        document = build_document()
        with tempfile.TemporaryDirectory() as directory:
            good = os.path.join(directory, "good.rbf0")
            bad = os.path.join(directory, "bad.rbf0")
            with open(good, "wb") as handle:
                handle.write(document)
            with open(bad, "wb") as handle:
                handle.write(document[:-4])
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(inspect.main([good]), 0)
                self.assertEqual(inspect.main([bad]), 2)


if __name__ == "__main__":
    unittest.main()
