"""Run a bounded entry census over every root archive and merge the summaries.

`lforge archive census` writes one summary per run. This driver:

- discovers root archives recursively, keeping installation-relative paths so
  archives with the same basename in different folders stay distinct;
- deletes the target before each run and refuses a file without a complete
  summary, so a stale result is never read as a current scan;
- records every failed root in the merged summary and marks the run incomplete,
  so a partial scan is never described as exhaustive;
- merges with exact archive occurrence counts.

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
import uuid

CENSUS = os.environ.get('LFORGE', 'lforge')

# Identities a checkpoint must match before it is reused.
SCHEMA_ID = 'leonida-forge.rpf9-census-merged/2'
RULES_ID = 'claims+native-registry'
REGISTRY_ID = 'e95020b2'


def build_identity(executable):
    """Size and modification time of the executable, as a build identity."""
    info = os.stat(executable)
    return '{}:{}'.format(info.st_size, int(info.st_mtime))


def root_identity(path):
    info = os.stat(path)
    return '{}:{}'.format(info.st_size, int(info.st_mtime))


def load_journal(path):
    """Completed roots from an append-only journal, keyed by relative path."""
    done = {}
    if not os.path.exists(path):
        return done
    with io.open(path, encoding='utf-8') as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except ValueError:
                # A truncated last line is an interrupted write, not a result.
                continue
            if record.get('schema') != SCHEMA_ID:
                continue
            if record.get('rules') != RULES_ID or record.get('registry') != REGISTRY_ID:
                continue
            done[record['relative']] = record
    return done


def append_journal(path, record):
    """Append one completed root, flushed to disk before it is trusted."""
    with io.open(path, 'a', encoding='utf-8', newline='\n') as handle:
        handle.write(json.dumps(record, sort_keys=True) + '\n')
        handle.flush()
        os.fsync(handle.fileno())


def discover(install):
    """Every `.rpf` under `install`, as (relative path, path), sorted."""
    roots = []
    for path in glob.glob(os.path.join(install, '**', '*.rpf'), recursive=True):
        relative = os.path.relpath(path, install).replace('\\', '/')
        roots.append((relative, path))
    roots.sort()
    return roots


def census(relative, path, executable, entries, directory):
    """One census run. Returns (summary, error); never a stale summary."""
    name = relative.replace('/', '__') + '.jsonl'
    target = os.path.join(directory, name)
    if os.path.exists(target):
        os.remove(target)
    token = uuid.uuid4().hex
    command = [
        CENSUS,
        'archive',
        'census',
        path,
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
    command.extend(os.environ.get('CENSUS_EXTRA', '').split())
    try:
        result = subprocess.run(command, capture_output=True, text=True)
    except OSError as failure:
        return None, 'cannot run {}: {}'.format(CENSUS, failure)
    summary = None
    error = result.stderr.strip().splitlines()[-1] if result.stderr.strip() else ''
    if os.path.exists(target):
        try:
            with io.open(target, encoding='utf-8') as handle:
                for line in handle:
                    record = json.loads(line)
                    if record.get('record') == 'summary':
                        summary = record
        except (OSError, ValueError) as failure:
            error = error or 'unreadable output: {}'.format(failure)
    if summary is None:
        return None, error or 'no summary record'
    summary['relative'] = relative
    summary['token'] = token
    return summary, None


def key(combination):
    return (
        combination['type'],
        combination['identification'],
        combination.get('variant'),
        combination['storage'],
        combination['transform'],
        combination['payload'],
        combination.get('structure'),
        combination['capability'],
        combination['extension'],
    )


def merge(summaries, failures, discovered):
    combinations = {}
    types = {}
    archives = 0
    entries = 0
    spooled = 0
    stopped = {}
    coverage = {}
    for summary in summaries:
        archives += summary['archives']
        entries += summary['entries']
        spooled += summary['spooled_bytes']
        if summary['stopped']:
            stopped[summary['relative']] = summary['stopped']
        for name, value in summary.get('coverage', {}).items():
            if name in ('roots_discovered', 'roots_opened'):
                continue
            coverage[name] = coverage.get(name, 0) + value
        for item in summary['types']:
            types[item['type']] = types.get(item['type'], 0) + item['entries']
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
            existing['archive_count'] = existing.get('archive_count', 0) + combination.get(
                'archive_count', 0
            )
            for archive in combination['archives']:
                if archive not in existing['archives'] and len(existing['archives']) < 8:
                    existing['archives'].append(archive)
            for sample in combination['samples']:
                if len(existing['samples']) < 24:
                    existing['samples'].append(dict(sample))
    coverage['roots_discovered'] = discovered
    coverage['roots_opened'] = len(summaries)
    coverage['failed_roots'] = len(failures)
    return {
        'record': 'summary',
        'schema': 'leonida-forge.rpf9-census-merged/2',
        'root': None,
        'roots': len(summaries),
        'archive_roots': [summary['relative'] for summary in summaries],
        'archives': archives,
        'entries': entries,
        'spooled_bytes': spooled,
        'stopped': stopped,
        'complete': not stopped and not failures and len(summaries) == discovered,
        'coverage': coverage,
        'types': [
            {'type': entry_type, 'entries': count}
            for entry_type, count in sorted(
                types.items(), key=lambda item: (item[0] is None, item[0])
            )
        ],
        'combinations': sorted(
            combinations.values(), key=lambda combination: -combination['entries']
        ),
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
    journal_path = os.path.join(directory, 'journal.jsonl')
    identity = build_identity(executable)
    done = load_journal(journal_path)
    roots = discover(install)
    print('{} root archives discovered'.format(len(roots)), flush=True)
    if done:
        print('journal holds {} completed roots'.format(len(done)), flush=True)
    summaries = []
    failures = []
    for relative, path in roots:
        fingerprint = root_identity(path)
        reuse = done.get(relative)
        if reuse is not None and reuse.get('root_identity') == fingerprint and reuse.get(
            'build'
        ) == identity:
            # A completed root whose archive and build are unchanged: its
            # persisted summary is reused, not recomputed.
            target = os.path.join(runs, relative.replace('/', '__') + '.jsonl')
            summary = None
            if os.path.exists(target):
                with io.open(target, encoding='utf-8') as handle:
                    for line in handle:
                        record = json.loads(line)
                        if record.get('record') == 'summary':
                            summary = record
                            summary['relative'] = relative
            if summary is not None:
                print('{}: resumed from the journal'.format(relative), flush=True)
                summaries.append(summary)
                continue
        summary, error = census(relative, path, executable, entries, runs)
        if summary is None:
            print('{}: FAILED {}'.format(relative, error), flush=True)
            failures.append({'archive': relative, 'error': error})
            continue
        append_journal(
            journal_path,
            {
                'schema': SCHEMA_ID,
                'rules': RULES_ID,
                'registry': REGISTRY_ID,
                'build': identity,
                'relative': relative,
                'root_identity': fingerprint,
                'archives': summary['archives'],
                'entries': summary['entries'],
                'stopped': summary['stopped'],
            },
        )
        print(
            '{}: {} archives, {} entries{}'.format(
                relative,
                summary['archives'],
                summary['entries'],
                '' if not summary['stopped'] else ' (stopped: {})'.format(summary['stopped']),
            ),
            flush=True,
        )
        summaries.append(summary)
    merged = merge(summaries, failures, len(roots))
    target = os.path.join(directory, 'census-merged.jsonl')
    with io.open(target, 'w', encoding='utf-8', newline='\n') as handle:
        handle.write(
            json.dumps(
                {'record': 'header', 'schema': merged['schema'], 'roots': merged['archive_roots']}
            )
            + '\n'
        )
        handle.write(json.dumps(merged) + '\n')
    print(
        'merged: {} entries in {} archives, complete={} -> {}'.format(
            merged['entries'], merged['archives'], merged['complete'], target
        )
    )


if __name__ == '__main__':
    main()
