"""Full census of the readable type-0 row population.

Every readable type-0 row of the supplied top-level manifests is attempted
once. The row is extracted, hashed, opened as an RPF9 archive, and its header
and nested rows are recorded. Progress is written atomically after each batch
and the run resumes from the completed row set.

Stored rows above the CLI output limit are copied from their payload offset
instead of going through the CLI. The copy is only used for rows whose location
record says mode 0, no chunk table, no payload transform and equal stored and
logical sizes.

All reads are read-only. Extracted bytes are temporary and are removed after
the manifest is read unless --keep-archives is given.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import recursive_inventory as inventory

SCHEMA = "leonida-forge.inventory-census/1"
ROW_SCHEMA = "leonida-forge.inventory-census-row/1"
HEADER_BYTES = 0x40
MAX_MANIFEST_ROWS = 10_000_000
MAX_MANIFEST_BYTES = 2 * 1024 * 1024 * 1024
COPY_STEP = 8 * 1024 * 1024
CLI_OUTPUT_LIMIT = 512 * 1024 * 1024

FAILURE_STAGES = (
    "missing input",
    "metadata readability",
    "unsupported transformation",
    "framing error",
    "unsupported storage class",
    "corrupt compressed stream",
    "incomplete reconstruction",
    "operational limit",
    "unclassified",
)

HEADER_FIELDS = (
    ("magic", 0x00, 4, "u32"),
    ("metadata_size", 0x04, 4, "u32"),
    ("primary_size", 0x08, 4, "u32"),
    ("trailer_length", 0x0C, 4, "u32"),
    ("unknown_0x10", 0x10, 8, "u64"),
    ("unknown_0x18", 0x18, 2, "u16"),
    ("a_records", 0x1A, 2, "u16"),
    ("b_bytes", 0x1C, 4, "u32"),
    ("c_columns", 0x20, 2, "u16"),
    ("d_secondary_columns", 0x22, 2, "u16"),
    ("e_rows", 0x24, 4, "u32"),
    ("fingerprint", 0x28, 4, "u32"),
    ("f_index_width", 0x2C, 1, "u8"),
    ("g_flags", 0x2D, 1, "u8"),
    ("cipher_selector", 0x2E, 1, "u8"),
    ("unknown_0x2F", 0x2F, 1, "u8"),
    ("b_trailer_length", 0x30, 4, "u32"),
    ("unknown_0x34", 0x34, 4, "u32"),
    ("unknown_0x38", 0x38, 4, "u32"),
    ("unknown_0x3C", 0x3C, 4, "u32"),
)


class CensusError(Exception):
    """A refusal or an invariant violation, not a row-level failure."""


class CopyRangeError(CensusError):
    """A stored range that does not fit the archive the manifest describes."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            block = handle.read(COPY_STEP)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def key_for(relative: str, row: int) -> str:
    return f"{relative}:{row}"


def row_key(row: dict) -> str:
    return key_for(row["relative"], int(row["row"]))


def is_readable(row: dict) -> bool:
    contents = row.get("contents")
    return isinstance(contents, dict) and contents.get("readable") is True


def population(manifests: list[dict]) -> tuple[list[dict], dict]:
    """Readable type-0 rows, deterministically ordered, with accounting."""
    selected = []
    type0 = 0
    unreadable_type0 = 0
    missing_size = 0
    for item in manifests:
        relative = item["header"].get("relative") or Path(str(item["header"]["archive"])).name
        archive = item["header"]["archive"]
        for row in item["rows"]:
            if row.get("kind") != "row" or row.get("type_id") != 0:
                continue
            type0 += 1
            if not is_readable(row):
                unreadable_type0 += 1
                continue
            size = row.get("logical_size")
            if not isinstance(size, int) or size < 0:
                missing_size += 1
                continue
            selected.append(
                {
                    "relative": relative,
                    "archive": archive,
                    "row": int(row["row"]),
                    "logical_size": size,
                    "stored_size": row.get("stored_size"),
                    "layout": row.get("layout"),
                    "mode": row.get("mode"),
                    "chunks": row.get("chunks"),
                    "payload_transform": row.get("payload_transform"),
                    "payload_offset": row.get("payload_offset"),
                    "source_row": row,
                }
            )
    selected.sort(key=lambda item: (str(item["relative"]).lower(), item["row"]))
    accounting = {
        "type0_rows": type0,
        "unreadable_type0": unreadable_type0,
        "type0_without_integer_size": missing_size,
        "declared_total": len(selected),
    }
    return selected, accounting


