"""Run an entry census over every root archive and merge the summaries.

`lforge archive census` writes one summary per run. This driver:

- discovers root archives recursively, keeping installation-relative paths so
  archives with the same basename in different folders stay distinct, and passes
  each path to the CLI as the root's name, so every chain carries it;
- deletes the target before each run and requires a successful exit status and a
  summary that says the run completed, so neither a stale result nor a partial
  one is read as a current scan;
- gives every root a journal of its own, so an interrupted root resumes at the
  nested archive where it stopped instead of starting over. A journal is reused
  only for the same schema, rules, registry, scan mode, limits, game executable,
  scanner build and root bytes, and only together with the summary that run
  wrote;
- merges with exact archive occurrence counts, and reports why a run is not
  complete instead of only that it is not.

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
# The schema of the record the CLI writes. A summary under another schema is not
# one this driver knows how to read.
CENSUS_HEADER_SCHEMA = 'leonida-forge.rpf9-census/1'
RULES_ID = 'claims+native-registry'
REGISTRY_ID = 'e95020b2'
# `metadata-only` and `payload` are different investigations over the same
# archives. A checkpoint from one must never satisfy the other.
MODE = 'metadata-only' if '--metadata-only' in os.environ.get('CENSUS_EXTRA', '').split() else 'payload'

# Bytes hashed at each end of a root archive, so a replaced archive is noticed
# without reading 20 GiB again.
FINGERPRINT_BYTES = 1024 * 1024


def option(name, default):
    return int(os.environ.get(name, default))


def limits(entries):
    """Every option that changes what a run traverses, classifies or writes."""
    return {
        'max_depth': option('CENSUS_MAX_DEPTH', 8),
        'max_archives': option('CENSUS_MAX_ARCHIVES', 4096),
        'max_entries': int(entries),
        'max_nested_bytes': option('CENSUS_MAX_NESTED_BYTES', 268435456),
        'max_spool_bytes': option('CENSUS_MAX_SPOOL_BYTES', 4294967296),
    }


def digest_of(path):
    """SHA-256 of a file, by 1 MiB blocks."""
    digest = hashlib.sha256()
    with io.open(path, 'rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def executable_identity(executable):
    """SHA-256 of the game executable, so a rebuilt binary is a different build."""
    return digest_of(executable)


def scanner_identity(census=None):
    """SHA-256 of the census binary that does the work.

    The rules live in that binary, so its bytes — not a version string a caller
    may forget to bump — are what a checkpoint is bound to.
    """
    try:
        return digest_of(census or CENSUS)
    except OSError:
        return 'unknown'


def root_fingerprint(path):
    """Size, modification time in nanoseconds, and the bytes at both ends.

    Whole-second modification times cannot tell two writes apart inside one
    second, and neither field notices an archive replaced by one of the same
    size. Hashing the first and last megabyte catches that, at a cost that does
    not grow with the archive. This is a fingerprint, not a whole-file hash: an
    edit in the middle of an archive that changes neither end is not detected,
    which is one reason a reused summary is also bound to the run that wrote it.
    """
    info = os.stat(path)
    digest = hashlib.sha256()
    digest.update(str(info.st_size).encode('utf-8'))
    digest.update(b'\0')
    digest.update(str(info.st_mtime_ns).encode('utf-8'))
    with io.open(path, 'rb') as handle:
        digest.update(handle.read(FINGERPRINT_BYTES))
        if info.st_size > FINGERPRINT_BYTES * 2:
            handle.seek(-FINGERPRINT_BYTES, os.SEEK_END)
            digest.update(handle.read(FINGERPRINT_BYTES))
    return '{}-{}'.format(info.st_size, digest.hexdigest())


def scan_identity(build, scanner, fingerprint, limits_used):
    """The identity a root's journal must carry before it is reused.

    Everything that can change what a run establishes: the record and merged
    schemas, the rule set, the registry build, the scan mode, every effective
    limit including the entry budget, the game executable, the scanner build and
    the root's own bytes.
    """
    material = [
        SCHEMA_ID,
        CENSUS_HEADER_SCHEMA,
        RULES_ID,
        REGISTRY_ID,
        MODE,
        json.dumps(limits_used, sort_keys=True),
        build,
        scanner,
        fingerprint,
    ]
    return hashlib.sha256('\n'.join(material).encode('utf-8')).hexdigest()


def load_journal(path, build, scanner, limits_used):
    """Completed roots from an append-only journal, keyed by relative path.

    A record is reused only when it describes the same scan: same schemas, rules,
    registry, mode, limits, game executable and scanner, the same root bytes, no
    configured limit stopped it, and a summary file whose digest, size and counts
    still match what it recorded.
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
            if record.get('header_schema') != CENSUS_HEADER_SCHEMA:
                continue
            if record.get('rules') != RULES_ID or record.get('registry') != REGISTRY_ID:
                continue
            if record.get('mode') != MODE:
                continue
            if record.get('limits') != limits_used:
                continue
            if record.get('build') != build or record.get('scanner') != scanner:
                continue
            if record.get('stopped'):
                continue
            if not record.get('complete'):
                continue
            if not summary_matches(record):
                continue
            done[record['relative']] = record
    return done


