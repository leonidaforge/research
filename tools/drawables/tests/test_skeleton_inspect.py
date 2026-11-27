"""Synthetic tests for skeleton_inspect.py. No game files are used."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import skeleton_inspect as si  # noqa: E402

SKELETON = 0x100
BONES = 0x200
INVERSE = 0x400
PARENTS = 0x600
SYSTEM_SIZE = 0x800


def system_ptr(offset):
    return 0x5000_0000 | offset


def build(bones, inverse=None):
    system = bytearray(SYSTEM_SIZE)
    # Fragment root: page map and the member drawable.
    struct.pack_into("<Q", system, 0x08, system_ptr(0x30))
    struct.pack_into("<Q", system, 0x18, system_ptr(0x40))
    struct.pack_into("<I", system, 0x40 + 0x18, 0)  # drawable word 0x18 is a pointer
    struct.pack_into("<Q", system, 0x40 + 0x18, system_ptr(SKELETON))

    struct.pack_into("<I", system, SKELETON + 0x10, 1)
    struct.pack_into("<I", system, SKELETON + 0x18, 0x20)
    struct.pack_into("<I", system, SKELETON + 0x1C, len(bones) * 2)
    struct.pack_into("<Q", system, SKELETON + 0x28, system_ptr(BONES))
    struct.pack_into("<Q", system, SKELETON + 0x40, system_ptr(PARENTS))
    if inverse is not None:
        struct.pack_into("<Q", system, SKELETON + 0x30, system_ptr(INVERSE))

    for index, (rotation, translation, parent) in enumerate(bones):
        at = BONES + index * si.BONE_LEN
        for slot, value in enumerate(rotation):
            struct.pack_into("<f", system, at + 4 * slot, value)
        for slot, value in enumerate(translation):
            struct.pack_into("<f", system, at + 0x10 + 4 * slot, value)
        for slot in range(3):
            struct.pack_into("<f", system, at + 0x20 + 4 * slot, 1.0)
        struct.pack_into("<I", system, at + 0x1C, index + 1)
        struct.pack_into("<H", system, at + 0x46, parent)
        struct.pack_into("<H", system, at + 0x48, index)
        struct.pack_into("<H", system, at + 0x4A, index + 1)
        struct.pack_into("<H", system, at + 0x4E, len(bones))
        struct.pack_into("<H", system, PARENTS + index * 2, parent)
    return bytes(system)


class HierarchyTests(unittest.TestCase):
    def test_an_invalid_parent_is_reported_and_unresolved(self):
        bones = [
            {"index": 0, "raw_parent": 7, "parent": 7},
        ]
        roots, depth, issues = si.resolve_hierarchy(bones)
        self.assertEqual(roots, [0])
        self.assertEqual(depth, 1)
        self.assertTrue(any(issue["code"] == "invalid_parent" for issue in issues))
        self.assertIsNone(bones[0]["parent"])

    def test_a_cycle_is_reported_for_every_member(self):
        bones = [
            {"index": 0, "raw_parent": 1, "parent": 1},
            {"index": 1, "raw_parent": 0, "parent": 0},
        ]
        roots, _depth, issues = si.resolve_hierarchy(bones)
        self.assertEqual(sorted(roots), [0, 1])
        self.assertEqual(
            sorted(issue["bone"] for issue in issues if issue["code"] == "cycle"),
            [0, 1],
        )

    def test_a_child_translation_is_rotated_by_its_parent(self):
        import math

        quarter = (0.0, 0.0, math.sin(math.pi / 4), math.cos(math.pi / 4))
        bones = [
            {"index": 0, "raw_parent": si.ROOT_PARENT, "parent": None,
             "rotation": quarter, "translation": [0.0, 0.0, 0.0]},
            {"index": 1, "raw_parent": 0, "parent": 0,
             "rotation": [0.0, 0.0, 0.0, 1.0], "translation": [1.0, 0.0, 0.0]},
        ]
        _rotations, positions = si.compose(bones)
        self.assertAlmostEqual(positions[1][0], 0.0, places=5)
        self.assertAlmostEqual(positions[1][1], 1.0, places=5)


class InspectTests(unittest.TestCase):
    def test_reads_bones_parents_and_matches_another_array(self):
        data = build(
            [
                ([0.0, 0.0, 0.0, 1.0], [0.0, 0.0, 0.0], si.ROOT_PARENT),
                ([0.0, 0.0, 0.0, 1.0], [1.0, 2.0, 3.0], 0),
            ]
        )
        report = si.inspect(data, SYSTEM_SIZE)
        self.assertEqual(report["status"], "complete")
        self.assertEqual(len(report["bones"]), 2)
        self.assertEqual(report["roots"], [0])
        self.assertEqual(report["max_depth"], 2)
        self.assertEqual(report["parent_array"], [si.ROOT_PARENT, 0])
        self.assertEqual(report["bones"][1]["model_position"], [1.0, 2.0, 3.0])

    def test_a_null_skeleton_is_not_a_failure(self):
        data = bytearray(build([([0.0, 0.0, 0.0, 1.0], [0.0, 0.0, 0.0], si.ROOT_PARENT)]))
        struct.pack_into("<Q", data, 0x40 + 0x18, 0)
        report = si.inspect(bytes(data), SYSTEM_SIZE)
        self.assertEqual(report["status"], "no_skeleton")
        self.assertEqual(report["bones"], [])

    def test_a_declared_key_count_that_disagrees_is_reported(self):
        data = bytearray(build([([0.0, 0.0, 0.0, 1.0], [0.0, 0.0, 0.0], si.ROOT_PARENT)]))
        struct.pack_into("<I", data, SKELETON + 0x1C, 99)
        report = si.inspect(bytes(data), SYSTEM_SIZE)
        self.assertEqual(report["status"], "partial")
        self.assertTrue(
            any(issue["code"] == "declared_key_count" for issue in report["issues"])
        )

    def test_a_system_length_outside_the_file_is_rejected(self):
        with self.assertRaises(ValueError):
            si.inspect(b"\x00" * 16, 32)


if __name__ == "__main__":
    unittest.main()
