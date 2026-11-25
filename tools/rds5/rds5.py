#!/usr/bin/env python3
"""Read-only parser and bounded decoder for the RDS5 container format.

The parser checks the header, the record array, the ETPF descriptor table and
the descriptor key table against caller-supplied limits. It opens inputs
read-only and never writes next to them.

Blocks are dispatched by their storage-class id. Class 0x20 is a complete zlib
stream and class 0x00 is stored bytes; every other observed class is reported as
not decoded. Payload bytes are never printed unless the caller asks for them.
"""

from __future__ import annotations

import argparse
import json
import os
import struct
import sys
import zlib
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

MAGIC = b"RDS5"
ETPF_MAGIC = b"ETPF"
ETPF_TYPE = 0x27A

# Bits 1..31 of the word at +0x0C are 0x16000000 in every observed store. Bit 0
# is bit 32 of the virtual payload size.
HEADER_RESERVED = 0x16000000

HEADER_SIZE = 0x10
RECORD_AREA = 0x10
RECORD_SIZE = 8
OFFSET_ALIGN = 0x100
OFFSET_MASK = 0xFFFFFF
OFFSET_MASK_26 = 0x3FFFFFF
ETPF_ALIGN = 0x1000
IO_CHUNK = 1 << 20

CLASS_ZLIB = 0x20
CLASS_STORED = 0x00
CLASS_OBSERVED = (0x00, 0x04, 0x0C, 0x10, 0x14, 0x18, 0x1C, 0x20)
CLASS_UNDECODED = (0x04, 0x0C, 0x10, 0x14, 0x18, 0x1C)
CLASS_MASK = 0x3C
CLASS_RESERVED_BITS = 0x03
PAGE_MASK = 0x03

DEFAULT_MAX_FILE_SIZE = 8 << 30
DEFAULT_MAX_RECORDS = 2_000_000
DEFAULT_MAX_ETPF_ENTRIES = 2_000_000
DEFAULT_MAX_UNCOMPRESSED = 64 << 20
DEFAULT_MAX_BLOCK_BYTES = 256 << 20


class Rds5Error(Exception):
    """The input violates the format contract or a configured limit."""


@dataclass(frozen=True)
class Limits:
    max_file_size: int = DEFAULT_MAX_FILE_SIZE
    max_records: int = DEFAULT_MAX_RECORDS
    max_etpf_entries: int = DEFAULT_MAX_ETPF_ENTRIES
    max_uncompressed: int = DEFAULT_MAX_UNCOMPRESSED
    max_block_bytes: int = DEFAULT_MAX_BLOCK_BYTES


@dataclass(frozen=True)
class Record:
    """One 8-byte record.

    ``offset`` uses the 24-bit field. Bits 24 and 25 are zero in every observed
    record, so the same value is obtained from the 26-bit field of the
    four-bit-class description. ``virtual_offset`` is the block position in
    virtual space and ``padding`` is the trailing zero count of the stored span.
    """

    index: int
    lo: int
    hi: int
    offset: int
    storage_class: int
    page_term: int
    virtual_offset: int
    padding: int


@dataclass(frozen=True)
class Descriptor:
    index: int
    width: int
    height: int
    mip: int
    flags: int
    format_id: int
    array_minus_one: int
    kind: int
    tile_mode: int
    locator: int

    @property
    def array_size(self) -> int:
        return self.array_minus_one + 1

    @property
    def first_page(self) -> int:
        return self.locator & 0x1FFFFF


