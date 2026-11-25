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
PMAP_BODY_HEADER_SIZE = 16
PMAP_BLOCK_SIZE = 16
LSCH_BODY_HEADER_SIZE = 0x10
LSCH_MARKER_RECORD_SIZE = 32
LENM_HEADER_SIZE = 0x20

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

    body = b""
    body_error = None
    if first_offset + SECTION_HEADER_SIZE <= len(data):
        length = _be32(data, first_offset + 4)
        end = first_offset + length
        if length >= SECTION_HEADER_SIZE and end <= len(data):
            body = data[first_offset + SECTION_HEADER_SIZE:end]
        else:
            body_error = "section length is outside the payload"
    else:
        body_error = "section header is truncated"

    header = None
    blocks = []
    checks = {
        "body_header_size": len(body) >= PMAP_BODY_HEADER_SIZE,
        "body_length_matches_count": False,
        "header_padding_70": False,
        "first_block_at_0x10": False,
        "offsets_aligned_16": False,
        "block_offsets_monotone": False,
        "block_offsets_follow_lengths": False,
        "block_ranges_in_bounds": False,
        "unused_words_zero": False,
        "padding_between_blocks_70": False,
        "formula_matches_first_offset": False,
        "all_large_ids_in_psch": False,
        "no_small_ids_in_psch": False,
    }
    formula_total = None
    if len(body) >= PMAP_BODY_HEADER_SIZE:
        mode, extra, count = struct.unpack_from(">IIH", body, 0)
        header = {
            "mode": mode,
            "extra": extra,
            "count": count,
            "padding": body[10:16].hex(),
        }
        checks["header_padding_70"] = body[10:16] == b"\x70" * 6
        expected = PMAP_BODY_HEADER_SIZE + PMAP_BLOCK_SIZE * count
        checks["body_length_matches_count"] = len(body) == expected

        checks["block_ranges_in_bounds"] = True
        previous_end = HEADER_SIZE
        formula_total = 0x10
        expected_offset = 0x10
        offsets_follow = True
        offset_ok = True
        all_zero = True
        padding_ok = True
        for index in range(count):
            base = PMAP_BODY_HEADER_SIZE + PMAP_BLOCK_SIZE * index
            if base + PMAP_BLOCK_SIZE > len(body):
                break
            kind, offset, unused, length = struct.unpack_from(">IIII", body, base)
            blocks.append(
                {
                    "index": index,
                    "id": kind,
                    "offset": offset,
                    "length": length,
                    "unused": unused,
                    "offset_aligned_16": offset % 16 == 0,
                }
            )
            if index == 0 and offset == 0x10:
                checks["first_block_at_0x10"] = True
            if offset != expected_offset:
                offsets_follow = False
            if offset % 16:
                offset_ok = False
            if offset < previous_end or offset + length > first_offset:
                checks["block_ranges_in_bounds"] = False
            gap = data[previous_end:offset]
            if gap and any(byte != 0x70 for byte in gap):
                padding_ok = False
            if unused:
                all_zero = False
            previous_end = offset + length
            if index + 1 < count:
                formula_total += _align16(length)
                expected_offset += _align16(length)
            else:
                formula_total += length
                expected_offset += length
        checks["offsets_aligned_16"] = offset_ok
        checks["block_offsets_follow_lengths"] = offsets_follow
        checks["block_offsets_monotone"] = all(
            blocks[i]["offset"] < blocks[i + 1]["offset"] for i in range(len(blocks) - 1)
        )
        checks["unused_words_zero"] = all_zero
        checks["padding_between_blocks_70"] = padding_ok
        checks["formula_matches_first_offset"] = formula_total == first_offset

    named = None
    for block in blocks:
        if block["id"] != 1:
            continue
        start = block["offset"]
        block_bytes = data[start:start + block["length"]]
        names = []
        all_printable = False
        if block_bytes.endswith(b"\x00"):
            parts = block_bytes[:-1].split(b"\x00")
            names = [
                part for part in parts
                if part and all(0x20 <= byte < 0x7F for byte in part)
            ]
            all_printable = len(names) == len(parts)
        named = {
            "block_index": block["index"],
            "name_count": len(names),
            "all_names_printable": all_printable,
            "printable_ratio": (
                round(sum(1 for byte in block_bytes if 0x20 <= byte < 0x7F) / len(block_bytes), 3)
                if block_bytes else 0.0
            ),
        }
        break

    psch = None
    section = None
    for tag, offset, length, section_body in _walk_sections(data):
        if tag == "PSCH":
            section = (offset, length, section_body)
            break
    if section is not None:
        psch = _psch_report(section[2])
        if psch and psch.get("ids") is not None:
            psch_ids = set(psch["ids"])
            large_ids = [block["id"] for block in blocks if block["id"] >= 0x100]
            small_ids = [block["id"] for block in blocks if block["id"] < 0x100]
            checks["all_large_ids_in_psch"] = all(
                identifier in psch_ids for identifier in large_ids
            )
            checks["no_small_ids_in_psch"] = all(
                identifier not in psch_ids for identifier in small_ids
            )

    return {
        "grammar": "pre-section area",
        "model": "block table",
        "descriptor_table": None,
        "body_error": body_error,
        "header": header,
        "blocks": blocks,
        "block_count": len(blocks),
        "name_table": named,
        "pre_section_length": len(pre_section),
        "header_marker_70": pre_section.startswith(PMAP_MARKER),
        "pre_section_sha256": hashlib.sha256(pre_section).hexdigest(),
        "embedded_magic": embedded,
        "formula_total": formula_total,
        "psch": psch,
        "checks": checks,
    }


