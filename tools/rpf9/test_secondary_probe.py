import contextlib
import io
import os
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _output
import secondary_probe


def build(path, prim, meta, columns=6, secondary=1, rows=3, width=1):
    header = bytearray(0x40)
    struct.pack_into("<4I", header, 0, secondary_probe.MAGIC, meta, prim, 64)
    struct.pack_into("<H", header, 0x1A, 4)
    struct.pack_into("<I", header, 0x1C, 336)
    struct.pack_into("<H", header, 0x20, columns)
    struct.pack_into("<H", header, 0x22, secondary)
    struct.pack_into("<I", header, 0x24, rows)
    struct.pack_into("<I", header, 0x28, 0xDA72573E)
    header[0x2C] = width
    header[0x2D] = 15
    header[0x2E] = 9
    with open(path, "wb") as fh:
        fh.write(header + b"\x00" * (meta - 0x40) + b"\x00" * 64)


class SecondaryProbeTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "synthetic.rpf")

    def tearDown(self):
        self.dir.cleanup()

    def test_index_store_arithmetic(self):
        build(self.path, prim=0x300, meta=0x330, secondary=2, rows=3, width=1)
        result = secondary_probe.probe(self.path)
        self.assertEqual(result["layout"]["area_bytes"], 48)
        self.assertEqual(result["layout"]["store_start"], 0x300)
        self.assertEqual(result["layout"]["index_bytes"], 6)
        self.assertEqual(result["layout"]["index_end"], 0x306)
        self.assertEqual(result["layout"]["pool_start"], 0x308)
        self.assertEqual(result["layout"]["pool_bytes"], 40)
        self.assertTrue(result["model_index_store"]["necessary_condition_fits"])
        self.assertEqual(result["model_direct_values"]["width"], 8)
        self.assertFalse(result["separation"]["models_make_different_size_predictions"])
        self.assertFalse(result["separation"]["observation_selects"])

    def test_store_start_uses_cell_width(self):
        build(self.path, prim=0x301, meta=0x340, secondary=2, rows=3, width=1)
        result = secondary_probe.probe(self.path)
        self.assertEqual(result["layout"]["start_padding"], 0)
        self.assertEqual(result["layout"]["store_start"], 0x301)
        self.assertEqual(result["layout"]["pool_start"], 0x308)

    def test_store_start_rounds_by_two_when_f_is_two(self):
        build(self.path, prim=0x301, meta=0x340, secondary=2, rows=3, width=2)
        result = secondary_probe.probe(self.path)
        self.assertEqual(result["layout"]["start_padding"], 1)
        self.assertEqual(result["layout"]["store_start"], 0x302)
        self.assertEqual(result["layout"]["index_bytes"], 12)

    def test_single_secondary_column(self):
        build(self.path, prim=0x340, meta=0x360, secondary=1, rows=2, width=1)
        result = secondary_probe.probe(self.path)
        self.assertEqual(result["layout"]["area_bytes"], 32)
        self.assertEqual(result["layout"]["index_bytes"], 2)
        self.assertEqual(result["layout"]["pool_bytes"], 24)
        self.assertEqual(result["model_direct_values"]["width"], 16)

    def test_non_integer_direct_width(self):
        build(self.path, prim=0x300, meta=0x330, secondary=2, rows=5, width=1)
        result = secondary_probe.probe(self.path)
        self.assertFalse(result["model_direct_values"]["same_width_for_all_secondary_columns"])
        self.assertIsNone(result["model_direct_values"]["width"])
        self.assertTrue(result["model_index_store"]["necessary_condition_fits"])
        self.assertTrue(result["separation"]["models_make_different_size_predictions"])
        self.assertFalse(result["separation"]["observation_selects"])

    def test_secondary_end_below_primary_is_refused(self):
        build(self.path, prim=0x340, meta=0x300)
        with self.assertRaises(secondary_probe.BoundsError):
            secondary_probe.probe(self.path)

    def test_summary_counts_models_separately(self):
        second = os.path.join(self.dir.name, "second.rpf")
        build(self.path, prim=0x300, meta=0x330, secondary=2, rows=3)
        build(second, prim=0x340, meta=0x360, secondary=1, rows=2)
        result = secondary_probe.summarize([self.path, second])
        self.assertEqual(result["summary"]["archives"], 2)
        self.assertEqual(result["summary"]["d_values"], {"1": 1, "2": 1})
        self.assertEqual(result["summary"]["d_above_one"], 1)
        self.assertEqual(result["summary"]["model_index_store_necessary_fits"], 2)
        self.assertEqual(result["summary"]["model_direct_same_width_fits"], 2)
        self.assertEqual(result["summary"]["size_predictions_differ"], 0)
        self.assertEqual(result["summary"]["size_decided_archives"], 0)

    def test_output_may_not_overwrite_the_input(self):
        build(self.path, prim=0x300, meta=0x330, secondary=2, rows=3)
        with open(self.path, "rb") as fh:
            original = fh.read()
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = secondary_probe.main([self.path, "--output", self.path])
        self.assertEqual(code, 1)
        self.assertIn("input file", stderr.getvalue())
        with self.assertRaises(_output.OutputCollisionError):
            _output.guard_output(self.path, [self.path])
        with open(self.path, "rb") as fh:
            self.assertEqual(fh.read(), original)


if __name__ == "__main__":
    unittest.main()
