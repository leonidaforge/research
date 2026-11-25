"""Synthetic tests for drawable_inspect.py. No game files are used."""

import os
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import drawable_inspect as di  # noqa: E402

SYSTEM_SIZE = 0x3000
GRAPHICS_SIZE = 0x2000


class Fixture:
    def __init__(self):
        self.system = bytearray(SYSTEM_SIZE)
        self.graphics = bytearray(GRAPHICS_SIZE)
        self.cursor = 0x100
        self.graphics_cursor = 0

    def alloc(self, size, align=8):
        self.cursor = (self.cursor + align - 1) & ~(align - 1)
        at = self.cursor
        self.cursor += size
        if self.cursor > len(self.system):
            raise AssertionError("synthetic system segment is full")
        return at

    def graphics_alloc(self, size, align=8):
        self.graphics_cursor = (self.graphics_cursor + align - 1) & ~(align - 1)
        at = self.graphics_cursor
        self.graphics_cursor += size
        if self.graphics_cursor > len(self.graphics):
            raise AssertionError("synthetic graphics segment is full")
        return at

    def u16(self, at, value):
        struct.pack_into("<H", self.system, at, value)

    def u32(self, at, value):
        struct.pack_into("<I", self.system, at, value)

    def u64(self, at, value):
        struct.pack_into("<Q", self.system, at, value)

    def f32(self, at, value):
        struct.pack_into("<f", self.system, at, value)

    def system_pointer(self, at, offset):
        self.u64(at, di.SYSTEM_BASE | offset)

    def graphics_pointer(self, at, offset):
        self.u64(at, di.GRAPHICS_BASE | offset)

    def layout(self, at, attributes, vertices, packed):
        for semantic in range(di.LAYOUT_SEMANTICS):
            self.u32(at + 4 * semantic, 0x80)
            self.system[at + di.LAYOUT_SIZES + semantic] = 0
            self.system[at + di.LAYOUT_FORMATS + semantic] = 0
        for semantic, offset, size, fmt in attributes:
            self.u32(at + 4 * semantic, offset)
            self.system[at + di.LAYOUT_SIZES + semantic] = size
            self.system[at + di.LAYOUT_FORMATS + semantic] = fmt
        self.u32(at + di.LAYOUT_PACKED, (vertices << 10) | packed)

    def geometry(self, at, index):
        vertex_buffer = self.alloc(di.VERTEX_BUFFER_LEN)
        self.system_pointer(at + 0x08, vertex_buffer)
        self.u64(at + 0x30, 0x1122334455667788 + index)
        descriptor = self.alloc(di.INDEX_DESCRIPTOR_LEN)
        self.system_pointer(at + 0x40, descriptor)

        layout = self.alloc(0x140)
        if index == 0:
            count, vertices, attribute_bytes = 192, 32, 0x300
            attributes = [
                (0, 0x80, 8, 0x10),
                (4, 0x180, 4, 0x29),
                (24, 0x200, 4, 0x1C),
                (28, 0x280, 4, 0x26),
            ]
            packed = 0x51
        else:
            count, vertices, attribute_bytes = 56, 4, 0xE0
            attributes = [
                (0, 0x80, 8, 0x10),
                (4, 0xA0, 4, 0x29),
                (24, 0xB0, 4, 0x1C),
                (28, 0xC0, 4, 0x26),
                (29, 0xD0, 4, 0x26),
            ]
            packed = 0x61
        self.layout(layout, attributes, vertices, packed)

        graphics_at = self.graphics_alloc(count * 4)
        self.graphics[graphics_at : graphics_at + 4] = di.GRAPHICS_MARKER
        self.u32(vertex_buffer + 0x08, count)
        self.u16(vertex_buffer + 0x0C, 4)
        self.u16(vertex_buffer + 0x0E, 9)
        self.u32(vertex_buffer + 0x10, 0x1601)
        self.graphics_pointer(vertex_buffer + 0x18, graphics_at)
        self.system_pointer(vertex_buffer + 0x28, descriptor + 0x20)
        self.system_pointer(vertex_buffer + 0x40, layout)

        buffer_record = self.alloc(di.INDEX_BUFFER_LEN)
        self.system_pointer(descriptor + 0x00, buffer_record)
        self.u16(descriptor + 0x08, 1 + index)
        self.u16(descriptor + 0x0A, 0x10)
        self.u32(descriptor + 0x0C, 0x2000)
        self.u64(descriptor + 0x30, 0xFFFFFFFFFFFF0214)

        index_bytes = 160
        index_at = self.graphics_alloc(index_bytes)
        self.u32(buffer_record + 0x08, 40)
        self.u16(buffer_record + 0x0C, 4)
        self.graphics_pointer(buffer_record + 0x18, index_at)
        self.system_pointer(buffer_record + 0x28, descriptor + 0x20)

    def model(self, at, group, geometries):
        geometry_array = self.alloc(8 * geometries)
        self.system_pointer(at + 0x08, geometry_array)
        self.u16(at + 0x10, geometries)
        self.u16(at + 0x12, geometries)
        self.u32(at + 0x14, 0x00020000)
        aabb = self.alloc(0x20)
        self.system_pointer(at + 0x18, aabb)
        for index in range(3):
            self.f32(aabb + 4 * index, -1.0)
            self.f32(aabb + 0x10 + 4 * index, 1.0)
        self.f32(aabb + 0x0C, -1.0)
        self.f32(aabb + 0x1C, 1.0)
        self.system_pointer(at + 0x20, group + 0x10)
        self.u64(at + 0x30, 0x000204FF00002400)
        for index in range(geometries):
            geometry = self.alloc(di.GEOMETRY_LEN)
            self.system_pointer(geometry_array + 8 * index, geometry)
            self.geometry(geometry, index)

    def shader(self, at, index, texture_parameters, bound_slots):
        self.u32(at + 0x00, 0x11223344 + index)
        self.u32(at + 0x04, di.SHADER_CONSTANT)
        first = self.alloc(0x20)
        self.system_pointer(at + 0x08, first)
        slots = self.alloc(8 * texture_parameters)
        self.system_pointer(at + 0x10, slots)
        total = texture_parameters + 2
        parameters = self.alloc(8 + 8 * total)
        self.system_pointer(at + 0x20, parameters)
        self.system[parameters + 1] = texture_parameters
        self.u16(parameters + 0x04, total)
        self.u16(parameters + 0x06, 0x0800)
        for pair in range(total):
            self.u32(parameters + 8 + 8 * pair, 0x1000 + pair)
            value = 4 * pair if pair < texture_parameters else 0x00000003
            self.u32(parameters + 12 + 8 * pair, value)
        for slot in range(texture_parameters):
            if slot >= bound_slots:
                self.u64(slots + 8 * slot, 0)
                continue
            record = self.alloc(di.VERTEX_BUFFER_LEN)
            self.system_pointer(slots + 8 * slot, record)
            name = self.alloc(0x20)
            self.system_pointer(record + 0x30, name)
            text = self.alloc(0x10)
            self.system[text : text + 4] = b"test"
            self.system_pointer(name + 0x00, text)
            self.u64(name + 0x08, 0x0102030405060708 + slot)

    def build(self, lod_count=1, models=1, geometries=2, shaders=2,
              texture_parameters=2, bound_slots=1, null_slots=()):
        self.system[0x88] = 1
        self.system[0x89] = 1
        self.system_pointer(0x08, 0x80)
        self.system[0x00:0x08] = b"\0" * 8
        for index in range(3):
            self.f32(0x20 + 4 * index, 0.0)
            self.f32(0x30 + 4 * index, -1.0)
            self.f32(0x40 + 4 * index, 1.0)
        self.f32(0x2C, 1.0)
        for index in range(4):
            self.f32(0x70 + 4 * index, 100.0 * (index + 1))
            self.u32(0x80 + 4 * index, 0x0000FF01 if index < lod_count else 0)
        self.u64(0xB8, 0x103)

        name = self.alloc(0x20)
        self.system[name : name + 4] = b"test"
        self.system_pointer(0xA8, name)
        optional = self.alloc(0x40)
        self.system_pointer(0xB0, optional)
        self.u16(optional + 0x08, 0)
        self.u16(optional + 0x0A, 0)

        for slot in range(4):
            if slot >= lod_count or slot in null_slots:
                self.u64(0x50 + 8 * slot, 0)
                continue
            group = self.alloc(di.LOD_GROUP_LEN)
            self.system_pointer(0x50 + 8 * slot, group)
            model_array = self.alloc(8 * models)
            self.system_pointer(group + 0x00, model_array)
            self.u16(group + 0x08, models)
            self.u16(group + 0x0A, models)
            self.u64(group + 0x10, 0x00010000)
            for index in range(models):
                model = self.alloc(di.MODEL_MIN_LEN)
                self.system_pointer(model_array + 8 * index, model)
                self.model(model, group, geometries)

        group = self.alloc(di.LOD_GROUP_LEN)
        self.system_pointer(0x10, group)
        self.u16(group + 0x18, shaders)
        self.u16(group + 0x1A, shaders)
        shader_list = self.alloc(8 * shaders)
        self.system_pointer(group + 0x10, shader_list)
        for index in range(shaders):
            shader = self.alloc(di.SHADER_LEN)
            self.system_pointer(shader_list + 8 * index, shader)
            self.shader(shader, index, texture_parameters, bound_slots)
        return bytes(self.system), bytes(self.graphics)


class DrawableCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

    def write(self, system, graphics):
        path = os.path.join(self.temp.name, "drawable.bin")
        with open(path, "wb") as handle:
            handle.write(system)
            handle.write(graphics)
        return path

    def analyze(self, fixture, system_length=SYSTEM_SIZE):
        system, graphics = fixture.build()
        return di.analyze(self.write(system, graphics), system_length)

    def issue_codes(self, report):
        return [issue["code"] for issue in report["issues"]]


class HeaderTests(DrawableCase):
    def test_one_lod_two_geometries(self):
        report = self.analyze(Fixture())
        self.assertEqual(report["status"], "complete", self.issue_codes(report))
        self.assertEqual(len(report["lod_slots"]), 1)
        lod = report["lod_slots"][0]
        self.assertEqual(lod["slot"], 0)
        self.assertEqual(lod["model_count"], 1)
        self.assertEqual(lod["model_capacity"], 1)
        self.assertEqual(lod["shader_indices"], [0, 1])
        model = lod["models"][0]
        self.assertEqual(model["geometry_count"], 2)
        self.assertEqual(model["geometry_capacity"], 2)
        first = model["geometries"][0]["vertex_buffer_record"]
        self.assertEqual(first["element_count"], 192)
        self.assertEqual(first["declared_bytes"], 768)
        self.assertEqual(first["layout_record"]["vertex_count"], 32)
        self.assertEqual(first["layout_record"]["attribute_stride"], 20)
        self.assertEqual(first["layout_record"]["attribute_end"], 768)
        self.assertEqual(first["layout_record"]["flags"], 0x51)
        self.assertEqual(first["layout_record"]["packed"], "0x00008051")
        self.assertEqual(first["layout_record"]["attributes"][0]["offset"], 0x80)
        self.assertEqual(len(first["layout_record"]["attributes"]), 4)
        second = model["geometries"][1]["vertex_buffer_record"]
        self.assertEqual(second["element_count"], 56)
        self.assertEqual(second["declared_bytes"], 224)
        self.assertEqual(second["layout_record"]["vertex_count"], 4)
        self.assertEqual(second["layout_record"]["flags"], 0x61)
        self.assertEqual(len(second["layout_record"]["attributes"]), 5)

    def test_four_lod_slots(self):
        fixture = Fixture()
        system, graphics = fixture.build(lod_count=4, geometries=1)
        report = di.analyze(self.write(system, graphics), SYSTEM_SIZE)
        self.assertEqual(report["status"], "complete", self.issue_codes(report))
        self.assertEqual([lod["slot"] for lod in report["lod_slots"]], [0, 1, 2, 3])
        for lod in report["lod_slots"]:
            self.assertEqual(lod["model_count"], 1)
            self.assertEqual(lod["models"][0]["geometry_count"], 1)
        self.assertEqual(report["graphics_base"]["base"], SYSTEM_SIZE)

    def test_null_lod_slot(self):
        fixture = Fixture()
        system, graphics = fixture.build(lod_count=3, geometries=1, null_slots=(1,))
        report = di.analyze(self.write(system, graphics), SYSTEM_SIZE)
        self.assertEqual(report["status"], "complete", self.issue_codes(report))
        self.assertEqual([lod["slot"] for lod in report["lod_slots"]], [0, 2])

    def test_bounds_and_distances(self):
        report = self.analyze(Fixture())
        bounds = report["header"]["bounds"]
        self.assertEqual(bounds["minimum"], [-1.0, -1.0, -1.0])
        self.assertEqual(bounds["maximum"], [1.0, 1.0, 1.0])
        self.assertEqual(bounds["radius"], 1.0)
        self.assertEqual(report["header"]["lod_distances"], [100.0, 200.0, 300.0, 400.0])
        self.assertEqual(report["header"]["lod_flags"], [0x0000FF01, 0, 0, 0])


