"""Turn a census JSONL summary into the matrix the research document quotes.

Reads the summary record of a `lforge archive census` run and writes:

- `entry-matrix.json`: the combinations, sorted by entry count, with samples.
- `entry-matrix.md`: the same as Markdown tables, one per entry type.

Usage: python entry_matrix.py <census.jsonl> <output-directory>
"""

import io
import json
import os
import sys


def load(path):
    with io.open(path, encoding='utf-8') as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            if record.get('record') == 'summary':
                return record
    raise SystemExit('no summary record in ' + path)


def rows(summary):
    combinations = sorted(
        summary['combinations'],
        key=lambda combination: (
            combination['type'] if combination['type'] is not None else 999,
            -combination['entries'],
            combination['identification'],
        ),
    )
    return combinations


def json_document(summary, combinations):
    return {
        'schema': 'leonida-forge.rpf9-entry-matrix/1',
        'census': summary['schema'],
        'root': summary.get('root'),
        'archive_roots': summary.get('archive_roots'),
        'archives': summary['archives'],
        'entries': summary['entries'],
        'stopped': summary['stopped'],
        'types': summary['types'],
        'combinations': combinations,
        'failures': summary['failures'],
    }


def cell(value):
    if value is None:
        return '-'
    text = str(value)
    return text.replace('|', '\\|')


def table(combinations):
    lines = [
        '| Type | Identification | Storage | Transform | Payload | Confidence | Capability | Extension | Entries |',
        '| ---- | -------------- | ------- | --------- | ------- | ---------- | ---------- | --------- | ------: |',
    ]
    for combination in combinations:
        lines.append(
            '| {} | {} | {} | {} | {} | {} | {} | {} | {} |'.format(
                cell(combination['type']),
                cell(combination['identification']),
                cell(combination['storage']),
                'yes' if combination['transform'] else 'no',
                cell(combination['payload']),
                cell(combination['confidence']),
                cell(combination['capability']),
                cell(combination['extension']),
                combination['entries'],
            )
        )
    return '\n'.join(lines)


def document(summary, combinations):
    stopped = summary['stopped']
    if isinstance(stopped, dict):
        stopped_text = ', '.join(
            '{}: {}'.format(name, reason) for name, reason in sorted(stopped.items())
        ) or 'nothing'
    else:
        stopped_text = cell(stopped)
    roots = summary.get('archive_roots') or [summary.get('root')]
    parts = [
        '# RPF9 entry matrix',
        '',
        'Machine-written from a `lforge archive census` run. Every row is one',
        'combination of properties observed in the sample: the entry type stored in',
        'the table of contents, the identification made from the decoded head, the',
        'storage shape, whether the payload transform applies, whether the payload',
        'decoded, the confidence of the identification, what the application can do',
        'with the entry, and the extension the classification allowed.',
        '',
        '- roots: {}'.format(', '.join('`{}`'.format(cell(root)) for root in roots)),
        '- archives opened: {}'.format(summary['archives']),
        '- entries classified: {}'.format(summary['entries']),
        '- stopped early: {}'.format(stopped_text),
        '',
        '## Every combination',
        '',
        table(combinations),
        '',
    ]
    by_type = {}
    for combination in combinations:
        by_type.setdefault(combination['type'], []).append(combination)
    parts.append('## By entry type')
    parts.append('')
    for entry_type in sorted(by_type, key=lambda value: (value is None, value)):
        group = by_type[entry_type]
        total = sum(combination['entries'] for combination in group)
        parts.append('### Type {}: {} entries'.format(cell(entry_type), total))
        parts.append('')
        parts.append(table(group))
        samples = [
            sample
            for combination in group
            for sample in combination['samples']
        ][:4]
        if samples:
            parts.append('')
            parts.append('Samples:')
            for sample in samples:
                parts.append(
                    '- `{}`: {} bytes, head `{}`'.format(
                        sample['chain'], cell(sample['size']), sample['head']
                    )
                )
        parts.append('')
    return '\n'.join(parts)


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    source, directory = sys.argv[1], sys.argv[2]
    summary = load(source)
    combinations = rows(summary)
    os.makedirs(directory, exist_ok=True)
    with io.open(os.path.join(directory, 'entry-matrix.json'), 'w', encoding='utf-8', newline='\n') as handle:
        json.dump(json_document(summary, combinations), handle, indent=1)
        handle.write('\n')
    with io.open(os.path.join(directory, 'entry-matrix.md'), 'w', encoding='utf-8', newline='\n') as handle:
        handle.write(document(summary, combinations))
        handle.write('\n')
    print('{} combinations, {} entries'.format(len(combinations), summary['entries']))


if __name__ == '__main__':
    main()
