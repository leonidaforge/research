"""Bounded encoding-2 framing survey for RPF9 row manifests.

Reads a native row manifest and the archive bytes it describes. Every read is
checked against the archive size and the row's stored range.
"""

import argparse
import json
import os
import struct
import sys
import zlib

SCHEMA = "leonida-forge.rpf9-framing-survey/1"
BLOCK = 1 << 20
DEFAULT_ROW_BYTES = 64 << 20
DEFAULT_OUTPUT = 4 << 20
PREFIX = 16


class BoundsError(ValueError):
    """A manifest range lies outside the archive."""


class Limits:
    def __init__(self, row_bytes=DEFAULT_ROW_BYTES, output=DEFAULT_OUTPUT):
        self.row_bytes = row_bytes
        self.output = output


def _int(value):
    if isinstance(value, int):
        return value
    text = str(value)
    return int(text, 16) if text.lower().startswith("0x") else int(text)


def _check(offset, size, file_size, what):
    if offset < 0 or size < 0 or offset + size > file_size:
        raise BoundsError("%s lies outside the archive: offset %d size %d file %d"
                          % (what, offset, size, file_size))


def _zlib_header(head):
    if len(head) < 2:
        return False
    cmf, flg = head[0], head[1]
    return ((cmf & 0x0F) == 8 and (cmf >> 4) <= 7
            and (((cmf << 8) | flg) % 31 == 0) and (flg & 0x20) == 0)


