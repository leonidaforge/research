import io
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import census_all
import entry_matrix


def combination(
    entry_type,
    identification,
    entries,
    capability,
    extension='-',
    structure='verified',
    payload='decoded',
    archive='a.rpf',
    variant='format:rpf9',
    archive_count=1,
    outcome='identified',
    provenance='native',
):
    return {
        'type': entry_type,
        'identification': identification,
        'variant': variant,
        'storage': 'chunked-2',
        'transform': False,
        'payload': payload,
        'structure': structure,
        'capability': capability,
        'extension': extension,
        'extension_provenance': provenance,
        'outcome': outcome,
        'entries': entries,
        'archive_count': archive_count,
        'archives': [archive],
        'samples': [{'archive': archive, 'chain': archive + '!0', 'size': 16, 'head': '00' * 16}],
    }


def summary(relative, entries, combinations, stopped=None):
    """A root summary with the records the CLI writes, so totals reconcile."""
    types = {}
    outcomes = {}
    for item in combinations:
        existing = types.setdefault(item['type'], {'type': item['type'], 'entries': 0, 'archives': 0})
        existing['entries'] += item['entries']
        existing['archives'] += 1
        outcomes[item['outcome']] = outcomes.get(item['outcome'], 0) + item['entries']
    return {
        'record': 'summary',
        'schema': 'leonida-forge.rpf9-census/1',
        'root': relative,
        'relative': relative,
        'archives': 1,
        'entries': entries,
        'spooled_bytes': 0,
        'stopped': stopped,
        'completion': {'complete': stopped is None},
        'coverage': {
            'roots_discovered': 1,
            'roots_opened': 1,
            'entries_probed': entries,
            'failed_archives': 0,
        },
        'types': list(types.values()),
        'outcomes': outcomes,
        'combinations': combinations,
        'failures': [],
    }


class MergeTest(unittest.TestCase):
    def test_the_merged_counts_add_up(self):
        first = summary(
            'a.rpf',
            3,
            [
                combination(0, 'format:rpf9', 1, 'archive', 'rpf'),
                combination(255, 'resource:segment-5', 2, 'resource'),
            ],
        )
        second = summary(
            'b.rpf',
            4,
            [
                combination(255, 'resource:segment-5', 3, 'resource', archive='b.rpf'),
                combination(11, 'format:psin', 1, 'structural'),
            ],
            'max_entries',
        )
        merged = census_all.merge([first, second], [], 2)
        self.assertEqual(merged['entries'], 7)
        self.assertEqual(sum(item['entries'] for item in merged['combinations']), 7)
        self.assertEqual(len(merged['combinations']), 3)
        resource = [
            item for item in merged['combinations'] if item['identification'] == 'resource:segment-5'
        ][0]
        self.assertEqual(resource['entries'], 5)
        self.assertEqual(resource['archive_count'], 2)
        self.assertEqual(merged['stopped'], {'b.rpf': 'max_entries'})
        # A run that stopped early is not complete, and says why.
        self.assertFalse(merged['complete'])
        self.assertEqual(merged['completion']['reasons'], ['stopped_scans'])
        self.assertEqual(merged['outcomes'], {'identified': 7})
        self.assertTrue(merged['completion']['checks']['reconciles'])

    def test_totals_that_disagree_make_the_run_incomplete(self):
        first = summary('a.rpf', 3, [combination(0, 'format:rpf9', 3, 'archive', 'rpf')])
        # The summary says three entries and its combinations say two.
        first['combinations'][0]['entries'] = 2
        merged = census_all.merge([first], [], 1)
        self.assertFalse(merged['completion']['checks']['reconciles'])
        self.assertIn('inconsistent_counts', merged['completion']['reasons'])
        self.assertFalse(merged['complete'])

    def test_a_nested_archive_failure_makes_the_run_incomplete(self):
        first = summary('a.rpf', 1, [combination(0, 'format:rpf9', 1, 'archive', 'rpf')])
        first['coverage']['failed_archives'] = 1
        merged = census_all.merge([first], [], 1)
        self.assertIn('nested_archive_failures', merged['completion']['reasons'])
        self.assertFalse(merged['complete'])

    def test_a_decoding_failure_does_not_make_enumeration_incomplete(self):
        # Undecodable and blocked entries are enumerated and have an outcome;
        # finished enumeration is still finished enumeration.
        first = summary(
            'a.rpf',
            2,
            [
                combination(255, 'none', 1, 'unavailable', payload='undecodable', outcome='undecodable'),
                combination(255, 'none', 1, 'unavailable', payload='transform-failed', outcome='blocked'),
            ],
        )
        merged = census_all.merge([first], [], 1)
        self.assertTrue(merged['complete'])
        self.assertEqual(
            merged['outcomes'], {'undecodable': 1, 'blocked': 1}
        )

    def test_a_metadata_pass_is_not_blocked_it_is_not_probed(self):
        first = summary(
            'a.rpf',
            2,
            [
                combination(0, 'none', 2, 'unprobed', payload='not-read', outcome='not-probed'),
            ],
        )
        merged = census_all.merge([first], [], 1)
        self.assertEqual(merged['outcomes'], {'not-probed': 2})
        self.assertTrue(merged['complete'])

    def test_exact_archive_counts_exceed_the_representative_list(self):
        combinations = [
            combination(5, 'resource:segment-5', 3, 'resource', archive='a.rpf')
            for _ in range(12)
        ]
        merged = census_all.merge([summary('root.rpf', 36, combinations)], [], 1)
        merged_combination = merged['combinations'][0]
        # Twelve runs, each reporting one archive for the combination.
        self.assertEqual(merged_combination['archive_count'], 12)
        self.assertLessEqual(len(merged_combination['archives']), 8)

    def test_a_failed_root_is_recorded_and_the_run_is_incomplete(self):
        merged = census_all.merge(
            [summary('a.rpf', 2, [combination(0, 'format:rpf9', 2, 'archive', 'rpf')])],
            [{'archive': 'b.rpf', 'error': 'the table of contents is not authenticated'}],
            2,
        )
        self.assertFalse(merged['complete'])
        self.assertEqual(merged['failures'], [{'archive': 'b.rpf', 'error': 'the table of contents is not authenticated'}])
        self.assertEqual(merged['coverage']['failed_roots'], 1)
        self.assertEqual(merged['coverage']['roots_discovered'], 2)
        self.assertEqual(merged['coverage']['roots_opened'], 1)

    def test_combinations_with_different_header_variants_stay_apart(self):
        first = summary(
            'a.rpf',
            2,
            [
                combination(255, 'none', 1, 'bytes', variant='binary:0badc0de'),
                combination(255, 'none', 1, 'bytes', variant='text'),
            ],
        )
        merged = census_all.merge([first], [], 1)
        self.assertEqual(len(merged['combinations']), 2)
        variants = sorted(item['variant'] for item in merged['combinations'])
        self.assertEqual(variants, ['binary:0badc0de', 'text'])