@dataclass
class Rds5File:
    path: str
    size: int
    record_count: int
    size_word: int
    header_word: int
    records: List[Record] = field(default_factory=list)
    etpf_offset: int = 0
    etpf_type: int = 0
    entry_count: int = 0
    field_m: int = 0
    descriptors: List[Descriptor] = field(default_factory=list)
    keys: List[int] = field(default_factory=list)
    keys_strictly_increasing: Optional[bool] = None
    data_end: int = 0
    align_end: int = 0
    flag_extra: int = 0
    layout_matches_observed: bool = False
    first_block: int = 0
    padding_bytes: int = 0

    @property
    def size_high_bit(self) -> int:
        return self.header_word & 1

    @property
    def payload_size(self) -> int:
        return self.size_word | (self.size_high_bit << 32)

    @property
    def blocks(self) -> List[Record]:
        return self.records[1:-1]

    @property
    def block_count(self) -> int:
        return max(0, self.record_count - 2)

    @property
    def extent_matches_payload_size(self) -> bool:
        return self.records[-1].virtual_offset == self.payload_size

    def class_counts(self) -> Dict[int, int]:
        counts: Dict[int, int] = {}
        for record in self.blocks:
            counts[record.storage_class] = counts.get(record.storage_class, 0) + 1
        return counts


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise Rds5Error(message)


def _read(f, offset: int, length: int, size: int) -> bytes:
    _expect(offset >= 0 and length >= 0, "negative read request")
    _expect(
        offset + length <= size,
        f"read 0x{length:x} at 0x{offset:x} exceeds file size 0x{size:x}",
    )
    f.seek(offset)
    data = f.read(length)
    _expect(len(data) == length, f"short read at 0x{offset:x}")
    return data


def _align_up(value: int, alignment: int) -> int:
    return (value + alignment - 1) & ~(alignment - 1)


def _check_zero(f, offset: int, length: int, size: int, what: str) -> None:
    """Scan a range in bounded chunks; never materialises it."""
    _expect(offset >= 0 and length >= 0, "negative range")
    _expect(
        offset + length <= size,
        f"{what}: range 0x{length:x} at 0x{offset:x} exceeds file size 0x{size:x}",
    )
    f.seek(offset)
    start = offset
    remaining = length
    while remaining:
        chunk = f.read(min(IO_CHUNK, remaining))
        _expect(len(chunk) > 0, f"{what}: short read at 0x{start:x}")
        bad = next((i for i, value in enumerate(chunk) if value), None)
        if bad is not None:
            raise Rds5Error(f"{what}: non-zero byte at 0x{start + bad:x}")
        start += len(chunk)
        remaining -= len(chunk)


def decode_class(lo: int) -> int:
    """Return the storage-class id of a record's first word.

    Bits 24..29 hold the class when read as six bits; bits 26..29 hold the
    four-bit value that is one quarter of that. Bits 24 and 25 are zero in the
    observed population, so a set bit there is out of the documented model.
    """
    high = (lo >> 24) & 0xFF
    _expect(
        (high & CLASS_RESERVED_BITS) == 0,
        f"record word 0x{lo:08x} sets bits 24..25; the observed storage-class "
        "model requires both bits to be zero",
    )
    return high & CLASS_MASK


def virtual_offset(hi: int, page_term: int) -> int:
    """Virtual block position: 20-bit counter of 0x4000 units plus 0x1000 units."""
    return (hi & 0xFFFFF) * 0x4000 + (page_term & PAGE_MASK) * 0x1000


def padding_count(hi: int) -> int:
    return hi >> 20


def stream_length(span: int, hi: int) -> int:
    pad = padding_count(hi)
    _expect(pad <= span, f"padding 0x{pad:x} exceeds the stored span 0x{span:x}")
    return span - pad


def payload_size(size_word: int, high_bit: int) -> int:
    return size_word | ((high_bit & 1) << 32)


def decode_record(index: int, lo: int, hi: int) -> Record:
    storage_class = decode_class(lo)
    page_term = (lo >> 30) & PAGE_MASK
    return Record(
        index=index,
        lo=lo,
        hi=hi,
        offset=(lo & OFFSET_MASK) * OFFSET_ALIGN,
        storage_class=storage_class,
        page_term=page_term,
        virtual_offset=virtual_offset(hi, page_term),
        padding=padding_count(hi),
    )


