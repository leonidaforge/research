"""Bounded RPF9 secondary-area probe.

Reads the plain header and reports the observed `C`, `D`, `E` and `F` values,
the secondary-area size, and whether two size models fit. No payload bytes are
read.
"""

import argparse
import json
import os
import struct
import sys

SCHEMA = "leonida-forge.rpf9-secondary-probe/1"
MAGIC = 0x52504639
HEADER = 0x40


class BoundsError(ValueError):
    pass


def _read(path):
    size = os.path.getsize(path)
    if size < HEADER:
        raise BoundsError("file is shorter than the 0x40-byte header")
    with open(path, "rb") as fh:
        raw = fh.read(HEADER)
    words = struct.unpack("<16I", raw)
    if words[0] != MAGIC:
        raise ValueError("not an RPF9 header")
    header = {
        "metadata_end": words[1],
        "primary_end": words[2],
        "trailing_length": words[3],
        "columns": struct.unpack_from("<H", raw, 0x20)[0],
        "secondary_columns": struct.unpack_from("<H", raw, 0x22)[0],
        "rows": struct.unpack_from("<I", raw, 0x24)[0],
        "cell_width": raw[0x2C],
        "flags": raw[0x2D],
        "selector": raw[0x2E],
        "a_records": struct.unpack_from("<H", raw, 0x1A)[0],
        "b_size": words[7],
        "fingerprint": words[10],
    }
    return header


def align(value, unit):
    if unit <= 0:
        raise ValueError("alignment unit must be positive")
    return ((value + unit - 1) // unit) * unit


def probe(path):
    header = _read(path)
    if header["metadata_end"] < header["primary_end"]:
        raise BoundsError("metadata end lies below the primary end")
    secondary = header["metadata_end"] - header["primary_end"]
    index_bytes = header["secondary_columns"] * header["rows"] * header["cell_width"]
    index_aligned = align(index_bytes, 8)
    denominator = header["secondary_columns"] * header["rows"]
    same_width = denominator > 0 and secondary % denominator == 0
    return {
        "schema": SCHEMA,
        "header": header,
        "secondary_bytes": secondary,
        "model_index_store": {
            "fits": secondary >= index_aligned,
            "index_bytes": index_bytes,
            "index_aligned_8": index_aligned,
            "pool_bytes": secondary - index_aligned if secondary >= index_aligned else None,
        },
        "model_direct_values": {
            "same_width_for_all_secondary_columns": same_width,
            "width": secondary // denominator if same_width else None,
        },
    }


def summarize(paths):
    archives = []
    for path in paths:
        result = probe(path)
        result["index"] = len(archives)
        archives.append(result)
    d_values = {}
    fits_index = 0
    fits_direct = 0
    d_gt_one = 0
    for result in archives:
        header = result["header"]
        d_values[str(header["secondary_columns"])] = d_values.get(
            str(header["secondary_columns"]), 0) + 1
        if result["model_index_store"]["fits"]:
            fits_index += 1
        if result["model_direct_values"]["same_width_for_all_secondary_columns"]:
            fits_direct += 1
        if header["secondary_columns"] > 1:
            d_gt_one += 1
    return {
        "schema": SCHEMA,
        "archives": archives,
        "summary": {
            "archives": len(archives),
            "d_values": d_values,
            "d_above_one": d_gt_one,
            "model_index_store_fits": fits_index,
            "model_direct_same_width_fits": fits_direct,
        },
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Probe the RPF9 secondary area.")
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    result = summarize(args.paths)
    text = json.dumps(result, indent=1, sort_keys=True)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
    else:
        sys.stdout.write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