class JournalTest(unittest.TestCase):
    def limits(self):
        return census_all.limits(700)

    def record(self, summary_path=None, **overrides):
        value = {
            'schema': census_all.SCHEMA_ID,
            'header_schema': census_all.CENSUS_HEADER_SCHEMA,
            'rules': census_all.RULES_ID,
            'registry': census_all.REGISTRY_ID,
            'mode': census_all.MODE,
            'limits': self.limits(),
            'build': 'exe-1',
            'scanner': 'scanner-1',
            'relative': 'pack/story000/story000.rpf',
            'root_fingerprint': '100:5',
            'summary_path': summary_path,
            'summary_bytes': None,
            'summary_sha256': None,
            'archives': 2,
            'entries': 700,
            'complete': True,
            'stopped': None,
        }
        value.update(overrides)
        return value

    def written(self, directory, content=None):
        """A summary file on disk, and the record fields that describe it."""
        path = os.path.join(directory, 'summary.jsonl')
        with io.open(path, 'w', encoding='utf-8', newline='\n') as handle:
            handle.write(content or json.dumps({'record': 'summary', 'entries': 700}) + '\n')
        return path, os.path.getsize(path), census_all.digest_of(path)

    def test_a_completed_root_is_reused_only_when_everything_matches(self):
        with tempfile.TemporaryDirectory() as directory:
            journal = os.path.join(directory, 'journal.jsonl')
            path, size, digest = self.written(directory)
            census_all.append_journal(
                journal,
                self.record(summary_path=path, summary_bytes=size, summary_sha256=digest),
            )
            done = census_all.load_journal(journal, 'exe-1', 'scanner-1', self.limits())
            self.assertIn('pack/story000/story000.rpf', done)
            # Another game build, another scanner build, another budget: work
            # this run did not do.
            self.assertEqual(
                census_all.load_journal(journal, 'exe-2', 'scanner-1', self.limits()), {}
            )
            self.assertEqual(
                census_all.load_journal(journal, 'exe-1', 'scanner-2', self.limits()), {}
            )
            self.assertEqual(
                census_all.load_journal(
                    journal, 'exe-1', 'scanner-1', census_all.limits(701)
                ),
                {},
            )

    def test_a_checkpoint_without_its_summary_is_not_reused(self):
        with tempfile.TemporaryDirectory() as directory:
            journal = os.path.join(directory, 'journal.jsonl')
            path, size, digest = self.written(directory)
            census_all.append_journal(
                journal,
                self.record(summary_path=path, summary_bytes=size, summary_sha256=digest),
            )
            # The summary is gone, truncated, or replaced by another one, and a
            # journal record must not authorize it on its own.
            os.remove(path)
            self.assertEqual(
                census_all.load_journal(journal, 'exe-1', 'scanner-1', self.limits()), {}
            )

    def test_a_stale_summary_is_not_reused(self):
        with tempfile.TemporaryDirectory() as directory:
            journal = os.path.join(directory, 'journal.jsonl')
            path, size, digest = self.written(directory)
            census_all.append_journal(
                journal,
                self.record(summary_path=path, summary_bytes=size, summary_sha256=digest),
            )
            with io.open(path, 'a', encoding='utf-8', newline='\n') as handle:
                handle.write(json.dumps({'record': 'summary', 'entries': 1}) + '\n')
            self.assertEqual(
                census_all.load_journal(journal, 'exe-1', 'scanner-1', self.limits()), {}
            )

    def test_a_stopped_root_is_pending_work_and_never_reused(self):
        with tempfile.TemporaryDirectory() as directory:
            journal = os.path.join(directory, 'journal.jsonl')
            path, size, digest = self.written(directory)
            census_all.append_journal(
                journal,
                self.record(
                    summary_path=path,
                    summary_bytes=size,
                    summary_sha256=digest,
                    stopped='max_archives',
                    complete=False,
                ),
            )
            self.assertEqual(
                census_all.load_journal(journal, 'exe-1', 'scanner-1', self.limits()), {}
            )

    def test_an_incompatible_checkpoint_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            journal = os.path.join(directory, 'journal.jsonl')
            path, size, digest = self.written(directory)
            for overrides in (
                {'schema': 'leonida-forge.rpf9-census-merged/1'},
                {'header_schema': 'leonida-forge.rpf9-census/0'},
                {'rules': 'older-rules'},
                {'registry': 'another-build'},
                {'mode': 'payload' if census_all.MODE != 'payload' else 'metadata-only'},
                {'limits': dict(self.limits(), max_depth=1)},
                {'limits': dict(self.limits(), max_entries=1)},
                # A checkpoint without a mode is older than the mode split.
                {'mode': None},
                # A checkpoint that claims completion without saying so.
                {'complete': None},
            ):
                census_all.append_journal(
                    journal,
                    self.record(
                        summary_path=path,
                        summary_bytes=size,
                        summary_sha256=digest,
                        **overrides,
                    ),
                )
            self.assertEqual(
                census_all.load_journal(journal, 'exe-1', 'scanner-1', self.limits()), {}
            )

    def test_a_truncated_journal_line_is_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            journal = os.path.join(directory, 'journal.jsonl')
            path, size, digest = self.written(directory)
            census_all.append_journal(
                journal,
                self.record(summary_path=path, summary_bytes=size, summary_sha256=digest),
            )
            with io.open(journal, 'a', encoding='utf-8') as handle:
                handle.write('{"schema": "leonida-forge.rpf9-cen')
            self.assertEqual(
                len(census_all.load_journal(journal, 'exe-1', 'scanner-1', self.limits())), 1
            )

    def test_an_append_after_a_truncated_record_starts_a_new_line(self):
        with tempfile.TemporaryDirectory() as directory:
            journal = os.path.join(directory, 'journal.jsonl')
            path, size, digest = self.written(directory)
            with io.open(journal, 'w', encoding='utf-8') as handle:
                handle.write('{"schema": "leonida-forge.rpf9-cen')
            census_all.append_journal(
                journal,
                self.record(summary_path=path, summary_bytes=size, summary_sha256=digest),
            )
            # The record must be readable, not glued to the torn one.
            self.assertEqual(
                len(census_all.load_journal(journal, 'exe-1', 'scanner-1', self.limits())), 1
            )


