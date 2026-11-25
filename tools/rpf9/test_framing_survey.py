import contextlib
import io
import json
import os
import struct
import sys
import tempfile
import unittest
import unittest.mock
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _output
import framing_survey


def pad16(data):
    return data + b"\x00" * ((16 - len(data) % 16) % 16)


def row(index, offset, stored, logical, count=1, transform=False, type_id=11):
    return {
        "row": index,
        "type_id": type_id,
        "payload_offset": offset,
        "stored_size": stored,
        "logical_size": logical,
        "payload_transform": transform,
        "chunks": {"encoding": 2, "count": count},
    }


class FramingSurveyTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.archive = os.path.join(self.dir.name, "synthetic.rpf")
        self.data = bytearray(8192)
        self.manifest = {"rows": []}
        with open(self.archive, "wb") as fh:
            fh.write(self.data)

    def tearDown(self):
        self.dir.cleanup()

    def place(self, offset, payload):
        self.data[offset:offset + len(payload)] = payload
        with open(self.archive, "wb") as fh:
            fh.write(self.data)

    def test_prefix_and_zlib(self):
        body = pad16(zlib.compress(b"X" * 100))
        self.place(0x100, b"\x00" * 16 + body)
        self.manifest["rows"].append(row(0, 0x100, 16 + len(body), 100))
        summary = framing_survey.survey(self.archive, self.manifest)
        self.assertEqual(summary["prefix"]["all_zero"], 1)
        self.assertEqual(summary["method_patterns"], {"zlib": 1})
        self.assertEqual(summary["decoded"]["zero_run"], {"0": 1})
        self.assertEqual(summary["decoded"]["pointer_at_8"], 0)

    def test_raw_chunk(self):
        self.place(0x200, b"\x00" * 16 + b"R" * 50)
        self.manifest["rows"].append(row(0, 0x200, 66, 50))
        summary = framing_survey.survey(self.archive, self.manifest)
        self.assertEqual(summary["methods"], {"raw": 1})
        self.assertEqual(summary["decoded"]["zero_run"], {"0": 1})

    def test_padded_copy_chunk(self):
        self.place(0x280, b"\x00" * 16 + b"P" * 16)
        self.manifest["rows"].append(row(0, 0x280, 32, 10))
        summary = framing_survey.survey(self.archive, self.manifest)
        self.assertEqual(summary["method_patterns"], {"raw": 1})
        self.assertEqual(summary["raw_padding"], {"6": 1})
        self.assertEqual(summary["padded_copy_rows"], 1)

    def test_two_part_resource_pages(self):
        first = bytearray(0x40)
        struct.pack_into("<Q", first, 8, 0x50000020)
        first[0x10:0x15] = b"0DRPz"
        first[0x28] = 1
        first[0x29] = 1
        body = pad16(zlib.compress(bytes(first))) + pad16(zlib.compress(b"G" * 40))
        self.place(0x300, b"\x00" * 16 + body)
        self.manifest["rows"].append(row(0, 0x300, 16 + len(body), len(first) + 40, count=2))
        summary = framing_survey.survey(self.archive, self.manifest)
        self.assertEqual(summary["method_patterns"], {"zlib,zlib": 1})
        self.assertEqual(summary["parts"]["page_counts_known"], 1)
        self.assertEqual(summary["parts"]["equal"], 1)
        self.assertEqual(summary["decoded"]["marker_0DRPz"], 1)
        self.assertEqual(summary["decoded"]["pointer_at_8"], 1)

    def test_raw_last_chunk(self):
        body = pad16(zlib.compress(b"A" * 20)) + b"B" * 10
        self.place(0x400, b"\x00" * 16 + body)
        self.manifest["rows"].append(row(0, 0x400, 16 + len(body), 30, count=2))
        summary = framing_survey.survey(self.archive, self.manifest)
        self.assertEqual(summary["method_patterns"], {"zlib,raw": 1})

    def test_transformed_row_is_not_decoded(self):
        self.place(0x500, b"\x00" * 16 + b"\xff" * 40)
        self.manifest["rows"].append(row(0, 0x500, 56, 1000, transform=True, type_id=89))
        summary = framing_survey.survey(self.archive, self.manifest)
        self.assertEqual(summary["transformed_rows"], 1)
        self.assertEqual(summary["methods"], {"transformed": 1})
        self.assertEqual(summary["decoded"]["pointer_at_8"], 0)

    def test_truncated_row_is_refused(self):
        self.place(0x1F00, b"\x00" * 16 + b"Z" * 16)
        self.manifest["rows"].append(row(0, 0x1F00, 0x400, 0x400))
        summary = framing_survey.survey(self.archive, self.manifest)
        self.assertEqual(summary["rows_encoding2"], 1)
        self.assertEqual(summary["out_of_bounds"], 1)
        self.assertEqual(summary["prefix"], {"all_zero": 0, "other": 0})

    def test_row_shorter_than_prefix_is_refused(self):
        self.place(0x700, b"\x00" * 8)
        self.manifest["rows"].append(row(0, 0x700, 8, 8))
        summary = framing_survey.survey(self.archive, self.manifest)
        self.assertEqual(summary["out_of_bounds"], 1)

    def test_manifest_absent_chunks_is_ignored(self):
        self.manifest["rows"].append({"row": 0, "payload_offset": 0, "stored_size": 4,
                                      "logical_size": 4, "chunks": None})
        summary = framing_survey.survey(self.archive, self.manifest)
        self.assertEqual(summary["rows_encoding2"], 0)

    def test_output_may_not_overwrite_the_archive(self):
        self.place(0x600, b"\x00" * 16 + b"Q" * 16)
        self.manifest["rows"].append(row(0, 0x600, 32, 16))
        manifest_path = os.path.join(self.dir.name, "manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as fh:
            json.dump(self.manifest, fh)
        with open(self.archive, "rb") as fh:
            original = fh.read()
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = framing_survey.main(["--archive", self.archive,
                                        "--manifest", manifest_path,
                                        "--output", self.archive])
        self.assertEqual(code, 1)
        self.assertIn("input file", stderr.getvalue())
        with self.assertRaises(_output.OutputCollisionError):
            _output.guard_output(self.archive, [self.archive])
        with open(self.archive, "rb") as fh:
            self.assertEqual(fh.read(), original)

    def test_atomic_write_removes_the_temporary_file_on_error(self):
        target = os.path.join(self.dir.name, "output.json")
        with open(target, "w", encoding="utf-8") as fh:
            fh.write("old")
        with unittest.mock.patch("_output.os.replace", side_effect=OSError("stop")):
            with self.assertRaises(OSError):
                _output.write_atomic(target, "new")
        with open(target, "r", encoding="utf-8") as fh:
            self.assertEqual(fh.read(), "old")
        leftovers = [name for name in os.listdir(self.dir.name) if name.startswith(".rpf9-")]
        self.assertEqual(leftovers, [])


if __name__ == "__main__":
    unittest.main()
