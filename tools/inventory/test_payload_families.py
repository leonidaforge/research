import json
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path

import payload_families as families


def wrapper(pages=(1, 1), tag=b"0DRPz", pointer_offset=0x20):
    data = bytearray(0x100)
    pointer = 0x50000000 | pointer_offset
    struct.pack_into("<Q", data, 0x08, pointer)
    data[0x10:0x10 + len(tag)] = tag
    data[pointer_offset + 8] = pages[0]
    data[pointer_offset + 9] = pages[1]
    return bytes(data)


class ClassifyTests(unittest.TestCase):
    def test_resource_wrapper_follows_the_page_map_pointer(self):
        entry = families.classify(wrapper((2, 3)))
        self.assertEqual(entry["class"], "resource-wrapper")
        self.assertEqual(entry["wrapper_tag"], "0DRPz")
        self.assertEqual(entry["page_map"], {"offset": 0x20, "system_pages": 2, "graphics_pages": 3})

    def test_zero_prefix_without_a_tag_is_not_a_wrapper(self):
        entry = families.classify(b"\0" * 32)
        self.assertEqual(entry["class"], "zero-prefix")
        self.assertIsNone(entry.get("wrapper_tag"))

    def test_known_magic_at_zero(self):
        entry = families.classify(b"PSIN" + b"\0" * 28)
        self.assertEqual(entry["class"], "psin-magic")

    def test_zlib_header(self):
        entry = families.classify(b"\x78\x9c" + b"\0" * 30)
        self.assertEqual(entry["class"], "zlib-container-header")

    def test_short_prefix_is_not_given_a_family(self):
        entry = families.classify(b"\0" * 8)
        self.assertEqual(entry["class"], "short")


def manifest(path, rows):
    documents = [
        {
            "kind": "header",
            "archive": str(path.with_suffix(".rpf")),
            "relative": path.stem,
            "authentication": {"status": "authenticated"},
        }
    ]
    documents.extend(rows)
    path.write_text("\n".join(json.dumps(document) for document in documents) + "\n", encoding="utf-8")


def row(index, type_id, size):
    return {
        "kind": "row",
        "row": index,
        "type_id": type_id,
        "logical_size": size,
        "stored_size": size,
        "layout": "F",
        "mode": 0,
        "chunks": None,
        "contents": {"readable": True, "state": "stored"},
    }


class FakeRunner:
    def __init__(self, payloads):
        self.payloads = payloads
        self.lforge = Path("fake-lforge")
        self.executable = Path("fake-executable")
        self.calls = 0

    def __call__(self, command):
        self.calls += 1
        index = int(command[command.index("--row") + 1])
        output = Path(command[command.index("--output") + 1])
        output.write_bytes(self.payloads[index])
        return subprocess.CompletedProcess(command, 0, "", "")


class SelectionTests(unittest.TestCase):
    def test_selection_is_per_type_and_bounded(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifests = root / "manifests"
            archives = root / "archives"
            manifests.mkdir()
            archives.mkdir()
            manifest(manifests / "a.jsonl", [row(0, 5, 10), row(1, 5, 20), row(2, 7, 30)])
            selected, frame = families.select(manifests, archives, 2, 1024)
            self.assertEqual(frame["types"], 2)
            self.assertEqual(len(selected), 3)
            self.assertEqual([item["row"]["row"] for item in selected if item["row"]["type_id"] == 5], [0, 1])

    def test_run_records_classes_and_removes_temporary_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            payloads = {0: wrapper(), 1: b"PSIN" + b"\0" * 28}
            selected = [
                {"sha256": "a", "archive": root / "a.rpf", "row": row(0, 5, 100), "logical_size": 100},
                {"sha256": "a", "archive": root / "a.rpf", "row": row(1, 7, 100), "logical_size": 100},
            ]
            (root / "a.rpf").write_bytes(b"archive")
            summary = families.run(selected, root / "out", FakeRunner(payloads))
            self.assertEqual(summary["successes"], 2)
            self.assertEqual(summary["classes"]["resource-wrapper"], 1)
            self.assertEqual(summary["classes"]["psin-magic"], 1)
            self.assertEqual(list((root / "out" / "tmp").iterdir()), [])

    def test_output_inside_an_input_directory_is_refused(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaises(families.FamilyError):
                families.ensure_output(root / "out", root)


if __name__ == "__main__":
    unittest.main()
