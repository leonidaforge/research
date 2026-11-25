"""Synthetic tests for dictionary_census.py. No game files are used."""

import contextlib
import io
import json
import os
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import dictionary_census as census  # noqa: E402
from tests import test_pool_reference as pool_tests  # noqa: E402
from tests import test_texture_dictionary as dictionary_tests  # noqa: E402


def write_row(directory, name, system):
    path = os.path.join(directory, name)
    with open(path, "wb") as handle:
        handle.write(dictionary_tests.stored_row(system, b"\0" * 0x2000))
    return path


def write_listing(directory, name, type_id):
    listing = {
        "rows": [
            {
                "row": 0,
                "type_id": type_id,
                "payload_offset": "0x0",
                "stored_size": 0,
                "logical_size": 0,
            }
        ]
    }
    # The stored size and logical size depend on the row; patched by the caller.
    path = os.path.join(directory, name)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(listing, handle)
    return path


class CensusTests(unittest.TestCase):
    def test_int_accepts_both_forms(self):
        self.assertEqual(census._int(16, "x"), 16)
        self.assertEqual(census._int("16", "x"), 16)
        self.assertEqual(census._int("0x10", "x"), 16)
        with self.assertRaises(census.CensusError):
            census._int("nope", "x")

    def test_dictionary_negative_and_control(self):
        dictionary_system = bytes(
            dictionary_tests.make_dictionary([{"name": "alpha", "gfx": 0}])
        )
        decode_fail_system = bytes(pool_tests.make_drawable())
        structural = bytearray(
            dictionary_tests.make_dictionary([{"name": "alpha", "gfx": 0}])
        )
        struct.pack_into("<Q", structural, 0x20, 0)
        with tempfile.TemporaryDirectory() as directory:
            dict_archive = write_row(directory, "dict.rpf", dictionary_system)
            fail_archive = write_row(directory, "fail.rpf", decode_fail_system)
            structural_archive = write_row(directory, "structural.rpf", bytes(structural))
            dict_listing = write_listing(directory, "dict.json", 5)
            fail_listing = write_listing(directory, "fail.json", 66)
            structural_listing = write_listing(directory, "structural.json", 3)
            # Patch the listing sizes to the stored rows.
            for archive, listing in ((dict_archive, dict_listing),
                                     (fail_archive, fail_listing),
                                     (structural_archive, structural_listing)):
                size = os.path.getsize(archive)
                with open(listing, encoding="utf-8") as handle:
                    data = json.load(handle)
                data["rows"][0]["stored_size"] = size
                data["rows"][0]["logical_size"] = size
                with open(listing, "w", encoding="utf-8") as handle:
                    json.dump(data, handle)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = census.main([
                    "--dictionary", dict_archive, dict_listing,
                    "--negative", fail_archive, fail_listing, "66",
                    "--negative", structural_archive, structural_listing, "3",
                    "--json",
                ])
        self.assertEqual(code, 0)
        report = json.loads(output.getvalue())
        self.assertEqual(report["dictionaries"]["stats"]["rows"], 1)
        self.assertEqual(report["dictionaries"]["stats"]["records"], 1)
        negatives = report["negatives"]
        self.assertEqual(negatives["stats"]["accepted"], 0)
        self.assertEqual(negatives["stats"]["decode_fail"], 1)
        self.assertEqual(negatives["stats"]["rejected_structural"], 1)
        self.assertEqual(negatives["by_type"]["66"].get("decode_fail"), 1)
        self.assertEqual(negatives["by_type"]["3"].get("rejected_structural"), 1)
        self.assertEqual(report["control"]["trials"], 10000)
        self.assertEqual(report["control"]["slot_accepted"], 0)
        self.assertEqual(report["control"]["hash_matched"], 0)
        self.assertEqual(report["control"]["slot_threshold"], 100)
        self.assertEqual(report["control"]["hash_threshold"], 100)


if __name__ == "__main__":
    unittest.main()
