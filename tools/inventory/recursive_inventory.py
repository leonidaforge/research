#!/usr/bin/env python3
"""Deterministic recursive RPF9 inventory sampler.

Reads top-level native manifests, extracts a deterministic sample of readable
type-0 rows, manifests the nested archives, and repeats to a bounded depth. It
then samples readable payloads per type. All inputs are opened read-only.

Every extracted artifact is content-addressed by SHA-256. A repeated row or a
duplicate archive reuses the cached artifact instead of extracting it again.
Outputs stay in the scratch directory. Nothing is written next to an input.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

RPF9_MAGIC = b"9FPR"
MAX_ARCHIVE_BYTES = 16 * 1024 * 1024
MAX_PAYLOAD_BYTES = 1 * 1024 * 1024
MAX_NESTED_ARCHIVES = 400
MAX_EXTRACTED_BYTES = 3 * 1024 * 1024 * 1024
MAX_ENUMERATED_ROWS = 0
MAX_DEPTH = 3
MAX_PAYLOADS_PER_TYPE = 4

DEFAULT_CAPS = {
    "max_depth": MAX_DEPTH,
    "max_nested_archives": MAX_NESTED_ARCHIVES,
    "max_extracted_bytes": MAX_EXTRACTED_BYTES,
    "max_enumerated_rows": MAX_ENUMERATED_ROWS,
    "max_archive_bytes": MAX_ARCHIVE_BYTES,
    "max_payload_bytes": MAX_PAYLOAD_BYTES,
    "samples_depth1": 24,
    "samples_depth2": 6,
    "samples_depth3": 3,
    "max_payloads_per_type": MAX_PAYLOADS_PER_TYPE,
}

# Signature classes from evidence/unknown-payloads and the documented formats.
# A class is a byte observation, not a format identity.
MAGIC_CLASSES = (
    (b"9FPR", "rpf9-magic"),
    (b"RBF0", "rbf0-magic"),
    (b"PSIN", "psin-magic"),
    (b"SGD5", "sgd5-magic"),
    (b"EDUP", "edup-magic"),
    (b"KB2j", "kb2j-magic"),
    (b"KB2n", "kb2n-magic"),
    (b"RDS5", "rds5-magic"),
    (b"PTFX", "ptfx-magic"),
)

# Classes the reference sampler reported before this expansion.
BASELINE_SIGNATURES = frozenset(
    {"rpf9-magic", "zlib-container-header", "zero-prefix", "unrecognized"}
)

SELECTION_RULE = {
    "top_level": (
        "For each top-level archive, order readable type-0 rows with logical "
        "size <= the archive size cap by (logical_size, row) and take "
        "quantile-spaced indices, including the smallest and largest. When "
        "the candidate count is at or below the per-parent limit, take all."
    ),
    "nested": (
        "For each unique extracted archive, apply the same quantile rule to "
        "its readable type-0 rows at the next depth. The per-depth limits are "
        "explicit caps, and archives are processed in discovery order."
    ),
    "payloads": (
        "For each distinct type across unique nested manifests, take up to "
        "the per-type limit of readable rows with logical size <= the payload "
        "size cap, ordered by (logical_size, archive hash, row)."
    ),
    "deduplication": (
        "Archives and payloads are keyed by SHA-256 of their extracted bytes. "
        "A duplicate is recorded against the first sample that produced the "
        "hash and is not expanded again."
    ),
}

DEPTH_LIMIT_ARG = {
    1: "samples_depth1",
    2: "samples_depth2",
    3: "samples_depth3",
}


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
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(temporary, path)


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
    for magic, label in MAGIC_CLASSES:
        if prefix.startswith(magic):
            return label
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


def _select_indices(count: int, limit: int) -> list[int]:
    if count <= 0 or limit <= 0:
        return []
    if count <= limit:
        return list(range(count))
    if limit == 1:
        return [0]
    return sorted({round(index * (count - 1) / (limit - 1)) for index in range(limit)})


def select_quantiles(rows: list[dict], max_size: int, limit: int) -> tuple[list[dict], int]:
    candidates = type0_rows(rows, max_size)
    selected = [candidates[index] for index in _select_indices(len(candidates), limit)]
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


def selection_gaps(rows: list[dict], max_size: int, limit: int) -> dict:
    type0 = [row for row in rows if row.get("kind") == "row" and row.get("type_id") == 0]
    readable = [row for row in type0 if is_readable(row)]
    within = [
        row
        for row in readable
        if isinstance(row.get("logical_size"), int) and row["logical_size"] <= max_size
    ]
    selected, _ = select_quantiles(rows, max_size, limit)
    return {
        "type0_rows": len(type0),
        "unreadable_type0": len(type0) - len(readable),
        "over_archive_size_cap": len(readable) - len(within),
        "readable_within_cap": len(within),
        "selected": len(selected),
        "not_selected_per_parent_limit": len(within) - len(selected),
    }


class ContentCache:
    """Content-addressed store for extracted archives and payloads."""

    def __init__(self, scratch: Path):
        self.root = scratch / "cache"
        self.archive_dir = self.root / "archives"
        self.payload_dir = self.root / "payloads"
        self.manifest_dir = self.root / "manifests"
        self.tmp_dir = self.root / "tmp"
        for directory in (self.archive_dir, self.payload_dir, self.manifest_dir, self.tmp_dir):
            directory.mkdir(parents=True, exist_ok=True)
        self.index_path = self.root / "index.json"
        self.entries: dict[str, dict] = {}
        if self.index_path.exists():
            try:
                self.entries = json.loads(self.index_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                self.entries = {}
        self.archive_bytes = sum(
            path.stat().st_size for path in self.archive_dir.glob("*.rpf")
        )
        self.payload_bytes = sum(
            path.stat().st_size for path in self.payload_dir.glob("*.bin")
        )

    @property
    def extracted_bytes(self) -> int:
        return self.archive_bytes + self.payload_bytes

    def entry_path(self, kind: str, digest: str) -> Path:
        suffix = "rpf" if kind == "archive" else "bin"
        directory = self.archive_dir if kind == "archive" else self.payload_dir
        return directory / f"{digest}.{suffix}"

    def save(self) -> None:
        write_json(self.index_path, self.entries)

    def lookup(self, kind: str, sample_key: str, expected_size: int) -> tuple[dict, Path] | None:
        entry = self.entries.get(f"{kind}:{sample_key}")
        if not entry:
            return None
        path = self.entry_path(kind, entry["sha256"])
        if path.exists() and path.stat().st_size == expected_size == entry.get("size"):
            return entry, path
        return None

    def temporary(self, kind: str, sample_key: str) -> Path:
        path = self.tmp_dir / f"{kind}-{safe_name(sample_key)}.part"
        if path.exists():
            path.unlink()
        return path

    def store(self, kind: str, sample_key: str, temporary: Path, expected_size: int) -> tuple[str, Path, bool]:
        digest = sha256_file(temporary)
        destination = self.entry_path(kind, digest)
        is_new = not destination.exists()
        if is_new:
            os.replace(temporary, destination)
        else:
            temporary.unlink()
        size = destination.stat().st_size
        self.entries[f"{kind}:{sample_key}"] = {"sha256": digest, "size": size}
        if is_new:
            if kind == "archive":
                self.archive_bytes += size
            else:
                self.payload_bytes += size
        self.save()
        return digest, destination, is_new

    def manifest_path(self, digest: str) -> Path:
        return self.manifest_dir / f"{digest}.jsonl"


def public_record(record: dict) -> dict:
    value = dict(record)
    value.pop("rows", None)
    return value


class Sampler:
    def __init__(self, lforge: Path, executable: Path, scratch: Path):
        self.lforge = lforge
        self.executable = executable
        self.scratch = scratch
        self.cache = ContentCache(scratch)
        self.records: list[dict] = []
        self.unique_records: dict[str, dict] = {}
        self.payload_records: list[dict] = []
        self.failures: list[dict] = []
        self.attempts = {"archive": 0, "payload": 0}
        self.successes = {"archive": 0, "payload": 0}
        self.extraction_failures = {"archive": 0, "payload": 0}
        self.enumerated_rows = 0
        self.row_limit_hit = False
        self.stop_flags: set[str] = set()
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

    def record_failure(self, failure: dict) -> None:
        self.failures.append(failure)
        append_jsonl(self.scratch / "failures.jsonl", failure)

    def budget_allows(self, kind: str, sample_key: str, expected_size: int, budget: int) -> bool:
        if self.cache.lookup(kind, sample_key, expected_size) is not None:
            return True
        return self.cache.extracted_bytes + expected_size <= budget

    def extract(
        self,
        kind: str,
        sample_key: str,
        parent: Path,
        row: dict,
        label: dict,
        budget: int,
    ) -> tuple[dict, str | None, Path | None, bool]:
        expected = row["logical_size"]
        self.attempts[kind] += 1
        cached = self.cache.lookup(kind, sample_key, expected)
        if cached:
            entry, path = cached
            self.successes[kind] += 1
            return (
                {
                    "ok": True,
                    "cached": True,
                    "exit": 0,
                    "actual_size": expected,
                    "expected_size": expected,
                },
                entry["sha256"],
                path,
                False,
            )
        if self.cache.extracted_bytes + expected > budget:
            self.extraction_failures[kind] += 1
            return (
                {
                    "ok": False,
                    "cached": False,
                    "exit": None,
                    "actual_size": None,
                    "expected_size": expected,
                    "reason": "byte budget",
                    "budget_blocked": True,
                },
                None,
                None,
                False,
            )
        temporary = self.cache.temporary(kind, sample_key)
        command = [
            str(self.lforge),
            "archive",
            "extract",
            str(parent),
            "--row",
            str(row["row"]),
            "--output",
            str(temporary),
            "--executable",
            str(self.executable),
        ]
        result = self.run(command)
        actual = temporary.stat().st_size if temporary.exists() else None
        if result.returncode == 0 and actual == expected:
            digest, destination, is_new = self.cache.store(kind, sample_key, temporary, expected)
            self.successes[kind] += 1
            return (
                {
                    "ok": True,
                    "cached": False,
                    "exit": 0,
                    "actual_size": actual,
                    "expected_size": expected,
                },
                digest,
                destination,
                is_new,
            )
        if temporary.exists():
            temporary.unlink()
        self.extraction_failures[kind] += 1
        reason = "size mismatch" if result.returncode == 0 else "nonzero exit"
        failure = dict(label)
        failure.update(
            {
                "kind": "failed_extraction",
                "failure_category": reason,
                "row_type_id": row.get("type_id"),
                "chunk_encoding": chunk_label(row),
                "compression_mode": row.get("mode"),
                "payload_transform": row.get("payload_transform"),
                "contents_state": row_state(row),
                "expected_size": expected,
                "actual_size": actual,
                "exit": result.returncode,
                "error": (result.stderr or result.stdout).strip()[:500],
            }
        )
        self.record_failure(failure)
        return (
            {
                "ok": False,
                "cached": False,
                "exit": result.returncode,
                "actual_size": actual,
                "expected_size": expected,
                "reason": reason,
            },
            None,
            None,
            False,
        )

    def manifest(
        self, digest: str, archive: Path, label: dict, max_rows: int
    ) -> tuple[dict, list[dict]]:
        path = self.cache.manifest_path(digest)
        cached = path.exists()
        if not cached:
            command = [
                str(self.lforge),
                "archive",
                "manifest",
                str(archive),
                "--format",
                "jsonl",
                "--output",
                str(path),
                "--overwrite",
                "--executable",
                str(self.executable),
            ]
            result = self.run(command)
            if result.returncode != 0:
                failure = dict(label)
                failure.update(
                    {
                        "kind": "failed_manifest",
                        "failure_category": "manifest command",
                        "exit": result.returncode,
                        "error": (result.stderr or result.stdout).strip()[:500],
                    }
                )
                self.record_failure(failure)
                return {
                    "ok": False,
                    "exit": result.returncode,
                    "error": failure["error"],
                    "provenance": "failed",
                }, []
        try:
            documents = read_jsonl(path)
        except (OSError, json.JSONDecodeError) as error:
            path.unlink(missing_ok=True)
            failure = dict(label)
            failure.update(
                {
                    "kind": "failed_manifest",
                    "failure_category": "manifest parse",
                    "exit": None,
                    "error": str(error)[:500],
                }
            )
            self.record_failure(failure)
            return {
                "ok": False,
                "exit": None,
                "error": str(error),
                "provenance": "failed",
            }, []
        if not documents or documents[0].get("kind") != "header":
            path.unlink(missing_ok=True)
            failure = dict(label)
            failure.update(
                {
                    "kind": "failed_manifest",
                    "failure_category": "missing header",
                    "exit": None,
                    "error": "manifest has no header record",
                }
            )
            self.record_failure(failure)
            return {
                "ok": False,
                "exit": None,
                "error": "missing manifest header",
                "provenance": "failed",
            }, []
        header = documents[0]
        rows = documents[1:]
        total_rows = len(rows)
        truncated = 0
        if max_rows:
            remaining = max(0, max_rows - self.enumerated_rows)
            if total_rows > remaining:
                truncated = total_rows - remaining
                rows = rows[:remaining]
                self.row_limit_hit = True
        self.enumerated_rows += len(rows)
        result = {
            "ok": True,
            "exit": 0,
            "authentication": header.get("authentication", {}),
            "rows": total_rows,
            "enumerated_rows": len(rows),
            "provenance": "cached" if cached else "rechecked",
            "types": type_histogram(rows),
        }
        if truncated:
            result["row_limit_truncated"] = truncated
        return result, rows


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
    rows: list[dict],
) -> dict:
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
        "rows": rows,
    }


def aggregate_nested(records: list[dict]) -> dict:
    by_depth = {}
    by_signature = {}
    by_type = {}
    auth = {}
    provenance = {}
    for record in records:
        depth = record["depth"]
        by_depth[depth] = by_depth.get(depth, 0) + 1
        signature = record["signature_class"]
        by_signature[signature] = by_signature.get(signature, 0) + 1
        manifest = record["manifest"]
        status = (
            manifest.get("authentication", {}).get("status")
            if manifest.get("ok")
            else "manifest-failed"
        )
        auth[status] = auth.get(status, 0) + 1
        source = manifest.get("provenance", "failed")
        provenance[source] = provenance.get(source, 0) + 1
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
    return {
        "by_depth": {str(key): value for key, value in sorted(by_depth.items())},
        "by_signature": by_signature,
        "by_type": [by_type[key] for key in sorted(by_type, key=lambda value: (value is None, value))],
        "authentication": auth,
        "auth_provenance": provenance,
    }


def payload_candidates(
    unique_records: list[dict], max_per_type: int, max_size: int
) -> tuple[dict[int, list[tuple[dict, dict]]], dict[int, dict]]:
    buckets: dict[int, list[tuple[dict, dict]]] = {}
    stats: dict[int, dict] = {}
    for record in unique_records:
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
                    "over_payload_size_cap": 0,
                    "chunk_encodings": {},
                    "selected": 0,
                    "failures": 0,
                },
            )
            entry["rows"] += 1
            encoding = chunk_label(row)
            entry["chunk_encodings"][encoding] = entry["chunk_encodings"].get(encoding, 0) + 1
            if not is_readable(row):
                continue
            entry["readable"] += 1
            if not isinstance(row.get("logical_size"), int) or row["logical_size"] > max_size:
                entry["over_payload_size_cap"] += 1
                continue
            entry["readable_within_limit"] += 1
            buckets.setdefault(type_id, []).append((row, record))
    selected = {}
    for type_id, candidates in buckets.items():
        ordered = sorted(
            candidates,
            key=lambda item: (
                item[0]["logical_size"],
                item[1]["sha256"],
                item[0]["row"],
            ),
        )
        selected[type_id] = ordered[:max_per_type]
        stats[type_id]["selected"] = len(selected[type_id])
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
                "unique": 0,
                "duplicates": 0,
                "signatures": {},
            },
        )
        entry["attempted"] += 1
        if record["extraction"]["ok"]:
            entry["succeeded"] += 1
            if record["duplicate_of"]:
                entry["duplicates"] += 1
            else:
                entry["unique"] += 1
        else:
            entry["failed"] += 1
        signature = record["signature_class"]
        entry["signatures"][signature] = entry["signatures"].get(signature, 0) + 1
        if record["duplicate_of"] is None:
            by_signature[signature] = by_signature.get(signature, 0) + 1
    for type_id in stats:
        if type_id not in by_type:
            by_type[type_id] = {
                "type_id": type_id,
                "attempted": 0,
                "succeeded": 0,
                "failed": 0,
                "unique": 0,
                "duplicates": 0,
                "signatures": {},
            }
    return {
        "by_type": [by_type[key] for key in sorted(by_type, key=lambda value: (value is None, value))],
        "by_signature": by_signature,
    }


def failure_summary(failures: list[dict]) -> list[dict]:
    buckets: dict[tuple, dict] = {}
    for failure in failures:
        key = (
            failure.get("kind"),
            failure.get("failure_category"),
            failure.get("depth"),
            failure.get("contents_state"),
            failure.get("chunk_encoding"),
        )
        bucket = buckets.setdefault(
            key,
            {
                "kind": failure.get("kind"),
                "category": failure.get("failure_category"),
                "depth": failure.get("depth"),
                "contents_state": failure.get("contents_state"),
                "chunk_encoding": failure.get("chunk_encoding"),
                "count": 0,
            },
        )
        bucket["count"] += 1
    return [buckets[key] for key in sorted(buckets, key=lambda value: tuple(str(item) for item in value))]


def write_report(path: Path, summary: dict) -> None:
    totals = summary["totals"]
    lines = ["# Expanded recursive inventory scratch report", ""]
    lines.append("Generated: {0}".format(time.strftime("%Y-%m-%dT%H:%M:%S")))
    lines.append("")
    lines.append(f"Run stop reason: {summary['stop_reason']}")
    lines.append("")
    lines.append("## Caps")
    lines.append("")
    for key, value in summary["selection"]["caps"].items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("## Totals")
    lines.append("")
    lines.append("| Measure | Value |")
    lines.append("| --- | ---: |")
    for key in (
        "archives_discovered",
        "archives_visited",
        "archives_enumerated",
        "top_level_archives",
        "top_level_authenticated",
        "top_level_rows",
        "unique_archives",
        "duplicate_archives",
        "max_depth_reached",
        "manifest_rows",
        "unique_rows",
        "rows_enumerated",
        "readable_rows",
        "unreadable_rows",
        "archive_extraction_attempts",
        "archive_extraction_successes",
        "archive_extraction_failures",
        "archive_bytes",
        "payload_attempts",
        "payload_successes",
        "payload_failures",
        "unique_payloads",
        "duplicate_payloads",
        "payload_bytes",
        "extracted_bytes",
    ):
        lines.append(f"| {key} | {totals.get(key)} |")
    lines.append("")
    lines.append("## Authentication")
    lines.append("")
    lines.append("| Status | Archives |")
    lines.append("| --- | ---: |")
    for key, value in sorted(summary["nested_aggregate"]["authentication"].items()):
        lines.append(f"| {key} | {value} |")
    lines.append("")
    lines.append("| Provenance | Archives |")
    lines.append("| --- | ---: |")
    for key, value in sorted(summary["nested_aggregate"]["auth_provenance"].items()):
        lines.append(f"| {key} | {value} |")
    lines.append("")
    lines.append("")
    lines.append("## Depth progress")
    lines.append("")
    lines.append("| Depth | Parents | Candidates | Selected | Attempts | Unique | Duplicates | Failures | Stop reason |")
    lines.append("| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |")
    for item in summary["depths"]:
        lines.append(
            "| {depth} | {parents} | {candidates} | {selected} | {attempts} | {unique} | "
            "{duplicates} | {failures} | {stop_reason} |".format(**item)
        )
    lines.append("")
    lines.append("## Top-level archives")
    lines.append("")
    lines.append("| Archive | Rows | Type-0 | Readable within cap | Selected | Extracted | Skipped |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: | --- |")
    for item in summary["top_level"]:
        skipped = item["skip_reason"] or (
            f"{item['gaps']['not_selected_per_parent_limit']} per-parent limit"
            if item["gaps"]["not_selected_per_parent_limit"]
            else ""
        )
        lines.append(
            "| {relative} | {rows} | {type0} | {within} | {selected} | {nested} | {skipped} |".format(
                relative=item["relative"],
                rows=item["rows"],
                type0=item["gaps"]["type0_rows"],
                within=item["gaps"]["readable_within_cap"],
                selected=item["gaps"]["selected"],
                nested=item["nested"],
                skipped=skipped or "-",
            )
        )
    lines.append("")
    lines.append("## Unique nested archives")
    lines.append("")
    lines.append("| Depth | Parent row | Size | SHA-256 | Signature | Auth | Provenance | Rows | Duplicate of |")
    lines.append("| ---: | ---: | ---: | --- | --- | --- | --- | ---: | --- |")
    for record in summary["unique_archives"]:
        lines.append(
            "| {depth} | {parent_row} | {logical_size} | `{sha256}` | {signature_class} | "
            "{auth} | {provenance} | {rows} | {duplicate_of} |".format(
                depth=record["depth"],
                parent_row=record["parent_row"],
                logical_size=record["logical_size"],
                sha256=record["sha256"],
                signature_class=record["signature_class"],
                auth=record["manifest"].get("authentication", {}).get("status", "failed"),
                provenance=record["manifest"].get("provenance", "failed"),
                rows=record["manifest"].get("rows", 0),
                duplicate_of=record["duplicate_of"] or "",
            )
        )
    lines.append("")
    lines.append("## Duplicate extractions")
    lines.append("")
    if summary["duplicates"]:
        lines.append("| Depth | Sample | SHA-256 | Duplicate of |")
        lines.append("| ---: | --- | --- | --- |")
        for record in summary["duplicates"]:
            lines.append(
                "| {depth} | {parent_id} | `{sha256}` | {duplicate_of} |".format(**record)
            )
    else:
        lines.append("No duplicate archive content was found.")
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
    lines.append("| Type | Attempted | Succeeded | Failed | Unique | Duplicates | Signatures |")
    lines.append("| ---: | ---: | ---: | ---: | ---: | ---: | --- |")
    for item in summary["payload_aggregate"]["by_type"]:
        signatures = ", ".join(
            f"{key}: {value}" for key, value in sorted(item["signatures"].items())
        )
        values = dict(item)
        values["signatures"] = signatures or "-"
        lines.append(
            "| {type_id} | {attempted} | {succeeded} | {failed} | {unique} | {duplicates} | "
            "{signatures} |".format(**values)
        )
    lines.append("")
    lines.append("## Payload signatures")
    lines.append("")
    lines.append("| Class | Unique payloads |")
    lines.append("| --- | ---: |")
    for key, value in sorted(summary["payload_aggregate"]["by_signature"].items()):
        lines.append(f"| {key} | {value} |")
    lines.append("")
    lines.append("## Gaps")
    lines.append("")
    if summary["gaps"]:
        lines.append("| Gap | Count |")
        lines.append("| --- | ---: |")
        for key, value in sorted(summary["gaps"].items()):
            lines.append(f"| {key} | {value} |")
    else:
        lines.append("No gap was recorded.")
    lines.append("")
    lines.append("## Archive extraction failures")
    lines.append("")
    if summary["failure_summary"]:
        lines.append("| Kind | Category | Depth | Contents state | Chunk encoding | Count |")
        lines.append("| --- | --- | ---: | --- | --- | ---: |")
        for item in summary["failure_summary"]:
            lines.append(
                "| {kind} | {category} | {depth} | {contents_state} | {chunk_encoding} | "
                "{count} |".format(**item)
            )
    else:
        lines.append("No extraction or manifest failure.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def caps_from_args(args: argparse.Namespace) -> dict:
    dests = {
        "max_nested_archives": "max_nested",
        "max_extracted_bytes": "max_bytes",
        "max_enumerated_rows": "max_rows",
    }
    return {
        name: getattr(args, dests.get(name, name))
        for name in DEFAULT_CAPS
    }


def build_top_level(manifests: list[dict], caps: dict) -> tuple[list[dict], list[tuple]]:
    top_level = []
    top_plan = []
    for item in manifests:
        archive = Path(item["header"]["archive"])
        relative = str(item["header"].get("relative") or archive.name)
        selected, _ = select_quantiles(
            item["rows"], caps["max_archive_bytes"], caps["samples_depth1"]
        )
        gaps = selection_gaps(
            item["rows"], caps["max_archive_bytes"], caps["samples_depth1"]
        )
        top_level.append(
            {
                "archive": str(archive),
                "relative": relative,
                "rows": len([row for row in item["rows"] if row.get("kind") == "row"]),
                "nested": 0,
                "gaps": gaps,
                "skip_reason": None
                if selected
                else (
                    "no readable type-0 row"
                    if gaps["type0_rows"] == 0 or gaps["unreadable_type0"] == gaps["type0_rows"]
                    else "no readable type-0 row within the archive size cap"
                ),
            }
        )
        top_plan.append((item, archive, relative, selected))
    return top_level, top_plan


def execute(
    args: argparse.Namespace,
    manifests: list[dict],
    manifest_duplicates: list[dict],
    sampler: Sampler,
) -> dict:
    caps = caps_from_args(args)
    selection = dict(SELECTION_RULE)
    selection["caps"] = caps
    top_level, top_plan = build_top_level(manifests, caps)

    gaps: dict[str, int] = {}

    def add_gap(name: str, count: int = 1) -> None:
        if count:
            gaps[name] = gaps.get(name, 0) + count

    depth_reports = []
    stopped = False
    for depth in range(1, caps["max_depth"] + 1):
        if stopped:
            break
        per_parent = caps[DEPTH_LIMIT_ARG[depth]]
        if depth == 1:
            parents = [
                {
                    "rows": item["rows"],
                    "parent": archive,
                    "parent_id": relative,
                    "top_relative": relative,
                    "sha256": None,
                }
                for item, archive, relative, _ in top_plan
            ]
        else:
            parents = [
                record
                for record in sorted(
                    sampler.unique_records.values(),
                    key=lambda value: (value["top_relative"], value["parent_id"], value["sha256"]),
                )
                if record["depth"] == depth - 1 and record["manifest"].get("ok")
            ]
        plan = []
        candidates = 0
        selected_total = 0
        transform_type0 = 0
        for parent in parents:
            selected, candidate_count = select_quantiles(
                parent["rows"], caps["max_archive_bytes"], per_parent
            )
            candidates += candidate_count
            selected_total += len(selected)
            transform_type0 += sum(
                1
                for candidate in parent["rows"]
                if candidate.get("kind") == "row"
                and candidate.get("type_id") == 0
                and not is_readable(candidate)
                and row_state(candidate) == "unsupported_transform"
            )
            parent_gaps = selection_gaps(
                parent["rows"], caps["max_archive_bytes"], per_parent
            )
            add_gap("type0_unreadable", parent_gaps["unreadable_type0"])
            add_gap("type0_over_archive_size_cap", parent_gaps["over_archive_size_cap"])
            add_gap(
                "type0_not_selected_per_parent_limit",
                parent_gaps["not_selected_per_parent_limit"],
            )
            plan.append((parent, selected))

        attempts = 0
        successes = 0
        failures = 0
        unique_added = 0
        duplicate_added = 0
        stop_reason = None
        for parent, selected in plan:
            if stopped:
                add_gap("parents_not_visited_cap", 1)
                continue
            for row in selected:
                if sampler.row_limit_hit:
                    stop_reason = "row limit"
                    sampler.stop_flags.add("row limit")
                    add_gap("row_limit_stop")
                    stopped = True
                    break
                if len(sampler.unique_records) >= caps["max_nested_archives"]:
                    stop_reason = "archive limit"
                    sampler.stop_flags.add("archive limit")
                    add_gap("nested_archive_cap")
                    stopped = True
                    break
                if depth == 1:
                    sample_key = f"d1:{parent['parent_id']}:{row['row']}"
                    parent_path = parent["parent"]
                else:
                    sample_key = f"d{depth}:{parent['sha256']}:{row['row']}"
                    parent_path = Path(parent["output"])
                if not sampler.budget_allows(
                    "archive", sample_key, row["logical_size"], caps["max_extracted_bytes"]
                ):
                    stop_reason = "byte budget"
                    sampler.stop_flags.add("byte budget")
                    add_gap("extracted_byte_cap")
                    stopped = True
                    break
                attempts += 1
                label = {
                    "sample": sample_key,
                    "depth": depth,
                    "parent_archive": str(parent_path),
                    "parent_row": row["row"],
                    "top_relative": parent["top_relative"],
                }
                extraction, digest, output, _ = sampler.extract(
                    "archive",
                    sample_key,
                    parent_path,
                    row,
                    label,
                    caps["max_extracted_bytes"],
                )
                if not extraction["ok"]:
                    failures += 1
                    add_gap("archive_extraction_failure")
                    if extraction.get("budget_blocked"):
                        stop_reason = "byte budget"
                        sampler.stop_flags.add("byte budget")
                        add_gap("extracted_byte_cap")
                        stopped = True
                        break
                    sampler.log(f"extract failed {sample_key}")
                    continue
                successes += 1
                duplicate_of = None
                if digest in sampler.unique_records:
                    duplicate_of = sampler.unique_records[digest]["parent_id"]
                first8 = b""
                with output.open("rb") as handle:
                    first8 = handle.read(8)
                if duplicate_of:
                    manifest = dict(sampler.unique_records[digest]["manifest"])
                    manifest["provenance"] = "inherited"
                    rows = []
                    duplicate_added += 1
                    add_gap("duplicate_archive_content")
                else:
                    manifest, rows = sampler.manifest(
                        digest, output, label, caps["max_enumerated_rows"]
                    )
                    unique_added += 1
                    if not manifest.get("ok"):
                        add_gap("archive_manifest_failure")
                record = nested_record(
                    depth,
                    parent_path,
                    sample_key,
                    parent["top_relative"],
                    row,
                    output,
                    extraction,
                    manifest,
                    digest,
                    first8,
                    duplicate_of,
                    rows,
                )
                sampler.records.append(record)
                append_jsonl(args.scratch_dir / "archives.jsonl", public_record(record))
                if not duplicate_of:
                    sampler.unique_records[digest] = record
                if depth == 1:
                    top_entry = next(
                        entry for entry in top_level if entry["relative"] == parent["parent_id"]
                    )
                    top_entry["nested"] += 1
                sampler.log(
                    f"d{depth} {sample_key} {row['logical_size']} bytes "
                    f"profile={record['signature_class']}"
                    + (" duplicate" if duplicate_of else "")
                )
                if sampler.row_limit_hit:
                    stop_reason = "row limit"
                    sampler.stop_flags.add("row limit")
                    add_gap("row_limit_stop")
                    stopped = True
                    break
        if selected_total == 0:
            if transform_type0:
                stop_reason = "transform"
                sampler.stop_flags.add("transform")
            else:
                stop_reason = "no readable type-0 row within the archive size cap"
        depth_reports.append(
            {
                "depth": depth,
                "parents": len(parents),
                "candidates": candidates,
                "selected": selected_total,
                "attempts": attempts,
                "unique": unique_added,
                "duplicates": duplicate_added,
                "failures": failures,
                "stop_reason": stop_reason or "sampled",
            }
        )
        if not parents:
            stop_reason = "no parent archive at the previous depth"
            depth_reports[-1]["stop_reason"] = stop_reason
            break

    unique_records = sorted(
        sampler.unique_records.values(), key=lambda value: (value["depth"], value["sha256"])
    )

    # Archives beyond the depth cap were not expanded; count the type-0 rows there.
    if unique_records:
        deepest = max(record["depth"] for record in unique_records)
        if deepest >= caps["max_depth"]:
            for record in unique_records:
                if record["depth"] == caps["max_depth"] and record["manifest"].get("ok"):
                    _, count = select_quantiles(
                        record["rows"],
                        caps["max_archive_bytes"],
                        caps["max_nested_archives"],
                    )
                    add_gap("type0_beyond_depth_cap", count)

    available_payloads, payload_stats = payload_candidates(
        unique_records,
        caps["max_payloads_per_type"],
        caps["max_payload_bytes"],
    )
    payload_duplicates: dict[str, str] = {}
    payload_budget_stopped = False
    for type_id in sorted(available_payloads, key=lambda value: (value is None, value)):
        if payload_budget_stopped:
            break
        for row, parent_record in available_payloads[type_id]:
            sample_key = f"{parent_record['sha256']}:{row['row']}"
            if not sampler.budget_allows(
                "payload", sample_key, row["logical_size"], caps["max_extracted_bytes"]
            ):
                add_gap("payload_extracted_byte_cap")
                sampler.stop_flags.add("byte budget")
                payload_budget_stopped = True
                break
            label = {
                "sample": f"payload:{type_id}:{sample_key}",
                "depth": parent_record["depth"] + 1,
                "parent_archive": parent_record["output"],
                "parent_row": row["row"],
                "top_relative": parent_record["top_relative"],
            }
            extraction, digest, output, _ = sampler.extract(
                "payload",
                sample_key,
                Path(parent_record["output"]),
                row,
                label,
                caps["max_extracted_bytes"],
            )
            duplicate_of = None
            if extraction["ok"]:
                if digest in payload_duplicates:
                    duplicate_of = payload_duplicates[digest]
                else:
                    payload_duplicates[digest] = sample_key
            first8 = b""
            if extraction["ok"] and output is not None:
                with output.open("rb") as handle:
                    first8 = handle.read(8)
            record = {
                "kind": "payload",
                "type_id": type_id,
                "sample": sample_key,
                "parent_sha256": parent_record["sha256"],
                "parent_id": parent_record["parent_id"],
                "archive": parent_record["output"],
                "top_relative": parent_record["top_relative"],
                "row": row["row"],
                "logical_size": row["logical_size"],
                "stored_size": row.get("stored_size"),
                "layout": row.get("layout"),
                "mode": row.get("mode"),
                "chunks": row.get("chunks"),
                "payload_transform": row.get("payload_transform"),
                "contents": row.get("contents"),
                "output": str(output) if output else None,
                "sha256": digest,
                "first8": first8.hex(),
                "signature_class": classify_signature(first8)
                if first8
                else "not-extracted",
                "duplicate_of": duplicate_of,
                "extraction": extraction,
            }
            sampler.payload_records.append(record)
            append_jsonl(args.scratch_dir / "payloads.jsonl", record)
            if extraction["ok"]:
                sampler.log(
                    f"payload type {type_id} {sample_key} "
                    f"profile={record['signature_class']}"
                    + (" duplicate" if duplicate_of else "")
                )
            else:
                add_gap("payload_extraction_failure")
                if extraction.get("budget_blocked"):
                    sampler.stop_flags.add("byte budget")
                    payload_budget_stopped = True
                    break

    for record in payload_stats.values():
        if record["over_payload_size_cap"]:
            add_gap("payload_rows_over_size_cap", record["over_payload_size_cap"])
        if record["rows"] > record["readable"]:
            add_gap("payload_rows_unreadable", record["rows"] - record["readable"])
        add_gap(
            "payload_rows_not_selected_per_type_limit",
            record["readable_within_limit"] - record["selected"],
        )

    for item in top_level:
        unprocessed = item["gaps"]["selected"] - item["nested"]
        add_gap("top_level_selected_not_extracted", unprocessed)

    unique_rows = 0
    readable_rows = 0
    unreadable_rows = 0
    manifest_rows = 0
    for record in unique_records:
        if not record["manifest"].get("ok"):
            continue
        manifest_rows += record["manifest"].get("rows", 0)
        for row in record["rows"]:
            if row.get("kind") != "row":
                continue
            unique_rows += 1
            if is_readable(row):
                readable_rows += 1
            else:
                unreadable_rows += 1

    if sampler.row_limit_hit:
        run_stop_reason = "row limit"
    elif "archive limit" in sampler.stop_flags:
        run_stop_reason = "archive limit"
    elif "byte budget" in sampler.stop_flags:
        run_stop_reason = "byte budget"
    elif "transform" in sampler.stop_flags:
        run_stop_reason = "transform"
    elif gaps.get("type0_beyond_depth_cap"):
        run_stop_reason = "depth"
    elif sampler.extraction_failures["archive"] and not sampler.successes["archive"]:
        run_stop_reason = "failure"
    else:
        run_stop_reason = "complete"

    payload_signatures = aggregate_payloads(
        sampler.payload_records, payload_stats
    )["by_signature"]
    new_signatures = sorted(
        signature
        for signature in payload_signatures
        if signature not in BASELINE_SIGNATURES and signature != "not-extracted"
    )
    duplicates = [
        {
            "depth": record["depth"],
            "parent_id": record["parent_id"],
            "sha256": record["sha256"],
            "duplicate_of": record["duplicate_of"],
        }
        for record in sampler.records
        if record["duplicate_of"]
    ]
    nested_aggregate = aggregate_nested(unique_records)
    provenance: dict[str, int] = {}
    for record in sampler.records:
        source = record["manifest"].get("provenance", "failed")
        provenance[source] = provenance.get(source, 0) + 1
    nested_aggregate["auth_provenance"] = provenance
    top_level_authenticated = sum(
        1
        for item in manifests
        if item["header"].get("authentication", {}).get("status") == "authenticated"
    )

    return {
        "selection": selection,
        "manifest_duplicates": manifest_duplicates,
        "top_level": top_level,
        "depths": depth_reports,
        "stop_reason": run_stop_reason,
        "unique_archives": [public_record(record) for record in unique_records],
        "duplicates": duplicates,
        "nested_aggregate": nested_aggregate,
        "payloads": sampler.payload_records,
        "payload_aggregate": aggregate_payloads(sampler.payload_records, payload_stats),
        "payload_types": [payload_stats[key] for key in sorted(payload_stats, key=lambda value: (value is None, value))],
        "new_payload_signatures": new_signatures,
        "failures": sampler.failures,
        "failure_summary": failure_summary(sampler.failures),
        "gaps": gaps,
        "totals": {
            "archives_discovered": len(manifests),
            "archives_visited": len(manifests) + sum(
                1 for record in unique_records if record["manifest"].get("ok")
            ),
            "archives_enumerated": sum(
                1 for record in unique_records if record["manifest"].get("ok")
            ),
            "top_level_archives": len(manifests),
            "top_level_authenticated": top_level_authenticated,
            "top_level_rows": sum(item["rows"] for item in top_level),
            "unique_archives": len(unique_records),
            "duplicate_archives": len(duplicates),
            "max_depth_reached": max(
                (record["depth"] for record in unique_records), default=0
            ),
            "manifest_rows": manifest_rows,
            "unique_rows": unique_rows,
            "rows_enumerated": sampler.enumerated_rows,
            "readable_rows": readable_rows,
            "unreadable_rows": unreadable_rows,
            "archive_extraction_attempts": sampler.attempts["archive"],
            "archive_extraction_successes": sampler.successes["archive"],
            "archive_extraction_failures": sampler.extraction_failures["archive"],
            "archive_bytes": sampler.cache.archive_bytes,
            "payload_attempts": sampler.attempts["payload"],
            "payload_successes": sampler.successes["payload"],
            "payload_failures": sampler.extraction_failures["payload"],
            "unique_payloads": len(
                {record["sha256"] for record in sampler.payload_records if record["sha256"]}
            ),
            "duplicate_payloads": len(
                [record for record in sampler.payload_records if record["duplicate_of"]]
            ),
            "payload_bytes": sampler.cache.payload_bytes,
            "extracted_bytes": sampler.cache.extracted_bytes,
            "elapsed_seconds": round(time.time() - sampler.started, 3),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory-dir", required=True, type=Path)
    parser.add_argument("--game-dir", required=True, type=Path)
    parser.add_argument("--scratch-dir", required=True, type=Path)
    parser.add_argument("--lforge", required=True, type=Path)
    parser.add_argument("--executable", required=True, type=Path)
    parser.add_argument("--max-depth", type=int, default=DEFAULT_CAPS["max_depth"])
    parser.add_argument(
        "--max-nested", type=int, default=DEFAULT_CAPS["max_nested_archives"]
    )
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_CAPS["max_extracted_bytes"])
    parser.add_argument(
        "--max-rows", type=int, default=DEFAULT_CAPS["max_enumerated_rows"]
    )
    parser.add_argument(
        "--max-archive-bytes", type=int, default=DEFAULT_CAPS["max_archive_bytes"]
    )
    parser.add_argument(
        "--max-payload-bytes", type=int, default=DEFAULT_CAPS["max_payload_bytes"]
    )
    parser.add_argument("--samples-depth1", type=int, default=DEFAULT_CAPS["samples_depth1"])
    parser.add_argument("--samples-depth2", type=int, default=DEFAULT_CAPS["samples_depth2"])
    parser.add_argument("--samples-depth3", type=int, default=DEFAULT_CAPS["samples_depth3"])
    parser.add_argument(
        "--max-payloads-per-type",
        type=int,
        default=DEFAULT_CAPS["max_payloads_per_type"],
    )
    parser.add_argument(
        "--plan-only",
        action="store_true",
        help="write the deterministic depth-1 selection without running extraction",
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
    if args.max_depth < 1 or args.max_depth > 3:
        raise SystemExit("max depth MUST be between 1 and 3")
    ensure_outside_inputs(args.scratch_dir, args.game_dir, args.inventory_dir)
    args.scratch_dir.mkdir(parents=True, exist_ok=True)

    manifests, manifest_duplicates = discover_manifests(args.inventory_dir)
    sampler = Sampler(args.lforge, args.executable, args.scratch_dir)
    log_path = args.scratch_dir / "run.log"
    sampler.log_handle = log_path.open("a", encoding="utf-8", newline="\n")
    sampler.log(f"manifests: {len(manifests)}")

    if args.plan_only:
        caps = caps_from_args(args)
        selection = dict(SELECTION_RULE)
        selection["caps"] = caps
        top_level, top_plan = build_top_level(manifests, caps)
        plan = {
            "selection": selection,
            "top_level": top_level,
            "depth1": [
                {
                    "archive": str(archive),
                    "rows": [row["row"] for row in selected],
                    "sizes": [row["logical_size"] for row in selected],
                }
                for _, archive, _, selected in top_plan
            ],
        }
        write_json(args.scratch_dir / "plan.json", plan)
        sampler.log("plan-only: no extraction run")
        sampler.log_handle.close()
        return 0

    summary = execute(args, manifests, manifest_duplicates, sampler)
    write_json(args.scratch_dir / "summary.json", summary)
    write_report(args.scratch_dir / "report.md", summary)
    sampler.log(
        "done: stop={} unique_archives={} unique_rows={} max_depth={} extracted_bytes={}".format(
            summary["stop_reason"],
            summary["totals"]["unique_archives"],
            summary["totals"]["unique_rows"],
            summary["totals"]["max_depth_reached"],
            summary["totals"]["extracted_bytes"],
        )
    )
    sampler.log_handle.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
