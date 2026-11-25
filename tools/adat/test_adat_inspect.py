import json
import os
import struct
import tempfile
import unittest

import adat_inspect

MAGIC = b"ADAT"
VARIANTS = (0xFF02, 0xFF21, 0xFF25, 0xFF61)


def record_start(variant, streams):
    return adat_inspect.record_start(variant, streams)


def build_payload(variant=0xFF21, streams=2, chunk_counts=None,
                  records=None, data_len=64, alignment_gap=0,
                  overrun=False, version=1):
    if records is None:
        records = [(0x36, 8, 0), (0x55, 8, 0), (0xA3, 8, 0)]
    if chunk_counts is None:
        if variant == 0xFF02:
            chunk_counts = [0] * streams
            for index in range(len(records)):
                chunk_counts[index % streams] += 1
        else:
            chunk_counts = [4] * streams
    per_stream_start = 0x14 if variant == 0xFF61 else 0x10
    start = record_start(variant, streams)
    data_offset = start + 8 * len(records) + alignment_gap
    payload_size = data_offset + data_len
    data = bytearray(payload_size)
    struct.pack_into("<4sII I", data, 0, MAGIC, (variant << 16) | version, streams, data_offset)
    if variant == 0xFF02:
        for index, chunks in enumerate(chunk_counts):
            struct.pack_into("<I", data, 0x10 + 4 * index, (chunks << 29) | (0x1000 + index))
    else:
        if variant == 0xFF61:
            struct.pack_into("<I", data, 0x10, data_offset)
        for index in range(streams):
            struct.pack_into("<H", data, per_stream_start + 2 * index, index * 4)
        region_start = per_stream_start + 2 * streams
        for index in range(2 * streams + 1):
            struct.pack_into("<I", data, region_start + 4 * index, 0)
    for index, (record_type, size, relative_offset) in enumerate(records):
        offset = data_offset + relative_offset
        if overrun and index == len(records) - 1:
            offset = payload_size - 4
            size = 8
        value = (record_type << 56) | ((size & 0xFFFFFFF) << 28) | (offset & 0xFFFFFFF)
        struct.pack_into("<Q", data, start + 8 * index, value)
    return bytes(data)


class InspectTests(unittest.TestCase):
    def test_parses_each_variant(self):
        for variant in VARIANTS:
            with self.subTest(variant=hex(variant)):
                data = build_payload(variant=variant, streams=2)
                report = adat_inspect.inspect_bytes(data)
                self.assertEqual(report["header"]["variant"], f"0x{variant:04x}")
                self.assertEqual(report["header"]["streams"], 2)
                self.assertEqual(report["layout"]["record_count"], 3)
                self.assertEqual(report["records"]["types"], {
                    "0x36": 1, "0x55": 1, "0xa3": 1})
                self.assertTrue(all(report["checks"].values()))

    def test_ff02_chunk_formula_with_mixed_counts(self):
        data = build_payload(variant=0xFF02, streams=3, chunk_counts=[2, 3, 4],
                             records=[(0x36, 8, 0)] * 9)
        report = adat_inspect.inspect_bytes(data)
        self.assertEqual(report["ff02"]["chunk_sum"], 9)
        self.assertTrue(report["ff02"]["formula_matches"])
        self.assertFalse(report["ff02"]["uniform_chunk_count"])

    def test_ff61_reports_second_offset(self):
        data = build_payload(variant=0xFF61, streams=2)
        report = adat_inspect.inspect_bytes(data)
        self.assertIn("second_offset", report["ff61"])

    def test_rejects_misaligned_record_run(self):
        data = build_payload(variant=0xFF21, streams=2, alignment_gap=4)
        with self.assertRaises(adat_inspect.AdatError):
            adat_inspect.inspect_bytes(data)

    def test_rejects_record_overrun(self):
        data = build_payload(variant=0xFF25, streams=2, overrun=True)
        with self.assertRaises(adat_inspect.AdatError):
            adat_inspect.inspect_bytes(data)

    def test_rejects_zero_size_record(self):
        data = build_payload(records=[(0x36, 0, 0)])
        with self.assertRaises(adat_inspect.AdatError):
            adat_inspect.inspect_bytes(data)

    def test_rejects_empty_record_run(self):
        data = build_payload(variant=0xFF21, streams=2, records=[])
        with self.assertRaises(adat_inspect.AdatError):
            adat_inspect.inspect_bytes(data)

    def test_rejects_unknown_variant(self):
        data = bytearray(build_payload())
        struct.pack_into("<I", data, 4, (0x1234 << 16) | 1)
        with self.assertRaises(adat_inspect.AdatError):
            adat_inspect.inspect_bytes(bytes(data))

    def test_rejects_other_version(self):
        data = build_payload(version=2)
        with self.assertRaises(adat_inspect.AdatError):
            adat_inspect.inspect_bytes(data)

    def test_rejects_wrong_magic(self):
        data = bytearray(build_payload())
        data[0:4] = b"ADAU"
        with self.assertRaises(adat_inspect.AdatError):
            adat_inspect.inspect_bytes(bytes(data))

    def test_output_inside_input_directory_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            source = os.path.join(directory, "sample.bin")
            output = os.path.join(directory, "report.txt")
            self.assertTrue(adat_inspect._output_is_inside_input(output, [source]))
            other = os.path.join(directory, "..", "outside.txt")
            self.assertFalse(adat_inspect._output_is_inside_input(other, [source]))


if __name__ == "__main__":
    unittest.main()
