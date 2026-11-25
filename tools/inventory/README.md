# Recursive inventory sampler

`recursive_inventory.py` builds a deterministic sample of nested RPF9 archives
from authenticated top-level manifests. It extracts type-0 rows, manifests the
nested archives, repeats to a bounded depth, and samples readable payloads per
type. Inputs are opened read-only.

The extracted-byte cap is a single joint budget over unique archive bytes and
unique payload bytes. It is not a per-kind allowance.

## Usage

```sh
python tools/inventory/recursive_inventory.py \
  --inventory-dir <top-level-manifest-directory> \
  --game-dir <game-installation> \
  --scratch-dir <scratch-directory> \
  --lforge <leonida-forge-cli> \
  --executable <game-executable>
```

All paths are required. The scratch directory MUST NOT lie inside the game or
manifest directory. Add `--plan-only` to write `plan.json` for the depth-1
selection without extracting.

## Caps

The defaults are bounded and can be lowered or raised explicitly.

| Flag | Default | Meaning |
| --- | ---: | --- |
| `--max-depth` | 3 | Maximum archive depth, 1 to 3 |
| `--max-nested` | 400 | Unique nested archives |
| `--max-bytes` | 3 GiB | Joint unique archive and payload bytes |
| `--max-rows` | 0 | Nested rows enumerated; 0 means no row cap |
| `--max-archive-bytes` | 16 MiB | Largest sampled type-0 row |
| `--max-payload-bytes` | 1 MiB | Largest sampled payload row |
| `--samples-depth1` | 24 | Type-0 samples per top-level archive |
| `--samples-depth2` | 6 | Type-0 samples per depth-1 archive |
| `--samples-depth3` | 3 | Type-0 samples per depth-2 archive |
| `--max-payloads-per-type` | 4 | Payload samples per type |

`--max-bytes` covers the cache as a whole. An archive and a payload share the
same budget, so the sum of their stored bytes cannot exceed the value. A cached
sample does not consume budget again.

`--max-rows` bounds the rows read from nested manifests. When a manifest crosses
the cap, its rows are truncated in manifest order and traversal stops. The
manifest's reported row count is unchanged; `rows_enumerated` records how many
rows were actually used.

## Selection rule

For each parent, readable type-0 rows at or below the archive size cap are
ordered by `(logical_size, row)`. Quantile-spaced indices are selected,
including the smallest and largest. All candidates are selected when their
count is at or below the per-parent limit. Parents are processed in discovery
order. The rule depends only on the manifests and the caps.

Payloads are selected per type from unique nested manifests. Readable rows at
or below the payload size cap are ordered by `(logical_size, archive hash,
row)` and the first `--max-payloads-per-type` are taken.

## Stop reasons

`summary.json` records one run-level `stop_reason`:

| Reason | Meaning |
| --- | --- |
| `complete` | The sampled population was exhausted |
| `depth` | Type-0 rows exist at `--max-depth` but were not expanded |
| `archive limit` | `--max-nested` unique archives were reached |
| `row limit` | `--max-rows` was reached |
| `byte budget` | The joint `--max-bytes` budget would be exceeded |
| `transform` | Only unreadable transform type-0 rows remained at a depth |
| `failure` | Every archive extraction failed |

Each depth also records its own stop reason. Unreadable payload-transform rows
are not extracted; they remain counted in the manifest state and type histogram.

## Authentication provenance

Nested manifests inherit the CLI signature result of the archive that produced
them. The summary separates:

- `rechecked`: the manifest command ran in this invocation.
- `cached`: the manifest file was reused from the cache.
- `inherited`: a duplicate archive reused the first archive's manifest.
- `failed`: the manifest command or parse failed.

Top-level authentication comes from the input manifests; `top_level_authenticated`
counts headers whose status is `authenticated`.

## Cache and deduplication

Every extracted artifact is stored by SHA-256:

```text
<scratch>/cache/archives/<sha256>.rpf
<scratch>/cache/payloads/<sha256>.bin
<scratch>/cache/manifests/<sha256>.jsonl
<scratch>/cache/index.json
```

A sample key resolves to a hash in `index.json`. A rerun reuses an artifact when
its size matches, so extraction is resumable and duplicate work is avoided.
Duplicate archives are recorded with `duplicate_of` and are not expanded again.
Duplicate payloads are recorded the same way.

## Output

| File | Content |
| --- | --- |
| `summary.json` | stop reason, caps, top-level results, depth progress, unique archives, payloads, authentication provenance, failures, gaps, totals |
| `archives.jsonl` | one record per successful archive extraction, without row lists |
| `payloads.jsonl` | one record per payload extraction attempt, including failures and signature class |
| `failures.jsonl` | extraction and manifest failures |
| `report.md` | aggregate report |
| `run.log` | progress log |
| `plan.json` | depth-1 selection with `--plan-only` |