def summary_matches(record):
    """Whether the summary file the record names is still the one it saw."""
    path = record.get('summary_path')
    if not path or not os.path.exists(path):
        return False
    if os.path.getsize(path) != record.get('summary_bytes'):
        return False
    return digest_of(path) == record.get('summary_sha256')


def append_journal(path, record):
    """Append one completed root, flushed to disk before it is trusted."""
    needs_newline = False
    if os.path.exists(path) and os.path.getsize(path) > 0:
        with io.open(path, 'rb') as existing:
            existing.seek(-1, os.SEEK_END)
            needs_newline = existing.read(1) != b'\n'
    with io.open(path, 'a', encoding='utf-8', newline='\n') as handle:
        # A previous write may have been cut before its newline, so start on a
        # line of its own instead of extending the partial record.
        if needs_newline:
            handle.write('\n')
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


def artifact_name(relative, suffix):
    """A file name that cannot collide for two distinct relative paths.

    Replacing `/` with `__` is not injective: `a/b` and `a__b`, or a folder
    named `a__b`, would share a file. Every character outside a small safe set
    is escaped, and a digest of the exact path is appended so two paths that
    differ only in case stay apart on a case-insensitive file system.
    """
    escaped = []
    for character in relative:
        if character.isascii() and (character.isalnum() or character in '.-'):
            escaped.append(character)
        else:
            escaped.append('%%%02X' % ord(character))
    digest = hashlib.sha256(relative.encode('utf-8')).hexdigest()[:8]
    return '{}-{}{}'.format(''.join(escaped), digest, suffix)


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
    '--root-name',
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
    target = os.path.join(directory, artifact_name(relative, '.jsonl'))
    budget = limits(entries)
    arguments = [
        CENSUS,
        'archive',
        'census',
        path,
        '--root-name',
        relative,
        '--executable',
        executable,
        '--recursive',
        '--samples',
        '3',
        '--max-depth',
        str(budget['max_depth']),
        '--max-archives',
        str(budget['max_archives']),
        '--max-entries',
        str(budget['max_entries']),
        '--max-nested-bytes',
        str(budget['max_nested_bytes']),
        '--max-spool-bytes',
        str(budget['max_spool_bytes']),
        '--journal',
        os.path.join(directory, artifact_name(relative, '.journal.jsonl')),
        '--journal-identity',
        identity,
        '--output',
        target,
        '--overwrite',
    ]
    arguments.extend(extra_options())
    return target, arguments


