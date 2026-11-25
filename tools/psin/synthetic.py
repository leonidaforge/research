#!/usr/bin/env python3
"""Build synthetic PSIN payloads for the classifier tests.

The builders create original synthetic data. They contain no game content.
"""

from __future__ import annotations

import argparse
import os
import struct

MAGIC = b"PSIN"
SEED = 0x3FAC7125
AA = b"\xAA" * 8
PAD70 = b"\x70" * 8


def be32(value: int) -> bytes:
    return struct.pack(">I", value)


def le32(value: int) -> bytes:
    return struct.pack("<I", value)


def align16(value: int) -> int:
    return (value + 15) & ~15


def one_at_a_time_signed(data: bytes, seed: int = SEED) -> int:
    value = seed & 0xFFFFFFFF
    for byte in data:
        if byte >= 128:
            byte -= 256
        value = (value + byte) & 0xFFFFFFFF
        value = (value + (value << 10)) & 0xFFFFFFFF
        value ^= value >> 6
    value = (value + (value << 3)) & 0xFFFFFFFF
    value ^= value >> 11
    value = (value + (value << 15)) & 0xFFFFFFFF
    return value


def section(tag: bytes, body: bytes) -> bytes:
    return tag + be32(8 + len(body)) + body


def with_checksum(prefix: bytes, sections) -> bytes:
    data = prefix + b"".join(section(tag, body) for tag, body in sections)
    data += b"CHKS" + be32(20) + b"\0" * 8 + b"zppp"
    body_offset = len(data) - 12
    zeroed = bytearray(data)
    zeroed[body_offset:body_offset + 8] = b"\0" * 8
    checksum = one_at_a_time_signed(bytes(zeroed))
    data = bytearray(data)
    data[body_offset:body_offset + 4] = be32(len(data))
    data[body_offset + 4:body_offset + 8] = be32(checksum)
    return bytes(data)


def psch_body(ids, values, prefix: bytes = b"\0" * 8) -> bytes:
    table = b"".join(struct.pack(">II", identifier, 0) for identifier in ids)
    first = 4 + 8 * len(ids) + len(prefix)
    offsets = []
    position = first
    for value in values:
        offsets.append(position)
        position += len(value)
    table = b"".join(
        struct.pack(">II", ids[i], offsets[i]) for i in range(len(ids))
    )
    return be32(len(ids)) + table + prefix + b"".join(values)


def lsch_document(lengths, sections=None) -> bytes:
    descriptors = b"".join(
        le32(0xDEAD0000 + index) + le32(length) + AA
        for index, length in enumerate(lengths)
    )
    blocks = b"".join(
        bytes([0x41 + index % 26]) * length + b"\0" * (align16(length) - length)
        for index, length in enumerate(lengths)
    )
    pre_section = descriptors + blocks + b"\0" * 8
    first_offset = 8 + len(pre_section)
    prefix = MAGIC + be32(first_offset) + pre_section
    if sections is None:
        lsch_body = (
            b"\x11" * 8 + le32(3) + le32(0)
            + AA + le32(4) + struct.pack("<HH", 0, 1) + b"\0" * 16
            + b"\0" * 16
        )
        sections = [
            (b"LSCH", lsch_body),
            (b"LENM", b""),
            (b"LSNS", be32(0)),
            (b"LGID", b""),
            (b"LRSC", b"\0" * 80),
        ]
    return with_checksum(prefix, sections)


def pmap_document(block_lengths=None, mode: int = 3, extra: int = 0, unaligned: bool = False, psch_values=None) -> bytes:
    if block_lengths is None:
        block_lengths = [17, 16]
    block_lengths = list(block_lengths)
    if unaligned:
        block_lengths[-1] += 3

    kinds = [1] + [0x100 + index for index in range(len(block_lengths) - 1)]
    pre_section = bytearray(PAD70)
    entries = []
    for index, (kind, length) in enumerate(zip(kinds, block_lengths)):
        offset = 8 + len(pre_section)
        entries.append((kind, offset, 0, length))
        if kind == 1:
            block = b"chassis\0wheel_lf\0"
            block = (block + b"\0" * length)[:length]
        else:
            block = bytes([0x40 + index % 26]) * length
        pre_section += block
        if index + 1 < len(block_lengths):
            padding = align16(length) - length
            pre_section += b"\x70" * padding
    first_offset = 8 + len(pre_section)
    pmap = (
        be32(mode) + be32(extra) + struct.pack(">H", len(entries)) + PAD70[:6]
        + b"".join(struct.pack(">IIII", *entry) for entry in entries)
    )
    psch = psch_body(
        [kind for kind in kinds if kind >= 0x100],
        psch_values if psch_values is not None else [
            b"\0" * 8 for kind in kinds if kind >= 0x100
        ],
    )
    sections = [
        (b"PMAP", pmap),
        (b"PSCH", psch),
        (b"PSIG", be32(0)),
        (b"STNS", b"\0" * 16),
    ]
    return with_checksum(MAGIC + be32(first_offset) + bytes(pre_section), sections)



def corrupted_lsch() -> bytes:
    data = bytearray(lsch_document([4, 8, 12]))
    offset = data.find(b"LSCH") + 8
    data[offset] ^= 0x01
    return bytes(data)


FIXTURES = {
    "lsch_valid": lambda: lsch_document([4, 8, 12]),
    "lsch_no_descriptors": lambda: lsch_document([]),
    "pmap_valid": pmap_document,
    "pmap_unaligned": lambda: pmap_document(unaligned=True),
    "lsch_corrupted": corrupted_lsch,
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Write synthetic PSIN fixtures.")
    parser.add_argument("directory", help="output directory for the fixtures")
    args = parser.parse_args()
    os.makedirs(args.directory, exist_ok=True)
    for name, build in sorted(FIXTURES.items()):
        path = os.path.join(args.directory, name + ".psin")
        with open(path, "wb") as handle:
            handle.write(build())
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
