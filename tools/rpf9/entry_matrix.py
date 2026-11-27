"""Turn a merged census into the matrix the research document quotes.

Reads the summary record of a `census_all.py` run and writes:

- `<name>.json`: the combinations with their samples, coverage and type summary;
- `<name>.md`: the same as Markdown: the coverage counts, the per-root table, the
  type summary, the distributions, one table per entry type and a sample block
  for every combination, so no combination loses its evidence.

Usage: python entry_matrix.py <census-merged.jsonl> <output-directory> [NAME]
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
        'roots_detail': summary.get('roots_detail'),
        'archives': summary['archives'],
        'entries': summary['entries'],
        'stopped': summary['stopped'],
        'complete': summary.get('complete'),
        'completion': summary.get('completion'),
        'coverage': summary.get('coverage'),
        'outcomes': summary.get('outcomes'),
        'types': summary['types'],
        'type_summary': type_summary(combinations, summary),
        'combinations': combinations,
        'rejections': summary.get('rejections'),
        'failures': summary['failures'],
    }


def cell(value):
    if value is None:
        return '-'
    if isinstance(value, int):
        return format(value, ',')
    return str(value).replace('|', '\\|')


# The order the coverage counts are published in. Every count the merged summary
# carries is published; this list only decides which come first.
COVERAGE_ORDER = (
    'roots_discovered',
    'roots_opened',
    'failed_roots',
    'archives_opened',
    'nested_archives_opened',
    'archives_resumed',
    'failed_archives',
    'rejected_archive_candidates',
    'entries_enumerated',
    'entries_probed',
    'entries_decoded',
    'entries_undecoded',
    'structures_verified',
    'containers_identified',
    'declared_asset_classes',
    'unresolved_formats',
)


def completion_table(summary):
    completion = summary.get('completion') or {}
    checks = completion.get('checks') or {}
    lines = [
        '## Completion',
        '',
        '| Check | Value |',
        '| ----- | ----- |',
        '| complete | {} |'.format(cell(completion.get('complete', summary.get('complete')))),
        '| reasons | {} |'.format(', '.join(completion.get('reasons') or []) or 'none'),
        '| pending traversal | {} |'.format(cell(completion.get('pending_traversal'))),
    ]
    for name in sorted(checks):
        lines.append('| {} | {} |'.format(name, cell(checks[name])))
    lines.append('')
    return lines


def outcomes_table(summary):
    outcomes = summary.get('outcomes') or {}
    if not outcomes:
        return []
    lines = [
        '## Outcomes',
        '',
        'Every entry has exactly one, so the counts add up to the entry count.',
        '',
        '| Outcome | Entries |',
        '| ------- | ------: |',
    ]
    for name, entries in sorted(outcomes.items(), key=lambda item: -item[1]):
        lines.append('| {} | {} |'.format(cell(name), cell(entries)))
    lines.append('')
    return lines


def roots_table(summary):
    detail = summary.get('roots_detail')
    if not detail:
        return []
    lines = [
        '## By root',
        '',
        '| Root | Archives | Entries | Stopped |',
        '| ---- | -------: | ------: | ------- |',
    ]
    for root in detail:
        lines.append(
            '| {} | {} | {} | {} |'.format(
                cell(root['root']),
                cell(root['archives']),
                cell(root['entries']),
                cell(root['stopped']),
            )
        )
    lines.append('')
    return lines


def kind(identification):
    """`format:psin` -> `format`; the part before the first colon."""
    return identification.split(':', 1)[0]


def distribution(combinations, field):
    """Entries per value of one property, largest first."""
    totals = {}
    for combination in combinations:
        value = field(combination)
        totals[value] = totals.get(value, 0) + combination['entries']
    return sorted(totals.items(), key=lambda item: (-item[1], str(item[0])))


def tally(target, value, entries):
    if value is None:
        value = '-'
    target[value] = target.get(value, 0) + entries


def type_summary(combinations, summary=None):
    """One row per entry type: what the type declared and what its rows were.

    The declared extensions come from the registry (the type's own property);
    the payload extensions come from the bytes. Keeping them apart is what stops
    a registry entry from being reported as a verified asset class.

    The archive count is the exact number of archives that hold an entry of the
    type, which only the census can know: a combination keeps a bounded
    representative list of archive names, and the largest such list is not the
    number of archives.
    """
    archives = {}
    for item in (summary or {}).get('types') or []:
        archives[item['type']] = item.get('archives')
    types = {}
    for combination in combinations:
        row = types.setdefault(
            combination['type'],
            {
                'type': combination['type'],
                'entries': 0,
                'archives': 0,
                'identifications': {},
                'outcomes': {},
                'declared': {},
                'payload': {},
            },
        )
        entries = combination['entries']
        row['entries'] += entries
        row['archives'] = max(row['archives'], combination.get('archive_count') or 0)
        tally(row['outcomes'], combination.get('outcome'), entries)
        provenance = combination.get('extension_provenance')
        extension = combination['extension']
        if provenance == 'native' and extension != '-':
            tally(row['declared'], extension, entries)
        if provenance == 'payload' and extension != '-':
            tally(row['payload'], extension, entries)
    for row in types.values():
        if archives.get(row['type']) is not None:
            row['archives'] = archives[row['type']]
    return sorted(types.values(), key=lambda row: (row['type'] is None, row['type']))


def type_table(combinations, summary=None):
    rows = type_summary(combinations, summary)
    if not rows:
        return []
    lines = [
        '## Type summary',
        '',
        'Sorted by type id. `declared` is the extension the engine registers for the type;',
        '`from payload` is an extension the bytes themselves established. `archives` is the',
        'exact number of archives that hold an entry of the type.',
        '',
        '| Type | Entries | Archives | Declared | From payload | Outcomes |',
        '| ---- | ------: | -------: | -------- | ------------ | -------- |',
    ]
    for row in rows:
        declared = ', '.join(
            '`{}` {}'.format(name, cell(entries))
            for name, entries in sorted(row['declared'].items())
        )
        payload = ', '.join(
            '`{}` {}'.format(name, cell(entries))
            for name, entries in sorted(row['payload'].items())
        )
        outcomes = ', '.join(
            '{} {}'.format(name, cell(entries))
            for name, entries in sorted(row['outcomes'].items())
        )
        lines.append(
            '| {} | {} | {} | {} | {} | {} |'.format(
                cell(row['type']),
                cell(row['entries']),
                cell(row['archives']),
                declared or '-',
                payload or '-',
                outcomes or '-',
            )
        )
    lines.append('')
    return lines


def distribution_tables(combinations):
    tables = (
        ('Identification kind', lambda item: kind(item['identification'])),
        ('Format', lambda item: item['identification']),
        ('Capability', lambda item: item['capability']),
        ('Outcome', lambda item: item.get('outcome')),
        ('Extension', lambda item: item['extension']),
        ('Extension provenance', lambda item: item.get('extension_provenance')),
        ('Structure claim', lambda item: item.get('structure')),
        ('Payload state', lambda item: item['payload']),
        ('Storage', lambda item: item['storage']),
        ('Entry type', lambda item: item['type']),
    )
    lines = ['## Distributions', '']
    for title, field in tables:
        lines.extend(
            [
                '### ' + title,
                '',
                '| Value | Entries |',
                '| ----- | ------: |',
            ]
        )
        for value, entries in distribution(combinations, field):
            lines.append('| {} | {} |'.format(cell(value), cell(entries)))
        lines.append('')
    return lines


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


def document(summary, combinations, title='RPF9 entry matrix'):
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
        '# ' + title,
        '',
        'Machine-written from a `lforge archive census` run. Every row is one',
        'combination of properties observed in the run: the entry type stored in',
        'the table of contents, the identification made from the decoded head, a',
        'normalised shape of that head, the storage shape, whether the payload',
        'transform applies, whether the payload decoded, whether the structure was',
        'validated, what the application can do with the entry, the extension the',
        'classification allowed and where that extension came from.',
        '',
        '## Coverage',
        '',
        '| Count | Value |',
        '| ----- | ----: |',
    ]
    for name in COVERAGE_ORDER:
        if name in coverage:
            parts.append('| {} | {} |'.format(name, cell(coverage[name])))
    for name in sorted(coverage):
        # A count the writer does not know about is still published.
        if name not in COVERAGE_ORDER:
            parts.append('| {} | {} |'.format(name, cell(coverage[name])))
    roots = coverage.get('roots_discovered', len(roots))
    parts.extend(
        [
            '| stopped early | {} |'.format(stopped_text),
            '| complete | {} |'.format(summary.get('complete')),
            '',
            'A bounded run is a sample. Only a run whose coverage reports every',
            'discovered root and no stopped scan is a count of the installation.',
            '',
        ]
    )
    parts.extend(roots_table(summary))
    parts.extend(completion_table(summary))
    parts.extend(outcomes_table(summary))
    parts.extend(type_table(combinations, summary))
    parts.extend(distribution_tables(combinations))
    parts.extend(
        [
            '## Every combination',
            '',
            table(combinations),
            '',
        ]
    )
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
    if len(sys.argv) not in (3, 4):
        raise SystemExit(__doc__)
    source, directory = sys.argv[1], sys.argv[2]
    name = sys.argv[3] if len(sys.argv) == 4 else 'entry-matrix'
    summary = load(source)
    combinations = rows(summary)
    os.makedirs(directory, exist_ok=True)
    with io.open(
        os.path.join(directory, name + '.json'), 'w', encoding='utf-8', newline='\n'
    ) as handle:
        json.dump(json_document(summary, combinations), handle, indent=1)
        handle.write('\n')
    with io.open(
        os.path.join(directory, name + '.md'), 'w', encoding='utf-8', newline='\n'
    ) as handle:
        handle.write(document(summary, combinations, 'RPF9 ' + name.replace('-', ' ')))
        handle.write('\n')
    print(
        '{} combinations, {} entries -> {}.md'.format(len(combinations), summary['entries'], name)
    )


if __name__ == '__main__':
    main()
