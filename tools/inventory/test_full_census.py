import json
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path

import full_census


def rpf_header(trailer=0, rows=1, columns=3, secondary=1, a=4, b=0x150):
    data = bytearray(0x40)
    data[0:4] = b"9FPR"
    struct.pack_into("<I", data, 0x04, 0x40)
    struct.pack_into("<I", data, 0x08, 0x40)
    struct.pack_into("<I", data, 0x0C, trailer)
    struct.pack_into("<H", data, 0x18, 0x7A00)
    struct.pack_into("<H", data, 0x1A, a)
    struct.pack_into("<I", data, 0x1C, b)
    struct.pack_into("<H", data, 0x20, columns)
    struct.pack_into("<H", data, 0x22, secondary)
    struct.pack_into("<I", data, 0x24, rows)
    struct.pack_into("<I", data, 0x28, 0x12345678)
    data[0x2C] = 2
    data[0x2D] = 1
    data[0x2E] = 9
    struct.pack_into("<I", data, 0x30, 0x10)
    return bytes(data)


def row(index, size, type_id=0, readable=True, offset=0, state=None, mode=0, layout="F"):
    return {
        "kind": "row",
        "row": index,
        "type_id": type_id,
        "logical_size": size,
        "stored_size": size,
        "layout": layout,
        "mode": mode,
        "chunks": None,
        "payload_transform": False,
        "payload_offset": f"0x{offset:016X}",
        "read_source": "main",
        "contents": {
            "readable": readable,
            "state": state or ("stored" if readable else "unsupported_transform"),
        },
    }


def nested_row(index, type_id, size, state="stored"):
    return {
        "kind": "row",
        "row": index,
        "type_id": type_id,
        "logical_size": size,
        "stored_size": size,
        "layout": "F",
        "mode": 0,
        "chunks": None,
        "payload_transform": state != "stored",
        "contents": {"readable": state == "stored", "state": state},
    }


class FakeRunner:
    def __init__(self, payloads, manifests, failure=None):
        self.payloads = payloads
        self.manifests = manifests
        self.failure = failure or {}
        self.calls = []
        self.lforge = Path("fake-lforge")
        self.executable = Path("fake-executable")

    def __call__(self, command):
        self.calls.append(command)
        if command[1:3] == ["archive", "extract"]:
            row_index = int(command[command.index("--row") + 1])
            output = Path(command[command.index("--output") + 1])
            if row_index in self.failure:
                return subprocess.CompletedProcess(command, 1, "", self.failure[row_index])
            output.write_bytes(self.payloads[row_index])
            return subprocess.CompletedProcess(command, 0, "", "")
        if command[1:3] == ["archive", "manifest"]:
            archive = Path(command[3])
            output = Path(command[command.index("--output") + 1])
            documents = [{"kind": "header", "archive": str(archive), "authentication": {"status": "authenticated"}}]
            documents.extend(self.manifests[archive.read_bytes()])
            output.write_text("\n".join(json.dumps(document) for document in documents) + "\n", encoding="utf-8")
            return subprocess.CompletedProcess(command, 0, "", "")
        raise AssertionError(command)


def make_inputs(root):
    game = Path(root) / "game"
    game.mkdir()
    archive = game / "top.rpf"
    archive.write_bytes(b"\0" * 0x200)
    manifest_dir = Path(root) / "manifests"
    manifest_dir.mkdir()
    top_rows = [
        row(0, len(rpf_header()), offset=0x100),
        row(1, len(rpf_header()), offset=0x180, type_id=0),
    ]
    documents = [{"kind": "header", "archive": str(archive), "relative": "top.rpf", "authentication": {"status": "authenticated"}}]
    documents.extend(top_rows)
    (manifest_dir / "top.jsonl").write_text("\n".join(json.dumps(document) for document in documents) + "\n", encoding="utf-8")
    payloads = {0: rpf_header(rows=2), 1: rpf_header(rows=1, columns=4)}
    manifests = {
        payloads[0]: [nested_row(0, 5, 100), nested_row(1, 0, 10)],
        payloads[1]: [nested_row(0, 7, 20)],
    }
    return manifest_dir, top_rows, payloads, manifests


