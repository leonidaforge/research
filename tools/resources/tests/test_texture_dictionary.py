"""Synthetic tests for texture_dictionary.py. No game files are used."""

import contextlib
import io
import json
import os
import struct
import sys
import tempfile
import unittest
import zlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import texture_dictionary as td  # noqa: E402


def _pointer(segment, offset):
    base = td.SYSTEM_BASE if segment == "system" else td.GRAPHICS_BASE
    return base | offset


def make_dictionary(records, graphics_length=0x2000, system_length=0x400,
                    record_offsets=None, value_permutation=False):
    """Build a synthetic system segment from a list of record dicts."""
    data = bytearray(system_length)
    map_at = system_length - 0x20
    struct.pack_into("<Q", data, 8, _pointer("system", map_at))
    data[map_at + 8] = 1
    data[map_at + 9] = 1
    struct.pack_into("<Q", data, 0x18, 1)
    count = len(records)
    if record_offsets is None:
        record_offsets = [0x40 + index * td.RECORD_LEN for index in range(count)]
    hash_at = ((max(record_offsets) + td.RECORD_LEN) + 7) & ~7
    value_at = (hash_at + 4 * count + 7) & ~7
    name_at = value_at + 8 * count
    prepared = []
    for position, record in enumerate(records):
        name = record.get("name", f"tex{position}")
        name_hash = record.get("hash", td.joaat(name.encode()))
        prepared.append((name_hash, name, record))
    prepared.sort(key=lambda item: item[0])
    for index, (name_hash, name, record) in enumerate(prepared):
        at = record_offsets[index]
        struct.pack_into("<I", data, hash_at + 4 * index, name_hash)
        struct.pack_into(
            "<Q", data, value_at + 8 * index, _pointer("system", at)
        )
        if record.get("skip_record"):
            continue
        struct.pack_into("<I", data, at + 0x08, record.get("allocation_units", 0x100))
        struct.pack_into("<Q", data, at + 0x10, record.get("field_10", 2432))
        struct.pack_into(
            "<Q", data, at + 0x18,
            _pointer("graphics", record.get("gfx", index * 0x1000)),
        )
        name_ptr = name_at + index * 0x20
        struct.pack_into("<Q", data, at + 0x28, _pointer("system", at + 0x50))
        struct.pack_into("<Q", data, at + 0x30, _pointer("system", name_ptr))
        struct.pack_into("<H", data, at + 0x44, record.get("field_44", 0))
        struct.pack_into("<H", data, at + 0x46, record.get("field_46", 1))
        struct.pack_into("<Q", data, at + 0x60,
                         record.get("field_60", 0xFFFFFFFFFFFF0241))
        text = record.get("text", name).encode() + b"\x00"
        if name_ptr + 8 + len(text) <= system_length:
            data[name_ptr + 8:name_ptr + 8 + len(text)] = text
        packed_38 = (
            record.get("width", 128)
            | (record.get("height", 128) << 16)
            | (record.get("field_3c", 1) << 32)
            | (record.get("field_3e", 1) << 48)
            | (record.get("format", 98) << 56)
        )
        packed_40 = (
            record.get("field_40", 5)
            | ((record.get("mips", 1) | record.get("mip_flag", 0)) << 16)
            | (1 << 48)
        )
        struct.pack_into("<Q", data, at + 0x38, packed_38)
        struct.pack_into("<Q", data, at + 0x40, packed_40)
        struct.pack_into("<Q", data, at + 0x48, 2 << 32)
    if value_permutation and count > 1:
        first = struct.unpack_from("<Q", data, value_at)[0]
        second = struct.unpack_from("<Q", data, value_at + 8)[0]
        struct.pack_into("<Q", data, value_at, second)
        struct.pack_into("<Q", data, value_at + 8, first)
    struct.pack_into("<Q", data, 0x20, _pointer("system", hash_at))
    struct.pack_into("<H", data, 0x28, count)
    struct.pack_into("<H", data, 0x2A, count)
    struct.pack_into("<Q", data, 0x30, _pointer("system", value_at))
    struct.pack_into("<H", data, 0x38, count)
    struct.pack_into("<H", data, 0x3A, count)
    return data


