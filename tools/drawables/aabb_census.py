#!/usr/bin/env python3
"""Aggregate the drawable AABB checks over decoded resources.

The manifest is JSON Lines with one object per decoded resource:

    {"id": "sample-a", "file": "drawA.bin", "system_length": 5872}

The tool runs the inspector on every file and counts the per-model AABB union
and the header AABB union. It reads only and prints the summary. The manifest
and the decoded files are local inputs; they are not part of this repository.

See formats/resources/drawables/README.md for the layout and the limits.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter

from drawable_inspect import Inspector, DrawableError, MAX_INPUT

MAX_ENTRIES = 1 << 16


class CensusError(Exception):
    pass


def read_manifest(path: str):
    entries = []
    with open(path, "r", encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            if len(entries) >= MAX_ENTRIES:
                raise CensusError(f"the manifest exceeds the {MAX_ENTRIES}-entry cap")
            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                raise CensusError(f"line {number} is not JSON: {error}") from error
            if not isinstance(record, dict):
                raise CensusError(f"line {number} is not an object")
            missing = {"id", "file", "system_length"} - record.keys()
            if missing:
                raise CensusError(f"line {number} is missing {', '.join(sorted(missing))}")
            if not isinstance(record["system_length"], int) or record["system_length"] <= 0:
                raise CensusError(f"line {number} has an invalid system_length")
            entries.append(record)
    return entries


def census_file(entry):
    with open(entry["file"], "rb") as handle:
        data = handle.read(MAX_INPUT + 1)
    if len(data) > MAX_INPUT:
        raise CensusError(f"the file exceeds the {MAX_INPUT}-byte cap")
    inspector = Inspector(data, entry["system_length"])
    inspector.walk()
    return inspector.report()


def census(manifest: str):
    entries = read_manifest(manifest)
    summary = {
        "entries": len(entries),
        "errors": [],
        "drawables_with_bounds": 0,
        "models": 0,
        "models_one_geometry": 0,
        "models_multi_geometry": 0,
        "model_union_pass": 0,
        "model_union_fail": 0,
        "multi_geometry_union_pass": 0,
        "multi_geometry_union_fail": 0,
        "header_pass": 0,
        "header_fail": 0,
        "exception_causes": Counter(),
        "exceptions": [],
    }
    for entry in entries:
        try:
            report = census_file(entry)
        except (OSError, DrawableError, CensusError) as error:
            summary["errors"].append({"id": entry["id"], "detail": str(error)})
            continue
        for lod in report.get("lod_slots", []):
            for model in lod["models"]:
                summary["models"] += 1
                if model["geometry_count"] == 1:
                    summary["models_one_geometry"] += 1
                elif model["geometry_count"] > 1:
                    summary["models_multi_geometry"] += 1
                if model["aabb_union_matches"] is True:
                    summary["model_union_pass"] += 1
                    if model["geometry_count"] > 1:
                        summary["multi_geometry_union_pass"] += 1
                elif model["aabb_union_matches"] is False:
                    summary["model_union_fail"] += 1
                    if model["geometry_count"] > 1:
                        summary["multi_geometry_union_fail"] += 1
        header = report.get("header_aabb_union")
        if header is None:
            continue
        summary["drawables_with_bounds"] += 1
        if header["matches"]:
            summary["header_pass"] += 1
            continue
        summary["header_fail"] += 1
        cause = "no_null_lod_slot"
        if header["null_lod_slots"] == 3:
            cause = "three_null_lod_slots"
        elif header["null_lod_slots"] > 0:
            cause = "some_null_lod_slots"
        summary["exception_causes"][cause] += 1
        if len(summary["exceptions"]) < 256:
            summary["exceptions"].append(
                {
                    "id": entry["id"],
                    "delta": header["delta"],
                    "null_lod_slots": header["null_lod_slots"],
                    "model_count": header["model_count"],
                    "cause": cause,
                }
            )
    summary["exception_causes"] = dict(summary["exception_causes"])
    return summary


def print_text(summary):
    print(f"entries:                 {summary['entries']}")
    print(f"drawables with bounds:   {summary['drawables_with_bounds']}")
    print(f"models:                  {summary['models']}")
    print(f"  one geometry:          {summary['models_one_geometry']}")
    print(f"  at least two:          {summary['models_multi_geometry']}")
    print(f"model union pass:        {summary['model_union_pass']}")
    print(f"model union fail:        {summary['model_union_fail']}")
    print(f"multi-geometry pass:     {summary['multi_geometry_union_pass']}")
    print(f"multi-geometry fail:     {summary['multi_geometry_union_fail']}")
    print(f"header union pass:       {summary['header_pass']}")
    print(f"header union fail:       {summary['header_fail']}")
    for cause, count in sorted(summary["exception_causes"].items()):
        print(f"  {cause}: {count}")
    for error in summary["errors"]:
        print(f"error: {error['id']}: {error['detail']}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--manifest", required=True, help="JSON Lines manifest of decoded resources")
    parser.add_argument("--json", action="store_true", help="print the summary as JSON")
    args = parser.parse_args(argv)
    try:
        summary = census(args.manifest)
    except CensusError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    if args.json:
        json.dump(summary, sys.stdout, indent=2)
        print()
    else:
        print_text(summary)
    return 0 if not summary["errors"] else 1


if __name__ == "__main__":
    sys.exit(main())
