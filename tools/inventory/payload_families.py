"""Classify decoded inventory payload families from their first bytes.

A payload behind the RPF9 chunk framing decodes to a 16-byte zero prefix and a
resource stream, or to a bare family magic. The classifier reads the first
window, records the bytes at +0x10, and follows the system pointer at +0x08 when
the page map falls inside the window.

The sample is selected per type from cached manifests. Extraction is bounded and
temporary bytes are removed. The output is a scratch artefact; only aggregate
counts belong in the evidence index.
"""

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

import recursive_inventory as inventory

SCHEMA = "leonida-forge.payload-families/1"
WINDOW = 4096
MAX_SELECTED = 10_000
MAGICS = {
    b"9FPR": "rpf9-magic",
    b"RBF0": "rbf0-magic",
    b"PSIN": "psin-magic",
    b"SGD5": "sgd5-magic",
    b"EDUP": "edup-magic",
    b"KB2j": "kb2j-magic",
    b"KB2n": "kb2n-magic",
    b"RDS5": "rds5-magic",
    b"PTFX": "ptfx-magic",
}


class FamilyError(Exception):
    """A refusal or an invariant violation."""


def classify(prefix: bytes) -> dict:
    if len(prefix) < 16:
        return {
            "class": "short",
            "confidence": "Confirmed (length only)",
            "tag": None,
            "pointer": None,
            "page_map": None,
        }
    zero8 = prefix[:8] == b"\0" * 8
    pointer = int.from_bytes(prefix[8:16], "little")
    selector = None if pointer >> 32 else pointer >> 28
    system_pointer = selector == 5
    tag = prefix[16:20] if len(prefix) >= 20 else b""
    entry = {
        "class": None,
        "confidence": None,
        "zero_prefix": zero8,
        "tag": tag.decode("latin-1") if tag and all(32 <= byte < 127 for byte in tag) else None,
        "tag_hex": tag.hex() if tag else None,
        "pointer": f"{pointer:#018x}",
        "pointer_selector": selector,
        "system_pointer": system_pointer,
        "pointer_agrees": bool(zero8 and system_pointer and tag == b"0DRP"),
        "page_map": None,
    }
    if zero8 and system_pointer and tag == b"0DRP":
        entry["class"] = "resource-wrapper"
        entry["wrapper_tag"] = "0DRPz" if prefix[20:21] == b"z" else "0DRP"
        entry["confidence"] = "Confirmed (bytes); Probable (resource header)"
    elif zero8:
        entry["class"] = "zero-prefix"
        entry["confidence"] = "Confirmed (bytes); Unknown (format identity)"
        if tag == b"0DRP":
            entry["rejected_wrapper"] = "0DRP tag without a selector-5 pointer at +0x08"
    elif prefix[:4] in MAGICS:
        entry["class"] = MAGICS[prefix[:4]]
        entry["confidence"] = "Confirmed (bytes); Unknown (format identity)"
    elif prefix[:2] in (b"\x78\x9c", b"\x78\xda"):
        entry["class"] = "zlib-container-header"
        entry["confidence"] = "Confirmed (bytes)"
    else:
        entry["class"] = "unrecognized"
        entry["confidence"] = "Confirmed (bytes); Unknown (format identity)"
    if zero8 and system_pointer and len(prefix) > pointer & 0x0FFFFFFF:
        offset = pointer & 0x0FFFFFFF
        if offset + 10 <= len(prefix):
            entry["page_map"] = {
                "offset": offset,
                "system_pages": prefix[offset + 8],
                "graphics_pages": prefix[offset + 9],
            }
    return entry


