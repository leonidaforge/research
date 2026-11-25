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


def build_with_records(variant, streams, specs):
    """Build a payload from (type, bytes, relative_offset) records."""
    start = record_start(variant, streams)
    data_offset = start + 8 * len(specs)
    size = data_offset + max(relative + len(body) for _, body, relative in specs)
    data = bytearray(size)
    struct.pack_into("<4sII I", data, 0, MAGIC, (variant << 16) | 1, streams, data_offset)
    per_stream_start = 0x14 if variant == 0xFF61 else 0x10
    if variant == 0xFF61:
        struct.pack_into("<I", data, 0x10, data_offset)
    for index in range(streams):
        struct.pack_into("<H", data, per_stream_start + 2 * index, index * 4)
    region_start = per_stream_start + 2 * streams
    for index in range(2 * streams + 1):
        struct.pack_into("<I", data, region_start + 4 * index, 0)
    for index, (record_type, body, relative) in enumerate(specs):
        offset = data_offset + relative
        value = (record_type << 56) | ((len(body) & 0xFFFFFFF) << 28) | (offset & 0xFFFFFFF)
        struct.pack_into("<Q", data, start + 8 * index, value)
        data[offset:offset + len(body)] = body
    return bytes(data)


def descriptor_76(declared=1000, rate=48000, codec=0x0B):
    body = bytearray(32)
    struct.pack_into("<I", body, 0x00, declared)
    struct.pack_into("<I", body, 0x04, 0xFFFFFFFF)
    struct.pack_into("<H", body, 0x08, rate)
    struct.pack_into("<I", body, 0x0C, declared)
    body[0x1C] = codec
    return bytes(body)


def descriptor_48(page_count, stride, entries):
    body = bytearray(12 + 16 * len(entries))
    struct.pack_into("<III", body, 0, page_count, stride, len(entries))
    for index, (codec, decoded, rate) in enumerate(entries):
        base = 12 + 16 * index
        struct.pack_into("<IIIHH", body, base, 0, decoded, (rate << 16) | 0x7000,
                         codec | 0x0100, 0xFFFF)
    return bytes(body)


def framed_block(packets, padding=b"\x00"):
    body = bytearray()
    for packet in packets:
        body += struct.pack("<H", len(packet)) + packet
    body += padding
    if len(body) < 2048:
        body += b"\x00" * (2048 - len(body))
    return bytes(body[:2048])


