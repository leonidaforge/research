#!/usr/bin/env python3
"""Read a RAGE resource stored in an RPF9 payload, or an already decoded one.

The stored form is 16 zero bytes followed by one zlib stream per RPF9 chunk.
The chunks reconstruct the system segment followed by the graphics segment. A
page is a group of chunks: one chunk per page, except that a page larger than
32 MiB is stored as several streams. The decoded form is the concatenation of
the two segments.

The system segment starts with the resource header: a zero u64 and, at +8, a
system pointer to the page map. Pointers are u64 values whose upper half is
zero, with bits 28..31 selecting the segment (5 system, 6 graphics) and the low
28 bits a byte offset into that segment.

The tool reads only. It bounds every stream and the total inflated size, and
reports what it cannot establish instead of guessing. See formats/resources/
for the documented layout and the limits of this model.
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
import zlib
from dataclasses import dataclass, field

SYSTEM_BASE = 0x5000_0000
GRAPHICS_BASE = 0x6000_0000
OFFSET_MASK = 0x0FFF_FFFF
PAGE_MAP_HEADER_LEN = 16
# Allocation granularity of every page of a multi-page segment except its last.
PAGE_UNIT = 0x1_0000
# Inflated length of every stream of a split page except the last.
SPLIT_LEN = 0x200_0000
STORED_PREFIX_LEN = 16

MAX_STREAM = 256 << 20
MAX_TOTAL = 512 << 20
MAX_PAGES = 2 * 0xFF

STREAM_CHUNK = 1 << 20


class ResourceError(Exception):
    pass


@dataclass(frozen=True)
class Pointer:
    segment: str
    offset: int


def decode_pointer(value: int):
    """Decode a stored virtual pointer, or return None."""
    if value >> 32:
        return None
    kind = value >> 28
    if kind == 5:
        return Pointer("system", value & OFFSET_MASK)
    if kind == 6:
        return Pointer("graphics", value & OFFSET_MASK)
    return None


def u64_at(data: bytes, at: int) -> int:
    if at < 0 or at + 8 > len(data):
        raise ResourceError(f"read of 8 bytes at {at:#x} is outside the buffer")
    return struct.unpack_from("<Q", data, at)[0]


@dataclass(frozen=True)
class Issue:
    code: str
    detail: str


@dataclass(frozen=True)
class PageMap:
    offset: int
    system_pages: int
    graphics_pages: int

    @property
    def byte_len(self) -> int:
        return PAGE_MAP_HEADER_LEN + 8 * (self.system_pages + self.graphics_pages)

    @property
    def pages(self) -> int:
        return self.system_pages + self.graphics_pages


def parse_page_map(system: bytes, offset: int):
    """Return (PageMap, None) or (None, Issue) for stored system data."""
    if offset < PAGE_MAP_HEADER_LEN:
        return None, Issue(
            "map_in_header", f"the page map offset {offset:#x} is below the 16-byte header"
        )
    if offset + PAGE_MAP_HEADER_LEN > len(system):
        return None, Issue(
            "map_outside",
            f"the page map at {offset:#x} is outside {len(system)} bytes of system data",
        )
    header = system[offset : offset + PAGE_MAP_HEADER_LEN]
    system_pages = header[8]
    graphics_pages = header[9]
    map_len = PAGE_MAP_HEADER_LEN + 8 * (system_pages + graphics_pages)
    if offset + map_len > len(system):
        return None, Issue(
            "map_outside",
            f"the page map at {offset:#x} needs {map_len} bytes but only "
            f"{len(system) - offset} are inside the system data",
        )
    body = system[offset : offset + map_len]
    bad = [at for at, byte in enumerate(body) if byte and at not in (8, 9)]
    if bad:
        return None, Issue(
            "map_nonzero",
            "the page map has non-zero bytes at offsets "
            + ", ".join(hex(at) for at in bad[:8]),
        )
    if system_pages == 0:
        return None, Issue("no_system_page", "the page map declares no system page")
    return PageMap(offset, system_pages, graphics_pages), None


def group_pages(lengths, page_count):
    """Assign stream lengths to pages.

    Returns (groups, method) where groups is a list of (inflated_len, streams).
    A stream of exactly SPLIT_LEN continues its page when that reading matches
    the declared page count; otherwise every stream is one page. When neither
    reading matches, the greedy split is returned with method "greedy".
    """
    greedy = []
    opened = False
    for length in lengths:
        if opened:
            greedy[-1][0] += length
            greedy[-1][1] += 1
        else:
            greedy.append([length, 1])
        opened = length == SPLIT_LEN
    greedy = [tuple(group) for group in greedy]
    if len(greedy) == page_count:
        return greedy, "split"
    if len(lengths) == page_count:
        return [(length, 1) for length in lengths], "single"
    return greedy, "greedy"


@dataclass
class Layout:
    source: str
    stored_offset: int | None = None
    stored_length: int | None = None
    page_map: PageMap | None = None
    page_map_issue: Issue | None = None
    pages: list = field(default_factory=list)
    system_len: int = 0
    graphics_len: int = 0
    pointers: dict = field(default_factory=dict)
    issues: list = field(default_factory=list)
    streams: list = field(default_factory=list)

    def add(self, code, detail):
        self.issues.append(Issue(code, detail))

    @property
    def status(self):
        if self.page_map is None:
            return "unverified"
        codes = {issue.code for issue in self.issues}
        if "missing_pages" in codes:
            return "partial"
        if codes - {"pointers_outside"}:
            return "unverified"
        return "complete"

    def report(self):
        out = {
            "source": self.source,
            "status": self.status,
            "page_map": None
            if self.page_map is None
            else {
                "offset": self.page_map.offset,
                "system_pages": self.page_map.system_pages,
                "graphics_pages": self.page_map.graphics_pages,
                "byte_len": self.page_map.byte_len,
            },
            "page_map_error": None
            if self.page_map_issue is None
            else {"code": self.page_map_issue.code, "detail": self.page_map_issue.detail},
            "system_size": self.system_len,
            "graphics_size": self.graphics_len,
            "pages": self.pages,
            "pointers": self.pointers,
            "issues": [{"code": issue.code, "detail": issue.detail} for issue in self.issues],
            "streams": self.streams,
        }
        if self.stored_offset is not None:
            out["stored_offset"] = self.stored_offset
        if self.stored_length is not None:
            out["stored_length"] = self.stored_length
        return out


def resource_map_offset(system: bytes):
    """The page map offset if the buffer starts like a RAGE resource."""
    if len(system) < PAGE_MAP_HEADER_LEN:
        return None
    if u64_at(system, 0) != 0:
        return None
    pointer = decode_pointer(u64_at(system, 8))
    if pointer is None or pointer.segment != "system":
        return None
    if pointer.offset < PAGE_MAP_HEADER_LEN:
        return None
    return pointer.offset


def scan_pointers(layout: Layout, system: bytes, graphics_len: int):
    counts = {
        "system": 0,
        "graphics": 0,
        "system_outside": 0,
        "graphics_outside": 0,
    }
    for at in range(0, len(system) - 7, 8):
        pointer = decode_pointer(u64_at(system, at))
        if pointer is None:
            continue
        counts[pointer.segment] += 1
        limit = len(system) if pointer.segment == "system" else graphics_len
        if pointer.offset >= limit:
            counts[pointer.segment + "_outside"] += 1
    layout.pointers = counts
    if counts["system_outside"] or counts["graphics_outside"]:
        layout.add(
            "pointers_outside",
            f"{counts['system_outside']} system and {counts['graphics_outside']} "
            "graphics pointer-like values point past the reconstructed segment; "
            "text, hashes and fill patterns can match the pointer encoding",
        )


def greedy_groups(lengths):
    groups = []
    opened = False
    for length in lengths:
        if opened:
            groups[-1][0] += length
            groups[-1][1] += 1
        else:
            groups.append([length, 1])
        opened = length == SPLIT_LEN
    return [tuple(group) for group in groups]


def finish_layout(layout: Layout, streams):
    lengths = [len(stream) for stream in streams]
    if not lengths:
        layout.add("no_streams", "the 16-byte prefix is not followed by a page stream")
        return
    map_offset = resource_map_offset(streams[0])
    if map_offset is None:
        layout.add("not_a_resource", "the first stream does not start with a resource header")
        return
    # The page map must lie inside the system pages it declares, so the number
    # of system pages is tried in order and checked against the map's own count.
    greedy = greedy_groups(lengths)
    page_map = None
    last_issue = Issue("map_outside", "no system page holds the page map")
    for candidate in range(1, min(len(greedy), MAX_PAGES) + 1):
        stream_count = sum(group[1] for group in greedy[:candidate])
        system = b"".join(streams[:stream_count])
        parsed, issue = parse_page_map(system, map_offset)
        if parsed is None:
            last_issue = issue
            if issue.code != "map_outside":
                layout.page_map_issue = issue
                return
            continue
        last_issue = issue
        page_map = parsed
        if parsed.system_pages <= candidate:
            break
    layout.page_map = page_map
    if page_map is None:
        layout.page_map_issue = last_issue
        return
    page_count = page_map.pages
    groups, method = group_pages(lengths, page_count)
    if page_map.system_pages > len(groups):
        layout.add(
            "missing_pages",
            f"the page map declares {page_map.system_pages} system pages but "
            f"{len(groups)} page groups were found",
        )
    elif len(groups) < page_count:
        layout.add(
            "missing_pages",
            f"{page_count - len(groups)} of {page_count} declared pages were not found",
        )
    elif len(groups) > page_count:
        layout.add(
            "page_count",
            f"{len(groups)} pages were found but the page map declares {page_count}",
        )
    if method == "greedy":
        layout.add(
            "ambiguous_split",
            "a 32 MiB stream can either continue a page or end it; the page "
            "count fits neither reading",
        )
    system_pages = page_map.system_pages
    if len(groups) < system_pages:
        system = b"".join(streams)
        graphics = b""
    else:
        system_streams = sum(group[1] for group in groups[:system_pages])
        system = b"".join(streams[:system_streams])
        graphics = b"".join(streams[system_streams:])
    layout.system_len = len(system)
    layout.graphics_len = len(graphics)
    for index, (length, count) in enumerate(groups[:page_count]):
        layout.pages.append(
            {
                "index": index,
                "segment": "system" if index < system_pages else "graphics",
                "size": length,
                "streams": count,
            }
        )
    if page_map.offset + page_map.byte_len > layout.system_len:
        layout.add(
            "map_outside",
            f"the page map at {page_map.offset:#x} does not fit in "
            f"{layout.system_len} bytes of system data under the chosen page grouping",
        )
        return
    for segment in ("system", "graphics"):
        sizes = [page["size"] for page in layout.pages if page["segment"] == segment]
        if len(sizes) < 2:
            continue
        for index, size in enumerate(sizes):
            last = index == len(sizes) - 1
            fits = size <= PAGE_UNIT if last else size % PAGE_UNIT == 0
            if not fits:
                layout.add(
                    "page_size",
                    f"{segment} page {index + 1} of {len(sizes)} is {size:#x} bytes, "
                    "which breaks the 0x10000 size pattern",
                )
    scan_pointers(layout, system, layout.graphics_len)


def zlib_header(data: bytes, at: int = 0) -> bool:
    if at + 2 > len(data):
        return False
    cmf, flg = data[at], data[at + 1]
    return (cmf & 0x0F) == 8 and (cmf >> 4) <= 7 and (flg & 0x20) == 0 and ((cmf << 8) | flg) % 31 == 0


def inflate_bounded(handle, offset, limit, max_stream):
    """Inflate one zlib stream starting at offset, reading no further than limit."""
    handle.seek(offset)
    decoder = zlib.decompressobj(15)
    out = bytearray()
    consumed = 0
    remaining = limit - offset
    while not decoder.eof:
        if remaining <= 0:
            raise ResourceError(f"the stream at {offset:#x} is truncated")
        chunk = handle.read(min(STREAM_CHUNK, remaining))
        if not chunk:
            raise ResourceError(f"the stream at {offset:#x} is truncated")
        remaining -= len(chunk)
        consumed += len(chunk)
        try:
            out += decoder.decompress(chunk, max_stream + 1 - len(out))
        except zlib.error as err:
            raise ResourceError(f"the stream at {offset:#x} does not inflate: {err}") from err
        if len(out) > max_stream:
            raise ResourceError(f"the stream at {offset:#x} exceeds the {max_stream}-byte cap")
    return bytes(out), consumed - len(decoder.unused_data)


def read_streams(handle, offset, length, max_stream, max_total):
    """Inflate the page streams of a stored payload region."""
    if length < STORED_PREFIX_LEN:
        raise ResourceError("the payload is shorter than the 16-byte prefix")
    handle.seek(offset)
    prefix = handle.read(STORED_PREFIX_LEN)
    if any(prefix):
        raise ResourceError("the 16 bytes before the first stream are not zero")
    end = offset + length
    pos = offset + STORED_PREFIX_LEN
    total = 0
    streams = []
    records = []
    while pos + 2 <= end:
        handle.seek(pos)
        if not zlib_header(handle.read(2)):
            break
        data, consumed = inflate_bounded(handle, pos, end, max_stream)
        total += len(data)
        if total > max_total:
            raise ResourceError(f"the inflated pages exceed the {max_total}-byte cap")
        streams.append(data)
        records.append({"offset": pos, "stored_size": consumed, "inflated_size": len(data)})
        next_pos = (pos + consumed + 15) & ~15
        pad = next_pos - (pos + consumed)
        if pad:
            handle.seek(pos + consumed)
            if any(handle.read(pad)):
                raise ResourceError(f"the padding after the stream at {pos:#x} is not zero")
        pos = next_pos
    return streams, records


def analyze_payload(path, offset, length, max_stream, max_total):
    layout = Layout(source=f"{path} payload at {offset:#x}", stored_offset=offset, stored_length=length)
    with open(path, "rb") as handle:
        try:
            streams, records = read_streams(handle, offset, length, max_stream, max_total)
        except ResourceError as err:
            layout.add("payload_error", str(err))
            return layout
    layout.streams = records
    finish_layout(layout, streams)
    return layout


def analyze_decoded(path, system_length, max_total):
    layout = Layout(source=f"{path} decoded, system length {system_length}")
    with open(path, "rb") as handle:
        handle.seek(0, 2)
        size = handle.tell()
        if system_length <= 0 or system_length > size:
            layout.add("size_error", f"system length {system_length} is outside the file")
            return layout
        if size > max_total:
            layout.add("total_cap", f"the decoded resource exceeds the {max_total}-byte cap")
            return layout
        handle.seek(0)
        system = handle.read(system_length)
        graphics = handle.read()
    layout.system_len = len(system)
    layout.graphics_len = len(graphics)
    map_offset = resource_map_offset(system)
    if map_offset is None:
        layout.add("not_a_resource", "the system data does not start with a resource header")
        return layout
    layout.page_map, layout.page_map_issue = parse_page_map(system, map_offset)
    if layout.page_map is None:
        return layout
    for index in range(layout.page_map.pages):
        layout.pages.append(
            {
                "index": index,
                "segment": "system" if index < layout.page_map.system_pages else "graphics",
                "size": None,
                "streams": None,
            }
        )
    scan_pointers(layout, system, layout.graphics_len)
    return layout


def print_text(report):
    print(f"source:      {report['source']}")
    print(f"status:      {report['status']}")
    if "stored_offset" in report:
        print(f"stored:      {report['stored_offset']:#x} + {report['stored_length']:#x} bytes")
    page_map = report["page_map"]
    if page_map is None:
        err = report["page_map_error"]
        print(f"page map:    none ({err['code']}: {err['detail']})")
    else:
        print(
            f"page map:    at {page_map['offset']:#x}, {page_map['system_pages']} system "
            f"and {page_map['graphics_pages']} graphics pages, {page_map['byte_len']} bytes"
        )
    print(f"system:      {report['system_size']} bytes")
    print(f"graphics:    {report['graphics_size']} bytes")
    if report["pages"]:
        for page in report["pages"]:
            size = "-" if page["size"] is None else f"{page['size']:#x}"
            print(
                f"  page {page['index']}: {page['segment']:<8} {size:>12} "
                f"{page['streams'] if page['streams'] is not None else '-'} stream(s)"
            )
    if report["streams"]:
        for index, stream in enumerate(report["streams"]):
            print(
                f"  stream {index}: {stream['offset']:#x} stored {stream['stored_size']} "
                f"inflated {stream['inflated_size']}"
            )
    pointers = report["pointers"]
    if pointers:
        print(
            f"pointers:    {pointers['system']} system ({pointers['system_outside']} outside), "
            f"{pointers['graphics']} graphics ({pointers['graphics_outside']} outside)"
        )
    for issue in report["issues"]:
        print(f"issue:       {issue['code']}: {issue['detail']}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="mode", required=True)

    stored = sub.add_parser("payload", help="read a resource stored as 16 zero bytes and zlib chunks")
    stored.add_argument("--file", required=True, help="archive or file that holds the payload")
    stored.add_argument("--offset", required=True, type=lambda text: int(text, 0))
    stored.add_argument("--length", required=True, type=lambda text: int(text, 0),
                        help="stored length of the entry, from the RPF9 location record")
    stored.add_argument("--max-stream", type=lambda text: int(text, 0), default=MAX_STREAM)
    stored.add_argument("--max-total", type=lambda text: int(text, 0), default=MAX_TOTAL)

    decoded = sub.add_parser("decoded", help="read a resource whose pages are already inflated")
    decoded.add_argument("--file", required=True)
    decoded.add_argument("--system-length", required=True, type=lambda text: int(text, 0),
                         help="bytes of system data before the graphics segment")
    decoded.add_argument("--max-total", type=lambda text: int(text, 0), default=MAX_TOTAL)

    for command in (stored, decoded):
        command.add_argument("--json", action="store_true", help="print the report as JSON")

    args = parser.parse_args(argv)
    if args.mode == "payload":
        layout = analyze_payload(
            args.file, args.offset, args.length, args.max_stream, args.max_total
        )
    else:
        layout = analyze_decoded(args.file, args.system_length, args.max_total)
    report = layout.report()
    if args.json:
        json.dump(report, sys.stdout, indent=2)
        print()
    else:
        print_text(report)
    return 0 if report["status"] == "complete" else 1


if __name__ == "__main__":
    sys.exit(main())
