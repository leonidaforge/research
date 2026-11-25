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
    CLASS_OBSERVED,
    CLASS_STORED,
    CLASS_UNDECODED,
    CLASS_ZLIB,
    ETPF_TYPE,
    HEADER_RESERVED,
    Limits,
    Rds5Error,
    decode_block,
    decode_class,
    decode_record,
    expected_level_sizes,
    main,
    parse,
    payload_size,
    padding_count,
    read_block_bytes,
    reconstruct,
    stream_length,
    virtual_offset,
)

ALIGN = 0x100


def align(value, alignment=ALIGN):
    return (value + alignment - 1) & ~(alignment - 1)


def align4k(value):
    return align(value, 0x1000)


def build_store(blocks, descriptors=None, field_m=16, reserved=HEADER_RESERVED,
                keys=None, end_virtual=None, record0_extra=0,
                size_word_override=None, header_word_override=None,
                gap_before_first=0):
    """Assemble a structurally valid RDS5 store.

    ``blocks`` is a list of dicts with ``payload``, ``class_id`` and optional
    ``virtual``, ``pad_extra``. ``descriptors`` is a list of dicts accepted by
    ``descriptor_words``. The builder derives the virtual counter and page term
    from each block's virtual position.
    """
    descriptors = descriptors or []
    n = len(descriptors)
    count = len(blocks) + 2
    etpf = align(0x10 + 8 * count)
    flag_extra = ALIGN * (record0_extra >> 28)
    first_phys = etpf + align4k(0x10 + 0x20 * n + field_m) + flag_extra + gap_before_first

    stored = []
    offsets = []
    virtuals = []
    cursor = first_phys
    cumulative = 0
    for block in blocks:
        cls = block["class_id"]
        payload = bytes(block["payload"])
        data = zlib.compress(payload, 6) if cls == CLASS_ZLIB else payload
        pad = align(len(data)) - len(data) + block.get("pad_extra", 0)
        span = len(data) + pad
        assert span % ALIGN == 0
        virtual = block.get("virtual")
        if virtual is None:
            virtual = 0x1000 + (cumulative // 0x1000) * 0x1000
        offsets.append(cursor)
        stored.append((data, pad, span))
        virtuals.append(virtual)
        cursor += span
        cumulative += len(payload)
    file_size = cursor
    if end_virtual is None:
        end_virtual = 0x1000 + (cumulative // 0x1000) * 0x1000

    records = [None] * count
    records[0] = (etpf // ALIGN, record0_extra)
    for i, (block, (data, pad, span), offset, virtual) in enumerate(
        zip(blocks, stored, offsets, virtuals)
    ):
        counter = virtual >> 14
        page = (virtual >> 12) & 3
        assert counter < (1 << 20)
        hi = (pad << 20) | counter
        lo = (block["class_id"] << 24) | (page << 30) | (offset // ALIGN)
        records[i + 1] = (lo, hi)
    end_page = (end_virtual >> 12) & 3
    end_counter = end_virtual >> 14
    assert end_counter < (1 << 20)
    records[-1] = (
        (CLASS_ZLIB << 24) | (end_page << 30) | (file_size // ALIGN),
        end_counter,
    )

    size_word = end_virtual & 0xFFFFFFFF
    header_word = reserved | ((end_virtual >> 32) & 1)
    if size_word_override is not None:
        size_word = size_word_override
    if header_word_override is not None:
        header_word = header_word_override

    table = bytearray()
    for d in descriptors:
        w0, w1, w2, w3 = descriptor_words(d)
        table += struct.pack("<IIII", w0, w1, w2, w3)
    if keys is None:
        keys = [0x1000 * (i + 1) for i in range(n)]
    key_bytes = b"".join(struct.pack("<Q", key) for key in keys)
    tail = bytes(8 * n + field_m)
    region = key_bytes + tail
    assert len(region) == 16 * n + field_m

    buf = bytearray(file_size)
    buf[0:4] = b"RDS5"
    struct.pack_into("<III", buf, 4, count, size_word, header_word)
    for i, (lo, hi) in enumerate(records):
        struct.pack_into("<II", buf, 0x10 + 8 * i, lo, hi)
    buf[etpf:etpf + 4] = b"ETPF"
    struct.pack_into("<III", buf, etpf + 4, ETPF_TYPE, n, field_m)
    buf[etpf + 0x10:etpf + 0x10 + len(table)] = table
    start = etpf + 0x10 + len(table)
    buf[start:start + len(region)] = region
    for (data, pad, span), offset in zip(stored, offsets):
        buf[offset:offset + len(data)] = data
    return bytes(buf)


def descriptor_words(d):
    w0 = ((d.get("mip", 0) & 0xF) << 28) | (((d["height"] - 1) & 0x3FFF) << 14) | (
        (d["width"] - 1) & 0x3FFF
    )
    w1 = (
        ((d.get("tile", 0) & 0xF) << 24)
        | ((d.get("kind", 2) & 0xF) << 20)
        | ((d.get("array_minus_one", 0) & 0x3FF) << 10)
        | ((d.get("format_id", 98) & 0x7F) << 3)
        | (d.get("flags", 0) & 0x7)
    )
    locator = d.get("page", 1)
    return w0, w1, locator & 0xFFFFFFFF, locator >> 32


def level_block(size, cls=CLASS_ZLIB, **kwargs):
    block = {"payload": bytes(size), "class_id": cls}
    block.update(kwargs)
    return block


class TempFiles(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

    def write(self, data, name="sample.ttpf"):
        path = os.path.join(self._tmp.name, name)
        with open(path, "wb") as f:
            f.write(data)
        return path


class ClassDispatchTests(TempFiles):
    def test_every_observed_class_is_reported(self):
        blocks = [level_block(0x1000, cls) for cls in CLASS_OBSERVED]
        info = parse(self.write(build_store(blocks)))
        self.assertEqual(
            {f"0x{k:02x}": v for k, v in info.class_counts().items()},
            {f"0x{k:02x}": 1 for k in CLASS_OBSERVED},
        )

    def test_only_zlib_and_stored_decode(self):
        blocks = [level_block(0x1000, cls) for cls in CLASS_OBSERVED]
        path = self.write(build_store(blocks))
        info = parse(path)
        for i, cls in enumerate(CLASS_OBSERVED):
            if cls in (CLASS_ZLIB, CLASS_STORED):
                decoded = decode_block(path, info, i)
                self.assertEqual(len(decoded.data), 0x1000)
                self.assertEqual(decoded.storage_class, cls)
            else:
                with self.assertRaises(Rds5Error) as ctx:
                    decode_block(path, info, i)
                self.assertIn("does not decode", str(ctx.exception))
                self.assertIn(f"0x{cls:02x}", str(ctx.exception))

    def test_class_id_reads_both_descriptions(self):
        for cls in CLASS_OBSERVED:
            lo = cls << 24
            six_bit = (lo >> 24) & 0x3F
            four_bit = (lo >> 26) & 0xF
            self.assertEqual(six_bit, four_bit << 2)
            self.assertEqual(decode_class(lo), cls)
            self.assertEqual(lo & 0x03000000, 0)

    def test_bit_24_set_is_out_of_model(self):
        with self.assertRaises(Rds5Error) as ctx:
            decode_class(0x01000000)
        self.assertIn("bits 24..25", str(ctx.exception))
        with self.assertRaises(Rds5Error):
            decode_class(0x02000000)

    def test_store_with_bit_24_set_is_rejected(self):
        data = bytearray(build_store([level_block(0x1000, CLASS_ZLIB)]))
        lo = struct.unpack_from("<I", data, 0x18)[0]
        struct.pack_into("<I", data, 0x18, lo | 0x01000000)
        with self.assertRaises(Rds5Error) as ctx:
            parse(self.write(bytes(data)))
        self.assertIn("bits 24..25", str(ctx.exception))


class ArithmeticTests(unittest.TestCase):
    def test_virtual_offsets(self):
        self.assertEqual(virtual_offset(0, 1), 0x1000)
        self.assertEqual(virtual_offset(0, 2), 0x2000)
        self.assertEqual(virtual_offset(1, 0), 0x4000)
        self.assertEqual(virtual_offset(4, 1), 0x11000)

    def test_padding_and_stream_length(self):
        hi = (0x123 << 20) | 0xABCDE
        self.assertEqual(padding_count(hi), 0x123)
        self.assertEqual(stream_length(0x500, hi), 0x3DD)
        with self.assertRaises(Rds5Error):
            stream_length(0x100, 0x200 << 20)

    def test_payload_size_high_bit(self):
        self.assertEqual(payload_size(0x2000, 0), 0x2000)
        self.assertEqual(payload_size(0x2000, 1), 0x100002000)

    def test_expected_level_sizes(self):
        self.assertEqual(expected_level_sizes(128, 128, 1, 2), [16384, 4096])
        self.assertEqual(expected_level_sizes(128, 64, 0.5, 2), [4096, 1024])
        self.assertEqual(expected_level_sizes(4, 4, 1, 3), [16, 4, 1])


class VirtualStoreTests(TempFiles):
    def test_sub_page_term(self):
        blocks = [level_block(0x1000, virtual=0x2000)]
        path = self.write(build_store(blocks, end_virtual=0x3000))
        info = parse(path)
        self.assertEqual(info.records[1].page_term, 2)
        self.assertEqual(info.records[1].virtual_offset, 0x2000)
        self.assertTrue(info.extent_matches_payload_size)

    def test_size_word_with_bit_32(self):
        blocks = [level_block(0x1000, virtual=0x1000)]
        end = 0x100002000
        info = parse(self.write(build_store(blocks, end_virtual=end)))
        self.assertEqual(info.size_word, 0x2000)
        self.assertEqual(info.size_high_bit, 1)
        self.assertEqual(info.payload_size, end)
        self.assertTrue(info.extent_matches_payload_size)
        self.assertEqual(info.header_word, HEADER_RESERVED | 1)

    def test_extent_mismatch_is_reported(self):
        blocks = [level_block(0x1000, virtual=0x1000)]
        data = build_store(blocks, end_virtual=0x2000, size_word_override=0x3000)
        info = parse(self.write(data))
        self.assertFalse(info.extent_matches_payload_size)


class PaddingTests(TempFiles):
    def test_nonzero_padding_count_and_zero_bytes(self):
        payload = bytes(range(256)) * 16
        block = {"payload": payload, "class_id": CLASS_ZLIB, "pad_extra": 0x200}
        path = self.write(build_store([block]))
        info = parse(path)
        record = info.records[1]
        self.assertGreaterEqual(record.padding, 0x200)
        decoded = decode_block(path, info, 0)
        self.assertEqual(decoded.data, payload)
        self.assertEqual(decoded.consumed, decoded.stored_span - record.padding)

    def test_nonzero_padding_byte_is_rejected(self):
        payload = bytes(range(256)) * 16
        block = {"payload": payload, "class_id": CLASS_ZLIB, "pad_extra": 0x200}
        data = bytearray(build_store([block]))
        info = parse(self.write(bytes(data)))
        start, end = info.records[1].offset, info.records[2].offset
        data[end - 1] = 0x55
        path = self.write(bytes(data))
        with self.assertRaises(Rds5Error) as ctx:
            decode_block(path, info, 0)
        self.assertIn("padding is not zero", str(ctx.exception))

    def test_padding_field_mismatch_is_rejected(self):
        payload = bytes(range(256)) * 16
        block = {"payload": payload, "class_id": CLASS_ZLIB, "pad_extra": 0x200}
        data = bytearray(build_store([block]))
        offset = 0x18
        lo, hi = struct.unpack_from("<II", data, offset)
        struct.pack_into("<I", data, offset + 4, hi & 0xFFFFF)
        path = self.write(bytes(data))
        info = parse(path)
        with self.assertRaises(Rds5Error) as ctx:
            decode_block(path, info, 0)
        self.assertIn("consumed", str(ctx.exception))


class DescriptorTests(TempFiles):
    def test_descriptor_fields(self):
        descriptors = [
            {"width": 1024, "height": 512, "mip": 0, "flags": 1, "format_id": 98,
             "array_minus_one": 0, "kind": 2, "tile": 0, "page": 1},
            {"width": 256, "height": 256, "mip": 1, "flags": 0, "format_id": 77,
             "array_minus_one": 5, "kind": 4, "tile": 1, "page": 2},
        ]
        blocks = [level_block(0x1000, virtual=0x1000), level_block(0x1000, virtual=0x2000)]
        info = parse(self.write(build_store(blocks, descriptors, keys=[3, 4])))
        self.assertEqual(info.entry_count, 2)
        first, second = info.descriptors
        self.assertEqual((first.width, first.height, first.mip), (1024, 512, 0))
        self.assertEqual((first.flags, first.format_id, first.array_size, first.kind, first.tile_mode),
                         (1, 98, 1, 2, 0))
        self.assertEqual(first.first_page, 1)
        self.assertEqual((second.width, second.height, second.mip), (256, 256, 1))
        self.assertEqual((second.flags, second.format_id, second.array_size, second.kind, second.tile_mode),
                         (0, 77, 6, 4, 1))
        self.assertTrue(info.keys_strictly_increasing)

    def test_unsorted_keys_are_reported(self):
        descriptors = [{"width": 8, "height": 8}, {"width": 8, "height": 8}]
        blocks = [level_block(0x1000, virtual=0x1000), level_block(0x1000, virtual=0x2000)]
        info = parse(self.write(build_store(blocks, descriptors, keys=[9, 4])))
        self.assertFalse(info.keys_strictly_increasing)


class ReconstructionTests(TempFiles):
    def test_small_mip_chain(self):
        blocks = [
            level_block(0x4000, virtual=0x1000),
            level_block(0x1000, virtual=0x5000),
        ]
        descriptors = [{"width": 128, "height": 128, "mip": 1, "format_id": 98,
                        "kind": 2, "tile": 0, "page": 1}]
        path = self.write(build_store(blocks, descriptors, end_virtual=0x6000))
        info = parse(path)
        report = reconstruct(path, info, 0, bytes_per_texel=1, levels=2)
        self.assertEqual(report["block_count"], 2)
        self.assertEqual(report["decoded_bytes"], 0x5000)
        self.assertEqual(report["level_sizes"], [0x4000, 0x1000])
        self.assertTrue(report["size_matches"])
        self.assertTrue(report["level_boundaries_on_block_boundaries"])

    def test_mip_count_mismatch_is_reported(self):
        blocks = [
            level_block(0x4000, virtual=0x1000),
            level_block(0x1000, virtual=0x5000),
        ]
        descriptors = [{"width": 128, "height": 128, "mip": 1}]
        path = self.write(build_store(blocks, descriptors, end_virtual=0x6000))
        info = parse(path)
        report = reconstruct(path, info, 0, bytes_per_texel=1, levels=3)
        self.assertFalse(report["size_matches"])

    def test_undecoded_class_stops_reconstruction(self):
        blocks = [
            level_block(0x1000, CLASS_ZLIB, virtual=0x1000),
            level_block(0x1000, 0x04, virtual=0x2000),
        ]
        descriptors = [{"width": 64, "height": 64, "mip": 1}]
        path = self.write(build_store(blocks, descriptors, end_virtual=0x3000))
        info = parse(path)
        with self.assertRaises(Rds5Error) as ctx:
            reconstruct(path, info, 0, bytes_per_texel=1, levels=2)
        self.assertIn("does not decode", str(ctx.exception))


class RejectionTests(TempFiles):
    def valid(self):
        return bytearray(build_store([level_block(0x1000, CLASS_ZLIB)]))

    def corrupt(self, mutate):
        data = self.valid()
        mutate(data)
        return self.write(bytes(data))

    def test_bad_magic(self):
        patched = self.corrupt(lambda b: b.__setitem__(slice(0, 4), b"XDS5"))
        assert_raises(self, parse, patched, "magic")

    def test_truncated_header(self):
        assert_raises(self, parse, self.write(b"RDS5\x03\x00"), "header")

    def test_unsupported_header_word(self):
        patched = self.corrupt(lambda b: struct.pack_into("<I", b, 0x0C, 0x17000000))
        assert_raises(self, parse, patched, "header word")

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
        broken = build_store([level_block(0x1000, CLASS_ZLIB)], field_m=15)
        assert_raises(self, parse, self.write(broken), "multiple of 16")

    def test_entry_count_over_limit(self):
        descriptors = [{"width": 8, "height": 8, "page": 1}]
        path = self.write(build_store([level_block(0x1000, CLASS_ZLIB)], descriptors))
        assert_raises(self, lambda p: parse(p, Limits(max_etpf_entries=0)), path, "entry count")

    def test_offsets_must_increase(self):
        data = self.valid()
        struct.pack_into("<I", data, 0x18, 0)
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
        path = self.write(build_store([level_block(0x1000, CLASS_ZLIB)]))
        assert_raises(self, lambda p: parse(p, Limits(max_file_size=64)), path, "limit")


class InflationTests(TempFiles):
    def test_cap_rejects_large_output(self):
        path = self.write(build_store([level_block(0x1000)]))
        info = parse(path)
        with self.assertRaises(Rds5Error):
            decode_block(path, info, 0, max_uncompressed=1024)

    def test_truncated_stream_is_rejected(self):
        payload = bytes(0x1000)
        block = {"payload": payload, "class_id": CLASS_ZLIB}
        data = bytearray(build_store([block]))
        info = parse(self.write(bytes(data)))
        start, end = info.records[1].offset, info.records[2].offset
        data[start + 4] = 0xFF
        path = self.write(bytes(data))
        info = parse(path)
        with self.assertRaises(Rds5Error):
            decode_block(path, info, 0)

    def test_block_index_bounds(self):
        path = self.write(build_store([level_block(0x1000)]))
        info = parse(path)
        with self.assertRaises(Rds5Error):
            read_block_bytes(path, info, 1)


class StreamingTests(TempFiles):
    def test_large_gap_is_scanned_without_materialising_it(self):
        gap = 8 << 20
        blocks = [level_block(0x1000, CLASS_ZLIB)]
        path = self.write(build_store(blocks, gap_before_first=gap))
        tracemalloc.start()
        info = parse(path)
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        self.assertGreaterEqual(info.padding_bytes, gap)
        self.assertLess(peak, gap // 2)

    def test_nonzero_byte_deep_in_gap_is_rejected(self):
        gap = 4 << 20
        data = bytearray(build_store([level_block(0x1000, CLASS_ZLIB)], gap_before_first=gap))
        info = parse(self.write(bytes(data)))
        data[info.first_block - 1] = 0x55
        assert_raises(self, parse, self.write(bytes(data)), "padding")


class CliTests(TempFiles):
    def sample(self):
        descriptors = [{"width": 64, "height": 64, "mip": 0, "format_id": 98, "page": 1}]
        blocks = [level_block(0x1000, CLASS_ZLIB, virtual=0x1000)]
        return self.write(build_store(blocks, descriptors))

    def test_inspect_json_with_records_and_block(self):
        path = self.sample()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main(["inspect", path, "--json", "--records", "--descriptors",
                         "--block", "0", "--decode"])
        self.assertEqual(code, 0)
        data = json.loads(out.getvalue())
        self.assertEqual(data["record_count"], 3)
        self.assertEqual(data["descriptor_count"], 1)
        self.assertEqual(data["class_counts"], {"0x20": 1})
        self.assertEqual(data["records"][0]["offset"], data["etpf_offset"])
        self.assertEqual(data["block"]["storage_class"], "0x20")
        self.assertEqual(data["block"]["decoded_bytes"], 0x1000)
        self.assertEqual(data["descriptors"][0]["width"], 64)

    def test_inspect_headers(self):
        path = self.sample()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main(["inspect", path, "--json", "--headers"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out.getvalue())["headers"], {"zlib": 1, "other": 0})

    def test_scan_reports_failures(self):
        self.write(build_store([level_block(0x1000)]), "ok.ttpf")
        self.write(b"RDS5\x03\x00\x00\x00", "short.ttpf")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main(["scan", self._tmp.name])
        self.assertEqual(code, 1)
        self.assertIn("failures=1", out.getvalue())

    def test_scan_class_totals(self):
        self.write(build_store([level_block(0x1000, CLASS_ZLIB)]), "a.ttpf")
        self.write(build_store([level_block(0x1000, CLASS_STORED)]), "b.ttpf")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main(["scan", self._tmp.name, "--headers"])
        self.assertEqual(code, 0)
        text = out.getvalue()
        self.assertIn("classes[0x00=1 0x20=1]", text)
        self.assertIn("zlib_headers=1 other_headers=1", text)

    def test_descriptors_command(self):
        path = self.sample()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main(["descriptors", path, "--json"])
        self.assertEqual(code, 0)
        report = json.loads(out.getvalue())
        self.assertEqual(report["descriptor_count"], 1)
        self.assertEqual(report["counts"]["width"], {"64": 1})

    def test_decode_command_writes_output(self):
        path = self.sample()
        out_path = os.path.join(self._tmp.name, "decoded.bin")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main(["decode", path, "--block", "0", "--out", out_path])
        self.assertEqual(code, 0)
        self.assertEqual(os.path.getsize(out_path), 0x1000)
        self.assertIn("class=0x20", out.getvalue())

    def test_decode_undecoded_class_fails(self):
        path = self.write(build_store([level_block(0x1000, 0x04)]))
        out = io.StringIO()
        err = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(["decode", path, "--block", "0"])
        self.assertEqual(code, 1)
        self.assertIn("does not decode", err.getvalue())

    def test_reconstruct_command(self):
        blocks = [
            level_block(0x4000, virtual=0x1000),
            level_block(0x1000, virtual=0x5000),
        ]
        descriptors = [{"width": 128, "height": 128, "mip": 1, "page": 1}]
        path = self.write(build_store(blocks, descriptors, end_virtual=0x6000))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main(["reconstruct", path, "--descriptor", "0", "--bytes-per-texel", "1",
                         "--levels", "2", "--json"])
        self.assertEqual(code, 0)
        report = json.loads(out.getvalue())
        self.assertTrue(report["size_matches"])
        self.assertEqual(report["decoded_bytes"], 0x5000)


def assert_raises(test, func, arg, needle):
    try:
        func(arg)
    except Rds5Error as exc:
        test.assertIn(needle, str(exc))
    else:
        test.fail("Rds5Error was not raised")


if __name__ == "__main__":
    unittest.main()
