# Inventory evidence index

Corrections that supersede a recorded finding are kept in
[research-history.md](research-history.md).

Read-only sample of nested RPF9 archives reached from the authenticated
top-level tables of contents. Archives, extracted payloads, manifests and exact
prefixes stay outside this repository. The sample covers one build and one local
archive set; the counts are observations, not format limits.

All findings below are **Private-evidence supported**: the sampler and its
selection rule are public, but the counts cannot be re-derived without the same
restricted inputs. Metadata authentication and decoding used the native path of
build [scarlett-e95020b2](../../builds/gta-vi/scarlett-e95020b2/README.md)
through `lforge 0.1.0`. RPF9 finding IDs refer to the
[RPF9 evidence index](../rpf9/INDEX.md).

## Evidence types

| Type                       | Meaning                                                                                                                                                            |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Authenticated manifest     | Read-only parse of an RPF9 table of contents whose metadata signature the CLI accepted. Supplies row count, type ID, sizes, layout, chunk encoding and readability |
| Native extraction          | `archive extract` exited 0 and the output size equals the row's logical size                                                                                       |
| Payload prefix             | First 8 bytes of an extracted payload, reduced to a signature class. Exact prefixes remain in scratch                                                              |
| Payload family classification | First 4 KiB of an extracted payload: bytes at `+0x00..+0x10`, `0DRP` tag, and the `+0x08` page-map pointer. Exact bytes remain in scratch |
| Archive header field read  | First `0x40` bytes of an extracted nested archive read as the documented numeric fields                                                                             |
| Hash fingerprint           | SHA-256 of extracted archive or payload bytes. Only uniqueness and duplicate counts are published                                                                  |
| Read-only path enumeration | Recursive listing of `*.rpf` under `<GAME_ROOT>` without opening the files                                                                                         |
| Sample audit               | Deterministic recomputation of a selection from the stored manifests                                                                                               |

## Sample frame

### Comprehensive run

- Input: 22 unique top-level archives from 23 manifest files. One duplicate
  manifest path was ignored. A recursive `*.rpf` enumeration under `<GAME_ROOT>`
  returned the same 22 files: 12 in the root and 10 under `pack/`.
- Authentication: every top-level manifest header reports a verified metadata
  signature. All 782 extracted nested manifests report `authenticated`. Of
  those, 599 manifest commands ran in this invocation and 183 reused a cached
  manifest. The sampler does not re-check signatures.
- Top-level population: 6,534 rows. 17 archives contain 4,351 readable type-0
  rows; 3,970 are at or below 64 MiB and 381 are above it. Five archives contain
  no type-0 row: `appdata0.rpf`, `common.rpf`, `movies.rpf`,
  `story000_bvh4.rpf` and `shaders.rpf`.
- Rule: per parent, order readable type-0 rows at or below 64 MiB by
  `(logical size, row)` and take quantile-spaced indices, including the smallest
  and largest. The limits are 128 rows per top-level archive, 6 per depth-1
  archive and 3 per depth-2 archive. Up to 2,000 unique archives are kept within
  a joint 20 GiB archive-and-payload budget. Payloads are limited to 4 per type
  at or below 1 MiB. The tool is
  [tools/inventory](../../tools/inventory/README.md).
- Result: 782 unique depth-1 archives from 17 top-level archives. Four
  top-level archives contributed 128 samples each (`anim.rpf`, `levels.rpf`,
  `core_bvh4.rpf`, `story000.rpf`); the rest contributed 60 (`audio.rpf`), 46
  (`packs.rpf`), 45 (`shared_minigame000.rpf`), 39 (`data.rpf`), 19
  (`textures.rpf`), 18 (`story000_restofworld.rpf`), 17 (`navmeshes.rpf`), 10
  (`core_restofworld.rpf`), 8 (`shared_minigame000_bvh4.rpf`), 4
  (`story000_script.rpf`), 2 (`script.rpf`), 1 (`core_licenses_data.rpf`) and 1
  (`core_restofworld001.rpf`).
- Caps: no cap was reached. The 782 sampled archives total 7,988,951,648 bytes
  and the payload sample totals 1,415,428 bytes, or 7,990,367,076 bytes across
  this sample. `summary.json` reports the cache as a whole: 8,239,352,896
  archive bytes, 1,415,428 payload bytes and 8,240,768,324 extracted bytes. The
  remaining 250,401,248 archive bytes are cached artifacts outside this sample.
  The run stopped `complete`. Accounting: 22 top-level archives discovered, 804
  parents visited (22 top-level and 782 nested) and 782 nested manifests
  enumerated.
- Depth 2: none of the 782 depth-1 manifests contains a type-0 row at any size,
  so the depth-2 selection has 0 candidates and the maximum depth reached is 1.
- Payload sample: 144 attempts, 137 distinct SHA-256 fingerprints, 7 duplicates.
- Run date: 2026-11-25. All inputs were opened read-only.

### Iteration 8 batch probes

Bounded probes extended the comprehensive frame without changing the top-level
selection. Traversal state and cache stayed outside the repository. All inputs
were opened read-only.

- Over-cap: 12 of the 381 readable type-0 rows above 64 MiB. The sample is the
  8 smallest rows and the 4 largest rows at or below a 512 MiB per-row probe
  cap. The sample totals 2,525,589,904 bytes. 35 candidates exceed the probe
  cap; 334 at or below it were not selected.
- Second disjoint batch: 32 of the 3,188 eligible rows skipped by the per-parent
  limit, 8 per parent from the complement in `anim.rpf`, `core_bvh4.rpf`,
  `levels.rpf` and `story000.rpf`. The sample totals 414,806,336 bytes.
