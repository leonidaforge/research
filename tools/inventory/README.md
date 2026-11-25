# Recursive inventory sampler

`recursive_inventory.py` builds a deterministic sample of nested RPF9 archives
from authenticated top-level manifests and records extraction and manifest
results. It reads archives and the executable read-only and writes only to the
scratch directory.

## Usage

```sh
python tools/inventory/recursive_inventory.py \
  --inventory-dir <top-level-manifest-directory> \
  --game-dir <game-installation> \
  --scratch-dir <scratch-directory> \
  --lforge <leonida-forge-cli> \
  --executable <game-executable>
```

`--game-dir` is used only to reject a scratch directory inside the game installation; the sampler never reads archives from it directly, it reads the manifests you pass. All paths are required. The scratch directory MUST NOT lie inside the game or
manifest directory. Add `--plan-only` to write `plan.json` without extracting.

## Sample rule

For each top-level archive, the sampler takes the smallest, upper-median
(`n // 2`) and largest readable type-0 row with logical size at most 8 MiB.
Rows are ordered by `(logical_size, row)` and duplicate indices are removed.
One level deeper, each extracted archive contributes its smallest and largest
qualifying type-0 row. The default caps are 60 nested archives, 512 MiB of
extracted bytes, 8 MiB per archive, 2 depth-2 archives per parent and 2 payload
samples per type.

A row counts as extracted only when the CLI exits 0 and the output size equals
the row's logical size. Reruns reuse outputs that already have the expected
size.

## Output

All files are written to the scratch directory:

| File | Content |
| --- | --- |
| `summary.json` | selection rule, per-archive results, type histograms, failures, totals |
| `nested.jsonl` | one record per extracted nested archive, including SHA-256 and first 8 bytes |
| `payloads.jsonl` | one record per payload sample, including first 8 bytes |
| `failures.jsonl` | failed extraction records |
| `report.md` | aggregate report |
| `run.log` | progress log |

The first 8 bytes and archive paths are scratch data. They are not publication
material. Payload signature classes are reported as `rpf9-magic`,
`zlib-container-header`, `zero-prefix` or `unrecognized`.

## Dependencies

- Python 3.11 or later, standard library only.
- A `lforge` build that implements `archive extract` and `archive manifest`.

## Tests

```sh
python -m unittest discover -s tools/inventory
```

The tests build synthetic rows and do not read game files.
