#!/usr/bin/env python3
"""Read-only parser for the RDS5 container format that carries an ETPF chunk.

Every read is bounded, every count is checked against a caller-supplied limit,
and structural violations raise Rds5Error instead of being repaired. The parser
opens inputs read-only and never writes next to them.

Only structural facts are printed: offsets, sizes, counts, flag bytes. Block
payload bytes are never printed.
"""

from __future__ import annotations

import argparse
import json
import os
import struct
import sys
import zlib
from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Sequence, Tuple

MAGIC = b"RDS5"
ETPF_MAGIC = b"ETPF"
ETPF_TYPE = 0x27A
SUPPORTED_VERSIONS = (0x16000000, 0x16000001)

HEADER_SIZE = 0x10
RECORD_AREA = 0x10
RECORD_SIZE = 8
OFFSET_ALIGN = 0x100
OFFSET_MASK = 0xFFFFFF
ETPF_ALIGN = 0x1000
IO_CHUNK = 1 << 20

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
    """One 8-byte record. ``offset`` is absolute and 0x100-aligned."""

    index: int
    flags: int
    offset: int
    extra: int


@dataclass(frozen=True)
class EtpfEntry:
    index: int
    w0: int
    w1: int
    w2: int
    w3: int

    @property
    def page(self) -> int:
        """Low 16 bits of ``w2``: a 16-bit, wrapping page counter."""
        return self.w2 & 0xFFFF


@dataclass
class Rds5File:
    path: str
    size: int
    record_count: int
    uncompressed_total: int
    version: int
    records: List[Record] = field(default_factory=list)
    etpf_offset: int = 0
    etpf_type: int = 0
    entry_count: int = 0
    field_m: int = 0
    entries: List[EtpfEntry] = field(default_factory=list)
    data_end: int = 0
    align_end: int = 0
    flag_extra: int = 0
    layout_matches_observed: bool = False
    first_block: int = 0
    padding_bytes: int = 0

    @property
    def blocks(self) -> List[Record]:
        return self.records[1:-1]

    @property
    def block_count(self) -> int:
        return max(0, self.record_count - 2)


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


def decode_record(index: int, lo: int, hi: int) -> Record:
    return Record(
        index=index,
        flags=(lo >> 24) & 0xFF,
        offset=(lo & OFFSET_MASK) * OFFSET_ALIGN,
        extra=hi,
    )


def block_codec(first: Optional[int]) -> str:
    """Classify a block by its first byte. Only zlib is established."""
    if first is None:
        return "unknown"
    if first == 0x78:
        return "zlib"
    return "unknown"