- Combined result: 44 new archives, 2,940,396,240 bytes, 44 distinct SHA-256
  fingerprints and no duplicates. All 44 fresh extractions exited 0 with output
  size equal to the logical size. All begin with `9FPR`, all manifests
  authenticate, and none contains a type-0 row. The 44 manifests hold 24,243
  rows: 24,241 readable and 2 `unsupported_transform`.
- Unreadable sample: 8 of the 823 unreadable rows, one per distinct archive
  (2 type-89 encoding-2, 5 type-11 encoding-3, 1 type-14 encoding-3).
  All 8 extraction attempts exited 1 with the payload-transform message.
- Signature census: 6,079 of the 6,534 top-level rows inspected; 455 rows with
  `payload_transform` skipped. See INV-F31.

### Prior samples

The earlier expanded run sampled 250 unique depth-1 archives and 38,395 rows
with 36 type IDs, using 24 samples per top-level archive, a 16 MiB archive cap
and a 3 GiB byte cap. It found no type-0 row in its 250 depth-1 manifests.
Its findings remain valid for that frame and are listed below as INV-F09 to
INV-F17.

The original bounded run sampled 44 depth-1 archives and 3,553 rows with 25
type IDs, using 3 samples per top-level archive and an 8 MiB archive cap. It
also found no type-0 row in its 44 depth-1 manifests. Its findings remain valid
for that frame and are listed below as INV-F01 to INV-F08.

## Population accounting

Four counts describe the comprehensive run. They are separate populations, not
alternative totals.

Let `C` be the type-0 rows in the 22 top-level manifests that satisfy
`kind == "row"`, `type_id == 0`, `contents.readable == true` and an integer
`logical_size`. No type-0 row in this frame is unreadable, so `C` also equals
the `type0_rows` gap total.

- `4,351` = `|C|`, over every logical size.
- `3,970` = rows in `C` with `logical_size <= 67,108,864` (64 MiB), the
  `readable_within_cap` gap. These rows are eligible for the per-parent rule.
- `381` = rows in `C` with `logical_size > 67,108,864`, the
  `over_archive_size_cap` gap. They were never eligible.
- `782` = rows selected from the 3,970 eligible rows under
  `samples_depth1 = 128` and extracted. `782` is also the archive extraction
  attempt and success count: 599 fresh extractions exited 0 and 183 reused a
  cached artifact. The 2,000-archive and joint 20 GiB caps did not bind.
- `3,188` = eligible rows not selected, `3,970 - 782`. These rows are a subset
  of `C` and disjoint from the 782.

The identities are `4,351 = 3,970 + 381` and
`3,970 = 782 + 3,188`, hence `4,351 = 782 + 3,188 + 381`. The 782 rows cover
18.0% of `C` and 19.7% of the eligible rows.

## Top-level coverage

Type-0 counts are readable rows. `Within 64 MiB` rows were eligible for the
per-parent rule; `Not selected` rows were skipped by the 128-sample limit. The
`Over 64 MiB` column is the archive size-cap gap. The five archives with zero
type-0 rows were skipped because they contain no archive container row.

| Archive                       |  Rows | Type-0 | Within 64 MiB | Over 64 MiB | Selected | Extracted | Not selected |
| ----------------------------- | ----: | -----: | ------------: | ----------: | -------: | --------: | -----------: |
| `anim.rpf`                    |   265 |    235 |           215 |          20 |      128 |       128 |           87 |
| `appdata0.rpf`                |     2 |      0 |             0 |           0 |        0 |         0 |            0 |
| `audio.rpf`                   |   103 |    103 |            60 |          43 |       60 |        60 |            0 |
| `common.rpf`                  |   418 |      0 |             0 |           0 |        0 |         0 |            0 |
| `data.rpf`                    |   699 |     41 |            39 |           2 |       39 |        39 |            0 |
| `levels.rpf`                  | 2,078 |  2,050 |         1,811 |         239 |      128 |       128 |        1,683 |
| `movies.rpf`                  |   515 |      0 |             0 |           0 |        0 |         0 |            0 |
| `navmeshes.rpf`               |    29 |     28 |            17 |          11 |       17 |        17 |            0 |
| `core_bvh4.rpf`               | 1,286 |  1,281 |         1,257 |          24 |      128 |       128 |        1,129 |
| `core_licenses_data.rpf`      |     4 |      1 |             1 |           0 |        1 |         1 |            0 |
| `core_restofworld001.rpf`     |     6 |      1 |             1 |           0 |        1 |         1 |            0 |
| `core_restofworld.rpf`        |    39 |     10 |            10 |           0 |       10 |        10 |            0 |
| `shared_minigame000.rpf`      |    68 |     49 |            45 |           4 |       45 |        45 |            0 |
| `shared_minigame000_bvh4.rpf` |    13 |      8 |             8 |           0 |        8 |         8 |            0 |
| `story000.rpf`                |   763 |    441 |           417 |          24 |      128 |       128 |          289 |
| `story000_script.rpf`         |     4 |      4 |             4 |           0 |        4 |         4 |            0 |
| `story000_bvh4.rpf`           |     4 |      0 |             0 |           0 |        0 |         0 |            0 |
| `story000_restofworld.rpf`    |    39 |     18 |            18 |           0 |       18 |        18 |            0 |
| `packs.rpf`                   |   172 |     59 |            46 |          13 |       46 |        46 |            0 |
| `script.rpf`                  |     2 |      2 |             2 |           0 |        2 |         2 |            0 |
| `shaders.rpf`                 |     3 |      0 |             0 |           0 |        0 |         0 |            0 |
| `textures.rpf`                |    22 |     20 |            19 |           1 |       19 |        19 |            0 |

## Findings

### Comprehensive run

