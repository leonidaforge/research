import json
import struct
import unittest

import edup_inspect
import synthetic


class EdubInspectTests(unittest.TestCase):
    def test_layout_and_field_counts(self):
        raw = synthetic.edup_document(
            [(0x10, 0x100), (0x20, 0x100), (0x30, 0x200), (0x40, 0x200)],
            b"\xA5" * 32,
        )
        report = edup_inspect.inspect_bytes(raw)
        self.assertEqual(report["count"], 4)
        self.assertEqual(report["blob_length"], 32)
        self.assertTrue(report["layout_ok"])
        self.assertEqual(report["key_multiplicity"]["distinct"], 4)
        self.assertEqual(report["stored_key_multiplicity"]["distinct"], 2)
        self.assertEqual(report["stored_key_multiplicity"]["max_repeat"], 2)
        self.assertTrue(report["key_sets_disjoint"])
        self.assertEqual(report["identity_entries"], 0)

    def test_store_membership_identifies_the_stored_field(self):
        raw = synthetic.edup_document(
            [(0x10, 0x100), (0x20, 0x200)], b"\xA5" * 16
        )
        keys = {0x100: {0x100, 0x999}, 0x200: {0x200}}
        report = edup_inspect.inspect_bytes(raw, store_keys=keys)
        test = report["store_test"]
        self.assertEqual(test["keys_in_store_union"], 0)
        self.assertEqual(test["stored_keys_in_store_union"], 2)
        self.assertIn("resolves", test["direction"])

    def test_store_parser_reads_the_etpf_key_table(self):
        raw = synthetic.store_document([0x300, 0x100, 0x200])
        path = "store.tmp"
        with open(path, "wb") as handle:
            handle.write(raw)
        try:
            keys = edup_inspect.etpf_keys(path)
        finally:
            import os
            os.remove(path)
        self.assertEqual(keys, {0x100, 0x200, 0x300})

    def test_empty_table_is_accepted(self):
        report = edup_inspect.inspect_bytes(synthetic.edup_document([], b"\0" * 16))
        self.assertEqual(report["count"], 0)
        self.assertTrue(report["layout_ok"])
        self.assertEqual(report["stored_key_multiplicity"]["distinct"], 0)

    def test_wrong_magic_is_rejected(self):
        raw = b"PUDE" + b"\0" * 16
        with self.assertRaises(edup_inspect.EdError):
            edup_inspect.inspect_bytes(raw)

    def test_entry_table_overrun_is_rejected(self):
        raw = b"EDUP" + struct.pack("<I", 10) + b"\0" * 8
        with self.assertRaises(edup_inspect.EdError):
            edup_inspect.inspect_bytes(raw)

    def test_trailing_bytes_after_blob_are_rejected(self):
        raw = synthetic.edup_document([(1, 2)], b"\0" * 16) + b"x"
        with self.assertRaises(edup_inspect.EdError):
            edup_inspect.inspect_bytes(raw)

    def test_count_cap_is_enforced(self):
        raw = synthetic.edup_document([(1, 2)], b"\0" * 16)
        with self.assertRaises(edup_inspect.EdError):
            edup_inspect.inspect_bytes(raw, max_entries=0)

    def test_report_is_json_serializable(self):
        report = edup_inspect.inspect_bytes(synthetic.edup_document([(1, 2)], b"\0" * 16))
        self.assertIn("EDUP", json.dumps(report) + "EDUP")

    def test_tool_does_not_emit_key_values(self):
        raw = synthetic.edup_document([(0xDEADBEEF, 0x12345678)], b"\0" * 16)
        report = edup_inspect.inspect_bytes(raw)
        text = json.dumps(report)
        self.assertNotIn("3735928559", text)
        self.assertNotIn("305419896", text)


if __name__ == "__main__":
    unittest.main()
