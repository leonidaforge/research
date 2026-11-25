#!/usr/bin/env python3
"""Bounded reader for the 0DRP root header and the records behind `+0x38`.

The root header is the first 0x50 bytes of a decoded system segment. The
fields below are positions and observed values; their meanings are not
established. The 16-byte records behind the `+0x38` pointer are walked using
the third `u16` at `+0x48` as a record count. That use is a walk convention,
not an established field meaning.

This module reads only; it refuses a pointer or a count that would leave the
segment and reports the refusal instead of resizing it.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field

SYSTEM_BASE = 0x5000_0000
GRAPHICS_BASE = 0x6000_0000
OFFSET_MASK = 0x0FFF_FFFF
ROOT_LEN = 0x50
TAG_OFFSET = 0x10
TAG = b"0DRP"
RECORD_LEN = 16


def decode_pointer(value: int):
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
    """One 16-byte record. `word0`/`word4` are positions, not named fields."""

    index: int
    word0: int
    word4: int
    target: int
    segment: str | None
    offset: int | None


@dataclass
class Root:
    page_map: int
    byte_14: int
    qword_18: int
    word_20: int
    pointers: dict
    fields_48: tuple
    records: list = field(default_factory=list)
    issues: list = field(default_factory=list)


def walk_records(system: bytes, graphics_len: int, pointer: int, count: int):
    """Read `count` 16-byte records at system offset `pointer`.

    The `word4` value at record `+4` is used as a length in the boundary check.
    Its meaning is not established. The walk stops at the first record that
    does not fit, so a corrupt count cannot read past the segment.
    """
    records = []
    issues = []
    if count < 0:
        return records, [Issue("record_count", f"negative record count {count}")]
    if pointer < 0 or pointer + count * RECORD_LEN > len(system):
        return records, [
            Issue(
                "record_table_outside",
                f"{count} records at {pointer:#x} do not fit in {len(system)} system bytes",
            )
        ]
    for index in range(count):
        at = pointer + index * RECORD_LEN
        word0, word4 = struct.unpack_from("<II", system, at)
        target = struct.unpack_from("<Q", system, at + 8)[0]
        decoded = decode_pointer(target)
        if decoded is None:
            records.append(Record(index, word0, word4, target, None, None))
            issues.append(
                Issue("record_target", f"record {index} pointer {target:#x} is not a segment pointer")
            )
            continue
        segment, offset = decoded
        limit = len(system) if segment == "system" else graphics_len
        records.append(Record(index, word0, word4, target, segment, offset))
        if offset + word4 > limit:
            issues.append(
                Issue(
                    "record_outside",
                    f"record {index} at {segment} {offset:#x} + {word4:#x} leaves the {limit:#x}-byte segment",
                )
            )
    return records, issues


def parse_root(system: bytes, graphics_len: int):
    """Parse the 0DRP root header and walk the records behind `+0x38`.

    Returns (Root, issues) or (None, issues) when the buffer is not a 0DRP
    root. Every nonzero pointer is required to stay inside the system segment.
    """
    issues = []
    if len(system) < ROOT_LEN:
        return None, [Issue("short_root", f"only {len(system)} bytes, need {ROOT_LEN}")]
    if struct.unpack_from("<Q", system, 0)[0] != 0:
        return None, [Issue("not_0drp", "the first qword is not zero")]
    if system[TAG_OFFSET : TAG_OFFSET + 4] != TAG:
        return None, [Issue("not_0drp", "the 0DRP tag is absent")]
    page_map = decode_pointer(struct.unpack_from("<Q", system, 8)[0])
    if page_map is None or page_map[0] != "system":
        return None, [Issue("root_pointer", "the page-map pointer is not a system pointer")]
    fields = {offset: struct.unpack_from("<Q", system, offset)[0] for offset in (0x28, 0x30, 0x38, 0x40)}
    pointers = {}
    for offset, value in fields.items():
        if value == 0:
            pointers[offset] = None
            continue
        decoded = decode_pointer(value)
        if decoded is None or decoded[0] != "system":
            issues.append(Issue("root_pointer", f"the pointer at {offset:#x} is not a system pointer"))
            pointers[offset] = None
            continue
        if decoded[1] >= len(system):
            issues.append(
                Issue("root_pointer", f"the pointer at {offset:#x} leaves the {len(system)}-byte system segment")
            )
            pointers[offset] = None
            continue
        pointers[offset] = decoded[1]
    fields_48 = struct.unpack_from("<4H", system, 0x48)
    root = Root(
        page_map=page_map[1],
        byte_14=system[0x14],
        qword_18=struct.unpack_from("<Q", system, 0x18)[0],
        word_20=struct.unpack_from("<Q", system, 0x20)[0],
        pointers=pointers,
        fields_48=fields_48,
    )
    record_pointer = pointers.get(0x38)
    if record_pointer is None:
        issues.append(Issue("record_table", "the +0x38 pointer is absent"))
        root.issues = issues
        return root, issues
    records, record_issues = walk_records(system, graphics_len, record_pointer, fields_48[2])
    root.records = records
    issues.extend(record_issues)
    root.issues = issues
    return root, issues
