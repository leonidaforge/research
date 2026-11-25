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


def _read_frame_records(handle, payload_offset, payload_size, starts, ends,
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
        if start < 0 or end < start or end > payload_size:
            raise Kb2Error(
                f"frame {frame_index} range {start}..{end} is outside"
                f" the payload size {payload_size}"
            )
        position = start
        bounded = True
        for track in range(audio_count):
            if position + 4 > end or position + 4 > payload_size:
                result["violations"].append(
                    {
                        "kind": "size_past_frame",
                        "frame": frame_index,
                        "track": track,
                        "offset": position,
                    }
                )
                bounded = False
                break
            handle.seek(payload_offset + position)
            raw_size = handle.read(4)
            if len(raw_size) != 4:
                raise Kb2Error(
                    f"short read for frame {frame_index} track {track}"
                    f" at payload offset 0x{position:x}"
                )
            record_bytes = struct.unpack("<I", raw_size)[0]
            if record_bytes == 0:
                result["zero_packets"] += 1
                position += 4
                continue
            if record_bytes < 4:
                result["violations"].append(
                    {
                        "kind": "record_too_short",
                        "frame": frame_index,
                        "track": track,
                        "record_bytes": record_bytes,
                        "offset": position,
                    }
                )
                bounded = False
                break
            if position + 4 + record_bytes > end or position + 4 + record_bytes > payload_size:
                result["violations"].append(
                    {
                        "kind": "record_past_frame",
                        "frame": frame_index,
                        "track": track,
                        "record_bytes": record_bytes,
                        "remaining": end - position,
                        "offset": position,
                    }
                )
                bounded = False
                break
            handle.seek(payload_offset + position + 4)
            raw_decoded = handle.read(4)
            if len(raw_decoded) != 4:
                raise Kb2Error(
                    f"short decoded-count read for frame {frame_index}"
                    f" track {track} at payload offset 0x{position + 4:x}"
                )
            decoded = struct.unpack("<I", raw_decoded)[0]
            result["packets"] += 1
            result["max_packet"] = max(result["max_packet"], record_bytes)
            result["max_decoded"] = max(result["max_decoded"], decoded)
            result["decoded_values"][decoded] = result["decoded_values"].get(decoded, 0) + 1
            position += 4 + record_bytes
        if not bounded:
            break
        result["frames"] += 1
    return result


def _probe_handle(handle, payload_offset: int, payload_size: int, label: str,
                  max_table_bytes: int = DEFAULT_MAX_TABLE_BYTES,
                  validate_frames: bool = False,
                  max_frames: int = DEFAULT_MAX_FRAMES) -> dict:
    if payload_size < HEADER_SIZE:
        raise Kb2Error(
            f"payload at 0x{payload_offset:x}..0x{payload_offset + payload_size:x}"
            f" is shorter than the 48-byte header"
        )

    handle.seek(payload_offset)
    header = handle.read(HEADER_SIZE)
    if len(header) != HEADER_SIZE:
        raise Kb2Error(
            f"short header at 0x{payload_offset:x}: read {len(header)}"
            f" of {HEADER_SIZE} bytes"
        )
    signature = header[:4]
    if signature not in SUPPORTED_SIGNATURES:
        raise Kb2Error(f"signature at 0x{payload_offset:x} is {signature!r}")

    size_field = _u32(header, 0x04)
    frame_count = _u32(header, 0x08)
    if frame_count == 0:
        raise Kb2Error(f"header field at 0x{payload_offset + 0x08:x} declares zero frames")
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
        raise Kb2Error(
            f"header field at 0x{payload_offset + 0x28:x} gives audio track count"
            f" {audio_count}, above the {MAX_AUDIO_TRACKS} limit"
        )
    descriptor_size = 12 * audio_count
    table_start = HEADER_SIZE + descriptor_size
    table_size = 4 * (frame_count + 1)
    if table_size > max_table_bytes:
        raise Kb2Error(
            f"frame table at 0x{payload_offset + table_start:x} would be"
            f" {table_size} bytes, above the {max_table_bytes}-byte limit"
        )
    if table_start + table_size > payload_size:
        raise Kb2Error(
            f"frame table at 0x{payload_offset + table_start:x}"
            f"..0x{payload_offset + table_start + table_size:x}"
            f" extends past the payload end 0x{payload_offset + payload_size:x}"
        )

    handle.seek(payload_offset + HEADER_SIZE)
    descriptors = handle.read(descriptor_size)
    if len(descriptors) != descriptor_size:
        raise Kb2Error(
            f"short audio descriptors at 0x{payload_offset + HEADER_SIZE:x}:"
            f" read {len(descriptors)} of {descriptor_size} bytes"
        )
    handle.seek(payload_offset + table_start)
    table = handle.read(table_size)
    if len(table) != table_size:
        raise Kb2Error(
            f"short frame table at 0x{payload_offset + table_start:x}:"
            f" read {len(table)} of {table_size} bytes"
        )

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
    last_is_file_size = offsets[-1] == payload_size
    last_is_even = offsets[-1] & 1 == 0
    first_masked_is_table_end = masked[0] == table_end
    masked_in_range = all(table_end <= value <= payload_size for value in masked)

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
            handle, payload_offset, payload_size, starts, ends, audio_count, max_frames
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
        "path": label,
        "signature": signature.decode("ascii"),
        "file_size": payload_size,
        "size_field": size_field,
        "declared_size": size_field + 8,
        "size_field_matches_file": size_field + 8 == payload_size,
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


def probe_file(path: str, max_table_bytes: int = DEFAULT_MAX_TABLE_BYTES,
               validate_frames: bool = False, max_frames: int = DEFAULT_MAX_FRAMES) -> dict:
    try:
        payload_size = os.path.getsize(path)
        with open(path, "rb") as handle:
            return _probe_handle(handle, 0, payload_size, path, max_table_bytes,
                                 validate_frames, max_frames)
    except OSError as error:
        raise Kb2Error(f"{path}: {error}") from error


def _read_manifest(path):
    rows = []
    try:
        handle = open(path, "rb")
    except OSError as error:
        raise Kb2Error(f"manifest {path}: {error}") from error
    with handle:
        for number, raw_line in enumerate(handle, 1):
            try:
                line = raw_line.decode("utf-8")
            except UnicodeDecodeError as error:
                raise Kb2Error(
                    f"manifest line {number}: invalid UTF-8: {error}"
                ) from error
            value = line.strip()
            if not value or value.startswith("#"):
                continue
            try:
                row = json.loads(value)
            except json.JSONDecodeError as error:
                raise Kb2Error(f"manifest line {number}: invalid JSON: {error}") from error
            if not isinstance(row, dict):
                raise Kb2Error(f"manifest line {number}: not a JSON object")
            if row.get("kind") != "row":
                continue
            for field in ("payload_offset", "logical_size", "row"):
                if field not in row:
                    raise Kb2Error(
                        f"manifest line {number}: missing field {field!r}"
                    )
            raw_offset = row["payload_offset"]
            try:
                offset = int(raw_offset, 16) if isinstance(raw_offset, str) else int(raw_offset)
            except (TypeError, ValueError, OverflowError) as error:
                raise Kb2Error(
                    f"manifest line {number}: payload_offset {raw_offset!r}"
                    f" is not a finite integer or hex string"
                ) from error
            raw_size = row["logical_size"]
            try:
                size = int(raw_size)
            except (TypeError, ValueError, OverflowError) as error:
                raise Kb2Error(
                    f"manifest line {number}: logical_size {raw_size!r}"
                    f" is not a finite integer"
                ) from error
            if offset < 0 or size < 0:
                raise Kb2Error(
                    f"manifest line {number}: negative payload range"
                    f" {offset}..{offset + size}"
                )
            row = dict(row)
            row["payload_offset_int"] = offset
            row["logical_size_int"] = size
            rows.append(row)
    return rows


def probe_manifest(archive_path, manifest_path, max_table_bytes=DEFAULT_MAX_TABLE_BYTES,
                   validate_frames=False, max_frames=DEFAULT_MAX_FRAMES):
    try:
        rows = _read_manifest(manifest_path)
    except OSError as error:
        raise Kb2Error(f"manifest {manifest_path}: {error}") from error
    results = []
    label_root = os.path.basename(archive_path)
    try:
        archive_size = os.path.getsize(archive_path)
    except OSError as error:
        raise Kb2Error(f"archive {archive_path}: {error}") from error
    try:
        handle = open(archive_path, "rb")
    except OSError as error:
        raise Kb2Error(f"archive {archive_path}: {error}") from error
    with handle:
        for row in rows:
            offset = row["payload_offset_int"]
            size = row["logical_size_int"]
            label = f"{label_root}:row{row['row']}"
            if offset + size > archive_size:
                raise Kb2Error(
                    f"{label}: payload range 0x{offset:x}..0x{offset + size:x}"
                    f" exceeds archive size 0x{archive_size:x}"
                )
            try:
                result = _probe_handle(handle, offset, size, label, max_table_bytes,
                                       validate_frames, max_frames)
            except Kb2Error as error:
                raise Kb2Error(f"{label}: {error}") from error
            except OSError as error:
                raise Kb2Error(f"{label}: {error}") from error
            results.append(result)
    return results


def summarize(results):
    summary = {
        "samples": len(results),
        "errors": 0,
        "signatures": {},
        "audio_counts": {},
        "flags": {},
        "alpha_rows": 0,
        "size_field_matches": 0,
        "frame_count_matches_duplicate": 0,
        "entry0_is_end_plus_one": 0,
        "masked_offsets_nondecreasing": 0,
        "last_entry_even": 0,
        "masked_offsets_in_range": 0,
        "intervals_within_largest": 0,
        "audio_rows": 0,
        "audio_tracks": 0,
        "frames": 0,
        "packets": 0,
        "zero_packets": 0,
        "max_packet": 0,
        "max_decoded": 0,
        "array1_is_max_decoded": 0,
        "array1_ge_max_packet": 0,
        "track_id_exceptions": [],
        "keyframe_entries": 0,
        "keyframe_min": None,
        "keyframe_max": None,
    }
    for result in results:
        if "error" in result:
            summary["errors"] += 1
            continue
        summary["signatures"][result["signature"]] = (
            summary["signatures"].get(result["signature"], 0) + 1
        )
        summary["audio_counts"][str(result["audio_track_count"])] = (
            summary["audio_counts"].get(str(result["audio_track_count"]), 0) + 1
        )
        summary["flags"][result["flags"]] = summary["flags"].get(result["flags"], 0) + 1
        summary["alpha_rows"] += int(result["alpha_bit"])
        summary["size_field_matches"] += int(result["size_field_matches_file"])
        summary["frame_count_matches_duplicate"] += int(
            result["frame_count_matches_duplicate"]
        )
        table = result["frame_table"]
        summary["entry0_is_end_plus_one"] += int(table["first_is_end_plus_one"])
        summary["masked_offsets_nondecreasing"] += int(table["masked_monotonic"])
        summary["last_entry_even"] += int(table["last_is_even"])
        summary["masked_offsets_in_range"] += int(table["masked_in_range"])
        summary["intervals_within_largest"] += int(table["max_interval_within_largest"])
        keyframe = result["validation"]["keyframe_entries"]
        summary["keyframe_entries"] += keyframe
        if summary["keyframe_min"] is None or keyframe < summary["keyframe_min"]:
            summary["keyframe_min"] = keyframe
        if summary["keyframe_max"] is None or keyframe > summary["keyframe_max"]:
            summary["keyframe_max"] = keyframe
        tracks = result["audio_tracks"]
        summary["audio_tracks"] += len(tracks)
        if result["audio_track_count"]:
            summary["audio_rows"] += 1
            ids = [track["track_value"] for track in tracks]
            if (len(set(ids)) != result["audio_track_count"]
                    or not all(0 <= value < result["audio_track_count"] for value in ids)):
                summary["track_id_exceptions"].append(
                    {"path": result["path"], "audio_count": result["audio_track_count"],
                     "track_ids": ids}
                )
            audio = result.get("audio_validation")
            if audio:
                summary["frames"] += audio["frames"]
                summary["packets"] += audio["packets"]
                summary["zero_packets"] += audio["zero_packets"]
                summary["max_packet"] = max(summary["max_packet"], audio["max_packet"])
                summary["max_decoded"] = max(summary["max_decoded"], audio["max_decoded"])
                summary["array1_is_max_decoded"] += int(audio["array1_is_max_decoded"])
                summary["array1_ge_max_packet"] += int(audio["array1_ge_max_packet"])
    return summary


def _print_summary(summary, stream):
    print(f"samples: {summary['samples']}; errors: {summary['errors']}", file=stream)
    print(f"signatures: {summary['signatures']}", file=stream)
    print(f"audio counts: {summary['audio_counts']}", file=stream)
    print(f"flags: {summary['flags']}", file=stream)
    print(
        f"size field matches: {summary['size_field_matches']};"
        f" frame count matches: {summary['frame_count_matches_duplicate']};"
        f" alpha rows: {summary['alpha_rows']}",
        file=stream,
    )
    print(
        f"entry0: {summary['entry0_is_end_plus_one']};"
        f" masked monotonic: {summary['masked_offsets_nondecreasing']};"
        f" last even: {summary['last_entry_even']};"
        f" masked in range: {summary['masked_offsets_in_range']};"
        f" intervals within largest: {summary['intervals_within_largest']}",
        file=stream,
    )
    print(
        f"audio rows: {summary['audio_rows']}; tracks: {summary['audio_tracks']};"
        f" frames: {summary['frames']}; packets: {summary['packets']};"
        f" zero packets: {summary['zero_packets']}",
        file=stream,
    )
    print(
        f"max packet: {summary['max_packet']}; max decoded: {summary['max_decoded']};"
        f" array1 is max decoded: {summary['array1_is_max_decoded']};"
        f" array1 >= max packet: {summary['array1_ge_max_packet']}",
        file=stream,
    )
    print(
        f"keyframe entries: {summary['keyframe_entries']}"
        f" (min {summary['keyframe_min']}, max {summary['keyframe_max']})",
        file=stream,
    )
    for item in summary["track_id_exceptions"]:
        print(f"track id exception: {item}", file=stream)


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
    parser.add_argument("payload", nargs="*", help="extracted KB2j or KB2n payload")
    parser.add_argument("--archive", help="archive that contains the manifest rows")
    parser.add_argument("--manifest", help="JSONL row manifest with payload offsets")
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
        "--summary",
        action="store_true",
        help="aggregate the inputs instead of printing each report",
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

    inputs = list(args.payload)
    if args.archive:
        inputs.append(args.archive)
    if args.manifest:
        inputs.append(args.manifest)
    if args.output and _output_is_inside_input(args.output, inputs):
        parser.error("refusing to write output inside an input directory")

    results = []
    failed = False
    if args.manifest:
        if not args.archive:
            parser.error("--manifest requires --archive")
        try:
            results = probe_manifest(args.archive, args.manifest,
                                     args.max_table_bytes, args.validate,
                                     args.max_frames)
        except (Kb2Error, OSError) as error:
            print(f"error: {error}", file=sys.stderr)
            return 1
        for result in results:
            if "error" in result:
                failed = True
            elif args.strict and not _valid(result):
                failed = True
    else:
        if not args.payload:
            parser.error("no payload")
        for path in args.payload:
            try:
                result = probe_file(path, args.max_table_bytes, args.validate,
                                    args.max_frames)
            except (Kb2Error, OSError) as error:
                print(f"{path}: {error}", file=sys.stderr)
                failed = True
                continue
            results.append(result)
            if args.strict and not _valid(result):
                failed = True

    if args.summary:
        summary = summarize(results)
        text = (json.dumps(summary, indent=2) + "\n") if args.json else None
        if text is None:
            buffer = io.StringIO()
            _print_summary(summary, buffer)
            text = buffer.getvalue()
    elif args.json:
        output = results[0] if len(results) == 1 else results
        text = json.dumps(output, indent=2) + "\n"
    else:
        buffer = io.StringIO()
        for index, result in enumerate(results):
            if index:
                buffer.write("\n")
            if "error" in result:
                buffer.write(f"{result['path']}: {result['error']}\n")
            else:
                _print_text(result, buffer)
        text = buffer.getvalue()

    if args.output:
        _write_atomic(args.output, text)
    else:
        sys.stdout.write(text)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