def fingerprint(row: dict) -> str:
    fields = (
        row.get("type_id"),
        row.get("layout"),
        row.get("mode"),
        inventory.chunk_label(row),
        row.get("payload_transform"),
        row.get("read_source"),
    )
    text = json.dumps(fields, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def read_header(path: Path) -> dict:
    with path.open("rb") as handle:
        data = handle.read(HEADER_BYTES)
    if len(data) != HEADER_BYTES:
        raise CensusError(f"archive {path.name} is shorter than the 0x40-byte header")
    values = {}
    for name, offset, width, kind in HEADER_FIELDS:
        values[name] = int.from_bytes(data[offset : offset + width], "little")
    values["magic_bytes"] = data[:4].hex()
    values["file_size"] = path.stat().st_size
    return values


def copy_stored_row(
    archive: Path, offset: int, length: int, output: Path, file_size: int
) -> None:
    if offset < 0 or length < 0 or offset + length > file_size:
        raise CopyRangeError(
            f"stored range {offset}+{length} is outside the {file_size}-byte archive"
        )
    partial = output.with_name(output.name + ".part")
    written = 0
    with archive.open("rb") as source, partial.open("wb") as sink:
        source.seek(offset)
        while written < length:
            block = source.read(min(COPY_STEP, length - written))
            if not block:
                break
            sink.write(block)
            written += len(block)
        sink.flush()
        os.fsync(sink.fileno())
    if written != length:
        partial.unlink(missing_ok=True)
        raise CensusError(f"stored range ended after {written} of {length} bytes")
    os.replace(partial, output)


def ensure_output_dir(output: Path, inventory_dir: Path) -> None:
    output = Path(output).resolve()
    inventory_dir = Path(inventory_dir).resolve()
    if output == inventory_dir or inventory_dir in output.parents:
        raise CensusError("the output directory MUST NOT lie inside the inventory directory")
    if output.exists() and output.is_file():
        for candidate in Path(inventory_dir).glob("*"):
            if candidate.is_file() and os.path.samefile(output, candidate):
                raise CensusError("the output path resolves to an inventory input")


def classify_failure(text: str, exit_code: int | None, actual: int | None, expected: int) -> str:
    lowered = (text or "").lower()
    if "no such file" in lowered or "cannot find the file" in lowered or "not found" in lowered:
        return "missing input"
    if "payload transform" in lowered or ("transform" in lowered and "unsupported" in lowered):
        return "unsupported transformation"
    if "output limit" in lowered:
        return "operational limit"
    if "table of contents" in lowered or "authenticat" in lowered or "signature" in lowered:
        return "metadata readability"
    if "chunk" in lowered or "encoding" in lowered or "prefix" in lowered or "framing" in lowered:
        return "framing error"
    if any(word in lowered for word in ("deflate", "zlib", "inflate", "checksum", "adler")):
        return "corrupt compressed stream"
    if "storage" in lowered or "unsupported mode" in lowered or "mode " in lowered:
        return "unsupported storage class"
    if exit_code == 0 and actual is not None and actual != expected:
        return "incomplete reconstruction"
    return "unclassified"


class Runner:
    def __init__(self, lforge: Path, executable: Path, timeout: int):
        self.lforge = Path(lforge)
        self.executable = Path(executable)
        self.timeout = timeout

    def __call__(self, command: list[str]) -> subprocess.CompletedProcess:
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=self.timeout,
        )


