import contextlib
import io
import json
import os
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _output
import trailer_probe


def build(path, trailer, meta=0x100, payload=0x100, trailer_len=None, shape=(4, 336, 6, 1, 1, 15, 9, 0xDA72573E)):
    if trailer_len is None:
        trailer_len = len(trailer)
    header = bytearray(0x40)
    struct.pack_into("<4I", header, 0, trailer_probe.MAGIC, meta, meta, trailer_len)
    struct.pack_into("<H", header, 0x1A, shape[0])
    struct.pack_into("<I", header, 0x1C, shape[1])
    struct.pack_into("<H", header, 0x20, shape[2])
    struct.pack_into("<H", header, 0x22, shape[3])
    struct.pack_into("<I", header, 0x24, 2)
    struct.pack_into("<I", header, 0x28, shape[7])
    header[0x2C] = shape[4]
    header[0x2D] = shape[5]
    header[0x2E] = shape[6]
    body = header + b"\x00" * (meta - 0x40) + b"\x11" * payload + trailer
    with open(path, "wb") as fh:
        fh.write(body)


def manifest(offset=0x100, stored=0x40):
    return {"rows": [{"row": 0, "payload_offset": offset, "stored_size": stored}]}


class TrailerProbeTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "synthetic.rpf")

    def tearDown(self):
        self.dir.cleanup()

    def test_consistent_header(self):
        build(self.path, b"T" * 64)
        result, header = trailer_probe.probe(self.path, manifest())
        self.assertEqual(result["file_size"], 0x240)
        self.assertEqual(result["trailing_region"], {"length": 64, "offset": 0x200})
        self.assertTrue(all(result["assertions"].values()))
        self.assertEqual(result["max_stored_end"], 0x140)

    def test_trailer_larger_than_file_is_refused(self):
        build(self.path, b"T" * 16, trailer_len=0x10000)
        with self.assertRaises(trailer_probe.BoundsError):
            trailer_probe.probe(self.path)

    def test_trailer_overlaps_metadata(self):
        build(self.path, b"T" * 0x100, meta=0x180, payload=0x80)
        with open(self.path, "r+b") as fh:
            fh.seek(0x0C)
            fh.write(struct.pack("<I", 0x1C0))
        result, _ = trailer_probe.probe(self.path)
        self.assertFalse(result["assertions"]["offset_above_metadata"])

    def test_unaligned_boundary(self):
        build(self.path, b"T" * 64, payload=0x104)
        result, _ = trailer_probe.probe(self.path)
        self.assertFalse(result["assertions"]["offset_aligned_16"])

    def test_manifest_end_above_boundary(self):
        build(self.path, b"T" * 64, payload=0x40)
        result, _ = trailer_probe.probe(self.path, manifest(offset=0x100, stored=0x100))
        self.assertFalse(result["assertions"]["max_stored_end_at_or_below_offset"])

    def test_identical_trailers_compare_equal(self):
        second = os.path.join(self.dir.name, "second.rpf")
        build(self.path, b"T" * 64)
        build(second, b"T" * 64)
        result = trailer_probe.compare([self.path, second])
        self.assertEqual(len(result["groups"]), 1)
        self.assertTrue(result["groups"][0]["equal_full"])
        self.assertTrue(result["groups"][0]["equal_first_16"])
        self.assertTrue(result["groups"][0]["equal_first_32"])

    def test_different_trailers_compare_unequal(self):
        second = os.path.join(self.dir.name, "second.rpf")
        build(self.path, b"T" * 64)
        build(second, b"U" * 64)
        result = trailer_probe.compare([self.path, second])
        group = result["groups"][0]
        self.assertFalse(group["equal_full"])
        self.assertFalse(group["equal_first_16"])
        self.assertFalse(group["equal_first_32"])

    def test_output_contains_no_bytes_or_digests(self):
        build(self.path, b"T" * 64)
        result, _ = trailer_probe.probe(self.path)
        text = json.dumps(result)
        self.assertNotIn("hash", text.lower())
        self.assertNotIn("digest", text.lower())
        self.assertNotIn("sha", text.lower())
        self.assertNotIn("T" * 8, text)

    def test_output_may_not_overwrite_the_input(self):
        build(self.path, b"T" * 64)
        with open(self.path, "rb") as fh:
            original = fh.read()
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = trailer_probe.main([self.path, "--output", self.path])
        self.assertEqual(code, 1)
        self.assertIn("input file", stderr.getvalue())
        with self.assertRaises(_output.OutputCollisionError):
            _output.guard_output(self.path, [self.path])
        with open(self.path, "rb") as fh:
            self.assertEqual(fh.read(), original)


if __name__ == "__main__":
    unittest.main()
