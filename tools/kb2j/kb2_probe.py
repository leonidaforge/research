#!/usr/bin/env python3
"""Bounded inspector for KB2j and KB2n container headers."""

from __future__ import annotations

import argparse
import json
import os
import struct
import sys

HEADER_SIZE = 0x30
SUPPORTED_SIGNATURES = (b"KB2j", b"KB2n")
MAX_AUDIO_TRACKS = 64
DEFAULT_MAX_TABLE_BYTES = 8 * 1024 * 1024


class Kb2Error(Exception):
    """Raised when a payload cannot be inspected as a KB2 container."""


def _u16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def _u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def probe_file(path: str, max_table_bytes: int = DEFAULT_MAX_TABLE_BYTES) -> dict:
    file_size = os.path.getsize(path)
    if file_size < HEADER_SIZE:
        raise Kb2Error("payload is shorter than the 48-byte header")

    with open(path, "rb") as handle:
        header = handle.read(HEADER_SIZE)
        signature = header[:4]
        if signature not in SUPPORTED_SIGNATURES:
            raise Kb2Error(f"unsupported signature {signature!r}")

        size_field = _u32(header, 0x04)
        frame_count = _u32(header, 0x08)
        if frame_count == 0:
            raise Kb2Error("payload declares zero frames")
        largest_frame = _u32(header, 0x0C)
        duplicate_count = _u32(header, 0x10)
        width = _u32(header, 0x14)
        height = _u32(header, 0x18)
        rate_num = _u32(header, 0x1C)
        rate_den = _u32(header, 0x20)
        field_24 = _u16(header, 0x24)
        field_26 = _u16(header, 0x26)
        audio_count = _u32(header, 0x28)
        variant = _u32(header, 0x2C)

        if audio_count > MAX_AUDIO_TRACKS:
            raise Kb2Error(f"audio track count {audio_count} exceeds the probe limit")
        descriptor_size = 12 * audio_count
        table_start = HEADER_SIZE + descriptor_size
        table_size = 4 * (frame_count + 1)
        if table_size > max_table_bytes:
            raise Kb2Error(f"frame table of {table_size} bytes exceeds the probe limit")
        if table_start + table_size > file_size:
            raise Kb2Error("frame table extends past the end of the payload")

        handle.seek(HEADER_SIZE)
        descriptors = handle.read(descriptor_size)
        handle.seek(table_start)
        table = handle.read(table_size)

    audio_tracks = []
    for index in range(audio_count):
        size_value = _u32(descriptors, 4 * index)
        rate_flags = _u32(descriptors, 4 * audio_count + 4 * index)
        track_value = _u32(descriptors, 8 * audio_count + 4 * index)
        audio_tracks.append(
            {
                "size_value": size_value,
                "sample_rate": rate_flags & 0xFFFF,
                "flags": rate_flags >> 16,
                "track_value": track_value,
            }
        )

    offsets = list(struct.unpack_from(f"<{frame_count + 1}I", table, 0))
    table_end = table_start + table_size
    monotonic = all(left <= right for left, right in zip(offsets, offsets[1:]))
    first_is_end_plus_one = offsets[0] == table_end + 1
    last_is_file_size = offsets[-1] == file_size

    intervals = []
    if offsets[1] >= table_end:
        intervals.append(offsets[1] - table_end)
    for index in range(1, frame_count):
        if offsets[index + 1] >= offsets[index]:
            intervals.append(offsets[index + 1] - offsets[index])
    max_interval = max(intervals) if intervals else None
    interval_within_limit = max_interval is None or max_interval <= largest_frame

    return {
        "path": path,
        "signature": signature.decode("ascii"),
        "file_size": file_size,
        "size_field": size_field,
        "declared_size": size_field + 8,
        "size_field_matches_file": size_field + 8 == file_size,
        "frame_count": frame_count,
        "duplicate_frame_count": duplicate_count,
        "frame_count_matches_duplicate": frame_count == duplicate_count,
        "largest_frame_size": largest_frame,
        "width": width,
        "height": height,
        "rate_numerator": rate_num,
        "rate_denominator": rate_den,
        "field_24": field_24,
        "field_26": field_26,
        "audio_track_count": audio_count,
        "variant": f"0x{variant:08X}",
        "audio_tracks": audio_tracks,
        "frame_table": {
            "start": table_start,
            "entries": frame_count + 1,
            "end": table_end,
            "first_offset": offsets[0],
            "last_offset": offsets[-1],
            "monotonic": monotonic,
            "first_is_end_plus_one": first_is_end_plus_one,
            "last_is_file_size": last_is_file_size,
            "max_interval": max_interval,
            "max_interval_within_largest": interval_within_limit,
        },
    }