class Census:
    def __init__(
        self,
        manifests: list[dict],
        output_dir: Path,
        runner: Runner,
        batch_size: int,
        keep_archives: bool = False,
        cli_output_limit: int = CLI_OUTPUT_LIMIT,
    ):
        self.rows, self.accounting = population(manifests)
        self.output_dir = Path(output_dir)
        self.runner = runner
        self.batch_size = batch_size
        self.keep_archives = keep_archives
        self.cli_output_limit = cli_output_limit
        self.root = self.output_dir
        self.tmp_dir = self.root / "tmp"
        self.manifest_dir = self.root / "manifests"
        self.archive_dir = self.root / "archives"
        for directory in (self.tmp_dir, self.manifest_dir):
            directory.mkdir(parents=True, exist_ok=True)
        if keep_archives:
            self.archive_dir.mkdir(parents=True, exist_ok=True)
        self.rows_path = self.root / "rows.jsonl"
        self.state_path = self.root / "state.json"
        self.failures_path = self.root / "failures.jsonl"
        self.log_path = self.root / "run.log"
        self.log_handle = None

    def log(self, message: str) -> None:
        line = f"{time.strftime('%H:%M:%S')} {message}"
        print(line, flush=True)
        if self.log_handle is not None:
            self.log_handle.write(line + "\n")
            self.log_handle.flush()

    def population_fingerprint(self) -> str:
        keys = "\n".join(row_key(row) for row in self.rows)
        return hashlib.sha256(keys.encode("utf-8")).hexdigest()

    def load_completed(self) -> dict[str, dict]:
        completed = {}
        if not self.rows_path.exists():
            return completed
        with self.rows_path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as error:
                    raise CensusError(
                        f"rows.jsonl line {line_number} is not JSON: {error}"
                    )
                if record.get("schema") != ROW_SCHEMA:
                    raise CensusError(f"rows.jsonl line {line_number} has an unknown schema")
                completed[row_key(record)] = record
        return completed

    def write_state(self, completed: dict[str, dict], stage: str) -> None:
        failures = Counter()
        succ = 0
        for record in completed.values():
            if record["attempt"]["ok"]:
                succ += 1
            else:
                failures[record["attempt"]["stage"]] += 1
        state = {
            "schema": SCHEMA,
            "stage": stage,
            "declared_total": self.accounting["declared_total"],
            "attempted": len(completed),
            "succeeded": succ,
            "failed": len(completed) - succ,
            "failure_stages": dict(sorted(failures.items())),
            "population_fingerprint": self.population_fingerprint(),
            "accounting": self.accounting,
            "updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        inventory.write_json(self.state_path, state)

    def record(self, record: dict) -> None:
        inventory.append_jsonl(self.rows_path, record)

    def manifest(self, digest: str, archive: Path) -> tuple[dict, dict]:
        path = self.manifest_dir / f"{digest}.jsonl"
        if not path.exists():
            partial = path.with_name(path.name + ".part")
            result = self.runner(
                [
                    str(self.runner.lforge),
                    "archive",
                    "manifest",
                    str(archive),
                    "--format",
                    "jsonl",
                    "--output",
                    str(partial),
                    "--overwrite",
                    "--executable",
                    str(self.runner.executable),
                ]
            )
            if result.returncode != 0:
                partial.unlink(missing_ok=True)
                return {"ok": False, "error": (result.stderr or result.stdout).strip()[:500]}, {}
            os.replace(partial, path)
        try:
            return self.read_manifest(path)
        except (OSError, UnicodeError, CensusError) as error:
            return {"ok": False, "error": str(error)[:500]}, {}

    def read_manifest(self, path: Path) -> tuple[dict, dict]:
        size = path.stat().st_size
        if size > MAX_MANIFEST_BYTES:
            raise CensusError(f"manifest exceeds the {MAX_MANIFEST_BYTES}-byte bound")
        header = None
        total = 0
        readable = 0
        states = Counter()
        types = defaultdict(lambda: {"rows": 0, "readable": 0, "unreadable": 0, "encodings": Counter()})
        layouts = Counter()
        depth2_type0 = []
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                document = json.loads(line)
                if header is None:
                    if document.get("kind") != "header":
                        raise CensusError("manifest has no header record")
                    header = document
                    continue
                total += 1
                if total > MAX_MANIFEST_ROWS:
                    raise CensusError(f"manifest exceeds the {MAX_MANIFEST_ROWS}-row bound")
                if document.get("kind") != "row":
                    continue
                type_id = document.get("type_id")
                entry = types[type_id]
                entry["rows"] += 1
                if is_readable(document):
                    readable += 1
                    entry["readable"] += 1
                else:
                    entry["unreadable"] += 1
                    states[str(document.get("contents", {}).get("state"))] += 1
                entry["encodings"][inventory.chunk_label(document)] += 1
                layouts[f"{document.get('layout')}/{inventory.chunk_label(document)}"] += 1
                if type_id == 0:
                    depth2_type0.append(
                        {
                            "row": document.get("row"),
                            "logical_size": document.get("logical_size"),
                            "stored_size": document.get("stored_size"),
                            "readable": is_readable(document),
                            "layout": document.get("layout"),
                            "mode": document.get("mode"),
                            "encoding": inventory.chunk_label(document),
                            "payload_transform": document.get("payload_transform"),
                            "contents_state": document.get("contents", {}).get("state"),
                            "type_fingerprint": fingerprint(document),
                        }
                    )
        if header is None:
            raise CensusError("manifest has no header record")
        authentication = header.get("authentication", {})
        summary = {
            "ok": True,
            "rows": total,
            "readable": readable,
            "unreadable": total - readable,
            "unreadable_states": dict(sorted(states.items())),
            "types": [
                {
                    "type_id": type_id,
                    "rows": value["rows"],
                    "readable": value["readable"],
                    "unreadable": value["unreadable"],
                    "encodings": dict(sorted(value["encodings"].items())),
                }
                for type_id, value in sorted(types.items(), key=lambda item: str(item[0]))
            ],
            "layout_encoding": dict(sorted(layouts.items())),
            "authentication_status": authentication.get("status") if isinstance(authentication, dict) else authentication,
            "depth2_type0": depth2_type0,
        }
        return summary, header

    def process(self, item: dict) -> dict:
        relative = item["relative"]
        row = item["row"]
        expected = item["logical_size"]
        parent = Path(item["archive"])
        record = {
            "schema": ROW_SCHEMA,
            "kind": "row",
            "relative": relative,
            "row": row,
            "type_id": 0,
            "logical_size": expected,
            "stored_size": item["stored_size"],
            "layout": item["layout"],
            "mode": item["mode"],
            "chunks": item["chunks"],
            "payload_transform": item["payload_transform"],
            "payload_offset": item["payload_offset"],
            "attempt": {
                "attempted": True,
                "mode": None,
                "ok": False,
                "exit": None,
                "actual_size": None,
                "sha256": None,
                "stage": None,
                "reason": None,
            },
            "manifest": None,
            "header": None,
            "duplicate_of": None,
        }
        if not parent.exists():
            record["attempt"]["stage"] = "missing input"
            record["attempt"]["reason"] = "the top-level archive is absent"
            return record
        temporary = self.tmp_dir / f"row_{re.sub(r'[^A-Za-z0-9._-]+', '_', relative)}_{row}.rpf"
        use_copy = expected > self.cli_output_limit
        try:
            if use_copy:
                location_ok = (
                    item["mode"] == 0
                    and item["chunks"] is None
                    and not item["payload_transform"]
                    and item["stored_size"] == expected
                    and isinstance(item["payload_offset"], str)
                )
                if not location_ok:
                    record["attempt"]["mode"] = "stored-copy"
                    record["attempt"]["stage"] = "operational limit"
                    record["attempt"]["reason"] = (
                        "the row exceeds the CLI output limit and its location record "
                        "is not a plain stored range"
                    )
                    return record
                record["attempt"]["mode"] = "stored-copy"
                copy_stored_row(
                    parent,
                    int(item["payload_offset"], 16),
                    int(item["stored_size"]),
                    temporary,
                    parent.stat().st_size,
                )
                record["attempt"]["exit"] = 0
            else:
                record["attempt"]["mode"] = "cli"
                result = self.runner(
                    [
                        str(self.runner.lforge),
                        "archive",
                        "extract",
                        str(parent),
                        "--row",
                        str(row),
                        "--output",
                        str(temporary),
                        "--overwrite",
                        "--executable",
                        str(self.runner.executable),
                    ]
                )
                record["attempt"]["exit"] = result.returncode
                if result.returncode != 0:
                    text = (result.stderr or result.stdout).strip()
                    record["attempt"]["stage"] = classify_failure(text, result.returncode, None, expected)
                    record["attempt"]["reason"] = text[:500]
                    return record
            actual = temporary.stat().st_size if temporary.exists() else None
            record["attempt"]["actual_size"] = actual
            if actual != expected:
                record["attempt"]["stage"] = "incomplete reconstruction"
                record["attempt"]["reason"] = f"extracted {actual} of {expected} bytes"
                return record
            digest = sha256_file(temporary)
            record["attempt"]["sha256"] = digest
            record["attempt"]["ok"] = True
            if self.keep_archives:
                shutil.copyfile(temporary, self.archive_dir / f"{digest}.rpf")
            summary, _ = self.manifest(digest, temporary)
            if not summary.get("ok"):
                record["attempt"]["ok"] = False
                record["attempt"]["stage"] = "metadata readability"
                record["attempt"]["reason"] = summary.get("error")
                return record
            record["manifest"] = summary
            record["header"] = read_header(temporary)
            return record
        except CopyRangeError as error:
            record["attempt"]["stage"] = "framing error"
            record["attempt"]["reason"] = str(error)[:500]
            return record
        except CensusError as error:
            record["attempt"]["stage"] = "operational limit"
            record["attempt"]["reason"] = str(error)[:500]
            return record
        except OSError as error:
            record["attempt"]["stage"] = "operational limit"
            record["attempt"]["reason"] = f"I/O error: {error}"[:500]
            return record
        except subprocess.TimeoutExpired:
            record["attempt"]["stage"] = "operational limit"
            record["attempt"]["reason"] = f"the command exceeded {self.runner.timeout} seconds"
            return record
        finally:
            temporary.unlink(missing_ok=True)

    def run(self) -> int:
        completed = self.load_completed()
        unknown = [key for key in completed if key not in {row_key(row) for row in self.rows}]
        if unknown:
            raise CensusError(f"{len(unknown)} completed rows are not in the declared population")
        state_fingerprint = None
        if self.state_path.exists():
            try:
                state_fingerprint = json.loads(self.state_path.read_text(encoding="utf-8")).get(
                    "population_fingerprint"
                )
            except (OSError, json.JSONDecodeError) as error:
                raise CensusError(f"state.json is unreadable: {error}")
        if state_fingerprint and state_fingerprint != self.population_fingerprint():
            raise CensusError("state.json belongs to a different population")
        pending = [row for row in self.rows if row_key(row) not in completed]
        self.log(
            f"declared {len(self.rows)} rows, {len(completed)} already complete, {len(pending)} pending"
        )
        self.log_handle = self.log_path.open("a", encoding="utf-8")
        try:
            batch = []
            for item in pending:
                batch.append(item)
                if len(batch) < self.batch_size:
                    continue
                self._flush(batch, completed)
                batch = []
            if batch:
                self._flush(batch, completed)
            self.write_state(completed, "complete")
            self.log(f"finished {len(completed)} of {len(self.rows)} rows")
        finally:
            self.log_handle.close()
            self.log_handle = None
        return 0

    def _flush(self, batch: list[dict], completed: dict[str, dict]) -> None:
        for item in batch:
            record = self.process(item)
            self.record(record)
            completed[row_key(record)] = record
            if not record["attempt"]["ok"]:
                inventory.append_jsonl(
                    self.failures_path,
                    {
                        "relative": record["relative"],
                        "row": record["row"],
                        "stage": record["attempt"]["stage"],
                        "reason": record["attempt"]["reason"],
                    },
                )
        self.write_state(completed, "running")
        self.log(f"batch complete: {len(completed)} of {len(self.rows)} rows")


def aggregate(output_dir: Path) -> dict:
    rows_path = output_dir / "rows.jsonl"
    if not rows_path.exists():
        raise CensusError("rows.jsonl is absent")
    identity = None
    identity_path = output_dir / "identity.json"
    if identity_path.exists():
        try:
            identity = json.loads(identity_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            identity = None
    records = []
    with rows_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))
    unique = {}
    duplicates = 0
    for record in records:
        digest = record.get("attempt", {}).get("sha256")
        if digest and digest in unique:
            record["duplicate_of"] = unique[digest]["relative"] + ":" + str(unique[digest]["row"])
            duplicates += 1
        elif digest:
            unique[digest] = record

    stages = Counter()
    attempts = Counter()
    extraction_modes = Counter()
    type_rows = Counter()
    type_readable = Counter()
    type_unreadable = Counter()
    type_encoding = defaultdict(Counter)
    type_layout = defaultdict(Counter)
    unreadable_states = Counter()
    layout_encoding = Counter()
    depth2_rows = []
    depth2_manifests = 0
    header_values = {name: [] for name, *_ in HEADER_FIELDS}
    header_sizes = []
    auth = Counter()
    manifest_rows = 0

    for record in records:
        attempt = record["attempt"]
        attempts[attempt.get("mode")] += 1
        if attempt.get("stage"):
            stages[attempt["stage"]] += 1

    effective = [record for record in records if not record.get("duplicate_of")]
    for record in effective:
        attempt = record["attempt"]
        manifest = record.get("manifest")
        if not attempt.get("ok") or not manifest:
            continue
        auth[str(manifest.get("authentication_status"))] += 1
        manifest_rows += manifest.get("rows", 0)
        if manifest.get("depth2_type0"):
            depth2_manifests += 1
            depth2_rows.extend(manifest["depth2_type0"])
        for entry in manifest.get("types", []):
            type_id = entry["type_id"]
            type_rows[type_id] += entry["rows"]
            type_readable[type_id] += entry["readable"]
            type_unreadable[type_id] += entry["unreadable"]
            for label, count in entry.get("encodings", {}).items():
                type_encoding[type_id][label] += count
        for key, count in manifest.get("layout_encoding", {}).items():
            layout_encoding[key] += count
        for state, count in manifest.get("unreadable_states", {}).items():
            unreadable_states[state] += count
        header = record.get("header")
        if header:
            for name, *_ in HEADER_FIELDS:
                header_values[name].append(header[name])
            header_sizes.append(header["file_size"])

    header_ranges = []
    for name, offset, width, kind in HEADER_FIELDS:
        values = header_values[name]
        header_ranges.append(
            {
                "field": name,
                "offset": f"0x{offset:02X}",
                "width": width,
                "kind": kind,
                "count": len(values),
                "min": min(values) if values else None,
                "max": max(values) if values else None,
                "distinct": len(set(values)),
            }
        )
    histogram = [
        {
            "type_id": type_id,
            "rows": count,
            "readable": type_readable[type_id],
            "unreadable": type_unreadable[type_id],
            "encodings": dict(sorted(type_encoding[type_id].items())),
        }
        for type_id, count in sorted(type_rows.items(), key=lambda item: str(item[0]))
    ]
    summary = {
        "schema": SCHEMA,
        "identity": identity,
        "declared_total": len(records),
        "attempted": len(records),
        "succeeded": sum(1 for record in records if record["attempt"].get("ok")),
        "failed": sum(1 for record in records if not record["attempt"].get("ok")),
        "unique_archive_contents": len(unique),
        "duplicate_rows": duplicates,
        "histogram_population": "unique_archive_contents",
        "extraction_modes": dict(attempts),
        "failure_stages": dict(sorted(stages.items())),
        "manifest_authentication": dict(sorted(auth.items())),
        "manifest_rows": manifest_rows,
        "depth2_type0_rows": len(depth2_rows),
        "depth2_source_manifests": depth2_manifests,
        "depth2_type0": depth2_rows,
        "type_histogram": histogram,
        "layout_encoding": dict(sorted(layout_encoding.items())),
        "unreadable_states": dict(sorted(unreadable_states.items())),
        "header_ranges": header_ranges,
        "header_file_size": {
            "count": len(header_sizes),
            "min": min(header_sizes) if header_sizes else None,
            "max": max(header_sizes) if header_sizes else None,
        },
    }
    inventory.write_json(output_dir / "report.json", summary)
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--lforge", type=Path)
    parser.add_argument("--executable", type=Path)
    parser.add_argument("--app-revision")
    parser.add_argument("--batch-size", type=int, default=50)
    parser.add_argument("--timeout", type=int, default=3600)
    parser.add_argument("--keep-archives", action="store_true")
    parser.add_argument("--summarize-only", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    ensure_output_dir(args.output_dir, args.inventory_dir)
    if args.summarize_only:
        summary = aggregate(args.output_dir)
        print(json.dumps({key: summary[key] for key in ("attempted", "succeeded", "failed")}))
        return 0
    if args.lforge is None or args.executable is None:
        raise CensusError("--lforge and --executable are required unless --summarize-only is set")
    identity = {
        "lforge_version": subprocess.run(
            [str(args.lforge), "--version"], capture_output=True, text=True, check=False
        ).stdout.strip(),
        "lforge_sha256": sha256_file(args.lforge),
        "executable_sha256": sha256_file(args.executable),
        "application_revision": args.app_revision,
    }
    inventory.write_json(args.output_dir / "identity.json", identity)
    manifests, duplicates = inventory.discover_manifests(args.inventory_dir)
    census = Census(
        manifests,
        args.output_dir,
        Runner(args.lforge, args.executable, args.timeout),
        args.batch_size,
        args.keep_archives,
    )
    if duplicates:
        inventory.write_json(args.output_dir / "manifest_duplicates.json", duplicates)
    census.log(
        f"type-0 rows {census.accounting['type0_rows']}, "
        f"unreadable {census.accounting['unreadable_type0']}, "
        f"declared {census.accounting['declared_total']}"
    )
    census.run()
    aggregate(args.output_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
