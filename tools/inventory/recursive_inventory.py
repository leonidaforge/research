#!/usr/bin/env python3
"""Deterministic recursive RPF9 inventory sampler.

Reads top-level native manifests, extracts a deterministic sample of readable
type-0 rows, manifests the nested archives, repeats one level deeper, and
samples readable payloads per type. All inputs are opened read-only.

Outputs stay in the scratch directory. Nothing is written next to an input.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

RPF9_MAGIC = b"9FPR"
MAX_ARCHIVE_BYTES = 8 * 1024 * 1024
MAX_PAYLOAD_BYTES = 1 * 1024 * 1024
MAX_NESTED_ARCHIVES = 60
MAX_EXTRACTED_BYTES = 512 * 1024 * 1024

SELECTION_RULE = {
    "top_level": (
        "For each top-level archive, take the smallest, upper-median "
        "(index n//2) and largest readable type-0 row with logical size "
        "<= 8 MiB, ordered by (logical_size, row). Duplicate row indices "
        "are removed. Archives without such a row are skipped."
    ),
    "depth2": (
        "For each extracted depth-1 archive, take the smallest and largest "
        "readable type-0 row with logical size <= 8 MiB, ordered by "
        "(logical_size, row). Duplicate row indices are removed."
    ),
    "payloads": (
        "For each distinct type across nested manifests, take up to two "
        "readable rows with logical size <= 1 MiB, ordered by "
        "(logical_size, archive id, row)."
    ),
    "caps": {
        "max_depth": 2,
        "max_nested_archives": MAX_NESTED_ARCHIVES,
        "max_extracted_bytes": MAX_EXTRACTED_BYTES,
        "max_archive_bytes": MAX_ARCHIVE_BYTES,
        "max_payload_bytes": MAX_PAYLOAD_BYTES,
        "max_depth2_per_parent": 2,
        "max_payloads_per_type": 2,
    },
}

FIELDS = (
    "type_id",
    "row",
    "logical_size",
    "stored_size",
    "mode",
    "chunks",
    "payload_transform",
    "contents",
    "layout",
)


def read_jsonl(path: Path) -> list[dict]:
    documents = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                documents.append(json.loads(line))
    return documents


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")


def append_jsonl(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, sort_keys=True))
        handle.write("\n")


def safe_name(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", text).strip("_") or "item"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def classify_signature(prefix: bytes) -> str:
    if prefix.startswith(RPF9_MAGIC):
        return "rpf9-magic"
    if len(prefix) >= 2 and prefix[0] == 0x78 and prefix[1] in (0x01, 0x5E, 0x9C, 0xDA):
        return "zlib-container-header"
    if len(prefix) >= 8 and prefix == b"\x00" * 8:
        return "zero-prefix"
    return "unrecognized"


def is_readable(row: dict) -> bool:
    return bool(row.get("contents", {}).get("readable"))


def type0_rows(rows: list[dict], max_size: int) -> list[dict]:
    candidates = [
        row
        for row in rows
        if row.get("kind") == "row"
        and row.get("type_id") == 0
        and isinstance(row.get("logical_size"), int)
        and row["logical_size"] <= max_size
        and is_readable(row)
    ]
    return sorted(candidates, key=lambda row: (row["logical_size"], row["row"]))


def select_three(rows: list[dict], max_size: int) -> tuple[list[dict], int]:
    candidates = type0_rows(rows, max_size)
    if not candidates:
        return [], 0
    indices = [0]
    if len(candidates) > 1:
        indices.append(len(candidates) // 2)
        indices.append(len(candidates) - 1)
    selected = []
    seen = set()
    for index in indices:
        row = candidates[index]
        if row["row"] not in seen:
            seen.add(row["row"])
            selected.append(row)
    return selected, len(candidates)


def select_two(rows: list[dict], max_size: int) -> tuple[list[dict], int]:
    candidates = type0_rows(rows, max_size)
    if not candidates:
        return [], 0
    indices = [0]
    if len(candidates) > 1:
        indices.append(len(candidates) - 1)
    selected = []
    seen = set()
    for index in indices:
        row = candidates[index]
        if row["row"] not in seen:
            seen.add(row["row"])
            selected.append(row)
    return selected, len(candidates)


def chunk_label(row: dict) -> str:
    chunks = row.get("chunks")
    if not chunks:
        return "none"
    return f"encoding-{chunks.get('encoding')}"


def row_state(row: dict) -> str:
    contents = row.get("contents", {})
    if contents.get("readable"):
        return "readable"
    return str(contents.get("state") or contents.get("reason") or "unreadable")


def type_histogram(rows: list[dict]) -> list[dict]:
    buckets: dict[int, dict] = {}
    for row in rows:
        if row.get("kind") != "row":
            continue
        type_id = row.get("type_id")
        bucket = buckets.setdefault(
            type_id,
            {
                "type_id": type_id,
                "extension": row.get("extension"),
                "namespace": row.get("namespace"),
                "rows": 0,
                "readable": 0,
                "payload_transform": 0,
                "states": {},
                "layouts": {},
                "compression_modes": {},
                "chunk_encodings": {},
            },
        )
        bucket["rows"] += 1
        if is_readable(row):
            bucket["readable"] += 1
        if row.get("payload_transform"):
            bucket["payload_transform"] += 1
        state = row_state(row)
        bucket["states"][state] = bucket["states"].get(state, 0) + 1
        layout = str(row.get("layout"))
        bucket["layouts"][layout] = bucket["layouts"].get(layout, 0) + 1
        mode = str(row.get("mode"))
        bucket["compression_modes"][mode] = bucket["compression_modes"].get(mode, 0) + 1
        chunks = row.get("chunks")
        encoding = str(chunks.get("encoding")) if chunks else "none"
        bucket["chunk_encodings"][encoding] = bucket["chunk_encodings"].get(encoding, 0) + 1
    return [buckets[key] for key in sorted(buckets, key=lambda value: (value is None, value))]


def discover_manifests(inventory_dir: Path) -> tuple[list[dict], list[dict]]:
    archives = []
    duplicates = []
    seen = {}
    for path in sorted(inventory_dir.glob("*.jsonl")):
        try:
            documents = read_jsonl(path)
        except (OSError, json.JSONDecodeError) as error:
            duplicates.append({"manifest": str(path), "reason": f"unreadable: {error}"})
            continue
        if not documents or documents[0].get("kind") != "header":
            continue
        header = documents[0]
        archive = header.get("archive")
        if not archive:
            continue
        key = str(Path(archive))
        if key in seen:
            duplicates.append(
                {"manifest": str(path), "archive": archive, "duplicate_of": str(seen[key])}
            )
            continue
        seen[key] = path
        archives.append(
            {
                "manifest": path,
                "header": header,
                "rows": documents[1:],
            }
        )
    archives.sort(key=lambda item: str(item["header"]["archive"]).lower())
    return archives, duplicates


def ensure_outside_inputs(scratch: Path, game_dir: Path, inventory_dir: Path) -> None:
    scratch = scratch.resolve()
    for label, source in (("game directory", game_dir), ("manifest directory", inventory_dir)):
        source = source.resolve()
        if scratch == source or source in scratch.parents:
            raise SystemExit(f"scratch directory MUST NOT be inside the {label}")
        if scratch in source.parents:
            raise SystemExit(f"the {label} MUST NOT be inside the scratch directory")


class Sampler:
    def __init__(self, lforge: Path, executable: Path, scratch: Path):
        self.lforge = lforge
        self.executable = executable
        self.scratch = scratch
        self.nested_records: list[dict] = []
        self.payload_records: list[dict] = []
        self.failures: list[dict] = []
        self.extracted_bytes = 0
        self.started = time.time()
        self.log_handle = None

    def log(self, message: str) -> None:
        line = f"{time.strftime('%H:%M:%S')} {message}"
        print(line)
        if self.log_handle is not None:
            self.log_handle.write(line + "\n")
            self.log_handle.flush()

    def run(self, command: list[str]) -> subprocess.CompletedProcess:
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

    def extract(
        self,
        parent: Path,
        row: dict,
        output: Path,
        label: dict,
    ) -> dict:
        expected = row["logical_size"]
        output.parent.mkdir(parents=True, exist_ok=True)
        if output.exists() and output.stat().st_size == expected:
            self.extracted_bytes += expected
            return {
                "ok": True,
                "cached": True,
                "exit": 0,
                "actual_size": expected,
                "expected_size": expected,
            }
        if output.exists():
            output.unlink()
        command = [
            str(self.lforge),
            "archive",
            "extract",
            str(parent),
            "--row",
            str(row["row"]),
            "--output",
            str(output),
            "--executable",
            str(self.executable),
        ]
        result = self.run(command)
        actual = output.stat().st_size if output.exists() else None
        ok = result.returncode == 0 and actual == expected
        if ok:
            self.extracted_bytes += expected
        record = {
            "ok": ok,
            "cached": False,
            "exit": result.returncode,
            "actual_size": actual,
            "expected_size": expected,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
        if not ok:
            failure = dict(label)
            failure.update(
                {
                    "kind": "failed_extraction",
                    "row_type_id": row.get("type_id"),
                    "chunk_encoding": chunk_label(row),
                    "compression_mode": row.get("mode"),
                    "payload_transform": row.get("payload_transform"),
                    "contents_state": row_state(row),
                    "expected_size": expected,
                    "actual_size": actual,
                    "exit": result.returncode,
                    "error": (result.stderr or result.stdout).strip(),
                }
            )
            self.failures.append(failure)
            append_jsonl(self.scratch / "failures.jsonl", failure)
        return record

    def manifest(self, archive: Path, output: Path) -> dict:
        output.parent.mkdir(parents=True, exist_ok=True)
        if not output.exists():
            command = [
                str(self.lforge),
                "archive",
                "manifest",
                str(archive),
                "--format",
                "jsonl",
                "--output",
                str(output),
                "--overwrite",
                "--executable",
                str(self.executable),
            ]
            result = self.run(command)
            if result.returncode != 0:
                return {
                    "ok": False,
                    "exit": result.returncode,
                    "error": (result.stderr or result.stdout).strip(),
                }
        try:
            documents = read_jsonl(output)
        except (OSError, json.JSONDecodeError) as error:
            return {"ok": False, "exit": None, "error": str(error)}
        if not documents or documents[0].get("kind") != "header":
            return {"ok": False, "exit": None, "error": "missing manifest header"}
        header = documents[0]
        rows = documents[1:]
        return {
            "ok": True,
            "exit": 0,
            "authentication": header.get("authentication", {}),
            "rows": len(rows),
            "types": type_histogram(rows),
            "documents": rows,
        }


def nested_record(
    depth: int,
    parent: Path,
    parent_id: str,
    top_relative: str,
    row: dict,
    output: Path,
    extraction: dict,
    manifest: dict,
    digest: str,
    first8: bytes,
    duplicate_of: str | None,
) -> dict:
    manifest_documents = manifest.pop("documents", [])
    return {
        "kind": "nested",
        "depth": depth,
        "parent_archive": str(parent),
        "parent_id": parent_id,
        "top_relative": top_relative,
        "parent_row": row["row"],
        "logical_size": row["logical_size"],
        "stored_size": row.get("stored_size"),
        "layout": row.get("layout"),
        "mode": row.get("mode"),
        "chunks": row.get("chunks"),
        "payload_transform": row.get("payload_transform"),
        "contents": row.get("contents"),
        "output": str(output),
        "sha256": digest,
        "first8": first8.hex(),
        "signature_class": classify_signature(first8),
        "duplicate_of": duplicate_of,
        "extraction": extraction,
        "manifest": manifest,
        "rows": manifest_documents,
    }


def aggregate_nested(records: list[dict]) -> dict:
    by_depth = {}
    by_signature = {}
    by_type = {}
    duplicates = {}
    auth = {}
    for record in records:
        depth = record["depth"]
        by_depth[depth] = by_depth.get(depth, 0) + 1
        signature = record["signature_class"]
        by_signature[signature] = by_signature.get(signature, 0) + 1
        manifest = record["manifest"]
        status = manifest.get("authentication", {}).get("status") if manifest.get("ok") else "manifest-failed"
        auth[status] = auth.get(status, 0) + 1
        for bucket in manifest.get("types", []):
            key = str(bucket["type_id"])
            entry = by_type.setdefault(
                key,
                {
                    "type_id": bucket["type_id"],
                    "rows": 0,
                    "readable": 0,
                    "archives": 0,
                },
            )
            entry["rows"] += bucket["rows"]
            entry["readable"] += bucket["readable"]
            entry["archives"] += 1
        if record["duplicate_of"]:
            duplicates.setdefault(record["duplicate_of"], []).append(record["parent_id"])
    return {
        "by_depth": {str(key): value for key, value in sorted(by_depth.items())},
        "by_signature": by_signature,
        "by_type": [by_type[key] for key in sorted(by_type, key=int)],
        "duplicates": duplicates,
        "authentication": auth,
    }


def payload_candidates(
    nested_records: list[dict], max_per_type: int, max_size: int
) -> tuple[dict[int, list[tuple[dict, dict]]], dict[int, dict]]:
    buckets: dict[int, list[tuple[dict, dict]]] = {}
    stats: dict[int, dict] = {}
    for record in nested_records:
        manifest = record["manifest"]
        if not manifest.get("ok"):
            continue
        for row in record.get("rows", []):
            if row.get("kind") != "row":
                continue
            type_id = row.get("type_id")
            entry = stats.setdefault(
                type_id,
                {
                    "type_id": type_id,
                    "rows": 0,
                    "readable": 0,
                    "readable_within_limit": 0,
                    "chunk_encodings": {},
                    "failures": 0,
                    "extracted": 0,
                },
            )
            entry["rows"] += 1
            encoding = chunk_label(row)
            entry["chunk_encodings"][encoding] = entry["chunk_encodings"].get(encoding, 0) + 1
            if not is_readable(row):
                continue
            entry["readable"] += 1
            if not isinstance(row.get("logical_size"), int) or row["logical_size"] > max_size:
                continue
            entry["readable_within_limit"] += 1
            buckets.setdefault(type_id, []).append((row, record))
    selected = {}
    for type_id, candidates in buckets.items():
        ordered = sorted(
            candidates,
            key=lambda item: (
                item[0]["logical_size"],
                item[1]["parent_id"],
                item[0]["row"],
            ),
        )
        selected[type_id] = ordered[:max_per_type]
    return selected, stats


def aggregate_payloads(records: list[dict], stats: dict[int, dict]) -> dict:
    by_type = {}
    by_signature = {}
    for record in records:
        type_id = record["type_id"]
        entry = by_type.setdefault(
            type_id,
            {
                "type_id": type_id,
                "attempted": 0,
                "succeeded": 0,
                "failed": 0,
                "signatures": {},
            },
        )
        entry["attempted"] += 1
        if record["extraction"]["ok"]:
            entry["succeeded"] += 1
        else:
            entry["failed"] += 1
        signature = record["signature_class"]
        entry["signatures"][signature] = entry["signatures"].get(signature, 0) + 1
        by_signature[signature] = by_signature.get(signature, 0) + 1
    for type_id, entry in stats.items():
        if type_id not in by_type:
            by_type[type_id] = {
                "type_id": type_id,
                "attempted": 0,
                "succeeded": 0,
                "failed": 0,
                "signatures": {},
            }
    return {
        "by_type": [by_type[key] for key in sorted(by_type, key=lambda value: (value is None, value))],
        "by_signature": by_signature,
    }


def write_report(path: Path, summary: dict) -> None:
    lines = ["# Recursive inventory scratch report", ""]
    lines.append(f"Generated: {time.strftime('%Y-%m-%dT%H:%M:%S')}")
    lines.append("")
    lines.append("## Caps")
    lines.append("")
    for key, value in summary["selection"]["caps"].items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("## Top-level archives")
    lines.append("")
    lines.append("| Archive | Rows | Type-0 candidates | Selected | Nested extracted |")
    lines.append("| --- | ---: | ---: | ---: | ---: |")
    for item in summary["top_level"]:
        lines.append(
            "| {relative} | {rows} | {candidates} | {selected} | {nested} |".format(**item)
        )
    lines.append("")
    lines.append("## Nested archives")
    lines.append("")
    lines.append(
        "| Depth | Parent row | Size | SHA-256 | Signature | Auth | Rows | Duplicate of |"
    )
    lines.append("| ---: | ---: | ---: | --- | --- | --- | ---: | --- |")
    for record in summary["nested"]:
        lines.append(
            "| {depth} | {parent_row} | {logical_size} | `{sha256}` | {signature_class} | "
            "{auth} | {rows} | {duplicate_of} |".format(
                depth=record["depth"],
                parent_row=record["parent_row"],
                logical_size=record["logical_size"],
                sha256=record["sha256"],
                signature_class=record["signature_class"],
                auth=record["manifest"].get("authentication", {}).get("status", "failed"),
                rows=record["manifest"].get("rows", 0),
                duplicate_of=record["duplicate_of"] or "",
            )
        )
    lines.append("")
    lines.append("## Depth 2")
    lines.append("")
    lines.append(f"- Candidates: {summary['depth2']['candidates']}")
    lines.append(f"- Extracted: {summary['depth2']['extracted']}")
    lines.append(f"- Reason: {summary['depth2']['reason'] or 'sampled'}")
    lines.append("")
    lines.append("## Nested type histogram")
    lines.append("")
    lines.append("| Type | Rows | Readable | Nested archives |")
    lines.append("| ---: | ---: | ---: | ---: |")
    for item in summary["nested_aggregate"]["by_type"]:
        lines.append(
            "| {type_id} | {rows} | {readable} | {archives} |".format(**item)
        )
    lines.append("")
    lines.append("## Payload samples")
    lines.append("")
    lines.append("| Type | Attempted | Succeeded | Failed | Signatures |")
    lines.append("| ---: | ---: | ---: | ---: | --- |")
    for item in summary["payload_aggregate"]["by_type"]:
        signatures = ", ".join(
            f"{key}: {value}" for key, value in sorted(item["signatures"].items())
        )
        values = dict(item)
        values["signatures"] = signatures or "-"
        lines.append(
            "| {type_id} | {attempted} | {succeeded} | {failed} | {signatures} |".format(
                **values
            )
        )
    lines.append("")
    lines.append("## Failures")
    lines.append("")
    if summary["failures"]:
        lines.append("| Kind | Type | Chunk encoding | Exit | Error |")
        lines.append("| --- | ---: | --- | ---: | --- |")
        for failure in summary["failures"]:
            lines.append(
                "| {kind} | {row_type_id} | {chunk_encoding} | {exit} | {error} |".format(
                    **failure
                )
            )
    else:
        lines.append("No extraction failures.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory-dir", required=True, type=Path)
    parser.add_argument("--game-dir", required=True, type=Path)
    parser.add_argument("--scratch-dir", required=True, type=Path)
    parser.add_argument("--lforge", required=True, type=Path)
    parser.add_argument("--executable", required=True, type=Path)
    parser.add_argument("--max-nested", type=int, default=MAX_NESTED_ARCHIVES)
    parser.add_argument("--max-bytes", type=int, default=MAX_EXTRACTED_BYTES)
    parser.add_argument("--max-archive-bytes", type=int, default=MAX_ARCHIVE_BYTES)
    parser.add_argument("--max-payload-bytes", type=int, default=MAX_PAYLOAD_BYTES)
    parser.add_argument("--max-depth2-per-parent", type=int, default=2)
    parser.add_argument("--max-payloads-per-type", type=int, default=2)
    parser.add_argument(
        "--plan-only",
        action="store_true",
        help="write the deterministic selection without running extraction",
    )
    args = parser.parse_args()

    if not args.inventory_dir.is_dir():
        raise SystemExit(f"manifest directory not found: {args.inventory_dir}")
    if not args.game_dir.is_dir():
        raise SystemExit(f"game directory not found: {args.game_dir}")
    if not args.lforge.is_file():
        raise SystemExit(f"lforge not found: {args.lforge}")
    if not args.executable.is_file():
        raise SystemExit(f"executable not found: {args.executable}")
    ensure_outside_inputs(args.scratch_dir, args.game_dir, args.inventory_dir)
    args.scratch_dir.mkdir(parents=True, exist_ok=True)

    selection = {key: value for key, value in SELECTION_RULE.items()}
    selection["caps"].update(
        {
            "max_nested_archives": args.max_nested,
            "max_extracted_bytes": args.max_bytes,
            "max_archive_bytes": args.max_archive_bytes,
            "max_payload_bytes": args.max_payload_bytes,
            "max_depth2_per_parent": args.max_depth2_per_parent,
            "max_payloads_per_type": args.max_payloads_per_type,
        }
    )

    manifests, manifest_duplicates = discover_manifests(args.inventory_dir)
    sampler = Sampler(args.lforge, args.executable, args.scratch_dir)
    log_path = args.scratch_dir / "run.log"
    sampler.log_handle = log_path.open("a", encoding="utf-8", newline="\n")
    sampler.log(f"manifests: {len(manifests)}")

    top_level = []
    depth1_plan = []
    for item in manifests:
        archive = Path(item["header"]["archive"])
        relative = str(item["header"].get("relative") or archive.name)
        selected, candidate_count = select_three(item["rows"], args.max_archive_bytes)
        depth1_plan.append((item, archive, relative, selected))
        top_level.append(
            {
                "archive": str(archive),
                "relative": relative,
                "rows": len([row for row in item["rows"] if row.get("kind") == "row"]),
                "candidates": candidate_count,
                "selected": len(selected),
                "nested": 0,
                "skip_reason": None
                if selected
                else "no readable type-0 row at or below the archive size limit",
            }
        )

    if args.plan_only:
        plan = {
            "selection": selection,
            "top_level": top_level,
            "depth1": [
                {
                    "archive": str(archive),
                    "rows": [row["row"] for row in selected],
                    "sizes": [row["logical_size"] for row in selected],
                }
                for _, archive, _, selected in depth1_plan
            ],
        }
        write_json(args.scratch_dir / "plan.json", plan)
        sampler.log("plan-only: no extraction run")
        return 0

    digest_first: dict[str, str] = {}
    d1_entries = []
    for item, archive, relative, selected in depth1_plan:
        top_record = next(entry for entry in top_level if entry["archive"] == str(archive))
        if not selected:
            sampler.log(f"skip {relative}: no candidate")
            continue
        for row in selected:
            if len(sampler.nested_records) >= args.max_nested:
                sampler.log(f"stop {relative} row {row['row']}: nested archive cap")
                top_record["skip_reason"] = "nested archive cap"
                break
            if sampler.extracted_bytes + row["logical_size"] > args.max_bytes:
                sampler.log(f"stop {relative} row {row['row']}: byte cap")
                top_record["skip_reason"] = "extracted byte cap"
                break
            identifier = f"d1:{relative}:{row['row']}"
            output = (
                args.scratch_dir
                / "nested"
                / "d1"
                / safe_name(relative)
                / f"row-{row['row']:05d}.rpf"
            )
            label = {
                "sample": identifier,
                "depth": 1,
                "parent_archive": str(archive),
                "parent_row": row["row"],
                "top_relative": relative,
            }
            extraction = sampler.extract(archive, row, output, label)
            if not extraction["ok"]:
                sampler.log(f"extract failed {identifier}")
                continue
            digest = sha256_file(output)
            duplicate_of = digest_first.get(digest)
            digest_first.setdefault(digest, identifier)
            with output.open("rb") as handle:
                first8 = handle.read(8)
            manifest = sampler.manifest(output, output.with_suffix(".jsonl"))
            record = nested_record(
                1,
                archive,
                identifier,
                relative,
                row,
                output,
                extraction,
                manifest,
                digest,
                first8,
                duplicate_of,
            )
            sampler.nested_records.append(record)
            append_jsonl(args.scratch_dir / "nested.jsonl", record)
            d1_entries.append(record)
            top_record["nested"] += 1
            sampler.log(
                f"d1 {identifier} {row['logical_size']} bytes profile={record['signature_class']}"
            )

    depth2_plan = []
    for record in sorted(d1_entries, key=lambda item: (item["top_relative"], item["parent_row"])):
        if len(sampler.nested_records) >= args.max_nested:
            break
        selected, candidate_count = select_two(record["rows"], args.max_archive_bytes)
        depth2_plan.append((record, selected, candidate_count))

    depth2_candidates = sum(candidate_count for _, _, candidate_count in depth2_plan)
    if not depth2_plan:
        depth2_reason = "no depth-1 archive was extracted"
    elif depth2_candidates == 0:
        depth2_reason = (
            "no readable type-0 row at or below the archive size limit in any "
            "extracted depth-1 archive"
        )
    elif len(sampler.nested_records) >= args.max_nested:
        depth2_reason = "nested archive cap reached after depth-1 extraction"
    else:
        depth2_reason = None

    for parent_record, selected, _ in depth2_plan:
        if len(sampler.nested_records) >= args.max_nested:
            break
        for row in selected[: args.max_depth2_per_parent]:
            if len(sampler.nested_records) >= args.max_nested:
                break
            if sampler.extracted_bytes + row["logical_size"] > args.max_bytes:
                sampler.log(f"stop depth2 {parent_record['parent_id']}: byte cap")
                break
            parent = Path(parent_record["output"])
            identifier = f"d2:{parent_record['parent_id']}:{row['row']}"
            output = (
                args.scratch_dir
                / "nested"
                / "d2"
                / safe_name(parent_record["parent_id"])
                / f"row-{row['row']:05d}.rpf"
            )
            label = {
                "sample": identifier,
                "depth": 2,
                "parent_archive": str(parent),
                "parent_row": row["row"],
                "top_relative": parent_record["top_relative"],
            }
            extraction = sampler.extract(parent, row, output, label)
            if not extraction["ok"]:
                sampler.log(f"extract failed {identifier}")
                continue
            digest = sha256_file(output)
            duplicate_of = digest_first.get(digest)
            digest_first.setdefault(digest, identifier)
            with output.open("rb") as handle:
                first8 = handle.read(8)
            manifest = sampler.manifest(output, output.with_suffix(".jsonl"))
            record = nested_record(
                2,
                parent,
                identifier,
                parent_record["top_relative"],
                row,
                output,
                extraction,
                manifest,
                digest,
                first8,
                duplicate_of,
            )
            sampler.nested_records.append(record)
            append_jsonl(args.scratch_dir / "nested.jsonl", record)
            sampler.log(
                f"d2 {identifier} {row['logical_size']} bytes profile={record['signature_class']}"
            )

    available_payloads, payload_stats = payload_candidates(
        sampler.nested_records,
        args.max_payloads_per_type,
        args.max_payload_bytes,
    )
    for type_id in sorted(available_payloads, key=lambda value: (value is None, value)):
        for row, parent_record in available_payloads[type_id]:
            if sampler.extracted_bytes + row["logical_size"] > args.max_bytes:
                sampler.log(f"stop payload type {type_id}: byte cap")
                break
            parent = Path(parent_record["output"])
            identifier = (
                f"payload:{type_id}:{parent_record['parent_id']}:{row['row']}"
            )
            output = (
                args.scratch_dir
                / "payloads"
                / f"type-{type_id}"
                / f"{safe_name(parent_record['parent_id'])}-row-{row['row']:05d}.bin"
            )
            label = {
                "sample": identifier,
                "depth": parent_record["depth"],
                "parent_archive": str(parent),
                "parent_row": row["row"],
                "top_relative": parent_record["top_relative"],
            }
            extraction = sampler.extract(parent, row, output, label)
            first8 = b""
            if extraction["ok"]:
                with output.open("rb") as handle:
                    first8 = handle.read(8)
            else:
                payload_stats[type_id]["failures"] += 1
            record = {
                "kind": "payload",
                "type_id": type_id,
                "parent_id": parent_record["parent_id"],
                "archive": str(parent),
                "top_relative": parent_record["top_relative"],
                "row": row["row"],
                "logical_size": row["logical_size"],
                "stored_size": row.get("stored_size"),
                "layout": row.get("layout"),
                "mode": row.get("mode"),
                "chunks": row.get("chunks"),
                "payload_transform": row.get("payload_transform"),
                "contents": row.get("contents"),
                "output": str(output),
                "first8": first8.hex(),
                "signature_class": classify_signature(first8) if first8 else "not-extracted",
                "extraction": extraction,
            }
            sampler.payload_records.append(record)
            append_jsonl(args.scratch_dir / "payloads.jsonl", record)
            sampler.log(
                f"payload type {type_id} row {row['row']} profile={record['signature_class']}"
            )

    summary = {
        "selection": selection,
        "manifest_duplicates": manifest_duplicates,
        "top_level": top_level,
        "nested": sampler.nested_records,
        "nested_aggregate": aggregate_nested(sampler.nested_records),
        "depth2": {
            "candidates": depth2_candidates,
            "extracted": sum(
                1 for record in sampler.nested_records if record["depth"] == 2
            ),
            "reason": depth2_reason,
        },
        "payloads": sampler.payload_records,
        "payload_aggregate": aggregate_payloads(sampler.payload_records, payload_stats),
        "failures": sampler.failures,
        "totals": {
            "nested_archives": len(sampler.nested_records),
            "nested_bytes": sum(record["logical_size"] for record in sampler.nested_records),
            "payloads": len(sampler.payload_records),
            "payload_bytes": sum(
                record["logical_size"]
                for record in sampler.payload_records
                if record["extraction"]["ok"]
            ),
            "extracted_bytes": sampler.extracted_bytes,
            "distinct_hashes": len(digest_first),
            "elapsed_seconds": round(time.time() - sampler.started, 3),
        },
    }
    write_json(args.scratch_dir / "summary.json", summary)
    write_report(args.scratch_dir / "report.md", summary)
    sampler.log(
        "done: nested={} payloads={} bytes={}".format(
            summary["totals"]["nested_archives"],
            summary["totals"]["payloads"],
            summary["totals"]["extracted_bytes"],
        )
    )
    sampler.log_handle.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