| ID      | Claim                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | Evidence                                                               | Confidence                                                 | Limits                                                                                                                                                                                                                      |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- | ---------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| INV-F18 | The comprehensive rule selected 782 readable type-0 rows from 17 of 22 top-level archives. All 782 archive artifacts have output size equal to the logical size. Fresh extractions exited 0; cached hits ran no extraction command and carry no exit code. Their SHA-256 fingerprints are distinct, so no duplicate nested archive content was found. The 782 sampled archives total 7,988,951,648 bytes; the smallest is 720 bytes and the largest 66,870,368 bytes. 256 are larger than 8 MiB, 161 larger than 16 MiB and 87 larger than 32 MiB.            | Sample audit, native extraction, hash fingerprint                      | Confirmed (sample)                                         | Readable type-0 rows at or below 64 MiB only. 381 larger type-0 rows were not extracted. 3,188 eligible rows were not selected. Five top-level archives have no type-0 row. The total number of nested archives is unknown. |
| INV-F19 | The 782 nested manifests hold 169,523 rows, 168,700 readable and 823 unreadable, with 40 distinct type IDs. Five type IDs dominate: 100 (27,482 rows), 111 (21,922), 15 (21,742), 67 (15,879) and 11 (13,487). Compared with the 250-archive expanded sample (36 type IDs; histogram below), four type IDs are new: 64, 86, 105 and 109; no type ID from that sample is absent. Every row reports read source `main`.                                                                                                                                         | Authenticated manifest                                                 | Confirmed (sample)                                         | One build and sample. Type IDs are row labels; this index assigns no payload format to them. Names remain unresolved hashes.                                                                                                |
| INV-F20 | Layout and chunk encoding correlate in the comprehensive sample. All 157,593 layout-R rows use chunk encoding 2. Layout F covers 11,930 rows: 11,006 use encoding 3 and 924 have no chunk table. Compression mode 0 covers 169,367 rows and mode 1 covers 156. No row uses encoding 4. All 924 unchunked rows are readable, including all 156 mode-1 rows.                                                                                                                                                                                                    | Authenticated manifest                                                 | Confirmed (sample correlation)                             | A sample correlation, not a format rule. No encoding-4 row was available to test.                                                                                                                                           |
| INV-F21 | The 823 unreadable rows are all `unsupported_transform`: 746 type-89 encoding-2 rows, 76 type-11 encoding-3 rows and one type-14 encoding-3 row. They were excluded from payload sampling, so no extraction was attempted for them.                                                                                                                                                                                                                                                                                                                           | Authenticated manifest                                                 | Confirmed (sample)                                         | Row states only. The payload transform remains unsupported (RPF9-F113, RPF9-F116, RPF9-F117).                                                                                                                               |
| INV-F22 | No type-0 row occurs at any size in the 782 sampled depth-1 manifests. The depth-2 selection therefore has 0 candidates and the recursive sample stops at depth 1. This extends the 250-archive and 44-archive observations to a larger sample.                                                                                                                                                                                                                                                                                                               | Authenticated manifest, sample audit                                   | Confirmed (sample); Unknown (general)                      | 782 of 3,970 eligible type-0 rows were sampled. 3,188 eligible rows and 381 rows above 64 MiB were not extracted. Larger or unselected top-level type-0 rows may contain archives.                                          |
| INV-F23 | All 144 payload attempts succeeded with exact logical size; none failed. Fresh extractions exited 0; cached hits ran no extraction command and carry no exit code. They produced 137 distinct SHA-256 fingerprints; 7 attempts repeated content already seen (`type 5`: 3, `type 79`: 1, `type 255`: 3). The attempts contain 116 encoding-2 rows, 27 encoding-3 rows and 1 row without a chunk table. 36 of 40 type IDs were sampled. Types 14 and 89 are unreadable, and the single type-96 and type-109 rows exceed the 1 MiB payload cap.                 | Native extraction, hash fingerprint, authenticated manifest            | Confirmed (sample)                                         | At most four payloads per type, all at or below 1 MiB. Most readable rows were not extracted.                                                                                                                               |
| INV-F24 | The 137 unique payloads fall into four prefix classes: 112 zero-prefix, 8 `PSIN`, 4 `RBF0` and 13 unrecognized. `RBF0` occurs only in type 11, across chunk encoding 3 and no chunk table, in two archives. `PSIN` occurs only in types 93 and 94, chunk encoding 3, across eight payloads from one archive. The 13 unrecognized samples are types 64, 66, 105 and 255 with chunk encoding 3, from six archives. The zero-prefix class spans 29 type IDs from 49 archives. No sample begins with `9FPR`, a zlib container header or another documented magic. | Payload prefix                                                         | Confirmed (classes and counts); Unknown (format identity)  | First 8 bytes only. Exact prefixes stay in scratch. Each non-zero class comes from one or a few archives and a small number of rows.                                                                                        |
| INV-F25 | Type ID does not determine the sampled prefix class. The zero-prefix class spans 29 type IDs; `RBF0` covers type 11; `PSIN` covers types 93 and 94; unrecognized covers types 64, 66, 105 and 255.                                                                                                                                                                                                                                                                                                                                                            | Payload prefix                                                         | Confirmed (sample independence); Unknown (format identity) | 36 of 40 type IDs were sampled. An 8-byte prefix is weak evidence of format.                                                                                                                                                |
| INV-F26 | Content-hash deduplication found no duplicate archive among the 782 extractions and seven duplicate payloads among 144 attempts. Sampling by name or row index alone would have counted those seven payload extractions twice.                                                                                                                                                                                                                                                                                                                                | Hash fingerprint                                                       | Confirmed (sample)                                         | The archive duplicate count covers the 782 sampled archives, not the whole game.                                                                                                                                            |
| INV-F27 | The comprehensive counts are disjoint populations: 4,351 readable type-0 rows over all sizes; 3,970 of them with `logical_size <= 67,108,864`; 381 with `logical_size > 67,108,864`; and 782 selected from the 3,970 by the per-parent quantile rule with `samples_depth1 = 128` and extracted. The other 3,188 eligible rows were not selected. `4,351 = 782 + 3,188 + 381`; the joint 20 GiB and 2,000-archive caps did not bind.                                                                                                                           | Sample audit (`selection_gaps`, `select_quantiles`), native extraction | Confirmed (sample)                                         | One build and one 22-archive top-level set. The predicates cover readable type-0 rows only. The 782 are a bounded sample, not archive coverage.                                                                             |