def census(relative, path, executable, entries, directory, identity):
    """One census run. Returns (summary, error); never a stale or partial one."""
    target, arguments = command(relative, path, executable, entries, directory, identity)
    if os.path.exists(target):
        os.remove(target)
    token = uuid.uuid4().hex
    try:
        result = subprocess.run(arguments, capture_output=True, text=True)
    except OSError as failure:
        return None, 'cannot run {}: {}'.format(CENSUS, failure)
    error = result.stderr.strip().splitlines()[-1] if result.stderr.strip() else ''
    if result.returncode != 0:
        # A run that stopped at a limit, or could not read an archive, writes a
        # summary and fails. Its result is not a completed root.
        return None, error or 'the census exited with {}'.format(result.returncode)
    header, summary = read_output(target)
    if header is None or summary is None:
        return None, error or 'no complete summary record'
    if header.get('schema') != CENSUS_HEADER_SCHEMA:
        return None, 'the summary is under schema {}, not {}'.format(
            header.get('schema'), CENSUS_HEADER_SCHEMA
        )
    if bool(header.get('metadata_only')) != (MODE == 'metadata-only'):
        return None, 'the summary was written in the wrong scan mode'
    if not (summary.get('completion') or {}).get('complete'):
        return None, 'the summary does not report a completed run'
    summary['relative'] = relative
    summary['token'] = token
    summary['summary_path'] = target
    summary['summary_bytes'] = os.path.getsize(target)
    summary['summary_sha256'] = digest_of(target)
    return summary, None


def read_output(path):
    """The header and summary records of a census file, or (None, None)."""
    header = None
    summary = None
    if not os.path.exists(path):
        return header, summary
    try:
        with io.open(path, encoding='utf-8') as handle:
            for line in handle:
                record = json.loads(line)
                if record.get('record') == 'header':
                    header = record
                elif record.get('record') == 'summary':
                    summary = record
    except (OSError, ValueError):
        return None, None
    return header, summary


def key(combination):
    """Every reported property that separates one combination from another.

    A combination that differs in any of these is a different finding and must
    not be merged into another one.
    """
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
        combination.get('extension_provenance'),
        combination.get('outcome'),
    )


def merge(summaries, failures, discovered):
    combinations = {}
    types = {}
    outcomes = {}
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
        for name, value in (summary.get('outcomes') or {}).items():
            outcomes[name] = outcomes.get(name, 0) + value
        for item in summary['types']:
            existing = types.setdefault(
                item['type'], {'type': item['type'], 'entries': 0, 'archives': 0}
            )
            existing['entries'] += item['entries']
            # Roots hold disjoint archives, so their exact per-type archive
            # counts add up without double counting.
            existing['archives'] += item.get('archives', 0)
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
    merged = {
        'record': 'summary',
        'schema': SCHEMA_ID,
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
        'coverage': coverage,
        'types': [
            types[type_id] for type_id in sorted(types, key=lambda value: (value is None, value))
        ],
        'outcomes': dict(sorted(outcomes.items())),
        'combinations': sorted(
            combinations.values(), key=lambda combination: -combination['entries']
        ),
        'failures': failures,
    }
    merged['completion'] = completion(merged, discovered)
    merged['complete'] = merged['completion']['complete']
    return merged


def completion(merged, discovered):
    """Whether the merge is a census of the installation, and why not.

    Enumeration is what this decides. An entry whose payload decoded and matched
    nothing is enumerated and has an outcome; an entry the run never reached is
    not. A stopped scan, an unopened root, an archive that failed to open and
    totals that disagree with each other all leave work undone.
    """
    checks = {
        'roots_discovered': discovered,
        'roots_opened': merged['roots'],
        'roots_failed': len(merged['failures']),
        'roots_stopped': len(merged['stopped']),
        'reconciles': reconciles(merged),
    }
    reasons = []
    if checks['roots_opened'] != discovered:
        reasons.append('roots_not_opened')
    if checks['roots_failed']:
        reasons.append('root_failures')
    if checks['roots_stopped']:
        reasons.append('stopped_scans')
    if merged['coverage'].get('failed_archives'):
        reasons.append('nested_archive_failures')
    if not checks['reconciles']:
        reasons.append('inconsistent_counts')
    return {
        'complete': not reasons,
        'reasons': reasons,
        'checks': checks,
        # No traversal is deferred: a root is walked depth first until it is
        # finished or a limit stops it, and a stopped scan is reported above.
        'pending_traversal': 0,
    }


