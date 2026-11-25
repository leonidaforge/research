#!/usr/bin/env python3
"""Inspect a decoded GFx container and walk its SWF tags.

The tool reads each input read-only, refuses to write output inside an input
directory, and reports offsets, lengths, tag codes and counts. It does not print
payload bytes or movie strings. It validates the container header and a bounded
tag walk; it does not decode ActionScript, tags or rendering.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import struct
import sys

MAGIC = b"GFX"
VERSION = 0x2A
NESTED_TAG = 39
END_TAG = 0
MAX_NESTING_DEPTH = 8
DEFAULT_MAX_BYTES = 64 * 1024 * 1024


class GfxError(ValueError):
    pass


def _u16le(data, offset, limit=None):
    boundary = len(data) if limit is None else limit
    if offset + 2 > boundary:
        raise GfxError(f"read past end at 0x{offset:x}")
    return struct.unpack_from("<H", data, offset)[0]


def _u32le(data, offset, limit=None):
    boundary = len(data) if limit is None else limit
    if offset + 4 > boundary:
        raise GfxError(f"read past end at 0x{offset:x}")
    return struct.unpack_from("<I", data, offset)[0]


def rect_size(nbits: int) -> int:
    return (5 + 4 * nbits + 7) // 8


def _read_tag_header(data, offset, limit):
    if offset + 2 > limit:
        raise GfxError(f"truncated tag header at 0x{offset:x}")
    header = _u16le(data, offset, limit)
    code = header >> 6
    length = header & 0x3F
    offset += 2
    if length == 0x3F:
        length = _u32le(data, offset, limit)
        offset += 4
    return code, length, offset


def _walk(data, start, end, depth, stats, label):
    """Walk tag records in [start, end). Return (count, reaches_end, last_code)."""
    position = start
    count = 0
    last_code = None
    while position < end:
        code, length, body = _read_tag_header(data, position, end)
        if body + length > end:
            raise GfxError(
                f"{label}: tag {code} at 0x{position:x} overruns its region"
                f" (body 0x{body:x} + {length} > 0x{end:x})"
            )
        count += 1
        last_code = code
        if code == NESTED_TAG:
            stats["tag39_count"] += 1
            if length >= 4:
                if depth + 1 > MAX_NESTING_DEPTH:
                    raise GfxError(
                        f"{label}: unsupported nesting depth at tag offset 0x{position:x}"
                    )
                nested_start = body + 4
                nested_count, nested_end, _ = _walk(
                    data, nested_start, body + length, depth + 1, stats, label
                )
                if not nested_end:
                    raise GfxError(
                        f"{label}: tag 39 body at 0x{position:x} does not end at its boundary"
                    )
                stats["nested_tag_count"] += nested_count
                stats["max_depth"] = max(stats["max_depth"], depth + 1)
        position = body + length
        if code == END_TAG:
            break
    return count, position == end, last_code


def inspect_bytes(data: bytes, label: str = "<memory>") -> dict:
    size = len(data)
    if size < 0x10:
        raise GfxError(f"{label}: shorter than the container header")
    if data[0:3] != MAGIC:
        raise GfxError(f"{label}: magic is {data[0:3].hex(' ')}, not GFX")
    version = data[3]
    if version != VERSION:
        raise GfxError(f"{label}: version is 0x{version:02x}, not 0x{VERSION:02x}")
    declared_size = _u32le(data, 0x04)
    if declared_size != size:
        raise GfxError(f"{label}: length field is {declared_size}, file is {size}")

    nbits = data[0x08] >> 3
    rect_bytes = rect_size(nbits)
    swf_end = 0x08 + rect_bytes
    if swf_end + 4 > size:
        raise GfxError(
            f"{label}: RECT of {rect_bytes} bytes leaves no frame header"
        )
    frame_rate_raw = _u16le(data, swf_end)
    frame_count = _u16le(data, swf_end + 2)
    first_tag_offset = swf_end + 4
    if first_tag_offset > size:
        raise GfxError(f"{label}: first tag offset is past the file end")

    stats = {"tag39_count": 0, "nested_tag_count": 0, "max_depth": 0}
    tag_count, reaches_end, last_code = _walk(
        data, first_tag_offset, size, 0, stats, label
    )
    if not reaches_end:
        raise GfxError(f"{label}: tag walk did not reach the file end")
    if last_code != END_TAG:
        raise GfxError(f"{label}: last tag code is {last_code}, not End (0)")

    first_code, first_length, _ = _read_tag_header(data, first_tag_offset, size)

    if size - 4 < first_tag_offset:
        raise GfxError(f"{label}: no room for the two final tag headers")
    last_four = data[-4:]
    first_header = _u16le(data, size - 4)
    second_header = _u16le(data, size - 2)
    if (first_header >> 6, first_header & 0x3F) != (1, 0):
        raise GfxError(f"{label}: the last four bytes do not begin with a zero-length ShowFrame")
    if (second_header >> 6, second_header & 0x3F) != (0, 0):
        raise GfxError(f"{label}: the last four bytes do not end with a zero-length End")
    last_two = [1, 0]

    return {
        "label": label,
        "size": size,
        "sha256": hashlib.sha256(data).hexdigest(),
        "container": {
            "magic": "GFX",
            "version": version,
            "length_field": declared_size,
            "length_matches": declared_size == size,
        },
        "header": {
            "rect_nbits": nbits,
            "rect_bytes": rect_bytes,
            "frame_rate_raw": frame_rate_raw,
            "frame_rate": frame_rate_raw / 256.0,
            "frame_count": frame_count,
            "first_tag_offset": first_tag_offset,
        },
        "tags": {
            "count": tag_count,
            "max_nesting_depth": stats["max_depth"],
            "tag39_count": stats["tag39_count"],
            "nested_tag_count": stats["nested_tag_count"],
            "total_tags": tag_count + stats["nested_tag_count"],
            "first_code": first_code,
            "first_length": first_length,
            "last_code": last_code,
            "last_two_codes": last_two,
        },
        "trailer": {
            "last_four_bytes": last_four.hex(),
            "last_two_tag_headers": last_two,
        },
    }


def _print_text(report: dict, stream) -> None:
    container = report["container"]
    header = report["header"]
    tags = report["tags"]
    print(f"sample: {report['label']}", file=stream)
    print(f"size: {report['size']} bytes", file=stream)
    print(f"sha256: {report['sha256']}", file=stream)
    print(
        f"container: magic={container['magic']}"
        f" version={container['version']}"
        f" length_field={container['length_field']}"
        f" length_matches={container['length_matches']}",
        file=stream,
    )
    print(
        f"header: rect_nbits={header['rect_nbits']}"
        f" rect_bytes={header['rect_bytes']}"
        f" frame_rate={header['frame_rate']:.2f}"
        f" frame_count={header['frame_count']}"
        f" first_tag_offset=0x{header['first_tag_offset']:x}",
        file=stream,
    )
    print(
        f"tags: count={tags['count']}"
        f" max_nesting_depth={tags['max_nesting_depth']}"
        f" tag39_count={tags['tag39_count']}"
        f" nested_tag_count={tags['nested_tag_count']}"
        f" total_tags={tags['total_tags']}"
        f" first_code={tags['first_code']}"
        f" first_length={tags['first_length']}"
        f" last_two={tags['last_two_codes']}",
        file=stream,
    )
    print(
        f"trailer: last_four_bytes={report['trailer']['last_four_bytes']}"
        f" last_two_tag_headers={report['trailer']['last_two_tag_headers']}",
        file=stream,
    )


def _output_is_inside_input(output: str, inputs: list[str]) -> bool:
    output_dir = os.path.realpath(os.path.dirname(os.path.abspath(output)) or ".")
    for path in inputs:
        input_dir = os.path.realpath(os.path.dirname(os.path.abspath(path)) or ".")
        if output_dir == input_dir or output_dir.startswith(input_dir + os.sep):
            return True
    return False


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Inspect a decoded GFx container and its SWF tags.")
    parser.add_argument("samples", nargs="+", help="decoded GFx payload files")
    parser.add_argument("--json", action="store_true", help="print JSON instead of text")
    parser.add_argument("--output", help="write output to this file instead of stdout")
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES,
                        help="refuse a sample larger than this many bytes")
    args = parser.parse_args(argv)

    if args.output and _output_is_inside_input(args.output, args.samples):
        parser.error("refusing to write output inside an input directory")

    reports = []
    try:
        for path in args.samples:
            label = os.path.basename(path)
            if os.path.getsize(path) > args.max_bytes:
                raise GfxError(f"{label}: larger than the {args.max_bytes}-byte cap")
            with open(path, "rb") as handle:
                data = handle.read()
            reports.append(inspect_bytes(data, label=label))
    except (OSError, GfxError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    if args.json:
        text = json.dumps(reports, indent=2) + "\n"
    else:
        buffer = io.StringIO()
        for report in reports:
            _print_text(report, buffer)
            buffer.write("\n")
        text = buffer.getvalue()

    if args.output:
        with open(args.output, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