### Iteration 8 batch probes

| ID      | Claim                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | Evidence                                                                             | Confidence                                                            | Limits                                                                                                                          |
| ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ | --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| INV-F28 | The raised-cap batch extracted 12 of the 381 readable type-0 rows above 64 MiB: the 8 smallest (67,238,752 to 68,446,368 bytes) and the 4 largest at or below the 512 MiB probe cap (478,848,640 to 514,812,688 bytes). All 12 fresh extractions exited 0 with exact logical size, begin with `9FPR`, authenticate and contain no type-0 row. The 35 rows above the probe cap (largest 14,159,487,680 bytes) and 334 other candidates at or below it were not extracted.                                                                                                                                                                                                               | Native extraction, authenticated manifest                                            | Confirmed (sample)                                                    | 12 of 381 over-cap rows. The 512 MiB probe cap is a sampling limit, not an archive limit.                                       |
| INV-F29 | The second disjoint batch selected 32 of the 3,188 eligible type-0 rows skipped by the per-parent 128-row limit: 8 quantile-spaced rows per parent from the complement in `anim.rpf` (87), `core_bvh4.rpf` (1,129), `levels.rpf` (1,683) and `story000.rpf` (289). All 32 fresh extractions exited 0 with exact logical size, begin with `9FPR`, authenticate and contain no type-0 row. 3,156 eligible rows remain unselected; the other 13 contributing parents had no complement because all their eligible rows were in the first batch.                                                                                                                                           | Native extraction, authenticated manifest                                            | Confirmed (sample)                                                    | 32 of 3,188 eligible rows. One second batch, not coverage of the remaining population.                                          |
| INV-F30 | The 823 unreadable rows in the 782 depth-1 manifests are 746 type-89 encoding-2, 76 type-11 encoding-3 and 1 type-14 encoding-3 row, all `unsupported_transform`. An 8-row sample covering all 8 distinct archives attempted extraction; all 8 exited 1 with `entry 0 is stored behind the payload transform, so its stored bytes are not its contents`. No sampled failure was a rejected signature or a decode error. 815 rows were not sampled.                                                                                                                                                                                                                                     | Authenticated manifest, native extraction                                            | Confirmed (sample)                                                    | Row states plus 8 extraction attempts. The transform implementation remains unsupported.                                        |
| INV-F31 | The stored-byte census inspected 6,079 of the 6,534 top-level rows and skipped 455 with `payload_transform`. It counts `9FPR` 4,351, zlib 924, `KB2n` 787, `KB2j` 10, `EDUP` 3, `SGD5` 2, `PTFX` 1 and a full-zero prefix 1. Classes with no assigned format are `PTFX` (1, `common.rpf` row 151), zlib (924) and zero-prefix (1, `data.rpf` row 476); `9FPR` is the documented RPF9 container. The `formats/unknown` table lists `PTFX` and not the other three. `KB2n` occurs in four archives: `movies.rpf` 505, `story000.rpf` 264, `core_restofworld.rpf` 11 and `story000_restofworld.rpf` 7. This contradicts the confinement claim in UPL-F06. It does not contradict KB2-F12, whose 787 is a different, `movies.rpf`-only population over an unpreserved 797-row manifest; INV-F32 reconciles the two figures. | Archive data, authenticated manifest                                                 | Confirmed (census); Unknown (format identity)                         | First eight stored bytes only. No format is assigned to `PTFX`, zlib or the zero prefix. The KB2 subject is not rewritten here. |
| INV-F32 | The `KB2n` contradiction in INV-F31 has two parts, and only one is a contradiction. (1) The confinement claim in UPL-F06 is contradicted: the `KB2n` stored prefix occurs in four top-level archives, not only `movies.rpf`. (2) KB2-F12 is not contradicted: its 787 is a `movies.rpf`-only count over a 797-row population that is not preserved, whereas the 787 of INV-F31 is a four-archive sum whose `movies.rpf` term is 505 and whose other three terms total 282. The equality of the two totals has no established cause and is an observation, not an explanation. The KB2 subject now records the four-archive population as KB2-F13 and keeps the historical figure as KB2-F12.                                                          | Reanalysis of INV-F31 against KB2-F01, KB2-F12 and UPL-F06; `BINARY`, `CROSS_SAMPLE` | Confirmed (arithmetic); the historical 797-row manifest stays Unknown | Neither figure may be substituted for the other, and neither generalises from `movies.rpf` to the whole archive set             |

### Iteration 11 payload family sample

The sample uses the 849 manifests in the iteration-8 expansion cache, not a
full archive census. The 849 are the 782 comprehensive-sample manifests plus 67
additional manifests cached by the earlier 250-archive run (183 of those 250
are already in the 782, so 183 + 67 = 250). Candidates are readable rows at or
below 1 MiB: 177,225 rows over 36 type IDs. The rule takes up to 8
quantile-spaced rows per type, ordered by `(logical_size, archive SHA-256,
row)`, and extracted 282 payloads. Every extraction exited 0. The classifier
reads the first 4 KiB and records the bytes at `+0x10`; it follows the system
pointer at `+0x08` when the page map lies inside the window. The sample and its
exact payload prefixes stay in scratch.