class ScanIdentityTest(unittest.TestCase):
    def test_the_identity_separates_every_input(self):
        budget = census_all.limits(5000)
        base = census_all.scan_identity('exe-1', 'scanner-1', '100:5', budget)
        self.assertEqual(base, census_all.scan_identity('exe-1', 'scanner-1', '100:5', budget))
        self.assertNotEqual(base, census_all.scan_identity('exe-2', 'scanner-1', '100:5', budget))
        self.assertNotEqual(base, census_all.scan_identity('exe-1', 'scanner-2', '100:5', budget))
        self.assertNotEqual(base, census_all.scan_identity('exe-1', 'scanner-1', '100:6', budget))
        # The entry budget is one of the limits, so a different one is a
        # different scan.
        self.assertNotEqual(
            base, census_all.scan_identity('exe-1', 'scanner-1', '100:5', census_all.limits(5001))
        )
        self.assertEqual(len(base), 64)

    def test_the_limits_include_the_entry_budget(self):
        self.assertEqual(census_all.limits(700)['max_entries'], 700)
        self.assertNotEqual(census_all.limits(700), census_all.limits(701))

    def test_a_root_fingerprint_notices_a_replaced_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, 'root.rpf')
            with io.open(path, 'wb') as handle:
                handle.write(b'A' * 4096)
            first = census_all.root_fingerprint(path)
            self.assertEqual(first, census_all.root_fingerprint(path))
            # Same size, different bytes: size and modification time alone
            # would not have noticed.
            with io.open(path, 'r+b') as handle:
                handle.write(b'B')
            self.assertNotEqual(first, census_all.root_fingerprint(path))


