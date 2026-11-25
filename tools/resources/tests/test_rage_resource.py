"""Synthetic tests for rage_resource.py. No game files are used."""

import os
import struct
import sys
import tempfile
import unittest
import zlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import rage_resource as rr  # noqa: E402


def system_data(length, map_at, system_pages, graphics_pages, pointers=()):
    """System bytes with a resource header and a page map at map_at."""
    data = bytearray(length)
    struct.pack_into("<Q", data, 8, rr.SYSTEM_BASE | map_at)
    data[map_at + 8] = system_pages
    data[map_at + 9] = graphics_pages
    for at, value in pointers:
        struct.pack_into("<Q", data, at, value)
    return bytes(data)


def page_streams(page, split=rr.SPLIT_LEN):
    chunks = [page[:split]]
    rest = page[split:]
    while rest:
        chunks.append(rest[:split])
        rest = rest[split:]
    return chunks


def stored_payload(streams, level=6):
    """16 zero bytes, then each stream as zlib, padded to 16 bytes."""
    out = bytearray(16)
    for stream in streams:
        out += zlib.compress(stream, level)
        out += b"\0" * ((-len(out)) % 16)
    return bytes(out)


class PayloadCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

    def write(self, data, name="sample.bin"):
        path = os.path.join(self.temp.name, name)
        with open(path, "wb") as handle:
            handle.write(data)
        return path

    def analyze(self, data, length=None, max_stream=rr.MAX_STREAM, max_total=rr.MAX_TOTAL):
        path = self.write(data)
        return rr.analyze_payload(
            path, 0, len(data) if length is None else length, max_stream, max_total
        )

    def codes(self, layout):
        return [issue.code for issue in layout.issues]


class PointerTests(unittest.TestCase):
    def test_decodes_both_segments(self):
        self.assertEqual(rr.decode_pointer(0x50000040), rr.Pointer("system", 0x40))
        self.assertEqual(rr.decode_pointer(0x6FFFFFFF), rr.Pointer("graphics", 0x0FFFFFFF))
        self.assertIsNone(rr.decode_pointer(0x4FFFFFFF))
        self.assertIsNone(rr.decode_pointer(0x70000000))
        self.assertIsNone(rr.decode_pointer(0x150000000))


class PageMapTests(unittest.TestCase):
    def test_reads_the_counts_at_plus_eight_and_nine(self):
        data = bytearray(0x100 + 16 + 3 * 8)
        data[0x100 + 8] = 1
        data[0x100 + 9] = 2
        page_map, issue = rr.parse_page_map(bytes(data), 0x100)
        self.assertIsNone(issue)
        self.assertEqual((page_map.system_pages, page_map.graphics_pages), (1, 2))
        self.assertEqual(page_map.byte_len, 40)

    def test_rejects_malformed_maps(self):
        data = bytearray(0x20 + 16 + 3 * 8)
        data[0x20 + 8] = 1
        data[0x20 + 9] = 2
        cases = {
            "map_outside": bytes(data[:-1]),
            "map_nonzero": bytes(data[: 0x20 + 16] + b"\x01" + data[0x20 + 17 :]),
            "no_system_page": bytes(data[: 0x20 + 8] + b"\0\0" + data[0x20 + 10 :]),
            "map_in_header": bytes(data),
        }
        for code, buffer in cases.items():
            with self.subTest(code):
                offset = 8 if code == "map_in_header" else 0x20
                page_map, issue = rr.parse_page_map(buffer, offset)
                self.assertIsNone(page_map)
                self.assertEqual(issue.code, code)


class GroupingTests(unittest.TestCase):
    def test_split_streams_form_one_page(self):
        groups, method = rr.group_pages([0x400, rr.SPLIT_LEN, 0x60_0000], 2)
        self.assertEqual(method, "split")
        self.assertEqual(groups, [(0x400, 1), (rr.SPLIT_LEN + 0x60_0000, 2)])

    def test_a_full_page_is_not_split_by_the_stream_count(self):
        groups, method = rr.group_pages([0x400, rr.SPLIT_LEN, 0x1000], 3)
        self.assertEqual(method, "single")
        self.assertEqual(groups, [(0x400, 1), (rr.SPLIT_LEN, 1), (0x1000, 1)])

    def test_page_count_decides_when_neither_reading_fits(self):
        groups, method = rr.group_pages([0x400, rr.SPLIT_LEN, 0x1000], 4)
        self.assertEqual(method, "greedy")
        self.assertEqual(groups, [(0x400, 1), (rr.SPLIT_LEN + 0x1000, 2)])