class ParseTests(unittest.TestCase):
    def test_reads_every_record_field(self):
        system = make_dictionary(
            [
                {"name": "alpha", "hash": 1, "allocation_units": 0x100, "gfx": 0, "format": 71,
                 "width": 10, "height": 20, "mips": 3, "mip_flag": 0x8000},
                {"name": "beta", "hash": 2, "allocation_units": 0x80, "gfx": 0x1000, "format": 98,
                 "width": 30, "height": 40, "mips": 1},
            ]
        )
        dictionary = td.parse_dictionary(bytes(system), 0x2000)
        self.assertEqual(dictionary.issues, [])
        self.assertEqual(dictionary.hash_count, 2)
        self.assertEqual(dictionary.value_count, 2)
        self.assertEqual(dictionary.record_count, 2)
        self.assertEqual(dictionary.allocated_total, 0x2000)
        self.assertTrue(dictionary.allocations_in_bounds)
        self.assertTrue(dictionary.allocation_sum_ok)
        self.assertTrue(dictionary.starts_at_zero)
        self.assertTrue(dictionary.partition_ok)
        self.assertTrue(dictionary.record_table_dense)
        self.assertTrue(dictionary.value_order_matches_index)
        first, second = dictionary.records
        self.assertEqual((first.width, first.height, first.format_id, first.mip_levels),
                         (10, 20, 71, 3))
        self.assertEqual(first.mip_flag, 0x8000)
        self.assertEqual(first.allocation_units, 0x100)
        self.assertEqual(first.allocation_offset, 0)
        self.assertEqual(first.allocation_size, 0x1000)
        self.assertEqual(first.allocation_extent, 0x1000)
        self.assertEqual(first.size_basis, "extent_upper_bound")
        self.assertEqual((second.allocation_offset, second.allocation_size), (0x1000, 0x1000))

    def test_reports_all_record_fields(self):
        system = make_dictionary(
            [{"name": "alpha", "hash": 1, "field_10": 0x980,
              "field_44": 0, "field_46": 1, "field_60": 0xFFFFFFFFFFFF0241}]
        )
        dictionary = td.parse_dictionary(bytes(system), 0x2000)
        record = dictionary.records[0]
        self.assertEqual(record.record_offset, 0x40)
        self.assertTrue(record.value_pointer)
        self.assertEqual(record.field_00, 0)
        self.assertEqual(record.field_0c, 0)
        self.assertEqual(record.field_10, 0x980)
        self.assertEqual(record.field_20, 0)
        self.assertEqual(record.field_28, td.SYSTEM_BASE | 0x90)
        self.assertEqual(record.field_44, 0)
        self.assertEqual(record.field_46, 1)
        self.assertEqual(record.field_48, 2 << 32)
        self.assertEqual(record.field_50, 0)
        self.assertEqual(record.field_58, 0)
        self.assertEqual(record.field_60, 0xFFFFFFFFFFFF0241)
        self.assertEqual(record.field_68, 0)
        keys = set(record.as_dict())
        self.assertTrue({"record_offset", "value_pointer", "name_pointer", "field_00",
                         "field_0c", "field_10", "field_20", "field_28", "field_44",
                         "field_46", "field_48", "field_50", "field_58", "field_60",
                         "field_68"}.issubset(keys))

    def test_partition_requires_a_zero_start(self):
        system = make_dictionary([{"name": "alpha", "hash": 1, "gfx": 0x1000},
                                  {"name": "beta", "hash": 2, "gfx": 0x1800}],
                                 graphics_length=0x2000)
        dictionary = td.parse_dictionary(bytes(system), 0x2000)
        self.assertFalse(dictionary.starts_at_zero)
        self.assertFalse(dictionary.partition_ok)
        self.assertLess(dictionary.allocated_total, dictionary.graphics_size)
        self.assertIn("allocation_front_gap", [issue.code for issue in dictionary.issues])

    def test_record_gap_and_value_order(self):
        gapped = make_dictionary(
            [{"name": "alpha", "hash": 1}, {"name": "beta", "hash": 2}],
            record_offsets=[0x40, 0x100],
        )
        dictionary = td.parse_dictionary(bytes(gapped), 0x2000)
        self.assertFalse(dictionary.record_table_dense)
        self.assertEqual(len(dictionary.record_gaps), 1)
        self.assertEqual(dictionary.record_gaps[0]["delta"], 0xC0)
        # A gap alone is not an order mismatch: the value order is compared with
        # the recorded addresses, not with a fixed stride.
        self.assertTrue(dictionary.value_order_matches_index)

        gapped_permuted = make_dictionary(
            [{"name": "alpha", "hash": 1}, {"name": "beta", "hash": 2}],
            record_offsets=[0x40, 0x100], value_permutation=True,
        )
        dictionary = td.parse_dictionary(bytes(gapped_permuted), 0x2000)
        self.assertFalse(dictionary.record_table_dense)
        self.assertFalse(dictionary.value_order_matches_index)

        permuted = make_dictionary(
            [{"name": "alpha", "hash": 1}, {"name": "beta", "hash": 2}],
            value_permutation=True,
        )
        dictionary = td.parse_dictionary(bytes(permuted), 0x2000)
        self.assertTrue(dictionary.record_table_dense)
        self.assertFalse(dictionary.value_order_matches_index)

        dense = make_dictionary([{"name": "alpha", "hash": 1}, {"name": "beta", "hash": 2}])
        dictionary = td.parse_dictionary(bytes(dense), 0x2000)
        self.assertTrue(dictionary.record_table_dense)
        self.assertTrue(dictionary.value_order_matches_index)

    def test_empty_dictionary(self):
        data = bytearray(0x60)
        struct.pack_into("<Q", data, 8, _pointer("system", 0x40))
        dictionary = td.parse_dictionary(bytes(data), 0)
        self.assertEqual(dictionary.record_count, 0)
        self.assertEqual(dictionary.issues, [])
        self.assertEqual(dictionary.allocated_total, 0)

    def test_count_mismatch_is_reported(self):
        system = make_dictionary([{"name": "alpha"}, {"name": "beta"}])
        struct.pack_into("<H", system, 0x38, 1)
        dictionary = td.parse_dictionary(bytes(system), 0x2000)
        self.assertIn("count_mismatch", [issue.code for issue in dictionary.issues])
        self.assertEqual(dictionary.record_count, 1)

    def test_unsorted_and_duplicate_hashes_are_reported(self):
        system = make_dictionary([{"name": "alpha", "hash": 0x10},
                                  {"name": "beta", "hash": 0x20}])
        value_at = struct.unpack_from("<Q", system, 0x30)[0] & td.OFFSET_MASK
        hash_at = struct.unpack_from("<Q", system, 0x20)[0] & td.OFFSET_MASK
        struct.pack_into("<I", system, hash_at, 0x20)
        struct.pack_into("<I", system, hash_at + 4, 0x10)
        dictionary = td.parse_dictionary(bytes(system), 0x2000)
        codes = [issue.code for issue in dictionary.issues]
        self.assertIn("hash_unsorted", codes)
        struct.pack_into("<I", system, hash_at, 0x10)
        dictionary = td.parse_dictionary(bytes(system), 0x2000)
        self.assertIn("hash_duplicate", [issue.code for issue in dictionary.issues])
        self.assertIsNotNone(value_at)

    def test_record_pointer_outside_is_reported(self):
        system = make_dictionary([{"name": "alpha"}])
        value_at = struct.unpack_from("<Q", system, 0x30)[0] & td.OFFSET_MASK
        struct.pack_into("<Q", system, value_at, td.SYSTEM_BASE | 0x3F8)
        dictionary = td.parse_dictionary(bytes(system), 0x2000)
        self.assertIn("record_outside", [issue.code for issue in dictionary.issues])

    def test_non_pointer_value_is_reported(self):
        system = make_dictionary([{"name": "alpha"}])
        value_at = struct.unpack_from("<Q", system, 0x30)[0] & td.OFFSET_MASK
        struct.pack_into("<Q", system, value_at, 0x1234)
        dictionary = td.parse_dictionary(bytes(system), 0x2000)
        self.assertIn("record_pointer", [issue.code for issue in dictionary.issues])

    def test_allocation_outside_is_reported(self):
        system = make_dictionary([{"name": "alpha", "gfx": 0x3000}],
                                 graphics_length=0x2000)
        dictionary = td.parse_dictionary(bytes(system), 0x2000)
        self.assertIn("allocation_outside", [issue.code for issue in dictionary.issues])
        self.assertFalse(dictionary.allocations_in_bounds)

    def test_duplicate_allocation_is_reported(self):
        system = make_dictionary([{"name": "alpha", "gfx": 0},
                                  {"name": "beta", "gfx": 0}])
        dictionary = td.parse_dictionary(bytes(system), 0x2000)
        self.assertIn("allocation_duplicate", [issue.code for issue in dictionary.issues])

    def test_format_is_raw_and_size_is_the_extent(self):
        system = make_dictionary([{"name": "alpha", "hash": 1, "format": 200, "allocation_units": 4, "gfx": 0},
                                  {"name": "beta", "hash": 2, "gfx": 0x1000}])
        dictionary = td.parse_dictionary(bytes(system), 0x2000)
        record = dictionary.records[0]
        self.assertEqual(record.format_id, 200)
        self.assertEqual(record.allocation_units, 4)
        self.assertEqual(record.allocation_size, record.allocation_extent)
        self.assertEqual(record.size_basis, "extent_upper_bound")
        self.assertNotIn("unknown_format", [issue.code for issue in dictionary.issues])

    def test_capacity_below_count_is_reported(self):
        system = make_dictionary([{"name": "alpha"}, {"name": "beta"}])
        struct.pack_into("<H", system, 0x2A, 1)
        struct.pack_into("<H", system, 0x3A, 1)
        dictionary = td.parse_dictionary(bytes(system), 0x2000)
        self.assertIn("capacity_short", [issue.code for issue in dictionary.issues])

    def test_dimensions_and_mips_are_checked(self):
        system = make_dictionary([{"name": "alpha", "width": 0, "height": 4}])
        dictionary = td.parse_dictionary(bytes(system), 0x2000)
        self.assertIn("dimensions_zero", [issue.code for issue in dictionary.issues])
        system = make_dictionary([{"name": "alpha", "width": 4, "height": 4, "mips": 9}])
        dictionary = td.parse_dictionary(bytes(system), 0x2000)
        self.assertIn("mips_exceeds", [issue.code for issue in dictionary.issues])
        system = make_dictionary([{"name": "alpha", "mips": 0}])
        dictionary = td.parse_dictionary(bytes(system), 0x2000)
        self.assertIn("mips_zero", [issue.code for issue in dictionary.issues])


