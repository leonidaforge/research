import json
import struct
import unittest

import psin_inspect


def section(tag, body):
    return tag + struct.pack(">I", 8 + len(body)) + body


def sample(sections, first_offset=48, header_tail=b"\0" * 8):
    prefix = b"PSIN" + struct.pack(">I", first_offset) + header_tail
    if len(prefix) > first_offset:
        raise ValueError("first offset is inside the header")
    return prefix + b"\0" * (first_offset - len(prefix)) + b"".join(sections)


class InspectTests(unittest.TestCase):
    def test_reads_two_sections_to_the_file_end(self):
        raw = sample([
            section(b"TST1", b"A" * 16),
            section(b"TST2", b"B" * 24),
        ])
        report = psin_inspect.inspect_bytes(raw)
        self.assertEqual(report["magic"], "PSIN")
        self.assertEqual(report["header"]["first_section_offset"], 48)
        self.assertEqual(report["tag_sequence"], ["TST1", "TST2"])
        self.assertEqual([item["body_length"] for item in report["sections"]], [16, 24])
        self.assertTrue(report["checks"]["section_walk_ends_at_file_size"])
        self.assertTrue(report["checks"]["field_06_equals_low16"])
        self.assertFalse(report["checks"]["first_section_offset_equals_size"])
        self.assertFalse(report["checks"]["field_06_equals_size"])

    def test_accepts_unaligned_first_section_offset(self):
        raw = sample([section(b"TST1", b"A" * 16)], first_offset=51)
        report = psin_inspect.inspect_bytes(raw)
        self.assertEqual(report["header"]["first_section_offset"], 51)
        self.assertFalse(report["checks"]["first_section_offset_aligned_16"])

    def test_reports_high_half_and_low_half_of_a_large_offset(self):
        raw = sample([section(b"TST1", b"A" * 16)], first_offset=0x10040)
        report = psin_inspect.inspect_bytes(raw)
        header = report["header"]
        self.assertEqual(header["first_section_offset"], 0x10040)
        self.assertEqual(header["first_section_offset_high16"], 1)
        self.assertEqual(header["first_section_offset_low16"], 0x40)
        self.assertEqual(header["field_06_be"], 0x40)
        self.assertTrue(report["checks"]["field_06_equals_low16"])

    def test_reports_the_unresolved_eight_bytes_as_raw_and_integer_readings(self):
        raw = sample([section(b"TST1", b"A" * 16)], header_tail=b"\x01\x02\x03\x04\x05\x06\x07\x08")
        report = psin_inspect.inspect_bytes(raw)
        header = report["header"]
        self.assertEqual(header["field_08_0f"], "0102030405060708")
        self.assertEqual(header["field_08_be"], 0x01020304)
        self.assertEqual(header["field_0c_le"], 0x08070605)

    def test_report_is_json_serializable(self):
        raw = sample([section(b"TST1", b"A" * 16)])
        report = psin_inspect.inspect_bytes(raw)
        self.assertIn("TST1", json.dumps(report))

    def test_rejects_wrong_magic(self):
        raw = sample([section(b"TST1", b"A" * 16)])
        with self.assertRaises(psin_inspect.PsinError):
            psin_inspect.inspect_bytes(b"NOPE" + raw[4:])

    def test_rejects_short_header(self):
        with self.assertRaises(psin_inspect.PsinError):
            psin_inspect.inspect_bytes(b"PSIN" + b"\0" * 8)

    def test_rejects_offset_inside_header(self):
        raw = b"PSIN" + struct.pack(">I", 15) + b"\0" * 8
        with self.assertRaises(psin_inspect.PsinError):
            psin_inspect.inspect_bytes(raw)

    def test_rejects_offset_past_file(self):
        raw = b"PSIN" + struct.pack(">I", 64) + b"\0" * 8
        with self.assertRaises(psin_inspect.PsinError):
            psin_inspect.inspect_bytes(raw)

    def test_rejects_non_printable_tag(self):
        raw = sample([b"\x00\x01\x02\x03" + struct.pack(">I", 8)])
        with self.assertRaises(psin_inspect.PsinError):
            psin_inspect.inspect_bytes(raw)

    def test_rejects_length_below_section_header(self):
        raw = sample([b"TST1" + struct.pack(">I", 7)])
        with self.assertRaises(psin_inspect.PsinError):
            psin_inspect.inspect_bytes(raw)

    def test_rejects_section_past_file_end(self):
        raw = sample([b"TST1" + struct.pack(">I", 32) + b"A" * 8])
        with self.assertRaises(psin_inspect.PsinError):
            psin_inspect.inspect_bytes(raw)

    def test_rejects_section_cap(self):
        raw = sample([
            section(b"TST1", b"A" * 16),
            section(b"TST2", b"B" * 16),
        ])
        with self.assertRaises(psin_inspect.PsinError):
            psin_inspect.inspect_bytes(raw, max_sections=1)


if __name__ == "__main__":
    unittest.main()
