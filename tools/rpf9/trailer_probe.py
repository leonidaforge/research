"""Bounded RPF9 trailing-region probe.

Reads the plain header and the declared trailing region, checks the bounds that
connect `hdr[0x0C]`, the metadata end and the file size, and reports lengths,
offsets and equality classes only. Trailer bytes and digests are not printed.
"""

import argparse
import json
import os
import struct
import sys

SCHEMA = "leonida-forge.rpf9-trailer-probe/1"
MAGIC = 0x52504639
HEADER = 0x40


class BoundsError(ValueError):
    pass


def _check(offset, size, file_size, what):
    if offset < 0 or size < 0 or offset + size > file_size:
        raise BoundsError("%s lies outside the file: offset %d size %d file %d"
                          % (what, offset, size, file_size))


def _read_header(path, file_size):
    if file_size < HEADER:
        raise BoundsError("file is shorter than the 0x40-byte header")
    with open(path, "rb") as fh:
        raw = fh.read(HEADER)
    words = struct.unpack("<16I", raw)
    if words[0] != MAGIC:
        raise ValueError("not an RPF9 header")
    return {
        "metadata_end": words[1],
        "primary_end": words[2],
        "trailer_length": words[3],
        "a_records": struct.unpack_from("<H", raw, 0x1A)[0],
        "b_size": words[7],
        "columns": struct.unpack_from("<H", raw, 0x20)[0],
        "secondary_columns": struct.unpack_from("<H", raw, 0x22)[0],
        "rows": struct.unpack_from("<I", raw, 0x24)[0],
        "fingerprint": words[10],
        "cell_width": raw[0x2C],
        "flags": raw[0x2D],
        "selector": raw[0x2E],
    }


def _int(value):
    if isinstance(value, int):
        return value
    text = str(value)
    return int(text, 16) if text.lower().startswith("0x") else int(text)


def _max_stored_end(manifest):
    rows = manifest.get("rows", manifest)
    return max((_int(row["payload_offset"]) + _int(row["stored_size"]) for row in rows),
               default=0)


def probe(path, manifest=None):
    file_size = os.path.getsize(path)
    header = _read_header(path, file_size)
    length = header["trailer_length"]
    offset = file_size - length
    if length < 0 or offset < 0:
        raise BoundsError("trailing region is larger than the file")
    _check(offset, length, file_size, "trailing region")
    assertions = {
        "length_positive": length > 0,
        "offset_above_metadata": offset > header["metadata_end"],
        "offset_below_file_size": offset < file_size,
        "offset_aligned_16": offset % 16 == 0,
    }
    result = {
        "schema": SCHEMA,
        "file_size": file_size,
        "metadata_end": header["metadata_end"],
        "primary_end": header["primary_end"],
        "trailing_region": {"length": length, "offset": offset},
        "header": header,
        "assertions": assertions,
    }
    if manifest is not None:
        end = _max_stored_end(manifest)
        result["max_stored_end"] = end
        result["assertions"]["max_stored_end_at_or_below_offset"] = end <= offset
    return result, header


def _shape(header):
    return (header["a_records"], header["b_size"], header["columns"],
            header["secondary_columns"], header["cell_width"], header["flags"],
            header["selector"], header["fingerprint"])


def _trailer_bytes(path, result):
    region = result["trailing_region"]
    with open(path, "rb") as fh:
        fh.seek(region["offset"])
        return fh.read(region["length"])


def compare(paths, manifests=None):
    manifests = manifests or [None] * len(paths)
    probes = []
    blobs = []
    for path, manifest in zip(paths, manifests):
        result, header = probe(path, manifest)
        result["index"] = len(probes)
        probes.append(result)
        blobs.append(_trailer_bytes(path, result))
    groups = []
    buckets = {}
    for result, blob in zip(probes, blobs):
        key = (_shape(result["header"]), result["trailing_region"]["length"])
        buckets.setdefault(key, []).append((result, blob))
    for key, members in buckets.items():
        group = {
            "trailing_length": key[1],
            "members": [result["index"] for result, _ in members],
            "equal_first_16": len({blob[:16] for _, blob in members}) == 1,
            "equal_first_32": len({blob[:32] for _, blob in members}) == 1,
            "equal_full": len({blob for _, blob in members}) == 1,
        }
        groups.append(group)
    return {"schema": SCHEMA, "archives": probes, "groups": groups}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Probe the RPF9 trailing region.")
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--manifest", action="append", default=[],
                        help="Manifest for the archive at the same position")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    manifests = [json.load(open(path, "r", encoding="utf-8")) for path in args.manifest]
    if manifests and len(manifests) != len(args.paths):
        parser.error("--manifest must be given once per path or not at all")
    if len(args.paths) == 1 and not manifests:
        result, _ = probe(args.paths[0])
    else:
        result = compare(args.paths, manifests or None)
    text = json.dumps(result, indent=1, sort_keys=True)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
    else:
        sys.stdout.write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
