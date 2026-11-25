#!/usr/bin/env python3
"""Reconstruct the pages of a stored RAGE resource row.

A stored row is 16 zero bytes followed by one chunk per page. A chunk is
either a zlib stream or a raw (uncompressed) page. The page map, at the system
offset named by the qword at +8, declares how many system and graphics pages
exist. Reconstruction must cover every declared page; a readable page map does
not end the reconstruction. A raw stored range is classified by the declared
page count and, when supplied, the declared logical size; a zlib header is only
a secondary check.

The tool reads only, bounds every stream and the total reconstructed bytes,
and reports what it cannot establish. See formats/resources/pages.md for the
layout.
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
PAGE_UNIT = 0x1_0000
SPLIT_LEN = 0x200_0000
STORED_PREFIX_LEN = 16

MAX_STREAM = 256 << 20
MAX_TOTAL = 512 << 20
MAX_PAGES = 2 * 0xFF
STREAM_CHUNK = 1 << 20


class ResourceError(Exception):
    pass


class Issue:
    def __init__(self, code: str, detail: str):
        self.code = code
        self.detail = detail

    def as_dict(self):
        return {"code": self.code, "detail": self.detail}


@dataclass
class Chunk:
    offset: int
    stored_size: int
    data: bytes
    kind: str  # "zlib" or "raw"

    @property
    def size(self) -> int:
        return len(self.data)


@dataclass
class PageMap:
    offset: int
    system_pages: int
    graphics_pages: int

    @property
    def byte_len(self) -> int:
        return PAGE_MAP_HEADER_LEN + 8 * (self.system_pages + self.graphics_pages)

    @property
    def total(self) -> int:
        return self.system_pages + self.graphics_pages


@dataclass
class Page:
    index: int
    segment: str
    size: int
    streams: int
    storage: str  # "zlib", "split", "raw" or "packed"


@dataclass
class Layout:
    source: str
    stored_offset: int | None = None
    stored_length: int | None = None
    page_map: PageMap | None = None
    pages: list = field(default_factory=list)
    chunks: list = field(default_factory=list)
    issues: list = field(default_factory=list)
    notes: list = field(default_factory=list)

    @property
    def status(self):
        if self.page_map is None:
            return "unverified"
        codes = {issue.code for issue in self.issues}
        if "missing_pages" in codes:
            return "partial"
        if codes - {"trailing_raw"}:
            return "unverified"
        return "complete"

    def add(self, code, detail):
        self.issues.append(Issue(code, detail))

    def note(self, detail):
        self.notes.append(detail)

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
            "system_size": sum(p.size for p in self.pages if p.segment == "system"),
            "graphics_size": sum(p.size for p in self.pages if p.segment == "graphics"),
            "pages": [
                {
                    "index": page.index,
                    "segment": page.segment,
                    "size": page.size,
                    "streams": page.streams,
                    "storage": page.storage,
                }
                for page in self.pages
            ],
            "chunks": [
                {
                    "offset": chunk.offset,
                    "stored_size": chunk.stored_size,
                    "inflated_size": len(chunk.data),
                    "kind": chunk.kind,
                }
                for chunk in self.chunks
            ],
            "issues": [issue.as_dict() for issue in self.issues],
            "notes": self.notes,
        }
        if self.stored_offset is not None:
            out["stored_offset"] = self.stored_offset
        if self.stored_length is not None:
            out["stored_length"] = self.stored_length
        return out


def zlib_header(data: bytes, at: int = 0) -> bool:
    if at + 2 > len(data):
        return False
    cmf, flg = data[at], data[at + 1]
    return (
        (cmf & 0x0F) == 8
        and (cmf >> 4) <= 7
        and (flg & 0x20) == 0
        and ((cmf << 8) | flg) % 31 == 0
    )


def align16(value: int) -> int:
    return (value + 15) & ~15


def inflate_at(buf: bytes, at: int, limit: int) -> tuple[bytes, int]:
    decoder = zlib.decompressobj(15)
    out = bytearray()
    consumed = 0
    while not decoder.eof:
        if at + consumed >= limit:
            raise ResourceError(f"the stream at {at:#x} is truncated")
        chunk = buf[at + consumed : at + consumed + STREAM_CHUNK]
        if not chunk:
            raise ResourceError(f"the stream at {at:#x} is truncated")
        consumed += len(chunk)
        try:
            out += decoder.decompress(chunk, MAX_STREAM + 1 - len(out))
        except zlib.error as err:
            raise ResourceError(f"the stream at {at:#x} does not inflate: {err}") from err
        if len(out) > MAX_STREAM:
            raise ResourceError(f"the stream at {at:#x} exceeds the {MAX_STREAM}-byte cap")
    return bytes(out), consumed - len(decoder.unused_data)


def read_chunks(buf: bytes, layout: Layout, max_total: int = MAX_TOTAL) -> list[Chunk]:
    if len(buf) < STORED_PREFIX_LEN:
        raise ResourceError("the entry is shorter than the 16-byte prefix")
    if any(buf[:STORED_PREFIX_LEN]):
        raise ResourceError("the 16 bytes before the first chunk are not zero")
    chunks: list[Chunk] = []
    total = 0
    pos = STORED_PREFIX_LEN
    while pos < len(buf):
        data = None
        used = 0
        if zlib_header(buf, pos):
            try:
                data, used = inflate_at(buf, pos, len(buf))
            except ResourceError as err:
                # A raw page can begin with bytes that look like a zlib header.
                # The declared page count and logical size decide later.
                layout.note(f"a zlib-like header at {pos:#x} does not inflate: {err}")
        if data is not None:
            chunks.append(Chunk(pos, used, data, "zlib"))
            total += len(data)
            if total > max_total:
                raise ResourceError(
                    f"the reconstructed chunks exceed the {max_total}-byte cap "
                    f"(observed {total})"
                )
            next_pos = align16(pos + used)
            if any(buf[pos + used : next_pos]):
                raise ResourceError(f"the padding after the stream at {pos:#x} is not zero")
            pos = next_pos
            continue
        tail = buf[pos:]
        chunks.append(Chunk(pos, len(tail), tail, "raw"))
        total += len(tail)
        if total > max_total:
            raise ResourceError(
                f"the reconstructed chunks exceed the {max_total}-byte cap "
                f"(observed {total})"
            )
        pos = len(buf)
    return chunks


def parse_page_map(decoded: bytes, offset: int):
    if offset < PAGE_MAP_HEADER_LEN:
        return None, Issue("map_in_header", f"the page map offset {offset:#x} is below the 16-byte header")
    if offset + PAGE_MAP_HEADER_LEN > len(decoded):
        return None, Issue("map_outside", f"the page map at {offset:#x} is outside {len(decoded)} bytes")
    system_pages = decoded[offset + 8]
    graphics_pages = decoded[offset + 9]
    page_map = PageMap(offset, system_pages, graphics_pages)
    if offset + page_map.byte_len > len(decoded):
        return None, Issue(
            "map_outside",
            f"the page map at {offset:#x} needs {page_map.byte_len} bytes but only "
            f"{len(decoded) - offset} were reconstructed",
        )
    body = decoded[offset : offset + page_map.byte_len]
    bad = [at for at, byte in enumerate(body) if byte and at not in (8, 9)]
    if bad:
        return None, Issue(
            "map_nonzero",
            "the page map has non-zero bytes at offsets " + ", ".join(hex(at) for at in bad[:8]),
        )
    if system_pages == 0:
        return None, Issue("no_system_page", "the page map declares no system page")
    return page_map, None


def zlib_groups(chunks: list[Chunk]):
    """Group consecutive zlib chunks into pages: a split stream continues."""
    groups = []
    opened = False
    for chunk in chunks:
        if chunk.kind == "zlib" and opened and groups:
            groups[-1].append(chunk)
        else:
            groups.append([chunk])
        opened = chunk.kind == "zlib" and chunk.size == SPLIT_LEN
    return groups


def split_candidate(group, deficit, storage):
    """Split one group into 1 + deficit pages if the size pattern allows it."""
    total = sum(chunk.size for chunk in group)
    count = deficit + 1
    if count == 1:
        if total < 1 or total > PAGE_UNIT:
            return None
        return [(total, 1, storage)]
    last = None
    for candidate in range(min(PAGE_UNIT, total), 0, -1):
        rest = total - candidate
        if rest >= (count - 1) * PAGE_UNIT and rest % PAGE_UNIT == 0:
            last = candidate
            break
    if last is None:
        return None
    rest = total - last
    pages = [(rest - (count - 2) * PAGE_UNIT, 1, storage)]
    for _ in range(count - 2):
        pages.append((PAGE_UNIT, 1, storage))
    pages.append((last, 1, storage))
    return pages


def assign_pages(chunks, page_map, layout, logical_size=None):
    groups = zlib_groups(chunks)
    declared = page_map.total
    candidates = []
    for group in groups:
        size = sum(chunk.size for chunk in group)
        if group[0].kind == "raw":
            candidates.append({"size": size, "streams": 1, "storage": "raw", "group": group})
        elif len(group) > 1:
            candidates.append({"size": size, "streams": len(group), "storage": "split", "group": group})
        else:
            candidates.append({"size": size, "streams": 1, "storage": "zlib", "group": group})

    # A raw stored range is classified by the declared page count and the
    # declared logical size. A zlib header is only a secondary check.
    raw = candidates[-1] if candidates and candidates[-1]["storage"] == "raw" else None
    if raw is not None:
        raw_bytes = raw["group"][0].data
        zlib_total = sum(candidate["size"] for candidate in candidates[:-1])
        needed = declared - (len(candidates) - 1)
        fits_logical = logical_size is None or zlib_total + raw["size"] == logical_size
        candidates.pop()
        if needed >= 1:
            split = split_candidate(raw["group"], needed - 1, "raw")
            if split is not None and fits_logical:
                for size, streams, storage in split:
                    candidates.append(
                        {"size": size, "streams": streams, "storage": storage, "group": None}
                    )
                layout.note(
                    f"the {raw['size']:#x}-byte raw stored range completes the declared "
                    "page count and is reconstructed as a raw page"
                )
            else:
                if any(raw_bytes):
                    layout.issues.append(
                        Issue(
                            "trailing_raw",
                            f"{raw['size']:#x} raw bytes do not complete the declared pages",
                        )
                    )
                else:
                    layout.note(f"{raw['size']} zero bytes after the last chunk")
                if split is not None and not fits_logical:
                    layout.note("the raw range does not match the declared logical size")
        else:
            if any(raw_bytes):
                layout.issues.append(
                    Issue(
                        "trailing_raw",
                        f"{raw['size']:#x} raw bytes follow the declared pages and are not a page",
                    )
                )
            else:
                layout.note(f"{raw['size']} zero bytes after the last chunk")

    # If zlib grouping still leaves a gap, a stream may pack several pages.
    if len(candidates) < declared:
        deficit = declared - len(candidates)
        for index in range(len(candidates) - 1, -1, -1):
            group = candidates[index]["group"]
            if group is None or candidates[index]["storage"] not in ("zlib", "split"):
                continue
            split = split_candidate(group, deficit, "packed")
            if split is not None:
                candidates[index : index + 1] = [
                    {"size": size, "streams": 1, "storage": storage, "group": None}
                    for size, streams, storage in split
                ]
                layout.note(
                    "one stream spans several declared pages; the split follows the "
                    "0x10000 page unit and is not confirmed by an observed packed page"
                )
                break
    return candidates


def analyze_bytes(buf: bytes, source: str, max_total: int = MAX_TOTAL,
                  logical_size: int | None = None) -> Layout:
    layout = Layout(source=source)
    try:
        layout.chunks = read_chunks(buf, layout, max_total)
    except ResourceError as err:
        layout.add("payload_error", str(err))
        return layout
    if not layout.chunks:
        layout.add("payload_error", "no chunk follows the 16-byte prefix")
        return layout
    first = layout.chunks[0].data
    if len(first) < PAGE_MAP_HEADER_LEN or struct.unpack_from("<Q", first, 0)[0] != 0:
        layout.add("not_a_resource", "the first chunk does not start with a resource header")
        return layout
    pointer = struct.unpack_from("<Q", first, 8)[0]
    if pointer >> 32 or pointer >> 28 != 5:
        layout.add("not_a_resource", "the qword at +8 is not a system pointer")
        return layout
    map_offset = pointer & OFFSET_MASK
    decoded = b"".join(chunk.data for chunk in layout.chunks)
    page_map, issue = parse_page_map(decoded, map_offset)
    if page_map is None:
        layout.page_map = None
        layout.add(issue.code, issue.detail)
        return layout
    layout.page_map = page_map
    if page_map.total > MAX_PAGES:
        layout.add("page_count", f"the page map declares {page_map.total} pages")
        return layout

    candidates = assign_pages(layout.chunks, page_map, layout, logical_size)
    page_total = sum(candidate["size"] for candidate in candidates)
    if page_total > max_total:
        layout.add(
            "payload_error",
            f"the reconstructed pages exceed the {max_total}-byte cap (observed {page_total})",
        )
        return layout
    if len(candidates) < page_map.total:
        layout.add(
            "missing_pages",
            f"{page_map.total - len(candidates)} of {page_map.total} declared pages were not found",
        )
    elif len(candidates) > page_map.total:
        layout.add(
            "page_count",
            f"{len(candidates)} page groups were found but the page map declares {page_map.total}",
        )
        candidates = candidates[: page_map.total]
    system_pages = page_map.system_pages
    for index, candidate in enumerate(candidates):
        segment = "system" if index < system_pages else "graphics"
        layout.pages.append(
            Page(index, segment, candidate["size"], candidate["streams"], candidate["storage"])
        )
    if len(candidates) < system_pages:
        layout.add(
            "missing_pages",
            f"{len(candidates)} of {system_pages} system pages were found",
        )
    system_size = sum(page.size for page in layout.pages if page.segment == "system")
    if map_offset + page_map.byte_len > system_size:
        layout.add(
            "map_outside",
            f"the page map at {map_offset:#x} does not fit in {system_size} bytes of system data",
        )
        return layout
    for segment in ("system", "graphics"):
        pages = [page for page in layout.pages if page.segment == segment]
        if len(pages) < 2:
            continue
        for index, page in enumerate(pages):
            last = index == len(pages) - 1
            fits = page.size <= PAGE_UNIT if last else page.size % PAGE_UNIT == 0
            if not fits:
                layout.add(
                    "page_size",
                    f"{segment} page {index + 1} of {len(pages)} is {page.size:#x} bytes, "
                    "which breaks the 0x10000 size pattern",
                )
    return layout


def analyze_file(path, offset, length, max_total: int = MAX_TOTAL,
                 logical_size: int | None = None):
    with open(path, "rb") as handle:
        handle.seek(offset)
        buf = handle.read(length)
    if len(buf) != length:
        layout = Layout(source=f"{path} payload at {offset:#x}", stored_offset=offset, stored_length=length)
        layout.add("payload_error", f"the entry needs {length} bytes but only {len(buf)} are present")
        return layout
    layout = analyze_bytes(buf, f"{path} payload at {offset:#x}", max_total, logical_size)
    layout.stored_offset = offset
    layout.stored_length = length
    return layout


def print_text(report):
    print(f"source:      {report['source']}")
    print(f"status:      {report['status']}")
    print(f"stored:      {report['stored_offset']:#x} + {report['stored_length']:#x} bytes")
    page_map = report["page_map"]
    if page_map is None:
        print("page map:    none")
    else:
        print(
            f"page map:    at {page_map['offset']:#x}, {page_map['system_pages']} system "
            f"and {page_map['graphics_pages']} graphics pages, {page_map['byte_len']} bytes"
        )
    print(f"system:      {report['system_size']} bytes")
    print(f"graphics:    {report['graphics_size']} bytes")
    for page in report["pages"]:
        print(
            f"  page {page['index']}: {page['segment']:<8} {page['size']:>10} "
            f"{page['streams']} chunk(s) {page['storage']}"
        )
    for chunk in report["chunks"]:
        print(
            f"  chunk {chunk['kind']:<4} at +{chunk['offset']:#x} stored {chunk['stored_size']} "
            f"inflated {chunk['inflated_size']}"
        )
    for issue in report["issues"]:
        print(f"issue:       {issue['code']}: {issue['detail']}")
    for note in report["notes"]:
        print(f"note:        {note}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--file", required=True, help="archive or file that holds the stored entry")
    parser.add_argument("--offset", required=True, type=lambda text: int(text, 0),
                        help="payload offset of the entry")
    parser.add_argument("--length", required=True, type=lambda text: int(text, 0),
                        help="stored length of the entry")
    parser.add_argument("--logical-size", type=lambda text: int(text, 0),
                        help="logical size from the RPF9 row, when known")
    parser.add_argument("--max-total", type=lambda text: int(text, 0), default=MAX_TOTAL,
                        help=f"cap on reconstructed bytes (default {MAX_TOTAL})")
    parser.add_argument("--json", action="store_true", help="print the report as JSON")
    args = parser.parse_args(argv)
    layout = analyze_file(args.file, args.offset, args.length, args.max_total, args.logical_size)
    report = layout.report()
    if args.json:
        json.dump(report, sys.stdout, indent=2)
        print()
    else:
        print_text(report)
    return 0 if report["status"] == "complete" else 1


if __name__ == "__main__":
    sys.exit(main())
