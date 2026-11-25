#!/usr/bin/env python3
"""Report the EDUP table, its key relationship and an optional store membership test.

EDUP is a length-framed table of 16-byte entries followed by a length-framed
trailing blob. The tool reads each input read-only, never prints key values and
optionally compares the two entry fields with the 64-bit key tables of local
RDS5/ETPF texture stores. It does not decode the trailing blob.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import struct
import sys

MAGIC = b"EDUP"
HEADER_SIZE = 8
ENTRY_SIZE = 16
LENGTH_SIZE = 4
DEFAULT_MAX_BYTES = 2 * 1024 * 1024 * 1024
DEFAULT_MAX_ENTRIES = 4_000_000
RDS5_HEADER_SIZE = 0x10
ETPF_HEADER_SIZE = 0x10


class EdError(ValueError):
    pass


def _le32(data: bytes, offset: int) -> int:
    if offset + 4 > len(data):
        raise EdError(f"read past end at 0x{offset:x}")
    return struct.unpack_from("<I", data, offset)[0]


def _le64(data: bytes, offset: int) -> int:
    if offset + 8 > len(data):
        raise EdError(f"read past end at 0x{offset:x}")
    return struct.unpack_from("<Q", data, offset)[0]


def _align_up(value: int, alignment: int) -> int:
    return (value + alignment - 1) & ~(alignment - 1)


def blob_bytes(data: bytes) -> bytes:
    if len(data) < HEADER_SIZE + LENGTH_SIZE or data[:4] != MAGIC:
        raise EdError("not an EDUP payload")
    count = _le32(data, 4)
    table_end = HEADER_SIZE + ENTRY_SIZE * count
    if table_end + LENGTH_SIZE > len(data):
        raise EdError("entry table overruns the payload")
    length = _le32(data, table_end)
    start = table_end + LENGTH_SIZE
    if start + length > len(data):
        raise EdError("trailing blob overruns the payload")
    return data[start:start + length]


def _multiplicity(values) -> dict:
    counts = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    distribution = {}
    for count in counts.values():
        distribution[count] = distribution.get(count, 0) + 1
    return {
        "distinct": len(counts),
        "repeated": sum(1 for count in counts.values() if count > 1),
        "max_repeat": max(counts.values()) if counts else 0,
        "repeat_distribution": dict(sorted(distribution.items())),
    }


def inspect_bytes(
    data: bytes,
    label: str = "<memory>",
    max_entries: int = DEFAULT_MAX_ENTRIES,
    store_keys: dict | None = None,
) -> dict:
    size = len(data)
    if size < HEADER_SIZE + LENGTH_SIZE:
        raise EdError(f"{label}: shorter than the EDUP header")
    if data[:4] != MAGIC:
        raise EdError(f"{label}: magic is {data[:4].hex(' ')}, not EDUP")

    count = _le32(data, 4)
    if count > max_entries:
        raise EdError(f"{label}: entry count {count} exceeds the {max_entries} cap")
    table_end = HEADER_SIZE + ENTRY_SIZE * count
    if table_end + LENGTH_SIZE > size:
        raise EdError(f"{label}: entry table overruns the payload")

    blob_length = _le32(data, table_end)
    blob_start = table_end + LENGTH_SIZE
    blob_end = blob_start + blob_length
    if blob_end > size:
        raise EdError(f"{label}: trailing blob overruns the payload")
    if blob_end != size:
        raise EdError(f"{label}: {size - blob_end} bytes follow the trailing blob")

    keys = []
    stored_keys = []
    keys_be = []
    stored_keys_be = []
    for index in range(count):
        base = HEADER_SIZE + ENTRY_SIZE * index
        keys.append(_le64(data, base))
        stored_keys.append(_le64(data, base + 8))
        keys_be.append(struct.unpack_from(">Q", data, base)[0])
        stored_keys_be.append(struct.unpack_from(">Q", data, base + 8)[0])

    key_set = set(keys)
    stored_set = set(stored_keys)
    report = {
        "label": label,
        "size": size,
        "sha256": hashlib.sha256(data).hexdigest(),
        "count": count,
        "table_end": table_end,
        "blob_length": blob_length,
        "blob_start": blob_start,
        "layout_ok": HEADER_SIZE + ENTRY_SIZE * count + LENGTH_SIZE + blob_length == size,
        "key_multiplicity": _multiplicity(keys),
        "stored_key_multiplicity": _multiplicity(stored_keys),
        "identity_entries": sum(1 for key, stored in zip(keys, stored_keys) if key == stored),
        "key_sets_disjoint": key_set.isdisjoint(stored_set),
        "keys_not_in_stored": len(key_set - stored_set),
        "stored_not_in_keys": len(stored_set - key_set),
        "store_test": None,
    }

    if store_keys is not None:
        union = set()
        for keyset in store_keys.values():
            union |= keyset
        first_hits = sum(1 for key in keys if key in union)
        stored_hits = sum(1 for key in stored_keys if key in union)
        first_hits_be = sum(1 for key in keys_be if key in union)
        stored_hits_be = sum(1 for key in stored_keys_be if key in union)
        report["store_test"] = {
            "stores": len(store_keys),
            "store_keys": sum(len(keyset) for keyset in store_keys.values()),
            "union_keys": len(union),
            "keys_in_store_union": first_hits,
            "stored_keys_in_store_union": stored_hits,
            "keys_in_store_union_be": first_hits_be,
            "stored_keys_in_store_union_be": stored_hits_be,
            "direction": (
                "stored-key field resolves, key field does not"
                if first_hits == 0 and count and stored_hits == count
                else "unresolved"
            ),
        }
    return report


def etpf_keys(path: str, max_key_bytes: int = 128 * 1024 * 1024) -> set:
    size = os.path.getsize(path)
    with open(path, "rb") as handle:
        head = handle.read(RDS5_HEADER_SIZE)
        if len(head) < RDS5_HEADER_SIZE or head[:4] != b"RDS5":
            raise EdError(f"{path}: not an RDS5 store")
        record_count = _le32(head, 4)
        if record_count < 3:
            raise EdError(f"{path}: record_count {record_count} is below 3")
        chunk = _align_up(RDS5_HEADER_SIZE + 8 * record_count, 0x100)
        if chunk + ETPF_HEADER_SIZE > size:
            raise EdError(f"{path}: ETPF offset {chunk} is past the end")
        handle.seek(chunk)
        header = handle.read(ETPF_HEADER_SIZE)
        if len(header) != ETPF_HEADER_SIZE or header[:4] != b"ETPF":
            raise EdError(f"{path}: no ETPF chunk at 0x{chunk:x}")
        descriptor_count = _le32(header, 8)
        key_offset = chunk + ETPF_HEADER_SIZE + 16 * descriptor_count
        key_bytes = 8 * descriptor_count
        if key_bytes > max_key_bytes:
            raise EdError(f"{path}: key table {key_bytes} exceeds the {max_key_bytes}-byte cap")
        if key_offset + key_bytes > size:
            raise EdError(f"{path}: key table overruns the store")
        handle.seek(key_offset)
        raw = handle.read(key_bytes)
        if len(raw) != key_bytes:
            raise EdError(f"{path}: short key table read")
    return {
        struct.unpack_from("<Q", raw, index * 8)[0]
        for index in range(descriptor_count)
    }


def load_stores(paths) -> dict:
    stores = {}
    for path in paths:
        if os.path.isdir(path):
            for root, _, files in os.walk(path):
                for name in sorted(files):
                    if name.lower().endswith(".ttpf"):
                        full = os.path.join(root, name)
                        stores[os.path.relpath(full, path)] = etpf_keys(full)
        else:
            stores[path] = etpf_keys(path)
    return stores


def _print_report(report: dict, stream) -> None:
    print(f"sample: {report['label']}", file=stream)
    print(f"size: {report['size']} bytes", file=stream)
    print(f"sha256: {report['sha256']}", file=stream)
    print(
        "layout:"
        f" count={report['count']}"
        f" table_end={report['table_end']}"
        f" blob={report['blob_length']}"
        f" ok={report['layout_ok']}",
        file=stream,
    )
    keys = report["key_multiplicity"]
    stored = report["stored_key_multiplicity"]
    print(
        "fields:"
        f" distinct_keys={keys['distinct']}"
        f" distinct_stored_keys={stored['distinct']}"
        f" repeated_stored={stored['repeated']}"
        f" max_repeat={stored['max_repeat']}"
        f" identity_entries={report['identity_entries']}"
        f" disjoint={report['key_sets_disjoint']}",
        file=stream,
    )
    test = report["store_test"]
    if test:
        print(
            "stores:"
            f" count={test['stores']}"
            f" keys={test['store_keys']}"
            f" union={test['union_keys']}"
            f" key_field_hits={test['keys_in_store_union']}"
            f" stored_field_hits={test['stored_keys_in_store_union']}"
            f" key_field_hits_be={test['keys_in_store_union_be']}"
            f" stored_field_hits_be={test['stored_keys_in_store_union_be']}"
            f" direction={test['direction']}",
            file=stream,
        )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Report the EDUP table and optional store membership.")
    parser.add_argument("samples", nargs="+", help="EDUP payload files")
    parser.add_argument("--store", action="append", default=[], help="RDS5/ETPF store file")
    parser.add_argument("--store-dir", action="append", default=[], help="directory of .ttpf stores")
    parser.add_argument("--json", action="store_true", help="print JSON instead of text")
    parser.add_argument(
        "--max-bytes", type=int, default=DEFAULT_MAX_BYTES,
        help="refuse an EDUP sample larger than this many bytes",
    )
    parser.add_argument(
        "--max-entries", type=int, default=DEFAULT_MAX_ENTRIES,
        help="refuse an entry count above this value",
    )
    args = parser.parse_args(argv)

    try:
        store_keys = load_stores(args.store + args.store_dir) if (args.store or args.store_dir) else None
        reports = []
        for path in args.samples:
            if os.path.getsize(path) > args.max_bytes:
                raise EdError(f"{path}: larger than the {args.max_bytes}-byte cap")
            with open(path, "rb") as handle:
                data = handle.read()
            reports.append(
                inspect_bytes(
                    data,
                    label=path,
                    max_entries=args.max_entries,
                    store_keys=store_keys,
                )
            )
    except (OSError, EdError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    if args.json:
        sys.stdout.write(json.dumps(reports, indent=2) + "\n")
    else:
        buffer = io.StringIO()
        for report in reports:
            _print_report(report, buffer)
            buffer.write("\n")
        sys.stdout.write(buffer.getvalue())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
