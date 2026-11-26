import io
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import census_all
import entry_matrix


def combination(entry_type, identification, entries, capability, extension='-', confidence='probable', payload='decoded', archive='a.rpf'):
    return {
        'type': entry_type,
        'identification': identification,
        'storage': 'chunked-2',
        'transform': False,
        'payload': payload,
        'confidence': confidence,
        'capability': capability,
        'extension': extension,
        'entries': entries,
        'archives': [archive],
        'samples': [{'archive': archive, 'chain': archive + '!0', 'size': 16, 'head': '00' * 16}],
    }


def summary(root, entries, combinations, stopped=None):
    return {
        'record': 'summary',
        'schema': 'leonida-forge.rpf9-census/1',
        'root': root,
        'archives': 1,
        'entries': entries,
        'spooled_bytes': 0,
        'stopped': stopped,
        'types': [{'type': item['type'], 'entries': item['entries']} for item in combinations],
        'combinations': combinations,
        'failures': [],
    }


class MergeTest(unittest.TestCase):
    def test_the_merged_counts_add_up(self):
        first = summary('a.rpf', 3, [combination(0, 'format:rpf9', 1, 'archive'), combination(255, 'resource:segment-5', 2, 'resource')])
        second = summary('b.rpf', 4, [combination(255, 'resource:segment-5', 3, 'resource'), combination(11, 'format:psin', 1, 'structural')], 'max_entries')
        merged = census_all.merge([first, second])
        self.assertEqual(merged['entries'], 7)
        self.assertEqual(sum(item['entries'] for item in merged['combinations']), 7)
        self.assertEqual(len(merged['combinations']), 3)
        resource = [item for item in merged['combinations'] if item['identification'] == 'resource:segment-5'][0]
        self.assertEqual(resource['entries'], 5)
        self.assertEqual(merged['stopped'], {'b.rpf': 'max_entries'})

    def test_a_combination_keeps_bounded_samples(self):
        merged = census_all.merge([
            summary('a.rpf', 1, [combination(255, 'resource:segment-5', 1, 'resource')]),
            summary('b.rpf', 1, [combination(255, 'resource:segment-5', 1, 'resource', archive='b.rpf')]),
        ])
        self.assertEqual(len(merged['combinations'][0]['samples']), 2)
        self.assertEqual(merged['combinations'][0]['archives'], ['a.rpf', 'b.rpf'])
        self.assertEqual(merged['combinations'][0]['entries'], 2)


class MatrixTest(unittest.TestCase):
    def test_the_document_reports_the_combinations(self):
        merged = census_all.merge([
            summary('a.rpf', 2, [combination(0, 'format:rpf9', 1, 'archive', 'rpf'), combination(5, 'resource:segment-5', 1, 'resource')])
        ])
        combinations = entry_matrix.rows(merged)
        document = entry_matrix.document(merged, combinations)
        self.assertIn('| 0 | format:rpf9 | chunked-2 | no | decoded | probable | archive | rpf | 1 |', document)
        self.assertIn('| 5 | resource:segment-5 | chunked-2 | no | decoded | probable | resource | - | 1 |', document)

    def test_the_json_document_counts_agree(self):
        merged = census_all.merge([summary('a.rpf', 2, [combination(0, 'format:rpf9', 2, 'archive', 'rpf')])])
        document = entry_matrix.json_document(merged, entry_matrix.rows(merged))
        self.assertEqual(document['entries'], 2)
        self.assertEqual(sum(item['entries'] for item in document['combinations']), 2)


if __name__ == '__main__':
    unittest.main()
