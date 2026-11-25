import json
import struct
import unittest

from inspect_type14 import describe


def synthetic_payload() -> bytes:
    strings = [b"alpha", b"beta"]
    string_table = b"".join(value + b"\x00" for value in strings)
    count = len(strings)
    stride = 0x28
    string_offset = 0x40
    size = 0xA0
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
        struct.pack_into("<I", data, offset, index + 1)
        struct.pack_into("<H", data, offset + 4, len(value))
        data[offset + 6 : offset + 6 + len(value)] = value
    return bytes(data)


class DescribeTest(unittest.TestCase):
    def test_reports_tables_without_payload_text(self):
        result = describe(synthetic_payload())
        self.assertEqual(result["size"], 0xA0)
        self.assertEqual(result["string_table"]["offset"], 0x40)
        self.assertEqual(result["string_table"]["lengths"], [5, 4])
        self.assertEqual(result["string_table"]["string_count"], 2)
        self.assertTrue(all(result["checks"].values()))
        self.assertEqual(len(result["record_table_candidates"]), 1)
        candidate = result["record_table_candidates"][0]
        self.assertEqual(candidate["stride"], 0x28)
        self.assertEqual(candidate["start"], 0x50)
        self.assertEqual([record["name_length"] for record in candidate["records"]], [5, 4])
        encoded = json.dumps(result)
        self.assertNotIn("alpha", encoded)
        self.assertNotIn("beta", encoded)

    def test_rejects_short_payload(self):
        with self.assertRaises(ValueError):
            describe(b"\x00" * 8)


if __name__ == "__main__":
    unittest.main()
