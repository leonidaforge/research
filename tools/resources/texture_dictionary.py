#!/usr/bin/env python3
"""Bounded reader for texture dictionaries stored as RAGE resources.

A texture dictionary is a system segment whose header holds two parallel
arrays: a sorted array of 32-bit name hashes and an array of pointers to
0x70-byte texture records. Each record holds candidate dimensions, a raw format
id, a mip count, an allocation unit count, and a graphics pointer. The
allocation size reported here is the extent to the next distinct allocation, an
upper bound; the byte scale of the unit count is not established.

Positions and arithmetic are observed from payload data. Field meanings are
**Probable** unless a finding states otherwise. This module reads only and does
not decode pixels; it reports allocation extents and bounds, not image data.

See formats/resources/textures.md for the layout and the limits of the model.
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from dataclasses import dataclass, field

SYSTEM_BASE = 0x5000_0000
GRAPHICS_BASE = 0x6000_0000
OFFSET_MASK = 0x0FFF_FFFF
ROOT_LEN = 0x60
RECORD_LEN = 0x70
MAX_RECORDS = 1 << 16
RECORD_NAME_TEXT = 0x08
MIP_COUNT_MASK = 0x7FFF


class TextureDictionaryError(Exception):
    """The buffer cannot be a texture dictionary at all."""


def decode_pointer(value: int):
    """Decode a 4-bit segment selector and 28-bit offset, or return None."""
    if value >> 32:
        return None
    kind = value >> 28
    if kind == 5:
        return ("system", value & OFFSET_MASK)
    if kind == 6:
        return ("graphics", value & OFFSET_MASK)
    return None


@dataclass(frozen=True)
class Issue:
    code: str
    detail: str


@dataclass
class Record:
    index: int
    name_hash: int
    width: int
    height: int
    format_id: int
    mip_levels: int
    mip_flag: int
    field_3c: int
    field_3e: int
    field_40: int
    allocation_units: int
    allocation_offset: int | None
    allocation_size: int | None
    allocation_extent: int | None
    size_basis: str
    name_pointer: int | None
    record_offset: int | None = None
    value_pointer: int | None = None
    field_00: int = 0
    field_0c: int = 0
    field_10: int = 0
    field_20: int = 0
    field_28: int = 0
    field_44: int = 0
    field_46: int = 0
    field_48: int = 0
    field_50: int = 0
    field_58: int = 0
    field_60: int = 0
    field_68: int = 0

    def as_dict(self):
        return {
            "index": self.index,
            "name_hash": f"0x{self.name_hash:08X}",
            "width": self.width,
            "height": self.height,
            "format_id": self.format_id,
            "mip_levels": self.mip_levels,
            "mip_flag": self.mip_flag,
            "field_3c": self.field_3c,
            "field_3e": self.field_3e,
            "field_40": self.field_40,
            "allocation_units": self.allocation_units,
            "allocation_offset": self.allocation_offset,
            "allocation_size": self.allocation_size,
            "allocation_extent": self.allocation_extent,
            "size_basis": self.size_basis,
            "record_offset": self.record_offset,
            "value_pointer": None
            if self.value_pointer is None
            else f"0x{self.value_pointer:016X}",
            "field_00": self.field_00,
            "field_0c": self.field_0c,
            "field_10": self.field_10,
            "field_20": self.field_20,
            "field_28": self.field_28,
            "field_44": self.field_44,
            "field_46": self.field_46,
            "field_48": self.field_48,
            "field_50": self.field_50,
            "field_58": self.field_58,
            "field_60": self.field_60,
            "field_68": self.field_68,
        }


@dataclass
class Dictionary:
    hash_count: int
    hash_capacity: int
    value_count: int
    value_capacity: int
    record_count: int
    graphics_size: int
    records: list = field(default_factory=list)
    issues: list = field(default_factory=list)
    system_length: int = 0
    page_map_offset: int = 0
    system_pages: int = 0
    graphics_pages: int = 0
    field_18: int = 0
    field_48: int = 0
    field_50: int = 0
    field_58: int = 0
    record_table_dense: bool = True
    record_gaps: list = field(default_factory=list)
    value_order_matches_index: bool = True

    def add(self, code, detail):
        self.issues.append(Issue(code, detail))

    @property
    def allocated_total(self):
        return sum(r.allocation_size for r in self.records if r.allocation_size is not None)

    @property
    def starts_at_zero(self):
        if self.record_count == 0:
            return self.graphics_size == 0
        offsets = [record.allocation_offset for record in self.records]
        if any(offset is None for offset in offsets):
            return False
        return min(offsets) == 0

    @property
    def allocations_in_bounds(self):
        if not self.records:
            return self.graphics_size == 0
        return all(
            record.allocation_offset is not None
            and record.allocation_size is not None
            and 0 <= record.allocation_offset < self.graphics_size
            and record.allocation_offset + record.allocation_size <= self.graphics_size
            for record in self.records
        )

    @property
    def allocation_sum_ok(self):
        return self.allocated_total <= self.graphics_size

    @property
    def partition_ok(self):
        if self.record_count == 0:
            return self.graphics_size == 0
        offsets = [record.allocation_offset for record in self.records]
        if any(offset is None for offset in offsets):
            return False
        if len(set(offsets)) != len(offsets):
            return False
        return min(offsets) == 0 and self.allocated_total == self.graphics_size

    @property
    def status(self):
        return "complete" if not self.issues else "issues"

    def report(self):
        return {
            "status": self.status,
            "hash_count": self.hash_count,
            "hash_capacity": self.hash_capacity,
            "value_count": self.value_count,
            "value_capacity": self.value_capacity,
            "record_count": self.record_count,
            "system_length": self.system_length,
            "page_map_offset": self.page_map_offset,
            "system_pages": self.system_pages,
            "graphics_pages": self.graphics_pages,
            "root_fields": {
                "field_18": self.field_18,
                "field_48": self.field_48,
                "field_50": self.field_50,
                "field_58": self.field_58,
            },
            "graphics_size": self.graphics_size,
            "allocated_total": self.allocated_total,
            "allocations_in_bounds": self.allocations_in_bounds,
            "starts_at_zero": self.starts_at_zero,
            "allocation_sum_ok": self.allocation_sum_ok,
            "partition_ok": self.partition_ok,
            "record_table_dense": self.record_table_dense,
            "record_gaps": self.record_gaps,
            "value_order_matches_index": self.value_order_matches_index,
            "records": [record.as_dict() for record in self.records],
            "issues": [{"code": issue.code, "detail": issue.detail} for issue in self.issues],
        }


def _u16(data, at):
    return struct.unpack_from("<H", data, at)[0]


def _u32(data, at):
    return struct.unpack_from("<I", data, at)[0]


def _u64(data, at):
    return struct.unpack_from("<Q", data, at)[0]


def _require_array(kind, offset, count, item_len, limit):
    if offset < 0 or count < 0:
        raise TextureDictionaryError(f"the {kind} array has a negative position")
    if offset + count * item_len > limit:
        raise TextureDictionaryError(
            f"the {kind} array at {offset:#x} with {count} entries leaves the "
            f"{limit:#x}-byte buffer"
        )


def _fill_root(dictionary, system, page_map):
    offset = page_map[1]
    if offset + 10 > len(system):
        raise TextureDictionaryError(
            f"the page map at {offset:#x} leaves the {len(system)}-byte system segment"
        )
    dictionary.system_length = len(system)
    dictionary.page_map_offset = offset
    dictionary.system_pages = system[offset + 8]
    dictionary.graphics_pages = system[offset + 9]
    dictionary.field_18 = _u64(system, 0x18)
    dictionary.field_48 = _u64(system, 0x48)
    dictionary.field_50 = _u64(system, 0x50)
    dictionary.field_58 = _u64(system, 0x58)


def parse_dictionary(system: bytes, graphics_length: int, max_records: int = MAX_RECORDS):
    """Parse a system segment that holds a texture dictionary.

    Raises ``TextureDictionaryError`` for a buffer that cannot be a dictionary:
    a short root, a nonzero first qword, a missing page-map pointer, a record
    count above ``max_records``, or an array that leaves the buffer. Per-record
    problems are issues on the returned object.
    """
    if len(system) < ROOT_LEN:
        raise TextureDictionaryError(f"the system segment has {len(system)} bytes, need {ROOT_LEN}")
    if graphics_length < 0:
        raise TextureDictionaryError("the graphics length is negative")
    if _u64(system, 0) != 0:
        raise TextureDictionaryError("the first qword is not zero")
    page_map = decode_pointer(_u64(system, 8))
    if page_map is None or page_map[0] != "system":
        raise TextureDictionaryError("the qword at +8 is not a system pointer")

    hash_pointer = decode_pointer(_u64(system, 0x20))
    value_pointer = decode_pointer(_u64(system, 0x30))
    hash_count, hash_capacity = _u16(system, 0x28), _u16(system, 0x2A)
    value_count, value_capacity = _u16(system, 0x38), _u16(system, 0x3A)

    if hash_pointer is None and value_pointer is None:
        if hash_count == 0 and value_count == 0:
            empty = Dictionary(0, 0, 0, 0, 0, graphics_length)
            _fill_root(empty, system, page_map)
            return empty
        raise TextureDictionaryError("the hash and value arrays are absent but the counts are not zero")
    if hash_pointer is None or hash_pointer[0] != "system":
        raise TextureDictionaryError("the hash-array pointer is not a system pointer")
    if value_pointer is None or value_pointer[0] != "system":
        raise TextureDictionaryError("the value-array pointer is not a system pointer")
    if hash_count > max_records or value_count > max_records:
        raise TextureDictionaryError(
            f"a count exceeds the {max_records}-record cap "
            f"(hash {hash_count}, value {value_count})"
        )

    _require_array("hash", hash_pointer[1], hash_count, 4, len(system))
    _require_array("value", value_pointer[1], value_count, 8, len(system))

    dictionary = Dictionary(
        hash_count, hash_capacity, value_count, value_capacity,
        min(hash_count, value_count), graphics_length,
    )
    _fill_root(dictionary, system, page_map)
    if hash_capacity < hash_count:
        dictionary.add(
            "capacity_short",
            f"the hash array count {hash_count} exceeds its capacity {hash_capacity}",
        )
    if value_capacity < value_count:
        dictionary.add(
            "capacity_short",
            f"the value array count {value_count} exceeds its capacity {value_capacity}",
        )
    if hash_count != value_count:
        dictionary.add(
            "count_mismatch",
            f"the hash array holds {hash_count} entries and the value array {value_count}",
        )
    count = min(hash_count, value_count)
    hashes = [_u32(system, hash_pointer[1] + 4 * i) for i in range(count)]
    if hashes != sorted(hashes):
        dictionary.add("hash_unsorted", "the name hashes are not in ascending order")
    if len(set(hashes)) != len(hashes):
        dictionary.add("hash_duplicate", "the name-hash array repeats a value")

    records = []
    for index in range(count):
        name_hash = hashes[index]
        target = decode_pointer(_u64(system, value_pointer[1] + 8 * index))
        if target is None or target[0] != "system":
            dictionary.add(
                "record_pointer",
                f"record {index} value pointer is not a system pointer",
            )
            records.append(Record(index, name_hash, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                  None, None, None, "unresolved", None))
            continue
        offset = target[1]
        if offset + RECORD_LEN > len(system):
            dictionary.add(
                "record_outside",
                f"record {index} at {offset:#x} leaves the {len(system)}-byte system segment",
            )
            records.append(Record(index, name_hash, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                  None, None, None, "unresolved", None))
            continue
        packed_38 = _u64(system, offset + 0x38)
        width = packed_38 & 0xFFFF
        height = (packed_38 >> 16) & 0xFFFF
        field_3c = (packed_38 >> 32) & 0xFFFF
        field_3e = (packed_38 >> 48) & 0xFF
        format_id = (packed_38 >> 56) & 0xFF
        packed_40 = _u64(system, offset + 0x40)
        mip_word = (packed_40 >> 16) & 0xFFFF
        allocation_units = _u32(system, offset + 0x08)
        allocation_target = decode_pointer(_u64(system, offset + 0x18))
        allocation_offset = (
            allocation_target[1]
            if allocation_target is not None and allocation_target[0] == "graphics"
            else None
        )
        name_target = decode_pointer(_u64(system, offset + 0x30))
        name_pointer = name_target[1] if name_target and name_target[0] == "system" else None
        records.append(
            Record(
                index=index,
                name_hash=name_hash,
                width=width,
                height=height,
                format_id=format_id,
                mip_levels=mip_word & MIP_COUNT_MASK,
                mip_flag=mip_word & ~MIP_COUNT_MASK,
                field_3c=field_3c,
                field_3e=field_3e,
                field_40=packed_40 & 0xFFFF,
                allocation_units=allocation_units,
                allocation_offset=allocation_offset,
                allocation_size=None,
                allocation_extent=None,
                size_basis="extent_upper_bound",
                name_pointer=name_pointer,
                record_offset=offset,
                value_pointer=_u64(system, value_pointer[1] + 8 * index),
                field_00=_u64(system, offset + 0x00),
                field_0c=_u32(system, offset + 0x0C),
                field_10=_u64(system, offset + 0x10),
                field_20=_u64(system, offset + 0x20),
                field_28=_u64(system, offset + 0x28),
                field_44=_u16(system, offset + 0x44),
                field_46=_u16(system, offset + 0x46),
                field_48=_u64(system, offset + 0x48),
                field_50=_u64(system, offset + 0x50),
                field_58=_u64(system, offset + 0x58),
                field_60=_u64(system, offset + 0x60),
                field_68=_u64(system, offset + 0x68),
            )
        )
    dictionary.records = records

    # Record table shape and value order. The value array is expected to be a
    # permutation of the record table, so its order can differ from the index
    # order even when the table itself is contiguous.
    record_offsets = sorted(
        record.record_offset for record in records if record.record_offset is not None
    )
    if records and len(record_offsets) == len(records):
        gaps = [
            {"previous": previous, "next": following, "delta": following - previous}
            for previous, following in zip(record_offsets, record_offsets[1:])
            if following - previous != RECORD_LEN
        ]
        dictionary.record_gaps = gaps
        dictionary.record_table_dense = not gaps
        base = record_offsets[0]
        dictionary.value_order_matches_index = all(
            record.record_offset == base + index * RECORD_LEN
            for index, record in enumerate(records)
        )
    elif records:
        dictionary.record_table_dense = False
        dictionary.value_order_matches_index = False

    # Allocation extents are the gaps between distinct starts, with the last
    # extending to the graphics end. They are an upper bound; the stored unit
    # count's byte scale is not established.
    offsets = sorted({r.allocation_offset for r in records if r.allocation_offset is not None})
    extent = {}
    for position, offset in enumerate(offsets):
        end = offsets[position + 1] if position + 1 < len(offsets) else graphics_length
        extent[offset] = max(0, end - offset)
    repeated = len([r for r in records if r.allocation_offset is not None]) - len(offsets)
    if repeated:
        dictionary.add("allocation_duplicate", f"{repeated} records share an allocation start")
    for record in records:
        if record.allocation_offset is None:
            dictionary.add(
                "allocation_target",
                f"record {record.index} has no graphics allocation pointer",
            )
            continue
        record.allocation_extent = extent[record.allocation_offset]
        record.allocation_size = record.allocation_extent
        if record.allocation_offset >= graphics_length:
            dictionary.add(
                "allocation_outside",
                f"record {record.index} allocation {record.allocation_offset:#x} is outside "
                f"the {graphics_length:#x}-byte graphics segment",
            )
        if record.width == 0 or record.height == 0:
            dictionary.add(
                "dimensions_zero",
                f"record {record.index} has dimensions {record.width}x{record.height}",
            )
        if record.mip_levels == 0:
            dictionary.add("mips_zero", f"record {record.index} declares no mip level")
        else:
            maximum = max(record.width, record.height).bit_length()
            if record.mip_levels > maximum:
                dictionary.add(
                    "mips_exceeds",
                    f"record {record.index} declares {record.mip_levels} mip levels for "
                    f"{record.width}x{record.height}",
                )

    if records and not dictionary.starts_at_zero:
        dictionary.add(
            "allocation_front_gap",
            "the lowest allocation start is not zero, so the extents do not cover the "
            "start of the graphics segment",
        )
    if not dictionary.allocation_sum_ok:
        dictionary.add(
            "allocation_sum",
            f"the allocation sizes sum to {dictionary.allocated_total}, above the "
            f"{graphics_length}-byte graphics segment",
        )
    return dictionary


def joaat(data: bytes) -> int:
    """Jenkins one-at-a-time with the engine's ASCII fold (HSH-F04).

    ``A``-``Z`` fold to lower case and ``\\`` folds to ``/``. Bytes above
    ``0x7F`` are unchanged. The fold makes the function accept either spelling
    of an already-normalised resource name.
    """
    result = 0
    for byte in data:
        if 0x41 <= byte <= 0x5A:
            byte += 0x20
        elif byte == 0x5C:
            byte = 0x2F
        result = (result + byte) & 0xFFFFFFFF
        result = (result + (result << 10)) & 0xFFFFFFFF
        result ^= result >> 6
    result = (result + (result << 3)) & 0xFFFFFFFF
    result ^= result >> 11
    result = (result + (result << 15)) & 0xFFFFFFFF
    return result


def check_names(system: bytes, dictionary: Dictionary, limit: int = 64):
    """Compare each record's hash with joaat of the ASCII text it points at.

    Returns ``(checked, matched)``. The text is not returned or logged; this
    check supports recognition and stays out of the report.
    """
    checked = 0
    matched = 0
    for record in dictionary.records:
        if record.name_pointer is None:
            continue
        at = record.name_pointer + RECORD_NAME_TEXT
        if at < 0 or at >= len(system):
            continue
        raw = system[at:at + limit]
        end = raw.find(b"\x00")
        if end < 0:
            # No terminator inside the window: the text is longer than the
            # limit, so the hash cannot be checked without guessing.
            continue
        text = raw[:end]
        if not text or any(byte < 0x20 or byte >= 0x7F for byte in text):
            continue
        checked += 1
        matched += int(joaat(text) == record.name_hash)
    return checked, matched


def analyze_stored(path, offset, length, logical_size=None):
    """Reconstruct one stored row with page_reconstruct and parse it."""
    import page_reconstruct

    with open(path, "rb") as handle:
        handle.seek(offset)
        buffer = handle.read(length)
    if len(buffer) != length:
        raise TextureDictionaryError(
            f"the entry needs {length} bytes but only {len(buffer)} are present"
        )
    layout = page_reconstruct.analyze_bytes(buffer, path, logical_size=logical_size)
    if layout.status != "complete" or layout.page_map is None:
        codes = ", ".join(issue.code for issue in layout.issues) or "no page map"
        raise TextureDictionaryError(f"the stored row does not reconstruct: {codes}")
    system_size = sum(page.size for page in layout.pages if page.segment == "system")
    decoded = b"".join(chunk.data for chunk in layout.chunks)
    system, graphics = decoded[:system_size], decoded[system_size:]
    dictionary = parse_dictionary(system, len(graphics))
    return dictionary, system, len(graphics)


def print_text(report):
    print(f"status:          {report['status']}")
    print(
        f"counts:          hash {report['hash_count']}/{report['hash_capacity']}, "
        f"value {report['value_count']}/{report['value_capacity']}, "
        f"records {report['record_count']}"
    )
    print(
        f"allocations:     {report['allocated_total']} of {report['graphics_size']} bytes, "
        f"in bounds {report['allocations_in_bounds']}, sum ok {report['allocation_sum_ok']}, "
        f"starts at zero {report['starts_at_zero']}, partition {report['partition_ok']}"
    )
    print(
        f"records:         dense {report['record_table_dense']}, "
        f"gaps {len(report['record_gaps'])}, "
        f"value order matches index {report['value_order_matches_index']}"
    )
    for record in report["records"]:
        offset = "-" if record["allocation_offset"] is None else f"{record['allocation_offset']:#x}"
        size = "-" if record["allocation_size"] is None else f"{record['allocation_size']}"
        print(
            f"  {record['index']:>4} {record['name_hash']} {record['width']:>5}x"
            f"{record['height']:<5} format {record['format_id']:>3} mips "
            f"{record['mip_levels']:>2} at {offset:>10} size {size} "
            f"({record['size_basis']})"
        )
    for issue in report["issues"]:
        print(f"issue:           {issue['code']}: {issue['detail']}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--file", required=True, help="archive or file that holds the resource")
    parser.add_argument("--offset", type=lambda text: int(text, 0),
                        help="payload offset of a stored row")
    parser.add_argument("--length", type=lambda text: int(text, 0),
                        help="stored length of a stored row")
    parser.add_argument("--logical-size", type=lambda text: int(text, 0),
                        help="logical size from the RPF9 row, when known")
    parser.add_argument("--system-length", type=lambda text: int(text, 0),
                        help="system length of an already decoded resource")
    parser.add_argument("--check-names", action="store_true",
                        help="count records whose hash equals joaat of their ASCII name")
    parser.add_argument("--json", action="store_true", help="print the report as JSON")
    args = parser.parse_args(argv)

    try:
        if args.system_length is not None:
            with open(args.file, "rb") as handle:
                system = handle.read(args.system_length)
                graphics = handle.read()
            dictionary = parse_dictionary(system, len(graphics))
        else:
            if args.offset is None or args.length is None:
                parser.error("--offset and --length are required for a stored row")
            dictionary, system, _ = analyze_stored(
                args.file, args.offset, args.length, args.logical_size
            )
    except TextureDictionaryError as err:
        print(f"error: {err}", file=sys.stderr)
        return 2

    report = dictionary.report()
    if args.check_names:
        checked, matched = check_names(system, dictionary)
        report["name_check"] = {"checked": checked, "matched": matched}
    if args.json:
        json.dump(report, sys.stdout, indent=2)
        print()
    else:
        print_text(report)
    return 0 if report["status"] == "complete" else 1


if __name__ == "__main__":
    sys.exit(main())
