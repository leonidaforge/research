#!/usr/bin/env python3
"""Bounded reader for drawable texture-slot references.

A drawable shader holds a parameter table and a slot table. The first
``texture_count`` parameter entries are texture parameters; each has a 32-bit
word whose low two bits are the entry class and whose upper bits are a texture
slot index. The slot table holds one 8-byte pointer per texture parameter. A
bound slot points to a 0x50-byte texture record; its name record at ``+0x30``
holds a 32-bit value at ``+0x18`` that is a dictionary name hash in the sampled
resources, and a separate 64-bit key at ``+0x08``.

The slot index is a reference into the shader's slot table. The 32-bit name
value is a reference into a texture dictionary. This module reports both, plus
the ordinary 0x5/0x6 pointer counts, so a caller can keep references and
pointers apart. It reads only and does not decode pixels or names.

See formats/resources/textures.md and the drawable document for the layouts.
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from dataclasses import dataclass, field

SYSTEM_BASE = 0x5000_0000
GRAPHICS_BASE = 0x6000_0000
OFFSET_MASK = 0x0FFF_FFFF
TEXTURE_RECORD_LEN = 0x50
NAME_RECORD_LEN = 0x20
MAX_SHADERS = 64
MAX_PARAMETERS = 4096

SLOT_CLASS_MASK = 0x3
SLOT_INDEX_SHIFT = 2


class PoolReferenceError(Exception):
    """The buffer cannot hold the drawable shader/slot chain."""


def decode_pointer(value: int):
    if value >> 32:
        return None
    kind = value >> 28
    if kind == 5:
        return ("system", value & OFFSET_MASK)
    if kind == 6:
        return ("graphics", value & OFFSET_MASK)
    return None


def _u16(data, at):
    return struct.unpack_from("<H", data, at)[0]


def _u32(data, at):
    return struct.unpack_from("<I", data, at)[0]


def _u64(data, at):
    return struct.unpack_from("<Q", data, at)[0]


def decode_slot_reference(value: int, slot_count: int):
    """Split one texture-parameter word into class and slot index.

    Returns ``(accepted, index)``. The class is the low two bits; a texture
    entry has class 0 and its index is ``value >> 2``. The split is Probable:
    it is exact for 969 texture entries and rejects 7,920 non-texture entries
    in the sampled drawables.
    """
    if value & SLOT_CLASS_MASK:
        return False, None
    index = value >> SLOT_INDEX_SHIFT
    if index >= slot_count:
        return False, None
    return True, index


@dataclass(frozen=True)
class Issue:
    code: str
    detail: str


@dataclass
class SlotReference:
    parameter: int
    packed: int
    index: int | None
    state: str
    target: int | None
    name_hash: int | None
    key64: int | None
    name_variant: str = ""

    def as_dict(self):
        return {
            "parameter": self.parameter,
            "packed": f"0x{self.packed:08X}",
            "index": self.index,
            "state": self.state,
            "target": self.target,
            "name_hash": None if self.name_hash is None else f"0x{self.name_hash:08X}",
            "name_variant": self.name_variant,
        }


@dataclass
class Shader:
    index: int
    texture_count: int
    parameter_count: int
    references: list = field(default_factory=list)


@dataclass
class PoolReport:
    shaders: list = field(default_factory=list)
    issues: list = field(default_factory=list)
    other_class: int = 0
    other_entries: int = 0
    other_accepted: int = 0
    pointers: dict = field(default_factory=dict)

    def add(self, code, detail):
        self.issues.append(Issue(code, detail))

    @property
    def references(self):
        return [ref for shader in self.shaders for ref in shader.references]

    @property
    def counts(self):
        result = {"shaders": len(self.shaders), "texture": 0, "index_in": 0,
                  "bound": 0, "null": 0, "bad": 0, "other_class": self.other_class,
                  "other_entries": self.other_entries,
                  "other_accepted": self.other_accepted}
        for ref in self.references:
            result["texture"] += 1
            if ref.index is not None:
                result["index_in"] += 1
            if ref.state == "bound":
                result["bound"] += 1
            elif ref.state == "null":
                result["null"] += 1
            else:
                result["bad"] += 1
        return result

    def report(self):
        return {
            "counts": self.counts,
            "pointers": self.pointers,
            "shaders": [
                {
                    "index": shader.index,
                    "texture_count": shader.texture_count,
                    "parameter_count": shader.parameter_count,
                    "references": [ref.as_dict() for ref in shader.references],
                }
                for shader in self.shaders
            ],
            "issues": [{"code": issue.code, "detail": issue.detail} for issue in self.issues],
        }


def scan_pointers(system: bytes, graphics_length: int | None = None):
    counts = {"system": 0, "graphics": 0, "system_outside": 0, "graphics_outside": 0}
    for at in range(0, len(system) - 7, 8):
        pointer = decode_pointer(_u64(system, at))
        if pointer is None:
            continue
        counts[pointer[0]] += 1
        if pointer[0] == "system" and pointer[1] >= len(system):
            counts["system_outside"] += 1
        if pointer[0] == "graphics" and graphics_length is not None and pointer[1] >= graphics_length:
            counts["graphics_outside"] += 1
    return counts


def _system_target(system, value, length, label):
    pointer = decode_pointer(value)
    if pointer is None or pointer[0] != "system":
        raise PoolReferenceError(f"{label} is not a system pointer")
    if pointer[1] + length > len(system):
        raise PoolReferenceError(f"{label} leaves the system segment")
    return pointer[1]


def parse_shader_pool(system: bytes, max_shaders: int = MAX_SHADERS,
                      max_parameters: int = MAX_PARAMETERS,
                      graphics_length: int | None = None):
    """Walk the shader group, parameter tables and slot tables.

    Raises ``PoolReferenceError`` when the header chain cannot be read or a
    count exceeds its cap. Per-reference problems are recorded as states.
    """
    if len(system) < 0x20:
        raise PoolReferenceError("the system segment is shorter than the header")
    group = _system_target(system, _u64(system, 0x10), 0x20, "the shader-group pointer")
    array = _system_target(system, _u64(system, group + 0x10), 8, "the shader-array pointer")
    count = _u16(system, group + 0x18)
    if count > max_shaders:
        raise PoolReferenceError(f"the shader count {count} exceeds the {max_shaders} cap")
    if array + 8 * count > len(system):
        raise PoolReferenceError(
            f"the {count}-entry shader array at {array:#x} leaves the "
            f"{len(system)}-byte system segment"
        )
    report = PoolReport()
    report.pointers = scan_pointers(system, graphics_length)
    for shader_index in range(count):
        shader_at = _system_target(
            system, _u64(system, array + 8 * shader_index), 0x40, f"shader {shader_index}"
        )
        slot_table = _system_target(
            system, _u64(system, shader_at + 0x10), 8, f"shader {shader_index} slot table"
        )
        parameter_table = _system_target(
            system, _u64(system, shader_at + 0x20), 8, f"shader {shader_index} parameter table"
        )
        texture_count = system[parameter_table + 1]
        parameter_count = _u16(system, parameter_table + 4)
        if texture_count > max_parameters or parameter_count > max_parameters:
            raise PoolReferenceError(
                f"shader {shader_index} declares {texture_count} texture and "
                f"{parameter_count} total parameters, above the {max_parameters} cap"
            )
        # The parameter table has parameter_count entries. A texture count above
        # it cannot be read from the declared table, so clamp the loop and report
        # the mismatch instead of reading unrelated words.
        texture_limit = min(texture_count, parameter_count)
        if parameter_count < texture_count:
            report.add(
                "parameter_count",
                f"shader {shader_index} declares {texture_count} texture parameters "
                f"but only {parameter_count} total; the loop reads {texture_limit}",
            )
        table_end = parameter_table + 8 + 8 * parameter_count
        if table_end > len(system):
            raise PoolReferenceError(f"shader {shader_index} parameter table leaves the segment")
        slot_end = slot_table + 8 * texture_limit
        if slot_end > len(system):
            raise PoolReferenceError(f"shader {shader_index} slot table leaves the segment")
        shader = Shader(shader_index, texture_count, parameter_count)
        for parameter in range(texture_limit):
            packed = _u32(system, parameter_table + 12 + 8 * parameter)
            accepted, index = decode_slot_reference(packed, texture_limit)
            if not accepted:
                state = "class" if packed & SLOT_CLASS_MASK else "index"
                shader.references.append(
                    SlotReference(parameter, packed, None, state, None, None, None)
                )
                report.add(
                    "slot_reference",
                    f"shader {shader_index} texture parameter {parameter} word "
                    f"{packed:#x} does not select a slot",
                )
                continue
            target = decode_pointer(_u64(system, slot_table + 8 * index))
            if target is None:
                state = "null" if _u64(system, slot_table + 8 * index) == 0 else "bad"
                shader.references.append(
                    SlotReference(parameter, packed, index, state, None, None, None)
                )
                if state == "bad":
                    report.add(
                        "slot_target",
                        f"shader {shader_index} slot {index} is not a segment pointer",
                    )
                continue
            if target[0] != "system" or target[1] + TEXTURE_RECORD_LEN > len(system):
                shader.references.append(
                    SlotReference(parameter, packed, index, "bad", None, None, None)
                )
                report.add(
                    "slot_target",
                    f"shader {shader_index} slot {index} is not a system texture record",
                )
                continue
            name_target = decode_pointer(_u64(system, target[1] + 0x30))
            name_hash = None
            key64 = None
            name_variant = ""
            if (
                name_target is not None
                and name_target[0] == "system"
                and name_target[1] + NAME_RECORD_LEN <= len(system)
            ):
                key64 = _u64(system, name_target[1] + 0x08)
                if _u64(system, name_target[1] + 0x10) == 6:
                    name_hash = _u32(system, name_target[1] + 0x18)
                    name_variant = "id"
                else:
                    name_variant = "other"
            shader.references.append(
                SlotReference(parameter, packed, index, "bound", target[1], name_hash,
                              key64, name_variant)
            )
        for parameter in range(texture_limit, parameter_count):
            packed = _u32(system, parameter_table + 12 + 8 * parameter)
            report.other_entries += 1
            report.other_class += int((packed & SLOT_CLASS_MASK) != 0)
            report.other_accepted += int(decode_slot_reference(packed, texture_limit)[0])
        report.shaders.append(shader)
    return report


def control_acceptance(values, slot_count: int):
    """Count values that the slot rule accepts. Used for the scalar control."""
    return sum(1 for value in values if decode_slot_reference(value, slot_count)[0])


def analyze_stored(path, offset, length, logical_size=None):
    """Reconstruct one stored row with page_reconstruct and parse its chain."""
    import page_reconstruct

    with open(path, "rb") as handle:
        handle.seek(offset)
        buffer = handle.read(length)
    if len(buffer) != length:
        raise PoolReferenceError(
            f"the entry needs {length} bytes but only {len(buffer)} are present"
        )
    layout = page_reconstruct.analyze_bytes(buffer, path, logical_size=logical_size)
    if layout.status != "complete" or layout.page_map is None:
        codes = ", ".join(issue.code for issue in layout.issues) or "no page map"
        raise PoolReferenceError(f"the stored row does not reconstruct: {codes}")
    system_size = sum(page.size for page in layout.pages if page.segment == "system")
    decoded = b"".join(chunk.data for chunk in layout.chunks)
    system = decoded[:system_size]
    return parse_shader_pool(system, graphics_length=len(decoded) - system_size), system


def print_text(report):
    counts = report["counts"]
    print(
        f"shaders:     {counts['shaders']}, texture entries {counts['texture']}, "
        f"index in range {counts['index_in']}"
    )
    print(
        f"slots:       {counts['bound']} bound, {counts['null']} null, "
        f"{counts['bad']} bad; other-class entries {counts['other_class']}"
    )
    print(
        f"pointers:    {report['pointers']['system']} system "
        f"({report['pointers']['system_outside']} outside), "
        f"{report['pointers']['graphics']} graphics "
        f"({report['pointers']['graphics_outside']} outside)"
    )
    for shader in report["shaders"]:
        print(
            f"  shader {shader['index']}: {shader['texture_count']} texture of "
            f"{shader['parameter_count']} parameters"
        )
        for ref in shader["references"]:
            name = ref["name_hash"] or (ref["name_variant"] or "-")
            print(
                f"    param {ref['parameter']:>2} packed {ref['packed']} index "
                f"{ref['index']} {ref['state']:<6} name {name}"
            )
    for issue in report["issues"]:
        print(f"issue:       {issue['code']}: {issue['detail']}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--file", required=True)
    parser.add_argument("--offset", type=lambda text: int(text, 0),
                        help="payload offset of a stored row")
    parser.add_argument("--length", type=lambda text: int(text, 0),
                        help="stored length of a stored row")
    parser.add_argument("--logical-size", type=lambda text: int(text, 0),
                        help="logical size from the RPF9 row, when known")
    parser.add_argument("--system-length", type=lambda text: int(text, 0),
                        help="system length of an already decoded resource")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.system_length is not None:
            with open(args.file, "rb") as handle:
                system = handle.read(args.system_length)
                graphics_length = max(0, len(handle.read()))
            report = parse_shader_pool(system, graphics_length=graphics_length)
        else:
            if args.offset is None or args.length is None:
                parser.error("--offset and --length are required for a stored row")
            report, _ = analyze_stored(args.file, args.offset, args.length, args.logical_size)
    except PoolReferenceError as err:
        print(f"error: {err}", file=sys.stderr)
        return 2
    out = report.report()
    if args.json:
        json.dump(out, sys.stdout, indent=2)
        print()
    else:
        print_text(out)
    return 0 if not report.issues else 1


if __name__ == "__main__":
    sys.exit(main())
