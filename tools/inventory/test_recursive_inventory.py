import tempfile
import unittest
from pathlib import Path

import recursive_inventory as inventory


def row(index, size, type_id=0, readable=True):
    return {
        "kind": "row",
        "row": index,
        "type_id": type_id,
        "logical_size": size,
        "contents": {"readable": readable, "state": "decoded" if readable else "unsupported"},
        "mode": 0,
        "layout": "F",
        "payload_transform": False,
    }


class SelectionTests(unittest.TestCase):
    def test_type0_selection_filters_and_orders(self):
        rows = [
            row(0, 10),
            row(1, 20, type_id=255),
            row(2, 30, readable=False),
            row(3, 40),
            row(4, 50),
            row(5, inventory.MAX_ARCHIVE_BYTES + 1),
        ]
        selected, count = inventory.select_three(rows, inventory.MAX_ARCHIVE_BYTES)
        self.assertEqual(count, 3)
        self.assertEqual([item["row"] for item in selected], [0, 3, 4])

    def test_single_candidate_produces_one_sample(self):
        selected, count = inventory.select_three([row(7, 123)], inventory.MAX_ARCHIVE_BYTES)
        self.assertEqual(count, 1)
        self.assertEqual([item["row"] for item in selected], [7])

    def test_two_candidates_produce_two_samples(self):
        selected, _ = inventory.select_three(
            [row(1, 100), row(2, 200)], inventory.MAX_ARCHIVE_BYTES
        )
        self.assertEqual([item["row"] for item in selected], [1, 2])

    def test_depth2_selection_takes_smallest_and_largest(self):
        selected, count = inventory.select_two(
            [row(1, 100), row(2, 300), row(3, 200)], inventory.MAX_ARCHIVE_BYTES
        )
        self.assertEqual(count, 3)
        self.assertEqual([item["row"] for item in selected], [1, 2])

    def test_depth2_single_candidate_is_not_duplicated(self):
        selected, _ = inventory.select_two([row(4, 100)], inventory.MAX_ARCHIVE_BYTES)
        self.assertEqual([item["row"] for item in selected], [4])


class QuantileSelectionTests(unittest.TestCase):
    def test_quantiles_include_endpoints(self):
        rows = [row(index, 100 * (index + 1)) for index in range(10)]
        selected, count = inventory.select_quantiles(rows, inventory.MAX_ARCHIVE_BYTES, 4)
        self.assertEqual(count, 10)
        self.assertEqual([item["row"] for item in selected], [0, 3, 6, 9])

    def test_limit_above_candidate_count_returns_all(self):
        rows = [row(1, 100), row(2, 200), row(3, 300)]
        selected, count = inventory.select_quantiles(rows, inventory.MAX_ARCHIVE_BYTES, 10)
        self.assertEqual(count, 3)
        self.assertEqual([item["row"] for item in selected], [1, 2, 3])

    def test_single_limit_returns_smallest(self):
        rows = [row(4, 400), row(1, 100), row(3, 300)]
        selected, _ = inventory.select_quantiles(rows, inventory.MAX_ARCHIVE_BYTES, 1)
        self.assertEqual([item["row"] for item in selected], [1])

    def test_gaps_separate_size_and_limit_reasons(self):
        rows = [
            row(0, 10),
            row(1, 20),
            row(2, 30),
            row(3, 40),
            row(4, inventory.MAX_ARCHIVE_BYTES + 1),
            row(5, 50, readable=False),
            row(6, 60, type_id=255),
        ]
        gaps = inventory.selection_gaps(rows, inventory.MAX_ARCHIVE_BYTES, 2)
        self.assertEqual(gaps["type0_rows"], 6)
        self.assertEqual(gaps["unreadable_type0"], 1)
        self.assertEqual(gaps["over_archive_size_cap"], 1)
        self.assertEqual(gaps["readable_within_cap"], 4)
        self.assertEqual(gaps["selected"], 2)
        self.assertEqual(gaps["not_selected_per_parent_limit"], 2)


class SignatureTests(unittest.TestCase):
    def test_rpf9_magic(self):
        self.assertEqual(
            inventory.classify_signature(b"9FPR\x02\x00\x00\x00"), "rpf9-magic"
        )

    def test_unknown_prefix(self):
        self.assertEqual(inventory.classify_signature(b"ABCDEFGH"), "unrecognized")

    def test_zero_prefix(self):
        self.assertEqual(inventory.classify_signature(b"\x00" * 8), "zero-prefix")

    def test_documented_magics(self):
        cases = {
            b"RBF0\x00\x00\x00\x00": "rbf0-magic",
            b"PSIN\x00\x00\x00\x00": "psin-magic",
            b"SGD5\x00\x00\x00\x00": "sgd5-magic",
            b"EDUP\x00\x00\x00\x00": "edup-magic",
            b"KB2j\x00\x00\x00\x00": "kb2j-magic",
            b"KB2n\x00\x00\x00\x00": "kb2n-magic",
        }
        for prefix, expected in cases.items():
            with self.subTest(prefix=prefix):
                self.assertEqual(inventory.classify_signature(prefix), expected)

    def test_zlib_header(self):
        self.assertEqual(
            inventory.classify_signature(b"\x78\xda\x00\x00\x00\x00\x00\x00"),
            "zlib-container-header",
        )


class ContentCacheTests(unittest.TestCase):
    def test_store_deduplicates_identical_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            cache = inventory.ContentCache(Path(temporary))
            content = b"9FPR-synthetic"
            first = cache.temporary("archive", "sample-one")
            first.write_bytes(content)
            digest, path, is_new = cache.store("archive", "sample-one", first, len(content))
            self.assertTrue(is_new)
            self.assertEqual(cache.archive_bytes, len(content))

            second = cache.temporary("archive", "sample-two")
            second.write_bytes(content)
            same_digest, same_path, is_new = cache.store(
                "archive", "sample-two", second, len(content)
            )
            self.assertFalse(is_new)
            self.assertEqual(digest, same_digest)
            self.assertEqual(path, same_path)
            self.assertEqual(cache.archive_bytes, len(content))

            cached = cache.lookup("archive", "sample-two", len(content))
            self.assertIsNotNone(cached)
            self.assertEqual(cached[0]["sha256"], digest)

    def test_store_keeps_payloads_separate(self):
        with tempfile.TemporaryDirectory() as temporary:
            cache = inventory.ContentCache(Path(temporary))
            archive = cache.temporary("archive", "archive")
            archive.write_bytes(b"same-bytes")
            cache.store("archive", "archive", archive, 10)
            payload = cache.temporary("payload", "payload")
            payload.write_bytes(b"same-bytes")
            cache.store("payload", "payload", payload, 10)
            self.assertEqual(cache.archive_bytes, 10)
            self.assertEqual(cache.payload_bytes, 10)


class RecordTests(unittest.TestCase):
    def test_public_record_drops_rows(self):
        record = {"sha256": "abc", "rows": [{"row": 0}]}
        self.assertNotIn("rows", inventory.public_record(record))


class PathTests(unittest.TestCase):
    def test_rejects_scratch_inside_game_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            game = root / "game"
            manifests = root / "manifests"
            game.mkdir()
            manifests.mkdir()
            with self.assertRaises(SystemExit):
                inventory.ensure_outside_inputs(game / "scratch", game, manifests)

    def test_accepts_separate_scratch_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            game = root / "game"
            manifests = root / "manifests"
            scratch = root / "scratch"
            game.mkdir()
            manifests.mkdir()
            inventory.ensure_outside_inputs(scratch, game, manifests)


if __name__ == "__main__":
    unittest.main()
