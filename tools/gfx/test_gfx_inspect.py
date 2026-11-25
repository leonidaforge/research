import json
import os
import struct
import tempfile
import unittest

import gfx_inspect

MAGIC = b"GFX"


def encode_tag(code, payload=b""):
    length = len(payload)
    if length < 0x3F:
        return struct.pack("<H", (code << 6) | length) + payload
    return struct.pack("<H", (code << 6) | 0x3F) + struct.pack("<I", length) + payload


def build_raw(body, nbits=17, frame_rate=30.0, frame_count=1, version=0x2A,
              magic=MAGIC, length_adjust=0):
    rect_bytes = gfx_inspect.rect_size(nbits)
    rect = bytes([(nbits << 3) & 0xF8]) + b"\x00" * (rect_bytes - 1)
    header = magic + bytes([version]) + struct.pack("<I", 0) + rect
    header += struct.pack("<HH", int(round(frame_rate * 256)), frame_count)
    raw = header + body
    raw = raw[:4] + struct.pack("<I", len(raw) + length_adjust) + raw[8:]
    return raw


def build_gfx(tags=None, **kwargs):
    if tags is None:
        tags = [(2, b"unit"), (1, b""), (0, b"")]
    body = b"".join(encode_tag(code, payload) for code, payload in tags)
    return build_raw(body, **kwargs)


class InspectTests(unittest.TestCase):
    def test_parses_short_tags_and_final_headers(self):
        raw = build_gfx(tags=[(2, b"unit"), (1, b""), (0, b"")])
        report = gfx_inspect.inspect_bytes(raw)
        self.assertEqual(report["size"], len(raw))
        self.assertEqual(report["container"]["version"], 0x2A)
        self.assertTrue(report["container"]["length_matches"])
        self.assertEqual(report["header"]["rect_nbits"], 17)
        self.assertEqual(report["header"]["rect_bytes"], 10)
        self.assertEqual(report["header"]["frame_rate"], 30.0)
        self.assertEqual(report["header"]["frame_count"], 1)
        self.assertEqual(report["header"]["first_tag_offset"], 0x16)
        self.assertEqual(report["tags"]["count"], 3)
        self.assertEqual(report["tags"]["first_code"], 2)
        self.assertEqual(report["tags"]["last_two_codes"], [1, 0])
        self.assertEqual(report["trailer"]["last_four_bytes"], "40000000")

    def test_parses_long_tag_form(self):
        raw = build_gfx(tags=[(2, b"A" * 70), (1, b""), (0, b"")])
        report = gfx_inspect.inspect_bytes(raw)
        self.assertEqual(report["tags"]["first_code"], 2)
        self.assertEqual(report["tags"]["first_length"], 70)
        self.assertEqual(report["tags"]["count"], 3)

    def test_tracks_sprite_nesting(self):
        nested = struct.pack("<HH", 1, 1)
        nested += encode_tag(2, b"x") + encode_tag(1) + encode_tag(0)
        raw = build_gfx(tags=[(39, nested), (1, b""), (0, b"")])
        report = gfx_inspect.inspect_bytes(raw)
        self.assertEqual(report["tags"]["count"], 3)
        self.assertEqual(report["tags"]["sprite_count"], 1)
        self.assertEqual(report["tags"]["nested_tag_count"], 3)
        self.assertEqual(report["tags"]["total_tags"], 6)
        self.assertEqual(report["tags"]["max_depth"], 1)

    def test_rejects_truncated_tag(self):
        body = struct.pack("<H", (2 << 6) | 10) + b"abcd"
        with self.assertRaises(gfx_inspect.GfxError):
            gfx_inspect.inspect_bytes(build_raw(body))

    def test_rejects_bad_rect(self):
        raw = MAGIC + bytes([0x2A]) + struct.pack("<I", 9) + bytes([31 << 3]) + b"\x00"
        raw = raw[:4] + struct.pack("<I", len(raw)) + raw[8:]
        with self.assertRaises(gfx_inspect.GfxError):
            gfx_inspect.inspect_bytes(raw)

    def test_rejects_other_version(self):
        raw = build_gfx(version=0x2B)
        with self.assertRaises(gfx_inspect.GfxError):
            gfx_inspect.inspect_bytes(raw)

    def test_rejects_wrong_magic(self):
        raw = build_gfx(magic=b"GFY")
        with self.assertRaises(gfx_inspect.GfxError):
            gfx_inspect.inspect_bytes(raw)

    def test_rejects_length_mismatch(self):
        raw = build_gfx(length_adjust=1)
        with self.assertRaises(gfx_inspect.GfxError):
            gfx_inspect.inspect_bytes(raw)

    def test_rejects_trailing_bytes_after_end(self):
        raw = build_raw(encode_tag(2, b"unit") + encode_tag(1) + encode_tag(0) + b"\x00")
        with self.assertRaises(gfx_inspect.GfxError):
            gfx_inspect.inspect_bytes(raw)

    def test_report_does_not_contain_payload_text(self):
        raw = build_gfx(tags=[(2, b"secret_movie_name"), (1, b""), (0, b"")])
        report = gfx_inspect.inspect_bytes(raw)
        self.assertNotIn("secret_movie_name", json.dumps(report))

    def test_output_inside_input_directory_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            source = os.path.join(directory, "sample.bin")
            output = os.path.join(directory, "report.txt")
            self.assertTrue(gfx_inspect._output_is_inside_input(output, [source]))
            other = os.path.join(directory, "..", "outside.txt")
            self.assertFalse(gfx_inspect._output_is_inside_input(other, [source]))


if __name__ == "__main__":
    unittest.main()
