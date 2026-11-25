import json
import struct
import unittest

from inspect_type14 import Type14Error, describe, joaat, verify_ids


def synthetic_payload(strings=None, identifiers=None, size=0x120, stride=0x28):
    if strings is None:
        strings = [b"alpha", b"beta"]
    string_table = b"".join(value + b"\x00" for value in strings)
    count = len(strings)
    string_offset = 0x40
    record_start = size - count * stride
    data = bytearray(size)
    struct.pack_into("<H", data, 0x00, string_offset)
    struct.pack_into("<H", data, 0x02, 1)
    struct.pack_into("<I", data, 0x04, size)
    struct.pack_into("<H", data, 0x0C, len(string_table))
    struct.pack_into("<H", data, 0x0E, string_offset)
    struct.pack_into("<H", data, 0x18, count)
    data[string_offset : string_offset + len(string_table)] = string_table
    for index, value in enumerate(strings):
        offset = record_start + index * stride
        identifier = index + 1 if identifiers is None else identifiers[index]
        struct.pack_into("<I", data, offset, identifier)
        struct.pack_into("<H", data, offset + 4, len(value))
        data[offset + 6 : offset + 6 + len(value)] = value
    return bytes(data)


class DescribeTest(unittest.TestCase):
    def test_reports_tables_without_payload_text(self):
        result = describe(synthetic_payload())
        self.assertEqual(result["size"], 0x120)
        self.assertEqual(result["string_table"]["offset"], 0x40)
        self.assertEqual(result["string_table"]["lengths"], [5, 4])
        self.assertEqual(result["string_table"]["string_count"], 2)
        self.assertTrue(all(result["checks"].values()))
        self.assertEqual(len(result["record_table_candidates"]), 1)
        candidate = result["record_table_candidates"][0]
        self.assertEqual(candidate["stride"], 0x28)
        self.assertEqual(candidate["start"], 0xD0)
        self.assertEqual([record["name_length"] for record in candidate["records"]], [5, 4])
        encoded = json.dumps(result)
        self.assertNotIn("alpha", encoded)
        self.assertNotIn("beta", encoded)
        self.assertNotIn('"id"', encoded)
        self.assertNotIn("name_key", encoded)
        self.assertNotIn("name_hash", encoded)

    def test_rejects_short_payload(self):
        with self.assertRaises(Type14Error):
            describe(b"\x00" * 8)

    def test_rejects_malformed_payload(self):
        with self.assertRaises(Type14Error):
            describe(b"\x00" * 0x2C)


class VerifyIdsTest(unittest.TestCase):
    def _payload(self):
        strings = [b"Alpha", b"beta", b"gamma"]
        identifiers = [joaat(value.lower()) for value in strings]
        return synthetic_payload(strings=strings, identifiers=identifiers)

    def test_counts_match_the_string_table(self):
        result = verify_ids(self._payload())
        self.assertEqual(result["records"], 3)
        self.assertEqual(result["string_entries"], 3)
        self.assertEqual(result["matches"]["folded_lower_no_terminator"], 3)
        self.assertEqual(result["matches"]["case_sensitive_no_terminator"], 2)
        self.assertEqual(result["matches"]["folded_lower_with_terminator"], 0)
        self.assertEqual(result["matches"]["case_sensitive_with_terminator"], 0)
        self.assertEqual(result["matches"]["folded_lower_no_terminator_big_endian"], 0)
        self.assertEqual(result["matches"]["case_sensitive_no_terminator_big_endian"], 0)
        self.assertEqual(result["record_name_matches"]["folded_lower_no_terminator"], 3)
        self.assertEqual(result["record_name_matches"]["case_sensitive_no_terminator"], 2)

    def test_result_contains_counts_only(self):
        encoded = json.dumps(verify_ids(self._payload()))
        for text in ("Alpha", "alpha", "beta", "gamma"):
            self.assertNotIn(text, encoded)
        self.assertNotIn("0x", encoded)


if __name__ == "__main__":
    unittest.main()
