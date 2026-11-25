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

    def test_lsch_body_marker_run_and_tail(self):
        report = psin_inspect.inspect_bytes(synthetic.lsch_document([4, 8, 12]))
        body = report["family_data"]["section_bodies"]["LSCH"]
        self.assertEqual(body["length"] % 16, 0)
        self.assertTrue(body["marker_at_0x10"])
        self.assertEqual(body["marker_count"], 1)
        self.assertEqual(body["tail_length"], 16)
        self.assertTrue(body["tail_multiple_16"])
        self.assertFalse(body["tail_has_marker"])

    def test_lsch_empty_lenm_is_reported(self):
        report = psin_inspect.inspect_bytes(synthetic.lsch_document([4]))
        lenm = report["family_data"]["section_bodies"]["LENM"]
        self.assertTrue(lenm["empty"])
        self.assertEqual(lenm["length"], 0)

    def test_lenm_chain_length_is_predicted(self):
        lenm = (
            b"\x01" * 8 + b"\xEE" * 8 + synthetic.le32(3)
            + b"\0" * 12
            + b"\x02" * 8 + synthetic.le32(1) + synthetic.le32(0)
            + b"\x03" * 8 + synthetic.le32(2) + synthetic.le32(0)
            + b"\x04" * 8
        )
        raw = synthetic.lsch_document([4], sections=[
            (b"LSCH", b"\x11" * 8 + synthetic.le32(3) + synthetic.le32(0)
             + synthetic.AA + synthetic.le32(4) + struct.pack("<HH", 0, 1) + b"\0" * 16),
            (b"LENM", lenm),
            (b"LSNS", synthetic.be32(0)),
            (b"LGID", b""),
            (b"LRSC", b"\0" * 80),
        ])
        report = psin_inspect.inspect_bytes(raw)
        body = report["family_data"]["section_bodies"]["LENM"]
        self.assertEqual(body["header_size"], 0x20)
        self.assertEqual(body["count"], 3)
        self.assertEqual(body["chain_length"], 16 * 3 - 8)
        self.assertEqual(body["predicted_body_length"], 0x20 + 16 * 3 - 8)
        self.assertEqual(body["extra_length"], 0)
        self.assertTrue(body["body_minus_header_multiple_8"])
        self.assertTrue(body["marker_ee_at_0x08"])
        self.assertTrue(body["header_tail_zero"])
        # The rejected reading used length - 0x14; it is not a multiple of 8 here.
        self.assertEqual(len(lenm) - 0x14, 52)
        self.assertNotEqual((len(lenm) - 0x14) % 8, 0)

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
        self.assertEqual(report["family_data"]["model"], "block table")
        self.assertIsNone(report["family_data"]["descriptor_table"])
        self.assertTrue(report["family_data"]["header_marker_70"])
        self.assertEqual(report["family_data"]["block_count"], 2)
        self.assertTrue(report["family_data"]["checks"]["formula_matches_first_offset"])
        self.assertTrue(report["family_data"]["psch"]["tiling_ok"])
        self.assertEqual(
            report["tag_sequence"], ["PMAP", "PSCH", "PSIG", "STNS", "CHKS"]
        )
        self.assertTrue(report["checks"]["checksum_ok"])

    def test_pmap_block_table_consumes_the_pre_section(self):
        raw = synthetic.pmap_document([17, 16, 24])
        report = psin_inspect.inspect_bytes(raw)
        data = report["family_data"]
        self.assertEqual(data["block_count"], 3)
        self.assertTrue(data["checks"]["body_length_matches_count"])
        self.assertTrue(data["checks"]["header_padding_70"])
        self.assertTrue(data["checks"]["first_block_at_0x10"])
        self.assertTrue(data["checks"]["offsets_aligned_16"])
        self.assertTrue(data["checks"]["padding_between_blocks_70"])
        self.assertTrue(data["checks"]["formula_matches_first_offset"])
        self.assertTrue(data["checks"]["block_offsets_follow_lengths"])
        self.assertTrue(data["checks"]["all_large_ids_in_psch"])
        self.assertTrue(data["checks"]["no_small_ids_in_psch"])
        self.assertEqual(data["name_table"]["name_count"], 2)
        self.assertTrue(data["name_table"]["all_names_printable"])

    def test_pmap_block_offsets_must_follow_lengths(self):
        raw = bytearray(synthetic.pmap_document([17, 16, 24]))
        section = raw.find(b"PMAP")
        body = section + 8
        second_offset = body + 16 + 4
        struct.pack_into(">I", raw, second_offset, struct.unpack_from(">I", raw, second_offset)[0] + 16)
        report = psin_inspect.inspect_bytes(bytes(raw))
        self.assertFalse(report["family_data"]["checks"]["block_offsets_follow_lengths"])
        self.assertFalse(report["family_data"]["checks"]["padding_between_blocks_70"])

    def test_pmap_psch_id_containment_is_checked(self):
        raw = bytearray(synthetic.pmap_document([17, 16]))
        section = raw.find(b"PSCH")
        body = section + 8
        # Replace the single PSCH id with one no block uses.
        struct.pack_into(">I", raw, body + 4, 0xDEADBEEF)
        report = psin_inspect.inspect_bytes(bytes(raw))
        self.assertFalse(report["family_data"]["checks"]["all_large_ids_in_psch"])

    def test_pmap_psch_table_tiles_the_body(self):
        report = psin_inspect.inspect_bytes(synthetic.pmap_document())
        psch = report["family_data"]["psch"]
        self.assertEqual(psch["count"], 1)
        self.assertTrue(psch["tiling_ok"])
        self.assertEqual(len(psch["value_lengths"]), 1)

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

    def test_unknown_first_tag_is_reported_as_other(self):
        prefix = b"PSIN" + struct.pack(">I", 16) + b"\0" * 8
        raw = synthetic.with_checksum(prefix, [(b"ZZZZ", b"\0" * 16)])
        report = psin_inspect.inspect_bytes(raw)
        self.assertEqual(report["family"], "OTHER")
        self.assertEqual(report["first_tag"], "ZZZZ")
        self.assertIsNone(report["family_data"])
        self.assertTrue(report["checks"]["checksum_ok"])

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