| ID      | Claim                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | Evidence                                                                 | Confidence                                                                                      | Limits                                                                                                                                                                                                                       |
| ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| INV-F33 | All 282 sampled payloads have a family class and a confidence. The classes are resource-wrapper 52, zero-prefix 178, `PSIN` 19, `RBF0` 1, unrecognized 31 and short 1. These are counts in a capped sample of 282 from 177,225 candidates, not an estimate of the candidate proportions. All 52 wrappers carry `0DRP` at `+0x10` followed by `z` (`0DRPz`) and the system pointer at `+0x08` agrees. They occur in type 11 (4), 73 (8), 74 (8), 87 (8), 108 (8), 111 (8) and 115 (8). Type 115 was not in the encoding-2 framing sample's `0DRPz` type list; the other six types were. Type 11 alone carries three classes in this sample (wrapper 4, `PSIN` 3, `RBF0` 1), so the type ID does not determine the class. No sampled payload begins with `9FPR` or a zlib container header. Every class is a byte observation; the resource-wrapper reading is Probable because the tag and a system pointer agree.                                                                                                                                                                                                 | `BINARY`, `CROSS_SAMPLE` (payload bytes; per-type counts)              | Confirmed (bytes and counts); Probable (wrapper reading); Unknown (format identity)              | 282 of 177,225 candidates, 8 per type, at or below 1 MiB, one build. The 52 `0DRPz` count is a sample count, not a population claim. Types 64, 66, 105 and 255 stay unrecognized. The sample does not test larger payloads. |
| INV-F34 | The system pointer at `+0x08` reaches the page map inside the 4 KiB window for 110 of the 282 samples. Those maps declare 1 system and 0 graphics pages for 56, 1/1 for 51 and 1/2 for 3. A page map outside the window is not evidence that the resource has no map.                                                                                                                                                                                                                                                                                                                                                                                                       | `BINARY` (payload bytes and page-map bytes)                                             | Confirmed (sample counts); the map reading is Probable                                          | 110 of 282. The other 172 were not followed because the map lies beyond the window or the family has no system pointer.                                                                                                      |
| INV-F35 | A zero prefix and a resource wrapper are separate classes. Of the 178 zero-prefix samples, 75 have four zero bytes at `+0x10`; the rest carry other values there. No zero-prefix sample carries `0DRP`. The classifier therefore does not infer a resource header from the zero prefix alone.                                                                                                                                                                                                                                                                                                                                                                                   | `BINARY` (payload bytes at `+0x00..+0x10`)                                           | Confirmed (bytes); Unknown (meaning of a nonzero `+0x10` value)                                 | 178 of 282. Reading only the first 4 KiB; a tag beyond that offset was not tested.                                                                                                                                          |

### Iteration 11 transform stage sample

The same 849 manifests hold 183,144 rows. `transform_census.py` assigns a stage
and a structural fingerprint to every unreadable row. This is a bounded sample,
not the full 4,351-row census; the full transform count remains unmeasured. The
fingerprint is the first 16 hex digits of SHA-256 over
`(type, layout, chunk encoding label and count, mode, payload_transform,
logical_size == stored_size, read source, cipher algorithm, cipher type,
cipher supported)`, as implemented in `transform_census.row_fingerprint`.

Overlap with the encoding-2 framing survey (48,087 rows from 1,268 nested
archives plus one top-level row) is not established. That survey selected
complete parent sets and type-0 rows up to 1 MiB; this sample was selected per
type from cached manifests. The branch does not retain the framing survey's
archive list, so neither disjointness nor a measured overlap is claimed.

| ID      | Claim                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | Evidence                                                                 | Confidence                                                                                      | Limits                                                                                                                                                                                                                       |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| INV-F36 | Of the 183,144 rows in the 849-manifest sample, 182,321 are readable structure rows and 823 are unreadable. All 823 are `unsupported_transform`: type 89 = 746 (encoding 2), type 11 = 76 (encoding 3) and type 14 = 1 (encoding 3). Every one carries cipher algorithm `0x11`, type 17, `supported: false`. Their structural fingerprints reduce to 15 distinct values (type 89: 2, type 11: 12, type 14: 1). No unreadable row failed at metadata, framing, storage, compression or limit in this sample. | `BINARY`, `CROSS_SAMPLE` (manifest states, cipher descriptor, fingerprint counts)        | Confirmed (sample counts and row states); the transform implementation stays unsupported        | 849 manifests, not the 4,351-row declared population. The full transform count is not established. Payload bytes behind algorithm `0x11` were not decoded.                                                                    |
| INV-F37 | The recorded locator set in [locators.md](../../tools/inventory/locators.md) identifies four `levels.rpf` type-0 parent archives (316, 638, 720 and 592 rows; SHA-256 per archive), 20 `textures.rpf` type-0 parent archives holding 1,365 type-5 rows (SHA-256, stored size and row count per archive), eight selected type-2 inner rows (stored, system, graphics, LOD slots, geometries, shaders and stored-row SHA-256), seven selected type-5 inner rows (stored, system, graphics, pages, record count, identifier runs, graphics pointers and stored-row SHA-256) and the texture-slot key statistics. Every entry names the extraction and manifest commands. | `BINARY`, `CROSS_SAMPLE` (recorded bytes and digests) | Confirmed (recorded locators); type-5 field meanings and any format identity remain Unknown | One build and archive set. The file is a recorded set, not a generator. The key join and graphics zlib negatives are bounded to the stated samples. |

### Prior expanded sample (250 archives)

