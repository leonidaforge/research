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

The `*_attempts` totals count every extraction attempt. `*_successes` and
`*_failures` partition those attempts, so a failed extraction is never hidden
from the attempt count.

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
