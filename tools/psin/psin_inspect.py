#!/usr/bin/env python3
"""Report the PSIN outer framing, family grammar and integrity section.

PSIN payloads share one outer framing and carry two section grammars, keyed by
their first section tag (`LSCH` and `PMAP`). The tool classifies the family and
reports the family-specific structure without treating the second family as a
failed parse. It reads each input read-only and does not decode section bodies.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import struct
import sys

MAGIC = b"PSIN"
HEADER_SIZE = 8
SECTION_HEADER_SIZE = 8
DEFAULT_MAX_BYTES = 2 * 1024 * 1024 * 1024
DEFAULT_MAX_SECTIONS = 10_000

DESCRIPTOR_TABLE_OFFSET = 0x08
DESCRIPTOR_SIZE = 16
DESCRIPTOR_CONSTANT = 0x10
DESCRIPTOR_LENGTH_OFFSET = 0x04
DESCRIPTOR_MARKER = b"\xAA" * 8
PMAP_MARKER = b"\x70" * 8

DESCRIPTOR_VARIANTS = (
    ("table_0x08_constant_0x10_length_0x04_aligned", 0x08, 0x10, 0x04, True),
    ("table_0x08_constant_0x10_length_0x04_raw", 0x08, 0x10, 0x04, False),
    ("table_0x10_constant_0x10_length_0x04_aligned", 0x10, 0x10, 0x04, True),
    ("table_0x08_constant_0x10_length_0x00_aligned", 0x08, 0x10, 0x00, True),
)

SEED = 0x3FAC7125
CHKS_BODY_SIZE = 12


class PsinError(ValueError):
    pass


def _be32(data: bytes, offset: int) -> int:
    if offset + 4 > len(data):
        raise PsinError(f"read past end at 0x{offset:x}")
    return struct.unpack_from(">I", data, offset)[0]


def _le32(data: bytes, offset: int) -> int:
    if offset + 4 > len(data):
        raise PsinError(f"read past end at 0x{offset:x}")
    return struct.unpack_from("<I", data, offset)[0]


def _tag(data: bytes, offset: int) -> str:
    raw = data[offset:offset + 4]
    if len(raw) != 4 or not all(0x20 <= byte < 0x7F for byte in raw):
        raise PsinError(f"no printable tag at 0x{offset:x}")
    return raw.decode("ascii")


def _align16(value: int) -> int:
    return (value + 15) & ~15


def one_at_a_time_signed(data: bytes, seed: int = SEED) -> int:
    """One-at-a-time hash over signed bytes."""
    value = seed & 0xFFFFFFFF
    for byte in data:
        if byte >= 128:
            byte -= 256
        value = (value + byte) & 0xFFFFFFFF
        value = (value + (value << 10)) & 0xFFFFFFFF
        value ^= value >> 6
    value = (value + (value << 3)) & 0xFFFFFFFF
    value ^= value >> 11
    value = (value + (value << 15)) & 0xFFFFFFFF
    return value


def solve_descriptor_counts(
    data: bytes,
    table_offset: int = DESCRIPTOR_TABLE_OFFSET,
    constant: int = DESCRIPTOR_CONSTANT,
    length_offset: int = DESCRIPTOR_LENGTH_OFFSET,
    aligned: bool = True,
) -> list[int]:
    """Return every descriptor count that satisfies the offset relation."""
    first_offset = _be32(data, 4)
    solutions: list[int] = []
    if constant == first_offset:
        solutions.append(0)
    total = constant
    count = 0
    while True:
        offset = table_offset + DESCRIPTOR_SIZE * count
        if offset + DESCRIPTOR_SIZE > len(data):
            break
        total += DESCRIPTOR_SIZE
        if total > first_offset:
            break
        if data[offset + 8:offset + 16] != DESCRIPTOR_MARKER:
            break
        length = _le32(data, offset + length_offset)
        total += _align16(length) if aligned else length
        count += 1
        if total == first_offset:
            solutions.append(count)
        elif total > first_offset:
            break
    return solutions


def _descriptor_report(data: bytes, first_offset: int) -> dict:
    variants = {}
    for name, table, constant, length_offset, aligned in DESCRIPTOR_VARIANTS:
        variants[name] = solve_descriptor_counts(data, table, constant, length_offset, aligned)

    solutions = variants["table_0x08_constant_0x10_length_0x04_aligned"]
    unique = len(solutions) == 1
    count = solutions[0] if unique else None
    descriptors = []
    sum_aligned = 0
    if count is not None:
        data_offset = DESCRIPTOR_TABLE_OFFSET + DESCRIPTOR_SIZE * count
        for index in range(count):
            offset = DESCRIPTOR_TABLE_OFFSET + DESCRIPTOR_SIZE * index
            length = _le32(data, offset + DESCRIPTOR_LENGTH_OFFSET)
            descriptors.append(
                {
                    "index": index,
                    "offset": offset,
                    "unknown_word": _le32(data, offset),
                    "length": length,
                    "marker_aa": data[offset + 8:offset + 16] == DESCRIPTOR_MARKER,
                    "data_offset": data_offset,
                }
            )
            data_offset += _align16(length)
            sum_aligned += _align16(length)
    formula_constant = DESCRIPTOR_CONSTANT + DESCRIPTOR_SIZE * (count or 0) + sum_aligned
    return {
        "grammar": "descriptor table",
        "table_offset": DESCRIPTOR_TABLE_OFFSET,
        "descriptor_size": DESCRIPTOR_SIZE,
        "solutions": solutions,
        "unique_solution": unique,
        "descriptor_count": count,
        "descriptors": descriptors,
        "sum_aligned_lengths": sum_aligned,
        "formula_constant": DESCRIPTOR_CONSTANT,
        "formula_total": formula_constant,
        "formula_matches": formula_constant == first_offset,
        "variants": variants,
    }


def _pmap_report(data: bytes, first_offset: int) -> dict:
    pre_section = data[HEADER_SIZE:first_offset]
    embedded = [
        tag.decode("ascii")
        for tag in (b"PSIN", b"RBF0", b"LSCH", b"PMAP", b"PSCH", b"STNS", b"CHKS")
        if tag in pre_section
    ]
    return {
        "grammar": "pre-section area",
        "descriptor_table": None,
        "pre_section_length": len(pre_section),
        "header_marker_70": pre_section.startswith(PMAP_MARKER),
        "pre_section_sha256": hashlib.sha256(pre_section).hexdigest(),
        "embedded_magic": embedded,
    }


def inspect_bytes(
    data: bytes,
    label: str = "<memory>",
    max_sections: int = DEFAULT_MAX_SECTIONS,
) -> dict:
    size = len(data)
    if size < HEADER_SIZE:
        raise PsinError(f"{label}: shorter than the {HEADER_SIZE}-byte header")
    if data[0:4] != MAGIC:
        raise PsinError(f"{label}: magic is {data[0:4].hex(' ')}, not PSIN")

    first_offset = _be32(data, 4)
    if first_offset < HEADER_SIZE:
        raise PsinError(f"{label}: first-section offset {first_offset} is inside the header")
    if first_offset > size:
        raise PsinError(f"{label}: first-section offset {first_offset} is past the file end")

    sections = []
    offset = first_offset
    while offset < size:
        if len(sections) >= max_sections:
            raise PsinError(f"{label}: section walk exceeds the {max_sections}-section cap")
        if offset + SECTION_HEADER_SIZE > size:
            raise PsinError(f"{label}: section header at 0x{offset:x} is truncated")
        tag = _tag(data, offset)
        length = _be32(data, offset + 4)
        if length < SECTION_HEADER_SIZE:
            raise PsinError(
                f"{label}: section {tag} at 0x{offset:x} length {length} "
                f"is below the {SECTION_HEADER_SIZE}-byte header"
            )
        end = offset + length
        if end > size:
            raise PsinError(f"{label}: section {tag} at 0x{offset:x} ends past the file")
        body_length = length - SECTION_HEADER_SIZE
        sections.append(
            {
                "tag": tag,
                "offset": offset,
                "length": length,
                "body_length": body_length,
                "body_mod_16": body_length % 16,
            }
        )
        offset = end

    tag_sequence = [section["tag"] for section in sections]
    family = tag_sequence[0] if tag_sequence else None

    header = {
        "first_section_offset": first_offset,
        "first_section_offset_high16": first_offset >> 16,
        "first_section_offset_low16": first_offset & 0xFFFF,
        "field_06_be": struct.unpack_from(">H", data, 6)[0],
        "field_08_0f": data[8:16].hex(),
        "field_08_be": _be32(data, 8) if size >= 12 else None,
        "field_0c_le": struct.unpack_from("<I", data, 12)[0] if size >= 16 else None,
    }

    family_data = None
    if family == "LSCH":
        family_data = _descriptor_report(data, first_offset)
    elif family == "PMAP":
        family_data = _pmap_report(data, first_offset)

    integrity = {
        "present": False,
        "section_offset": None,
        "total_length": None,
        "total_length_equals_size": False,
        "stored_checksum": None,
        "computed_checksum": None,
        "checksum_ok": False,
        "tail": None,
        "tail_is_zppp": False,
    }
    for section in sections:
        if section["tag"] != "CHKS":
            continue
        integrity["present"] = True
        integrity["section_offset"] = section["offset"]
        body = section["offset"] + SECTION_HEADER_SIZE
        integrity["body_length"] = section["body_length"]
        if section["body_length"] >= CHKS_BODY_SIZE:
            total_length = _be32(data, body)
            stored = _be32(data, body + 4)
            tail = data[body + 8:body + 12].decode("latin-1")
            zeroed = bytearray(data)
            zeroed[body:body + 8] = b"\0" * 8
            computed = one_at_a_time_signed(bytes(zeroed))
            integrity.update(
                {
                    "total_length": total_length,
                    "total_length_equals_size": total_length == size,
                    "stored_checksum": stored,
                    "computed_checksum": computed,
                    "checksum_ok": computed == stored,
                    "tail": tail,
                    "tail_is_zppp": tail == "zppp",
                }
            )
        break

    checks = {
        "first_section_offset_equals_size": first_offset == size,
        "first_section_offset_aligned_16": first_offset % 16 == 0,
        "field_06_equals_size": header["field_06_be"] == size,
        "field_06_equals_low16": header["field_06_be"] == header["first_section_offset_low16"],
        "section_walk_ends_at_file_size": offset == size,
        "descriptor_formula_matches": bool(
            family_data and family_data.get("formula_matches")
        ),
        "checksum_ok": integrity["checksum_ok"],
    }

    return {
        "label": label,
        "size": size,
        "sha256": hashlib.sha256(data).hexdigest(),
        "magic": "PSIN",
        "family": family,
        "header": header,
        "family_data": family_data,
        "sections": sections,
        "section_count": len(sections),
        "tag_sequence": tag_sequence,
        "integrity": integrity,
        "checks": checks,
    }


def _print_text(report: dict, stream) -> None:
    print(f"sample: {report['label']}", file=stream)
    print(f"size: {report['size']} bytes", file=stream)
    print(f"sha256: {report['sha256']}", file=stream)
    print(f"family: {report['family']}", file=stream)
    header = report["header"]
    print(
        "header:"
        f" first_section_offset={header['first_section_offset']}"
        f" high16=0x{header['first_section_offset_high16']:04x}"
        f" low16=0x{header['first_section_offset_low16']:04x}"
        f" field_06_be={header['field_06_be']}"
        f" field_08_0f={header['field_08_0f']}",
        file=stream,
    )
    family_data = report["family_data"]
    if family_data and family_data.get("grammar") == "descriptor table":
        print(
            "descriptors:"
            f" count={family_data['descriptor_count']}"
            f" unique={family_data['unique_solution']}"
            f" solutions={family_data['solutions']}"
            f" sum_aligned={family_data['sum_aligned_lengths']}"
            f" formula_matches={family_data['formula_matches']}",
            file=stream,
        )
    elif family_data:
        print(
            "pre_section:"
            f" length={family_data['pre_section_length']}"
            f" marker_70={family_data['header_marker_70']}"
            f" embedded_magic={family_data['embedded_magic']}",
            file=stream,
        )
    print(f"sections: {report['section_count']}", file=stream)
    for section in report["sections"]:
        print(
            f"  {section['tag']} offset=0x{section['offset']:x}"
            f" length={section['length']} body={section['body_length']}"
            f" body_mod_16={section['body_mod_16']}",
            file=stream,
        )
    integrity = report["integrity"]
    if integrity["present"]:
        print(
            "integrity:"
            f" total_length={integrity['total_length']}"
            f" total_length_equals_size={integrity['total_length_equals_size']}"
            f" checksum_ok={integrity['checksum_ok']}"
            f" tail_is_zppp={integrity['tail_is_zppp']}",
            file=stream,
        )
    checks = report["checks"]
    print(
        "checks:"
        f" first_section_offset_equals_size={checks['first_section_offset_equals_size']}"
        f" first_section_offset_aligned_16={checks['first_section_offset_aligned_16']}"
        f" field_06_equals_size={checks['field_06_equals_size']}"
        f" field_06_equals_low16={checks['field_06_equals_low16']}"
        f" section_walk_ends_at_file_size={checks['section_walk_ends_at_file_size']}"
        f" descriptor_formula_matches={checks['descriptor_formula_matches']}"
        f" checksum_ok={checks['checksum_ok']}",
        file=stream,
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Report PSIN framing, family grammar and integrity.")
    parser.add_argument("samples", nargs="+", help="PSIN payload files")
    parser.add_argument("--json", action="store_true", help="print JSON instead of text")
    parser.add_argument(
        "--max-bytes", type=int, default=DEFAULT_MAX_BYTES,
        help="refuse a sample larger than this many bytes",
    )
    parser.add_argument(
        "--max-sections", type=int, default=DEFAULT_MAX_SECTIONS,
        help="refuse a section walk above this count",
    )
    args = parser.parse_args(argv)

    reports = []
    try:
        for path in args.samples:
            if os.path.getsize(path) > args.max_bytes:
                raise PsinError(f"{path}: larger than the {args.max_bytes}-byte cap")
            with open(path, "rb") as handle:
                data = handle.read()
            reports.append(inspect_bytes(data, label=path, max_sections=args.max_sections))
    except (OSError, PsinError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    if args.json:
        sys.stdout.write(json.dumps(reports, indent=2) + "\n")
    else:
        buffer = io.StringIO()
        for report in reports:
            _print_text(report, buffer)
            buffer.write("\n")
        sys.stdout.write(buffer.getvalue())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