def _psch_report(body: bytes) -> dict:
    count = _be32(body, 0) if len(body) >= 4 else None
    report = {
        "count": count,
        "table_bytes": None,
        "prefix": None,
        "value_lengths": [],
        "tiling_ok": False,
    }
    if count is None:
        return report
    table_bytes = 4 + 8 * count
    report["table_bytes"] = table_bytes
    if table_bytes + 8 > len(body):
        return report
    ids = [_be32(body, 4 + 8 * i) for i in range(count)]
    offsets = [_be32(body, 8 + 8 * i) for i in range(count)]
    report["ids"] = ids
    report["prefix"] = body[table_bytes:table_bytes + 8].hex()
    report["first_ids"] = [f"0x{value:08x}" for value in ids[:8]]
    if count == 0:
        report["tiling_ok"] = table_bytes == len(body) or table_bytes + 8 == len(body)
        return report
    start = table_bytes + 8
    tiling = offsets[0] == start
    tiling = tiling and all(
        offsets[i] < offsets[i + 1] for i in range(count - 1)
    )
    tiling = tiling and offsets[-1] <= len(body)
    lengths = [
        (offsets[i + 1] if i + 1 < count else len(body)) - offsets[i]
        for i in range(count)
    ]
    report["value_lengths"] = lengths
    report["tiling_ok"] = bool(tiling and offsets[-1] + lengths[-1] == len(body))
    return report


def _walk_sections(data: bytes):
    offset = _be32(data, 4)
    while offset < len(data):
        tag = _tag(data, offset)
        length = _be32(data, offset + 4)
        yield tag, offset, length, data[offset + SECTION_HEADER_SIZE:offset + length]
        offset += length


def _lsch_body_report(body: bytes) -> dict:
    report = {
        "length": len(body),
        "length_multiple_16": len(body) % 16 == 0,
        "marker_at_0x10": body[LSCH_BODY_HEADER_SIZE:LSCH_BODY_HEADER_SIZE + 8] == DESCRIPTOR_MARKER,
        "header_word_0x08": _le32(body, 0x08) if len(body) >= 0x0C else None,
        "marker_count": 0,
        "tail_length": None,
        "tail_multiple_16": None,
        "tail_has_marker": None,
    }
    position = LSCH_BODY_HEADER_SIZE
    while (
        position + LSCH_MARKER_RECORD_SIZE <= len(body)
        and body[position:position + 8] == DESCRIPTOR_MARKER
    ):
        report["marker_count"] += 1
        position += LSCH_MARKER_RECORD_SIZE
    tail = len(body) - position
    report["tail_length"] = tail
    report["tail_multiple_16"] = tail % 16 == 0
    report["tail_has_marker"] = DESCRIPTOR_MARKER in body[position:]
    return report


