import os
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
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

    def test_index_store_model(self):
        build(self.path, prim=0x300, meta=0x330, secondary=2, rows=3, width=1)
        result = secondary_probe.probe(self.path)
        self.assertEqual(result["secondary_bytes"], 48)
        self.assertTrue(result["model_index_store"]["fits"])
        self.assertEqual(result["model_index_store"]["index_bytes"], 6)
        self.assertEqual(result["model_index_store"]["index_aligned_8"], 8)
        self.assertEqual(result["model_index_store"]["pool_bytes"], 40)
        self.assertEqual(result["model_direct_values"]["width"], 8)

    def test_single_secondary_column(self):
        build(self.path, prim=0x340, meta=0x360, secondary=1, rows=2, width=1)
        result = secondary_probe.probe(self.path)
        self.assertEqual(result["secondary_bytes"], 32)
        self.assertEqual(result["model_index_store"]["index_bytes"], 2)
        self.assertEqual(result["model_index_store"]["pool_bytes"], 24)
        self.assertEqual(result["model_direct_values"]["width"], 16)

    def test_non_integer_direct_width(self):
        build(self.path, prim=0x300, meta=0x330, secondary=2, rows=5, width=1)
        result = secondary_probe.probe(self.path)
        self.assertFalse(result["model_direct_values"]["same_width_for_all_secondary_columns"])
        self.assertIsNone(result["model_direct_values"]["width"])
        self.assertTrue(result["model_index_store"]["fits"])

    def test_secondary_end_below_primary_is_refused(self):
        build(self.path, prim=0x340, meta=0x300)
        with self.assertRaises(secondary_probe.BoundsError):
            secondary_probe.probe(self.path)

    def test_summary_counts_d_values(self):
        second = os.path.join(self.dir.name, "second.rpf")
        build(self.path, prim=0x300, meta=0x330, secondary=2, rows=3)
        build(second, prim=0x340, meta=0x360, secondary=1, rows=2)
        result = secondary_probe.summarize([self.path, second])
        self.assertEqual(result["summary"]["archives"], 2)
        self.assertEqual(result["summary"]["d_values"], {"1": 1, "2": 1})
        self.assertEqual(result["summary"]["d_above_one"], 1)
        self.assertEqual(result["summary"]["model_index_store_fits"], 2)


if __name__ == "__main__":
    unittest.main()
