import os
import struct
import tempfile
import unittest

import gfx_inspect

MAGIC = b"GFX*"
TAIL = bytes.fromhex("fa0104000000000e00")
INTER = bytes.fromhex("00004411090000004302")
TRAILER = b".Main\x00\x40\x00\x00\x00"
NAME_OFFSETS = {
    (0x70, 0x0A): 0x20,
    (0x70, 0x0B): 0x20,
    (0x78, 0x05): 0x21,
    (0x80, 0x02): 0x21,
    (0x88, 0x01): 0x22,
}


def build_sample(byte8=0x88, byte0a=0x01, name1=b"alpha", name2=b"unit_alpha_Main",
                 body=b"\x10\x20\x30\x40", final=b"unit.alpha"):
    name_offset = NAME_OFFSETS[(byte8, byte0a)]
    pretail = name_offset - 0x16
    header = bytes([byte8, 0x00, byte0a]) + b"\x11" * pretail
    header += TAIL + struct.pack(">H", len(name1))
    header += name1
    header += INTER + b"\x00\x00\x00\x00" + b"\x0a"
    header += name2 + b"\x00"
    raw = MAGIC + struct.pack("<I", 0) + header + body + final + TRAILER
    return raw[:4] + struct.pack("<I", len(raw)) + raw[8:]


class InspectTests(unittest.TestCase):
    def test_parses_88_variant(self):
        report = gfx_inspect.inspect_bytes(build_sample())
        self.assertEqual(report["size"], len(build_sample()))
        self.assertEqual(report["variant"]["byte_08"], "0x88")
        self.assertEqual(report["variant"]["name1_offset"], 0x22)
        self.assertTrue(report["size_field"]["equals_file_size"])
        self.assertEqual(report["name2"]["length"], len(b"unit_alpha_Main"))
        self.assertEqual(report["marker_counts"], {
            "pre_name_tail": 1, "interstitial": 1, "trailer": 1})

    def test_parses_80_and_70_variants(self):
        for key, offset in [((0x80, 0x02), 0x21), ((0x70, 0x0B), 0x20)]:
            report = gfx_inspect.inspect_bytes(build_sample(byte8=key[0], byte0a=key[1]))
            self.assertEqual(report["variant"]["name1_offset"], offset)
            self.assertEqual(report["name1"]["offset"], offset)

    def test_rejects_unknown_variant(self):
        raw = build_sample()
        raw = raw[:0x08] + bytes([0x90, 0x00, 0x01]) + raw[0x0B:]
        raw = raw[:4] + struct.pack("<I", len(raw)) + raw[8:]
        with self.assertRaises(gfx_inspect.GfxError):
            gfx_inspect.inspect_bytes(raw)

    def test_rejects_wrong_magic(self):
        raw = b"NOPE" + build_sample()[4:]
        with self.assertRaises(gfx_inspect.GfxError):
            gfx_inspect.inspect_bytes(raw)

    def test_rejects_size_mismatch(self):
        raw = build_sample()
        raw = raw[:4] + struct.pack("<I", len(raw) + 1) + raw[8:]
        with self.assertRaises(gfx_inspect.GfxError):
            gfx_inspect.inspect_bytes(raw)

    def test_rejects_truncated_prefix(self):
        with self.assertRaises(gfx_inspect.GfxError):
            gfx_inspect.inspect_bytes(build_sample()[:0x30])

    def test_rejects_missing_interstitial(self):
        raw = build_sample()
        index = raw.index(INTER)
        raw = raw[:index] + b"\x00" * len(INTER) + raw[index + len(INTER):]
        raw = raw[:4] + struct.pack("<I", len(raw)) + raw[8:]
        with self.assertRaises(gfx_inspect.GfxError):
            gfx_inspect.inspect_bytes(raw)

    def test_rejects_second_run_without_first(self):
        with self.assertRaises(gfx_inspect.GfxError):
            gfx_inspect.inspect_bytes(build_sample(name2=b"other_Main"))

    def test_output_inside_input_directory_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            source = os.path.join(directory, "sample.bin")
            output = os.path.join(directory, "report.txt")
            self.assertTrue(gfx_inspect._output_is_inside_input(output, [source]))
            other = os.path.join(directory, "..", "outside.txt")
            self.assertFalse(gfx_inspect._output_is_inside_input(other, [source]))


if __name__ == "__main__":
    unittest.main()