def _valid(result: dict) -> bool:
    table = result["frame_table"]
    return all(
        (
            result["size_field_matches_file"],
            result["frame_count_matches_duplicate"],
            table["monotonic"],
            table["first_is_end_plus_one"],
            table["last_is_file_size"],
            table["max_interval_within_largest"],
        )
    )


def _print_text(result: dict) -> None:
    table = result["frame_table"]
    print(f"path: {result['path']}")
    print(f"signature: {result['signature']}")
    print(
        f"file size: {result['file_size']} bytes; "
        f"size field: {result['size_field']} "
        f"(declared {result['declared_size']}, "
        f"matches: {'yes' if result['size_field_matches_file'] else 'no'})"
    )
    print(
        f"frames: {result['frame_count']} "
        f"(duplicate: {result['duplicate_frame_count']}); "
        f"largest frame: {result['largest_frame_size']} bytes"
    )
    print(
        f"dimensions: {result['width']}x{result['height']}; "
        f"rate: {result['rate_numerator']}/{result['rate_denominator']}"
    )
    print(
        f"header fields: +0x24={result['field_24']}, "
        f"+0x26={result['field_26']}, +0x2c={result['variant']}"
    )
    print(f"audio tracks: {result['audio_track_count']}")
    for index, track in enumerate(result["audio_tracks"]):
        print(
            f"  {index}: sample rate {track['sample_rate']}, "
            f"flags 0x{track['flags']:04X}, "
            f"size value {track['size_value']}, track value {track['track_value']}"
        )
    print(
        f"frame table: {table['entries']} entries at {table['start']}..{table['end']}; "
        f"first {table['first_offset']}, last {table['last_offset']}"
    )
    print(
        "  monotonic: "
        f"{'yes' if table['monotonic'] else 'no'}; "
        "first is end plus one: "
        f"{'yes' if table['first_is_end_plus_one'] else 'no'}; "
        "last is file size: "
        f"{'yes' if table['last_is_file_size'] else 'no'}"
    )
    if table["max_interval"] is None:
        print("  max interval: none")
    else:
        print(
            f"  max interval: {table['max_interval']}; "
            "within largest frame: "
            f"{'yes' if table['max_interval_within_largest'] else 'no'}"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Inspect KB2j/KB2n container headers and frame tables."
    )
    parser.add_argument("payload", nargs="+", help="extracted KB2j or KB2n payload")
    parser.add_argument("--json", action="store_true", help="write JSON")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="exit non-zero when a structural validation fails",
    )
    parser.add_argument(
        "--max-table-bytes",
        type=int,
        default=DEFAULT_MAX_TABLE_BYTES,
        help=f"frame table size limit (default: {DEFAULT_MAX_TABLE_BYTES})",
    )
    args = parser.parse_args(argv)

    results = []
    failed = False
    for path in args.payload:
        try:
            result = probe_file(path, args.max_table_bytes)
        except (Kb2Error, OSError) as error:
            print(f"{path}: {error}", file=sys.stderr)
            failed = True
            continue
        results.append(result)
        if args.strict and not _valid(result):
            failed = True

    if args.json:
        output = results[0] if len(results) == 1 else results
        print(json.dumps(output, indent=2))
    else:
        for index, result in enumerate(results):
            if index:
                print()
            _print_text(result)

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
