#!/usr/bin/env python3
"""Bounded inspector for KB2j and KB2n containers.

The probe reads headers, the frame index and audio descriptors. Optional
validation walks the audio records at frame starts without reading or printing
payload bytes.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import struct
import sys
import tempfile

HEADER_SIZE = 0x30
SUPPORTED_SIGNATURES = (b"KB2j", b"KB2n")
MAX_AUDIO_TRACKS = 64
DEFAULT_MAX_TABLE_BYTES = 8 * 1024 * 1024
DEFAULT_MAX_FRAMES = 1_000_000


class Kb2Error(Exception):
    """Raised when a payload cannot be inspected as a KB2 container."""


def _u16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def _u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def _read_frame_records(handle, payload_offset, file_size, starts, ends,
                        audio_count, max_frames):
    """Read the leading per-track records of each frame without payload data."""
    result = {
        "frames": 0,
        "packets": 0,
        "zero_packets": 0,
        "max_packet": 0,
        "max_decoded": 0,
        "violations": [],
        "decoded_values": {},
    }
    for frame_index, (start, end) in enumerate(zip(starts, ends)):
        if frame_index >= max_frames:
            result["violations"].append({"kind": "frame_limit", "frame": frame_index})
            break
        if end < start:
            result["violations"].append({"kind": "negative_frame", "frame": frame_index})
            break
        position = start
        bounded = True
        for track in range(audio_count):
            if position + 4 > end:
                result["violations"].append(
                    {"kind": "size_past_frame", "frame": frame_index, "track": track}
                )
                bounded = False
                break
            handle.seek(payload_offset + position)
            record_bytes = struct.unpack("<I", handle.read(4))[0]
            if record_bytes == 0:
                result["zero_packets"] += 1
                position += 4
                continue
            if position + 4 + record_bytes > end:
                result["violations"].append(
                    {
                        "kind": "record_past_frame",
                        "frame": frame_index,
                        "track": track,
                        "record_bytes": record_bytes,
                        "remaining": end - position,
                    }
                )
                bounded = False
                break
            handle.seek(payload_offset + position + 4)
            decoded = struct.unpack("<I", handle.read(4))[0]
            result["packets"] += 1
            result["max_packet"] = max(result["max_packet"], record_bytes)
            result["max_decoded"] = max(result["max_decoded"], decoded)
            result["decoded_values"][decoded] = result["decoded_values"].get(decoded, 0) + 1
            position += 4 + record_bytes
        if not bounded:
            break
        result["frames"] += 1
    return result


def probe_file(path: str, max_table_bytes: int = DEFAULT_MAX_TABLE_BYTES,
               validate_frames: bool = False, max_frames: int = DEFAULT_MAX_FRAMES) -> dict:
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
        flags32 = _u32(header, 0x24)
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
        masked = [value & ~1 for value in offsets]
        monotonic = all(left <= right for left, right in zip(offsets, offsets[1:]))
        masked_monotonic = all(left <= right for left, right in zip(masked, masked[1:]))
        first_is_end_plus_one = offsets[0] == table_end + 1
        last_is_file_size = offsets[-1] == file_size
        last_is_even = offsets[-1] & 1 == 0
        first_masked_is_table_end = masked[0] == table_end
        masked_in_range = all(table_end <= value <= file_size for value in masked)

        intervals = []
        if masked[1] >= table_end:
            intervals.append(masked[1] - table_end)
        for index in range(1, frame_count):
            if masked[index + 1] >= masked[index]:
                intervals.append(masked[index + 1] - masked[index])
        max_interval = max(intervals) if intervals else None
        interval_within_limit = max_interval is None or max_interval <= largest_frame

        audio_validation = None
        if validate_frames and audio_count:
            starts = [table_end] + masked[1:-1]
            ends = masked[1:]
            audio_validation = _read_frame_records(
                handle, 0, file_size, starts, ends, audio_count, max_frames
            )
            array1 = max(track["size_value"] for track in audio_tracks)
            audio_validation["array1"] = array1
            audio_validation["array1_is_max_decoded"] = (
                audio_validation["max_decoded"] == array1
            )
            audio_validation["array1_ge_max_packet"] = (
                audio_validation["max_packet"] <= array1
            )

    track_ids = [track["track_value"] for track in audio_tracks]
    validation = {
        "flags_is_u32": True,
        "alpha_bit": bool(flags32 & 0x100000),
        "keyframe_entries": sum(1 for value in offsets if value & 1),
        "entry0_is_end_plus_one": first_is_end_plus_one,
        "masked_offsets_nondecreasing": masked_monotonic,
        "masked_offsets_in_range": masked_in_range,
        "last_entry_even": last_is_even,
        "audio_track_ids_in_range": all(0 <= value < audio_count for value in track_ids),
        "audio_track_ids_distinct": len(set(track_ids)) == audio_count,
    }

    result = {
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
        "flags": f"0x{flags32:08X}",
        "flags_low16": flags32 & 0xFFFF,
        "flags_high16": flags32 >> 16,
        "alpha_bit": bool(flags32 & 0x100000),
        "audio_track_count": audio_count,
        "variant": f"0x{variant:08X}",
        "audio_tracks": audio_tracks,
        "validation": validation,
        "frame_table": {
            "start": table_start,
            "entries": frame_count + 1,
            "end": table_end,
            "first_offset": offsets[0],
            "last_offset": offsets[-1],
            "monotonic": monotonic,
            "masked_monotonic": masked_monotonic,
            "first_is_end_plus_one": first_is_end_plus_one,
            "first_masked_is_table_end": first_masked_is_table_end,
            "last_is_file_size": last_is_file_size,
            "last_is_even": last_is_even,
            "masked_in_range": masked_in_range,
            "max_interval": max_interval,
            "max_interval_within_largest": interval_within_limit,
        },
        "audio_validation": audio_validation,
    }
    return result


def _valid(result: dict) -> bool:
    table = result["frame_table"]
    checks = [
        result["size_field_matches_file"],
        result["frame_count_matches_duplicate"],
        table["monotonic"],
        table["masked_monotonic"],
        table["first_is_end_plus_one"],
        table["first_masked_is_table_end"],
        table["last_is_file_size"],
        table["last_is_even"],
        table["masked_in_range"],
        table["max_interval_within_largest"],
        result["validation"]["audio_track_ids_in_range"],
        result["validation"]["audio_track_ids_distinct"],
    ]
    audio = result.get("audio_validation")
    if audio is not None:
        checks.append(not audio["violations"])
        checks.append(audio["array1_ge_max_packet"])
    return all(checks)


def _print_text(result: dict, stream=None) -> None:
    stream = sys.stdout if stream is None else stream

    def p(*args):
        print(*args, file=stream)

    table = result["frame_table"]
    p(f"path: {result['path']}")
    p(f"signature: {result['signature']}")
    p(
        f"file size: {result['file_size']} bytes; "
        f"size field: {result['size_field']} "
        f"(declared {result['declared_size']}, "
        f"matches: {'yes' if result['size_field_matches_file'] else 'no'})"
    )
    p(
        f"frames: {result['frame_count']} "
        f"(duplicate: {result['duplicate_frame_count']}); "
        f"largest frame: {result['largest_frame_size']} bytes"
    )
    p(
        f"dimensions: {result['width']}x{result['height']}; "
        f"rate: {result['rate_numerator']}/{result['rate_denominator']}"
    )
    p(
        f"flags: {result['flags']} (low16={result['flags_low16']}, "
        f"high16={result['flags_high16']}, alpha_bit={result['alpha_bit']})"
    )
    p(f"audio tracks: {result['audio_track_count']}")
    for index, track in enumerate(result["audio_tracks"]):
        p(
            f"  {index}: sample rate {track['sample_rate']}, "
            f"flags 0x{track['flags']:04X}, "
            f"size value {track['size_value']}, track value {track['track_value']}"
        )
    p(
        f"frame table: {table['entries']} entries at {table['start']}..{table['end']}; "
        f"first {table['first_offset']}, last {table['last_offset']}"
    )
    p(
        "  monotonic: "
        f"{'yes' if table['monotonic'] else 'no'}; "
        "masked monotonic: "
        f"{'yes' if table['masked_monotonic'] else 'no'}; "
        "first is end plus one: "
        f"{'yes' if table['first_is_end_plus_one'] else 'no'}; "
        "last is file size: "
        f"{'yes' if table['last_is_file_size'] else 'no'}"
    )
    if table["max_interval"] is None:
        p("  max interval: none")
    else:
        p(
            f"  max interval: {table['max_interval']}; "
            "within largest frame: "
            f"{'yes' if table['max_interval_within_largest'] else 'no'}"
        )
    audio = result.get("audio_validation")
    if audio is not None:
        p(
            f"audio frames: {audio['frames']}; packets: {audio['packets']}; "
            f"zero-size: {audio['zero_packets']}; max packet: {audio['max_packet']}; "
            f"max decoded: {audio['max_decoded']}; array1: {audio['array1']}; "
            f"violations: {len(audio['violations'])}"
        )
        for violation in audio["violations"][:5]:
            p(f"  audio violation: {violation}")


def _output_is_inside_input(output: str, inputs: list[str]) -> bool:
    output_dir = os.path.realpath(os.path.dirname(os.path.abspath(output)) or ".")
    for path in inputs:
        input_dir = os.path.realpath(os.path.dirname(os.path.abspath(path)) or ".")
        if output_dir == input_dir or output_dir.startswith(input_dir + os.sep):
            return True
    return False


def _write_atomic(path: str, text: str) -> None:
    directory = os.path.dirname(os.path.abspath(path)) or "."
    handle = tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="\n", dir=directory, delete=False
    )
    try:
        handle.write(text)
        handle.close()
        os.replace(handle.name, path)
    except BaseException:
        handle.close()
        try:
            os.unlink(handle.name)
        except OSError:
            pass
        raise


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
        "--validate",
        action="store_true",
        help="walk the leading audio records of each frame",
    )
    parser.add_argument(
        "--max-table-bytes",
        type=int,
        default=DEFAULT_MAX_TABLE_BYTES,
        help=f"frame table size limit (default: {DEFAULT_MAX_TABLE_BYTES})",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=DEFAULT_MAX_FRAMES,
        help=f"frame validation limit (default: {DEFAULT_MAX_FRAMES})",
    )
    parser.add_argument("--output", help="write output to this file instead of stdout")
    args = parser.parse_args(argv)

    if args.output and _output_is_inside_input(args.output, args.payload):
        parser.error("refusing to write output inside an input directory")

    results = []
    failed = False
    for path in args.payload:
        try:
            result = probe_file(path, args.max_table_bytes, args.validate, args.max_frames)
        except (Kb2Error, OSError) as error:
            print(f"{path}: {error}", file=sys.stderr)
            failed = True
            continue
        results.append(result)
        if args.strict and not _valid(result):
            failed = True

    if args.json:
        output = results[0] if len(results) == 1 else results
        text = json.dumps(output, indent=2) + "\n"
    else:
        buffer = io.StringIO()
        for index, result in enumerate(results):
            if index:
                buffer.write("\n")
            _print_text(result, buffer)
        text = buffer.getvalue()

    if args.output:
        _write_atomic(args.output, text)
    else:
        sys.stdout.write(text)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
