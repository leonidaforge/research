#!/usr/bin/env python3
"""Reproduce the PMAP block-offset prediction record.

The tool reads extracted PMAP payloads read-only. It applies two candidate
padding rules to the block table and records which payloads were used for the
designed alignment contrast and for the random reproduction split. It writes
labels and counts only; it does not print payload bytes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import struct
import sys
import tempfile

import psin_inspect

SEED = 20261125
HELD_OUT_COUNT = 10
DEFAULT_MAX_BYTES = 2 * 1024 * 1024 * 1024


def path_inside(target: str, directory: str) -> bool:
    target_path = os.path.realpath(os.path.abspath(target))
    directory_path = os.path.realpath(os.path.abspath(directory))
    return target_path == directory_path or target_path.startswith(directory_path + os.sep)


def align16(value: int) -> int:
    return (value + 15) & ~15


def payload_model(data: bytes, label: str) -> dict:
    report = psin_inspect.inspect_bytes(data, label=label)
    if report["family"] != "PMAP":
        raise psin_inspect.PsinError(f"{label}: not a PMAP payload")
    family = report["family_data"]
    blocks = family["blocks"]
    header = family["header"]
    if header is None:
        raise psin_inspect.PsinError(f"{label}: PMAP body header is missing")
    return {
        "label": label,
        "first_offset": report["header"]["first_section_offset"],
        "count": header["count"],
        "lengths": [block["length"] for block in blocks],
        "actual_offsets": [block["offset"] for block in blocks],
    }


def predict(lengths, pad_after_last: bool) -> tuple:
    offsets = []
    position = 0x10
    for index, length in enumerate(lengths):
        offsets.append(position)
        last = index + 1 == len(lengths)
        position += length if last and not pad_after_last else align16(length)
    return offsets, position


def check(row: dict, pad_after_last: bool) -> bool:
    offsets, first = predict(row["lengths"], pad_after_last)
    return offsets == row["actual_offsets"] and first == row["first_offset"]


def evaluate(rows: list, seed: int = SEED, held_out_count: int = HELD_OUT_COUNT) -> dict:
    aligned = [row for row in rows if row["first_offset"] % 16 == 0]
    unaligned = [row for row in rows if row["first_offset"] % 16 != 0]

    contrast_passed = [row["label"] for row in unaligned if check(row, False)]
    contrast_failed = [row["label"] for row in unaligned if not check(row, False)]

    random.seed(seed)
    held_out = random.sample(rows, min(held_out_count, len(rows)))
    held_labels = {row["label"] for row in held_out}
    fit_rows = [row for row in rows if row["label"] not in held_labels]
    reproduction_passed = [row["label"] for row in held_out if check(row, False)]
    reproduction_failed = [row["label"] for row in held_out if not check(row, False)]

    return {
        "population": len(rows),
        "models": {
            "pad_after_last": "padding after the last block",
            "no_pad_after_last": "padding only between blocks",
        },
        "designed_alignment_contrast": {
            "aligned_payloads": [row["label"] for row in aligned],
            "aligned_count": len(aligned),
            "unaligned_payloads": [row["label"] for row in unaligned],
            "unaligned_count": len(unaligned),
            "model_tested": "no_pad_after_last",
            "passed": len(contrast_passed),
            "failed": contrast_failed,
            "blind": False,
            "note": "Both padding models fit the aligned set, so the aligned set does not identify the rule. The split is a designed contrast, not a fit-and-predict hold-out.",
        },
        "random_reproduction_split": {
            "seed": seed,
            "excluding_held_out": [row["label"] for row in fit_rows],
            "excluding_held_out_count": len(fit_rows),
            "held_out": [row["label"] for row in held_out],
            "held_out_count": len(held_out),
            "passed": len(reproduction_passed),
            "failed": reproduction_failed,
            "blind": False,
            "note": "The model was known before this split; the split checks reproduction, not generalization.",
        },
        "alternative_model_fit": {
            "pad_after_last": sum(1 for row in rows if check(row, True)),
            "no_pad_after_last": sum(1 for row in rows if check(row, False)),
            "population": len(rows),
        },
    }


def load_directory(directory: str, max_bytes: int = DEFAULT_MAX_BYTES) -> list:
    rows = []
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
            rows.append(payload_model(data, name[:-4]))
        except psin_inspect.PsinError:
            continue
    return rows


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Reproduce the PMAP block-offset prediction.")
    parser.add_argument("--samples", required=True, help="directory of extracted .bin payloads")
    parser.add_argument("--json", action="store_true", help="print JSON instead of a summary")
    parser.add_argument("--output", help="write JSON atomically to this file")
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--held-out", type=int, default=HELD_OUT_COUNT)
    parser.add_argument(
        "--max-bytes", type=int, default=DEFAULT_MAX_BYTES,
        help="refuse a sample larger than this many bytes",
    )
    args = parser.parse_args(argv)

    if args.output and path_inside(args.output, args.samples):
        print("error: output path is inside the sample directory", file=sys.stderr)
        return 1
    try:
        rows = load_directory(args.samples, args.max_bytes)
    except (OSError, psin_inspect.PsinError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    if not rows:
        print("error: no PMAP payloads found", file=sys.stderr)
        return 1
    result = evaluate(rows, args.seed, args.held_out)
    rendered = json.dumps(result, indent=2) + "\n"

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
        contrast = result["designed_alignment_contrast"]
        reproduction = result["random_reproduction_split"]
        print(f"population: {result['population']}")
        print(f"designed contrast: {contrast['passed']} of {contrast['unaligned_count']}")
        print(f"random reproduction: {reproduction['passed']} of {reproduction['held_out_count']}")
        print(f"alternative fits: {result['alternative_model_fit']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
