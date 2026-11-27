"""Run an entry census over every root archive and merge the summaries.

`lforge archive census` writes one summary per run. This driver:

- discovers root archives recursively, keeping installation-relative paths so
  archives with the same basename in different folders stay distinct;
- deletes the target before each run and refuses a file without a complete
  summary, so a stale result is never read as a current scan;
- records every failed root in the merged summary and marks the run incomplete,
  so a partial scan is never described as exhaustive;
- gives every root a journal of its own, so an interrupted root resumes at the
  nested archive where it stopped instead of starting over. A journal is reused
  only for the same schema, rules, registry, scan mode, limits, executable bytes
  and root bytes;
- merges with exact archive occurrence counts.

A complete payload census of a large installation is expensive: classifying one
entry decodes a chunk, not only a head. A metadata-only pass is the cheaper
inventory and does not replace the payload pass.

Usage:
    LFORGE=/path/to/lforge python census_all.py <install-directory> <executable> <output-directory> [entries-per-root]
"""

import glob
import hashlib
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
# `metadata-only` and `payload` are different investigations over the same
# archives. A checkpoint from one must never satisfy the other.
MODE = 'metadata-only' if '--metadata-only' in os.environ.get('CENSUS_EXTRA', '').split() else 'payload'


def option(name, default):
    return int(os.environ.get(name, default))


LIMITS = {
    'max_depth': option('CENSUS_MAX_DEPTH', 8),
    'max_archives': option('CENSUS_MAX_ARCHIVES', 4096),
    'max_nested_bytes': option('CENSUS_MAX_NESTED_BYTES', 268435456),
    'max_spool_bytes': option('CENSUS_MAX_SPOOL_BYTES', 4294967296),
}


def build_identity(executable):
    """SHA-256 of the executable, so a rebuilt binary is a different build."""
    digest = hashlib.sha256()
    with io.open(executable, 'rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def root_identity(path):
    info = os.stat(path)
    return '{}:{}'.format(info.st_size, int(info.st_mtime))


def scan_identity(build, fingerprint):
    """The identity a root's journal must carry before it is reused.

    A journal from another build, scan mode, rule set, registry or limit set
    describes work this run did not do.
    """
    material = [
        SCHEMA_ID,
        RULES_ID,
        REGISTRY_ID,
        MODE,
        json.dumps(LIMITS, sort_keys=True),
        build,
        fingerprint,
    ]
    return hashlib.sha256('\n'.join(material).encode('utf-8')).hexdigest()


def load_journal(path, build):
    """Completed roots from an append-only journal, keyed by relative path.

    A record is reused only when it describes the same scan: same schema, rules,
    registry, mode and executable, the same root bytes, and no configured limit
    stopped it. A stopped root is pending work, never a completed one.
    """
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
            if record.get('mode') != MODE:
                continue
            if record.get('limits') != LIMITS:
                continue
            if record.get('build') != build:
                continue
            if record.get('stopped'):
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


# Options the driver sets itself. A `CENSUS_EXTRA` copy would be a second,
# contradictory value on the command line.
OWNED_OPTIONS = (
    '--executable',
    '--recursive',
    '--samples',
    '--max-depth',
    '--max-archives',
    '--max-entries',
    '--max-nested-bytes',
    '--max-spool-bytes',
    '--journal',
    '--journal-identity',
    '--output',
    '--overwrite',
)


def extra_options():
    """`CENSUS_EXTRA`, without any option the driver owns."""
    kept = []
    tokens = os.environ.get('CENSUS_EXTRA', '').split()
    index = 0
    while index < len(tokens):
        token = tokens[index]
        index += 1
        if token in OWNED_OPTIONS or any(
            token.startswith(option + '=') for option in OWNED_OPTIONS
        ):
            if token in OWNED_OPTIONS and index < len(tokens) and tokens[index][:1] != '-':
                index += 1
            continue
        kept.append(token)
    return kept


def command(relative, path, executable, entries, directory, identity):
    """The full argument list for one root, so the flags can be inspected."""
    name = relative.replace('/', '__') + '.jsonl'
    target = os.path.join(directory, name)
    arguments = [
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
        str(LIMITS['max_depth']),
        '--max-archives',
        str(LIMITS['max_archives']),
        '--max-entries',
        str(entries),
        '--max-nested-bytes',
        str(LIMITS['max_nested_bytes']),
        '--max-spool-bytes',
        str(LIMITS['max_spool_bytes']),
        '--journal',
        os.path.join(directory, relative.replace('/', '__') + '.journal.jsonl'),
        '--journal-identity',
        identity,
        '--output',
        target,
        '--overwrite',
    ]
    arguments.extend(extra_options())
    return target, arguments


def census(relative, path, executable, entries, directory, identity):
    """One census run. Returns (summary, error); never a stale summary."""
    target, arguments = command(relative, path, executable, entries, directory, identity)
    if os.path.exists(target):
        os.remove(target)
    token = uuid.uuid4().hex
    try:
        result = subprocess.run(arguments, capture_output=True, text=True)
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
    coverage['archives_resumed'] = sum(
        summary.get('resumed_archives', 0) for summary in summaries
    )
    return {
        'record': 'summary',
        'schema': 'leonida-forge.rpf9-census-merged/2',
        'root': None,
        'roots': len(summaries),
        'archive_roots': [summary['relative'] for summary in summaries],
        'roots_detail': [
            {
                'root': summary['relative'],
                'archives': summary['archives'],
                'entries': summary['entries'],
                'stopped': summary['stopped'],
            }
            for summary in summaries
        ],
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
    done = load_journal(journal_path, identity)
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
                print('{}: reused the completed root'.format(relative), flush=True)
                summaries.append(summary)
                continue
        summary, error = census(
            relative,
            path,
            executable,
            entries,
            runs,
            scan_identity(identity, fingerprint),
        )
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
                'mode': MODE,
                'limits': LIMITS,
                'build': identity,
                'relative': relative,
                'root_identity': fingerprint,
                'archives': summary['archives'],
                'resumed_archives': summary.get('resumed_archives', 0),
                'entries': summary['entries'],
                'stopped': summary['stopped'],
            },
        )
        print(
            '{}: {} archives, {} entries{}{}'.format(
                relative,
                summary['archives'],
                summary['entries'],
                ''
                if not summary.get('resumed_archives')
                else ' ({} resumed)'.format(summary['resumed_archives']),
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