class CommandTest(unittest.TestCase):
    def test_every_root_carries_its_own_journal_and_identity(self):
        target, arguments = census_all.command(
            'pack/story000/story000.rpf',
            'D:/install/pack/story000/story000.rpf',
            'D:/install/game.exe',
            5000,
            'runs',
            'abc',
        )
        self.assertTrue(os.path.basename(target).startswith('pack%2Fstory000%2Fstory000.rpf-'))
        self.assertEqual(arguments[arguments.index('--root-name') + 1], 'pack/story000/story000.rpf')
        self.assertIn('--journal', arguments)
        journal = arguments[arguments.index('--journal') + 1]
        self.assertTrue(os.path.basename(journal).endswith('.journal.jsonl'))
        self.assertNotEqual(os.path.basename(journal), os.path.basename(target))
        self.assertEqual(arguments[arguments.index('--journal-identity') + 1], 'abc')

    def test_two_paths_that_a_naive_escape_would_collide_stay_apart(self):
        names = {
            census_all.artifact_name(relative, '.jsonl')
            for relative in (
                'a/b.rpf',
                'a__b.rpf',
                'a/b_rpf',
                'pack/core_bvh4/core_bvh4.rpf',
                'pack/core_bvh4_core_bvh4.rpf',
                # Two roots that differ only in case must not share a file on a
                # case-insensitive file system.
                'Data.rpf',
                'data.rpf',
            )
        }
        self.assertEqual(len(names), 7)

    def test_the_driver_never_sets_an_owned_option_twice(self):
        previous = os.environ.get('CENSUS_EXTRA')
        os.environ['CENSUS_EXTRA'] = '--max-depth 3 --metadata-only --entries --samples 5'
        try:
            _, arguments = census_all.command('a.rpf', 'a.rpf', 'exe', 10, 'runs', 'abc')
        finally:
            if previous is None:
                del os.environ['CENSUS_EXTRA']
            else:
                os.environ['CENSUS_EXTRA'] = previous
        self.assertEqual(arguments.count('--max-depth'), 1)
        self.assertEqual(arguments.count('--samples'), 1)
        self.assertEqual(arguments.count('--root-name'), 1)
        # The mode and the extra switches are the caller's to choose.
        self.assertIn('--metadata-only', arguments)
        self.assertIn('--entries', arguments)


class DiscoveryTest(unittest.TestCase):
    def test_roots_are_relative_and_keep_duplicate_basenames(self):
        with tempfile.TemporaryDirectory() as install:
            for relative in ('data.rpf', 'nested/data.rpf', 'nested/deeper/data.rpf'):
                path = os.path.join(install, relative)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with io.open(path, 'wb') as handle:
                    handle.write(b'9FPR')
            roots = census_all.discover(install)
            relatives = [relative for relative, _ in roots]
            self.assertEqual(
                relatives, ['data.rpf', 'nested/data.rpf', 'nested/deeper/data.rpf']
            )