def select(manifest_dir: Path, archive_dir: Path, per_type: int, max_payload_bytes: int) -> tuple[list[dict], dict]:
    candidates = defaultdict(list)
    manifests = 0
    for path in sorted(manifest_dir.glob("*.jsonl")):
        try:
            with path.open(encoding="utf-8") as handle:
                header = json.loads(handle.readline())
                if header.get("kind") != "header":
                    continue
                sha = path.stem
                archive = archive_dir / (sha + ".rpf")
                for line in handle:
                    if not line.strip():
                        continue
                    row = json.loads(line)
                    if row.get("kind") != "row" or not inventory.is_readable(row):
                        continue
                    size = row.get("logical_size")
                    if not isinstance(size, int) or size < 0 or size > max_payload_bytes:
                        continue
                    type_id = row.get("type_id")
                    candidates[type_id].append(
                        {
                            "sha256": sha,
                            "archive": archive,
                            "row": row,
                            "logical_size": size,
                        }
                    )
            manifests += 1
        except (OSError, UnicodeError, json.JSONDecodeError):
            continue
    selected = []
    for type_id in sorted(candidates, key=str):
        rows = sorted(
            candidates[type_id],
            key=lambda item: (item["logical_size"], item["sha256"], item["row"]["row"]),
        )
        if len(rows) <= per_type:
            chosen = rows
        elif per_type == 1:
            chosen = [rows[len(rows) // 2]]
        else:
            indices = sorted({round(index * (len(rows) - 1) / (per_type - 1)) for index in range(per_type)})
            chosen = [rows[index] for index in indices]
        selected.extend(chosen)
        if len(selected) > MAX_SELECTED:
            raise FamilyError(f"the selection exceeds the {MAX_SELECTED}-payload bound")
    return selected, {
        "manifests": manifests,
        "types": len(candidates),
        "candidates": sum(len(value) for value in candidates.values()),
        "selected": len(selected),
    }


class Runner:
    def __init__(self, lforge: Path, executable: Path, timeout: int):
        self.lforge = Path(lforge)
        self.executable = Path(executable)
        self.timeout = timeout

    def __call__(self, command):
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=self.timeout,
        )


def run(selected: list[dict], output_dir: Path, runner: Runner) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows_path = output_dir / "payloads.jsonl"
    tmp = output_dir / "tmp"
    tmp.mkdir(exist_ok=True)
    classes = Counter()
    tags = Counter()
    wrappers = Counter()
    page_maps = Counter()
    per_type = defaultdict(Counter)
    stages = Counter()
    successes = 0
    failures = 0
    for item in selected:
        row = item["row"]
        output = tmp / f"{item['sha256']}_{row['row']}.bin"
        command = [
            str(runner.lforge),
            "archive",
            "extract",
            str(item["archive"]),
            "--row",
            str(row["row"]),
            "--output",
            str(output),
            "--overwrite",
            "--executable",
            str(runner.executable),
        ]
        record = {
            "schema": SCHEMA,
            "type_id": row.get("type_id"),
            "sha256": item["sha256"],
            "row": row["row"],
            "logical_size": item["logical_size"],
            "encoding": inventory.chunk_label(row),
            "layout": row.get("layout"),
        }
        try:
            if not item["archive"].exists():
                record["stage"] = "missing input"
                record["reason"] = "the cached archive is absent"
                stages["missing input"] += 1
                failures += 1
            else:
                result = runner(command)
                if result.returncode != 0:
                    record["stage"] = "unsupported transformation" if "transform" in (result.stderr or "").lower() else "extraction"
                    record["reason"] = (result.stderr or result.stdout).strip()[:300]
                    stages[record["stage"]] += 1
                    failures += 1
                else:
                    with output.open("rb") as handle:
                        prefix = handle.read(WINDOW)
                    record["classification"] = classify(prefix)
                    record["prefix_sha256"] = hashlib.sha256(prefix).hexdigest()[:16]
                    classes[record["classification"]["class"]] += 1
                    tags[record["classification"].get("tag_hex")] += 1
                    if record["classification"].get("wrapper_tag"):
                        wrappers[record["classification"]["wrapper_tag"]] += 1
                    page_map = record["classification"].get("page_map")
                    if page_map:
                        page_maps[f"{page_map['system_pages']}/{page_map['graphics_pages']}"] += 1
                    per_type[row.get("type_id")][record["classification"]["class"]] += 1
                    successes += 1
        except (OSError, subprocess.TimeoutExpired) as error:
            record["stage"] = "operational limit"
            record["reason"] = str(error)[:300]
            stages[record["stage"]] += 1
            failures += 1
        finally:
            output.unlink(missing_ok=True)
        inventory.append_jsonl(rows_path, record)
    summary = {
        "schema": SCHEMA,
        "selected": len(selected),
        "successes": successes,
        "failures": failures,
        "failure_stages": dict(sorted(stages.items())),
        "classes": dict(sorted(classes.items())),
        "tags_at_0x10": {str(key): value for key, value in sorted(tags.items(), key=lambda item: str(item[0]))},
        "wrapper_tags": dict(sorted(wrappers.items())),
        "page_maps": dict(sorted(page_maps.items())),
        "per_type": {str(key): dict(sorted(value.items())) for key, value in sorted(per_type.items(), key=lambda item: str(item[0]))},
    }
    inventory.write_json(output_dir / "summary.json", summary)
    return summary


def ensure_output(output: Path, *inputs: Path) -> None:
    output = Path(output).resolve()
    for source in inputs:
        source = Path(source).resolve()
        if output == source or source in output.parents:
            raise FamilyError("the output directory MUST NOT lie inside an input directory")
        if output in source.parents:
            raise FamilyError("an input directory MUST NOT lie inside the output directory")


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while True:
            block = handle.read(8 * 1024 * 1024)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest-dir", type=Path, required=True)
    parser.add_argument("--archive-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--lforge", type=Path, required=True)
    parser.add_argument("--executable", type=Path, required=True)
    parser.add_argument("--per-type", type=int, default=8)
    parser.add_argument("--max-payload-bytes", type=int, default=1024 * 1024)
    parser.add_argument("--app-revision")
    parser.add_argument("--timeout", type=int, default=600)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.per_type < 1:
        raise FamilyError("--per-type MUST be at least 1")
    ensure_output(args.output_dir, args.manifest_dir, args.archive_dir)
    selected, frame = select(args.manifest_dir, args.archive_dir, args.per_type, args.max_payload_bytes)
    identity = {
        "lforge_version": subprocess.run(
            [str(args.lforge), "--version"], capture_output=True, text=True, check=False
        ).stdout.strip(),
        "lforge_sha256": sha256_path(args.lforge),
        "executable_sha256": sha256_path(args.executable),
        "application_revision": args.app_revision,
    }
    summary = run(selected, args.output_dir, Runner(args.lforge, args.executable, args.timeout))
    summary["frame"] = frame
    summary["identity"] = identity
    inventory.write_json(args.output_dir / "identity.json", identity)
    inventory.write_json(args.output_dir / "summary.json", summary)
    print(json.dumps({"selected": summary["selected"], "successes": summary["successes"], "classes": summary["classes"]}))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except FamilyError as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(2)
