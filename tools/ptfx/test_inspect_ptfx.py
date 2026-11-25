import json
import unittest

from inspect_ptfx import describe


def synthetic_payload() -> bytes:
    return b"PTFX_ALPHA_ONE 1.0\r\nTEST_VALUE 0.0\r\n\r\n"


class DescribeTest(unittest.TestCase):
    def test_reports_line_structure_without_payload_text(self):
        result = describe(synthetic_payload())
        self.assertEqual(result["size"], 38)
        self.assertEqual(result["byte_counts"]["crlf"], 3)
        self.assertEqual(result["byte_counts"]["nul"], 0)
        self.assertEqual(result["document"]["non_empty_record_count"], 2)
        self.assertEqual(result["document"]["blank_record_count"], 1)
        self.assertTrue(result["document"]["final_blank_line"])
        self.assertEqual(
            [record["key_length"] for record in result["records"] if not record["empty"]],
            [14, 10],
        )
        self.assertEqual(
            [record["value_length"] for record in result["records"] if not record["empty"]],
            [3, 3],
        )
        self.assertEqual(
            [record["key_segment_lengths"] for record in result["records"] if not record["empty"]],
            [[4, 5, 3], [4, 5]],
        )
        self.assertTrue(all(result["checks"].values()))
        encoded = json.dumps(result)
        for token in ("ALPHA", "ONE", "TEST", "VALUE", "1.0"):
            self.assertNotIn(token, encoded)

    def test_rejects_empty_payload(self):
        with self.assertRaises(ValueError):
            describe(b"")

    def test_reports_non_text_bytes(self):
        result = describe(b"PTFX_KEY 1.0\r\n\x00")
        self.assertFalse(result["checks"]["all_bytes_printable_or_crlf"])
        self.assertFalse(result["checks"]["no_nul"])
        self.assertEqual(result["byte_counts"]["non_text"], 1)
        self.assertEqual(result["non_text_offsets"], ["0x000e"])

    def test_rejects_lf_only_line_endings(self):
        result = describe(b"PTFX_KEY 1.0\n")
        self.assertFalse(result["checks"]["crlf_only_line_endings"])

    def test_rejects_extra_delimiters(self):
        result = describe(b"KEY  VALUE\r\n")
        self.assertEqual(result["records"][0]["field_count"], 3)
        self.assertFalse(result["checks"]["every_non_empty_record_has_two_fields"])

    def test_rejects_tab_delimiter(self):
        result = describe(b"KEY\tVALUE\r\n")
        self.assertEqual(result["records"][0]["field_count"], 1)
        self.assertTrue(result["records"][0]["contains_tab"])
        self.assertFalse(result["checks"]["every_non_empty_record_has_two_fields"])

    def test_unterminated_tail_is_reported(self):
        result = describe(b"PTFX_KEY 1.0")
        self.assertFalse(result["records"][0]["terminated_with_crlf"])
        self.assertFalse(result["checks"]["final_blank_line"])


if __name__ == "__main__":
    unittest.main()
