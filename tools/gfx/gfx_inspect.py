#!/usr/bin/env python3
"""Report the observed GFX* decoded-payload header and trailer.

The tool encodes the grammar that 49 decoded type-66 payloads share. It is an
experimental structural sampler, not a format validator and not a filename
decoder. It reads each input read-only, refuses to write output inside an input
directory, and prints offsets, lengths, variant bytes and counts. It does not
print the ASCII runs themselves.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import struct
import sys

MAGIC = b"GFX*"
PRE_NAME_TAIL = bytes.fromhex("fa0104000000000e00")
INTERSTITIAL = bytes.fromhex("00004411090000004302")
TRAILER = b".Main\x00\x40\x00\x00\x00"
DEFAULT_MAX_BYTES = 64 * 1024 * 1024

# (byte at +0x08, byte at +0x0A) -> offset of the first ASCII run.
VARIANTS = {
    (0x70, 0x0A): 0x20,
    (0x70, 0x0B): 0x20,
    (0x78, 0x05): 0x21,
    (0x80, 0x02): 0x21,
    (0x88, 0x01): 0x22,
}


class GfxError(ValueError):
    pass


def _u16be(data, offset):
    if offset + 2 > len(data):
        raise GfxError(f"read past end at 0x{offset:x}")
    return struct.unpack_from(">H", data, offset)[0]


def _u32le(data, offset):
    if offset + 4 > len(data):
        raise GfxError(f"read past end at 0x{offset:x}")
    return struct.unpack_from("<I", data, offset)[0]


def _printable(data, offset, length):
    return all(0x20 <= byte <= 0x7E for byte in data[offset:offset + length])


def _last_printable_run(data, end):
    start = end
    while start > 0 and 0x20 <= data[start - 1] <= 0x7E:
        start -= 1
    return start, end - start


def inspect_bytes(data: bytes, label: str = "<memory>") -> dict:
    size = len(data)
    if size < 0x40:
        raise GfxError(f"{label}: shorter than the observed 0x40-byte prefix")
    if data[0:4] != MAGIC:
        raise GfxError(f"{label}: magic is {data[0:4].hex(' ')}, not GFX*")

    declared_size = _u32le(data, 0x04)
    if declared_size != size:
        raise GfxError(f"{label}: size field is {declared_size}, file is {size}")

    variant_key = (data[0x08], data[0x0A])
    name1_offset = VARIANTS.get(variant_key)
    if name1_offset is None:
        raise GfxError(
            f"{label}: variant {variant_key[0]:02x}/{variant_key[1]:02x} is not in the observed set"
        )

    if data[0x09] != 0:
        raise GfxError(f"{label}: byte at +0x09 is {data[0x09]:02x}, not zero")

    tail_offset = name1_offset - 11
    if data[tail_offset:name1_offset - 2] != PRE_NAME_TAIL:
        raise GfxError(f"{label}: the pre-name constant run is absent at 0x{tail_offset:x}")

    name1_length = _u16be(data, name1_offset - 2)
    name1_end = name1_offset + name1_length
    if name1_length == 0 or name1_end + 15 > size:
        raise GfxError(f"{label}: first run length {name1_length} does not fit")
    if not _printable(data, name1_offset, name1_length):
        raise GfxError(f"{label}: first run is not printable ASCII")

    interstitial = data[name1_end:name1_end + 15]
    if interstitial[0:10] != INTERSTITIAL:
        raise GfxError(f"{label}: interstitial prefix is absent at 0x{name1_end:x}")
    if interstitial[14] != 0x0A:
        raise GfxError(f"{label}: interstitial does not end in 0x0A")

    name2_offset = name1_end + 15
    name2_end = data.find(b"\x00", name2_offset)
    if name2_end < 0:
        raise GfxError(f"{label}: second run is not terminated")
    name2_length = name2_end - name2_offset
    if name2_length == 0 or not _printable(data, name2_offset, name2_length):
        raise GfxError(f"{label}: second run is empty or not printable")
    first_run = data[name1_offset:name1_end]
    second_run = data[name2_offset:name2_end]
    if first_run not in second_run or not second_run.endswith(b"_Main"):
        raise GfxError(f"{label}: second run does not contain the first run and end in _Main")

    body_offset = name2_end + 1
    if body_offset >= size - len(TRAILER):
        raise GfxError(f"{label}: no body before the trailer")

    if data[-len(TRAILER):] != TRAILER:
        raise GfxError(f"{label}: the observed trailer is absent")
    trailer_offset = size - len(TRAILER)
    if body_offset > trailer_offset:
        raise GfxError(f"{label}: body crosses the trailer")

    final_offset, final_length = _last_printable_run(data, size - 5)
    if final_offset < body_offset or not data[final_offset:size - 5].endswith(b".Main"):
        raise GfxError(f"{label}: the trailing printable run is absent or does not end in .Main")

    tail_count = data.count(PRE_NAME_TAIL)
    interstitial_count = data.count(INTERSTITIAL)
    trailer_count = data.count(TRAILER)
    if (tail_count, interstitial_count, trailer_count) != (1, 1, 1):
        raise GfxError(
            f"{label}: marker counts are tail={tail_count}, interstitial={interstitial_count},"
            f" trailer={trailer_count}, expected one each"
        )

    return {
        "label": label,
        "size": size,
        "sha256": hashlib.sha256(data).hexdigest(),
        "variant": {
            "byte_08": f"0x{variant_key[0]:02x}",
            "byte_0a": f"0x{variant_key[1]:02x}",
            "name1_offset": name1_offset,
        },
        "size_field": {
            "offset": 4,
            "width": 4,
            "value": declared_size,
            "equals_file_size": True,
        },
        "pre_name_tail": {"offset": tail_offset, "length": len(PRE_NAME_TAIL)},
        "name1": {"offset": name1_offset, "length": name1_length},
        "interstitial": {
            "offset": name1_end,
            "length": 15,
            "group": interstitial[10:13].hex(),
            "end_byte": f"0x{interstitial[14]:02x}",
        },
        "name2": {
            "offset": name2_offset,
            "length": name2_length,
            "contains_name1": True,
            "ends_main": True,
        },
        "body": {"offset": body_offset, "length": trailer_offset - body_offset},
        "final_run": {"offset": final_offset, "length": final_length},
        "trailer": {"offset": trailer_offset, "length": len(TRAILER)},
        "marker_counts": {
            "pre_name_tail": tail_count,
            "interstitial": interstitial_count,
            "trailer": trailer_count,
        },
    }


def _print_text(report: dict, stream) -> None:
    variant = report["variant"]
    print(f"sample: {report['label']}", file=stream)
    print(f"size: {report['size']} bytes", file=stream)
    print(f"sha256: {report['sha256']}", file=stream)
    print(
        f"variant: byte_08={variant['byte_08']}"
        f" byte_0a={variant['byte_0a']}"
        f" name1_offset=0x{variant['name1_offset']:x}",
        file=stream,
    )
    field = report["size_field"]
    print(
        f"size field: offset=0x{field['offset']:x} width={field['width']}"
        f" value={field['value']} equals_file_size={field['equals_file_size']}",
        file=stream,
    )
    print(
        f"pre-name tail: offset=0x{report['pre_name_tail']['offset']:x}"
        f" length={report['pre_name_tail']['length']}",
        file=stream,
    )
    print(
        f"first run: offset=0x{report['name1']['offset']:x}"
        f" length={report['name1']['length']}",
        file=stream,
    )
    inter = report["interstitial"]
    print(
        f"interstitial: offset=0x{inter['offset']:x} length={inter['length']}"
        f" group={inter['group']} end_byte={inter['end_byte']}",
        file=stream,
    )
    print(
        f"second run: offset=0x{report['name2']['offset']:x}"
        f" length={report['name2']['length']}"
        f" contains_name1={report['name2']['contains_name1']}"
        f" ends_main={report['name2']['ends_main']}",
        file=stream,
    )
    print(
        f"body: offset=0x{report['body']['offset']:x}"
        f" length={report['body']['length']}",
        file=stream,
    )
    print(
        f"final run: offset=0x{report['final_run']['offset']:x}"
        f" length={report['final_run']['length']}",
        file=stream,
    )
    print(
        f"trailer: offset=0x{report['trailer']['offset']:x}"
        f" length={report['trailer']['length']}",
        file=stream,
    )
    counts = report["marker_counts"]
    print(
        f"markers: pre_name_tail={counts['pre_name_tail']}"
        f" interstitial={counts['interstitial']} trailer={counts['trailer']}",
        file=stream,
    )


def _output_is_inside_input(output: str, inputs: list[str]) -> bool:
    output_dir = os.path.realpath(os.path.dirname(os.path.abspath(output)) or ".")
    for path in inputs:
        input_dir = os.path.realpath(os.path.dirname(os.path.abspath(path)) or ".")
        if output_dir == input_dir or output_dir.startswith(input_dir + os.sep):
            return True
    return False


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Report observed GFX* structural fields.")
    parser.add_argument("samples", nargs="+", help="decoded GFX* payload files")
    parser.add_argument("--json", action="store_true", help="print JSON instead of text")
    parser.add_argument("--output", help="write output to this file instead of stdout")
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES,
                        help="refuse a sample larger than this many bytes")
    args = parser.parse_args(argv)

    if args.output and _output_is_inside_input(args.output, args.samples):
        parser.error("refusing to write output inside an input directory")

    reports = []
    try:
        for path in args.samples:
            if os.path.getsize(path) > args.max_bytes:
                raise GfxError(f"{path}: larger than the {args.max_bytes}-byte cap")
            with open(path, "rb") as handle:
                data = handle.read()
            reports.append(inspect_bytes(data, label=path))
    except (OSError, GfxError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    if args.json:
        text = json.dumps(reports, indent=2) + "\n"
    else:
        buffer = io.StringIO()
        for report in reports:
            _print_text(report, buffer)
            buffer.write("\n")
        text = buffer.getvalue()

    if args.output:
        with open(args.output, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
