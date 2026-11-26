"""Random decode checks for payload-transformed rows across top-level RPFs.

Read-only. The harness drives a compatible Leonida Forge CLI (it needs
`archive search --transformed` and `archive extract`), lists transformed rows,
picks rows at random with a fixed seed, extracts each, and compares the output
size with the row's declared logical size. It prints only archive names, row
numbers and sizes. The CLI reads the executable's key state; this script does
not read key material itself.

This is not part of the synthetic unit-test suite: it needs the application
CLI, a local installation and the matching executable. Set `PER_ARCHIVE` to
change the sample size (default 5).

Usage:
    python tools/rpf9/random_transform_tests.py <lforge> <game-dir>
        <executable> [seed]
"""

import json
import os
import random
import subprocess
import sys
import tempfile

MAX_BYTES = 16 * 1024 * 1024
PER_ARCHIVE = int(os.environ.get("PER_ARCHIVE", "5"))


def run(args):
    return subprocess.run(args, capture_output=True, text=True)


def transformed_rows(lforge, archive, executable):
    result = run([
        lforge, "archive", "search", archive,
        "--executable", executable,
        "--transformed", "true",
        "--limit", "100000",
        "--json",
    ])
    if result.returncode != 0:
        return None, result.stderr.strip().splitlines()[:1]
    document = json.loads(result.stdout)
    return document.get("rows", []), None


def main():
    lforge, game_dir, executable = sys.argv[1:4]
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 20261126
    rng = random.Random(seed)
    archives = sorted(
        os.path.join(game_dir, name)
        for name in os.listdir(game_dir)
        if name.lower().endswith(".rpf")
        and os.path.isfile(os.path.join(game_dir, name))
    )
    total = passed = failed = skipped = 0
    with tempfile.TemporaryDirectory() as temp:
        for archive in archives:
            name = os.path.basename(archive)
            rows, error = transformed_rows(lforge, archive, executable)
            if rows is None:
                print(f"{name}: listing failed: {error}")
                continue
            if not rows:
                print(f"{name}: no transformed rows")
                continue
            candidates = [
                row for row in rows
                if row.get("logical_size", 0) <= MAX_BYTES
                and row.get("stored_size", 0) <= MAX_BYTES
            ]
            if not candidates:
                skipped += len(rows)
                print(f"{name}: {len(rows)} transformed rows, all above {MAX_BYTES} bytes")
                continue
            sample = rng.sample(candidates, min(PER_ARCHIVE, len(candidates)))
            results = []
            for row in sample:
                total += 1
                output = os.path.join(temp, f"{name}-{row['row']}.bin")
                result = run([
                    lforge, "archive", "extract", archive,
                    "--row", str(row["row"]),
                    "--output", output,
                    "--overwrite",
                    "--executable", executable,
                ])
                if result.returncode != 0:
                    failed += 1
                    results.append((row["row"], "error", result.stderr.strip().splitlines()[:1]))
                    continue
                size = os.path.getsize(output)
                if size != row["logical_size"]:
                    failed += 1
                    results.append((row["row"], f"size {size} != {row['logical_size']}", []))
                else:
                    passed += 1
                    results.append((row["row"], size, []))
            print(f"{name}: {len(rows)} transformed, sampled {len(sample)}: {results}")
    print(f"summary: {passed}/{total} decoded, {failed} failed, {skipped} skipped")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