class LayoutTests(PayloadCase):
    def test_one_page_per_segment(self):
        system = system_data(0x100, 0x80, 1, 1, [(0x20, rr.SYSTEM_BASE | 0x40),
                                                  (0x28, rr.GRAPHICS_BASE | 0x10)])
        graphics = b"\xAB" * 0x2000
        layout = self.analyze(stored_payload([system, graphics]))
        self.assertEqual(layout.status, "complete", self.codes(layout))
        self.assertEqual(layout.page_map.offset, 0x80)
        self.assertEqual(layout.system_len, 0x100)
        self.assertEqual(layout.graphics_len, 0x2000)
        self.assertEqual(
            [(page["segment"], page["size"], page["streams"]) for page in layout.pages],
            [("system", 0x100, 1), ("graphics", 0x2000, 1)],
        )
        self.assertEqual(
            layout.pointers,
            {"system": 2, "graphics": 1, "system_outside": 0, "graphics_outside": 0},
        )

    def test_system_only_resource(self):
        system = system_data(0x80, 0x40, 1, 0)
        layout = self.analyze(stored_payload([system]))
        self.assertEqual(layout.status, "complete", self.codes(layout))
        self.assertEqual(layout.graphics_len, 0)
        self.assertEqual(len(layout.pages), 1)

    def test_page_map_in_a_later_system_page(self):
        system = system_data(0x10100, 0x10040, 2, 1, [(0x20, rr.SYSTEM_BASE | 0x80)])
        graphics = b"\x11" * 0x800
        streams = [system[:0x10000], system[0x10000:], graphics]
        layout = self.analyze(stored_payload(streams))
        self.assertEqual(layout.status, "complete", self.codes(layout))
        self.assertEqual(
            [(page["segment"], page["size"]) for page in layout.pages],
            [("system", 0x10000), ("system", 0x100), ("graphics", 0x800)],
        )

    def test_split_graphics_page(self):
        system = system_data(0x80, 0x40, 1, 1)
        graphics = bytes(rr.SPLIT_LEN) + b"\x22" * 0x1000
        streams = [system] + page_streams(graphics)
        layout = self.analyze(stored_payload(streams, level=1))
        self.assertEqual(layout.status, "complete", self.codes(layout))
        self.assertEqual(len(layout.pages), 2)
        page = layout.pages[1]
        self.assertEqual((page["size"], page["streams"]), (rr.SPLIT_LEN + 0x1000, 2))

    def test_a_full_32_mib_page_is_its_own_page(self):
        system = system_data(0x80, 0x40, 1, 2)
        first = bytes(rr.SPLIT_LEN)
        second = b"\x33" * 0x1000
        layout = self.analyze(stored_payload([system, first, second], level=1))
        self.assertEqual(layout.status, "complete", self.codes(layout))
        self.assertEqual(
            [(page["size"], page["streams"]) for page in layout.pages],
            [(0x80, 1), (rr.SPLIT_LEN, 1), (0x1000, 1)],
        )

    def test_missing_graphics_page_is_partial(self):
        system = system_data(0x100, 0xC0, 1, 2)
        graphics = b"\0" * 0x2_0000
        layout = self.analyze(stored_payload([system, graphics]))
        self.assertEqual(layout.status, "partial")
        self.assertIn("missing_pages", self.codes(layout))
        self.assertEqual(len(layout.pages), 2)

    def test_extra_page_stream_is_reported(self):
        system = system_data(0x100, 0xC0, 1, 1)
        layout = self.analyze(
            stored_payload([system, b"\0" * 0x1000, b"\0" * 0x1000])
        )
        self.assertEqual(layout.status, "unverified")
        self.assertIn("page_count", self.codes(layout))

    def test_page_size_pattern_is_checked(self):
        system = system_data(0x100, 0xC0, 1, 2)
        first = b"\0" * 0x1_8000
        second = b"\0" * 0x2_0000
        layout = self.analyze(stored_payload([system, first, second]))
        self.assertEqual(layout.status, "unverified")
        self.assertEqual(self.codes(layout).count("page_size"), 2)

    def test_pointer_outside_is_only_a_warning(self):
        system = system_data(
            0x100, 0xC0, 1, 1, [(0x20, rr.SYSTEM_BASE | 0x1000)]
        )
        layout = self.analyze(stored_payload([system, b"\0" * 0x100]))
        self.assertEqual(layout.status, "complete")
        self.assertEqual(self.codes(layout), ["pointers_outside"])


