"""Synthetic tests for aabb_census.py. No game files are used."""

import json
import os
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import aabb_census  # noqa: E402
import drawable_inspect as di  # noqa: E402
from tests.test_drawable_inspect import Fixture, SYSTEM_SIZE  # noqa: E402


class CensusTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

    def write(self, name, system, graphics):
        path = os.path.join(self.temp.name, name)
        with open(path, "wb") as handle:
            handle.write(system + graphics)
        return path

    def manifest(self, records):
        path = os.path.join(self.temp.name, "manifest.jsonl")
        with open(path, "w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record) + "\n")
        return path

    def test_counts_pass_and_fail(self):
        system, graphics = Fixture().build()
        good = self.write("good.bin", system, graphics)
        data = bytearray(system + graphics)
        report = di.analyze(good, SYSTEM_SIZE)
        model = report["lod_slots"][0]["models"][0]
        struct.pack_into("<f", data, model["aabb"]["offset"], -0.5)
        bad = self.write("bad.bin", bytes(data), b"")
        path = self.manifest(
            [
                {"id": "good", "file": good, "system_length": SYSTEM_SIZE},
                {"id": "bad", "file": bad, "system_length": SYSTEM_SIZE},
            ]
        )
        summary = aabb_census.census(path)
        self.assertEqual(summary["entries"], 2)
        self.assertEqual(summary["errors"], [])
        self.assertEqual(summary["models"], 2)
        self.assertEqual(summary["models_multi_geometry"], 2)
        self.assertEqual(summary["models_one_geometry"], 0)
        self.assertEqual(summary["aabb_records"], 6)
        self.assertEqual(summary["extra_min_equal"], 5)
        self.assertEqual(summary["extra_max_equal"], 6)
        self.assertEqual(summary["model_union_pass"], 1)
        self.assertEqual(summary["model_union_fail"], 1)
        self.assertEqual(summary["multi_geometry_union_pass"], 1)
        self.assertEqual(summary["multi_geometry_union_fail"], 1)
        self.assertEqual(summary["drawables_with_bounds"], 2)
        self.assertEqual(summary["header_pass"], 1)
        self.assertEqual(summary["header_fail"], 1)
        self.assertEqual(summary["exception_causes"], {"three_null_lod_slots": 1})
        self.assertEqual(summary["exceptions"][0]["id"], "bad")
        self.assertEqual(summary["exceptions"][0]["null_lod_slots"], 3)

    def test_malformed_manifest_is_refused(self):
        path = os.path.join(self.temp.name, "broken.jsonl")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write('{"id": "x"}\n')
        with self.assertRaises(aabb_census.CensusError):
            aabb_census.census(path)

    def test_missing_file_is_counted_not_raised(self):
        path = self.manifest(
            [{"id": "missing", "file": os.path.join(self.temp.name, "absent.bin"), "system_length": 16}]
        )
        summary = aabb_census.census(path)
        self.assertEqual(summary["entries"], 1)
        self.assertEqual(len(summary["errors"]), 1)
        self.assertEqual(summary["errors"][0]["id"], "missing")


if __name__ == "__main__":
    unittest.main()
