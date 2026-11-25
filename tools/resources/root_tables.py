#!/usr/bin/env python3
"""Bounded reader for the 0DRP root header and its block table.

The root header is the first 0x50 bytes of a decoded system segment. The
fields below are descriptive labels from observation, not recovered names.
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
BLOCK_ENTRY_LEN = 16


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
class Block:
    index: int
    identifier: int
    size: int
    target: int
    segment: str | None
    offset: int | None


@dataclass
class Root:
    page_map: int
    version: int
    qword_18: int
    variant: int
    pointers: dict
    counts: tuple
    blocks: list = field(default_factory=list)
    issues: list = field(default_factory=list)

    @property
    def block_count(self) -> int:
        return self.counts[2]


def walk_blocks(system: bytes, graphics_len: int, pointer: int, count: int):
    """Read `count` 16-byte block entries at system offset `pointer`.

    Returns (blocks, issues). The walk stops at the first entry that does not
    fit, so a corrupt count cannot read past the segment.
    """
    blocks = []
    issues = []
    if count < 0:
        return blocks, [Issue("block_count", f"negative block count {count}")]
    if pointer < 0 or pointer + count * BLOCK_ENTRY_LEN > len(system):
        return blocks, [
            Issue(
                "block_table_outside",
                f"{count} block entries at {pointer:#x} do not fit in {len(system)} system bytes",
            )
        ]
    for index in range(count):
        at = pointer + index * BLOCK_ENTRY_LEN
        identifier, size = struct.unpack_from("<II", system, at)
        target = struct.unpack_from("<Q", system, at + 8)[0]
        decoded = decode_pointer(target)
        if decoded is None:
            blocks.append(Block(index, identifier, size, target, None, None))
            issues.append(
                Issue("block_target", f"block {index} target {target:#x} is not a segment pointer")
            )
            continue
        segment, offset = decoded
        limit = len(system) if segment == "system" else graphics_len
        blocks.append(Block(index, identifier, size, target, segment, offset))
        if offset + size > limit:
            issues.append(
                Issue(
                    "block_outside",
                    f"block {index} at {segment} {offset:#x} + {size:#x} leaves the {limit:#x}-byte segment",
                )
            )
    return blocks, issues


def parse_root(system: bytes, graphics_len: int):
    """Parse the 0DRP root header and walk its block table.

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
    counts = struct.unpack_from("<4H", system, 0x48)
    root = Root(
        page_map=page_map[1],
        version=system[0x14],
        qword_18=struct.unpack_from("<Q", system, 0x18)[0],
        variant=struct.unpack_from("<Q", system, 0x20)[0],
        pointers=pointers,
        counts=counts,
    )
    block_pointer = pointers.get(0x38)
    if block_pointer is None:
        issues.append(Issue("block_table", "the block-table pointer is absent"))
        root.issues = issues
        return root, issues
    blocks, block_issues = walk_blocks(system, graphics_len, block_pointer, counts[2])
    root.blocks = blocks
    issues.extend(block_issues)
    root.issues = issues
    return root, issues
