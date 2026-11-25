"""Synthetic tests for the texture candidate analyser. No game files needed."""

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import rds5  # noqa: E402
import textures  # noqa: E402
from test_rds5 import build_store  # noqa: E402


def _box(img):
    h, w = len(img), len(img[0])
    return [[(img[2 * y][2 * x] + img[2 * y][2 * x + 1]
              + img[2 * y + 1][2 * x] + img[2 * y + 1][2 * x + 1]) // 4
             for x in range(w // 2)] for y in range(h // 2)]


def _levels(width, height, count):
    """Build count levels where each is the exact box downsample of the previous."""
    levels = [[[((x // 2) + (y // 2) + 1) % 251 for x in range(width)]
               for y in range(height)]]
    w, h = width, height
    for _ in range(count - 1):
        levels.append(_box(levels[-1]))
        w, h = w // 2, h // 2
    return levels


def _flat(data):
    return bytes(v for row in data for v in row)


def _texture_store(levels, descriptor=None):
    """Store levels smallest first; each level is one stored-class block."""
    sizes = []
    blocks = []
    virtual = 0x1000
    flat = [_flat(level) for level in levels]
    for index in range(len(levels) - 1, -1, -1):
        blocks.append({"payload": flat[index], "class_id": 0, "virtual": virtual})
        sizes.append(len(flat[index]))
        virtual += len(flat[index])
    descriptor = descriptor or {}
    desc = {"width": len(levels[0][0]), "height": len(levels[0]), "mip": 0,
            "format_id": 200, "page": 1, "kind": 2, "tile": 0}
    desc.update(descriptor)
    return build_store(blocks, descriptors=[desc], end_virtual=virtual), sizes


class SlotLayoutTest(unittest.TestCase):
    def test_reverse_order_layout(self):
        layout = textures.slot_layout(512, 512, 6, "B8")
        self.assertEqual(layout["total"], 176128)
        self.assertEqual(layout["prelude"], 1280)
        entries = {level: (offset, size, slot)
                   for level, offset, size, slot in layout["entries"]}
        self.assertEqual(entries[5], (1280, 128, 256))
        self.assertEqual(entries[4], (1536, 512, 512))
        self.assertEqual(entries[3], (2048, 2048, 2048))
        self.assertEqual(entries[0], (45056, 131072, 131072))

    def test_minimum_slot(self):
        layout = textures.slot_layout(16, 16, 1, "L1")
        self.assertEqual(layout["total"], 0x1000)
        self.assertEqual(layout["prelude"], 3840)
        self.assertEqual(layout["entries"], [(0, 3840, 256, 256)])

    def test_unit_sizes(self):
        self.assertEqual(textures.level_bytes(512, 512, "B8"), 131072)
        self.assertEqual(textures.level_bytes(128, 256, "L1"), 32768)
        self.assertEqual(textures.level_bytes(5, 3, "B16"), 2 * 1 * 16)


class BlockDecoderTest(unittest.TestCase):
    def test_bc1_four_colour(self):
        block = bytes([0x00, 0xF8, 0x1F, 0x00, 0x00, 0x00, 0x00, 0x00])
        pixels = textures.decode_bc1_block(block)
        self.assertEqual(pixels[0][0], (255, 0, 0))
        self.assertEqual(pixels[3][3], (255, 0, 0))

    def test_bc1_three_colour(self):
        block = bytes([0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        pixels = textures.decode_bc1_block(block)
        self.assertEqual(pixels[0][0], (0, 0, 0))

    def test_bc4_endpoints(self):
        block = bytes([0x00, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        self.assertEqual(textures.decode_bc4_block(block)[0], 0)
        block = bytes([0x00, 0xFF] + [0xFF] * 6)
        self.assertEqual(textures.decode_bc4_block(block)[0], 255)

    def test_bc4_two_planes(self):
        first = bytes([0x00, 0xFF] + [0x00] * 6)
        second = bytes([0xFF, 0x00] + [0x00] * 6)
        img = textures.decode_bc4(first + second, 4, 4, 16, 2)
        self.assertEqual(img[0][0], (0, 255))

    def test_short_block_rejected(self):
        with self.assertRaises(ValueError):
            textures.decode_bc1_block(b"\x00" * 7)


class FirstByteStatsTest(unittest.TestCase):
    def test_mode_prefix_statistics(self):
        data = bytes([0x40]) + bytes(15) + bytes([0x20]) + bytes(15)
        stats = textures.block_first_byte_stats(data, 16)
        self.assertEqual(stats["blocks"], 2)
        self.assertEqual(stats["multiple_of_16_fraction"], 1.0)
        self.assertEqual(stats["lowest_set_bit_counts"], {"5": 1, "6": 1})


class AnalyseTest(unittest.TestCase):
    def _write(self, blob):
        handle = tempfile.NamedTemporaryFile(delete=False, suffix=".ttpf")
        handle.write(blob)
        handle.close()
        self.addCleanup(os.unlink, handle.name)
        return handle.name

    def test_aligned_levels_and_pass(self):
        levels = _levels(1024, 512, 4)
        blob, sizes = _texture_store(levels)
        path = self._write(blob)
        info = rds5.parse(path)
        report = textures.analyse(path, info, 0, "L1", decoder="channels",
                                  channels=1)
        self.assertEqual(report["decoded_bytes"], sum(sizes))
        self.assertEqual(report["size_candidate_levels"], [4])
        self.assertEqual(len(report["aligned_levels"]), 4)
        self.assertTrue(report["mip_check"]["pass"])
        self.assertLess(report["mip_check"]["worst_error"], 0.1)

    def test_shuffled_level_fails(self):
        levels = _levels(1024, 512, 4)
        # Rotate the second-largest level so its box relation no longer holds.
        levels[2] = [[0] * len(levels[2][0]) for _ in levels[2]]
        blob, _sizes = _texture_store(levels)
        path = self._write(blob)
        info = rds5.parse(path)
        report = textures.analyse(path, info, 0, "L1", decoder="channels",
                                  channels=1)
        self.assertFalse(report["mip_check"]["pass"])

    def test_cli_json(self):
        levels = _levels(1024, 512, 4)
        blob, _sizes = _texture_store(levels)
        path = self._write(blob)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = textures.main(["probe", path, "--descriptor", "0",
                                  "--unit", "L1", "--decoder", "channels",
                                  "--channels", "1", "--json"])
        self.assertEqual(code, 0)
        report = json.loads(out.getvalue())
        self.assertTrue(report["mip_check"]["pass"])

    def test_block_byte_cap_is_honoured(self):
        levels = _levels(1024, 512, 4)
        blob, _sizes = _texture_store(levels)
        path = self._write(blob)
        info = rds5.parse(path)
        with self.assertRaises(rds5.Rds5Error):
            textures.analyse(path, info, 0, "L1", max_block_bytes=1024)

    def test_cli_block_byte_cap(self):
        levels = _levels(1024, 512, 4)
        blob, _sizes = _texture_store(levels)
        path = self._write(blob)
        with contextlib.redirect_stderr(io.StringIO()) as err:
            code = textures.main(["probe", path, "--descriptor", "0",
                                  "--unit", "L1", "--max-block-bytes", "1024"])
        self.assertEqual(code, 1)
        self.assertIn("exceeds limit", err.getvalue())

    def test_descriptor_index_rejected(self):
        levels = _levels(256, 256, 2)
        blob, _sizes = _texture_store(levels)
        path = self._write(blob)
        with contextlib.redirect_stderr(io.StringIO()):
            code = textures.main(["probe", path, "--descriptor", "5",
                                  "--unit", "L1"])
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
