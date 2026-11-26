"""Run a bounded entry census over every root archive and merge the summaries.

`lforge archive census` writes one summary per run. This driver gives every root
archive of an installation the same entry budget, so the sample covers every
root instead of the first one, then merges the summaries into one record that
`entry_matrix.py` turns into the published matrix.

A complete census of a large installation is not affordable today: classifying
one entry decodes a chunk, not only a head.

Usage:
    LFORGE=/path/to/lforge python census_all.py <install-directory> <executable> <output-directory> [entries-per-root]
"""

import glob
import io
import json
import os
import subprocess
import sys

CENSUS = os.environ.get('LFORGE', 'lforge')


def census(root, executable, entries, directory):
    """One census run, as its summary record."""
    target = os.path.join(directory, os.path.basename(root) + '.jsonl')
    command = [
        CENSUS,
        'archive',
        'census',
        root,
        '--executable',
        executable,
        '--recursive',
        '--samples',
        '3',
        '--max-depth',
        '4',
        '--max-archives',
        '64',
        '--max-entries',
        str(entries),
        '--max-nested-bytes',
        '268435456',
        '--max-spool-bytes',
        '4294967296',
        '--output',
        target,
        '--overwrite',
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0 and not os.path.exists(target):
        return None, result.stderr.strip()
    with io.open(target, encoding='utf-8') as handle:
        for line in handle:
            record = json.loads(line)
            if record.get('record') == 'summary':
                return record, None
    return None, 'no summary'


def key(combination):
    return (
        combination['type'],
        combination['identification'],
        combination['storage'],
        combination['transform'],
        combination['payload'],
        combination['confidence'],
        combination['capability'],
        combination['extension'],
    )


def merge(summaries):
    combinations = {}
    types = {}
    failures = []
    archives = 0
    entries = 0
    spooled = 0
    roots = []
    stopped = {}
    for summary in summaries:
        archives += summary['archives']
        entries += summary['entries']
        spooled += summary['spooled_bytes']
        roots.append(summary['root'])
        if summary['stopped']:
            stopped[summary['root']] = summary['stopped']
        for item in summary['types']:
            types[item['type']] = types.get(item['type'], 0) + item['entries']
        for failure in summary['failures']:
            failures.append(failure)
        for combination in summary['combinations']:
            existing = combinations.get(key(combination))
            if existing is None:
                combinations[key(combination)] = {
                    **combination,
                    'archives': list(combination['archives']),
                    'samples': [dict(sample) for sample in combination['samples']],
                }
                continue
            existing['entries'] += combination['entries']
            for archive in combination['archives']:
                if archive not in existing['archives'] and len(existing['archives']) < 8:
                    existing['archives'].append(archive)
            for sample in combination['samples']:
                if len(existing['samples']) < 6:
                    existing['samples'].append(dict(sample))
    return {
        'record': 'summary',
        'schema': 'leonida-forge.rpf9-census-merged/1',
        'root': None,
        'roots': len(roots),
        'archive_roots': roots,
        'archives': archives,
        'entries': entries,
        'spooled_bytes': spooled,
        'stopped': stopped,
        'types': [
            {'type': entry_type, 'entries': count}
            for entry_type, count in sorted(types.items(), key=lambda item: (item[0] is None, item[0]))
        ],
        'combinations': sorted(combinations.values(), key=lambda combination: -combination['entries']),
        'failures': failures,
    }


def main():
    if len(sys.argv) not in (4, 5):
        raise SystemExit(__doc__)
    install, executable, directory = sys.argv[1:4]
    entries = int(sys.argv[4]) if len(sys.argv) == 5 else 900
    os.makedirs(directory, exist_ok=True)
    runs = os.path.join(directory, 'runs')
    os.makedirs(runs, exist_ok=True)
    roots = sorted(glob.glob(os.path.join(install, '*.rpf')))
    summaries = []
    for root in roots:
        summary, error = census(root, executable, entries, runs)
        if summary is None:
            print('{}: {}'.format(os.path.basename(root), error), flush=True)
        else:
            print(
                '{}: {} archives, {} entries{}'.format(
                    os.path.basename(root),
                    summary['archives'],
                    summary['entries'],
                    '' if not summary['stopped'] else ' (stopped: {})'.format(summary['stopped']),
                ),
                flush=True,
            )
            summaries.append(summary)
    merged = merge(summaries)
    target = os.path.join(directory, 'census-merged.jsonl')
    with io.open(target, 'w', encoding='utf-8', newline='\n') as handle:
        handle.write(json.dumps({'record': 'header', 'schema': merged['schema'], 'roots': merged['archive_roots']}) + '\n')
        handle.write(json.dumps(merged) + '\n')
    print('merged: {} entries in {} archives -> {}'.format(merged['entries'], merged['archives'], target))


if __name__ == '__main__':
    main()
