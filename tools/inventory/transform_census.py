"""Enumerate the unreadable population of a census manifest set by failure stage.

Each unreadable row gets a stage and a structural fingerprint. The fingerprint
hashes the row's type, layout, chunk encoding and count, compression mode, size
relation and cipher descriptor. It is not a content hash and carries no payload
bytes.

The full population behind the payload transform is the set of rows whose
`payload_transform` flag is true. The readable structure population is the rest.
"""

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import recursive_inventory as inventory

SCHEMA = "leonida-forge.transform-census/1"
MAX_ROWS = 10_000_000
MAX_MANIFESTS = 100_000


class TransformError(Exception):
    """A refusal or a bound violation."""


def row_fingerprint(row: dict) -> str:
    cipher = row.get("payload_cipher") or {}
    fields = (
        row.get("type_id"),
        row.get("layout"),
        row.get("mode"),
        inventory.chunk_label(row),
        (row.get("chunks") or {}).get("count"),
        bool(row.get("payload_transform")),
        cipher.get("algorithm"),
        cipher.get("type"),
        cipher.get("supported"),
        row.get("logical_size") == row.get("stored_size"),
        row.get("read_source"),
    )
    text = json.dumps(fields, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def stage_for(row: dict) -> tuple[str, str]:
    contents = row.get("contents") or {}
    state = contents.get("state")
    reason = contents.get("reason")
    if row.get("payload_transform") is True or state == "unsupported_transform":
        return "unsupported transformation", state or reason or ""
    if state in ("unsupported", "unsupported_storage"):
        return "unsupported storage class", state or reason or ""
    if state in ("corrupt", "decode_error"):
        return "corrupt compressed stream", state or reason or ""
    if state == "partial":
        return "incomplete reconstruction", state or reason or ""
    if state == "unreadable":
        return "metadata readability", state or reason or ""
    return "unclassified", state or reason or ""


def ensure_output(output: Path, *inputs: Path) -> None:
    output = Path(output).resolve()
    for source in inputs:
        source = Path(source).resolve()
        if output == source or source in output.parents:
            raise TransformError("the output directory MUST NOT lie inside an input directory")
        if output in source.parents:
            raise TransformError("an input directory MUST NOT lie inside the output directory")


def census(manifest_dir: Path, rows_path: Path, output_dir: Path) -> dict:
    top = {}
    if rows_path.exists():
        with rows_path.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as error:
                    raise TransformError(f"{rows_path.name} line {line_number} is not JSON: {error}") from error
                digest = (record.get("attempt") or {}).get("sha256")
                if digest:
                    top[digest] = (record.get("relative"), record.get("row"))
    stages = Counter()
    by_type = defaultdict(lambda: {"rows": 0, "stages": Counter(), "encodings": Counter(), "fingerprints": Counter()})
    fingerprints = Counter()
    algorithm = Counter()
    cipher_type = Counter()
    total = 0
    readable = 0
    unreadable = 0
    transform_flagged = 0
    manifests = 0
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "unreadable.jsonl"
    with output_path.open("w", encoding="utf-8", newline="\n") as sink:
        for path in sorted(manifest_dir.glob("*.jsonl")):
            manifests += 1
            if manifests > MAX_MANIFESTS:
                raise TransformError(f"the manifest set exceeds the {MAX_MANIFESTS}-manifest bound")
            digest = path.stem
            with path.open(encoding="utf-8") as handle:
                try:
                    header = json.loads(handle.readline())
                except json.JSONDecodeError as error:
                    raise TransformError(f"{path.name} header is not JSON: {error}") from error
                if header.get("kind") != "header":
                    raise TransformError(f"{path.name} has no header record")
                for line_number, line in enumerate(handle, 2):
                    if not line.strip():
                        continue
                    try:
                        row = json.loads(line)
                    except json.JSONDecodeError as error:
                        raise TransformError(f"{path.name} line {line_number} is not JSON: {error}") from error
                    if row.get("kind") != "row":
                        continue
                    total += 1
                    if total > MAX_ROWS:
                        raise TransformError(f"the manifest set exceeds the {MAX_ROWS}-row bound")
                    if row.get("payload_transform") is True:
                        transform_flagged += 1
                    if inventory.is_readable(row):
                        readable += 1
                        continue
                    unreadable += 1
                    stage, detail = stage_for(row)
                    fingerprint = row_fingerprint(row)
                    stages[stage] += 1
                    fingerprints[fingerprint] += 1
                    type_id = row.get("type_id")
                    entry = by_type[type_id]
                    entry["rows"] += 1
                    entry["stages"][stage] += 1
                    entry["encodings"][inventory.chunk_label(row)] += 1
                    entry["fingerprints"][fingerprint] += 1
                    cipher = row.get("payload_cipher") or {}
                    algorithm[str(cipher.get("algorithm"))] += 1
                    cipher_type[str(cipher.get("type"))] += 1
                    sink.write(
                        json.dumps(
                            {
                                "schema": SCHEMA,
                                "sha256": digest,
                                "top_relative": top.get(digest, (None, None))[0],
                                "top_row": top.get(digest, (None, None))[1],
                                "row": row.get("row"),
                                "type_id": type_id,
                                "layout": row.get("layout"),
                                "mode": row.get("mode"),
                                "encoding": inventory.chunk_label(row),
                                "logical_size": row.get("logical_size"),
                                "stored_size": row.get("stored_size"),
                                "payload_transform": row.get("payload_transform"),
                                "cipher": cipher,
                                "state": (row.get("contents") or {}).get("state"),
                                "stage": stage,
                                "detail": detail,
                                "fingerprint": fingerprint,
                            },
                            sort_keys=True,
                        )
                        + "\n"
                    )
    summary = {
        "schema": SCHEMA,
        "manifests": manifests,
        "rows_total": total,
        "rows_readable": readable,
        "rows_unreadable": unreadable,
        "transform_flagged": transform_flagged,
        "structure_population": total - transform_flagged,
        "stages": dict(sorted(stages.items())),
        "cipher_algorithm": dict(sorted(algorithm.items())),
        "cipher_type": dict(sorted(cipher_type.items())),
        "distinct_fingerprints": len(fingerprints),
        "fingerprints": dict(sorted(fingerprints.items(), key=lambda item: (-item[1], item[0]))),
        "by_type": {
            str(type_id): {
                "rows": value["rows"],
                "stages": dict(sorted(value["stages"].items())),
                "encodings": dict(sorted(value["encodings"].items())),
                "distinct_fingerprints": len(value["fingerprints"]),
            }
            for type_id, value in sorted(by_type.items(), key=lambda item: str(item[0]))
        },
    }
    inventory.write_json(output_dir / "summary.json", summary)
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest-dir", type=Path, required=True)
    parser.add_argument("--rows", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    ensure_output(args.output_dir, args.manifest_dir)
    summary = census(args.manifest_dir, args.rows, args.output_dir)
    print(
        json.dumps(
            {
                "rows_total": summary["rows_total"],
                "rows_unreadable": summary["rows_unreadable"],
                "transform_flagged": summary["transform_flagged"],
                "stages": summary["stages"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except TransformError as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(2)
