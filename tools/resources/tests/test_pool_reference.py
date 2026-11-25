"""Synthetic tests for pool_reference.py. No game files are used."""

import contextlib
import io
import json
import os
import struct
import sys
import tempfile
import unittest
import zlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pool_reference as pr  # noqa: E402


def _ptr(segment, offset):
    base = pr.SYSTEM_BASE if segment == "system" else pr.GRAPHICS_BASE
    return base | offset


def make_drawable(packed=(0, 4), other=(0x00800003,), slot0=True,
                  shader_count=1, texture_count=None, total=None,
                  slot_target=None, name_pointer_variant=False):
    """Build a synthetic system segment with one or more shaders."""
    data = bytearray(0x500)
    map_at = 0x480
    struct.pack_into("<Q", data, 8, _ptr("system", map_at))
    data[map_at + 8] = 1
    if texture_count is None:
        texture_count = len(packed)
    if total is None:
        total = texture_count + len(other)
    group_at = 0x100
    array_at = 0x120
    shader_at = 0x140
    slot_at = 0x1A0
    param_at = 0x1C0
    texture_at = 0x240
    name_at = 0x2C0
    struct.pack_into("<Q", data, 0x10, _ptr("system", group_at))
    struct.pack_into("<Q", data, group_at + 0x10, _ptr("system", array_at))
    struct.pack_into("<H", data, group_at + 0x18, shader_count)
    struct.pack_into("<H", data, group_at + 0x1A, shader_count)
    for index in range(shader_count):
        struct.pack_into("<Q", data, array_at + 8 * index, _ptr("system", shader_at))
    struct.pack_into("<Q", data, shader_at + 0x10, _ptr("system", slot_at))
    struct.pack_into("<Q", data, shader_at + 0x20, _ptr("system", param_at))
    data[param_at + 0] = 1
    data[param_at + 1] = texture_count
    struct.pack_into("<H", data, param_at + 4, total)
    struct.pack_into("<H", data, param_at + 6, 0x0800)
    for index in range(texture_count):
        struct.pack_into("<I", data, param_at + 8 + 8 * index, 0x1000 + index)
        struct.pack_into("<I", data, param_at + 12 + 8 * index, packed[index])
    for index, value in enumerate(other):
        struct.pack_into("<I", data, param_at + 8 + 8 * (texture_count + index), 0x2000 + index)
        struct.pack_into("<I", data, param_at + 12 + 8 * (texture_count + index), value)
    for index in range(texture_count):
        if index == 0 and slot0:
            target = slot_target if slot_target is not None else _ptr("system", texture_at)
            struct.pack_into("<Q", data, slot_at + 8 * index, target)
    struct.pack_into("<Q", data, texture_at + 0x30, _ptr("system", name_at))
    struct.pack_into("<Q", data, name_at + 0x08, 0x1122334455667788)
    struct.pack_into("<Q", data, name_at + 0x10,
                     _ptr("system", 0x300) if name_pointer_variant else 6)
    struct.pack_into("<I", data, name_at + 0x18, 0xB2307B84)
    return data