def reconciles(merged):
    """Whether every published total agrees with every other one."""
    entries = merged['entries']
    by_combination = sum(item['entries'] for item in merged['combinations'])
    by_type = sum(item['entries'] for item in merged['types'])
    by_outcome = sum(merged['outcomes'].values())
    by_root = sum(item['entries'] for item in merged['roots_detail'])
    return entries == by_combination == by_type == by_outcome == by_root


def main():
    if len(sys.argv) not in (4, 5):
        raise SystemExit(__doc__)
    install, executable, directory = sys.argv[1:4]
    entries = int(sys.argv[4]) if len(sys.argv) == 5 else 900
    budget = limits(entries)
    os.makedirs(directory, exist_ok=True)
    runs = os.path.join(directory, 'runs')
    os.makedirs(runs, exist_ok=True)
    journal_path = os.path.join(directory, 'journal.jsonl')
    build = executable_identity(executable)
    scanner = scanner_identity()
    done = load_journal(journal_path, build, scanner, budget)
    roots = discover(install)
    print('{} root archives discovered'.format(len(roots)), flush=True)
    if done:
        print('journal holds {} completed roots'.format(len(done)), flush=True)
    summaries = []
    failures = []
    for relative, path in roots:
        fingerprint = root_fingerprint(path)
        reuse = done.get(relative)
        if reuse is not None and reuse.get('root_fingerprint') == fingerprint:
            # A completed root whose archive, build and summary are unchanged:
            # its persisted summary is reused, not recomputed.
            _, summary = read_output(reuse['summary_path'])
            if summary is not None:
                summary['relative'] = relative
                summary['summary_path'] = reuse['summary_path']
                print('{}: reused the completed root'.format(relative), flush=True)
                summaries.append(summary)
                continue
        summary, error = census(
            relative,
            path,
            executable,
            entries,
            runs,
            scan_identity(build, scanner, fingerprint, budget),
        )
        if summary is None:
            print('{}: FAILED {}'.format(relative, error), flush=True)
            failures.append({'archive': relative, 'error': error})
            continue
        append_journal(
            journal_path,
            {
                'schema': SCHEMA_ID,
                'header_schema': CENSUS_HEADER_SCHEMA,
                'rules': RULES_ID,
                'registry': REGISTRY_ID,
                'mode': MODE,
                'limits': budget,
                'build': build,
                'scanner': scanner,
                'relative': relative,
                'root_fingerprint': fingerprint,
                'summary_path': summary['summary_path'],
                'summary_bytes': summary['summary_bytes'],
                'summary_sha256': summary['summary_sha256'],
                'archives': summary['archives'],
                'resumed_archives': summary.get('resumed_archives', 0),
                'entries': summary['entries'],
                'complete': True,
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
    partial = target + '.part'
    with io.open(partial, 'w', encoding='utf-8', newline='\n') as handle:
        handle.write(
            json.dumps(
                {'record': 'header', 'schema': merged['schema'], 'roots': merged['archive_roots']}
            )
            + '\n'
        )
        handle.write(json.dumps(merged) + '\n')
    os.replace(partial, target)
    print(
        'merged: {} entries in {} archives, complete={} {} -> {}'.format(
            merged['entries'],
            merged['archives'],
            merged['completion']['complete'],
            merged['completion']['reasons'] or '',
            target,
        )
    )
    if not merged['completion']['complete']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