def decode_descriptor(index: int, w0: int, w1: int, w2: int, w3: int) -> Descriptor:
    return Descriptor(
        index=index,
        width=(w0 & 0x3FFF) + 1,
        height=((w0 >> 14) & 0x3FFF) + 1,
        mip=(w0 >> 28) & 0xF,
        flags=w1 & 0x7,
        format_id=(w1 >> 3) & 0x7F,
        array_minus_one=(w1 >> 10) & 0x3FF,
        kind=(w1 >> 20) & 0xF,
        tile_mode=(w1 >> 24) & 0xF,
        locator=(w3 << 32) | w2,
    )


def parse(path: str, limits: Limits = Limits()) -> Rds5File:
    size = os.path.getsize(path)
    _expect(size >= HEADER_SIZE, f"file is {size} bytes, shorter than the 0x10-byte header")
    _expect(size <= limits.max_file_size, f"file size {size} exceeds limit {limits.max_file_size}")

    with open(path, "rb") as f:
        head = _read(f, 0, 0x10, size)
        _expect(head[:4] == MAGIC, f"bad magic {head[:4]!r}, expected {MAGIC!r}")

        record_count, size_word, header_word = struct.unpack_from("<III", head, 4)
        _expect(
            (header_word & ~1) == HEADER_RESERVED,
            f"unsupported header word 0x{header_word:08x}; bits 1..31 must be "
            f"0x{HEADER_RESERVED:08x}",
        )
        _expect(3 <= record_count, f"record count {record_count} is below the minimum of 3")
        _expect(
            record_count <= limits.max_records,
            f"record count {record_count} exceeds limit {limits.max_records}",
        )

        record_area_end = RECORD_AREA + RECORD_SIZE * record_count
        _expect(record_area_end <= size, "record array exceeds file size")
        raw = _read(f, RECORD_AREA, RECORD_SIZE * record_count, size)

        records = []
        for i in range(record_count):
            lo, hi = struct.unpack_from("<II", raw, RECORD_SIZE * i)
            records.append(decode_record(i, lo, hi))

        etpf_offset = _align_up(record_area_end, OFFSET_ALIGN)
        _expect(etpf_offset + 0x10 <= size, "ETPF chunk offset exceeds file size")
        _expect(
            records[0].offset == etpf_offset,
            f"record 0 offset 0x{records[0].offset:x} does not match"
            f" the ETPF offset 0x{etpf_offset:x}",
        )

        header = _read(f, etpf_offset, 0x10, size)
        _expect(header[:4] == ETPF_MAGIC, f"bad ETPF magic {header[:4]!r} at 0x{etpf_offset:x}")
        etpf_type, entry_count, field_m = struct.unpack_from("<III", header, 4)
        _expect(etpf_type == ETPF_TYPE, f"unsupported ETPF type 0x{etpf_type:x}")
        _expect(
            entry_count <= limits.max_etpf_entries,
            f"ETPF entry count {entry_count} exceeds limit",
        )
        _expect(field_m % 16 == 0, f"ETPF field M 0x{field_m:x} is not a multiple of 16")

        table_start = etpf_offset + 0x10
        table_end = table_start + 16 * entry_count
        keys_start = table_end
        keys_end = keys_start + 8 * entry_count
        data_end = keys_end + 8 * entry_count + field_m
        _expect(table_end <= size, "ETPF descriptor table exceeds file size")
        _expect(data_end <= size, "ETPF chunk exceeds file size")

        table = _read(f, table_start, 16 * entry_count, size)
        descriptors = [
            decode_descriptor(i, *struct.unpack_from("<IIII", table, 16 * i))
            for i in range(entry_count)
        ]

        keys: List[int] = []
        keys_strictly_increasing: Optional[bool] = None
        if entry_count:
            key_bytes = _read(f, keys_start, 8 * entry_count, size)
            keys = list(struct.unpack("<%dQ" % entry_count, key_bytes))
            if entry_count >= 2:
                keys_strictly_increasing = all(
                    keys[i] < keys[i + 1] for i in range(entry_count - 1)
                )

        for rec in records[1:-1]:
            _expect(rec.offset % OFFSET_ALIGN == 0, f"record {rec.index} offset is not aligned")
            _expect(
                rec.offset < size,
                f"record {rec.index} offset 0x{rec.offset:x} is outside the file",
            )
        for a, b in zip(records[1:], records[2:]):
            _expect(a.offset < b.offset, f"record offsets not increasing at 0x{a.offset:x}")
        _expect(
            records[-1].offset == size,
            f"last record offset 0x{records[-1].offset:x} does not equal file size 0x{size:x}",
        )

        first_block = records[1].offset
        _expect(
            data_end <= first_block,
            f"ETPF content ends at 0x{data_end:x}, after the first block 0x{first_block:x}",
        )
        _check_zero(
            f,
            data_end,
            first_block - data_end,
            size,
            "padding between the ETPF chunk and the first block",
        )

        align_end = etpf_offset + _align_up(0x10 + 0x20 * entry_count + field_m, ETPF_ALIGN)
        flag_extra = OFFSET_ALIGN * (records[0].hi >> 28)

    return Rds5File(
        path=path,
        size=size,
        record_count=record_count,
        size_word=size_word,
        header_word=header_word,
        records=records,
        etpf_offset=etpf_offset,
        etpf_type=etpf_type,
        entry_count=entry_count,
        field_m=field_m,
        descriptors=descriptors,
        keys=keys,
        keys_strictly_increasing=keys_strictly_increasing,
        data_end=data_end,
        align_end=align_end,
        flag_extra=flag_extra,
        layout_matches_observed=first_block == align_end + flag_extra,
        first_block=first_block,
        padding_bytes=first_block - data_end,
    )