| ID      | Claim                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | Evidence                                                    | Confidence                                                 | Limits                                                                                                                                                                                 |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- | ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| INV-F09 | The expanded rule selected 250 readable type-0 rows from 17 of 22 top-level archives. All 250 native extractions exited 0 with output size equal to the logical size. Their SHA-256 fingerprints are distinct, so no duplicate nested archive content was found. The archives total 843,608,368 bytes; the smallest is 720 bytes and the largest 16,714,192 bytes. 42 are larger than 8 MiB.                                                                                          | Sample audit, native extraction, hash fingerprint           | Confirmed (sample)                                         | Readable type-0 rows at or below 16 MiB only. 1,274 larger type-0 rows were not extracted. Five top-level archives have no type-0 row. The total number of nested archives is unknown. |
| INV-F10 | The 250 nested manifests hold 38,395 rows, 38,378 readable and 17 unreadable, with 36 distinct type IDs. Three type IDs dominate: 11 (11,040 rows), 111 (10,181) and 100 (4,896). Compared with the prior 25-type sample, 12 type IDs are new: 6, 17, 93, 94, 95, 99, 100, 101, 102, 108, 110 and 114. Type 109 was present in the prior sample but absent here. Every row reports read source `main`.                                                                                | Authenticated manifest                                      | Confirmed (sample)                                         | One build and sample. Type IDs are row labels; this index assigns no payload format to them. Names remain unresolved hashes.                                                           |
| INV-F11 | Layout and chunk encoding correlate in the expanded sample. All 35,548 layout-R rows use chunk encoding 2. Layout F covers 2,847 rows: 2,536 use encoding 3 and 311 have no chunk table. Compression mode 0 covers 38,239 rows and mode 1 covers 156. No row uses encoding 4. All 311 unchunked rows are readable, including all 156 mode-1 rows.                                                                                                                                     | Authenticated manifest                                      | Confirmed (sample correlation)                             | A sample correlation, not a format rule. No encoding-4 row was available to test.                                                                                                      |
| INV-F12 | The 17 unreadable rows are all `unsupported_transform`: 15 type-11 encoding-3 rows, one type-14 encoding-3 row and one type-89 encoding-2 row. They were excluded from payload sampling, so no extraction was attempted for them.                                                                                                                                                                                                                                                     | Authenticated manifest                                      | Confirmed (sample)                                         | Row states only. The payload transform remains unsupported (RPF9-F113, RPF9-F116, RPF9-F117).                                                                                          |
| INV-F13 | No type-0 row occurs at any size in the 250 sampled depth-1 manifests. The depth-2 selection therefore has 0 candidates and the recursive sample stops at depth 1. This extends the prior 44-archive observation to a larger sample.                                                                                                                                                                                                                                                  | Authenticated manifest, sample audit                        | Confirmed (sample); Unknown (general)                      | 250 of 3,077 eligible type-0 rows were sampled. 2,827 eligible rows and 1,274 rows above 16 MiB were not extracted. Larger or unselected top-level type-0 rows may contain archives.   |
| INV-F14 | All 130 payload attempts exited 0 with exact logical size; none failed. They produced 122 distinct SHA-256 fingerprints; 8 attempts repeated content already seen (`type 5`: 3, `type 255`: 3, `type 11`: 1, `type 79`: 1). The sample contains 110 encoding-2 rows, 16 encoding-3 rows and 4 unchunked mode-1 rows. 33 of 36 type IDs were sampled. Types 14 and 89 are unreadable, and the single type-96 row exceeds the 1 MiB payload cap.                                        | Native extraction, hash fingerprint, authenticated manifest | Confirmed (sample)                                         | At most four payloads per type, all at or below 1 MiB. Most readable rows were not extracted.                                                                                          |
| INV-F15 | The 122 unique payloads fall into four prefix classes: 106 zero-prefix, 8 `PSIN`, 3 `RBF0` and 5 unrecognized. `RBF0` occurs only in type 11, mode 1 without a chunk table, across three payloads from one archive. `PSIN` occurs only in types 93 and 94, chunk encoding 3, across eight payloads from one archive. The five unrecognized samples are type 66 and type 255 with chunk encoding 3. No sample begins with `9FPR`, a zlib container header or another documented magic. | Payload prefix                                              | Confirmed (classes and counts); Unknown (format identity)  | First 8 bytes only. Exact prefixes stay in scratch. Each non-zero class comes from one archive and a small number of rows.                                                             |
| INV-F16 | Type ID does not determine the sampled prefix class. The zero-prefix class spans 28 type IDs; `RBF0` covers type 11; `PSIN` covers types 93 and 94; unrecognized covers types 66 and 255. Type 255 carried several distinct signatures in the prior sample and one unrecognized class here.                                                                                                                                                                                           | Payload prefix                                              | Confirmed (sample independence); Unknown (format identity) | 33 of 36 type IDs were sampled. An 8-byte prefix is weak evidence of format.                                                                                                           |
| INV-F17 | Content-hash deduplication found no duplicate archive among the 250 extractions and eight duplicate payloads among 130 attempts. Sampling by name or row index alone would have counted those eight payload extractions twice.                                                                                                                                                                                                                                                        | Hash fingerprint                                            | Confirmed (sample)                                         | The archive duplicate count covers the 250 sampled archives, not the whole game.                                                                                                       |

### Original bounded sample (44 archives, INV-F01 to INV-F08)

| ID      | Claim                                                                                                                                          |
| ------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| INV-F01 | 44 readable type-0 rows from 17 of 22 top-level archives; all 44 extractions exact; 100,904,448 archive bytes; 39 payloads of 1,044,822 bytes. |
| INV-F02 | All 44 nested files begin with `9FPR` and authenticate under the same build; 44 distinct SHA-256 fingerprints.                                 |
| INV-F03 | The 44 manifests hold 3,553 rows and 25 type IDs; 3,535 readable and 18 unreadable.                                                            |
| INV-F04 | Layout R uses encoding 2 and layout F uses encoding 3 or no chunk table in that sample; no encoding 4.                                         |
| INV-F05 | All 44 archive and 39 payload extractions succeeded; 18 unreadable rows were not attempted.                                                    |
| INV-F06 | The 39 payloads split into 34 zero-prefix and 5 non-zero prefixes; no archive or zlib header prefix.                                           |
| INV-F07 | Type ID does not determine the sampled prefix class; 18 type IDs share the zero-prefix class.                                                  |
| INV-F08 | No depth-1 archive contains a type-0 row, so the 44-archive sample stops at depth 1; larger and unselected archives were not examined.         |