def _inflate(fileobj, pos, end, limits, full):
    """Inflate one zlib stream. Returns (status, compressed, prefix_bytes, stored_len)."""
    dec = zlib.decompressobj()
    out = bytearray()
    fed = 0
    with open(fileobj, "rb") as fh:
        fh.seek(pos)
        while pos + fed < end:
            block = fh.read(min(BLOCK, end - pos - fed))
            if not block:
                break
            fed += len(block)
            if fed > limits.row_bytes:
                return "truncated", 0, bytes(out), 0
            data = block
            while data:
                room = limits.output - len(out)
                try:
                    if room > 0:
                        chunk = dec.decompress(data, room)
                        if chunk:
                            out += chunk
                    elif not full:
                        return "partial", 0, bytes(out), 0
                    else:
                        dec.decompress(data, BLOCK)
                except zlib.error:
                    return "error", 0, bytes(out), 0
                if dec.eof:
                    compressed = fed - len(dec.unused_data)
                    return "eof", compressed, bytes(out), ((compressed + 15) // 16) * 16
                data = dec.unconsumed_tail
    return "partial", 0, bytes(out), 0


def _decode_row(fileobj, file_size, row, limits):
    offset = _int(row["payload_offset"])
    stored = _int(row["stored_size"])
    logical = _int(row["logical_size"])
    count = int(row["chunks"]["count"])
    _check(offset, stored, file_size, "row %s" % row.get("row"))
    if stored < PREFIX:
        raise BoundsError("row %s is shorter than its stored prefix" % row.get("row"))
    with open(fileobj, "rb") as fh:
        fh.seek(offset)
        prefix = fh.read(PREFIX)
    result = {
        "prefix_zero": prefix == b"\x00" * PREFIX,
        "count": count,
        "methods": [],
        "pages": None,
        "zero_run": None,
        "pointer8": False,
        "marker": None,
    }
    if row.get("payload_transform"):
        result["methods"] = ["transformed"] * count
        return result
    pos = offset + PREFIX
    end = offset + stored
    decoded = bytearray()
    produced = 0
    for index in range(count):
        if pos >= end:
            result["methods"].append("unknown")
            break
        last = index == count - 1
        with open(fileobj, "rb") as fh:
            fh.seek(pos)
            head = fh.read(2)
        if _zlib_header(head):
            status, compressed, out, stored_len = _inflate(fileobj, pos, end, limits, count > 1)
            if status == "eof":
                result["methods"].append("zlib")
                produced += len(out)
                if len(decoded) < limits.output:
                    decoded += out[:limits.output - len(decoded)]
                pos += stored_len
                continue
            if status == "partial" and count == 1:
                result["methods"].append("zlib")
                if len(decoded) < limits.output:
                    decoded += out[:limits.output - len(decoded)]
                break
            result["methods"].append("unknown")
            break
        if last:
            stored_len = end - pos
            remaining = logical - produced
            if stored_len == remaining:
                result["methods"].append("raw")
                with open(fileobj, "rb") as fh:
                    fh.seek(pos)
                    out = fh.read(min(limits.output, stored_len))
                if len(decoded) < limits.output:
                    decoded += out[:limits.output - len(decoded)]
            else:
                result["methods"].append("unknown")
            pos = end
        else:
            result["methods"].append("unknown")
            break
    data = bytes(decoded)
    run = 0
    for byte in data:
        if byte == 0:
            run += 1
        else:
            break
    result["zero_run"] = min(run, 16)
    if len(data) >= 16:
        value = struct.unpack_from("<Q", data, 8)[0]
        result["pointer8"] = value >> 32 == 0 and ((value & 0xFFFFFFFF) >> 28) in (5, 6)
        if result["pointer8"]:
            map_offset = value & 0x0FFFFFFF
            if map_offset + 10 <= len(data):
                result["pages"] = [data[map_offset + 8], data[map_offset + 9]]
    if len(data) >= 0x15:
        token = data[0x10:0x15]
        if all(32 <= byte < 127 for byte in token):
            result["marker"] = token.decode("ascii")
    return result


def survey(archive, manifest, limits=None):
    limits = limits or Limits()
    file_size = os.path.getsize(archive)
    rows = manifest.get("rows", manifest)
    encoding2 = [row for row in rows if row.get("chunks") and row["chunks"].get("encoding") == 2]
    summary = {
        "schema": SCHEMA,
        "rows": len(rows),
        "rows_encoding2": len(encoding2),
        "prefix": {"all_zero": 0, "other": 0},
        "chunk_counts": {},
        "methods": {},
        "method_patterns": {},
        "decoded": {"zero_run": {}, "pointer_at_8": 0, "marker_0DRPz": 0, "other_at_0x10": 0},
        "parts": {"page_counts_known": 0, "equal": 0, "more_chunks": 0, "fewer_chunks": 0},
        "transformed_rows": 0,
        "out_of_bounds": 0,
        "limits": {"row_bytes": limits.row_bytes, "output": limits.output},
    }
    for row in encoding2:
        try:
            result = _decode_row(archive, file_size, row, limits)
        except BoundsError:
            summary["out_of_bounds"] += 1
            continue
        summary["prefix"]["all_zero" if result["prefix_zero"] else "other"] += 1
        key = str(result["count"])
        summary["chunk_counts"][key] = summary["chunk_counts"].get(key, 0) + 1
        pattern = ",".join(result["methods"])
        summary["method_patterns"][pattern] = summary["method_patterns"].get(pattern, 0) + 1
        for method in result["methods"]:
            summary["methods"][method] = summary["methods"].get(method, 0) + 1
        if result["methods"] and result["methods"][0] == "transformed":
            summary["transformed_rows"] += 1
            continue
        run = str(result["zero_run"])
        summary["decoded"]["zero_run"][run] = summary["decoded"]["zero_run"].get(run, 0) + 1
        if result["pointer8"]:
            summary["decoded"]["pointer_at_8"] += 1
        if result["marker"] == "0DRPz":
            summary["decoded"]["marker_0DRPz"] += 1
        else:
            summary["decoded"]["other_at_0x10"] += 1
        if result["pages"] is not None:
            summary["parts"]["page_counts_known"] += 1
            pages = result["pages"][0] + result["pages"][1]
            if result["count"] == pages:
                summary["parts"]["equal"] += 1
            elif result["count"] > pages:
                summary["parts"]["more_chunks"] += 1
            else:
                summary["parts"]["fewer_chunks"] += 1
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description="Survey encoding-2 framing in one RPF9 archive.")
    parser.add_argument("--archive", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output")
    parser.add_argument("--max-row-bytes", type=int, default=DEFAULT_ROW_BYTES)
    parser.add_argument("--max-output", type=int, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    manifest = json.load(open(args.manifest, "r", encoding="utf-8"))
    summary = survey(args.archive, manifest, Limits(args.max_row_bytes, args.max_output))
    text = json.dumps(summary, indent=1, sort_keys=True)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
    else:
        sys.stdout.write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