def parse(path: str, limits: Limits = Limits()) -> Rds5File:
    size = os.path.getsize(path)
    _expect(size >= HEADER_SIZE, f"file is {size} bytes, shorter than the 0x10-byte header")
    _expect(size <= limits.max_file_size, f"file size {size} exceeds limit {limits.max_file_size}")

    with open(path, "rb") as f:
        head = _read(f, 0, 0x10, size)
        _expect(head[:4] == MAGIC, f"bad magic {head[:4]!r}, expected {MAGIC!r}")

        record_count, uncompressed_total, version = struct.unpack_from("<III", head, 4)
        _expect(
            version in SUPPORTED_VERSIONS,
            f"unsupported RDS5 version 0x{version:08x}; supported: "
            + ", ".join(f"0x{v:08x}" for v in SUPPORTED_VERSIONS),
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

        table_end = etpf_offset + 0x10 + 16 * entry_count
        data_end = table_end + 16 * entry_count + field_m
        _expect(table_end <= size, "ETPF entry table exceeds file size")
        _expect(data_end <= size, "ETPF chunk exceeds file size")

        table = _read(f, etpf_offset + 0x10, 16 * entry_count, size)
        entries = [
            EtpfEntry(i, *struct.unpack_from("<IIII", table, 16 * i))
            for i in range(entry_count)
        ]

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

        # Observed layout relation. The meaning of the flag field is unproven, so a
        # mismatch is reported rather than rejected.
        align_end = etpf_offset + _align_up(0x10 + 0x20 * entry_count + field_m, ETPF_ALIGN)
        flag_extra = OFFSET_ALIGN * (records[0].extra >> 28)

    return Rds5File(
        path=path,
        size=size,
        record_count=record_count,
        uncompressed_total=uncompressed_total,
        version=version,
        records=records,
        etpf_offset=etpf_offset,
        etpf_type=etpf_type,
        entry_count=entry_count,
        field_m=field_m,
        entries=entries,
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


def inflate_block(
    path: str,
    info: Rds5File,
    index: int,
    max_uncompressed: int = DEFAULT_MAX_UNCOMPRESSED,
    max_block_bytes: int = DEFAULT_MAX_BLOCK_BYTES,
) -> bytes:
    """Inflate one zlib block straight from the file.

    The stored span and the output are both capped. A cap hit is an error, not a
    truncation.
    """
    start, end = block_span(info, index)
    span = end - start
    _expect(
        span <= max_block_bytes,
        f"block {index} span 0x{span:x} exceeds limit {max_block_bytes}",
    )
    out = bytearray()
    with open(path, "rb") as f:
        head = _read(f, start, 1, info.size)
        _expect(head == b"\x78", f"block {index} has no zlib header")
        f.seek(start)
        dec = zlib.decompressobj()
        remaining = span
        try:
            while remaining:
                chunk = f.read(min(IO_CHUNK, remaining))
                _expect(
                    len(chunk) > 0,
                    f"block {index} is truncated at 0x{start + span - remaining:x}",
                )
                remaining -= len(chunk)
                out += dec.decompress(chunk, max_uncompressed + 1 - len(out))
                if len(out) > max_uncompressed:
                    raise Rds5Error(
                        f"block {index} exceeds the {max_uncompressed}-byte decompression cap"
                    )
                if dec.eof:
                    break
        except zlib.error as exc:
            raise Rds5Error(f"block {index} is not a valid zlib stream: {exc}") from exc
    _expect(dec.eof, f"block {index} zlib stream is truncated")
    return bytes(out)


def summarize(info: Rds5File, path: str, with_codecs: bool = False) -> dict:
    codecs = None
    if with_codecs:
        codecs = {"zlib": 0, "unknown": 0}
        with open(path, "rb") as f:
            for i in range(info.block_count):
                start = info.records[1 + i].offset
                first = _read(f, start, 1, info.size)[0]
                codecs[block_codec(first)] += 1
    offsets = [r.offset for r in info.records]
    report = {
        "path": info.path,
        "size": info.size,
        "version": f"0x{info.version:08x}",
        "record_count": info.record_count,
        "block_count": info.block_count,
        "uncompressed_total": info.uncompressed_total,
        "etpf_offset": info.etpf_offset,
        "etpf_type": f"0x{info.etpf_type:x}",
        "entry_count": info.entry_count,
        "field_m": info.field_m,
        "etpf_data_end": info.data_end,
        "etpf_align_end": info.align_end,
        "flag_extra": info.flag_extra,
        "layout_matches_observed": info.layout_matches_observed,
        "padding_bytes": info.padding_bytes,
        "first_block": info.first_block,
        "offsets_in_bounds": all(0 < o <= info.size for o in offsets),
    }
    if codecs is not None:
        report["codecs"] = codecs
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
    report = summarize(info, args.path, with_codecs=True)
    if args.records:
        report["records"] = [
            {
                "index": rec.index,
                "offset": rec.offset,
                "high_byte": rec.flags,
                "second_word": rec.extra,
            }
            for rec in info.records
        ]
    if args.block is not None:
        start, end = block_span(info, args.block)
        with open(args.path, "rb") as f:
            first = _read(f, start, 1, info.size)[0]
        report["block"] = {
            "index": args.block,
            "block_span": end - start,
            "codec": block_codec(first),
        }
        if args.inflate:
            report["block"]["uncompressed_bytes"] = len(
                inflate_block(
                    args.path,
                    info,
                    args.block,
                    max_uncompressed=args.max_uncompressed,
                    max_block_bytes=limits.max_block_bytes,
                )
            )
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
            if args.json:
                rows.append({"path": path, "error": str(exc)})
            else:
                print(f"FAIL {path}: {exc}")
            continue
        rows.append(summarize(info, path, with_codecs=args.codecs))
    if args.json:
        print(json.dumps(rows, indent=2, sort_keys=True))
    else:
        for row in rows:
            if "error" in row:
                continue
            codec_note = ""
            if "codecs" in row:
                codec_note = f"\tzlib={row['codecs']['zlib']}\tother={row['codecs']['unknown']}"
            layout = "ok" if row["layout_matches_observed"] else "MISMATCH"
            print(
                f"{row['path']}\tsize={row['size']}\trecords={row['record_count']}\t"
                f"entries={row['entry_count']}\tm=0x{row['field_m']:x}\tlayout={layout}"
                f"{codec_note}"
            )
        ok_rows = [r for r in rows if "error" not in r]
        total_blocks = sum(r.get("block_count", 0) for r in ok_rows)
        total_entries = sum(r.get("entry_count", 0) for r in ok_rows)
        layout_mismatches = sum(1 for r in ok_rows if not r["layout_matches_observed"])
        summary = (f"summary: files={len(rows) - failures} failures={failures} "
                   f"blocks={total_blocks} entries={total_entries} "
                   f"layout_mismatches={layout_mismatches}")
        if args.codecs:
            zlib = sum(r["codecs"]["zlib"] for r in ok_rows)
            other = sum(r["codecs"]["unknown"] for r in ok_rows)
            summary += f" zlib={zlib} other={other}"
        print(summary)
    return 0 if failures == 0 else 1


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
    insp.add_argument("--block", type=int, help="report one block record")
    insp.add_argument(
        "--inflate", action="store_true", help="inflate the reported block (zlib only)"
    )
    insp.add_argument("--max-uncompressed", type=int, default=DEFAULT_MAX_UNCOMPRESSED)
    common(insp)
    insp.set_defaults(func=cmd_inspect)

    scan = sub.add_parser("scan", help="parse every *.ttpf under a directory")
    scan.add_argument("root")
    scan.add_argument("--json", action="store_true")
    scan.add_argument("--codecs", action="store_true", help="read the first byte of every block")
    common(scan)
    scan.set_defaults(func=cmd_scan)
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