class RefusalTests(unittest.TestCase):
    def test_short_buffer(self):
        with self.assertRaises(td.TextureDictionaryError):
            td.parse_dictionary(b"\0" * 0x20, 0)

    def test_nonzero_first_qword(self):
        data = make_dictionary([{"name": "alpha"}])
        struct.pack_into("<Q", data, 0, 1)
        with self.assertRaises(td.TextureDictionaryError):
            td.parse_dictionary(bytes(data), 0x1000)

    def test_missing_page_map(self):
        data = make_dictionary([{"name": "alpha"}])
        struct.pack_into("<Q", data, 8, 0)
        with self.assertRaises(td.TextureDictionaryError):
            td.parse_dictionary(bytes(data), 0x1000)

    def test_huge_count_is_refused(self):
        data = make_dictionary([{"name": "alpha"}])
        struct.pack_into("<H", data, 0x28, 0xFFFF)
        struct.pack_into("<H", data, 0x38, 0xFFFF)
        with self.assertRaises(td.TextureDictionaryError):
            td.parse_dictionary(bytes(data), 0x1000, max_records=10)

    def test_array_outside_is_refused(self):
        data = make_dictionary([{"name": "alpha"}])
        struct.pack_into("<Q", data, 0x20, td.SYSTEM_BASE | 0x3FC)
        struct.pack_into("<H", data, 0x28, 4)
        struct.pack_into("<H", data, 0x38, 4)
        with self.assertRaises(td.TextureDictionaryError):
            td.parse_dictionary(bytes(data), 0x1000)


