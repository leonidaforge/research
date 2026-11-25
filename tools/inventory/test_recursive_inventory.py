import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import recursive_inventory as inventory


def row(index, size, type_id=0, readable=True, state=None):
    return {
        "kind": "row",
        "row": index,
        "type_id": type_id,
        "logical_size": size,
        "contents": {
            "readable": readable,
            "state": state or ("decoded" if readable else "unsupported"),
        },
        "mode": 0,
        "layout": "F",
        "payload_transform": False,
    }


def header(archive, status="authenticated"):
    path = Path(archive)
    return {
        "kind": "header",
        "archive": str(path),
        "relative": path.name,
        "authentication": {"status": status, "signature": "valid"},
    }


def top_manifest(archive, rows):
    path = Path(archive)
    return {"manifest": path, "header": header(path), "rows": rows}


class FakeRunner:
    """Serve archive extract and manifest commands from synthetic byte maps."""

    def __init__(self, extract_map, manifests):
        self.extract_map = extract_map
        self.manifests = manifests
        self.extract_calls = 0
        self.manifest_calls = 0

    def __call__(self, command):
        if command[1:3] == ["archive", "extract"]:
            self.extract_calls += 1
            parent = Path(command[3])
            index = int(command[5])
            output = Path(command[command.index("--output") + 1])
            key = (parent.read_bytes(), index)
            data = self.extract_map.get(key)
            if data is None:
                return subprocess.CompletedProcess(command, 1, "", "synthetic failure")
            output.write_bytes(data)
            return subprocess.CompletedProcess(command, 0, "", "")
        if command[1:3] == ["archive", "manifest"]:
            self.manifest_calls += 1
            archive = Path(command[3])
            output = Path(command[command.index("--output") + 1])
            rows = self.manifests.get(archive.read_bytes())
            if rows is None:
                return subprocess.CompletedProcess(command, 1, "", "unknown archive")
            documents = [header(archive)] + rows
            output.write_text(
                "\n".join(json.dumps(document) for document in documents) + "\n",
                encoding="utf-8",
            )
            return subprocess.CompletedProcess(command, 0, "", "")
        raise AssertionError(f"unexpected command: {command}")


class FakeSampler(inventory.Sampler):
    def __init__(self, scratch, runner):
        super().__init__(Path("fake-lforge"), Path("fake-executable"), scratch)
        self.runner = runner

    def run(self, command):
        return self.runner(command)