## Type histogram

Counts are rows in the 782 unique nested manifests. "Encoding" is the
chunk-table encoding; `none` means no chunk table.

| Type ID |   Rows | Readable | Unreadable | Encoding                      |
| ------: | -----: | -------: | ---------: | ----------------------------- |
|       2 |  6,613 |    6,613 |          0 | 2                             |
|       3 |  5,107 |    5,107 |          0 | 2                             |
|       4 |  7,522 |    7,522 |          0 | 2                             |
|       5 |  1,557 |    1,557 |          0 | 2                             |
|       6 |  3,891 |    3,891 |          0 | 2                             |
|      11 | 13,487 |   13,411 |         76 | 2: 4,507; 3: 8,824; none: 156 |
|      14 |      1 |        0 |          1 | 3                             |
|      15 | 21,742 |   21,742 |          0 | 2                             |
|      16 |  1,604 |    1,604 |          0 | 2                             |
|      17 |  1,781 |    1,781 |          0 | 2                             |
|      64 |    324 |      324 |          0 | 3                             |
|      66 |     49 |       49 |          0 | 3                             |
|      67 | 15,879 |   15,879 |          0 | 2                             |
|      70 |  5,142 |    5,142 |          0 | 2                             |
|      72 |    226 |      226 |          0 | 2                             |
|      73 |  6,653 |    6,653 |          0 | 2                             |
|      74 |    594 |      594 |          0 | 2                             |
|      78 |  7,638 |    7,638 |          0 | 2                             |
|      79 |  7,506 |    7,506 |          0 | 2                             |
|      86 |     11 |       11 |          0 | 2                             |
|      87 |  7,138 |    7,138 |          0 | 2                             |
|      88 |    176 |      176 |          0 | 2                             |
|      89 |    746 |        0 |        746 | 2                             |
|      93 |    211 |      211 |          0 | 3                             |
|      94 |     80 |       80 |          0 | 3                             |
|      95 |     97 |       97 |          0 | 2                             |
|      96 |      1 |        1 |          0 | 3                             |
|      99 |     98 |       98 |          0 | 2                             |
|     100 | 27,482 |   27,482 |          0 | 2                             |
|     101 |      5 |        5 |          0 | 2                             |
|     102 |     94 |       94 |          0 | 2                             |
|     103 |  1,511 |    1,511 |          0 | 2                             |
|     105 |  1,476 |    1,476 |          0 | 3                             |
|     108 |    110 |      110 |          0 | 2                             |
|     109 |      1 |        1 |          0 | 2                             |
|     110 |      5 |        5 |          0 | 2                             |
|     111 | 21,922 |   21,922 |          0 | 2                             |
|     114 |     97 |       97 |          0 | 2                             |
|     115 |    138 |      138 |          0 | 2                             |
|     255 |    808 |      808 |          0 | 3: 40; none: 768              |

### Prior expanded sample

Counts are rows in the 250 unique nested manifests of the prior expanded run.

| Type ID |   Rows | Readable | Unreadable | Encoding                      |
| ------: | -----: | -------: | ---------: | ----------------------------- |
|       2 |    996 |      996 |          0 | 2                             |
|       3 |    446 |      446 |          0 | 2                             |
|       4 |    687 |      687 |          0 | 2                             |
|       5 |    191 |      191 |          0 | 2                             |
|       6 |    275 |      275 |          0 | 2                             |
|      11 | 11,040 |   11,025 |         15 | 2: 8,673, 3: 2,211, none: 156 |
|      14 |      1 |        0 |          1 | 3                             |
|      15 |  2,719 |    2,719 |          0 | 2                             |
|      16 |    120 |      120 |          0 | 2                             |
|      17 |    293 |      293 |          0 | 2                             |
|      66 |     12 |       12 |          0 | 3                             |
|      67 |    803 |      803 |          0 | 2                             |
|      70 |  1,249 |    1,249 |          0 | 2                             |
|      72 |    149 |      149 |          0 | 2                             |
|      73 |  1,044 |    1,044 |          0 | 2                             |
|      74 |    106 |      106 |          0 | 2                             |
|      78 |  1,037 |    1,037 |          0 | 2                             |
|      79 |    162 |      162 |          0 | 2                             |
|      87 |    580 |      580 |          0 | 2                             |
|      88 |    140 |      140 |          0 | 2                             |
|      89 |      1 |        0 |          1 | 2                             |
|      93 |    211 |      211 |          0 | 3                             |
|      94 |     80 |       80 |          0 | 3                             |
|      95 |     97 |       97 |          0 | 2                             |
|      96 |      1 |        1 |          0 | 3                             |
|      99 |     98 |       98 |          0 | 2                             |
|     100 |  4,896 |    4,896 |          0 | 2                             |
|     101 |      5 |        5 |          0 | 2                             |
|     102 |     93 |       93 |          0 | 2                             |
|     103 |    266 |      266 |          0 | 2                             |
|     108 |      3 |        3 |          0 | 2                             |
|     110 |      3 |        3 |          0 | 2                             |
|     111 | 10,181 |   10,181 |          0 | 2                             |
|     114 |     97 |       97 |          0 | 2                             |
|     115 |    138 |      138 |          0 | 2                             |
|     255 |    175 |      175 |          0 | 3: 20, none: 155              |

Type 0 does not appear in either nested sample; it labels the top-level rows
used as archive containers.

## Extraction outcomes

