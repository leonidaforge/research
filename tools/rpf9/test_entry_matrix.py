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
        'entries': entries,
        'archive_count': archive_count,
        'archives': [archive],
        'samples': [{'archive': archive, 'chain': archive + '!0', 'size': 16, 'head': '00' * 16}],
    }


def summary(relative, entries, combinations, stopped=None):
    return {
        'record': 'summary',
        'schema': 'leonida-forge.rpf9-census/1',
        'root': relative,
        'relative': relative,
        'archives': 1,
        'entries': entries,
        'spooled_bytes': 0,
        'stopped': stopped,
        'coverage': {'roots_discovered': 1, 'roots_opened': 1, 'entries_probed': entries},
        'types': [{'type': item['type'], 'entries': item['entries']} for item in combinations],
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
        # A run that stopped early is not complete.
        self.assertFalse(merged['complete'])

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
    def test_a_completed_root_is_reused_only_when_its_identity_matches(self):
        with tempfile.TemporaryDirectory() as directory:
            journal = os.path.join(directory, 'journal.jsonl')
            census_all.append_journal(
                journal,
                {
                    'schema': census_all.SCHEMA_ID,
                    'rules': census_all.RULES_ID,
                    'registry': census_all.REGISTRY_ID,
                    'build': 'exe-1',
                    'relative': 'pack/story000/story000.rpf',
                    'root_identity': '100:5',
                    'archives': 2,
                    'entries': 700,
                    'stopped': None,
                },
            )
            done = census_all.load_journal(journal)
            self.assertIn('pack/story000/story000.rpf', done)

    def test_an_incompatible_checkpoint_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            journal = os.path.join(directory, 'journal.jsonl')
            for schema, rules in (
                ('leonida-forge.rpf9-census-merged/1', census_all.RULES_ID),
                (census_all.SCHEMA_ID, 'older-rules'),
            ):
                census_all.append_journal(
                    journal,
                    {
                        'schema': schema,
                        'rules': rules,
                        'registry': census_all.REGISTRY_ID,
                        'build': 'exe-1',
                        'relative': 'data.rpf',
                        'root_identity': '100:5',
                        'archives': 1,
                        'entries': 1,
                        'stopped': None,
                    },
                )
            self.assertEqual(census_all.load_journal(journal), {})

    def test_a_truncated_journal_line_is_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            journal = os.path.join(directory, 'journal.jsonl')
            census_all.append_journal(
                journal,
                {
                    'schema': census_all.SCHEMA_ID,
                    'rules': census_all.RULES_ID,
                    'registry': census_all.REGISTRY_ID,
                    'build': 'exe-1',
                    'relative': 'data.rpf',
                    'root_identity': '100:5',
                    'archives': 1,
                    'entries': 1,
                    'stopped': None,
                },
            )
            with io.open(journal, 'a', encoding='utf-8') as handle:
                handle.write('{"schema": "leonida-forge.rpf9-cen')
            self.assertEqual(len(census_all.load_journal(journal)), 1)


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
                found, error = census_all.census('data.rpf', stale, 'exe', 10, runs)
            finally:
                census_all.CENSUS = previous
            self.assertIsNone(found)
            self.assertTrue(error)
            self.assertFalse(os.path.exists(stale))


class MatrixTest(unittest.TestCase):
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
