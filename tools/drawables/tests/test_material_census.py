"""Synthetic tests for material_census.py. No game files are used."""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import material_census  # noqa: E402
from tests.test_drawable_inspect import Fixture, SYSTEM_SIZE  # noqa: E402


class MaterialCensusTests(unittest.TestCase):
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

    def test_counts(self):
        system, graphics = Fixture().build()
        path = self.write("drawable.bin", system, graphics)
        manifest = self.manifest(
            [{"id": "one", "file": path, "system_length": SYSTEM_SIZE}]
        )
        summary = material_census.census(manifest)
        self.assertEqual(summary["entries"], 1)
        self.assertEqual(summary["errors"], [])
        self.assertEqual(summary["drawables"], 1)
        self.assertEqual(summary["shaders"], 2)
        self.assertEqual(summary["declared_slots"], 4)
        self.assertEqual(summary["bound"], 2)
        self.assertEqual(summary["unbound"], 2)
        self.assertEqual(summary["null_key"], 0)
        self.assertEqual(len(summary["shader_hashes"]), 2)
        self.assertEqual(summary["shader_hashes"]["0x11223344"], 1)
        self.assertEqual(summary["shader_hashes"]["0x11223345"], 1)
        self.assertEqual(summary["parameter_hashes"]["0x00001000"], 2)
        self.assertEqual(summary["parameter_hashes"]["0x00001001"], 2)

    def test_malformed_manifest_is_refused(self):
        path = os.path.join(self.temp.name, "broken.jsonl")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("[]\n")
        with self.assertRaises(material_census.CensusError):
            material_census.census(path)


if __name__ == "__main__":
    unittest.main()