class FramingTests(unittest.TestCase):
    def test_0x76_framed_blocks(self):
        block0 = framed_block([b"\xF8\x01\x02", b"\xFC\x03\x04\x05"])
        block1 = framed_block([b"\xD8\x06\x07"])
        data = build_with_records(0xFF21, 1, [
            (0x76, descriptor_76(), 0),
            (0x55, block0 + block1, 32),
        ])
        report = adat_inspect.inspect_framing(data)
        self.assertEqual(report["totals"]["violations"], 0)
        self.assertEqual(report["totals"]["packets"], 3)
        self.assertEqual(report["totals"]["data_blocks"], 2)
        self.assertEqual(report["codec_counts"], {"0x0b": 1})
        stream = report["streams"][0]
        self.assertEqual(stream["lengths"], {3: 2, 4: 1})
        self.assertEqual(stream["toc"], {0xF8: 1, 0xFC: 1, 0xD8: 1})

    def test_length_overrun_is_reported(self):
        block = bytearray(2048)
        struct.pack_into("<H", block, 0, 2047)
        data = build_with_records(0xFF21, 1, [
            (0x76, descriptor_76(), 0),
            (0x55, bytes(block), 32),
        ])
        report = adat_inspect.inspect_framing(data)
        kinds = {item["kind"] for item in report["streams"][0]["violations"]}
        self.assertIn("length_overruns_block", kinds)

    def test_nonzero_padding_is_reported(self):
        block = bytearray(2048)
        struct.pack_into("<H", block, 0, 2)
        block[2:4] = b"\xAA\xBB"
        block[10] = 0x01
        data = build_with_records(0xFF21, 1, [
            (0x76, descriptor_76(), 0),
            (0x55, bytes(block), 32),
        ])
        report = adat_inspect.inspect_framing(data)
        kinds = [item["kind"] for item in report["streams"][0]["violations"]]
        self.assertIn("nonzero_padding", kinds)

    def test_size_not_multiple_is_reported(self):
        data = build_with_records(0xFF21, 1, [
            (0x76, descriptor_76(), 0),
            (0x55, b"\x00" * 2049, 32),
        ])
        report = adat_inspect.inspect_framing(data)
        kinds = {item["kind"] for item in report["exceptions"]}
        self.assertIn("size_not_multiple_of_block", kinds)

    def test_0x02_size_relation(self):
        data = build_with_records(0xFF21, 1, [
            (0x76, descriptor_76(declared=512, codec=0x02), 0),
            (0x55, b"\x00" * 2048, 32),
        ])
        report = adat_inspect.inspect_framing(data)
        stream = report["streams"][0]
        self.assertTrue(stream["raw_size_check"]["four_bytes_per_sample"])

    def test_ff25_page_layout(self):
        block0 = bytearray(2048)
        struct.pack_into("<I", block0, 0, 0xFFFFFFFF)
        data = build_with_records(0xFF25, 2, [
            (0x48, descriptor_48(1, 4 * 2048, [(0x0B, 1000, 48000)]), 0),
            (0x55, bytes(block0) + framed_block([b"\xF8\x01"]) * 2 + b"\x00" * 2048, 60),
        ])
        report = adat_inspect.inspect_framing(data)
        self.assertEqual(report["totals"]["violations"], 0)
        stream = report["streams"][0]
        self.assertEqual(stream["page_count"], 1)
        self.assertEqual(stream["pages"], 1)
        self.assertEqual(stream["metadata_blocks"], 1)
        self.assertEqual(stream["data_blocks"], 2)
        self.assertEqual(stream["zero_blocks"], 1)

    def test_ff25_page_count_mismatch(self):
        block0 = bytearray(2048)
        struct.pack_into("<I", block0, 0, 0xFFFFFFFF)
        data = build_with_records(0xFF25, 2, [
            (0x48, descriptor_48(2, 4 * 2048, [(0x0B, 1000, 48000)]), 0),
            (0x55, bytes(block0) + framed_block([b"\xF8\x01"]) * 2 + b"\x00" * 2048, 60),
        ])
        report = adat_inspect.inspect_framing(data)
        kinds = {item["kind"] for item in report["streams"][0]["violations"]}
        self.assertIn("page_count_mismatch", kinds)

    def test_framing_rejects_record_overrun(self):
        data = build_with_records(0xFF21, 1, [
            (0x76, descriptor_76(), 0),
            (0x55, b"\x00" * 2048, 32),
        ])
        damaged = bytearray(data)
        struct.pack_into("<I", damaged, 0x08, 1)
        # Point the 0x55 record beyond the payload.
        record_position = record_start(0xFF21, 1) + 8
        value = struct.unpack_from("<Q", damaged, record_position)[0]
        value = (value & ~0xFFFFFFF) | (len(damaged) - 8)
        struct.pack_into("<Q", damaged, record_position, value)
        with self.assertRaises(adat_inspect.AdatError):
            adat_inspect.inspect_framing(bytes(damaged))

    def test_short_0x76_is_rejected(self):
        data = build_with_records(0xFF21, 1, [
            (0x76, b"\x00" * 16, 0),
        ])
        with self.assertRaises(adat_inspect.AdatError):
            adat_inspect.inspect_framing(data)

    def test_short_0x48_is_rejected(self):
        data = build_with_records(0xFF25, 2, [
            (0x48, b"\x00" * 8, 0),
        ])
        with self.assertRaises(adat_inspect.AdatError):
            adat_inspect.inspect_framing(data)

    def test_atomic_output(self):
        with tempfile.TemporaryDirectory() as directory:
            target = os.path.join(directory, "report.json")
            adat_inspect._write_atomic(target, "content\n")
            with open(target, encoding="utf-8") as handle:
                self.assertEqual(handle.read(), "content\n")


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