def block_span(info: Rds5File, index: int) -> Tuple[int, int]:
    """Return ``(start, end)`` of block ``index`` (0-based among block records)."""
    _expect(0 <= index < info.block_count, f"block index {index} outside 0..{info.block_count - 1}")
    start = info.records[1 + index].offset
    end = info.records[2 + index].offset
    return start, end


def read_block_bytes(
    path: str,
    info: Rds5File,
    index: int,
    max_block_bytes: int = DEFAULT_MAX_BLOCK_BYTES,
) -> bytes:
    """Return the stored bytes of block ``index``. The span is checked first."""
    start, end = block_span(info, index)
    _expect(
        end - start <= max_block_bytes,
        f"block {index} span 0x{end - start:x} exceeds limit {max_block_bytes}",
    )
    with open(path, "rb") as f:
        return _read(f, start, end - start, info.size)


@dataclass
class BlockDecode:
    index: int
    storage_class: int
    stored_span: int
    padding: int
    stream_length: int
    consumed: int
    data: bytes
    virtual_length: int


def decode_block(
    path: str,
    info: Rds5File,
    index: int,
    max_uncompressed: int = DEFAULT_MAX_UNCOMPRESSED,
    max_block_bytes: int = DEFAULT_MAX_BLOCK_BYTES,
) -> BlockDecode:
    """Decode one block by storage-class id.

    Class 0x20 must be one complete zlib stream whose consumed length equals
    ``span - padding``. Class 0x00 returns ``span - padding`` stored bytes. Any
    other observed class raises a class-specific error; it is never guessed.
    """
    record = info.records[1 + index]
    start, end = block_span(info, index)
    span = end - start
    pad = record.padding
    _expect(span <= max_block_bytes, f"block {index} span 0x{span:x} exceeds limit {max_block_bytes}")
    _expect(pad <= span, f"block {index} padding 0x{pad:x} exceeds span 0x{span:x}")
    length = span - pad
    next_record = info.records[2 + index]
    virtual_length = next_record.virtual_offset - record.virtual_offset

    if record.storage_class == CLASS_ZLIB:
        out = bytearray()
        consumed = 0
        with open(path, "rb") as f:
            f.seek(start)
            dec = zlib.decompressobj()
            remaining = span
            try:
                while remaining:
                    chunk = f.read(min(IO_CHUNK, remaining))
                    _expect(len(chunk) > 0, f"block {index} is truncated")
                    remaining -= len(chunk)
                    out += dec.decompress(chunk, max_uncompressed + 1 - len(out))
                    if len(out) > max_uncompressed:
                        raise Rds5Error(
                            f"block {index} exceeds the {max_uncompressed}-byte decompression cap"
                        )
                    if dec.eof:
                        consumed = span - remaining - len(dec.unused_data)
                        break
            except zlib.error as exc:
                raise Rds5Error(f"block {index} is not a valid zlib stream: {exc}") from exc
        _expect(dec.eof, f"block {index} zlib stream is truncated")
        _expect(
            consumed == length,
            f"block {index} consumed 0x{consumed:x} bytes but span-padding is 0x{length:x}",
        )
        _check_tail(path, info, start + length, pad, index)
        return BlockDecode(index, record.storage_class, span, pad, length, consumed, bytes(out), virtual_length)

    if record.storage_class == CLASS_STORED:
        data = read_block_bytes(path, info, index, max_block_bytes)
        _check_tail(path, info, start + length, pad, index)
        return BlockDecode(index, record.storage_class, span, pad, length, length, data[:length], virtual_length)

    raise Rds5Error(
        f"block {index} has storage class 0x{record.storage_class:02x}, which this "
        "decoder does not decode; the class payload remains unidentified"
    )