`archive_extraction_attempts` and `payload_attempts` count every requested
extraction, including cache hits. `archive_extraction_cached` and
`archive_extraction_fresh` split the archive attempts, and
`payload_extraction_cached` and `payload_extraction_fresh` split the payload
attempts. `*_successes` and `*_failures` partition the attempts. A cache hit
runs no extraction command and carries no `exit` value.

`archive_bytes`, `payload_bytes` and `extracted_bytes` describe the cache as a
whole. A resumed run can hold artifacts from earlier samples, so these totals
can exceed the bytes of the current sample. The current sample is the records
in `archives.jsonl` and `payloads.jsonl`.

Only the first eight extracted bytes are read for classification. Exact
prefixes, archive paths and archived rows stay in the scratch directory.

## Signature classes

A class is a byte observation, not a format identity. The classifier reports
the documented magics `9FPR`, `RBF0`, `PSIN`, `SGD5`, `EDUP`, `KB2j`, `KB2n`,
`RDS5` and `PTFX`, the zlib container header, a full zero prefix, or
`unrecognized`.

## Dependencies

- Python 3.11 or later, standard library only.
- A `lforge` build that implements `archive extract` and `archive manifest`.

## Tests

```sh
python -m unittest discover -s tools/inventory
```

The tests use synthetic rows, synthetic cache bytes and temporary directories.
They do not read game files.

## Full type-0 census

`full_census.py` attempts every readable type-0 row in a directory of
top-level manifests, extracts it, records the archive header, and reads its
nested manifest. A run that reaches every declared row supports a population
count; the committed index does not yet carry one.

```sh
python tools/inventory/full_census.py \
  --inventory-dir <top-level-manifest-directory> \
  --output-dir <scratch-directory> \
  --lforge <leonida-forge-cli> \
  --executable <game-executable> \
  --batch-size 50
```

Every row is attempted once. `rows.jsonl` holds one record per attempt,
`manifests/<sha256>.jsonl` the decoded nested manifest, `identity.json` the CLI
version, binary SHA-256, executable SHA-256 and the optional `--app-revision`,
and `state.json` the atomically rewritten progress. A rerun resumes from
`rows.jsonl` and refuses a population whose row keys differ from the saved
state.

Rows larger than the CLI `archive extract` output limit are copied from their
manifest `payload_offset` when the location record is a plain stored range
(mode 0, no chunk table, no payload transform, equal stored and logical size).
Any other over-limit row is recorded as `operational limit`. The copy is
bounds-checked against the parent archive size and written through a temporary
file.

Run `--summarize-only` after a completed or interrupted run to rebuild
`report.json` without touching an archive. Failures are grouped by the stage
that stopped them: `missing input`, `metadata readability`, `unsupported
transformation`, `framing error`, `unsupported storage class`, `corrupt
compressed stream`, `incomplete reconstruction`, `operational limit` or
`unclassified`. A stage is assigned from the CLI message or the observed size,
not guessed from a row type.

## Payload families

`payload_families.py` selects a bounded sample per type from cached manifests,
extracts each payload, and classifies the first 4 KiB:

```sh
python tools/inventory/payload_families.py \
  --manifest-dir <manifest-directory> \
  --archive-dir <archive-directory> \
  --output-dir <scratch-directory> \
  --lforge <leonida-forge-cli> \
  --executable <game-executable> \
  --per-type 8
```

Selection is quantile-spaced by `(logical_size, archive hash, row)` per type,
at or below `--max-payload-bytes`. The classes are `resource-wrapper` (eight
zero bytes, a system pointer at `+0x08`, `0DRP` at `+0x10`), `zero-prefix`,
the documented family magics, `zlib-container-header`, `unrecognized` and
`short`. The classifier reports the `+0x10` tag and follows the `+0x08` pointer
to the page-map counts when the map lies inside the read window. A class is a
byte observation; only `resource-wrapper` has a structural reading, and that
reading is **Probable**.

## Transform population

`transform_census.py` reads the manifests produced by the full census and
groups every unreadable row by stage:

```sh
python tools/inventory/transform_census.py \
  --manifest-dir <census-manifest-directory> \
  --rows <census-rows.jsonl> \
  --output-dir <scratch-directory>
```

Each unreadable row gets a stage and a 16-hex-digit structural fingerprint over
its type, layout, chunk encoding and count, mode, size relation, read source and
cipher descriptor. The output separates `transform_flagged` from the readable
structure population and splits every type, including 89, 11 and 14.


