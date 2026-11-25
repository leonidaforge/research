import json
import tempfile
import unittest
from pathlib import Path

import transform_census as census


def header():
    return {"kind": "header", "authentication": {"status": "authenticated"}}


def row(index, type_id, state="unsupported_transform", transform=True, encoding=2, count=1, cipher_type=17):
    return {
        "kind": "row",
        "row": index,
        "type_id": type_id,
        "layout": "R",
        "mode": 0,
        "chunks": {"encoding": encoding, "count": count},
        "logical_size": 100,
        "stored_size": 50,
        "payload_transform": transform,
        "payload_cipher": {"algorithm": "0x11", "supported": False, "type": cipher_type} if transform else None,
        "read_source": "main",
        "contents": {"readable": not transform, "state": state},
    }


class TransformCensusTests(unittest.TestCase):
    def test_unreadable_rows_are_split_by_type_and_stage(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifests = root / "manifests"
            manifests.mkdir()
            rows = [
                header(),
                row(0, 89),
                row(1, 89, count=2),
                row(2, 11, encoding=3),
                row(3, 14, encoding=3, count=11),
                row(4, 5, state="stored", transform=False),
            ]
            (manifests / "a.jsonl").write_text("\n".join(json.dumps(document) for document in rows) + "\n", encoding="utf-8")
            records = root / "rows.jsonl"
            records.write_text(json.dumps({"attempt": {"sha256": "a"}, "relative": "levels.rpf", "row": 3}) + "\n", encoding="utf-8")
            summary = census.census(manifests, records, root / "out")
            self.assertEqual(summary["rows_total"], 5)
            self.assertEqual(summary["rows_unreadable"], 4)
            self.assertEqual(summary["transform_flagged"], 4)
            self.assertEqual(summary["stages"], {"unsupported transformation": 4})
            self.assertEqual(summary["by_type"]["89"]["rows"], 2)
            self.assertEqual(summary["by_type"]["11"]["rows"], 1)
            self.assertEqual(summary["by_type"]["14"]["rows"], 1)
            self.assertEqual(summary["distinct_fingerprints"], 4)

    def test_fingerprint_separates_chunk_counts(self):
        first = census.row_fingerprint(row(0, 89, count=1))
        second = census.row_fingerprint(row(1, 89, count=2))
        self.assertNotEqual(first, second)

    def test_output_inside_the_manifest_directory_is_refused(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaises(census.TransformError):
                census.ensure_output(root / "out", root)


if __name__ == "__main__":
    unittest.main()