def _check_tail(path: str, info: Rds5File, offset: int, length: int, index: int) -> None:
    if not length:
        return
    with open(path, "rb") as f:
        tail = _read(f, offset, length, info.size)
    bad = next((i for i, value in enumerate(tail) if value), None)
    _expect(bad is None, f"block {index} padding is not zero at 0x{offset + (bad or 0):x}")


def descriptor_page_range(info: Rds5File, index: int) -> Tuple[int, int]:
    """Virtual byte range referenced by descriptor ``index``."""
    _expect(0 <= index < len(info.descriptors), f"descriptor index {index} out of range")
    start = info.descriptors[index].first_page * 0x1000
    if index + 1 < len(info.descriptors):
        end = info.descriptors[index + 1].first_page * 0x1000
    else:
        end = info.payload_size
    return start, end


def blocks_in_range(info: Rds5File, start: int, end: int) -> List[int]:
    out = []
    for i, record in enumerate(info.blocks):
        if start <= record.virtual_offset < end:
            out.append(i)
    return out


def expected_level_sizes(width: int, height: int, bytes_per_texel: float, levels: int) -> List[int]:
    _expect(width >= 1 and height >= 1, "texture dimensions must be positive")
    _expect(levels >= 1, "mip level count must be at least 1")
    sizes = []
    w, h = width, height
    for _ in range(levels):
        sizes.append(int(max(1, w) * max(1, h) * bytes_per_texel))
        w = max(1, w // 2)
        h = max(1, h // 2)
    return sizes


def reconstruct(
    path: str,
    info: Rds5File,
    descriptor_index: int,
    bytes_per_texel: Optional[float] = None,
    levels: Optional[int] = None,
    max_uncompressed: int = DEFAULT_MAX_UNCOMPRESSED,
    max_block_bytes: int = DEFAULT_MAX_BLOCK_BYTES,
) -> dict:
    """Decode every block referenced by a descriptor into one virtual stream.

    The function reports the block boundaries, the decoded total and, when a
    bytes-per-texel value and level count are supplied, the expected mip level
    sizes. It does not infer a block codec or a pixel format from a format id.
    """
    descriptor = info.descriptors[descriptor_index]
    start, end = descriptor_page_range(info, descriptor_index)
    indices = blocks_in_range(info, start, end)
    _expect(indices, f"descriptor {descriptor_index} references no block")

    buffer = bytearray()
    boundaries = []
    for index in indices:
        decoded = decode_block(
            path,
            info,
            index,
            max_uncompressed=max_uncompressed,
            max_block_bytes=max_block_bytes,
        )
        boundaries.append((index, len(buffer), len(buffer) + len(decoded.data)))
        buffer += decoded.data

    report = {
        "descriptor": descriptor_index,
        "width": descriptor.width,
        "height": descriptor.height,
        "mip": descriptor.mip,
        "format_id": descriptor.format_id,
        "kind": descriptor.kind,
        "tile_mode": descriptor.tile_mode,
        "range_start": start,
        "range_end": end,
        "range_bytes": end - start,
        "block_count": len(indices),
        "blocks": indices,
        "decoded_bytes": len(buffer),
        "block_boundaries": boundaries,
    }

    if bytes_per_texel is not None or levels is not None:
        _expect(
            bytes_per_texel is not None and levels is not None,
            "--bytes-per-texel and --levels must be supplied together",
        )
        sizes = expected_level_sizes(descriptor.width, descriptor.height, bytes_per_texel, levels)
        expected = sum(sizes)
        report["bytes_per_texel"] = bytes_per_texel
        report["levels"] = levels
        report["level_sizes"] = sizes
        report["expected_bytes"] = expected
        report["size_matches"] = expected == len(buffer)
        offset = 0
        aligned = []
        for size in sizes:
            aligned.append(offset in {b[1] for b in boundaries} | {b[2] for b in boundaries})
            offset += size
        report["level_boundaries_on_block_boundaries"] = all(aligned)
    return report


def summarize(info: Rds5File, path: str, with_headers: bool = False) -> dict:
    headers = None
    if with_headers:
        headers = {"zlib": 0, "other": 0}
        with open(path, "rb") as f:
            for i in range(info.block_count):
                start = info.blocks[i].offset
                first = _read(f, start, 1, info.size)[0]
                headers["zlib" if first == 0x78 else "other"] += 1
    report = {
        "path": info.path,
        "size": info.size,
        "size_word": info.size_word,
        "header_word": f"0x{info.header_word:08x}",
        "size_high_bit": info.size_high_bit,
        "payload_size": info.payload_size,
        "record_count": info.record_count,
        "block_count": info.block_count,
        "descriptor_count": info.entry_count,
        "etpf_offset": info.etpf_offset,
        "etpf_type": f"0x{info.etpf_type:x}",
        "field_m": info.field_m,
        "etpf_data_end": info.data_end,
        "etpf_align_end": info.align_end,
        "flag_extra": info.flag_extra,
        "layout_matches_observed": info.layout_matches_observed,
        "padding_bytes": info.padding_bytes,
        "first_block": info.first_block,
        "extent_matches_payload_size": info.extent_matches_payload_size,
        "keys_strictly_increasing": info.keys_strictly_increasing,
        "class_counts": {f"0x{k:02x}": v for k, v in sorted(info.class_counts().items())},
    }
    if headers is not None:
        report["headers"] = headers
    return report


def _iter_inputs(root: str) -> Iterable[str]:
    for dirpath, _dirs, files in os.walk(root):
        for name in files:
            if name.lower().endswith(".ttpf"):
                yield os.path.join(dirpath, name)


def _limits_from(args: argparse.Namespace) -> Limits:
    return Limits(
        max_file_size=args.max_file_size,
        max_records=args.max_records,
        max_etpf_entries=args.max_etpf_entries,
        max_block_bytes=args.max_block_bytes,
    )


def cmd_inspect(args: argparse.Namespace) -> int:
    limits = _limits_from(args)
    info = parse(args.path, limits)
    report = summarize(info, args.path, with_headers=args.headers)
    if args.records:
        report["records"] = [
            {
                "index": rec.index,
                "offset": rec.offset,
                "storage_class": f"0x{rec.storage_class:02x}",
                "page_term": rec.page_term,
                "virtual_offset": rec.virtual_offset,
                "padding": rec.padding,
                "second_word": rec.hi,
            }
            for rec in info.records
        ]
    if args.descriptors:
        report["descriptors"] = [
            {
                "index": d.index,
                "width": d.width,
                "height": d.height,
                "mip": d.mip,
                "flags": d.flags,
                "format_id": d.format_id,
                "array_size": d.array_size,
                "kind": d.kind,
                "tile_mode": d.tile_mode,
                "first_page": d.first_page,
            }
            for d in info.descriptors
        ]
    if args.block is not None:
        start, end = block_span(info, args.block)
        record = info.records[1 + args.block]
        report["block"] = {
            "index": args.block,
            "storage_class": f"0x{record.storage_class:02x}",
            "block_span": end - start,
            "padding": record.padding,
            "stream_length": end - start - record.padding,
        }
        if args.decode:
            decoded = decode_block(
                args.path,
                info,
                args.block,
                max_uncompressed=args.max_uncompressed,
                max_block_bytes=limits.max_block_bytes,
            )
            report["block"]["decoded_bytes"] = len(decoded.data)
            report["block"]["consumed"] = decoded.consumed
            report["block"]["virtual_length"] = decoded.virtual_length
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        for key, value in report.items():
            print(f"{key}: {value}")
    return 0


def cmd_scan(args: argparse.Namespace) -> int:
    limits = _limits_from(args)
    rows = []
    failures = 0
    for path in _iter_inputs(args.root):
        try:
            info = parse(path, limits)
        except (Rds5Error, OSError) as exc:
            failures += 1
            rows.append({"path": path, "error": str(exc)})
            continue
        rows.append(summarize(info, path, with_headers=args.headers))
    if args.json:
        print(json.dumps(rows, indent=2, sort_keys=True))
        return 0 if failures == 0 else 1

    totals = {"blocks": 0, "descriptors": 0, "classes": {}, "headers": {"zlib": 0, "other": 0}}
    for row in rows:
        if "error" in row:
            print(f"FAIL {row['path']}: {row['error']}")
            continue
        totals["blocks"] += row["block_count"]
        totals["descriptors"] += row["descriptor_count"]
        for key, value in row["class_counts"].items():
            totals["classes"][key] = totals["classes"].get(key, 0) + value
        if "headers" in row:
            totals["headers"]["zlib"] += row["headers"]["zlib"]
            totals["headers"]["other"] += row["headers"]["other"]
        layout = "ok" if row["layout_matches_observed"] else "MISMATCH"
        print(
            f"{row['path']}\tsize={row['size']}\trecords={row['record_count']}\t"
            f"descriptors={row['descriptor_count']}\tlayout={layout}"
        )
    ok_rows = [r for r in rows if "error" not in r]
    layout_mismatches = sum(1 for r in ok_rows if not r["layout_matches_observed"])
    classes = " ".join(f"{k}={v}" for k, v in sorted(totals["classes"].items()))
    summary = (
        f"summary: files={len(ok_rows)} failures={failures} blocks={totals['blocks']} "
        f"descriptors={totals['descriptors']} layout_mismatches={layout_mismatches} "
        f"classes[{classes}]"
    )
    if args.headers:
        summary += f" zlib_headers={totals['headers']['zlib']} other_headers={totals['headers']['other']}"
    print(summary)
    return 0 if failures == 0 else 1


def cmd_descriptors(args: argparse.Namespace) -> int:
    info = parse(args.path, _limits_from(args))
    counts: Dict[str, Dict[str, int]] = {
        "width": {},
        "height": {},
        "mip": {},
        "format_id": {},
        "array_size": {},
        "kind": {},
        "tile_mode": {},
        "flags": {},
    }
    for d in info.descriptors:
        for name, value in (
            ("width", d.width),
            ("height", d.height),
            ("mip", d.mip),
            ("format_id", d.format_id),
            ("array_size", d.array_size),
            ("kind", d.kind),
            ("tile_mode", d.tile_mode),
            ("flags", d.flags),
        ):
            key = str(value)
            counts[name][key] = counts[name].get(key, 0) + 1
    report = {
        "path": info.path,
        "descriptor_count": info.entry_count,
        "keys_strictly_increasing": info.keys_strictly_increasing,
        "counts": counts,
        "range_violations": [
            d.index for d in info.descriptors if d.width < 1 or d.height < 1
        ],
    }
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"descriptors: {report['descriptor_count']}")
        print(f"keys_strictly_increasing: {report['keys_strictly_increasing']}")
        for name, table in counts.items():
            print(f"{name}: " + ", ".join(f"{k}={v}" for k, v in sorted(table.items(), key=lambda kv: int(kv[0]))))
    return 0


def cmd_decode(args: argparse.Namespace) -> int:
    info = parse(args.path, _limits_from(args))
    decoded = decode_block(
        args.path,
        info,
        args.block,
        max_uncompressed=args.max_uncompressed,
        max_block_bytes=args.max_block_bytes,
    )
    if args.out:
        with open(args.out, "wb") as f:
            f.write(decoded.data)
    print(
        f"block={decoded.index} class=0x{decoded.storage_class:02x} "
        f"span={decoded.stored_span} padding={decoded.padding} "
        f"stream_length={decoded.stream_length} consumed={decoded.consumed} "
        f"decoded={len(decoded.data)} virtual_length={decoded.virtual_length}"
    )
    return 0


def cmd_reconstruct(args: argparse.Namespace) -> int:
    info = parse(args.path, _limits_from(args))
    report = reconstruct(
        args.path,
        info,
        args.descriptor,
        bytes_per_texel=args.bytes_per_texel,
        levels=args.levels,
        max_uncompressed=args.max_uncompressed,
        max_block_bytes=args.max_block_bytes,
    )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        for key, value in report.items():
            print(f"{key}: {value}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Read-only RDS5/ETPF structural parser")
    sub = p.add_subparsers(dest="command", required=True)

    def common(sp: argparse.ArgumentParser) -> None:
        sp.add_argument("--max-file-size", type=int, default=DEFAULT_MAX_FILE_SIZE)
        sp.add_argument("--max-records", type=int, default=DEFAULT_MAX_RECORDS)
        sp.add_argument("--max-etpf-entries", type=int, default=DEFAULT_MAX_ETPF_ENTRIES)
        sp.add_argument("--max-block-bytes", type=int, default=DEFAULT_MAX_BLOCK_BYTES)

    insp = sub.add_parser("inspect", help="parse one file and print its structure")
    insp.add_argument("path")
    insp.add_argument("--json", action="store_true")
    insp.add_argument("--records", action="store_true", help="include every decoded record")
    insp.add_argument("--descriptors", action="store_true", help="include every descriptor")
    insp.add_argument("--headers", action="store_true", help="read the first byte of every block")
    insp.add_argument("--block", type=int, help="report one block record")
    insp.add_argument("--decode", action="store_true", help="decode the reported block by class")
    insp.add_argument("--max-uncompressed", type=int, default=DEFAULT_MAX_UNCOMPRESSED)
    common(insp)
    insp.set_defaults(func=cmd_inspect)

    scan = sub.add_parser("scan", help="parse every *.ttpf under a directory")
    scan.add_argument("root")
    scan.add_argument("--json", action="store_true")
    scan.add_argument("--headers", action="store_true", help="count first-byte zlib headers")
    common(scan)
    scan.set_defaults(func=cmd_scan)

    desc = sub.add_parser("descriptors", help="summarize one file's descriptor table")
    desc.add_argument("path")
    desc.add_argument("--json", action="store_true")
    common(desc)
    desc.set_defaults(func=cmd_descriptors)

    dec = sub.add_parser("decode", help="decode one block by storage class")
    dec.add_argument("path")
    dec.add_argument("--block", type=int, required=True)
    dec.add_argument("--out", help="write decoded bytes to this path")
    dec.add_argument("--max-uncompressed", type=int, default=DEFAULT_MAX_UNCOMPRESSED)
    common(dec)
    dec.set_defaults(func=cmd_decode)

    rec = sub.add_parser("reconstruct", help="decode the blocks referenced by a descriptor")
    rec.add_argument("path")
    rec.add_argument("--descriptor", type=int, required=True)
    rec.add_argument("--bytes-per-texel", type=float)
    rec.add_argument("--levels", type=int)
    rec.add_argument("--json", action="store_true")
    rec.add_argument("--max-uncompressed", type=int, default=DEFAULT_MAX_UNCOMPRESSED)
    common(rec)
    rec.set_defaults(func=cmd_reconstruct)
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (Rds5Error, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
