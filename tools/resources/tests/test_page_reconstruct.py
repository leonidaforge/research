"""Synthetic tests for page_reconstruct.py. No game files are used."""

import os
import struct
import sys
import unittest
import zlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import page_reconstruct as pr  # noqa: E402


def system_data(length, map_at, system_pages, graphics_pages):
    data = bytearray(length)
    struct.pack_into("<Q", data, 8, pr.SYSTEM_BASE | map_at)
    data[map_at + 8] = system_pages
    data[map_at + 9] = graphics_pages
    return bytes(data)


def stored(chunks):
    """16 zero bytes, then zlib chunks padded to 16 bytes or one raw tail."""
    out = bytearray(16)
    for kind, data in chunks:
        if kind == "zlib":
            out += zlib.compress(data, 1)
            out += b"\0" * ((-len(out)) % 16)
        else:
            out += data
    return bytes(out)


def codes(layout):
    return [issue.code for issue in layout.issues]


class ReconstructionTests(unittest.TestCase):
    def test_map_near_end_of_page_zero_with_raw_second_page(self):
        page0 = system_data(0x1_0000, 0xFD60, 2, 0)
        tail = (bytes(range(256)) * 35)[:8768]
        layout = pr.analyze_bytes(stored([("zlib", page0), ("raw", tail)]), "fixture")
        self.assertEqual(layout.status, "complete", codes(layout))
        self.assertEqual(layout.page_map.offset, 0xFD60)
        self.assertEqual([page.size for page in layout.pages], [0x1_0000, 8768])
        self.assertEqual([page.storage for page in layout.pages], ["zlib", "raw"])
        self.assertEqual(sum(page.size for page in layout.pages), 74304)
        self.assertEqual(codes(layout), [])

    def test_stream_only_view_reports_the_second_page_missing(self):
        page0 = system_data(0x1_0000, 0xFD60, 2, 0)
        layout = pr.analyze_bytes(stored([("zlib", page0)]), "fixture")
        self.assertEqual(layout.status, "partial")
        self.assertEqual([page.size for page in layout.pages], [0x1_0000])
        self.assertIn("missing_pages", codes(layout))

    def test_single_page_resource(self):
        system = system_data(0x100, 0x80, 1, 0)
        layout = pr.analyze_bytes(stored([("zlib", system)]), "fixture")
        self.assertEqual(layout.status, "complete", codes(layout))
        self.assertEqual([(page.segment, page.size) for page in layout.pages],
                         [("system", 0x100)])

    def test_missing_declared_page_is_partial(self):
        system = system_data(0x100, 0xC0, 2, 0)
        layout = pr.analyze_bytes(stored([("zlib", system)]), "fixture")
        self.assertEqual(layout.status, "partial")
        self.assertIn("missing_pages", codes(layout))

    def test_packed_page_is_detected_and_split(self):
        packed = system_data(0x2_0000, 0xFD60, 2, 0)
        layout = pr.analyze_bytes(stored([("zlib", packed)]), "fixture")
        self.assertEqual(layout.status, "complete", codes(layout))
        self.assertEqual([page.size for page in layout.pages], [0x1_0000, 0x1_0000])
        self.assertEqual([page.storage for page in layout.pages], ["packed", "packed"])
        self.assertTrue(any("packed" in note for note in layout.notes))

    def test_packed_page_with_unequal_pages(self):
        packed = system_data(0x3_0000, 0xFD60, 2, 0)
        layout = pr.analyze_bytes(stored([("zlib", packed)]), "fixture")
        self.assertEqual(layout.status, "complete", codes(layout))
        self.assertEqual([page.size for page in layout.pages], [0x2_0000, 0x1_0000])
        self.assertEqual([page.storage for page in layout.pages], ["packed", "packed"])

    def test_packed_page_with_remainder(self):
        packed = system_data(0x2_4000, 0xFD60, 2, 0)
        layout = pr.analyze_bytes(stored([("zlib", packed)]), "fixture")
        self.assertEqual(layout.status, "complete", codes(layout))
        self.assertEqual([page.size for page in layout.pages], [0x2_0000, 0x4000])

    def test_raw_tail_is_not_a_page_when_no_page_is_missing(self):
        system = system_data(0x1000, 0x80, 1, 0)
        tail = b"\x01\x02\x03\x04" * 16
        layout = pr.analyze_bytes(stored([("zlib", system), ("raw", tail)]), "fixture",
                                  logical_size=0x1000)
        self.assertEqual(layout.status, "complete", codes(layout))
        self.assertEqual([page.size for page in layout.pages], [0x1000])
        self.assertEqual([page.storage for page in layout.pages], ["zlib"])
        self.assertIn("trailing_raw", codes(layout))

    def test_all_zero_raw_tail_is_a_page_when_the_count_needs_it(self):
        page0 = system_data(0x1_0000, 0xFD60, 2, 0)
        tail = bytes(8768)
        layout = pr.analyze_bytes(stored([("zlib", page0), ("raw", tail)]), "fixture",
                                  logical_size=74304)
        self.assertEqual(layout.status, "complete", codes(layout))
        self.assertEqual([page.size for page in layout.pages], [0x1_0000, 8768])
        self.assertEqual([page.storage for page in layout.pages], ["zlib", "raw"])

    def test_zlib_like_raw_tail_is_a_page_not_a_payload_error(self):
        page0 = system_data(0x1_0000, 0xFD60, 2, 0)
        tail = b"\x78\xDA" + bytes(8766)
        layout = pr.analyze_bytes(stored([("zlib", page0), ("raw", tail)]), "fixture",
                                  logical_size=74304)
        self.assertEqual(layout.status, "complete", codes(layout))
        self.assertEqual([page.size for page in layout.pages], [0x1_0000, 8768])
        self.assertEqual([page.storage for page in layout.pages], ["zlib", "raw"])
        self.assertNotIn("payload_error", codes(layout))

    def test_raw_tail_that_breaks_the_logical_size_is_not_a_page(self):
        page0 = system_data(0x1_0000, 0xFD60, 2, 0)
        tail = (bytes(range(256)) * 35)[:8768]
        layout = pr.analyze_bytes(stored([("zlib", page0), ("raw", tail)]), "fixture",
                                  logical_size=0x1_0000)
        self.assertEqual(layout.status, "partial")
        self.assertEqual([page.size for page in layout.pages], [0x1_0000])
        self.assertIn("trailing_raw", codes(layout))
        self.assertIn("missing_pages", codes(layout))

    def test_total_cap_is_enforced_across_chunks(self):
        system = system_data(0x200, 0x80, 2, 0)
        data = stored([("zlib", system[:0x100]), ("zlib", system[0x100:])])
        layout = pr.Layout("fixture")
        with self.assertRaises(pr.ResourceError) as raised:
            pr.read_chunks(data, layout, max_total=0x100)
        self.assertIn("cap", str(raised.exception))
        self.assertIn("observed 512", str(raised.exception))
        report = pr.analyze_bytes(data, "fixture", max_total=0x100)
        self.assertEqual(report.status, "unverified")
        self.assertIn("payload_error", codes(report))
        self.assertIn("cap", report.issues[0].detail)

    def test_page_map_in_second_system_page(self):
        system = system_data(0x1_0100, 0x10040, 2, 0)
        page0 = system[:0x1_0000]
        page1 = system[0x1_0000:]
        layout = pr.analyze_bytes(stored([("zlib", page0), ("zlib", page1)]), "fixture")
        self.assertEqual(layout.status, "complete", codes(layout))
        self.assertEqual(layout.page_map.offset, 0x10040)
        self.assertEqual([page.size for page in layout.pages], [0x1_0000, 0x100])

    def test_first_page_larger_than_64_kib(self):
        system = system_data(0x3_1000, 0x2FF00, 2, 0)
        layout = pr.analyze_bytes(
            stored([("zlib", system[:0x3_0000]), ("zlib", system[0x3_0000:])]),
            "fixture",
        )
        self.assertEqual(layout.status, "complete", codes(layout))
        self.assertEqual([page.size for page in layout.pages], [0x3_0000, 0x1000])

    def test_split_page_is_one_page_with_two_streams(self):
        system = system_data(0x80, 0x40, 1, 1)
        graphics = bytes(pr.SPLIT_LEN) + b"\x11" * 0x1000
        layout = pr.analyze_bytes(
            stored([("zlib", system), ("zlib", graphics[:pr.SPLIT_LEN]),
                    ("zlib", graphics[pr.SPLIT_LEN:])]),
            "fixture",
        )
        self.assertEqual(layout.status, "complete", codes(layout))
        page = layout.pages[1]
        self.assertEqual((page.segment, page.size, page.streams, page.storage),
                         ("graphics", pr.SPLIT_LEN + 0x1000, 2, "split"))

    def test_page_size_pattern_is_checked(self):
        system = system_data(0x1_8000, 0x80, 2, 0)
        layout = pr.analyze_bytes(
            stored([("zlib", system[:0x8000]), ("zlib", system[0x8000:])]),
            "fixture",
        )
        self.assertEqual([page.size for page in layout.pages], [0x8000, 0x10000])
        self.assertEqual(layout.status, "unverified")
        self.assertIn("page_size", codes(layout))

    def test_nonzero_prefix_is_rejected(self):
        system = system_data(0x80, 0x40, 1, 0)
        data = bytearray(stored([("zlib", system)]))
        data[0] = 1
        layout = pr.analyze_bytes(bytes(data), "fixture")
        self.assertEqual(layout.status, "unverified")
        self.assertIn("payload_error", codes(layout))

    def test_truncated_stream_is_reported(self):
        system = system_data(0x100, 0x80, 1, 0)
        data = stored([("zlib", system)])
        layout = pr.analyze_bytes(data[:-20], "fixture")
        self.assertEqual(layout.status, "unverified")
        self.assertIn(layout.issues[0].code, ("not_a_resource", "payload_error"))


if __name__ == "__main__":
    unittest.main()
