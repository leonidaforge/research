import os
import struct
import tempfile
import unittest

import sgd5_inspect


def block(entries, descriptor_byte, length=None):
    payload = b"".join(struct.pack("<IHH", value, kind, index) for value, kind, index in entries)
    if length is None:
        length = 24 + len(payload)
    return struct.pack("<I", length) + bytes([descriptor_byte]) * 20 + b"\0\0\0\0" + payload


def sample(tables, data=b"", data_length=100):
    header = b"SGD5" + struct.pack("<III", 0x11111111, 0x22222222, len(tables))
    body = b"".join(
        block(entries, 0x40 + index)
        for index, entries in enumerate(tables)
    )
    data_header = struct.pack("<I", data_length) + b"\x7f" * 20 + b"\0\0\0\0"
    return header + body + data_header + data


class InspectTests(unittest.TestCase):
    def test_reads_two_tables_and_data_prefix(self):
        records = b"".join(
            struct.pack("<IIHH12s", 0xAABBCCDD, 0xAABBCCDD, 0x0405, index, b"\0" * 12)
            for index in range(3)
        )
        raw = sample(
            [
                [(0x10, 0x0405, 0), (0x20, 0x0102, 1)],
                [(0x30, 0x0407, 0)],
            ],
            data=records + b"ABCDEFGH",
        )
        report = sgd5_inspect.inspect_bytes(raw)
        self.assertEqual(report["magic"], "SGD5")
        self.assertEqual(report["table_block_count"], 2)
        self.assertEqual([block["entries"] for block in report["table_blocks"]], [2, 1])
        self.assertTrue(report["checks"]["all_table_indices_sequential"])
        self.assertTrue(report["checks"]["field_10_equals_first_block_length"])
        self.assertEqual(report["data_region"]["fixed_stride_records"], 3)
        self.assertGreaterEqual(report["data_region"]["printable_run_near_break"], 8)

    def test_accepts_empty_table(self):
        raw = sample([[]])
        report = sgd5_inspect.inspect_bytes(raw)
        self.assertEqual(report["table_blocks"][0]["entries"], 0)
        self.assertIsNone(report["table_blocks"][0]["entry_values"]["max"])

    def test_detects_non_sequential_index(self):
        raw = sample([[(0x10, 0x0405, 5), (0x20, 0x0102, 1)]])
        report = sgd5_inspect.inspect_bytes(raw)
        self.assertFalse(report["table_blocks"][0]["indices_sequential"])
        self.assertFalse(report["checks"]["all_table_indices_sequential"])

    def test_rejects_wrong_magic(self):
        raw = sample([[(0x10, 0x0405, 0)]])
        with self.assertRaises(sgd5_inspect.Sgd5Error):
            sgd5_inspect.inspect_bytes(b"NOPE" + raw[4:])

    def test_rejects_truncated_sample(self):
        raw = sample([[(0x10, 0x0405, 0)]])
        with self.assertRaises(sgd5_inspect.Sgd5Error):
            sgd5_inspect.inspect_bytes(raw[:20])

    def test_output_inside_input_directory_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            source = os.path.join(directory, "sample.bin")
            output = os.path.join(directory, "report.txt")
            self.assertTrue(sgd5_inspect._output_is_inside_input(output, [source]))
            other = os.path.join(directory, "..", "outside.txt")
            self.assertFalse(sgd5_inspect._output_is_inside_input(other, [source]))


if __name__ == "__main__":
    unittest.main()
