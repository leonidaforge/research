#!/usr/bin/env python3
"""Inspect the ADAT header, chunk records, stream descriptors and framing.

The tool reads each input read-only, refuses to write output inside an input
directory, and reports offsets, counts, type bytes, codec bytes, descriptor
entries, seek tables and framing statistics. It does not print payload text and
assigns no codec identity.
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
A3_ENTRY_BYTES = 4
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


def _validate_record_extents(records, data, label, data_offset):
    for record in records:
        if record["data_offset"] < data_offset:
            raise AdatError(
                f"{label}: record at 0x{record['offset']:x} points before the data offset"
            )
        if record["data_offset"] + record["size"] > len(data):
            raise AdatError(
                f"{label}: record at 0x{record['offset']:x} overruns the payload"
            )


def _descriptor_76(data, record):
    size = record["size"]
    start = record["data_offset"]
    if size != 32:
        raise AdatError(
            f"0x76 record at 0x{record['offset']:x} is {size} bytes, not 32"
        )
    return {
        "kind": "0x76",
        "declared": _u32(data, start),
        "rate": _u16(data, start + 8),
        "rate_flags": _u16(data, start + 10),
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
        unknown, decoded, rate_flags, codec_word, flags = struct.unpack_from(
            "<IIIHH", data, base
        )
        entries.append(
            {
                "unknown": unknown,
                "decoded": decoded,
                "rate": rate_flags >> 16,
                "rate_flags": rate_flags & 0xFFFF,
                "codec": codec_word & 0xFF,
                "codec_word": codec_word,
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


def _parse_a3(data, record):
    size = record["size"]
    if size % A3_ENTRY_BYTES:
        raise AdatError(
            f"0xA3 record at 0x{record['offset']:x} has size {size},"
            f" not a multiple of {A3_ENTRY_BYTES}"
        )
    count = size // A3_ENTRY_BYTES
    values = [
        _u32(data, record["data_offset"] + A3_ENTRY_BYTES * index)
        for index in range(count)
    ]
    return {
        "entry_bytes": A3_ENTRY_BYTES,
        "count": count,
        "first": values[0] if values else None,
        "last": values[-1] if values else None,
        "first_is_zero": bool(values) and values[0] == 0,
        "nondecreasing": all(left <= right for left, right in zip(values, values[1:])),
        "size": size,
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
        "sentinel_blocks": 0,
        "metadata_blocks": 0,
        "zero_blocks": 0,
        "unknown_blocks": 0,
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


def _inspect_ff25_stream(chunk, size, descriptor, stats):
    stride = descriptor["page_stride"] // BLOCK_SIZE
    page_count = descriptor["page_count"]
    entries = descriptor["entries"]
    stats["entries"] = entries
    stats["entry_codecs"] = {}
    stats["entry_rates"] = {}
    for entry in entries:
        codec = f"0x{entry['codec']:02x}"
        rate = entry["rate"]
        stats["entry_codecs"][codec] = stats["entry_codecs"].get(codec, 0) + 1
        stats["entry_rates"][rate] = stats["entry_rates"].get(rate, 0) + 1
    if len(stats["entry_codecs"]) > 1:
        stats["violations"].append(
            {"kind": "mixed_entry_codecs", "values": sorted(stats["entry_codecs"])}
        )
    if len(stats["entry_rates"]) > 1:
        stats["violations"].append(
            {"kind": "mixed_entry_rates", "values": sorted(stats["entry_rates"])}
        )

    block_total = size // BLOCK_SIZE
    position = 0
    pages = 0
    metadata_per_page = {}
    while position < block_total:
        end = min(position + stride, block_total)
        classes = [
            _block_class(chunk[index * BLOCK_SIZE:(index + 1) * BLOCK_SIZE])
            for index in range(position, end)
        ]
        cursor = 0
        sentinel = 0
        while cursor < len(classes) and classes[cursor] == "sentinel":
            sentinel += 1
            cursor += 1
        metadata = 0
        while cursor < len(classes) and classes[cursor] == "other":
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
        zero_end = cursor
        unknown = len(classes) - zero_end
        if sentinel == 0:
            stats["violations"].append(
                {"kind": "missing_page_sentinel", "page": pages, "block": position}
            )
        if unknown:
            stats["violations"].append(
                {
                    "kind": "unexplained_page_tail",
                    "page": pages,
                    "block": position + zero_end,
                    "classes": classes[zero_end:],
                }
            )
        stats["sentinel_blocks"] += sentinel
        stats["metadata_blocks"] += metadata
        stats["data_blocks"] += data_end - data_start
        stats["zero_blocks"] += zero_end - data_end
        stats["unknown_blocks"] += unknown
        metadata_per_page[metadata] = metadata_per_page.get(metadata, 0) + 1
        position = end
        pages += 1
    stats["pages"] = pages
    stats["page_count"] = page_count
    stats["page_stride"] = stride
    stats["page_metadata_counts"] = metadata_per_page
    if pages != page_count:
        stats["violations"].append(
            {"kind": "page_count_mismatch", "declared": page_count, "observed": pages}
        )


def _inspect_plain_stream(chunk, size, stats):
    block_total = size // BLOCK_SIZE
    for index in range(block_total):
        block = chunk[index * BLOCK_SIZE:(index + 1) * BLOCK_SIZE]
        kind = _block_class(block)
        if kind in ("data", "other", "bad_padding"):
            _walk_data_block(block, stats, index)
            stats["data_blocks"] += 1
        else:
            stats["unknown_blocks"] += 1
            stats["violations"].append(
                {"kind": "unexpected_block_class", "block": index, "class": kind}
            )


def _pair_records(records, variant):
    """Return (descriptor, 0x55, 0xA3) triples in stream order."""
    if variant == 0xFF25:
        d48 = [record for record in records if record["type"] == 0x48]
        chunks = [record for record in records if record["type"] == 0x55]
        a3 = [record for record in records if record["type"] == 0xA3]
        return [
            (d48[0] if d48 else None,
             chunks[0] if chunks else None,
             a3[0] if a3 else None)
        ]
    groups = []
    start = 0
    for index, record in enumerate(records):
        if record["type"] != 0x76:
            continue
        chunk = next(
            (candidate for candidate in reversed(records[start:index])
             if candidate["type"] == 0x55),
            None,
        )
        a3 = None
        cursor = index + 1
        while cursor < len(records) and records[cursor]["type"] != 0x76:
            if records[cursor]["type"] == 0x55 and chunk is None:
                chunk = records[cursor]
            if records[cursor]["type"] == 0xA3 and a3 is None:
                a3 = records[cursor]
            cursor += 1
        if a3 is None:
            a3 = next(
                (candidate for candidate in reversed(records[start:index])
                 if candidate["type"] == 0xA3),
                None,
            )
        groups.append((record, chunk, a3))
        start = index + 1
    return groups


def _empty_totals():
    return {
        "streams": 0,
        "blocks": 0,
        "data_blocks": 0,
        "sentinel_blocks": 0,
        "metadata_blocks": 0,
        "zero_blocks": 0,
        "unknown_blocks": 0,
        "packets": 0,
        "payload_bytes": 0,
        "padding_bytes": 0,
        "violations": 0,
    }


def inspect_framing(data: bytes, label: str = "<memory>") -> dict:
    """Walk stream records, descriptors, 0xA3 tables and 0x55 framing."""
    if len(data) < 0x10 or data[0:4] != MAGIC:
        raise AdatError(f"{label}: not an ADAT payload")
    flags = _u32(data, 0x04)
    variant = flags >> 16
    streams = _u32(data, 0x08)
    data_offset = _u32(data, 0x0C)
    records = _read_records(data, variant, streams, data_offset)
    _validate_record_extents(records, data, label, data_offset)

    report = {
        "variant": f"0x{variant:04x}",
        "streams": [],
        "codec_counts": {},
        "codec_totals": {},
        "all_totals": _empty_totals(),
        "exceptions": [],
    }

    for descriptor_record, chunk_record, a3_record in _pair_records(records, variant):
        if descriptor_record is None:
            report["exceptions"].append(
                {"kind": "missing_stream_descriptor", "chunk": chunk_record is not None}
            )
            continue
        if descriptor_record["type"] == 0x48:
            descriptor = _descriptor_48(data, descriptor_record)
        else:
            descriptor = _descriptor_76(data, descriptor_record)
        if chunk_record is None:
            report["exceptions"].append(
                {"kind": "missing_stream_chunk", "descriptor": descriptor_record["type"]}
            )
            continue
        size = chunk_record["size"]
        chunk = data[chunk_record["data_offset"]:chunk_record["data_offset"] + size]
        if len(chunk) != size:
            raise AdatError(
                f"{label}: 0x55 record at 0x{chunk_record['offset']:x} is truncated"
            )
        stats = _new_stream_stats(descriptor)
        stats["variant"] = report["variant"]
        stats["label"] = label
        stats["size"] = size
        stats["blocks"] = size // BLOCK_SIZE
        stats["records"] = len(descriptor["entries"]) if "entries" in descriptor else 1
        codec = descriptor["codec"]
        mixed_entries = False
        if variant == 0xFF25 and "entries" in descriptor:
            entries = descriptor["entries"]
            entry_codecs = {}
            entry_rates = {}
            for entry in entries:
                entry_codec = f"0x{entry['codec']:02x}"
                entry_codecs[entry_codec] = entry_codecs.get(entry_codec, 0) + 1
                entry_rates[entry["rate"]] = entry_rates.get(entry["rate"], 0) + 1
            if len(entry_codecs) > 1 or len(entry_rates) > 1:
                mixed_entries = True
                stats["entries"] = entries
                stats["entry_codecs"] = entry_codecs
                stats["entry_rates"] = entry_rates
                if len(entry_codecs) > 1:
                    stats["violations"].append(
                        {"kind": "mixed_entry_codecs", "values": sorted(entry_codecs)}
                    )
                if len(entry_rates) > 1:
                    stats["violations"].append(
                        {"kind": "mixed_entry_rates", "values": sorted(entry_rates)}
                    )
        if mixed_entries:
            pass
        elif codec == 0x02:
            stats["raw_size_check"] = {
                "size": size,
                "declared": descriptor["declared"],
                "four_bytes_per_sample": size == 4 * descriptor["declared"],
            }
        elif codec == 0x0B:
            if size % BLOCK_SIZE:
                stats["violations"].append(
                    {
                        "kind": "size_not_multiple_of_block",
                        "size": size,
                        "remainder": size % BLOCK_SIZE,
                        "record_offset": chunk_record["offset"],
                    }
                )
            if variant == 0xFF25:
                _inspect_ff25_stream(chunk, size, descriptor, stats)
            else:
                _inspect_plain_stream(chunk, size, stats)
        else:
            stats["violations"].append(
                {"kind": "unclassified_codec", "codec": f"0x{codec:02x}"}
            )
        if a3_record is not None:
            stats["a3"] = _parse_a3(data, a3_record)
            if codec == 0x02:
                report["exceptions"].append(
                    {"kind": "unexpected_a3_for_codec_0x02",
                     "record_offset": chunk_record["offset"]}
                )
            elif variant == 0xFF25:
                stats["a3"]["count_matches_pages"] = (
                    stats["a3"]["count"] == stats.get("pages")
                )
            else:
                stats["a3"]["count_matches_blocks_plus_one"] = (
                    stats["a3"]["count"] == stats["blocks"] + 1
                )
        elif codec == 0x0B and not mixed_entries:
            report["exceptions"].append(
                {"kind": "missing_a3", "record_offset": chunk_record["offset"]}
            )

        codec_key = stats["codec"]
        report["codec_counts"][codec_key] = report["codec_counts"].get(codec_key, 0) + 1
        totals = report["codec_totals"].setdefault(codec_key, _empty_totals())
        totals["streams"] += 1
        totals["blocks"] += stats["blocks"]
        totals["data_blocks"] += stats["data_blocks"]
        totals["sentinel_blocks"] += stats["sentinel_blocks"]
        totals["metadata_blocks"] += stats["metadata_blocks"]
        totals["zero_blocks"] += stats["zero_blocks"]
        totals["unknown_blocks"] += stats["unknown_blocks"]
        totals["packets"] += stats["packets"]
        totals["payload_bytes"] += stats["payload_bytes"]
        totals["padding_bytes"] += stats["padding_bytes"]
        totals["violations"] += len(stats["violations"])
        report["all_totals"]["streams"] += 1
        for key in ("blocks", "data_blocks", "sentinel_blocks", "metadata_blocks",
                    "zero_blocks", "unknown_blocks", "packets", "payload_bytes",
                    "padding_bytes"):
            report["all_totals"][key] += stats[key]
        report["all_totals"]["violations"] += len(stats["violations"])
        report["streams"].append(stats)
        for violation in stats["violations"]:
            entry = dict(violation)
            entry["record_offset"] = chunk_record["offset"]
            report["exceptions"].append(entry)

    report["all_totals"]["exceptions"] = len(report["exceptions"])
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


def _summarize(reports):
    summary = {
        "samples": len(reports),
        "variants": {},
        "codec_counts": {},
        "codec_rows": {},
        "codec_variant_rows": {},
        "descriptor_counts": {},
        "codec_totals": {},
        "a3": {
            "streams": 0,
            "first_is_zero": 0,
            "nondecreasing": 0,
            "count_matches_blocks_plus_one": 0,
            "count_matches_pages": 0,
            "missing": 0,
            "unexpected": 0,
        },
        "ff25": {
            "streams": 0,
            "pages": 0,
            "sentinel_blocks": 0,
            "metadata_blocks": 0,
            "zero_blocks": 0,
            "data_blocks": 0,
            "page_metadata_counts": {},
            "entry_codecs": {},
            "entry_rates": {},
            "stride_rows": {},
        },
        "rates": {"0x76": {}, "atypical": []},
        "lengths": {},
        "length_min": None,
        "length_max": None,
        "toc": {},
        "codec02": {"records": 0, "four_bytes_per_sample": 0},
        "violations": 0,
        "exceptions": 0,
        "exception_kinds": {},
        "block_size_violations": 0,
    }
    for report in reports:
        framing = report.get("framing")
        if not framing:
            continue
        summary["variants"][framing["variant"]] = (
            summary["variants"].get(framing["variant"], 0) + 1
        )
        for key, value in framing["codec_counts"].items():
            summary["codec_counts"][key] = summary["codec_counts"].get(key, 0) + value
        codecs_in_sample = {stream["codec"] for stream in framing["streams"]}
        for codec in codecs_in_sample:
            summary["codec_rows"][codec] = summary["codec_rows"].get(codec, 0) + 1
            key = f"{framing['variant']}:{codec}"
            summary["codec_variant_rows"][key] = (
                summary["codec_variant_rows"].get(key, 0) + 1
            )
        for key, totals in framing["codec_totals"].items():
            target = summary["codec_totals"].setdefault(key, _empty_totals())
            for field, value in totals.items():
                target[field] = target.get(field, 0) + value
        summary["violations"] += framing["all_totals"]["violations"]
        summary["exceptions"] += len(framing["exceptions"])
        for exception in framing["exceptions"]:
            kind = exception.get("kind", "unknown")
            summary["exception_kinds"][kind] = summary["exception_kinds"].get(kind, 0) + 1

        for index, stream in enumerate(framing["streams"]):
            if stream["variant"] == "0xff25":
                for codec, count in stream.get("entry_codecs", {}).items():
                    summary["descriptor_counts"][codec] = (
                        summary["descriptor_counts"].get(codec, 0) + count
                    )
            else:
                summary["descriptor_counts"][stream["codec"]] = (
                    summary["descriptor_counts"].get(stream["codec"], 0) + 1
                )
            a3 = stream.get("a3")
            if a3:
                summary["a3"]["streams"] += 1
                summary["a3"]["first_is_zero"] += int(a3["first_is_zero"])
                summary["a3"]["nondecreasing"] += int(a3["nondecreasing"])
                summary["a3"]["count_matches_blocks_plus_one"] += int(
                    a3.get("count_matches_blocks_plus_one", False)
                )
                summary["a3"]["count_matches_pages"] += int(
                    a3.get("count_matches_pages", False)
                )
                if stream["codec"] == "0x02":
                    summary["a3"]["unexpected"] += 1
            elif stream["codec"] == "0x0b":
                summary["a3"]["missing"] += 1
            for length, count in stream.get("lengths", {}).items():
                summary["lengths"][str(length)] = (
                    summary["lengths"].get(str(length), 0) + count
                )
            for toc, count in stream.get("toc", {}).items():
                summary["toc"][str(toc)] = summary["toc"].get(str(toc), 0) + count
            if stream.get("length_min") is not None:
                if summary["length_min"] is None or stream["length_min"] < summary["length_min"]:
                    summary["length_min"] = stream["length_min"]
            if stream.get("length_max") is not None:
                if summary["length_max"] is None or stream["length_max"] > summary["length_max"]:
                    summary["length_max"] = stream["length_max"]
            if stream["codec"] == "0x02":
                summary["codec02"]["records"] += 1
                if stream.get("raw_size_check", {}).get("four_bytes_per_sample"):
                    summary["codec02"]["four_bytes_per_sample"] += 1
            if stream["codec"] == "0x0b" and stream["variant"] == "0xff25":
                summary["ff25"]["streams"] += 1
                summary["ff25"]["pages"] += stream.get("pages", 0)
                summary["ff25"]["sentinel_blocks"] += stream.get("sentinel_blocks", 0)
                summary["ff25"]["metadata_blocks"] += stream.get("metadata_blocks", 0)
                summary["ff25"]["zero_blocks"] += stream.get("zero_blocks", 0)
                summary["ff25"]["data_blocks"] += stream.get("data_blocks", 0)
                for count, pages in stream.get("page_metadata_counts", {}).items():
                    summary["ff25"]["page_metadata_counts"][str(count)] = (
                        summary["ff25"]["page_metadata_counts"].get(str(count), 0) + pages
                    )
                for codec, count in stream.get("entry_codecs", {}).items():
                    summary["ff25"]["entry_codecs"][codec] = (
                        summary["ff25"]["entry_codecs"].get(codec, 0) + count
                    )
                for rate, count in stream.get("entry_rates", {}).items():
                    summary["ff25"]["entry_rates"][str(rate)] = (
                        summary["ff25"]["entry_rates"].get(str(rate), 0) + count
                    )
                stride_blocks = stream.get("page_stride")
                if stride_blocks is not None:
                    summary["ff25"]["stride_rows"][str(stride_blocks)] = (
                        summary["ff25"]["stride_rows"].get(str(stride_blocks), 0) + 1
                    )
            if stream["codec"] == "0x02":
                continue
            rate = stream.get("rate")
            if rate is None:
                continue
            key = str(rate)
            if stream["variant"] == "0xff25":
                # Entry rates are already counted above; keep 0x76 only here.
                continue
            summary["rates"]["0x76"][key] = summary["rates"]["0x76"].get(key, 0) + 1
            if rate != 48000:
                summary["rates"]["atypical"].append(
                    {
                        "label": report["label"],
                        "variant": stream["variant"],
                        "stream_index": index,
                        "codec": stream["codec"],
                        "rate": rate,
                        "declared": stream.get("declared"),
                        "size": stream.get("size"),
                    }
                )
        for exception in framing["exceptions"]:
            if exception.get("kind") == "size_not_multiple_of_block":
                summary["block_size_violations"] += 1
    summary["rates"]["atypical_rows"] = len(
        {item["label"] for item in summary["rates"]["atypical"]}
    )
    return summary


def _print_summary(summary, stream):
    print(f"samples: {summary['samples']}", file=stream)
    if "selection" in summary:
        print(f"selection: {summary['selection']}", file=stream)
    print(f"variants: {summary['variants']}", file=stream)
    print(f"codec_counts: {summary['codec_counts']}", file=stream)
    print(f"codec_rows: {summary['codec_rows']}", file=stream)
    print(f"codec_variant_rows: {summary['codec_variant_rows']}", file=stream)
    print(f"descriptor_counts: {summary['descriptor_counts']}", file=stream)
    for codec, totals in sorted(summary["codec_totals"].items()):
        print(
            f"codec {codec}: streams={totals['streams']} blocks={totals['blocks']}"
            f" data={totals['data_blocks']} sentinel={totals['sentinel_blocks']}"
            f" metadata={totals['metadata_blocks']} zero={totals['zero_blocks']}"
            f" unknown={totals['unknown_blocks']} packets={totals['packets']}"
            f" payload_bytes={totals['payload_bytes']}"
            f" padding_bytes={totals['padding_bytes']}"
            f" violations={totals['violations']}",
            file=stream,
        )
    print(
        f"length range: {summary['length_min']}..{summary['length_max']};"
        f" toc: {summary['toc']};"
        f" top lengths: {sorted(summary['lengths'].items(), key=lambda item: -item[1])[:5]}",
        file=stream,
    )
    print(f"a3: {summary['a3']}", file=stream)
    print(f"ff25: {summary['ff25']}", file=stream)
    print(f"rates 0x76: {summary['rates']['0x76']}", file=stream)
    print(f"rates 0x48 entries: {summary['ff25']['entry_rates']}", file=stream)
    print(f"codec02: {summary['codec02']}", file=stream)
    print(f"violations: {summary['violations']}; exceptions: {summary['exceptions']}", file=stream)
    print(f"exception kinds: {summary['exception_kinds']}", file=stream)
    if summary["rates"]["atypical"]:
        print(
            f"atypical rate records: {len(summary['rates']['atypical'])}"
            f" in {summary['rates']['atypical_rows']} samples",
            file=stream,
        )
        for item in summary["rates"]["atypical"]:
            print(f"  {item}", file=stream)


def _print_framing(report, stream):
    framing = report.get("framing")
    if not framing:
        return
    for codec, totals in sorted(framing["codec_totals"].items()):
        print(
            f"framing {codec}: streams={totals['streams']} blocks={totals['blocks']}"
            f" data={totals['data_blocks']} sentinel={totals['sentinel_blocks']}"
            f" metadata={totals['metadata_blocks']} zero={totals['zero_blocks']}"
            f" unknown={totals['unknown_blocks']} packets={totals['packets']}"
            f" payload_bytes={totals['payload_bytes']}"
            f" padding_bytes={totals['padding_bytes']}"
            f" violations={totals['violations']}",
            file=stream,
        )
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


def _read_input_list(path):
    entries = []
    with open(path, encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            value = line.strip()
            if not value or value.startswith("#"):
                continue
            if value.startswith("{"):
                try:
                    row = json.loads(value)
                except json.JSONDecodeError as error:
                    raise AdatError(f"input list line {number}: {error}") from error
                sample_path = row.get("file") or row.get("path")
                if not sample_path:
                    raise AdatError(f"input list line {number}: no file path")
                entries.append(
                    {
                        "path": sample_path,
                        "parent_id": row.get("parent_id"),
                        "row": row.get("row"),
                        "archive_sha256": row.get("archive_sha256"),
                    }
                )
            else:
                entries.append(
                    {"path": value, "parent_id": None, "row": None,
                     "archive_sha256": None}
                )
    return entries


def _deduplicate(entries):
    raw = len(entries)
    keyed = [
        entry for entry in entries
        if entry.get("parent_id") is not None and entry.get("row") is not None
    ]
    if raw == 0:
        return entries, {
            "raw_inputs": 0, "deduped_inputs": 0, "collapsed_inputs": 0,
            "distinct_parents": 0, "distinct_archive_digests": 0,
            "missing_keys": 0,
        }
    if len(keyed) != raw:
        return entries, {
            "raw_inputs": raw, "deduped_inputs": raw, "collapsed_inputs": 0,
            "distinct_parents": None, "distinct_archive_digests": None,
            "missing_keys": raw - len(keyed),
        }
    unique = {}
    for entry in entries:
        unique.setdefault((entry["parent_id"], entry["row"]), entry)
    return list(unique.values()), {
        "raw_inputs": raw,
        "deduped_inputs": len(unique),
        "collapsed_inputs": raw - len(unique),
        "distinct_parents": len({entry["parent_id"] for entry in entries}),
        "distinct_archive_digests": len({
            entry["archive_sha256"] for entry in entries
            if entry.get("archive_sha256") is not None
        }),
        "missing_keys": 0,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Inspect ADAT headers, chunk records, descriptors and framing."
    )
    parser.add_argument("samples", nargs="*", help="stored ADAT payload files")
    parser.add_argument("--input-list", help="read sample paths from this file")
    parser.add_argument("--json", action="store_true", help="print JSON instead of text")
    parser.add_argument("--framing", action="store_true",
                        help="walk the 0x55 stream records in 2048-byte blocks")
    parser.add_argument("--summary", action="store_true",
                        help="aggregate the inputs instead of printing each report")
    parser.add_argument("--output", help="write output to this file instead of stdout")
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES,
                        help="refuse a sample larger than this many bytes")
    args = parser.parse_args(argv)

    samples = [
        {"path": path, "parent_id": None, "row": None, "archive_sha256": None}
        for path in args.samples
    ]
    if args.input_list:
        try:
            samples.extend(_read_input_list(args.input_list))
        except (OSError, AdatError) as error:
            print(f"error: {error}", file=sys.stderr)
            return 1
    if not samples:
        parser.error("no samples")
    selection = None
    if args.summary:
        samples, selection = _deduplicate(samples)
    paths = [sample["path"] for sample in samples]
    if args.output and _output_is_inside_input(args.output, paths):
        parser.error("refusing to write output inside an input directory")

    reports = []
    try:
        for sample in samples:
            path = sample["path"]
            label = os.path.basename(path)
            if os.path.getsize(path) > args.max_bytes:
                raise AdatError(f"{label}: larger than the {args.max_bytes}-byte cap")
            with open(path, "rb") as handle:
                data = handle.read()
            reports.append(
                inspect_bytes(data, label=label, framing=args.framing or args.summary)
            )
    except (OSError, AdatError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    if args.summary:
        summary = _summarize(reports)
        summary["selection"] = selection
        if args.json:
            text = json.dumps(summary, indent=2) + "\n"
        else:
            buffer = io.StringIO()
            _print_summary(summary, buffer)
            text = buffer.getvalue()
    elif args.json:
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
