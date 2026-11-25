"""Synthetic fixtures and contract tests for the RDS5 parser. No game files needed."""

import contextlib
import io
import json
import os
import struct
import sys
import tempfile
import tracemalloc
import unittest
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rds5 import (  # noqa: E402
    ETPF_TYPE,
    Limits,
    Rds5Error,
    block_codec,
    decode_record,
    inflate_block,
    main,
    parse,
    read_block_bytes,
)

ALIGN = 0x100


def align(value):
    return (value + ALIGN - 1) & ~(ALIGN - 1)


def align4k(value):
    return (value + 0xFFF) & ~0xFFF


def build_file(blocks, entries, field_m=16, version=0x16000000, record0_extra=0,
               gap_before_first=0):
    """Assemble a structurally valid RDS5 file.

    ``blocks`` is a list of (stored_bytes, flags, extra). ``entries`` is a list
    of four-word tuples. ``gap_before_first`` inserts extra zero bytes before the
    first block, which also breaks the observed chunk-to-block relation.
    """
    if gap_before_first % ALIGN:
        raise ValueError("gap must be a multiple of 0x100")
    count = len(blocks) + 2
    record_area_end = 0x10 + 8 * count
    etpf = align(record_area_end)
    table = b"".join(struct.pack("<IIII", *e) for e in entries)
    blob = bytes([0xAA]) * (16 * len(entries) + field_m)
    content_end = etpf + 0x10 + len(table) + len(blob)

    payload = bytearray()
    offsets = []
    flag_extra = ALIGN * (record0_extra >> 28)
    cursor = etpf + align4k(0x10 + 0x20 * len(entries) + field_m) + flag_extra + gap_before_first
    payload.extend(b"\x00" * cursor)
    for data, _flags, _extra in blocks:
        offsets.append(cursor)
        payload.extend(data)
        cursor = align(len(payload))
        payload.extend(b"\x00" * (cursor - len(payload)))
    size = len(payload)

    buf = bytearray(size)
    buf[0:4] = b"RDS5"
    struct.pack_into("<III", buf, 4, count, 0x1000 + sum(len(b[0]) for b in blocks), version)
    struct.pack_into("<II", buf, 0x10, etpf // ALIGN, record0_extra)
    for i, ((data, flags, extra), off) in enumerate(zip(blocks, offsets), start=1):
        struct.pack_into("<II", buf, 0x10 + 8 * i, (flags << 24) | (off // ALIGN), extra)
    struct.pack_into("<II", buf, 0x10 + 8 * (count - 1), 0x20 << 24 | (size // ALIGN), 0)

    buf[etpf:etpf + 4] = b"ETPF"
    struct.pack_into("<III", buf, etpf + 4, ETPF_TYPE, len(entries), field_m)
    buf[etpf + 0x10:etpf + 0x10 + len(table)] = table
    buf[etpf + 0x10 + len(table):content_end] = blob
    for data, off in zip((b[0] for b in blocks), offsets):
        buf[off:off + len(data)] = data
    return bytes(buf)


def zblock(payload):
    return zlib.compress(payload, 6)


class TempFiles(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

    def write(self, data, name="sample.ttpf"):
        path = os.path.join(self._tmp.name, name)
        with open(path, "wb") as f:
            f.write(data)
        return path


class ParseTests(TempFiles):
    def test_minimal_roundtrip(self):
        block = zblock(b"row" * 100)
        path = self.write(build_file([(block, 0x20, 0)], [(1, 2, 3, 4)]))
        info = parse(path)
        self.assertEqual(info.record_count, 3)
        self.assertEqual(info.block_count, 1)
        self.assertEqual(info.etpf_offset, align(0x10 + 8 * 3))
        self.assertEqual(info.entry_count, 1)
        self.assertEqual(info.field_m, 16)
        self.assertEqual(info.records[0].offset, info.etpf_offset)
        self.assertEqual(info.records[-1].offset, info.size)
        self.assertEqual(info.entries[0].w0, 1)
        self.assertEqual(info.entries[0].page, 3)
        self.assertTrue(read_block_bytes(path, info, 0).startswith(block))
        self.assertEqual(inflate_block(path, info, 0), b"row" * 100)

    def test_both_versions_accepted(self):
        for version in (0x16000000, 0x16000001):
            path = self.write(build_file([(zblock(b"x"), 0, 0)], [(0, 0, 0, 0)], version=version))
            self.assertEqual(parse(path).version, version)

    def test_multiple_blocks_are_contiguous_and_aligned(self):
        blocks = [(zblock(b"a" * 10), 0x20, 0), (zblock(b"b" * 10), 0x60, 4)]
        info = parse(self.write(build_file(blocks, [(0, 0, 0, 0), (0, 0, 1, 0)])))
        offsets = [r.offset for r in info.records]
        self.assertEqual(offsets, sorted(offsets))
        self.assertTrue(all(o % ALIGN == 0 for o in offsets))
        self.assertGreater(info.padding_bytes, 0)

    def test_block_codec_classification(self):
        self.assertEqual(block_codec(0x78), "zlib")
        self.assertEqual(block_codec(0x32), "unknown")
        self.assertEqual(block_codec(None), "unknown")

    def test_decode_record_fields(self):
        rec = decode_record(5, (0x60 << 24) | 0x1234, 0xDEADBEEF)
        self.assertEqual(rec.index, 5)
        self.assertEqual(rec.flags, 0x60)
        self.assertEqual(rec.offset, 0x123400)
        self.assertEqual(rec.extra, 0xDEADBEEF)

    def test_layout_relation_is_reported(self):
        info = parse(self.write(build_file([(zblock(b"q" * 8), 0x20, 0)], [(0, 0, 0, 0)])))
        raw = 0x10 + 0x20 * 1 + 16
        self.assertEqual(info.data_end, info.etpf_offset + raw)
        self.assertEqual(info.align_end, info.etpf_offset + align4k(raw))
        self.assertEqual(info.flag_extra, 0)
        self.assertTrue(info.layout_matches_observed)
        self.assertEqual(info.padding_bytes, info.first_block - info.data_end)


class StreamingTests(TempFiles):
    def test_large_gap_is_scanned_without_materialising_it(self):
        gap = 8 << 20
        path = self.write(
            build_file([(zblock(b"q" * 64), 0x20, 0)], [(0, 0, 0, 0)], gap_before_first=gap)
        )
        tracemalloc.start()
        info = parse(path)
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        self.assertGreaterEqual(info.padding_bytes, gap)
        self.assertLess(peak, gap // 2)

    def test_nonzero_byte_deep_in_gap_is_rejected(self):
        gap = 4 << 20
        data = bytearray(
            build_file([(zblock(b"q" * 64), 0x20, 0)], [(0, 0, 0, 0)], gap_before_first=gap)
        )
        info = parse(self.write(bytes(data)))
        data[info.first_block - 1] = 0x55
        assert_raises(self, parse, self.write(bytes(data)), "padding")

    def test_default_block_limit(self):
        self.assertEqual(Limits().max_block_bytes, 256 << 20)

    def test_block_span_limit_applies_before_reading(self):
        stored = bytes(range(256)) * 16  # 4096 bytes, not zlib
        path = self.write(build_file([(stored, 0x04, 0)], [(0, 0, 0, 0)]))
        info = parse(path)
        assert_raises_call(self, lambda: read_block_bytes(path, info, 0, max_block_bytes=1024),
                           "limit")
        assert_raises_call(self, lambda: inflate_block(path, info, 0, max_block_bytes=1024),
                           "limit")

    def test_inflate_reads_from_file(self):
        payload = b"row" * 4096
        path = self.write(build_file([(zblock(payload), 0x20, 0)], [(0, 0, 0, 0)]))
        info = parse(path)
        self.assertEqual(inflate_block(path, info, 0), payload)


class RejectionTests(TempFiles):
    def valid(self):
        return bytearray(build_file([(zblock(b"q" * 32), 0x20, 0)], [(1, 1, 1, 0)]))

    def corrupt(self, mutate):
        data = self.valid()
        mutate(data)
        return self.write(bytes(data))

    def test_bad_magic(self):
        patched = self.corrupt(lambda b: b.__setitem__(slice(0, 4), b"XDS5"))
        assert_raises(self, parse, patched, "magic")

    def test_truncated_header(self):
        assert_raises(self, parse, self.write(b"RDS5\x03\x00"), "header")

    def test_unsupported_version(self):
        patched = self.corrupt(lambda b: struct.pack_into("<I", b, 0x0C, 0x17000000))
        assert_raises(self, parse, patched, "version")

    def test_record_count_too_small(self):
        patched = self.corrupt(lambda b: struct.pack_into("<I", b, 4, 2))
        assert_raises(self, parse, patched, "minimum")

    def test_record_count_over_limit(self):
        path = self.corrupt(lambda b: struct.pack_into("<I", b, 4, 1_000_000))
        assert_raises(self, lambda p: parse(p, Limits(max_records=1000)), path, "limit")

    def test_record0_must_point_at_etpf(self):
        patched = self.corrupt(lambda b: struct.pack_into("<I", b, 0x10, 7))
        assert_raises(self, parse, patched, "record 0")

    def test_bad_etpf_magic(self):
        data = self.valid()
        etpf = struct.unpack_from("<I", data, 0x10)[0] * ALIGN
        data[etpf:etpf + 4] = b"XTPF"
        assert_raises(self, parse, self.write(bytes(data)), "ETPF magic")

    def test_bad_etpf_type(self):
        data = self.valid()
        etpf = struct.unpack_from("<I", data, 0x10)[0] * ALIGN
        struct.pack_into("<I", data, etpf + 4, 0x27B)
        assert_raises(self, parse, self.write(bytes(data)), "ETPF type")

    def test_field_m_must_be_multiple_of_16(self):
        broken = build_file([(zblock(b"q"), 0x20, 0)], [(0, 0, 0, 0)], field_m=15)
        assert_raises(self, parse, self.write(broken), "multiple of 16")

    def test_entry_count_over_limit(self):
        path = self.write(build_file([(zblock(b"q"), 0x20, 0)], [(0, 0, 0, 0)]))
        assert_raises(self, lambda p: parse(p, Limits(max_etpf_entries=0)), path, "entry count")

    def test_offsets_must_increase(self):
        data = self.valid()
        struct.pack_into("<I", data, 0x18, 0)  # first block offset becomes 0
        assert_raises(self, parse, self.write(bytes(data)), "first block")

    def test_last_record_must_equal_file_size(self):
        data = self.valid()
        assert_raises(self, parse, self.write(bytes(data) + b"\x00" * ALIGN), "file size")

    def test_padding_must_be_zero(self):
        data = self.valid()
        etpf = struct.unpack_from("<I", data, 0x10)[0] * ALIGN
        content_end = etpf + 0x10 + 16 + 32
        data[content_end] = 0x7F
        assert_raises(self, parse, self.write(bytes(data)), "padding")

    def test_file_size_limit(self):
        path = self.write(build_file([(zblock(b"q"), 0x20, 0)], [(0, 0, 0, 0)]))
        assert_raises(self, lambda p: parse(p, Limits(max_file_size=64)), path, "limit")


class InflationTests(TempFiles):
    def test_cap_rejects_large_output(self):
        payload = bytes(4096)
        path = self.write(build_file([(zblock(payload), 0x20, 0)], [(0, 0, 0, 0)]))
        info = parse(path)
        with self.assertRaises(Rds5Error):
            inflate_block(path, info, 0, max_uncompressed=1024)

    def test_truncated_stream_is_rejected(self):
        block = zblock(b"z" * 4096)[:-4]
        path = self.write(build_file([(block, 0x20, 0)], [(0, 0, 0, 0)]))
        info = parse(path)
        with self.assertRaises(Rds5Error):
            inflate_block(path, info, 0)

    def test_non_zlib_block_is_rejected(self):
        path = self.write(build_file([(b"\x32\xde\x37\x3a\x00\x00", 0x04, 0)], [(0, 0, 0, 0)]))
        info = parse(path)
        with self.assertRaises(Rds5Error):
            inflate_block(path, info, 0)

    def test_block_index_bounds(self):
        path = self.write(build_file([(zblock(b"q"), 0x20, 0)], [(0, 0, 0, 0)]))
        info = parse(path)
        with self.assertRaises(Rds5Error):
            read_block_bytes(path, info, 1)


class CliTests(TempFiles):
    def test_inspect_json_with_records_and_block(self):
        path = self.write(build_file([(zblock(b"q" * 64), 0x20, 0)], [(1, 2, 3, 4)]))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main(["inspect", path, "--json", "--records", "--block", "0", "--inflate"])
        self.assertEqual(code, 0)
        data = json.loads(out.getvalue())
        self.assertEqual(data["record_count"], 3)
        self.assertEqual(len(data["records"]), 3)
        self.assertEqual(data["records"][0]["offset"], data["etpf_offset"])
        self.assertEqual(data["block"]["codec"], "zlib")
        self.assertEqual(data["block"]["uncompressed_bytes"], 64)

    def test_scan_reports_failures(self):
        self.write(build_file([(zblock(b"q"), 0x20, 0)], [(0, 0, 0, 0)]), "ok.ttpf")
        self.write(b"RDS5\x03\x00\x00\x00", "short.ttpf")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main(["scan", self._tmp.name])
        self.assertEqual(code, 1)
        self.assertIn("failures=1", out.getvalue())

    def test_scan_reports_layout_mismatch(self):
        self.write(
            build_file([(zblock(b"q" * 32), 0x20, 0)], [(0, 0, 0, 0)], gap_before_first=0x200),
            "gap.ttpf",
        )
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main(["scan", self._tmp.name])
        text = out.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("layout=MISMATCH", text)
        self.assertIn("layout_mismatches=1", text)

    def test_scan_codec_totals_and_layout(self):
        self.write(
            build_file([(zblock(b"q" * 32), 0x20, 0)], [(0, 0, 0, 0)], gap_before_first=0x200),
            "gap.ttpf",
        )
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main(["scan", self._tmp.name, "--codecs"])
        text = out.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("layout=MISMATCH", text)
        self.assertIn("layout_mismatches=1", text)
        self.assertIn("zlib=1 other=0", text)


def assert_raises(test, func, arg, needle):
    try:
        func(arg)
    except Rds5Error as exc:
        test.assertIn(needle, str(exc))
    else:
        test.fail("Rds5Error was not raised")


def assert_raises_call(test, func, needle):
    try:
        func()
    except Rds5Error as exc:
        test.assertIn(needle, str(exc))
    else:
        test.fail("Rds5Error was not raised")


if __name__ == "__main__":
    unittest.main()
