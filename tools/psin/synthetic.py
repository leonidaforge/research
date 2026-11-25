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
        sections = [
            (b"LSCH", b"\0" * 16),
            (b"LENM", b""),
            (b"LSNS", be32(0)),
            (b"LGID", b""),
            (b"LRSC", b"\0" * 80),
        ]
    return with_checksum(prefix, sections)


def pmap_document(pre_section: bytes = None, unaligned: bool = False) -> bytes:
    if pre_section is None:
        pre_section = PAD70 + b"\0" * 8 + PAD70 + be32(1) + be32(0) + be32(1) + be32(1)
    if unaligned:
        pre_section += b"\0" * 3
    first_offset = 8 + len(pre_section)
    prefix = MAGIC + be32(first_offset) + pre_section
    sections = [
        (b"PMAP", b"\0" * 16),
        (b"PSCH", b"\0" * 16),
        (b"PSIG", be32(0)),
        (b"STNS", b"\0" * 16),
    ]
    return with_checksum(prefix, sections)


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
