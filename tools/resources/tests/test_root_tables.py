"""Synthetic tests for root_tables.py. No game files are used."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import root_tables as rt  # noqa: E402


def root_bytes(length=0x200, map_at=0x1E0, block_ptr=0x100, count=2):
    data = bytearray(length)
    struct.pack_into("<Q", data, 8, rt.SYSTEM_BASE | map_at)
    data[0x10:0x14] = b"0DRP"
    data[0x14] = 0x7A
    struct.pack_into("<Q", data, 0x20, 3)
    struct.pack_into("<Q", data, 0x28, rt.SYSTEM_BASE | 0x40)
    struct.pack_into("<Q", data, 0x30, 0)
    struct.pack_into("<Q", data, 0x38, rt.SYSTEM_BASE | block_ptr)
    struct.pack_into("<Q", data, 0x40, rt.SYSTEM_BASE | 0x80)
    struct.pack_into("<4H", data, 0x48, 3, 0, count, 0)
    if block_ptr + count * 16 <= length:
        struct.pack_into("<IIQ", data, block_ptr, 0x11111111, 0x20, rt.SYSTEM_BASE | 0x40)
        if count > 1:
            struct.pack_into("<IIQ", data, block_ptr + 16, 0x22222222, 0x30, rt.GRAPHICS_BASE | 0x10)
    return bytes(data)


class RootTests(unittest.TestCase):
    def test_reads_the_candidate_fields(self):
        root, issues = rt.parse_root(root_bytes(), graphics_len=0x100)
        self.assertEqual(issues, [])
        self.assertEqual(root.page_map, 0x1E0)
        self.assertEqual(root.version, 0x7A)
        self.assertEqual(root.qword_18, 0)
        self.assertEqual(root.variant, 3)
        self.assertEqual(root.counts, (3, 0, 2, 0))
        self.assertEqual(root.pointers[0x28], 0x40)
        self.assertIsNone(root.pointers[0x30])
        self.assertEqual(root.pointers[0x38], 0x100)
        self.assertEqual(root.pointers[0x40], 0x80)

    def test_walks_the_block_table(self):
        root, issues = rt.parse_root(root_bytes(), graphics_len=0x100)
        self.assertEqual(issues, [])
        self.assertEqual(len(root.blocks), 2)
        self.assertEqual([(b.segment, b.offset, b.size) for b in root.blocks],
                         [("system", 0x40, 0x20), ("graphics", 0x10, 0x30)])

    def test_block_table_outside_is_refused(self):
        root, issues = rt.parse_root(root_bytes(block_ptr=0x1F8, count=2), graphics_len=0x100)
        self.assertEqual(root.blocks, [])
        self.assertIn("block_table_outside", [issue.code for issue in issues])

    def test_block_target_outside_is_reported(self):
        data = bytearray(root_bytes())
        struct.pack_into("<IIQ", data, 0x100, 0x11111111, 0x200, rt.GRAPHICS_BASE | 0x10)
        root, issues = rt.parse_root(bytes(data), graphics_len=0x100)
        self.assertIn("block_outside", [issue.code for issue in issues])

    def test_huge_count_does_not_read_past_the_segment(self):
        root, issues = rt.parse_root(root_bytes(count=0xFFFF), graphics_len=0x100)
        self.assertEqual(root.blocks, [])
        self.assertIn("block_table_outside", [issue.code for issue in issues])

    def test_root_pointer_outside_is_reported(self):
        data = bytearray(root_bytes())
        struct.pack_into("<Q", data, 0x28, rt.SYSTEM_BASE | 0x1000)
        root, issues = rt.parse_root(bytes(data), graphics_len=0x100)
        self.assertIn("root_pointer", [issue.code for issue in issues])

    def test_missing_tag_is_rejected(self):
        data = bytearray(root_bytes())
        data[0x10:0x14] = b"XXXX"
        root, issues = rt.parse_root(bytes(data), graphics_len=0x100)
        self.assertIsNone(root)
        self.assertEqual(issues[0].code, "not_0drp")

    def test_short_buffer_is_refused(self):
        root, issues = rt.parse_root(b"\0" * 0x20, graphics_len=0)
        self.assertIsNone(root)
        self.assertEqual(issues[0].code, "short_root")


if __name__ == "__main__":
    unittest.main()