class NameCheckTests(unittest.TestCase):
    def test_hashes_match_the_ascii_names(self):
        system = make_dictionary([{"name": "alpha"}, {"name": "beta"}])
        dictionary = td.parse_dictionary(bytes(system), 0x2000)
        checked, matched = td.check_names(bytes(system), dictionary)
        self.assertEqual((checked, matched), (2, 2))

    def test_a_wrong_hash_does_not_match(self):
        system = make_dictionary([{"name": "alpha", "hash": 0x12345678},
                                  {"name": "beta"}])
        dictionary = td.parse_dictionary(bytes(system), 0x2000)
        checked, matched = td.check_names(bytes(system), dictionary)
        self.assertEqual(checked, 2)
        self.assertLess(matched, checked)

    def test_joaat_folds_case_and_backslash(self):
        self.assertEqual(td.joaat(b"alpha/beta"), 0x75438640)
        self.assertEqual(td.joaat(b"ALPHA\\BETA"), 0x75438640)
        system = make_dictionary([{"name": "ALPHA\\BETA", "hash": 0x75438640}])
        dictionary = td.parse_dictionary(bytes(system), 0x2000)
        checked, matched = td.check_names(bytes(system), dictionary)
        self.assertEqual((checked, matched), (1, 1))

    def test_name_longer_than_the_window_is_unchecked(self):
        name = "a" * 80
        system = make_dictionary([{"name": name}])
        dictionary = td.parse_dictionary(bytes(system), 0x2000)
        checked, matched = td.check_names(bytes(system), dictionary, limit=64)
        self.assertEqual((checked, matched), (0, 0))