| Measure                         |        Result |
| ------------------------------- | ------------: |
| Nested archive attempts         |           782 |
| Nested archive successes        |           782 |
| Nested archive failures         |             0 |
| Duplicate nested archives       |             0 |
| Sampled archive bytes           | 7,988,951,648 |
| Payload attempts                |           144 |
| Payload successes               |           144 |
| Payload failures                |             0 |
| Unique payload fingerprints     |           137 |
| Duplicate payloads              |             7 |
| Payload bytes                   |     1,415,428 |
| Sampled bytes total             | 7,990,367,076 |
| Cache archive bytes             | 8,239,352,896 |
| Cache payload bytes             |     1,415,428 |
| Cache extracted bytes           | 8,240,768,324 |
| Cache bytes outside this sample |   250,401,248 |
| Extraction failures             |             0 |

The attempts include cache hits. `summary.json` counts cached and fresh archive
and payload extractions separately; a cache hit runs no extraction command and
carries no `exit` value. The cache totals cover every artifact in the scratch
cache, including 250,401,248 archive bytes from earlier samples.

## Payload signature classes

| Class                 | Unique payloads | Type IDs                                                                                                               | Encoding | Archives |
| --------------------- | --------------: | ---------------------------------------------------------------------------------------------------------------------- | -------- | -------: |
| zero-prefix           |             112 | 2, 3, 4, 5, 6, 15, 16, 17, 67, 70, 72, 73, 74, 78, 79, 86, 87, 88, 95, 99, 100, 101, 102, 103, 108, 110, 111, 114, 115 | 2        |       49 |
| psin-magic            |               8 | 93, 94                                                                                                                 | 3        |        1 |
| rbf0-magic            |               4 | 11                                                                                                                     | 3, none  |        2 |
| unrecognized          |              13 | 64, 66, 105, 255                                                                                                       | 3        |        6 |
| rpf9-magic            |               0 | none                                                                                                                   | none     |        0 |
| zlib-container-header |               0 | none                                                                                                                   | none     |        0 |

## Top-level signature census

Counts are first eight stored bytes of the 6,079 untransformed top-level rows
with at least eight stored bytes. The other 455 rows are behind the payload
transform. A class is a byte observation, not a format identity.

| Class                 |  Rows | Occurrence                                                                                    |
| --------------------- | ----: | --------------------------------------------------------------------------------------------- |
| `9FPR`                | 4,351 | Type-0 container rows                                                                         |
| zlib-container-header |   924 | No format assigned                                                                            |
| `KB2n`                |   787 | `movies.rpf` 505; `story000.rpf` 264; `core_restofworld.rpf` 11; `story000_restofworld.rpf` 7 |
| `KB2j`                |    10 | `movies.rpf` only                                                                             |
| `EDUP`                |     3 | Stored bytes; decoded occurrence is 5                                                         |
| `SGD5`                |     2 | `shaders.rpf` only                                                                            |
| `PTFX`                |     1 | `common.rpf` row 151                                                                          |
| zero-prefix           |     1 | `data.rpf` row 476                                                                            |

`9FPR` is the documented RPF9 container. `PTFX`, zlib and the zero prefix have
no assigned format. The `formats/unknown` table lists neither `9FPR`, zlib nor
the zero prefix; it lists `PTFX` as a text payload and records `KB2n` as 505
inspected rows plus 787 prefix-counted rows across four archives. The census
counts 787 `KB2n` rows across those four archives; see INV-F31 and INV-F32.

## Gaps

| Gap                                                                 |   Count |
| ------------------------------------------------------------------- | ------: |
| Top-level archives with no type-0 row                               |       5 |
| Top-level readable type-0 rows not selected by the per-parent limit |   3,188 |
| Top-level readable type-0 rows above the 64 MiB archive cap         |     381 |
| Nested type-0 rows beyond the depth cap                             |       0 |
| Readable nested payload rows not selected by the per-type limit     | 163,826 |
| Readable nested payload rows above the 1 MiB payload cap            |   4,730 |
| Unreadable nested rows                                              |     823 |
| Archive extraction or manifest failures                             |       0 |
| Payload extraction failures                                         |       0 |

The unselected top-level type-0 rows, especially the 381 above 64 MiB, are the
main unknown. They are the only sampled population that could contain further
nested archives; the 782 sampled depth-1 manifests contain none.

### Iteration 8 frontier

The batch probes above are samples. They do not cover the remaining population.

| Population                                           |                                                Unvisited |
| ---------------------------------------------------- | -------------------------------------------------------: |
| Readable type-0 rows above 64 MiB                    | 369 (35 above the 512 MiB probe cap, 334 at or below it) |
| Eligible type-0 rows skipped by the per-parent limit |                                                    3,156 |
| Unreadable nested rows                               |                                                      815 |
| Top-level rows behind the payload transform          |                                                      455 |

## Not concluded

- No payload format is identified. A type ID, a magic or an 8-byte prefix alone
  does not establish a format.
- No extension or original filename is assigned to any nested type ID.
- The 8-byte prefix sample is too short to distinguish resource headers,
  container headers or compressed streams.
- Encoding 4 is absent from this sample.
- Depth-2 absence is a property of this sample, not evidence that nested
  archives never contain archives.
- The nested archive and payload counts are not game-wide totals. They are
  bounded by the per-parent limits, the 64 MiB archive cap and the 20 GiB joint
  byte budget. The 44 archive probes add 12 over-cap and 32 second-batch rows;
  they leave 369 over-cap and 3,156 second-batch rows unvisited.
- The `KB2n` census is reconciled in this revision: INV-F32 splits the
  contradiction into the confinement claim (contradicted) and the two distinct
  787 populations (not the same measurement), and the KB2 subject records the
  four-archive population as KB2-F13.
- The full type-0 census was not completed. The run stopped at 3,362 of 4,351
  rows; every attempted row succeeded, but the partial total is not a population
  statement. The exact depth-2 count, full type histogram and full header range
  table remain unmeasured.
- The transform counts in INV-F36 and the family counts in INV-F33 to INV-F35
  are sample counts over the 849-manifest cache. They are not the full transform
  or payload populations.