class NegativeTests(PayloadCase):
    def test_truncated_stream(self):
        system = system_data(0x100, 0x80, 1, 1)
        data = stored_payload([system, b"\x44" * 0x4000])
        layout = self.analyze(data, length=len(data) - 40)
        self.assertEqual(layout.status, "unverified")
        self.assertEqual(layout.issues[0].code, "payload_error")
        self.assertIn("truncated", layout.issues[0].detail)

    def test_no_system_page(self):
        system = system_data(0x100, 0x80, 0, 1)
        layout = self.analyze(stored_payload([system, b"\0" * 0x100]))
        self.assertEqual(layout.status, "unverified")
        self.assertEqual(layout.page_map_issue.code, "no_system_page")

    def test_map_outside_the_system_data(self):
        system = bytearray(0x100)
        struct.pack_into("<Q", system, 8, rr.SYSTEM_BASE | 0x200)
        layout = self.analyze(stored_payload([bytes(system)]))
        self.assertEqual(layout.status, "unverified")
        self.assertEqual(layout.page_map_issue.code, "map_outside")

    def test_nonzero_page_slot(self):
        system = bytearray(system_data(0x100, 0x80, 1, 1))
        system[0x80 + 16] = 1
        layout = self.analyze(stored_payload([bytes(system), b"\0" * 0x100]))
        self.assertEqual(layout.status, "unverified")
        self.assertEqual(layout.page_map_issue.code, "map_nonzero")

    def test_nonzero_prefix(self):
        system = system_data(0x80, 0x40, 1, 0)
        data = bytearray(stored_payload([system]))
        data[0] = 1
        layout = self.analyze(bytes(data))
        self.assertEqual(layout.issues[0].code, "payload_error")
        self.assertIn("not zero", layout.issues[0].detail)

    def test_nonzero_padding(self):
        system = system_data(0x80, 0x40, 1, 0)
        data = bytearray(stored_payload([system]))
        # The stream ends before the next 16-byte boundary.
        offset = 16 + len(zlib.compress(system, 6))
        self.assertGreater((16 - offset % 16) % 16, 0)
        data[offset] = 1
        layout = self.analyze(bytes(data))
        self.assertEqual(layout.issues[0].code, "payload_error")
        self.assertIn("padding", layout.issues[0].detail)

    def test_stream_cap_is_enforced(self):
        system = system_data(0x80, 0x40, 1, 0)
        layout = self.analyze(stored_payload([system]), max_stream=0x40)
        self.assertEqual(layout.issues[0].code, "payload_error")
        self.assertIn("cap", layout.issues[0].detail)

    def test_total_cap_is_enforced(self):
        system = system_data(0x80, 0x40, 1, 1)
        layout = self.analyze(stored_payload([system, b"\0" * 0x100]), max_total=0x100)
        self.assertEqual(layout.issues[0].code, "payload_error")
        self.assertIn("cap", layout.issues[0].detail)

    def test_data_without_a_resource_header(self):
        layout = self.analyze(stored_payload([b"<?xml version=\"1.0\"?>" * 4]))
        self.assertEqual(layout.status, "unverified")
        self.assertIn(
            layout.issues[0].code, ("not_a_resource", "payload_error")
        )


class DecodedTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

    def write(self, data):
        path = os.path.join(self.temp.name, "decoded.bin")
        with open(path, "wb") as handle:
            handle.write(data)
        return path

    def test_decoded_resource(self):
        system = system_data(0x100, 0x80, 1, 1, [(0x20, rr.GRAPHICS_BASE | 0x100)])
        graphics = b"\0" * 0x2000
        path = self.write(system + graphics)
        layout = rr.analyze_decoded(path, len(system), rr.MAX_TOTAL)
        self.assertEqual(layout.status, "complete", [i.code for i in layout.issues])
        self.assertEqual(layout.system_len, 0x100)
        self.assertEqual(layout.graphics_len, 0x2000)
        self.assertEqual(layout.pointers["graphics"], 1)

    def test_system_length_must_cover_the_map(self):
        system = system_data(0x100, 0x80, 1, 1)
        path = self.write(system + b"\0" * 0x2000)
        layout = rr.analyze_decoded(path, 0x80, rr.MAX_TOTAL)
        self.assertEqual(layout.status, "unverified")
        self.assertEqual(layout.page_map_issue.code, "map_outside")


if __name__ == "__main__":
    unittest.main()