def _lenm_body_report(body: bytes) -> dict:
    report = {
        "length": len(body),
        "empty": len(body) == 0,
        "header_size": LENM_HEADER_SIZE,
        "body_minus_header_multiple_8": None,
        "marker_ee_at_0x08": len(body) >= 0x10 and body[8:16] == b"\xEE" * 8,
        "header_tail_zero": len(body) >= 0x20 and body[0x14:0x20] == b"\0" * 12,
        "count": None,
        "chain_length": None,
        "predicted_body_length": None,
        "extra_length": None,
        "extra_multiple_8": None,
    }
    if len(body) < LENM_HEADER_SIZE:
        return report
    count = _le32(body, 0x10)
    chain_length = 16 * count - 8
    predicted = LENM_HEADER_SIZE + chain_length
    extra = len(body) - predicted
    report.update(
        {
            "body_minus_header_multiple_8": (len(body) - LENM_HEADER_SIZE) % 8 == 0,
            "count": count,
            "chain_length": chain_length,
            "predicted_body_length": predicted,
            "extra_length": extra,
            "extra_multiple_8": extra % 8 == 0,
        }
    )
    return report



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
    first_tag = tag_sequence[0] if tag_sequence else None
    if first_tag == "LSCH":
        family = "LSCH"
    elif first_tag == "PMAP":
        family = "PMAP"
    elif first_tag is not None:
        family = "OTHER"
    else:
        family = None

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
        body_reports = {}
        for section_tag, section_offset, section_length, section_body in _walk_sections(data):
            if section_tag == "LSCH":
                body_reports["LSCH"] = _lsch_body_report(section_body)
            elif section_tag == "LENM":
                body_reports["LENM"] = _lenm_body_report(section_body)
        family_data["section_bodies"] = body_reports
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
        "pmap_block_formula_matches": bool(
            family_data and family_data.get("checks", {}).get("formula_matches_first_offset")
        ),
        "pmap_offsets_follow_lengths": bool(
            family_data and family_data.get("checks", {}).get("block_offsets_follow_lengths")
        ),
        "pmap_ids_contained": bool(
            family_data
            and family_data.get("checks", {}).get("all_large_ids_in_psch")
            and family_data.get("checks", {}).get("no_small_ids_in_psch")
        ),
        "lsch_body_marker_at_0x10": bool(
            family_data
            and family_data.get("section_bodies", {})
            .get("LSCH", {})
            .get("marker_at_0x10")
        ),
        "lsch_body_tail_multiple_16": bool(
            family_data
            and family_data.get("section_bodies", {})
            .get("LSCH", {})
            .get("tail_multiple_16")
        ),
        "checksum_ok": integrity["checksum_ok"],
    }

    return {
        "label": label,
        "size": size,
        "sha256": hashlib.sha256(data).hexdigest(),
        "magic": "PSIN",
        "family": family,
        "first_tag": first_tag,
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
    print(f"first_tag: {report['first_tag']}", file=stream)
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
        header = family_data.get("header") or {}
        print(
            "pre_section:"
            f" length={family_data['pre_section_length']}"
            f" marker_70={family_data['header_marker_70']}"
            f" model={family_data.get('model')}"
            f" blocks={family_data.get('block_count')}"
            f" mode={header.get('mode')}"
            f" count={header.get('count')}"
            f" offsets_follow_lengths={family_data.get('checks', {}).get('block_offsets_follow_lengths')}"
            f" formula_matches={family_data.get('checks', {}).get('formula_matches_first_offset')}",
            file=stream,
        )
        name_table = family_data.get("name_table")
        if name_table:
            print(
                "name_table:"
                f" block={name_table['block_index']}"
                f" names={name_table['name_count']}"
                f" printable={name_table['all_names_printable']}",
                file=stream,
            )
        psch = family_data.get("psch")
        if psch:
            print(
                "psch:"
                f" count={psch['count']}"
                f" tiling_ok={psch['tiling_ok']}"
                f" large_ids_in_psch={family_data['checks'].get('all_large_ids_in_psch')}"
                f" small_ids_absent={family_data['checks'].get('no_small_ids_in_psch')}"
                f" prefix={psch['prefix']}",
                file=stream,
            )
    if family_data and family_data.get("section_bodies"):
        for tag, body in family_data["section_bodies"].items():
            if tag == "LSCH":
                print(
                    "lsch_body:"
                    f" length={body['length']}"
                    f" marker_at_0x10={body['marker_at_0x10']}"
                    f" markers={body['marker_count']}"
                    f" tail={body['tail_length']}"
                    f" tail_multiple_16={body['tail_multiple_16']}",
                    file=stream,
                )
            elif tag == "LENM":
                print(
                    "lenm_body:"
                    f" length={body['length']}"
                    f" empty={body['empty']}"
                    f" header=0x{body['header_size']:x}"
                    f" body_minus_header_multiple_8={body['body_minus_header_multiple_8']}"
                    f" marker_ee={body['marker_ee_at_0x08']}"
                    f" header_tail_zero={body['header_tail_zero']}"
                    f" count={body['count']}"
                    f" chain={body['chain_length']}"
                    f" extra={body['extra_length']}",
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
        f" pmap_block_formula_matches={checks['pmap_block_formula_matches']}"
        f" pmap_offsets_follow_lengths={checks['pmap_offsets_follow_lengths']}"
        f" pmap_ids_contained={checks['pmap_ids_contained']}"
        f" lsch_body_marker_at_0x10={checks['lsch_body_marker_at_0x10']}"
        f" lsch_body_tail_multiple_16={checks['lsch_body_tail_multiple_16']}"
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
