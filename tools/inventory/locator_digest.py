"""Compute the SHA-256 of an archive or one stored row from its manifest.

The digest is over the extracted archive bytes (``--whole-archive``) or over
the bytes at the selected row's payload offset and stored size. The tool is
read-only and prints one digest, so a locator can state how its value was
produced.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

MAX_ROWS = 10_000_000
STEP = 8 * 1024 * 1024


class DigestError(Exception):
    """A refusal or a malformed locator input."""


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while True:
            block = handle.read(STEP)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def find_row(manifest: Path, index: int) -> dict:
    with Path(manifest).open(encoding="utf-8") as handle:
        for count, line in enumerate(handle, 1):
            if count > MAX_ROWS:
                raise DigestError(f"the manifest exceeds the {MAX_ROWS}-row bound")
            if not line.strip():
                continue
            try:
                document = json.loads(line)
            except json.JSONDecodeError as error:
                raise DigestError(f"{manifest.name} line {count} is not JSON: {error}") from error
            if document.get("kind") == "row" and document.get("row") == index:
                return document
    raise DigestError(f"row {index} is not present in {manifest.name}")


def digest_row(archive: Path, manifest: Path, index: int) -> str:
    row = find_row(manifest, index)
    try:
        offset = int(row["payload_offset"], 16)
        length = int(row["stored_size"])
    except (KeyError, TypeError, ValueError) as error:
        raise DigestError(f"row {index} has no integer payload offset and stored size") from error
    size = Path(archive).stat().st_size
    if offset < 0 or length < 0 or offset + length > size:
        raise DigestError(f"row {index} range {offset}+{length} is outside the {size}-byte archive")
    digest = hashlib.sha256()
    with Path(archive).open("rb") as handle:
        handle.seek(offset)
        remaining = length
        while remaining:
            block = handle.read(min(STEP, remaining))
            if not block:
                raise DigestError(f"row {index} ended before {length} stored bytes")
            digest.update(block)
            remaining -= len(block)
    return digest.hexdigest()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--row", type=int)
    parser.add_argument("--whole-archive", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.whole_archive:
        print(digest_file(args.archive))
        return 0
    if args.manifest is None or args.row is None:
        raise DigestError("--manifest and --row are required unless --whole-archive is set")
    print(digest_row(args.archive, args.manifest, args.row))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except DigestError as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(2)
