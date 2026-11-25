#!/usr/bin/env python3
"""Report the observed PSIN header and tagged-section walk.

The tool is a bounded structural sampler, not a format validator. It reads
each input read-only and prints header words, section offsets, tags and
lengths. It does not assign any field or tag a meaning.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import struct
import sys

MAGIC = b"PSIN"
HEADER_SIZE = 16
SECTION_HEADER_SIZE = 8
DEFAULT_MAX_BYTES = 2 * 1024 * 1024 * 1024
DEFAULT_MAX_SECTIONS = 10_000


class PsinError(ValueError):
    pass


def _be32(data: bytes, offset: int) -> int:
    if offset + 4 > len(data):
        raise PsinError(f"read past end at 0x{offset:x}")
    return struct.unpack_from(">I", data, offset)[0]


def _tag(data: bytes, offset: int) -> str:
    raw = data[offset:offset + 4]
    if len(raw) != 4 or not all(0x20 <= byte < 0x7F for byte in raw):
        raise PsinError(f"no printable tag at 0x{offset:x}")
    return raw.decode("ascii")


def inspect_bytes(data: bytes, label: str = "<memory>",
                  max_sections: int = DEFAULT_MAX_SECTIONS) -> dict:
    size = len(data)
    if size < HEADER_SIZE:
        raise PsinError(f"{label}: shorter than the {HEADER_SIZE}-byte header")
    if data[0:4] != MAGIC:
        raise PsinError(f"{label}: magic is {data[0:4].hex(' ')}, not PSIN")

    first_offset = _be32(data, 4)
    if first_offset < HEADER_SIZE:
        raise PsinError(f"{label}: first-section offset {first_offset} is inside the header")
    if first_offset > size:
        raise PsinError(f"{label}: first-section offset {first_offset} is past the file end")

    sections = []
    offset = first_offset
    while offset < size:
        if len(sections) >= max_sections:
            raise PsinError(f"{label}: section walk exceeds the {max_sections}-section cap")
        if offset + SECTION_HEADER_SIZE > size:
            raise PsinError(f"{label}: section header at 0x{offset:x} is truncated")
        tag = _tag(data, offset)
        length = _be32(data, offset + 4)
        if length < SECTION_HEADER_SIZE:
            raise PsinError(
                f"{label}: section {tag} at 0x{offset:x} length {length} "
                f"is below the {SECTION_HEADER_SIZE}-byte header"
            )
        end = offset + length
        if end > size:
            raise PsinError(f"{label}: section {tag} at 0x{offset:x} ends past the file")
        body_length = length - SECTION_HEADER_SIZE
        sections.append({
            "tag": tag,
            "offset": offset,
            "length": length,
            "body_length": body_length,
            "body_mod_16": body_length % 16,
        })
        offset = end

    header = {
        "first_section_offset": first_offset,
        "first_section_offset_high16": first_offset >> 16,
        "first_section_offset_low16": first_offset & 0xFFFF,
        "field_06_be": struct.unpack_from(">H", data, 6)[0],
        "field_08_0f": data[8:16].hex(),
        "field_08_be": _be32(data, 8),
        "field_0c_le": struct.unpack_from("<I", data, 12)[0],
    }
    return {
        "label": label,
        "size": size,
        "sha256": hashlib.sha256(data).hexdigest(),
        "magic": "PSIN",
        "header": header,
        "sections": sections,
        "section_count": len(sections),
        "tag_sequence": [section["tag"] for section in sections],
        "checks": {
            "first_section_offset_equals_size": first_offset == size,
            "first_section_offset_aligned_16": first_offset % 16 == 0,
            "field_06_equals_size": header["field_06_be"] == size,
            "field_06_equals_low16": header["field_06_be"] == header["first_section_offset_low16"],
            "section_walk_ends_at_file_size": offset == size,
        },
    }


def _print_text(report: dict, stream) -> None:
    print(f"sample: {report['label']}", file=stream)
    print(f"size: {report['size']} bytes", file=stream)
    print(f"sha256: {report['sha256']}", file=stream)
    header = report["header"]
    print(
        "header:"
        f" first_section_offset={header['first_section_offset']}"
        f" high16=0x{header['first_section_offset_high16']:04x}"
        f" low16=0x{header['first_section_offset_low16']:04x}"
        f" field_06_be={header['field_06_be']}"
        f" field_08_0f={header['field_08_0f']}",
        file=stream,
    )
    print(f"sections: {report['section_count']}", file=stream)
    for section in report["sections"]:
        print(
            f"  {section['tag']} offset=0x{section['offset']:x}"
            f" length={section['length']} body={section['body_length']}"
            f" body_mod_16={section['body_mod_16']}",
            file=stream,
        )
    checks = report["checks"]
    print(
        "checks:"
        f" first_section_offset_equals_size={checks['first_section_offset_equals_size']}"
        f" first_section_offset_aligned_16={checks['first_section_offset_aligned_16']}"
        f" field_06_equals_size={checks['field_06_equals_size']}"
        f" field_06_equals_low16={checks['field_06_equals_low16']}"
        f" section_walk_ends_at_file_size={checks['section_walk_ends_at_file_size']}",
        file=stream,
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Report observed PSIN structural fields.")
    parser.add_argument("samples", nargs="+", help="PSIN payload files")
    parser.add_argument("--json", action="store_true", help="print JSON instead of text")
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES,
                        help="refuse a sample larger than this many bytes")
    parser.add_argument("--max-sections", type=int, default=DEFAULT_MAX_SECTIONS,
                        help="refuse a section walk above this count")
    args = parser.parse_args(argv)

    reports = []
    try:
        for path in args.samples:
            if os.path.getsize(path) > args.max_bytes:
                raise PsinError(f"{path}: larger than the {args.max_bytes}-byte cap")
            with open(path, "rb") as handle:
                data = handle.read()
            reports.append(inspect_bytes(data, label=path, max_sections=args.max_sections))
    except (OSError, PsinError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    if args.json:
        sys.stdout.write(json.dumps(reports, indent=2) + "\n")
    else:
        buffer = io.StringIO()
        for report in reports:
            _print_text(report, buffer)
            buffer.write("\n")
        sys.stdout.write(buffer.getvalue())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