class MaterialTests(DrawableCase):
    def test_declared_and_bound_are_separate(self):
        report = self.analyze(Fixture())
        materials = report["materials"]
        self.assertEqual(materials["shader_count"], 2)
        for shader in materials["shaders"]:
            parameters = shader["parameters"]
            self.assertEqual(parameters["texture_count"], 2)
            self.assertEqual(parameters["total"], 4)
            self.assertEqual(parameters["bound"], 1)
            self.assertEqual(parameters["unbound"], 1)
            self.assertEqual(parameters["distinct_keys"], 1)
            unbound = [entry for entry in parameters["texture_parameters"] if entry["record"] is None]
            self.assertEqual(len(unbound), 1)
            self.assertIsNone(unbound[0]["key"])


class NegativeTests(DrawableCase):
    def test_truncated_header(self):
        system, graphics = Fixture().build()
        path = self.write(system, graphics)
        report = di.analyze(path, 0x40)
        self.assertEqual(report["status"], "unverified")
        self.assertIn("truncated_header", self.issue_codes(report))

    def test_zero_header_is_reported(self):
        fixture = Fixture()
        system, graphics = fixture.build()
        data = bytearray(system + graphics)
        data[0] = 1
        path = self.write(bytes(data[:SYSTEM_SIZE]), bytes(data[SYSTEM_SIZE:]))
        report = di.analyze(path, SYSTEM_SIZE)
        self.assertEqual(report["status"], "unverified")
        self.assertIn("header_zero", self.issue_codes(report))

    def test_out_of_range_geometry_pointer(self):
        fixture = Fixture()
        system, graphics = fixture.build(geometries=1)
        # The first model's geometry array is the pointer at the model +0x08.
        # Locate it through the parsed report, then replace its first entry.
        good = di.analyze(self.write(system, graphics), SYSTEM_SIZE)
        geometry_array = good["lod_slots"][0]["models"][0]["geometry_array"]["offset"]
        data = bytearray(system + graphics)
        struct.pack_into("<Q", data, geometry_array, di.SYSTEM_BASE | (SYSTEM_SIZE + 0x80))
        report = di.analyze(self.write(bytes(data[:SYSTEM_SIZE]), bytes(data[SYSTEM_SIZE:])), SYSTEM_SIZE)
        self.assertEqual(report["status"], "partial")
        self.assertIn("pointer_outside", self.issue_codes(report))
        self.assertEqual(report["lod_slots"][0]["models"][0]["geometries"], [])

    def test_graphics_pointer_outside(self):
        fixture = Fixture()
        system, graphics = fixture.build(geometries=1)
        good = di.analyze(self.write(system, graphics), SYSTEM_SIZE)
        vertex_buffer = good["lod_slots"][0]["models"][0]["geometries"][0]["vertex_buffer_record"]["offset"]
        data = bytearray(system + graphics)
        struct.pack_into("<Q", data, vertex_buffer + 0x18, di.GRAPHICS_BASE | 0x1F000)
        report = di.analyze(self.write(bytes(data[:SYSTEM_SIZE]), bytes(data[SYSTEM_SIZE:])), SYSTEM_SIZE)
        self.assertEqual(report["status"], "partial")
        self.assertIn("pointer_outside", self.issue_codes(report))

    def test_buffer_size_mismatch(self):
        fixture = Fixture()
        system, graphics = fixture.build(geometries=1)
        good = di.analyze(self.write(system, graphics), SYSTEM_SIZE)
        vertex_buffer = good["lod_slots"][0]["models"][0]["geometries"][0]["vertex_buffer_record"]["offset"]
        data = bytearray(system + graphics)
        struct.pack_into("<I", data, vertex_buffer + 0x08, 191)
        report = di.analyze(self.write(bytes(data[:SYSTEM_SIZE]), bytes(data[SYSTEM_SIZE:])), SYSTEM_SIZE)
        self.assertEqual(report["status"], "partial")
        self.assertIn("buffer_size", self.issue_codes(report))


class PointerTests(unittest.TestCase):
    def test_decodes_both_segments(self):
        self.assertEqual(di.decode_pointer(0x50000040), di.Pointer("system", 0x40))
        self.assertEqual(di.decode_pointer(0x6FFFFFFF), di.Pointer("graphics", 0x0FFFFFFF))
        self.assertIsNone(di.decode_pointer(0x4FFFFFFF))
        self.assertIsNone(di.decode_pointer(0x70000000))
        self.assertIsNone(di.decode_pointer(0x150000000))


if __name__ == "__main__":
    unittest.main()