def make_args(scratch, **overrides):
    values = {
        "max_depth": inventory.DEFAULT_CAPS["max_depth"],
        "max_nested": inventory.DEFAULT_CAPS["max_nested_archives"],
        "max_bytes": inventory.DEFAULT_CAPS["max_extracted_bytes"],
        "max_rows": inventory.DEFAULT_CAPS["max_enumerated_rows"],
        "max_archive_bytes": inventory.DEFAULT_CAPS["max_archive_bytes"],
        "max_payload_bytes": inventory.DEFAULT_CAPS["max_payload_bytes"],
        "samples_depth1": inventory.DEFAULT_CAPS["samples_depth1"],
        "samples_depth2": inventory.DEFAULT_CAPS["samples_depth2"],
        "samples_depth3": inventory.DEFAULT_CAPS["samples_depth3"],
        "max_payloads_per_type": inventory.DEFAULT_CAPS["max_payloads_per_type"],
        "plan_only": False,
        "scratch_dir": Path(scratch),
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def make_case(root, top_bytes, top_rows, extract_map, manifests):
    game = Path(root) / "game"
    game.mkdir()
    archive = game / "top.rpf"
    archive.write_bytes(top_bytes)
    item = top_manifest(archive, top_rows)
    return [item], FakeRunner(extract_map, manifests)


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
        selected, count = inventory.select_quantiles(rows, inventory.MAX_ARCHIVE_BYTES, 3)
        self.assertEqual(count, 3)
        self.assertEqual([item["row"] for item in selected], [0, 3, 4])

    def test_single_candidate_produces_one_sample(self):
        selected, count = inventory.select_quantiles(
            [row(7, 123)], inventory.MAX_ARCHIVE_BYTES, 3
        )
        self.assertEqual(count, 1)
        self.assertEqual([item["row"] for item in selected], [7])

    def test_two_candidates_produce_two_samples(self):
        selected, _ = inventory.select_quantiles(
            [row(1, 100), row(2, 200)], inventory.MAX_ARCHIVE_BYTES, 3
        )
        self.assertEqual([item["row"] for item in selected], [1, 2])

    def test_smallest_and_largest_for_two_samples(self):
        selected, count = inventory.select_quantiles(
            [row(1, 100), row(2, 300), row(3, 200)], inventory.MAX_ARCHIVE_BYTES, 2
        )
        self.assertEqual(count, 3)
        self.assertEqual([item["row"] for item in selected], [1, 2])


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
            self.assertEqual(cache.extracted_bytes, len(content))

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
            self.assertEqual(cache.extracted_bytes, 20)


class TraversalTests(unittest.TestCase):
    def run_case(self, top_bytes, top_rows, extract_map, manifests, **overrides):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        items, runner = make_case(root, top_bytes, top_rows, extract_map, manifests)
        scratch = root / "scratch"
        scratch.mkdir()
        sampler = FakeSampler(scratch, runner)
        summary = inventory.execute(make_args(scratch, **overrides), items, [], sampler)
        return summary, runner

    def test_depth_stop(self):
        archive_a = b"9FPR-ARCHIVE-A"
        archive_b = b"9FPR-ARCHIVE-B"
        summary, runner = self.run_case(
            b"TOP-DEPTH",
            [row(0, len(archive_a))],
            {(b"TOP-DEPTH", 0): archive_a, (archive_a, 0): archive_b},
            {archive_a: [row(0, len(archive_b))], archive_b: []},
            max_depth=1,
            max_payloads_per_type=0,
        )
        self.assertEqual(summary["stop_reason"], "depth")
        self.assertEqual(summary["totals"]["unique_archives"], 1)
        self.assertEqual(summary["gaps"]["type0_beyond_depth_cap"], 1)
        self.assertEqual(runner.extract_calls, 1)

    def test_archive_count_stop(self):
        archive_a = b"9FPR-ARCHIVE-A"
        archive_b = b"9FPR-ARCHIVE-B"
        summary, runner = self.run_case(
            b"TOP-COUNT",
            [row(0, len(archive_a)), row(1, len(archive_b))],
            {
                (b"TOP-COUNT", 0): archive_a,
                (b"TOP-COUNT", 1): archive_b,
            },
            {archive_a: [], archive_b: []},
            max_depth=2,
            max_nested=1,
        )
        self.assertEqual(summary["stop_reason"], "archive limit")
        self.assertEqual(summary["totals"]["unique_archives"], 1)
        self.assertEqual(summary["totals"]["archive_extraction_attempts"], 1)
        self.assertEqual(summary["gaps"]["nested_archive_cap"], 1)
        self.assertEqual(runner.extract_calls, 1)

    def test_row_count_stop_truncates_manifest(self):
        archive_a = b"9FPR-ARCHIVE-A"
        summary, _ = self.run_case(
            b"TOP-ROWS",
            [row(0, len(archive_a))],
            {(b"TOP-ROWS", 0): archive_a},
            {archive_a: [row(0, 4, type_id=11), row(1, 5, type_id=11)]},
            max_depth=2,
            max_rows=1,
        )
        self.assertEqual(summary["stop_reason"], "row limit")
        self.assertEqual(summary["totals"]["manifest_rows"], 2)
        self.assertEqual(summary["totals"]["rows_enumerated"], 1)
        self.assertEqual(summary["totals"]["unique_rows"], 1)
        self.assertEqual(summary["gaps"]["row_limit_stop"], 1)
        self.assertEqual(
            summary["unique_archives"][0]["manifest"]["row_limit_truncated"], 1
        )

    def test_archive_byte_budget_exhaustion(self):
        archive_a = b"AAAAAAAA"
        archive_b = b"BBBBBBBB"
        summary, runner = self.run_case(
            b"TOP-BUDGET",
            [row(0, len(archive_a)), row(1, len(archive_b))],
            {
                (b"TOP-BUDGET", 0): archive_a,
                (b"TOP-BUDGET", 1): archive_b,
            },
            {archive_a: [], archive_b: []},
            max_depth=2,
            max_bytes=10,
        )
        self.assertEqual(summary["stop_reason"], "byte budget")
        self.assertEqual(summary["totals"]["archive_extraction_attempts"], 1)
        self.assertEqual(summary["totals"]["archive_extraction_successes"], 1)
        self.assertEqual(summary["gaps"]["extracted_byte_cap"], 1)
        self.assertEqual(runner.extract_calls, 1)

    def test_joint_byte_budget_covers_payloads(self):
        archive_a = b"9FPRXX"
        payload = b"PAYLDX"
        summary, runner = self.run_case(
            b"TOP-JOINT",
            [row(0, len(archive_a))],
            {(b"TOP-JOINT", 0): archive_a, (archive_a, 0): payload},
            {archive_a: [row(0, len(payload), type_id=11)]},
            max_depth=2,
            max_bytes=10,
        )
        self.assertEqual(summary["stop_reason"], "byte budget")
        self.assertEqual(summary["totals"]["archive_extraction_successes"], 1)
        self.assertEqual(summary["totals"]["payload_attempts"], 0)
        self.assertEqual(summary["gaps"]["payload_extracted_byte_cap"], 1)
        self.assertEqual(runner.extract_calls, 1)

    def test_failed_extraction_counts_as_attempt(self):
        archive_a = b"9FPR-OK"
        summary, runner = self.run_case(
            b"TOP-FAIL",
            [row(0, len(archive_a)), row(1, 8)],
            {(b"TOP-FAIL", 0): archive_a},
            {archive_a: []},
            max_depth=2,
        )
        self.assertEqual(summary["totals"]["archive_extraction_attempts"], 2)
        self.assertEqual(summary["totals"]["archive_extraction_successes"], 1)
        self.assertEqual(summary["totals"]["archive_extraction_failures"], 1)
        self.assertEqual(summary["failure_summary"][0]["kind"], "failed_extraction")
        self.assertEqual(runner.extract_calls, 2)

    def test_duplicate_archive_is_not_expanded_twice(self):
        duplicate = b"9FPR-DUPLICATE"
        summary, runner = self.run_case(
            b"TOP-DUPLICATE",
            [row(0, len(duplicate)), row(1, len(duplicate))],
            {(b"TOP-DUPLICATE", 0): duplicate, (b"TOP-DUPLICATE", 1): duplicate},
            {duplicate: [row(0, 3, type_id=11)]},
            max_depth=2,
        )
        self.assertEqual(summary["totals"]["archive_extraction_attempts"], 2)
        self.assertEqual(summary["totals"]["archive_extraction_successes"], 2)
        self.assertEqual(summary["totals"]["unique_archives"], 1)
        self.assertEqual(summary["totals"]["duplicate_archives"], 1)
        self.assertEqual(summary["totals"]["archive_bytes"], len(duplicate))
        self.assertEqual(
            summary["nested_aggregate"]["auth_provenance"]["inherited"], 1
        )
        self.assertEqual(runner.manifest_calls, 1)

    def test_resumed_run_reuses_cache(self):
        archive_a = b"9FPR-RESUME"
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        items, runner = make_case(
            root,
            b"TOP-RESUME",
            [row(0, len(archive_a))],
            {(b"TOP-RESUME", 0): archive_a},
            {archive_a: []},
        )
        scratch = root / "scratch"
        scratch.mkdir()
        args = make_args(scratch, max_depth=2)
        first = inventory.execute(args, items, [], FakeSampler(scratch, runner))
        first_calls = (runner.extract_calls, runner.manifest_calls)
        first_bytes = first["totals"]["extracted_bytes"]

        second_runner = FakeRunner(runner.extract_map, runner.manifests)
        second = inventory.execute(args, items, [], FakeSampler(scratch, second_runner))
        self.assertEqual(second_runner.extract_calls, 0)
        self.assertEqual(second_runner.manifest_calls, 0)
        self.assertEqual(second["totals"]["archive_extraction_attempts"], 1)
        self.assertEqual(second["totals"]["archive_extraction_successes"], 1)
        self.assertEqual(second["totals"]["extracted_bytes"], first_bytes)
        self.assertTrue(second["unique_archives"][0]["extraction"]["cached"])
        self.assertEqual(second["unique_archives"][0]["manifest"]["provenance"], "cached")
        self.assertEqual(first_calls, (1, 1))

    def test_transform_only_rows_stop(self):
        archive_a = b"9FPR-TRANSFORM"
        summary, _ = self.run_case(
            b"TOP-TRANSFORM",
            [row(0, len(archive_a))],
            {(b"TOP-TRANSFORM", 0): archive_a},
            {archive_a: [row(0, 4, readable=False, state="unsupported_transform")]},
            max_depth=2,
            max_payloads_per_type=0,
        )
        self.assertEqual(summary["stop_reason"], "transform")
        self.assertEqual(summary["depths"][1]["stop_reason"], "transform")

    def test_failed_only_run_stops_on_failure(self):
        summary, _ = self.run_case(
            b"TOP-FAIL-ONLY",
            [row(0, 8)],
            {},
            {},
            max_depth=2,
        )
        self.assertEqual(summary["totals"]["archive_extraction_attempts"], 1)
        self.assertEqual(summary["totals"]["archive_extraction_successes"], 0)
        self.assertEqual(summary["totals"]["archive_extraction_failures"], 1)
        self.assertEqual(summary["stop_reason"], "failure")


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
