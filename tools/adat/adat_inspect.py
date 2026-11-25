#!/usr/bin/env python3
"""Inspect the ADAT header, its chunk records and the stream framing.

The tool reads each input read-only, refuses to write output inside an input
directory, and reports offsets, counts, type bytes, codec bytes and framing
statistics. It does not print payload text and assigns no codec identity.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import struct
import sys
import tempfile

MAGIC = b"ADAT"
VERSION = 1
VARIANTS = {0xFF02, 0xFF21, 0xFF25, 0xFF61}
RECORD_BYTES = 8
BLOCK_SIZE = 2048
DEFAULT_MAX_BYTES = 64 * 1024 * 1024


class AdatError(ValueError):
    pass


def _u16(data, offset, limit=None):
    boundary = len(data) if limit is None else limit
    if offset + 2 > boundary:
        raise AdatError(f"read past end at 0x{offset:x}")
    return struct.unpack_from("<H", data, offset)[0]


def _u32(data, offset, limit=None):
    boundary = len(data) if limit is None else limit
    if offset + 4 > boundary:
        raise AdatError(f"read past end at 0x{offset:x}")
    return struct.unpack_from("<I", data, offset)[0]


def _u64(data, offset):
    if offset + 8 > len(data):
        raise AdatError(f"read past end at 0x{offset:x}")
    return struct.unpack_from("<Q", data, offset)[0]


def record_start(variant: int, streams: int) -> int:
    """Return the first record offset for an observed variant."""
    if variant == 0xFF02:
        return 0x10 + 4 * streams
    if variant == 0xFF61:
        return 0x18 + 10 * streams
    return 0x14 + 10 * streams


def _record_type(value: int) -> int:
    return (value >> 56) & 0xFF


def _record_size(value: int) -> int:
    return (value >> 28) & 0xFFFFFFF


def _record_offset(value: int) -> int:
    return value & 0xFFFFFFF


def _read_records(data, variant, streams, data_offset):
    start = record_start(variant, streams)
    records = []
    position = start
    while position < data_offset:
        value = _u64(data, position)
        records.append(
            {
                "offset": position,
                "type": _record_type(value),
                "size": _record_size(value),
                "data_offset": _record_offset(value),
            }
        )
        position += RECORD_BYTES
    return records


def _descriptor_76(data, record):
    size = record["size"]
    start = record["data_offset"]
    if size < 32:
        raise AdatError(
            f"0x76 record at 0x{record['offset']:x} is {size} bytes, shorter than 32"
        )
    return {
        "kind": "0x76",
        "declared": _u32(data, start),
        "rate": _u16(data, start + 8),
        "codec": data[start + 28],
        "tail": data[start + 28:start + 32].hex(),
    }


def _descriptor_48(data, record):
    size = record["size"]
    start = record["data_offset"]
    if size < 12:
        raise AdatError(
            f"0x48 record at 0x{record['offset']:x} is {size} bytes, shorter than 12"
        )
    page_count = _u32(data, start)
    stride = _u32(data, start + 4)
    count = _u32(data, start + 8)
    expected = 12 + 16 * count
    if size != expected:
        raise AdatError(
            f"0x48 record at 0x{record['offset']:x} is {size} bytes;"
            f" {count} entries require {expected}"
        )
    if stride == 0 or stride % BLOCK_SIZE:
        raise AdatError(
            f"0x48 record at 0x{record['offset']:x} has page stride {stride},"
            f" not a nonzero multiple of {BLOCK_SIZE}"
        )
    entries = []
    for index in range(count):
        base = start + 12 + 16 * index
        unknown, decoded, rate_flags, codec, flags = struct.unpack_from(
            "<IIIHH", data, base
        )
        entries.append(
            {
                "unknown": unknown,
                "decoded": decoded,
                "rate": rate_flags >> 16,
                "rate_flags": rate_flags & 0xFFFF,
                "codec": codec & 0xFF,
                "codec_word": codec,
                "flags": flags,
            }
        )
    return {
        "kind": "0x48",
        "page_count": page_count,
        "page_stride": stride,
        "entry_count": count,
        "size": size,
        "codec": entries[0]["codec"] if entries else 0,
        "rate": entries[0]["rate"] if entries else None,
        "declared": entries[0]["decoded"] if entries else None,
        "entries": entries,
    }


def _block_class(block):
    if not any(block):
        return "zero"
    if _u32(block, 0) == 0xFFFFFFFF:
        return "sentinel"
    position = 0
    while position + 2 <= BLOCK_SIZE:
        length = _u16(block, position)
        if length == 0:
            return "data" if not any(block[position:]) else "bad_padding"
        if position + 2 + length > BLOCK_SIZE:
            return "other"
        position += 2 + length
    return "data" if position == BLOCK_SIZE else "bad_padding"


def _new_stream_stats(descriptor):
    return {
        "codec": f"0x{descriptor['codec']:02x}",
        "rate": descriptor.get("rate"),
        "declared": descriptor.get("declared"),
        "blocks": 0,
        "data_blocks": 0,
        "metadata_blocks": 0,
        "zero_blocks": 0,
        "packets": 0,
        "payload_bytes": 0,
        "padding_bytes": 0,
        "terminated_blocks": 0,
        "full_blocks": 0,
        "length_min": None,
        "length_max": None,
        "lengths": {},
        "toc": {},
        "violations": [],
    }


def _walk_data_block(block, stats, block_index):
    position = 0
    terminated = False
    while position + 2 <= BLOCK_SIZE:
        length = _u16(block, position)
        if length == 0:
            terminated = True
            position += 2
            break
        if position + 2 + length > BLOCK_SIZE:
            stats["violations"].append(
                {
                    "kind": "length_overruns_block",
                    "block": block_index,
                    "offset_in_block": position,
                    "length": length,
                }
            )
            return False
        stats["packets"] += 1
        stats["payload_bytes"] += length
        stats["lengths"][length] = stats["lengths"].get(length, 0) + 1
        if stats["length_min"] is None or length < stats["length_min"]:
            stats["length_min"] = length
        if stats["length_max"] is None or length > stats["length_max"]:
            stats["length_max"] = length
        stats["toc"][block[position + 2]] = stats["toc"].get(block[position + 2], 0) + 1
        position += 2 + length
    if position < BLOCK_SIZE:
        padding = block[position:]
        if any(padding):
            stats["violations"].append(
                {
                    "kind": "nonzero_padding",
                    "block": block_index,
                    "offset_in_block": position,
                    "pad_bytes": len(padding),
                }
            )
        stats["padding_bytes"] += len(padding)
    if terminated:
        stats["terminated_blocks"] += 1
    else:
        stats["full_blocks"] += 1
    return True


def _inspect_ff25_stream(data, chunk, size, descriptor, stats, report):
    stride = descriptor["page_stride"] // BLOCK_SIZE
    page_count = descriptor["page_count"]
    entries = descriptor["entries"]
    stats["codec"] = f"0x{entries[0]['codec']:02x}" if entries else "unknown"
    stats["rate"] = entries[0]["rate"] if entries else None
    stats["declared"] = entries[0]["decoded"] if entries else None
    stats["page_count"] = page_count
    stats["page_stride"] = stride
    stats["entry_count"] = len(entries)

    block_total = size // BLOCK_SIZE
    position = 0
    pages = 0
    while position < block_total:
        end = min(position + stride, block_total)
        classes = [
            _block_class(chunk[index * BLOCK_SIZE:(index + 1) * BLOCK_SIZE])
            for index in range(position, end)
        ]
        cursor = 0
        if cursor < len(classes) and classes[cursor] == "sentinel":
            cursor += 1
        metadata = 0
        while cursor < len(classes) and classes[cursor] in ("other", "sentinel"):
            metadata += 1
            cursor += 1
        data_start = cursor
        while cursor < len(classes) and classes[cursor] == "data":
            _walk_data_block(
                chunk[(position + cursor) * BLOCK_SIZE:(position + cursor + 1) * BLOCK_SIZE],
                stats,
                position + cursor,
            )
            cursor += 1
        data_end = cursor
        while cursor < len(classes) and classes[cursor] == "zero":
            cursor += 1
        if cursor != len(classes):
            stats["violations"].append(
                {
                    "kind": "unexplained_page_tail",
                    "page": pages,
                    "block": position,
                    "classes": classes[cursor:],
                }
            )
        stats["data_blocks"] += data_end - data_start
        stats["metadata_blocks"] += data_start
        stats["zero_blocks"] += len(classes) - data_end
        stats["pages"] = pages + 1
        position = end
        pages += 1
    if pages != page_count:
        stats["violations"].append(
            {
                "kind": "page_count_mismatch",
                "declared": page_count,
                "observed": pages,
            }
        )


def _inspect_plain_stream(data, chunk, size, descriptor, stats):
    block_total = size // BLOCK_SIZE
    for index in range(block_total):
        block = chunk[index * BLOCK_SIZE:(index + 1) * BLOCK_SIZE]
        kind = _block_class(block)
        if kind in ("data", "other", "bad_padding"):
            _walk_data_block(block, stats, index)
            stats["data_blocks"] += 1
        else:
            stats["metadata_blocks" if kind != "zero" else "zero_blocks"] += 1
            stats["violations"].append(
                {"kind": "unexpected_block_class", "block": index, "class": kind}
            )


def inspect_framing(data: bytes, label: str = "<memory>") -> dict:
    """Walk 0x55 stream records and classify their framing."""
    if len(data) < 0x10 or data[0:4] != MAGIC:
        raise AdatError(f"{label}: not an ADAT payload")
    flags = _u32(data, 0x04)
    variant = flags >> 16
    streams = _u32(data, 0x08)
    data_offset = _u32(data, 0x0C)
    records = _read_records(data, variant, streams, data_offset)

    descriptors = []
    chunk_records = []
    if variant == 0xFF25:
        for record in records:
            if record["type"] == 0x48:
                descriptors.append(_descriptor_48(data, record))
            elif record["type"] == 0x55:
                chunk_records.append(record)
    else:
        for record in records:
            if record["type"] == 0x76:
                descriptors.append(_descriptor_76(data, record))
            elif record["type"] == 0x55:
                chunk_records.append(record)

    report = {
        "variant": f"0x{variant:04x}",
        "streams": [],
        "codec_counts": {},
        "exceptions": [],
        "totals": {
            "streams": 0,
            "blocks": 0,
            "data_blocks": 0,
            "metadata_blocks": 0,
            "zero_blocks": 0,
            "packets": 0,
            "payload_bytes": 0,
            "padding_bytes": 0,
            "violations": 0,
        },
    }

    if variant == 0xFF25:
        pairs = [(descriptors, chunk_records[0])] if descriptors and chunk_records else []
        if len(chunk_records) != 1:
            report["exceptions"].append(
                {"kind": "0x55_record_count", "count": len(chunk_records)}
            )
    else:
        pairs = [([descriptor], chunk) for descriptor, chunk in zip(descriptors, chunk_records)]
        if len(descriptors) != len(chunk_records):
            report["exceptions"].append(
                {
                    "kind": "descriptor_chunk_count_mismatch",
                    "descriptors": len(descriptors),
                    "chunks": len(chunk_records),
                }
            )

    for descriptor_list, chunk_record in pairs:
        size = chunk_record["size"]
        if size % BLOCK_SIZE:
            report["exceptions"].append(
                {
                    "kind": "size_not_multiple_of_block",
                    "size": size,
                    "remainder": size % BLOCK_SIZE,
                    "record_offset": chunk_record["offset"],
                }
            )
        chunk = data[chunk_record["data_offset"]:chunk_record["data_offset"] + size]
        if len(chunk) != size:
            raise AdatError(
                f"{label}: 0x55 record at 0x{chunk_record['offset']:x} is truncated"
            )
        if variant == 0xFF25:
            stats = _new_stream_stats(descriptor_list[0])
            stats["records"] = len(descriptor_list)
            _inspect_ff25_stream(data, chunk, size, descriptor_list[0], stats, report)
        else:
            descriptor = descriptor_list[0]
            stats = _new_stream_stats(descriptor)
            stats["records"] = 1
            if descriptor["codec"] == 0x02:
                stats["raw_size_check"] = {
                    "size": size,
                    "declared": descriptor["declared"],
                    "four_bytes_per_sample": size == 4 * descriptor["declared"],
                }
                stats["rate"] = descriptor["rate"]
                stats["declared"] = descriptor["declared"]
            else:
                _inspect_plain_stream(data, chunk, size, descriptor, stats)
        stats["size"] = size
        stats["blocks"] = size // BLOCK_SIZE
        codec_key = stats["codec"]
        report["codec_counts"][codec_key] = report["codec_counts"].get(codec_key, 0) + 1
        report["streams"].append(stats)
        totals = report["totals"]
        totals["streams"] += 1
        totals["blocks"] += stats["blocks"]
        totals["data_blocks"] += stats["data_blocks"]
        totals["metadata_blocks"] += stats["metadata_blocks"]
        totals["zero_blocks"] += stats["zero_blocks"]
        totals["packets"] += stats["packets"]
        totals["payload_bytes"] += stats["payload_bytes"]
        totals["padding_bytes"] += stats["padding_bytes"]
        totals["violations"] += len(stats["violations"])
        if stats["violations"]:
            for violation in stats["violations"][:3]:
                entry = dict(violation)
                entry["record_offset"] = chunk_record["offset"]
                report["exceptions"].append(entry)

    return report


def inspect_bytes(data: bytes, label: str = "<memory>", framing: bool = False) -> dict:
    size = len(data)
    if size < 0x10:
        raise AdatError(f"{label}: shorter than the ADAT header")
    if data[0:4] != MAGIC:
        raise AdatError(f"{label}: magic is {data[0:4].hex(' ')}, not ADAT")

    flags = _u32(data, 0x04)
    version = flags & 0xFFFF
    variant = flags >> 16
    if version != VERSION:
        raise AdatError(f"{label}: version is {version}, not {VERSION}")
    if variant not in VARIANTS:
        raise AdatError(f"{label}: variant 0x{variant:04x} is not in the observed set")
    streams = _u32(data, 0x08)
    data_offset = _u32(data, 0x0C)
    if streams == 0:
        raise AdatError(f"{label}: stream count is zero")
    if data_offset > size:
        raise AdatError(f"{label}: data offset {data_offset} is past the payload end")
    if data_offset < 0x10:
        raise AdatError(f"{label}: data offset {data_offset} overlaps the header")

    per_stream_start = 0x14 if variant == 0xFF61 else 0x10
    if per_stream_start + 2 * streams > data_offset:
        raise AdatError(f"{label}: the per-stream table crosses the data offset")

    start = record_start(variant, streams)
    if start > data_offset:
        raise AdatError(f"{label}: the record run starts past the data offset")
    remainder = (data_offset - start) % RECORD_BYTES
    if remainder:
        raise AdatError(
            f"{label}: record run length {data_offset - start} leaves a"
            f" {remainder}-byte remainder"
        )

    if start == data_offset:
        raise AdatError(f"{label}: record run is empty")

    records = []
    position = start
    while position < data_offset:
        value = _u64(data, position)
        record_type = _record_type(value)
        record_size = _record_size(value)
        record_offset = _record_offset(value)
        if record_size == 0:
            raise AdatError(f"{label}: record at 0x{position:x} has size zero")
        if record_offset < data_offset:
            raise AdatError(
                f"{label}: record at 0x{position:x} points before the data offset"
            )
        if record_offset + record_size > size:
            raise AdatError(
                f"{label}: record at 0x{position:x} overruns the payload"
                f" (0x{record_offset:x} + {record_size} > {size})"
            )
        records.append(
            {
                "offset": position,
                "type": record_type,
                "size": record_size,
                "data_offset": record_offset,
            }
        )
        position += RECORD_BYTES

    type_counts = {}
    for record in records:
        key = f"0x{record['type']:02x}"
        type_counts[key] = type_counts.get(key, 0) + 1

    report = {
        "label": label,
        "size": size,
        "sha256": hashlib.sha256(data).hexdigest(),
        "header": {
            "magic": "ADAT",
            "flags": f"0x{flags:08x}",
            "version": version,
            "variant": f"0x{variant:04x}",
            "streams": streams,
            "data_offset": data_offset,
        },
        "layout": {
            "per_stream_start": per_stream_start,
            "record_start": start,
            "record_count": len(records),
            "record_bytes": len(records) * RECORD_BYTES,
            "remainder": remainder,
        },
        "records": {
            "types": type_counts,
            "first_type": f"0x{records[0]['type']:02x}" if records else None,
            "last_type": f"0x{records[-1]['type']:02x}" if records else None,
            "min_size": min((record["size"] for record in records), default=None),
            "max_size": max((record["size"] for record in records), default=None),
        },
        "checks": {
            "flags_packing": flags == ((variant << 16) | VERSION),
            "record_run_ends_at_data_offset": start + len(records) * RECORD_BYTES == data_offset,
            "nonzero_sizes": all(record["size"] for record in records),
            "extents_within_payload": all(
                record["data_offset"] + record["size"] <= size for record in records
            ),
            "last_record_type_matches_prefix_byte": bool(records)
            and records[-1]["type"] == data[data_offset - 1],
        },
    }

    if variant == 0xFF02:
        chunk_values = [_u32(data, 0x10 + 4 * index) for index in range(streams)]
        chunk_counts = [value >> 29 for value in chunk_values]
        expected = 0x10 + 4 * streams + 8 * sum(chunk_counts)
        if expected != data_offset:
            raise AdatError(
                f"{label}: FF02 data offset is {data_offset}, the chunk formula gives {expected}"
            )
        report["ff02"] = {
            "chunk_counts": chunk_counts,
            "chunk_sum": sum(chunk_counts),
            "expected_data_offset": expected,
            "formula_matches": expected == data_offset,
            "uniform_chunk_count": len(set(chunk_counts)) == 1,
        }
    elif variant == 0xFF61:
        report["ff61"] = {"second_offset": _u32(data, 0x10)}

    if framing:
        report["framing"] = inspect_framing(data, label)
    return report


def _print_framing(report, stream):
    framing = report.get("framing")
    if not framing:
        return
    totals = framing["totals"]
    print(
        f"framing: streams={totals['streams']} blocks={totals['blocks']}"
        f" data={totals['data_blocks']} metadata={totals['metadata_blocks']}"
        f" zero={totals['zero_blocks']} packets={totals['packets']}"
        f" payload_bytes={totals['payload_bytes']}"
        f" padding_bytes={totals['padding_bytes']}"
        f" violations={totals['violations']}",
        file=stream,
    )
    codecs = ", ".join(
        f"{key}={value}" for key, value in sorted(framing["codec_counts"].items())
    )
    print(f"framing codecs: {codecs}", file=stream)
    for exception in framing["exceptions"][:8]:
        print(f"framing exception: {exception}", file=stream)


def _print_text(report: dict, stream) -> None:
    header = report["header"]
    layout = report["layout"]
    records = report["records"]
    print(f"sample: {report['label']}", file=stream)
    print(f"size: {report['size']} bytes", file=stream)
    print(f"sha256: {report['sha256']}", file=stream)
    print(
        f"header: flags={header['flags']} version={header['version']}"
        f" variant={header['variant']} streams={header['streams']}"
        f" data_offset={header['data_offset']}",
        file=stream,
    )
    print(
        f"records: start=0x{layout['record_start']:x}"
        f" count={layout['record_count']} bytes={layout['record_bytes']}"
        f" remainder={layout['remainder']}"
        f" first_type={records['first_type']} last_type={records['last_type']}"
        f" types={records['types']}",
        file=stream,
    )
    if "ff02" in report:
        section = report["ff02"]
        print(
            f"ff02: chunk_sum={section['chunk_sum']}"
            f" expected_data_offset={section['expected_data_offset']}"
            f" formula_matches={section['formula_matches']}"
            f" uniform_chunk_count={section['uniform_chunk_count']}",
            file=stream,
        )
    if "ff61" in report:
        print(f"ff61: second_offset={report['ff61']['second_offset']}", file=stream)
    _print_framing(report, stream)


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


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Inspect an ADAT header, chunk records and stream framing."
    )
    parser.add_argument("samples", nargs="+", help="stored ADAT payload files")
    parser.add_argument("--json", action="store_true", help="print JSON instead of text")
    parser.add_argument("--framing", action="store_true",
                        help="walk the 0x55 stream records in 2048-byte blocks")
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
                raise AdatError(f"{label}: larger than the {args.max_bytes}-byte cap")
            with open(path, "rb") as handle:
                data = handle.read()
            reports.append(inspect_bytes(data, label=label, framing=args.framing))
    except (OSError, AdatError) as error:
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
        _write_atomic(args.output, text)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
