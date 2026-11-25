"""Bounded RPF9 secondary-area probe.

Reads the plain header and reports the documented store start, the secondary
area size, and two necessary-condition size checks. Header sizes alone do not
choose between the index-store and direct-value models. No payload bytes are
read and no store bytes are interpreted.
"""

import argparse
import json
import os
import struct
import sys

import _output

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
    return {
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


def align(value, unit):
    if unit <= 0:
        raise ValueError("alignment unit must be positive")
    return ((value + unit - 1) // unit) * unit


def probe(path):
    header = _read(path)
    if header["metadata_end"] < header["primary_end"]:
        raise BoundsError("metadata end lies below the primary end")
    area_bytes = header["metadata_end"] - header["primary_end"]
    store_start = align(header["primary_end"], header["cell_width"])
    index_bytes = header["secondary_columns"] * header["rows"] * header["cell_width"]
    index_end = store_start + index_bytes
    pool_start = align(index_end, 8)
    index_fits = pool_start <= header["metadata_end"]
    pool_bytes = header["metadata_end"] - pool_start if index_fits else None
    direct_bytes = header["metadata_end"] - store_start
    denominator = header["secondary_columns"] * header["rows"]
    direct_same_width = denominator > 0 and direct_bytes % denominator == 0
    direct_width = direct_bytes // denominator if direct_same_width else None
    return {
        "schema": SCHEMA,
        "header": header,
        "layout": {
            "area_start": header["primary_end"],
            "area_bytes": area_bytes,
            "store_start": store_start,
            "start_padding": store_start - header["primary_end"],
            "index_bytes": index_bytes,
            "index_end": index_end,
            "pool_start": pool_start,
            "pool_bytes": pool_bytes,
            "area_end": header["metadata_end"],
        },
        "model_index_store": {
            "necessary_condition_fits": index_fits,
            "required_bytes_from_area_start": (pool_start - header["primary_end"])
            if index_fits else None,
            "pool_bytes": pool_bytes,
        },
        "model_direct_values": {
            "same_width_for_all_secondary_columns": direct_same_width,
            "width": direct_width,
            "bytes_from_store_start": direct_bytes,
        },
        "separation": {
            "models_make_different_size_predictions": index_fits != direct_same_width,
            "observation_selects": False,
            "observation_used": None,
            "reason": "a necessary size condition cannot discriminate: the direct model "
                      "also fits with a different width per column",
        },
    }


def summarize(paths):
    archives = []
    for path in paths:
        result = probe(path)
        result["index"] = len(archives)
        archives.append(result)
    d_values = {}
    index_fits = 0
    direct_same_width = 0
    d_gt_one = 0
    start_padding = 0
    predictions_differ = 0
    decided = 0
    for result in archives:
        header = result["header"]
        d_values[str(header["secondary_columns"])] = d_values.get(
            str(header["secondary_columns"]), 0) + 1
        if result["model_index_store"]["necessary_condition_fits"]:
            index_fits += 1
        if result["model_direct_values"]["same_width_for_all_secondary_columns"]:
            direct_same_width += 1
        if header["secondary_columns"] > 1:
            d_gt_one += 1
        if result["layout"]["start_padding"]:
            start_padding += 1
        if result["separation"]["models_make_different_size_predictions"]:
            predictions_differ += 1
        if result["separation"]["observation_selects"]:
            decided += 1
    return {
        "schema": SCHEMA,
        "archives": archives,
        "summary": {
            "archives": len(archives),
            "d_values": d_values,
            "d_above_one": d_gt_one,
            "store_start_padding_nonzero": start_padding,
            "model_index_store_necessary_fits": index_fits,
            "model_direct_same_width_fits": direct_same_width,
            "size_predictions_differ": predictions_differ,
            "size_decided_archives": decided,
        },
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Probe the RPF9 secondary area.")
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    try:
        _output.guard_output(args.output, args.paths)
        result = summarize(args.paths)
        text = json.dumps(result, indent=1, sort_keys=True) + "\n"
        if args.output:
            _output.write_atomic(args.output, text)
        else:
            sys.stdout.write(text)
    except _output.OutputCollisionError as error:
        sys.stderr.write("error: %s\n" % error)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
