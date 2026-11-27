"""Print the counts a research document is allowed to quote.

Every figure in `entry-classification.md` is either published by the
machine-written matrix or printed here, so a document never carries a number no
tool can reproduce.

Usage:
    python census_facts.py <census-merged.jsonl> [<type-registry.json>]
"""

import io
import json
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


def distribution(combinations, field):
    totals = {}
    for combination in combinations:
        value = field(combination)
        if value is None:
            value = '-'
        totals[value] = totals.get(value, 0) + combination['entries']
    return sorted(totals.items(), key=lambda item: (-item[1], str(item[0])))


def section(title):
    print('')
    print('## ' + title)


def main():
    if len(sys.argv) not in (2, 3):
        raise SystemExit(__doc__)
    summary = load(sys.argv[1])
    combinations = summary['combinations']

    print('entries {:,}'.format(summary['entries']))
    print('archives {:,}'.format(summary['archives']))
    print('roots {:,}'.format(summary['roots']))
    print('complete {}'.format(summary.get('complete')))
    print('stopped {}'.format(summary['stopped'] or 'nothing'))
    print('failures {:,}'.format(len(summary['failures'])))
    for name, value in sorted((summary.get('coverage') or {}).items()):
        print('coverage {} {:,}'.format(name, value))

    section('outcome')
    for name, entries in distribution(combinations, lambda item: item.get('outcome')):
        print('{} {:,}'.format(name, entries))

    section('identification')
    for name, entries in distribution(
        combinations, lambda item: item['identification'].split(':', 1)[0]
    ):
        print('{} {:,}'.format(name, entries))

    section('format')
    for name, entries in distribution(
        combinations,
        lambda item: item['identification']
        if item['identification'].startswith('format:')
        else None,
    ):
        print('{} {:,}'.format(name, entries))

    section('capability')
    for name, entries in distribution(combinations, lambda item: item['capability']):
        print('{} {:,}'.format(name, entries))

    section('extension provenance')
    for name, entries in distribution(
        combinations, lambda item: item.get('extension_provenance')
    ):
        print('{} {:,}'.format(name, entries))

    section('extension')
    for name, entries in distribution(combinations, lambda item: item['extension']):
        print('{} {:,}'.format(name, entries))

    section('structure claim')
    for name, entries in distribution(combinations, lambda item: item.get('structure')):
        print('{} {:,}'.format(name, entries))

    section('payload state')
    for name, entries in distribution(combinations, lambda item: item['payload']):
        print('{} {:,}'.format(name, entries))

    section('storage')
    for name, entries in distribution(combinations, lambda item: item['storage']):
        print('{} {:,}'.format(name, entries))

    section('transform')
    transformed = sum(
        combination['entries'] for combination in combinations if combination['transform']
    )
    print('transformed {:,}'.format(transformed))
    print('untransformed {:,}'.format(summary['entries'] - transformed))

    section('types')
    print('observed {:,}'.format(len(summary['types'])))
    for item in summary['types']:
        print('type {} {:,}'.format(item['type'], item['entries']))

    if len(sys.argv) == 3:
        with io.open(sys.argv[2], encoding='utf-8') as handle:
            registry = json.load(handle)
        registered = {
            item['type']: item['extension'] for item in registry['ids'] if item['registered']
        }
        observed = {item['type'] for item in summary['types']}
        missing = sorted(entry for entry in registered if entry not in observed)
        section('registry coverage')
        print('registered {:,}'.format(len(registered)))
        print('registered observed {:,}'.format(len(registered) - len(missing)))
        print('registered unobserved {}'.format(' '.join(str(entry) for entry in missing)))
        print(
            'unregistered observed {}'.format(
                ' '.join(str(entry) for entry in sorted(observed) if entry not in registered)
            )
        )


if __name__ == '__main__':
    main()