class StaleOutputTest(unittest.TestCase):
    def test_a_stale_output_file_is_never_read_as_a_current_scan(self):
        with tempfile.TemporaryDirectory() as directory:
            runs = os.path.join(directory, 'runs')
            os.makedirs(runs)
            stale = os.path.join(runs, 'data.rpf.jsonl')
            with io.open(stale, 'w', encoding='utf-8', newline='\n') as handle:
                handle.write(
                    json.dumps(
                        {'record': 'summary', 'root': 'data.rpf', 'archives': 1, 'entries': 99}
                    )
                    + '\n'
                )
            # The binary cannot run, so the run fails; the stale file must not
            # be reported as its result.
            previous = census_all.CENSUS
            census_all.CENSUS = 'definitely-not-a-binary'
            try:
                found, error = census_all.census(
                    'data.rpf',
                    stale,
                    'exe',
                    10,
                    runs,
                    census_all.scan_identity('exe', 'scanner', '100:5', census_all.limits(10)),
                )
            finally:
                census_all.CENSUS = previous
            self.assertIsNone(found)
            self.assertTrue(error)
            target, _ = census_all.command(
                'data.rpf',
                stale,
                'exe',
                10,
                runs,
                census_all.scan_identity('exe', 'scanner', '100:5', census_all.limits(10)),
            )
            os.remove(target) if os.path.exists(target) else None
            self.assertFalse(os.path.exists(target))


class MatrixTest(unittest.TestCase):
    def test_the_type_archive_count_is_the_exact_one(self):
        permutations = [
            combination(5, 'resource:segment-5', 2, 'resource', archive='a.rpf'),
            combination(5, 'format:psin', 1, 'structural', archive='b.rpf'),
        ]
        merged = census_all.merge([summary('root.rpf', 3, permutations)], [], 1)
        # The census counted seven archives holding the type; the combinations
        # keep one representative archive each, and the largest list is one.
        merged['types'] = [{'type': 5, 'entries': 3, 'archives': 7}]
        document = entry_matrix.json_document(merged, entry_matrix.rows(merged))
        row = [item for item in document['type_summary'] if item['type'] == 5][0]
        self.assertEqual(row['archives'], 7)

    def test_combinations_that_differ_in_outcome_stay_apart(self):
        first = summary(
            'a.rpf',
            2,
            [
                combination(255, 'none', 1, 'bytes', outcome='unresolved'),
                combination(255, 'none', 1, 'bytes', outcome='identified'),
            ],
        )
        merged = census_all.merge([first], [], 1)
        self.assertEqual(len(merged['combinations']), 2)
        self.assertEqual(
            sorted(item['outcome'] for item in merged['combinations']),
            ['identified', 'unresolved'],
        )

    def test_combinations_that_differ_in_provenance_stay_apart(self):
        first = summary(
            'a.rpf',
            2,
            [
                combination(255, 'xml:root', 1, 'text', 'xml', provenance='payload'),
                combination(255, 'xml:root', 1, 'text', 'xml', provenance='native'),
            ],
        )
        merged = census_all.merge([first], [], 1)
        self.assertEqual(len(merged['combinations']), 2)
        self.assertEqual(
            sorted(item['extension_provenance'] for item in merged['combinations']),
            ['native', 'payload'],
        )

    def test_every_combination_carries_its_own_samples(self):
        merged = census_all.merge(
            [
                summary(
                    'a.rpf',
                    3,
                    [
                        combination(255, 'none', 1, 'bytes', variant='binary:0badc0de'),
                        combination(255, 'none', 2, 'bytes', variant='text'),
                    ],
                )
            ],
            [],
            1,
        )
        document = entry_matrix.document(merged, entry_matrix.rows(merged))
        self.assertIn('binary:0badc0de', document)
        self.assertIn('text', document)
        # One sample block per combination, not one per entry type.
        self.assertEqual(document.count('Samples of type'), 2)

    def test_the_json_document_counts_agree(self):
        merged = census_all.merge(
            [summary('a.rpf', 2, [combination(0, 'format:rpf9', 2, 'archive', 'rpf')])], [], 1
        )
        document = entry_matrix.json_document(merged, entry_matrix.rows(merged))
        self.assertEqual(document['entries'], 2)
        self.assertEqual(sum(item['entries'] for item in document['combinations']), 2)


if __name__ == '__main__':
    unittest.main()
