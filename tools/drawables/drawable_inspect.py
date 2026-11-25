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
        if model_array is not None:
            for index in range(count):
                pointer, value = self.system_pointer(
                    model_array.offset + 8 * index, f"{what} model pointer {index}"
                )
                if pointer is None:
                    continue
                model = self.read_model(pointer.offset, slot, index)
                if model is not None:
                    models.append(model)
        return {
            "slot": slot,
            "offset": offset,
            "model_array": self._pointer_report(model_array, model_value),
            "model_count": count,
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
        geometries = []
        if geometry_array is not None:
            for geometry_index in range(count):
                pointer, value = self.system_pointer(
                    geometry_array.offset + 8 * geometry_index,
                    f"{what} geometry pointer {geometry_index}",
                )
                if pointer is None:
                    continue
                geometry = self.read_geometry(pointer.offset, slot, index, geometry_index)
                if geometry is not None:
                    geometries.append(geometry)
        return {
            "slot": slot,
            "index": index,
            "offset": offset,
            "geometry_array": self._pointer_report(geometry_array, geometry_value),
            "geometry_count": count,
            "geometry_capacity": capacity,
            "uninterpreted_14": f"{unknown_14:#010x}",
            "aabb": self._pointer_report(aabb, aabb_value),
            "shader_indices": self._pointer_report(shader_indices, shader_value),
            "flags": f"{flags:#018x}",
            "geometries": geometries,
        }

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
            "layout_record": None,
        }
        if graphics is not None:
            marker = self.graphics_marker(graphics)
            report["graphics_marker"] = None if marker is None else marker.hex(" ")
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
        return report

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
            "uninterpreted_0a": f"{field_0a:#06x}",
            "uninterpreted_0c": f"{field_0c:#010x}",
            "constant": f"{constant:#018x}",
            "buffer": None,
        }
        if buffer_record is not None:
            report["buffer"] = self.read_index_buffer(buffer_record.offset, what)
        return report

    def read_index_buffer(self, offset: int, parent: str):
        what = f"index buffer record at {offset:#x} ({parent})"
        try:
            element_count = self.u32(offset + 0x08, self.system_len, what + " element count")
            element_unit = self.u16(offset + 0x0C, self.system_len, what + " element unit")
            graphics, graphics_value = self.graphics_pointer(offset + 0x18, what + " graphics")
            layout, layout_value = self.system_pointer(offset + 0x28, what + " layout")
        except DrawableError as err:
            self.add("index_buffer", str(err))
            return None
        declared_bytes = element_count * element_unit
        if graphics is not None and graphics.offset + declared_bytes > self.graphics_len:
            self.add(
                "index_outside_graphics",
                f"{what} declares {declared_bytes} bytes at graphics offset "
                f"{graphics.offset:#x}, past the {self.graphics_len:#x}-byte segment",
            )
        return {
            "offset": offset,
            "element_count": element_count,
            "element_unit": element_unit,
            "declared_bytes": declared_bytes,
            "graphics": self._pointer_report(graphics, graphics_value),
            "declaration": self._pointer_report(layout, layout_value),
        }

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
        if shader_list is not None:
            for index in range(count):
                pointer, value = self.system_pointer(
                    shader_list.offset + 8 * index, f"{what} shader pointer {index}"
                )
                if pointer is None:
                    continue
                shader = self.read_shader(pointer.offset, index)
                if shader is not None:
                    shaders.append(shader)
        return {
            "group": group,
            "optional": self._pointer_report(optional, optional_value),
            "shader_list": self._pointer_report(shader_list, shader_value),
            "shader_count": count,
            "shader_capacity": capacity,
            "shaders": shaders,
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
            "constant": f"{constant:#010x}",
            "first": self._pointer_report(first, first_value),
            "slot_table": self._pointer_report(slots, slots_value),
            "parameter_table": self._pointer_report(parameters, parameters_value),
            "parameters": None,
        }
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
        for index in range(texture_count):
            if index >= len(pairs):
                break
            packed = int(pairs[index]["packed"], 0)
            slot = packed // 4
            entry = {"index": index, "name": pairs[index]["name"], "packed": pairs[index]["packed"], "slot": slot, "record": None, "key": None}
            if slots is not None and slot < texture_count:
                pointer, value = self.system_pointer(slots.offset + 8 * slot, what + f" slot {slot}")
                if pointer is not None:
                    bound += 1
                    entry["record"] = self._pointer_report(pointer, value)
                    name_record, name_value = self.system_pointer(
                        pointer.offset + 0x30, what + f" texture record {slot} name"
                    )
                    if name_record is not None:
                        key = self.u64(name_record.offset + 0x08, self.system_len, what + " key")
                        entry["key"] = f"{key:#018x}"
                        keys.append(key)
            textures.append(entry)
        return {
            "offset": offset,
            "texture_count": texture_count,
            "total": total,
            "texture_parameters": textures,
            "bound": bound,
            "unbound": texture_count - bound,
            "distinct_keys": len(set(keys)),
        }

    def derive_graphics_base(self):
        """Derive a base from at least two graphics pointers landing on the marker."""
        pointers = []
        for lod in self.lods:
            for model in lod["models"]:
                for geometry in model["geometries"]:
                    record = geometry.get("vertex_buffer_record")
                    if record and record.get("graphics", {}).get("resolved"):
                        pointers.append(record["graphics"]["offset"])
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
            for index, offset in enumerate(pointers):
                base = at - offset
                if base < 0:
                    continue
                supports.setdefault(base, set()).add(index)
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
                aabb = model.get("aabb", {})
                if aabb.get("resolved"):
                    print(f"      AABB at {aabb['offset']:#x}")
    graphics_base = report.get("graphics_base")
    if graphics_base:
        print(
            f"graphics base: {graphics_base['base'] if graphics_base['base'] is not None else 'ambiguous'} "
            f"from {graphics_base['pointer_count']} pointer(s)"
        )
    materials = report.get("materials")
    if materials:
        print(f"shader group: {materials['shader_count']} shader(s), capacity {materials['shader_capacity']}")
        for shader in materials["shaders"]:
            params = shader.get("parameters") or {}
            print(
                f"  shader {shader['index']} at {shader['offset']:#x}: "
                f"{params.get('texture_count', 0)} texture parameter(s), "
                f"{params.get('total', 0)} total, {params.get('bound', 0)} bound, "
                f"{params.get('unbound', 0)} unbound, "
                f"{params.get('distinct_keys', 0)} distinct key(s)"
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
