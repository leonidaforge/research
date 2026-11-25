import json
import struct
import unittest

import psin_inspect
import synthetic


class InspectTests(unittest.TestCase):
    def test_lsch_family_descriptor_table_and_checksum(self):
        raw = synthetic.lsch_document([4, 8, 12])
        report = psin_inspect.inspect_bytes(raw)
        self.assertEqual(report["family"], "LSCH")
        self.assertEqual(report["family_data"]["descriptor_count"], 3)
        self.assertTrue(report["family_data"]["unique_solution"])
        self.assertEqual(report["family_data"]["solutions"], [3])
        self.assertTrue(report["family_data"]["formula_matches"])
        self.assertEqual(report["family_data"]["sum_aligned_lengths"], 48)
        self.assertTrue(report["family_data"]["descriptors"][0]["marker_aa"])
        self.assertEqual(
            report["tag_sequence"],
            ["LSCH", "LENM", "LSNS", "LGID", "LRSC", "CHKS"],
        )
        self.assertTrue(report["checks"]["checksum_ok"])
        self.assertTrue(report["integrity"]["total_length_equals_size"])
        self.assertTrue(report["integrity"]["tail_is_zppp"])

    def test_lsch_zero_descriptors_has_a_unique_solution(self):
        report = psin_inspect.inspect_bytes(synthetic.lsch_document([]))
        self.assertEqual(report["family"], "LSCH")
        self.assertEqual(report["family_data"]["descriptor_count"], 0)
        self.assertTrue(report["family_data"]["unique_solution"])
        self.assertTrue(report["checks"]["checksum_ok"])

    def test_lsch_variant_requires_alignment(self):
        report = psin_inspect.inspect_bytes(synthetic.lsch_document([4, 8, 12]))
        variants = report["family_data"]["variants"]
        self.assertEqual(
            variants["table_0x08_constant_0x10_length_0x04_aligned"], [3]
        )
        self.assertEqual(variants["table_0x08_constant_0x10_length_0x04_raw"], [])
        self.assertEqual(variants["table_0x10_constant_0x10_length_0x04_aligned"], [])
        self.assertEqual(variants["table_0x08_constant_0x10_length_0x00_aligned"], [])

    def test_pmap_family_is_classified_not_failed(self):
        raw = synthetic.pmap_document()
        report = psin_inspect.inspect_bytes(raw)
        self.assertEqual(report["family"], "PMAP")
        self.assertEqual(report["family_data"]["grammar"], "pre-section area")
        self.assertIsNone(report["family_data"]["descriptor_table"])
        self.assertTrue(report["family_data"]["header_marker_70"])
        self.assertEqual(
            report["tag_sequence"], ["PMAP", "PSCH", "PSIG", "STNS", "CHKS"]
        )
        self.assertTrue(report["checks"]["checksum_ok"])

    def test_pmap_descriptor_relation_has_no_solution(self):
        raw = synthetic.pmap_document()
        solutions = psin_inspect.solve_descriptor_counts(raw)
        self.assertEqual(solutions, [])

    def test_pmap_accepts_unaligned_first_section_offset(self):
        raw = synthetic.pmap_document(unaligned=True)
        report = psin_inspect.inspect_bytes(raw)
        self.assertEqual(report["family"], "PMAP")
        self.assertFalse(report["checks"]["first_section_offset_aligned_16"])
        self.assertTrue(report["checks"]["checksum_ok"])

    def test_corrupted_payload_fails_the_checksum(self):
        raw = synthetic.corrupted_lsch()
        report = psin_inspect.inspect_bytes(raw)
        self.assertFalse(report["checks"]["checksum_ok"])
        self.assertNotEqual(
            report["integrity"]["computed_checksum"],
            report["integrity"]["stored_checksum"],
        )
        self.assertTrue(report["integrity"]["total_length_equals_size"])

    def test_report_is_json_serializable(self):
        raw = synthetic.lsch_document([4, 8])
        report = psin_inspect.inspect_bytes(raw)
        self.assertIn("LSCH", json.dumps(report))

    def test_rejects_wrong_magic(self):
        raw = synthetic.lsch_document([4])
        with self.assertRaises(psin_inspect.PsinError):
            psin_inspect.inspect_bytes(b"NOPE" + raw[4:])

    def test_rejects_short_header(self):
        with self.assertRaises(psin_inspect.PsinError):
            psin_inspect.inspect_bytes(b"PSIN" + b"\0" * 2)

    def test_rejects_offset_inside_header(self):
        raw = b"PSIN" + struct.pack(">I", 7) + b"\0" * 8
        with self.assertRaises(psin_inspect.PsinError):
            psin_inspect.inspect_bytes(raw)

    def test_rejects_offset_past_file(self):
        raw = b"PSIN" + struct.pack(">I", 64) + b"\0" * 8
        with self.assertRaises(psin_inspect.PsinError):
            psin_inspect.inspect_bytes(raw)

    def test_rejects_non_printable_tag(self):
        raw = synthetic.with_checksum(b"PSIN" + struct.pack(">I", 16) + b"\0" * 8, [])
        data = bytearray(raw)
        data[16:20] = b"\x00\x01\x02\x03"
        with self.assertRaises(psin_inspect.PsinError):
            psin_inspect.inspect_bytes(bytes(data))

    def test_rejects_length_below_section_header(self):
        prefix = b"PSIN" + struct.pack(">I", 16) + b"\0" * 8
        raw = prefix + b"TST1" + struct.pack(">I", 7)
        with self.assertRaises(psin_inspect.PsinError):
            psin_inspect.inspect_bytes(raw)

    def test_rejects_section_past_file_end(self):
        prefix = b"PSIN" + struct.pack(">I", 16) + b"\0" * 8
        raw = prefix + b"TST1" + struct.pack(">I", 32) + b"A" * 8
        with self.assertRaises(psin_inspect.PsinError):
            psin_inspect.inspect_bytes(raw)

    def test_rejects_section_cap(self):
        raw = synthetic.lsch_document([4])
        with self.assertRaises(psin_inspect.PsinError):
            psin_inspect.inspect_bytes(raw, max_sections=1)


if __name__ == "__main__":
    unittest.main()
