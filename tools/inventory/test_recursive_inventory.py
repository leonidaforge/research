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


class SignatureTests(unittest.TestCase):
    def test_rpf9_magic(self):
        self.assertEqual(
            inventory.classify_signature(b"9FPR\x02\x00\x00\x00"), "rpf9-magic"
        )

    def test_unknown_prefix(self):
        self.assertEqual(inventory.classify_signature(b"ABCDEFGH"), "unrecognized")

    def test_zero_prefix(self):
        self.assertEqual(inventory.classify_signature(b"\x00" * 8), "zero-prefix")


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
