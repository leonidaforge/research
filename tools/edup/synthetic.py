#!/usr/bin/env python3
"""Build synthetic EDUP payloads and a minimal RDS5/ETPF store for tests.

The builders create original synthetic data. They contain no game content.
"""

from __future__ import annotations

import argparse
import os
import struct


def le32(value: int) -> bytes:
    return struct.pack("<I", value)


def le64(value: int) -> bytes:
    return struct.pack("<Q", value)


def align_up(value: int, alignment: int) -> int:
    return (value + alignment - 1) & ~(alignment - 1)


def edup_document(entries, blob: bytes) -> bytes:
    body = b"".join(le64(key) + le64(stored) for key, stored in entries)
    return b"EDUP" + le32(len(entries)) + body + le32(len(blob)) + blob


def store_document(keys) -> bytes:
    """Minimal RDS5 layout with three records and an empty ETPF descriptor table."""
    keys = sorted(keys)
    header = b"RDS5" + le32(3) + le32(0) + le32(0x16000000)
    records = b"\0" * (8 * 3)
    chunk = align_up(len(header) + len(records), 0x100)
    etpf = b"ETPF" + le32(0x27A) + le32(len(keys)) + le32(0)
    descriptors = b"\0" * (16 * len(keys))
    return header + records + b"\0" * (chunk - len(header) - len(records)) + etpf + descriptors + b"".join(le64(k) for k in keys)


FIXTURES = {
    "edup_four": lambda: edup_document(
        [(0x10, 0x100), (0x20, 0x100), (0x30, 0x200), (0x40, 0x200)],
        b"\xA5" * 32,
    ),
    "edup_empty": lambda: edup_document([], b"\x5A" * 16),
    "store_three": lambda: store_document([0x100, 0x200, 0x300]),
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Write synthetic EDUP fixtures.")
    parser.add_argument("directory", help="output directory for the fixtures")
    args = parser.parse_args()
    os.makedirs(args.directory, exist_ok=True)
    for name, build in sorted(FIXTURES.items()):
        extension = ".bin"
        with open(os.path.join(args.directory, name + extension), "wb") as handle:
            handle.write(build())
        print(os.path.join(args.directory, name + extension))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
