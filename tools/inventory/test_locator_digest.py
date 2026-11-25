import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import locator_digest as digest


def manifest(path, rows):
    documents = [{"kind": "header"}, *rows]
    path.write_text("\n".join(json.dumps(document) for document in documents) + "\n", encoding="utf-8")


class DigestTests(unittest.TestCase):
    def test_whole_archive_digest(self):
        with tempfile.TemporaryDirectory() as temporary:
            archive = Path(temporary) / "a.rpf"
            archive.write_bytes(b"0123456789")
            self.assertEqual(digest.digest_file(archive), hashlib.sha256(b"0123456789").hexdigest())

    def test_stored_row_digest(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = root / "a.rpf"
            archive.write_bytes(b"headerpayload")
            path = root / "a.jsonl"
            manifest(
                path,
                [{"kind": "row", "row": 0, "payload_offset": "0x0000000000000006", "stored_size": 7}],
            )
            self.assertEqual(digest.digest_row(archive, path, 0), hashlib.sha256(b"payload").hexdigest())

    def test_missing_row_is_a_typed_error(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = root / "a.rpf"
            archive.write_bytes(b"x")
            path = root / "a.jsonl"
            manifest(path, [])
            with self.assertRaises(digest.DigestError):
                digest.digest_row(archive, path, 1)

    def test_out_of_bounds_row_is_a_typed_error(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = root / "a.rpf"
            archive.write_bytes(b"x")
            path = root / "a.jsonl"
            manifest(
                path,
                [{"kind": "row", "row": 0, "payload_offset": "0x0000000000000004", "stored_size": 8}],
            )
            with self.assertRaises(digest.DigestError):
                digest.digest_row(archive, path, 0)


if __name__ == "__main__":
    unittest.main()