class CensusTests(unittest.TestCase):
    def test_every_declared_row_is_attempted_and_summarised(self):
        with tempfile.TemporaryDirectory() as temporary:
            manifest_dir, _, payloads, manifests = make_inputs(temporary)
            runner = FakeRunner(payloads, manifests)
            census = full_census.Census(
                full_census.inventory.discover_manifests(manifest_dir)[0],
                Path(temporary) / "out",
                runner,
                batch_size=1,
            )
            self.assertEqual(census.accounting["declared_total"], 2)
            census.run()
            summary = full_census.aggregate(Path(temporary) / "out")
            self.assertEqual(summary["attempted"], 2)
            self.assertEqual(summary["succeeded"], 2)
            self.assertEqual(summary["failed"], 0)
            self.assertEqual(summary["depth2_type0_rows"], 1)
            histogram = {entry["type_id"]: entry for entry in summary["type_histogram"]}
            self.assertEqual(histogram[5]["rows"], 1)
            self.assertEqual(histogram[0]["rows"], 1)
            self.assertEqual(histogram[7]["rows"], 1)
            ranges = {entry["field"]: entry for entry in summary["header_ranges"]}
            self.assertEqual(ranges["magic"]["min"], 0x52504639)
            self.assertEqual(ranges["magic"]["count"], 2)
            self.assertEqual(ranges["e_rows"]["min"], 1)
            self.assertEqual(ranges["e_rows"]["max"], 2)
            state = json.loads((Path(temporary) / "out" / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["attempted"], 2)

    def test_transform_failure_has_a_stage(self):
        with tempfile.TemporaryDirectory() as temporary:
            manifest_dir, _, payloads, manifests = make_inputs(temporary)
            runner = FakeRunner(payloads, manifests, failure={0: "entry 0 is stored behind the payload transform"})
            census = full_census.Census(
                full_census.inventory.discover_manifests(manifest_dir)[0],
                Path(temporary) / "out",
                runner,
                batch_size=10,
            )
            census.run()
            summary = full_census.aggregate(Path(temporary) / "out")
            self.assertEqual(summary["failed"], 1)
            self.assertEqual(summary["failure_stages"], {"unsupported transformation": 1})

    def test_rows_above_the_cli_limit_use_a_bounded_stored_copy(self):
        with tempfile.TemporaryDirectory() as temporary:
            manifest_dir, top_rows, payloads, manifests = make_inputs(temporary)
            archive = Path(json.loads((manifest_dir / "top.jsonl").read_text(encoding="utf-8").splitlines()[0])["archive"])
            body = bytearray(0x400)
            body[0x100 : 0x100 + len(payloads[0])] = payloads[0]
            body[0x180 : 0x180 + len(payloads[1])] = payloads[1]
            archive.write_bytes(bytes(body))
            runner = FakeRunner(payloads, manifests)
            census = full_census.Census(
                full_census.inventory.discover_manifests(manifest_dir)[0],
                Path(temporary) / "out",
                runner,
                batch_size=10,
                cli_output_limit=8,
            )
            census.run()
            summary = full_census.aggregate(Path(temporary) / "out")
            self.assertEqual(summary["extraction_modes"], {"stored-copy": 2})
            self.assertEqual(summary["succeeded"], 2)

    def test_resume_skips_completed_rows(self):
        with tempfile.TemporaryDirectory() as temporary:
            manifest_dir, _, payloads, manifests = make_inputs(temporary)
            output = Path(temporary) / "out"
            full_census.Census(
                full_census.inventory.discover_manifests(manifest_dir)[0],
                output,
                FakeRunner(payloads, manifests),
                batch_size=1,
            ).run()
            runner = FakeRunner({}, {}, failure={0: "should not run", 1: "should not run"})
            census = full_census.Census(
                full_census.inventory.discover_manifests(manifest_dir)[0],
                output,
                runner,
                batch_size=1,
            )
            census.run()
            self.assertEqual(runner.calls, [])

    def test_output_directory_inside_the_inventory_is_refused(self):
        with tempfile.TemporaryDirectory() as temporary:
            manifest_dir, _, _, _ = make_inputs(temporary)
            with self.assertRaises(full_census.CensusError):
                full_census.ensure_output_dir(manifest_dir / "out", manifest_dir)

    def test_header_shorter_than_the_prefix_is_refused(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "short.rpf"
            path.write_bytes(b"9FPR")
            with self.assertRaises(full_census.CensusError):
                full_census.read_header(path)


if __name__ == "__main__":
    unittest.main()
