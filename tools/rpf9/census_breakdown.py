"""Print the breakdowns the follow-up backlog quotes.

The census publishes combinations, not per-entry records, so a question about
one family of entries is answered from the combinations' own dimensions:
storage, outcome, type, identification and the normalised header variant. Every
figure in the backlog comes from here.

Usage:
    python census_breakdown.py <census-merged.jsonl> [SECTION ...]
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


def totals(combinations, predicate, field):
    counts = {}
    entries = 0
    for combination in combinations:
        if not predicate(combination):
            continue
        entries += combination['entries']
        value = field(combination)
        counts[value] = counts.get(value, 0) + combination['entries']
    return entries, sorted(counts.items(), key=lambda item: (-item[1], str(item[0])))


def table(title, rows, key='Value'):
    print('')
    print('### ' + title)
    print('')
    print('| {} | Entries |'.format(key))
    print('| --- | ------: |')
    for value, entries in rows:
        print('| `{}` | {:,} |'.format(value, entries))


def samples(combinations, predicate, limit=6):
    lines = []
    for combination in combinations:
        if not predicate(combination):
            continue
        for sample in combination['samples'][:2]:
            lines.append(
                '{} rows, type {}: `{}`, {} bytes, head `{}`'.format(
                    combination['entries'],
                    combination['type'],
                    sample['chain'],
                    sample['size'],
                    sample['head'],
                )
            )
            if len(lines) >= limit:
                return lines
    return lines


def chunked4(summary):
    combinations = summary['combinations']
    is_chunked4 = lambda item: item['storage'] == 'chunked-4'
    entries, by_outcome = totals(combinations, is_chunked4, lambda item: item['outcome'])
    print('')
    print('## Chunk-encoding 4')
    print('')
    print('entries {:,}'.format(entries))
    _, by_type = totals(combinations, is_chunked4, lambda item: item['type'])
    table('By outcome', by_outcome, 'Outcome')
    table('By type', by_type, 'Type')
    undecodable = [item for item in combinations if item['storage'] == 'chunked-4' and item['payload'] == 'undecodable']
    decodable = [item for item in combinations if item['storage'] == 'chunked-4' and item['payload'] != 'undecodable']
    print('')
    print('Undecodable chunked-4 rows: {:,} in {} combination(s)'.format(
        sum(item['entries'] for item in undecodable), len(undecodable)))
    print('Decodable chunked-4 rows: {:,} in {} combination(s)'.format(
        sum(item['entries'] for item in decodable), len(decodable)))
    print('')
    print('Representative undecodable samples:')
    for line in samples(combinations, lambda item: item['storage'] == 'chunked-4' and item['payload'] == 'undecodable'):
        print('- ' + line)
    print('')
    print('Representative decodable samples:')
    for line in samples(combinations, lambda item: item['storage'] == 'chunked-4' and item['payload'] != 'undecodable'):
        print('- ' + line)
    print('')
    print('Every undecodable entry uses chunked-4: {}'.format(
        all(item['storage'] == 'chunked-4' for item in combinations if item['payload'] == 'undecodable')))


def transform(summary):
    combinations = summary['combinations']
    transformed = lambda item: item['transform']
    entries, by_outcome = totals(combinations, transformed, lambda item: item['outcome'])
    _, by_type = totals(combinations, transformed, lambda item: item['type'])
    _, by_storage = totals(combinations, transformed, lambda item: item['storage'])
    print('')
    print('## Payload transform')
    print('')
    print('transformed entries {:,}'.format(entries))
    table('By outcome', by_outcome, 'Outcome')
    table('By type', by_type, 'Type')
    table('By storage', by_storage, 'Storage')
    blocked = [item for item in combinations if item['transform'] and item['outcome'] == 'blocked']
    print('')
    print('Blocked transformed rows: {:,}'.format(sum(item['entries'] for item in blocked)))
    for line in samples(combinations, lambda item: item['transform'] and item['outcome'] == 'blocked'):
        print('- ' + line)


def resources(summary):
    combinations = summary['combinations']
    is_resource = lambda item: item['identification'].startswith('resource:')
    entries, by_variant = totals(combinations, is_resource, lambda item: item['variant'])
    print('')
    print('## Resource headers')
    print('')
    print('resource entries {:,}'.format(entries))
    table('By normalised header variant', by_variant, 'Variant')
    _, by_type = totals(combinations, is_resource, lambda item: item['type'])
    table('By type', by_type, 'Type')


def unregistered(summary):
    combinations = summary['combinations']
    is_255 = lambda item: item['type'] == 255
    entries, by_identification = totals(combinations, is_255, lambda item: item['identification'].split(':', 1)[0])
    _, by_provenance = totals(combinations, is_255, lambda item: item['extension_provenance'])
    _, by_outcome = totals(combinations, is_255, lambda item: item['outcome'])
    print('')
    print('## Type 255')
    print('')
    print('entries {:,}'.format(entries))
    table('By identification kind', by_identification, 'Kind')
    table('By extension provenance', by_provenance, 'Provenance')
    table('By outcome', by_outcome, 'Outcome')
    without = sum(item['entries'] for item in combinations if item['type'] == 255 and item['extension'] == '-')
    print('')
    print('Without an extension: {:,}'.format(without))
    print('')
    print('Distinct identifications:')
    for value, count in totals(combinations, is_255, lambda item: item['identification'])[1][:24]:
        print('- `{}`: {:,}'.format(value, count))


def observed(summary, type_ids):
    combinations = summary['combinations']
    print('')
    print('## Newly observed types')
    for type_id in type_ids:
        rows = [item for item in combinations if item['type'] == type_id]
        entries = sum(item['entries'] for item in rows)
        archives = [item for item in summary['types'] if item['type'] == type_id]
        print('')
        print('### Type {}{}'.format(
            type_id,
            '' if not archives else ' ({} archives)'.format(archives[0].get('archives'))))
        print('')
        print('entries {:,}'.format(entries))
        for item in rows:
            print(
                '- {} rows, {} entries, extension `{}` ({}), outcome {}, structure {}'.format(
                    item['identification'],
                    item['entries'],
                    item['extension'],
                    item['extension_provenance'],
                    item['outcome'],
                    item['structure'],
                )
            )
        for line in samples(combinations, lambda item: item['type'] == type_id, limit=4):
            print('- ' + line)


SECTIONS = {
    'chunked4': chunked4,
    'transform': transform,
    'resources': resources,
    'unregistered': unregistered,
}


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    summary = load(sys.argv[1])
    wanted = sys.argv[2:] or list(SECTIONS)
    for name in wanted:
        if name == 'observed':
            observed(summary, [18, 100, 104, 105, 113])
        else:
            SECTIONS[name](summary)


if __name__ == '__main__':
    main()
