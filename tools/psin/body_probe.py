#!/usr/bin/env python3
"""Summarise committed LSCH/LENM body and PMAP name observations.

The tool reads extracted PSIN payloads read-only and writes counts only. It does
not print names, payload bytes or key values.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile

import psin_inspect

DEFAULT_MAX_BYTES = 2 * 1024 * 1024 * 1024


def name_strings(data: bytes, blocks: list) -> list:
    for block in blocks:
        if block["id"] != 1:
            continue
        start = block["offset"]
        raw = data[start:start + block["length"]]
        if not raw.endswith(b"\x00"):
            return []
        parts = raw[:-1].split(b"\x00")
        return [
            part for part in parts
            if part and all(0x20 <= byte < 0x7F for byte in part)
        ]
    return []


def inspect_payload(data: bytes, label: str) -> dict:
    report = psin_inspect.inspect_bytes(data)
    family = report["family"]
    result = {"label": label, "family": family}
    if family == "LSCH":
        bodies = report["family_data"]["section_bodies"]
        lsch = bodies["LSCH"]
        lenm = bodies["LENM"]
        result["lsch"] = {
            "length": lsch["length"],
            "marker_count": lsch["marker_count"],
            "tail_length": lsch["tail_length"],
            "header_word_0x08": lsch["header_word_0x08"],
        }
        result["lenm"] = {
            "empty": lenm["empty"],
            "length": lenm["length"],
            "header_multiple_8": lenm["body_minus_header_multiple_8"],
            "count": lenm["count"],
            "extra_length": lenm["extra_length"],
        }
    elif family == "PMAP":
        family_data = report["family_data"]
        names = name_strings(data, family_data["blocks"])
        psch_ids = set(family_data["psch"]["ids"]) if family_data["psch"] else set()
        block_ids = {block["id"] for block in family_data["blocks"]}
        result["names"] = {
            "block": any(block["id"] == 1 for block in family_data["blocks"]),
            "count": len(names),
            "strings": names,
        }
        result["psch"] = {
            "ids": len(psch_ids),
            "unused_by_blocks": len(psch_ids - block_ids),
        }
    return result


def aggregate(reports: list) -> dict:
    lsch = [report for report in reports if report["family"] == "LSCH"]
    pmap = [report for report in reports if report["family"] == "PMAP"]
    tails = [report["lsch"]["tail_length"] for report in lsch]
    headers = {}
    for report in lsch:
        word = report["lsch"]["header_word_0x08"]
        headers[str(word)] = headers.get(str(word), 0) + 1
    nonempty_lenm = [
        report["lenm"] for report in lsch if not report["lenm"]["empty"]
    ]
    extras = [item["extra_length"] for item in nonempty_lenm if item["extra_length"] > 0]
    names = [name for report in pmap for name in report["names"]["strings"]]
    return {
        "lsch_payloads": len(lsch),
        "lsch_marker_records": sum(report["lsch"]["marker_count"] for report in lsch),
        "lsch_tail_min": min(tails) if tails else None,
        "lsch_tail_max": max(tails) if tails else None,
        "lsch_tail_multiple_16": all(length % 16 == 0 for length in tails),
        "lsch_header_words": headers,
        "lenm_empty": sum(1 for report in lsch if report["lenm"]["empty"]),
        "lenm_nonempty": len(nonempty_lenm),
        "lenm_header_multiple_8": sum(
            1 for item in nonempty_lenm if item["header_multiple_8"]
        ),
        "lenm_zero_extra": sum(1 for item in nonempty_lenm if item["extra_length"] == 0),
        "lenm_extra": len(extras),
        "lenm_extra_min": min(extras) if extras else None,
        "lenm_extra_max": max(extras) if extras else None,
        "pmap_payloads": len(pmap),
        "name_blocks": sum(1 for report in pmap if report["names"]["block"]),
        "name_total": len(names),
        "name_distinct": len(set(names)),
        "psch_unused_ids_total": sum(
            report["psch"]["unused_by_blocks"] for report in pmap
        ),
    }


def load_directory(directory: str, max_bytes: int = DEFAULT_MAX_BYTES) -> list:
    reports = []
    seen = set()
    for name in sorted(os.listdir(directory)):
        path = os.path.join(directory, name)
        if not os.path.isfile(path) or not name.lower().endswith(".bin"):
            continue
        if os.path.getsize(path) > max_bytes:
            raise psin_inspect.PsinError(f"{name}: larger than the {max_bytes}-byte cap")
        with open(path, "rb") as handle:
            data = handle.read()
        if data[:4] != b"PSIN":
            continue
        digest = hashlib.sha256(data).digest()
        if digest in seen:
            continue
        seen.add(digest)
        try:
            reports.append(inspect_payload(data, name[:-4]))
        except psin_inspect.PsinError:
            continue
    return reports


def path_inside(target: str, directory: str) -> bool:
    target_path = os.path.realpath(os.path.abspath(target))
    directory_path = os.path.realpath(os.path.abspath(directory))
    return target_path == directory_path or target_path.startswith(directory_path + os.sep)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Summarise LSCH/LENM bodies and PMAP names.")
    parser.add_argument("--samples", required=True, help="directory of extracted .bin payloads")
    parser.add_argument("--summary-only", action="store_true", help="omit per-payload reports")
    parser.add_argument("--json", action="store_true", help="print JSON")
    parser.add_argument("--output", help="write JSON atomically to this file")
    parser.add_argument(
        "--max-bytes", type=int, default=DEFAULT_MAX_BYTES,
        help="refuse a sample larger than this many bytes",
    )
    args = parser.parse_args(argv)

    if args.output and path_inside(args.output, args.samples):
        print("error: output path is inside the sample directory", file=sys.stderr)
        return 1
    try:
        reports = load_directory(args.samples, args.max_bytes)
    except (OSError, psin_inspect.PsinError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    if not reports:
        print("error: no PSIN payloads found", file=sys.stderr)
        return 1
    document = {"summary": aggregate(reports)}
    if not args.summary_only:
        for report in reports:
            report.get("names", {}).pop("strings", None)
        document["reports"] = reports
    rendered = json.dumps(document, indent=2) + "\n"
    if args.output:
        target = os.path.abspath(args.output)
        directory = os.path.dirname(target) or "."
        handle = tempfile.NamedTemporaryFile("w", delete=False, dir=directory, encoding="utf-8")
        try:
            handle.write(rendered)
            handle.close()
            os.replace(handle.name, target)
        finally:
            if not handle.closed:
                handle.close()
            if os.path.exists(handle.name):
                os.remove(handle.name)
        return 0
    if args.json:
        sys.stdout.write(rendered)
    else:
        summary = document["summary"]
        for key, value in summary.items():
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