class ParseTests(unittest.TestCase):
    def test_reads_shader_parameters_and_slots(self):
        report = pr.parse_shader_pool(bytes(make_drawable()))
        self.assertEqual(report.issues, [])
        counts = report.counts
        self.assertEqual(counts["shaders"], 1)
        self.assertEqual(counts["texture"], 2)
        self.assertEqual(counts["index_in"], 2)
        self.assertEqual(counts["bound"], 1)
        self.assertEqual(counts["null"], 1)
        self.assertEqual(counts["other_class"], 1)
        reference = report.references[0]
        self.assertEqual(reference.index, 0)
        self.assertEqual(reference.state, "bound")
        self.assertEqual(reference.name_hash, 0xB2307B84)
        self.assertEqual(reference.key64, 0x1122334455667788)
        self.assertEqual(report.references[1].state, "null")

    def test_class_mismatch_is_an_issue(self):
        report = pr.parse_shader_pool(bytes(make_drawable(packed=(0, 7))))
        states = [ref.state for ref in report.references]
        self.assertIn("class", states)
        self.assertIn("slot_reference", [issue.code for issue in report.issues])

    def test_index_out_of_range_is_an_issue(self):
        report = pr.parse_shader_pool(bytes(make_drawable(packed=(0, 12))))
        self.assertEqual(report.references[1].state, "index")
        self.assertIsNone(report.references[1].index)

    def test_bad_slot_target_is_an_issue(self):
        report = pr.parse_shader_pool(bytes(make_drawable(slot_target=0x1234)))
        self.assertEqual(report.references[0].state, "bad")
        self.assertIn("slot_target", [issue.code for issue in report.issues])

    def test_name_variant_selects_the_hash_reading(self):
        report = pr.parse_shader_pool(bytes(make_drawable(name_pointer_variant=True)))
        reference = report.references[0]
        self.assertIsNone(reference.name_hash)
        self.assertEqual(reference.name_variant, "other")
        self.assertEqual(reference.key64, 0x1122334455667788)

    def test_parameter_count_below_texture_count_is_an_issue(self):
        report = pr.parse_shader_pool(bytes(make_drawable(other=(), total=1)))
        self.assertIn("parameter_count", [issue.code for issue in report.issues])

    def test_pointers_are_counted_separately(self):
        report = pr.parse_shader_pool(bytes(make_drawable()))
        self.assertGreaterEqual(report.pointers["system"], 4)

    def test_shader_cap_is_enforced(self):
        with self.assertRaises(pr.PoolReferenceError):
            pr.parse_shader_pool(bytes(make_drawable(shader_count=2)), max_shaders=1)

    def test_short_buffer_is_refused(self):
        with self.assertRaises(pr.PoolReferenceError):
            pr.parse_shader_pool(b"\0" * 8)

    def test_non_system_shader_pointer_is_refused(self):
        data = make_drawable()
        struct.pack_into("<Q", data, 0x10, pr.GRAPHICS_BASE | 0x100)
        with self.assertRaises(pr.PoolReferenceError):
            pr.parse_shader_pool(bytes(data))

    def test_parameter_table_outside_is_refused(self):
        data = make_drawable()
        struct.pack_into("<H", data, 0x1C4, 0xFFFF)
        with self.assertRaises(pr.PoolReferenceError):
            pr.parse_shader_pool(bytes(data))


class ControlTests(unittest.TestCase):
    def test_scalar_control_accepts_no_values(self):
        values = [0x3, 0x7, 0xFFFFFFFF, 0x00000010, 0x00000100]
        self.assertEqual(pr.control_acceptance(values, 4), 0)

    def test_reference_decoder(self):
        self.assertEqual(pr.decode_slot_reference(0, 4), (True, 0))
        self.assertEqual(pr.decode_slot_reference(12, 4), (True, 3))
        self.assertEqual(pr.decode_slot_reference(16, 4), (False, None))
        self.assertEqual(pr.decode_slot_reference(7, 4), (False, None))


class StoredTests(unittest.TestCase):
    def test_stored_row_and_cli(self):
        system = bytes(make_drawable())
        row = b"\0" * 16 + zlib.compress(system)
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "drawable.bin")
            with open(path, "wb") as handle:
                handle.write(row)
            report, decoded = pr.analyze_stored(path, 0, len(row), logical_size=len(system))
        self.assertEqual(decoded, system)
        self.assertEqual(report.counts["bound"], 1)

        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "decoded.bin")
            with open(path, "wb") as handle:
                handle.write(system)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = pr.main(["--file", path, "--system-length", str(len(system)), "--json"])
        self.assertEqual(code, 0)
        parsed = json.loads(output.getvalue())
        self.assertEqual(parsed["counts"]["texture"], 2)


if __name__ == "__main__":
    unittest.main()
