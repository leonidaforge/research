"""Turn a merged census into the matrix the research document quotes.

Reads the summary record of a `census_all.py` run and writes:

- `entry-matrix.json`: the combinations with their samples and coverage;
- `entry-matrix.md`: the same as Markdown, one table per entry type and a
  sample block for every combination, so no combination loses its evidence.

Usage: python entry_matrix.py <census-merged.jsonl> <output-directory>
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
    return sorted(
        summary['combinations'],
        key=lambda combination: (
            combination['type'] if combination['type'] is not None else 999,
            -combination['entries'],
            combination['identification'],
            combination.get('variant') or '',
        ),
    )


def json_document(summary, combinations):
    return {
        'schema': 'leonida-forge.rpf9-entry-matrix/2',
        'census': summary['schema'],
        'archive_roots': summary.get('archive_roots') or [summary.get('root')],
        'archives': summary['archives'],
        'entries': summary['entries'],
        'stopped': summary['stopped'],
        'complete': summary.get('complete'),
        'coverage': summary.get('coverage'),
        'types': summary['types'],
        'combinations': combinations,
        'failures': summary['failures'],
    }


def cell(value):
    if value is None:
        return '-'
    return str(value).replace('|', '\\|')


def table(combinations):
    lines = [
        '| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |',
        '| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |',
    ]
    for combination in combinations:
        lines.append(
            '| {} | {} | {} | {} | {} | {} | {} | {} | {} | {} | {} |'.format(
                cell(combination['type']),
                cell(combination['identification']),
                cell(combination.get('variant')),
                cell(combination['storage']),
                'yes' if combination['transform'] else 'no',
                cell(combination['payload']),
                cell(combination.get('structure')),
                cell(combination['capability']),
                cell(combination['extension']),
                combination['entries'],
                combination.get('archive_count', '-'),
            )
        )
    return '\n'.join(lines)


def samples(combination):
    lines = ['Samples of type {} as `{}`:'.format(
        cell(combination['type']), cell(combination.get('variant') or combination['identification'])
    )]
    for sample in combination['samples']:
        lines.append(
            '- `{}`: {} bytes, head `{}`'.format(
                sample['chain'], cell(sample['size']), sample['head']
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
    coverage = summary.get('coverage') or {}
    parts = [
        '# RPF9 entry matrix',
        '',
        'Machine-written from a `lforge archive census` run. Every row is one',
        'combination of properties observed in the sample: the entry type stored in',
        'the table of contents, the identification made from the decoded head, a',
        'normalised shape of that head, the storage shape, whether the payload',
        'transform applies, whether the payload decoded, whether the structure was',
        'validated, what the application can do with the entry, and the extension',
        'the classification allowed.',
        '',
        '- roots discovered: {}'.format(coverage.get('roots_discovered', len(roots))),
        '- roots opened: {}'.format(coverage.get('roots_opened', len(roots))),
        '- archives opened: {}'.format(summary['archives']),
        '- entries classified: {}'.format(summary['entries']),
        '- structures verified: {}'.format(coverage.get('structures_verified', '-')),
        '- asset classes verified: {}'.format(coverage.get('assets_verified', '-')),
        '- unresolved formats: {}'.format(coverage.get('unresolved_formats', '-')),
        '- stopped early: {}'.format(stopped_text),
        '- complete: {}'.format(summary.get('complete')),
        '',
        'A bounded run is a sample. Only a run whose coverage reports every',
        'discovered root and no stopped scan is a count of the installation.',
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
        for combination in group:
            if combination['samples']:
                parts.append('')
                parts.append(samples(combination))
        parts.append('')
    return '\n'.join(parts)


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    source, directory = sys.argv[1], sys.argv[2]
    summary = load(source)
    combinations = rows(summary)
    os.makedirs(directory, exist_ok=True)
    with io.open(
        os.path.join(directory, 'entry-matrix.json'), 'w', encoding='utf-8', newline='\n'
    ) as handle:
        json.dump(json_document(summary, combinations), handle, indent=1)
        handle.write('\n')
    with io.open(
        os.path.join(directory, 'entry-matrix.md'), 'w', encoding='utf-8', newline='\n'
    ) as handle:
        handle.write(document(summary, combinations))
        handle.write('\n')
    print('{} combinations, {} entries'.format(len(combinations), summary['entries']))


if __name__ == '__main__':
    main()
