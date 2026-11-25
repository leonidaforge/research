#!/usr/bin/env python3
"""Aggregate material counts over decoded drawable resources.

The manifest is JSON Lines with one object per decoded resource:

    {"id": "sample-a", "file": "drawA.bin", "system_length": 5872}

The tool runs the inspector on every file and counts drawables with a material
chain, shaders, declared slots, bound and unbound slots, null keys, and the
occurrence of every shader and texture-parameter hash. It reads only and prints
the summary. The manifest and decoded files are local inputs.

No store join is attempted, so no resolved count is reported.
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
        "drawables": 0,
        "shaders": 0,
        "declared_slots": 0,
        "bound": 0,
        "unbound": 0,
        "null_key": 0,
        "shader_hashes": Counter(),
        "parameter_hashes": Counter(),
    }
    for entry in entries:
        try:
            report = census_file(entry)
        except (OSError, DrawableError, CensusError) as error:
            summary["errors"].append({"id": entry["id"], "detail": str(error)})
            continue
        materials = report.get("materials")
        if not materials:
            continue
        summary["drawables"] += 1
        for shader in materials["shaders"]:
            summary["shaders"] += 1
            summary["shader_hashes"][shader["shader_hash"]] += 1
            parameters = shader.get("parameters")
            if not parameters:
                continue
            summary["declared_slots"] += parameters["texture_count"]
            summary["bound"] += parameters["bound"]
            summary["unbound"] += parameters["unbound"]
            summary["null_key"] += parameters["keys"]["null_key"]
            for texture in parameters["texture_parameters"]:
                summary["parameter_hashes"][texture["name"]] += 1
    summary["shader_hashes"] = dict(sorted(summary["shader_hashes"].items()))
    summary["parameter_hashes"] = dict(sorted(summary["parameter_hashes"].items()))
    return summary


def print_text(summary):
    print(f"entries:          {summary['entries']}")
    print(f"drawables:        {summary['drawables']}")
    print(f"shaders:          {summary['shaders']}")
    print(f"declared slots:   {summary['declared_slots']}")
    print(f"  bound:          {summary['bound']}")
    print(f"  unbound:        {summary['unbound']}")
    print(f"  null keys:      {summary['null_key']}")
    print("shader hashes:")
    for value, count in summary["shader_hashes"].items():
        print(f"  {value}: {count}")
    print("parameter hashes:")
    for value, count in summary["parameter_hashes"].items():
        print(f"  {value}: {count}")
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