def stored_row(system, graphics):
    chunks = [zlib.compress(system), zlib.compress(graphics)]
    body = b"".join(chunk + b"\0" * ((-len(chunk)) % 16) for chunk in chunks)
    return b"\0" * 16 + body


class StoredTests(unittest.TestCase):
    def test_reconstructs_and_parses_a_stored_row(self):
        system = bytes(make_dictionary([{"name": "alpha"}]))
        graphics = bytes(0x2000)
        row = stored_row(system, graphics)
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "row.rpf")
            with open(path, "wb") as handle:
                handle.write(row)
            dictionary, decoded_system, graphics_length = td.analyze_stored(
                path, 0, len(row), logical_size=len(system) + len(graphics)
            )
        self.assertEqual(decoded_system, system)
        self.assertEqual(graphics_length, 0x2000)
        self.assertEqual(dictionary.record_count, 1)

    def test_cli_json_report(self):
        system = bytes(make_dictionary([{"name": "alpha"}]))
        graphics = bytes(0x2000)
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "decoded.bin")
            with open(path, "wb") as handle:
                handle.write(system + graphics)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = td.main(["--file", path, "--system-length", str(len(system)), "--json"])
        self.assertEqual(code, 0)
        report = json.loads(output.getvalue())
        self.assertEqual(report["record_count"], 1)
        self.assertEqual(report["records"][0]["width"], 128)
        self.assertEqual(report["records"][0]["mip_levels"], 1)


if __name__ == "__main__":
    unittest.main()
