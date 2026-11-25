#!/usr/bin/env python3
"""Inspect a decoded drawable resource: header, LOD chain, geometry and shaders.

The input is a reconstructed RAGE resource: the system segment followed by the
graphics segment. The system length must be supplied because the page map
records page counts, not byte lengths. All pointers use the 4-bit segment
selector and 28-bit offset documented in formats/resources/pointers.md.

The tool reads only. It bounds every record and reports pointers that cannot be
resolved instead of following them. Vertex attribute semantics, format codes,
material parameter meanings and 64-bit keys are not interpreted. See
formats/resources/drawables/README.md for the observed layout and its limits.
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from dataclasses import dataclass

SYSTEM_BASE = 0x5000_0000
GRAPHICS_BASE = 0x6000_0000
OFFSET_MASK = 0x0FFF_FFFF

HEADER_MIN = 0xC8
LOD_SLOT_COUNT = 4
LOD_GROUP_LEN = 0x20
MODEL_MIN_LEN = 0x38
GEOMETRY_LEN = 0x50
VERTEX_BUFFER_LEN = 0x50
INDEX_DESCRIPTOR_LEN = 0x40
INDEX_BUFFER_LEN = 0x50

AABB_RECORD_LEN = 0x20
AABB_UNION_TOLERANCE = 2e-3
DECLARATION_ENTRY_LEN = 4
MAX_DECLARATION_ENTRIES = 16
INDEX_HEADER_LEN = 12
MAX_SEQUENTIAL_CANDIDATES = 4096
MAX_SEQUENTIAL_RUN = 1 << 16

LAYOUT_SEMANTICS = 52
LAYOUT_SIZES = 0xD0
LAYOUT_FORMATS = 0x104
LAYOUT_PACKED = 0x138

SHADER_LEN = 0x40
SHADER_CONSTANT = 0x6D65_7461
PARAMETER_HEADER_LEN = 8
PARAMETER_PAIR_LEN = 8

GRAPHICS_MARKER = b"\x42\x40\x00\x00"

MAX_MODELS = 1024
MAX_GEOMETRIES = 1024
MAX_SHADERS = 256
MAX_PARAMETERS = 4096
MAX_MARKER_HITS = 1 << 20
MAX_INPUT = 512 << 20


class DrawableError(Exception):
    pass


@dataclass(frozen=True)
class Pointer:
    segment: str
    offset: int


@dataclass(frozen=True)
class Issue:
    code: str
    detail: str


def decode_pointer(value: int):
    """Decode a stored pointer, or return None when the value is not one."""
    if value >> 32:
        return None
    kind = value >> 28
    if kind == 5:
        return Pointer("system", value & OFFSET_MASK)
    if kind == 6:
        return Pointer("graphics", value & OFFSET_MASK)
    return None


class Inspector:
    def __init__(self, data: bytes, system_len: int):
        if system_len <= 0 or system_len > len(data):
            raise DrawableError(
                f"the system length {system_len} is outside the {len(data)}-byte input"
            )
        self.data = data
        self.system = data[:system_len]
        self.system_len = system_len
        self.graphics_len = len(data) - system_len
        self.issues: list[Issue] = []
        self.header = {}
        self.page_map = None
        self.lods = []
        self.materials = None
        self.graphics_base = None
        self.header_aabb = None

    def add(self, code: str, detail: str):
        self.issues.append(Issue(code, detail))

    def _slice(self, at: int, size: int, limit: int, what: str):
        if at < 0 or at + size > limit:
            raise DrawableError(
                f"{what} at {at:#x} needs {size} bytes but only "
                f"{max(0, limit - at)} are inside its segment"
            )
        return self.data[at : at + size]

    def u8(self, at: int, limit: int, what: str) -> int:
        return self._slice(at, 1, limit, what)[0]

    def u16(self, at: int, limit: int, what: str) -> int:
        return struct.unpack("<H", self._slice(at, 2, limit, what))[0]

    def u32(self, at: int, limit: int, what: str) -> int:
        return struct.unpack("<I", self._slice(at, 4, limit, what))[0]

    def u64(self, at: int, limit: int, what: str) -> int:
        return struct.unpack("<Q", self._slice(at, 8, limit, what))[0]

    def f32(self, at: int, limit: int, what: str) -> float:
        return struct.unpack("<f", self._slice(at, 4, limit, what))[0]

    def pointer(self, at: int, segment: str, what: str):
        """Return (Pointer|None, raw value) for a stored u64 slot."""
        value = self.u64(at, self.system_len, what)
        pointer = decode_pointer(value)
        if pointer is None:
            if value:
                self.add(
                    "pointer_undecodable",
                    f"{what} at {at:#x} is {value:#018x}, not a decodable "
                    f"system or graphics pointer",
                )
            return None, value
        if pointer.segment != segment:
            self.add(
                "pointer_segment",
                f"{what} at {at:#x} selects the {pointer.segment} segment, "
                f"expected {segment}",
            )
            return None, value
        limit = self.system_len if segment == "system" else self.graphics_len
        if pointer.offset >= limit:
            self.add(
                "pointer_outside",
                f"{what} at {at:#x} points to {pointer.segment} offset "
                f"{pointer.offset:#x}, outside the {limit:#x}-byte segment",
            )
            return None, value
        return pointer, value

    def array_count(self, base: int, count: int, entry_size: int, what: str) -> int:
        """Clamp a declared array to the entries that fit in the system segment."""
        if not count:
            return 0
        available = 0 if base >= self.system_len else (self.system_len - base) // entry_size
        if count > available:
            self.add(
                "array_outside",
                f"{what} at {base:#x} declares {count} entries of {entry_size} "
                f"bytes but only {available} fit in the system segment",
            )
            return available
        return count

    def system_pointer(self, at: int, what: str):
        return self.pointer(at, "system", what)

    def graphics_pointer(self, at: int, what: str):
        return self.pointer(at, "graphics", what)

    def graphics_file_offset(self, pointer: Pointer) -> int:
        return self.system_len + pointer.offset

    def graphics_marker(self, pointer: Pointer):
        at = self.graphics_file_offset(pointer)
        if at + len(GRAPHICS_MARKER) > len(self.data):
            return None
        return self.data[at : at + len(GRAPHICS_MARKER)]

    def read_header(self):
        if self.system_len < HEADER_MIN:
            self.add(
                "truncated_header",
                f"the system segment is {self.system_len} bytes; the observed "
                f"header needs at least {HEADER_MIN}",
            )
            return
        zero = self.u64(0x00, self.system_len, "header +0x00")
        if zero:
            self.add("header_zero", f"header +0x00 is {zero:#x}, expected zero")
        map_pointer, map_value = self.system_pointer(0x08, "header +0x08 page map")
        shader_pointer, shader_value = self.system_pointer(0x10, "header +0x10 shader group")
        if map_pointer is None:
            self.add("missing_pointer", "header +0x08 page map is null or unresolved")
        if shader_pointer is None:
            self.add("missing_pointer", "header +0x10 shader group is null or unresolved")
        skeleton, skeleton_value = self.system_pointer(0x18, "header +0x18 skeleton")
        bounds = {
            "centre": [self.f32(0x20 + 4 * i, self.system_len, "header centre") for i in range(3)],
            "radius": self.f32(0x2C, self.system_len, "header radius"),
            "minimum": [self.f32(0x30 + 4 * i, self.system_len, "header AABB minimum") for i in range(3)],
            "maximum": [self.f32(0x40 + 4 * i, self.system_len, "header AABB maximum") for i in range(3)],
        }
        lod_slots = []
        for slot in range(LOD_SLOT_COUNT):
            pointer, value = self.system_pointer(0x50 + 8 * slot, f"header LOD slot {slot}")
            lod_slots.append(
                {
                    "slot": slot,
                    "value": f"{value:#018x}",
                    "resolved": pointer is not None,
                    "segment": None if pointer is None else pointer.segment,
                    "offset": None if pointer is None else pointer.offset,
                }
            )
        distances = [self.f32(0x70 + 4 * i, self.system_len, "header LOD distance") for i in range(4)]
        flags = [self.u32(0x80 + 4 * i, self.system_len, "header LOD flags") for i in range(4)]
        name_pointer, name_value = self.system_pointer(0xA8, "header +0xA8 name")
        list_pointer, list_value = self.system_pointer(0xB0, "header +0xB0 list")
        trailer = self.u64(0xB8, self.system_len, "header +0xB8")
        self.header = {
            "zero": zero,
            "page_map": self._pointer_report(map_pointer, map_value),
            "shader_group": self._pointer_report(shader_pointer, shader_value),
            "skeleton": self._pointer_report(skeleton, skeleton_value),
            "bounds": bounds,
            "lod_slots": lod_slots,
            "lod_distances": distances,
            "lod_flags": flags,
            "name": self._pointer_report(name_pointer, name_value),
            "optional_list": self._pointer_report(list_pointer, list_value),
            "uninterpreted": {
                "+0xB8": f"{trailer:#018x}",
                "+0xC0": f"{self.u64(0xC0, self.system_len, 'header +0xC0'):#018x}",
            },
        }
        if map_pointer is not None:
            self.read_page_map(map_pointer.offset)

    def read_page_map(self, offset: int):
        try:
            system_pages = self.u8(offset + 8, self.system_len, "page map system count")
            graphics_pages = self.u8(offset + 9, self.system_len, "page map graphics count")
        except DrawableError as err:
            self.add("page_map", str(err))
            return
        self.page_map = {
            "offset": offset,
            "system_pages": system_pages,
            "graphics_pages": graphics_pages,
        }

    @staticmethod
    def _pointer_report(pointer, value):
        if pointer is None:
            return {"value": f"{value:#018x}", "resolved": False}
        return {
            "value": f"{value:#018x}",
            "resolved": True,
            "segment": pointer.segment,
            "offset": pointer.offset,
        }

    def walk(self):
        self.read_header()
        if self.system_len < HEADER_MIN:
            return
        for slot in self.header["lod_slots"]:
            if not slot["resolved"]:
                continue
            group = self.read_lod_group(slot["offset"], slot["slot"])
            if group is not None:
                self.lods.append(group)
        self.materials = self.read_materials()
        self.graphics_base = self.derive_graphics_base()
        self.header_aabb = self.header_aabb_union()

    def header_aabb_union(self):
        """Union of all walked model aggregates against the header AABB."""
        if not self.header:
            return None
        aggregates = [
            model["aabb_aggregate"]
            for lod in self.lods
            for model in lod["models"]
            if model.get("aabb_aggregate")
        ]
        if not aggregates:
            return None
        minimum = [min(record["minimum"][axis] for record in aggregates) for axis in range(3)]
        maximum = [max(record["maximum"][axis] for record in aggregates) for axis in range(3)]
        bounds = self.header["bounds"]
        delta = max(
            max(abs(minimum[axis] - bounds["minimum"][axis]) for axis in range(3)),
            max(abs(maximum[axis] - bounds["maximum"][axis]) for axis in range(3)),
        )
        return {
            "minimum": minimum,
            "maximum": maximum,
            "delta": delta,
            "matches": delta <= AABB_UNION_TOLERANCE,
            "model_count": len(aggregates),
            "null_lod_slots": sum(1 for slot in self.header["lod_slots"] if not slot["resolved"]),
        }

    def read_lod_group(self, offset: int, slot: int):
        what = f"LOD group {slot} at {offset:#x}"
        try:
            model_array, model_value = self.system_pointer(offset + 0x00, what + " model array")
            count = self.u16(offset + 0x08, self.system_len, what + " count")
            capacity = self.u16(offset + 0x0A, self.system_len, what + " capacity")
            shader_indices = self.u64(offset + 0x10, self.system_len, what + " shader indices")
            marker = self.u64(offset + 0x18, self.system_len, what + " tail")
        except DrawableError as err:
            self.add("lod_group", str(err))
            return None
        if count > MAX_MODELS:
            self.add("lod_count", f"{what} declares {count} models, above the {MAX_MODELS} cap")
            return None
        models = []
        array_count = 0
        if model_array is not None:
            array_count = self.array_count(model_array.offset, count, 8, what + " model array")
            for index in range(array_count):
                try:
                    pointer, value = self.system_pointer(
                        model_array.offset + 8 * index, f"{what} model pointer {index}"
                    )
                except DrawableError as err:
                    self.add("pointer_read", str(err))
                    break
                if pointer is None:
                    continue
                model = self.read_model(pointer.offset, slot, index)
                if model is not None:
                    models.append(model)
        elif count:
            self.add("missing_pointer", f"{what} has {count} model(s) but no model array pointer")
        return {
            "slot": slot,
            "offset": offset,
            "model_array": self._pointer_report(model_array, model_value),
            "model_count": count,
            "model_array_entries": array_count,
            "model_capacity": capacity,
            "shader_indices": [shader_indices & 0xFFFF, (shader_indices >> 16) & 0xFFFF],
            "tail": f"{marker:#018x}",
            "models": models,
        }

    def read_model(self, offset: int, slot: int, index: int):
        what = f"model {index} in LOD {slot} at {offset:#x}"
        try:
            geometry_array, geometry_value = self.system_pointer(offset + 0x08, what + " geometry array")
            count = self.u16(offset + 0x10, self.system_len, what + " geometry count")
            capacity = self.u16(offset + 0x12, self.system_len, what + " geometry capacity")
            unknown_14 = self.u32(offset + 0x14, self.system_len, what + " +0x14")
            aabb, aabb_value = self.system_pointer(offset + 0x18, what + " AABB")
            shader_indices, shader_value = self.system_pointer(offset + 0x20, what + " shader indices")
            flags = self.u64(offset + 0x30, self.system_len, what + " flags")
        except DrawableError as err:
            self.add("model", str(err))
            return None
        if count > MAX_GEOMETRIES:
            self.add("model_count", f"{what} declares {count} geometries, above the {MAX_GEOMETRIES} cap")
            return None
        aabb_report = self.read_model_aabb(aabb, count, what) if aabb is not None else None
        geometries = []
        array_count = 0
        if geometry_array is not None:
            array_count = self.array_count(geometry_array.offset, count, 8, what + " geometry array")
            for geometry_index in range(array_count):
                try:
                    pointer, value = self.system_pointer(
                        geometry_array.offset + 8 * geometry_index,
                        f"{what} geometry pointer {geometry_index}",
                    )
                except DrawableError as err:
                    self.add("pointer_read", str(err))
                    break
                if pointer is None:
                    continue
                geometry = self.read_geometry(pointer.offset, slot, index, geometry_index)
                if geometry is not None:
                    geometries.append(geometry)
        elif count:
            self.add("missing_pointer", f"{what} has {count} geometry(ies) but no geometry array pointer")
        union = self._aabb_union(aabb_report, count)
        if union is False:
            self.add("aabb_union", f"{what} aggregate AABB does not equal the union of its geometry records")
        return {
            "slot": slot,
            "index": index,
            "offset": offset,
            "geometry_array": self._pointer_report(geometry_array, geometry_value),
            "geometry_count": count,
            "geometry_array_entries": array_count,
            "geometry_capacity": capacity,
            "uninterpreted_14": f"{unknown_14:#010x}",
            "aabb": self._pointer_report(aabb, aabb_value),
            "aabb_record_count": None if aabb_report is None else len(aabb_report),
            "aabb_aggregate": None if not aabb_report else aabb_report[0],
            "aabb_records": aabb_report,
            "aabb_union_matches": union,
            "shader_indices": self._pointer_report(shader_indices, shader_value),
            "flags": f"{flags:#018x}",
            "geometries": geometries,
        }

    def read_model_aabb(self, aabb, count: int, what: str):
        """Read record0 plus one record per geometry. A one-geometry model has one record."""
        if count <= 0:
            return []
        length = 1 if count == 1 else count + 1
        records = []
        for index in range(length):
            at = aabb.offset + AABB_RECORD_LEN * index
            try:
                values = [self.f32(at + 4 * i, self.system_len, what + " AABB") for i in range(8)]
            except DrawableError as err:
                self.add("aabb", str(err))
                break
            records.append(
                {
                    "minimum": values[0:3],
                    "maximum": values[4:7],
                    "min_extra": values[3],
                    "max_extra": values[7],
                }
            )
        return records

    @staticmethod
    def _aabb_union(records, count: int):
        if not records or count <= 0:
            return None
        if count == 1:
            return True
        if len(records) != count + 1:
            return None
        aggregate = records[0]
        minimum = [min(record["minimum"][axis] for record in records[1:]) for axis in range(3)]
        maximum = [max(record["maximum"][axis] for record in records[1:]) for axis in range(3)]
        return all(
            abs(minimum[axis] - aggregate["minimum"][axis]) <= AABB_UNION_TOLERANCE
            for axis in range(3)
        ) and all(
            abs(maximum[axis] - aggregate["maximum"][axis]) <= AABB_UNION_TOLERANCE
            for axis in range(3)
        )

    def read_geometry(self, offset: int, slot: int, model_index: int, geometry_index: int):
        what = f"geometry {geometry_index} of model {model_index} in LOD {slot} at {offset:#x}"
        try:
            vertex_buffer, vertex_value = self.system_pointer(offset + 0x08, what + " vertex buffer")
            tag = self.u64(offset + 0x30, self.system_len, what + " +0x30")
            index_descriptor, index_value = self.system_pointer(offset + 0x40, what + " index descriptor")
        except DrawableError as err:
            self.add("geometry", str(err))
            return None
        report = {
            "offset": offset,
            "vertex_buffer": self._pointer_report(vertex_buffer, vertex_value),
            "uninterpreted_30": f"{tag:#018x}",
            "index_descriptor": self._pointer_report(index_descriptor, index_value),
            "vertex_buffer_record": None,
            "index_descriptor_record": None,
        }
        if vertex_buffer is None and vertex_value == 0:
            self.add("missing_pointer", f"{what} has no vertex buffer pointer")
        if index_descriptor is None and index_value == 0:
            self.add("missing_pointer", f"{what} has no index descriptor pointer")
        if vertex_buffer is not None:
            report["vertex_buffer_record"] = self.read_vertex_buffer(vertex_buffer.offset, what)
        if index_descriptor is not None:
            report["index_descriptor_record"] = self.read_index_descriptor(index_descriptor.offset, what)
        return report

    def read_vertex_buffer(self, offset: int, parent: str):
        what = f"vertex buffer at {offset:#x} ({parent})"
        try:
            element_count = self.u32(offset + 0x08, self.system_len, what + " element count")
            element_unit = self.u16(offset + 0x0C, self.system_len, what + " element unit")
            unit_tail = self.u16(offset + 0x0E, self.system_len, what + " +0x0e")
            constant_10 = self.u32(offset + 0x10, self.system_len, what + " +0x10")
            graphics, graphics_value = self.graphics_pointer(offset + 0x18, what + " graphics")
            declaration, declaration_value = self.system_pointer(offset + 0x28, what + " declaration")
            layout, layout_value = self.system_pointer(offset + 0x40, what + " layout")
        except DrawableError as err:
            self.add("vertex_buffer", str(err))
            return None
        declared_bytes = element_count * element_unit
        report = {
            "offset": offset,
            "element_count": element_count,
            "element_unit": element_unit,
            "unit_tail": unit_tail,
            "uninterpreted_10": f"{constant_10:#010x}",
            "graphics": self._pointer_report(graphics, graphics_value),
            "declaration": self._pointer_report(declaration, declaration_value),
            "layout": self._pointer_report(layout, layout_value),
            "declared_bytes": declared_bytes,
            "graphics_marker": None,
            "declaration_table": None,
            "layout_record": None,
        }
        if graphics is None and graphics_value == 0:
            self.add("missing_pointer", f"{what} has no graphics pointer")
        if layout is None and layout_value == 0:
            self.add("missing_pointer", f"{what} has no layout pointer")
        if graphics is not None:
            marker = self.graphics_marker(graphics)
            report["graphics_marker"] = None if marker is None else marker.hex(" ")
            report["declaration_table"] = self.read_declaration(graphics.offset, what)
            if graphics.offset + declared_bytes > self.graphics_len:
                self.add(
                    "buffer_outside_graphics",
                    f"{what} declares {declared_bytes} bytes at graphics offset "
                    f"{graphics.offset:#x}, past the {self.graphics_len:#x}-byte segment",
                )
        if layout is not None:
            report["layout_record"] = self.read_layout(layout.offset, what)
            layout_record = report["layout_record"]
            if layout_record is not None:
                if layout_record["attribute_end"] > declared_bytes:
                    self.add(
                        "buffer_size",
                        f"{what} declares {declared_bytes} bytes but an attribute "
                        f"ends at {layout_record['attribute_end']}",
                    )
                elif layout_record["attribute_end"] != declared_bytes:
                    self.add(
                        "buffer_size",
                        f"{what} declares {declared_bytes} bytes but the attributes "
                        f"end at {layout_record['attribute_end']}",
                    )
                self.check_declaration(report["declaration_table"], layout_record, what)
        return report

    def read_declaration(self, graphics_offset: int, parent: str):
        """The graphics prefix starts with u32 entries of format and offset/2."""
        entries = []
        at = self.system_len + graphics_offset
        for index in range(MAX_DECLARATION_ENTRIES):
            if at + DECLARATION_ENTRY_LEN * (index + 1) > len(self.data):
                break
            value = self.u32(at + DECLARATION_ENTRY_LEN * index, len(self.data), parent + " declaration")
            if value == 0:
                break
            entries.append({"format": f"{value & 0xFF:#04x}", "offset": (value >> 8) * 2})
        return entries

    def check_declaration(self, entries, layout_record, what: str):
        if not entries:
            return
        layout_offsets = {attribute["offset"] for attribute in layout_record["attributes"]}
        for index, entry in enumerate(entries):
            if entry["offset"] not in layout_offsets:
                self.add(
                    "declaration",
                    f"{what} declaration entry {index} names offset {entry['offset']:#x}, "
                    f"which is not a present layout attribute",
                )

    def read_layout(self, offset: int, parent: str):
        what = f"layout at {offset:#x} ({parent})"
        try:
            offsets = [self.u32(offset + 4 * i, self.system_len, what + " offset") for i in range(LAYOUT_SEMANTICS)]
            sizes = [self.u8(offset + LAYOUT_SIZES + i, self.system_len, what + " size") for i in range(LAYOUT_SEMANTICS)]
            formats = [self.u8(offset + LAYOUT_FORMATS + i, self.system_len, what + " format") for i in range(LAYOUT_SEMANTICS)]
            packed = self.u32(offset + LAYOUT_PACKED, self.system_len, what + " packed count")
        except DrawableError as err:
            self.add("layout", str(err))
            return None
        vertex_count = packed >> 10
        attributes = []
        end = 0
        stride = 0
        for index in range(LAYOUT_SEMANTICS):
            if sizes[index] == 0 and formats[index] == 0:
                continue
            attribute_end = offsets[index] + sizes[index] * vertex_count
            end = max(end, attribute_end)
            stride += sizes[index]
            attributes.append(
                {
                    "semantic": index,
                    "offset": offsets[index],
                    "size": sizes[index],
                    "format": f"{formats[index]:#04x}",
                }
            )
        return {
            "offset": offset,
            "packed": f"{packed:#010x}",
            "vertex_count": vertex_count,
            "flags": packed & 0x3FF,
            "attributes": attributes,
            "attribute_stride": stride,
            "attribute_end": end,
        }

    def read_index_descriptor(self, offset: int, parent: str):
        what = f"index descriptor at {offset:#x} ({parent})"
        try:
            buffer_record, buffer_value = self.system_pointer(offset + 0x00, what + " buffer record")
            clusters = self.u16(offset + 0x08, self.system_len, what + " cluster count")
            field_0a = self.u16(offset + 0x0A, self.system_len, what + " +0x0a")
            field_0c = self.u32(offset + 0x0C, self.system_len, what + " +0x0c")
            constant = self.u64(offset + 0x30, self.system_len, what + " +0x30")
        except DrawableError as err:
            self.add("index_descriptor", str(err))
            return None
        report = {
            "offset": offset,
            "buffer_record": self._pointer_report(buffer_record, buffer_value),
            "cluster_count": clusters,
            "index_count_a": field_0a,
            "index_count_b_raw": f"{field_0c:#010x}",
            "index_count_b": (field_0c >> 8) & 0xFFFF,
            "constant": f"{constant:#018x}",
            "buffer": None,
        }
        if buffer_record is None and buffer_value == 0:
            self.add("missing_pointer", f"{what} has no index-buffer record pointer")
        if buffer_record is not None:
            report["buffer"] = self.read_index_buffer(
                buffer_record.offset, what, clusters, field_0a, (field_0c >> 8) & 0xFFFF
            )
        return report

    def read_index_buffer(self, offset: int, parent: str, clusters: int, count_a: int, count_b: int):
        what = f"index buffer record at {offset:#x} ({parent})"
        try:
            element_count = self.u32(offset + 0x08, self.system_len, what + " element count")
            element_unit = self.u16(offset + 0x0C, self.system_len, what + " element unit")
            graphics, graphics_value = self.graphics_pointer(offset + 0x18, what + " graphics")
            pointer_28, pointer_28_value = self.system_pointer(offset + 0x28, what + " +0x28")
        except DrawableError as err:
            self.add("index_buffer", str(err))
            return None
        declared_bytes = element_count * element_unit
        report = {
            "offset": offset,
            "element_count": element_count,
            "element_unit": element_unit,
            "declared_bytes": declared_bytes,
            "graphics": self._pointer_report(graphics, graphics_value),
            "uninterpreted_28": self._pointer_report(pointer_28, pointer_28_value),
            "header": None,
            "header_matches_descriptor": None,
            "sequential_run_length": None,
            "sequential_run_in_range": None,
        }
        if graphics is None and graphics_value == 0:
            self.add("missing_pointer", f"{what} has no graphics pointer")
        if graphics is None:
            return report
        if graphics.offset + declared_bytes > self.graphics_len:
            self.add(
                "index_outside_graphics",
                f"{what} declares {declared_bytes} bytes at graphics offset "
                f"{graphics.offset:#x}, past the {self.graphics_len:#x}-byte segment",
            )
            return report
        at = self.system_len + graphics.offset
        if declared_bytes >= INDEX_HEADER_LEN:
            header = [self.u32(at + 4 * index, len(self.data), what + " header") for index in range(3)]
            report["header"] = {
                "marker": f"{header[0]:#010x}",
                "count_a": header[1],
                "count_b": header[2],
            }
            report["header_matches_descriptor"] = (
                (header[0] & 0x8000_0000) != 0
                and (header[0] & 0x7FFF_FFFF) == clusters
                and header[1] == count_a
                and header[2] == count_b
            )
            if not report["header_matches_descriptor"]:
                self.add(
                    "index_header",
                    f"{what} header {header[0]:#x}/{header[1]}/{header[2]} does not match "
                    f"descriptor clusters {clusters} and counts {count_a}/{count_b}",
                )
        report["sequential_run_length"] = self.find_sequential_run(at, declared_bytes, count_b)
        if report["sequential_run_length"] is not None:
            report["sequential_run_in_range"] = (
                report["sequential_run_length"] > 0
                and report["sequential_run_length"] <= MAX_SEQUENTIAL_RUN
            )
        return report

    def find_sequential_run(self, at: int, length: int, vertex_count: int):
        """Length of the leading 0,1,2,... run found in the u16 view of the buffer."""
        if vertex_count <= 0 or length < 2:
            return 0
        limit = at + min(length, 2 * MAX_SEQUENTIAL_RUN)
        best = 0
        candidates = 0
        position = at
        while position + 2 <= limit and candidates < MAX_SEQUENTIAL_CANDIDATES:
            if self.u16(position, len(self.data), "index") == 0:
                candidates += 1
                run = 0
                while (
                    run < vertex_count
                    and position + 2 * (run + 1) <= limit
                    and self.u16(position + 2 * run, len(self.data), "index") == run
                ):
                    run += 1
                best = max(best, run)
                if best >= vertex_count:
                    break
            position += 2
        return best

    def read_materials(self):
        header = self.header.get("shader_group")
        if not header or not header.get("resolved"):
            return None
        group = header["offset"]
        what = f"shader group at {group:#x}"
        try:
            optional, optional_value = self.system_pointer(group + 0x08, what + " +0x08")
            shader_list, shader_value = self.system_pointer(group + 0x10, what + " shader list")
            count = self.u16(group + 0x18, self.system_len, what + " count")
            capacity = self.u16(group + 0x1A, self.system_len, what + " capacity")
        except DrawableError as err:
            self.add("shader_group", str(err))
            return None
        if count > MAX_SHADERS:
            self.add("shader_count", f"{what} declares {count} shaders, above the {MAX_SHADERS} cap")
            return None
        shaders = []
        array_count = 0
        if shader_list is not None:
            array_count = self.array_count(shader_list.offset, count, 8, what + " shader array")
            for index in range(array_count):
                try:
                    pointer, value = self.system_pointer(
                        shader_list.offset + 8 * index, f"{what} shader pointer {index}"
                    )
                except DrawableError as err:
                    self.add("pointer_read", str(err))
                    break
                if pointer is None:
                    continue
                shader = self.read_shader(pointer.offset, index)
                if shader is not None:
                    shaders.append(shader)
        elif count:
            self.add("missing_pointer", f"{what} has {count} shader(s) but no shader array pointer")
        keys = {"declared": 0, "bound": 0, "unbound": 0, "null_key": 0, "bound_with_key": 0,
                "join_attempted": False, "resolved": None}
        for shader in shaders:
            parameters = shader.get("parameters")
            if not parameters:
                continue
            for name in ("declared", "bound", "unbound", "null_key", "bound_with_key"):
                keys[name] += parameters["keys"][name]
        return {
            "group": group,
            "optional": self._pointer_report(optional, optional_value),
            "shader_list": self._pointer_report(shader_list, shader_value),
            "shader_count": count,
            "shader_array_entries": array_count,
            "shader_capacity": capacity,
            "shaders": shaders,
            "keys": keys,
        }

    def read_shader(self, offset: int, index: int):
        what = f"shader {index} at {offset:#x}"
        try:
            tag = self.u32(offset + 0x00, self.system_len, what + " +0x00")
            constant = self.u32(offset + 0x04, self.system_len, what + " +0x04")
            first, first_value = self.system_pointer(offset + 0x08, what + " +0x08")
            slots, slots_value = self.system_pointer(offset + 0x10, what + " slot table")
            parameters, parameters_value = self.system_pointer(offset + 0x20, what + " parameter table")
        except DrawableError as err:
            self.add("shader", str(err))
            return None
        if constant != SHADER_CONSTANT:
            self.add("shader_constant", f"{what} +0x04 is {constant:#010x}, expected {SHADER_CONSTANT:#010x}")
        report = {
            "index": index,
            "offset": offset,
            "uninterpreted_00": f"{tag:#010x}",
            "shader_hash": f"{tag:#010x}",
            "constant": f"{constant:#010x}",
            "first": self._pointer_report(first, first_value),
            "slot_table": self._pointer_report(slots, slots_value),
            "parameter_table": self._pointer_report(parameters, parameters_value),
            "parameters": None,
        }
        if parameters is None and parameters_value == 0:
            self.add("missing_pointer", f"{what} has no parameter table pointer")
        if parameters is not None:
            report["parameters"] = self.read_parameters(parameters.offset, slots, what)
        return report

    def read_parameters(self, offset: int, slots, parent: str):
        what = f"parameter table at {offset:#x} ({parent})"
        try:
            texture_count = self.u8(offset + 0x01, self.system_len, what + " texture count")
            total = self.u16(offset + 0x04, self.system_len, what + " total")
        except DrawableError as err:
            self.add("parameter_table", str(err))
            return None
        if total > MAX_PARAMETERS:
            self.add("parameter_count", f"{what} declares {total} parameters, above the {MAX_PARAMETERS} cap")
            return None
        if texture_count > total:
            self.add(
                "parameter_count",
                f"{what} declares {texture_count} texture parameters of {total} total",
            )
        pairs = []
        for index in range(total):
            at = offset + PARAMETER_HEADER_LEN + PARAMETER_PAIR_LEN * index
            try:
                name = self.u32(at, self.system_len, what + " parameter name")
                packed = self.u32(at + 4, self.system_len, what + " parameter value")
            except DrawableError as err:
                self.add("parameter_table", str(err))
                break
            pairs.append({"name": f"{name:#010x}", "packed": f"{packed:#010x}"})
        textures = []
        keys = []
        bound = 0
        null_keys = 0
        slot_limit = 0
        if slots is not None:
            slot_limit = self.array_count(slots.offset, texture_count, 8, what + " slot table")
        elif texture_count:
            self.add(
                "missing_pointer",
                f"{what} declares {texture_count} texture parameter(s) but no slot table",
            )
        for index in range(texture_count):
            if index >= len(pairs):
                break
            packed = int(pairs[index]["packed"], 0)
            slot = packed // 4
            entry = {
                "index": index,
                "name": pairs[index]["name"],
                "packed": pairs[index]["packed"],
                "slot": slot,
                "record": None,
                "key": "0x0000000000000000",
                "key_status": "unbound",
            }
            if slots is not None and slot < slot_limit:
                try:
                    pointer, value = self.system_pointer(
                        slots.offset + 8 * slot, what + f" slot {slot}"
                    )
                except DrawableError as err:
                    self.add("pointer_read", str(err))
                    break
                if pointer is not None:
                    bound += 1
                    entry["record"] = self._pointer_report(pointer, value)
                    entry["key_status"] = "unresolved"
                    try:
                        name_record, _ = self.system_pointer(
                            pointer.offset + 0x30, what + f" texture record {slot} name"
                        )
                        if name_record is not None:
                            key = self.u64(name_record.offset + 0x08, self.system_len, what + " key")
                            entry["key"] = f"{key:#018x}"
                            if key == 0:
                                entry["key_status"] = "null"
                                null_keys += 1
                            else:
                                keys.append(key)
                    except DrawableError as err:
                        self.add("pointer_read", str(err))
            textures.append(entry)
        unresolved = bound - null_keys
        return {
            "offset": offset,
            "texture_count": texture_count,
            "total": total,
            "texture_parameters": textures,
            "slot_table_entries": slot_limit,
            "bound": bound,
            "unbound": texture_count - bound,
            "distinct_keys": len(set(keys)),
            "keys": {
                "declared": texture_count,
                "bound": bound,
                "unbound": texture_count - bound,
                "null_key": null_keys,
                "bound_with_key": unresolved,
                "join_attempted": False,
                "resolved": None,
            },
        }

    def derive_graphics_base(self):
        """Derive a base from at least two distinct graphics pointers landing on the marker."""
        pointers = set()
        for lod in self.lods:
            for model in lod["models"]:
                for geometry in model["geometries"]:
                    record = geometry.get("vertex_buffer_record")
                    if record and record.get("graphics", {}).get("resolved"):
                        pointers.add(record["graphics"]["offset"])
        pointers = sorted(pointers)
        if len(pointers) < 2:
            return None
        supports = {}
        marker = GRAPHICS_MARKER
        start = 0
        hits = 0
        while True:
            at = self.data.find(marker, start)
            if at < 0 or hits >= MAX_MARKER_HITS:
                break
            hits += 1
            for offset in pointers:
                base = at - offset
                if base < 0:
                    continue
                supports.setdefault(base, set()).add(offset)
            start = at + 1
        candidates = {base: found for base, found in supports.items() if len(found) >= 2}
        if not candidates:
            return None
        if self.system_len in candidates:
            base = self.system_len
        elif len(candidates) == 1:
            base = next(iter(candidates))
        else:
            base = None
        return {
            "base": base,
            "candidates": {f"{value:#x}": len(found) for value, found in sorted(candidates.items())},
            "pointer_count": len(pointers),
            "marker": marker.hex(" "),
        }

    def report(self):
        status = "complete"
        if any(issue.code in ("truncated_header", "header_zero") for issue in self.issues):
            status = "unverified"
        elif self.issues:
            status = "partial"
        return {
            "system_size": self.system_len,
            "graphics_size": self.graphics_len,
            "status": status,
            "page_map": self.page_map,
            "header": self.header,
            "header_aabb_union": self.header_aabb,
            "lod_slots": self.lods,
            "materials": self.materials,
            "graphics_base": self.graphics_base,
            "issues": [{"code": issue.code, "detail": issue.detail} for issue in self.issues],
        }


def analyze(path, system_len):
    with open(path, "rb") as handle:
        data = handle.read(MAX_INPUT + 1)
    if len(data) > MAX_INPUT:
        return {
            "system_size": system_len,
            "status": "unverified",
            "issues": [{"code": "input_cap", "detail": f"the input exceeds the {MAX_INPUT}-byte cap"}],
        }
    try:
        inspector = Inspector(data, system_len)
    except DrawableError as err:
        return {"system_size": system_len, "status": "unverified", "issues": [{"code": "size", "detail": str(err)}]}
    inspector.walk()
    return inspector.report()


def print_text(report):
    print(f"status:      {report['status']}")
    print(f"system:      {report['system_size']} bytes")
    print(f"graphics:    {report['graphics_size']} bytes")
    page_map = report.get("page_map")
    if page_map:
        print(
            f"page map:    at {page_map['offset']:#x}, {page_map['system_pages']} system "
            f"and {page_map['graphics_pages']} graphics pages"
        )
    header = report.get("header") or {}
    if header:
        bounds = header["bounds"]
        print(
            "bounds:      centre "
            + ", ".join(f"{value:.6g}" for value in bounds["centre"])
            + f"; radius {bounds['radius']:.6g}"
        )
        print(
            "             min "
            + ", ".join(f"{value:.6g}" for value in bounds["minimum"])
            + "; max "
            + ", ".join(f"{value:.6g}" for value in bounds["maximum"])
        )
        print("LOD distances: " + ", ".join(f"{value:.6g}" for value in header["lod_distances"]))
    for lod in report.get("lod_slots", []):
        print(
            f"LOD {lod['slot']}:     {lod['model_count']} model(s), "
            f"capacity {lod['model_capacity']}, group at {lod['offset']:#x}"
        )
        for model in lod["models"]:
            print(
                f"  model {model['index']}: {model['geometry_count']} geometry(ies), "
                f"geometry list at {model['geometry_array'].get('offset', 0):#x}"
            )
            for geometry in model["geometries"]:
                record = geometry.get("vertex_buffer_record") or {}
                layout = record.get("layout_record") or {}
                print(
                    f"    geometry {geometry['offset']:#x}: vertex buffer "
                    f"{record.get('offset', 0):#x}, {record.get('declared_bytes', 0)} bytes, "
                    f"{layout.get('vertex_count', 0)} vertices, "
                    f"{len(layout.get('attributes', []))} attribute(s), "
                    f"graphics {record.get('graphics', {}).get('offset', 0):#x}"
                )
                descriptor = geometry.get("index_descriptor_record") or {}
                index_buffer = descriptor.get("buffer") or {}
                if index_buffer:
                    print(
                        f"      index buffer: {index_buffer.get('element_count', 0)} element(s), "
                        f"{index_buffer.get('declared_bytes', 0)} bytes, "
                        f"header match {index_buffer.get('header_matches_descriptor')}, "
                        f"sequential run {index_buffer.get('sequential_run_length')}"
                    )
                aabb = model.get("aabb", {})
                if aabb.get("resolved"):
                    print(f"      AABB at {aabb['offset']:#x}, records {model.get('aabb_record_count')}, "
                          f"union {model.get('aabb_union_matches')}")
    graphics_base = report.get("graphics_base")
    if graphics_base:
        base = graphics_base["base"]
        shown = "ambiguous" if base is None else f"{base:#x}"
        print(f"graphics base: {shown} from {graphics_base['pointer_count']} pointer(s)")
    materials = report.get("materials")
    if materials:
        print(f"shader group: {materials['shader_count']} shader(s), capacity {materials['shader_capacity']}")
        for shader in materials["shaders"]:
            params = shader.get("parameters") or {}
            print(
                f"  shader {shader['index']} at {shader['offset']:#x}: hash {shader['shader_hash']}, "
                f"{params.get('texture_count', 0)} texture parameter(s), "
                f"{params.get('total', 0)} total, {params.get('bound', 0)} bound, "
                f"{params.get('unbound', 0)} unbound, "
                f"{params.get('distinct_keys', 0)} distinct key(s)"
            )
        join = materials["keys"]
        resolved = "not attempted" if join["resolved"] is None else join["resolved"]
        print(
            f"  keys: {join['bound']} bound ({join['bound_with_key']} with key, "
            f"{join['null_key']} null), {join['unbound']} unbound, resolved {resolved}"
        )
    for issue in report.get("issues", []):
        print(f"issue:       {issue['code']}: {issue['detail']}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="mode", required=True)
    inspect = sub.add_parser("inspect", help="inspect a decoded drawable resource")
    inspect.add_argument("--file", required=True, help="decoded resource: system segment then graphics segment")
    inspect.add_argument("--system-length", required=True, type=lambda text: int(text, 0),
                         help="bytes of system data before the graphics segment")
    inspect.add_argument("--json", action="store_true", help="print the report as JSON")
    args = parser.parse_args(argv)
    report = analyze(args.file, args.system_length)
    if args.json:
        json.dump(report, sys.stdout, indent=2)
        print()
    else:
        print_text(report)
    return 0 if report["status"] == "complete" else 1


if __name__ == "__main__":
    sys.exit(main())
