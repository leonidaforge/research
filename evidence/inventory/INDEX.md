# Inventory evidence index

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

| Type | Meaning |
| --- | --- |
| Authenticated manifest | Read-only parse of an RPF9 table of contents whose metadata signature the CLI accepted. Supplies row count, type ID, sizes, layout, chunk encoding and readability |
| Native extraction | `archive extract` exited 0 and the output size equals the row's logical size |
| Payload prefix | First 8 bytes of an extracted payload, reduced to a signature class. Exact prefixes remain in scratch |
| Hash fingerprint | SHA-256 of extracted archive or payload bytes. Only uniqueness and duplicate counts are published |
| Read-only path enumeration | Recursive listing of `*.rpf` under `<GAME_ROOT>` without opening the files |
| Sample audit | Deterministic recomputation of a selection from the stored manifests |

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
- Caps: no cap was reached. Used: 782 archives, 7,988,951,648 archive bytes and
  1,415,428 payload bytes (8,240,768,324 bytes in total). The run stopped
  `complete`. Accounting: 22 top-level archives discovered, 804 parents visited
  (22 top-level and 782 nested) and 782 nested manifests enumerated.
- Depth 2: none of the 782 depth-1 manifests contains a type-0 row at any size,
  so the depth-2 selection has 0 candidates and the maximum depth reached is 1.
- Payload sample: 144 attempts, 137 distinct SHA-256 fingerprints, 7 duplicates.
- Run date: 2026-11-25. All inputs were opened read-only.

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

## Top-level coverage

Type-0 counts are readable rows. `Within 64 MiB` rows were eligible for the
per-parent rule; `Not selected` rows were skipped by the 128-sample limit. The
`Over 64 MiB` column is the archive size-cap gap. The five archives with zero
type-0 rows were skipped because they contain no archive container row.

| Archive | Rows | Type-0 | Within 64 MiB | Over 64 MiB | Selected | Extracted | Not selected |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `anim.rpf` | 265 | 235 | 215 | 20 | 128 | 128 | 87 |
| `appdata0.rpf` | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| `audio.rpf` | 103 | 103 | 60 | 43 | 60 | 60 | 0 |
| `common.rpf` | 418 | 0 | 0 | 0 | 0 | 0 | 0 |
| `data.rpf` | 699 | 41 | 39 | 2 | 39 | 39 | 0 |
| `levels.rpf` | 2,078 | 2,050 | 1,811 | 239 | 128 | 128 | 1,683 |
| `movies.rpf` | 515 | 0 | 0 | 0 | 0 | 0 | 0 |
| `navmeshes.rpf` | 29 | 28 | 17 | 11 | 17 | 17 | 0 |
| `core_bvh4.rpf` | 1,286 | 1,281 | 1,257 | 24 | 128 | 128 | 1,129 |
| `core_licenses_data.rpf` | 4 | 1 | 1 | 0 | 1 | 1 | 0 |
| `core_restofworld001.rpf` | 6 | 1 | 1 | 0 | 1 | 1 | 0 |
| `core_restofworld.rpf` | 39 | 10 | 10 | 0 | 10 | 10 | 0 |
| `shared_minigame000.rpf` | 68 | 49 | 45 | 4 | 45 | 45 | 0 |
| `shared_minigame000_bvh4.rpf` | 13 | 8 | 8 | 0 | 8 | 8 | 0 |
| `story000.rpf` | 763 | 441 | 417 | 24 | 128 | 128 | 289 |
| `story000_script.rpf` | 4 | 4 | 4 | 0 | 4 | 4 | 0 |
| `story000_bvh4.rpf` | 4 | 0 | 0 | 0 | 0 | 0 | 0 |
| `story000_restofworld.rpf` | 39 | 18 | 18 | 0 | 18 | 18 | 0 |
| `packs.rpf` | 172 | 59 | 46 | 13 | 46 | 46 | 0 |
| `script.rpf` | 2 | 2 | 2 | 0 | 2 | 2 | 0 |
| `shaders.rpf` | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| `textures.rpf` | 22 | 20 | 19 | 1 | 19 | 19 | 0 |

## Findings

### Comprehensive run

| ID | Claim | Evidence | Confidence | Limits |
| --- | --- | --- | --- | --- |
| INV-F18 | The comprehensive rule selected 782 readable type-0 rows from 17 of 22 top-level archives. All 782 native extractions exited 0 with output size equal to the logical size. Their SHA-256 fingerprints are distinct, so no duplicate nested archive content was found. The archives total 7,988,951,648 bytes; the smallest is 720 bytes and the largest 66,870,368 bytes. 256 are larger than 8 MiB, 161 larger than 16 MiB and 87 larger than 32 MiB. | Sample audit, native extraction, hash fingerprint | Confirmed (sample) | Readable type-0 rows at or below 64 MiB only. 381 larger type-0 rows were not extracted. 3,188 eligible rows were not selected. Five top-level archives have no type-0 row. The total number of nested archives is unknown. |
| INV-F19 | The 782 nested manifests hold 169,523 rows, 168,700 readable and 823 unreadable, with 40 distinct type IDs. Five type IDs dominate: 100 (27,482 rows), 111 (21,922), 15 (21,742), 67 (15,879) and 11 (13,487). Compared with the 250-archive sample, four type IDs are new: 64, 86, 105 and 109; no prior type ID is absent. Every row reports read source `main`. | Authenticated manifest | Confirmed (sample) | One build and sample. Type IDs are row labels; this index assigns no payload format to them. Names remain unresolved hashes. |
| INV-F20 | Layout and chunk encoding correlate in the comprehensive sample. All 157,593 layout-R rows use chunk encoding 2. Layout F covers 11,930 rows: 11,006 use encoding 3 and 924 have no chunk table. Compression mode 0 covers 169,367 rows and mode 1 covers 156. No row uses encoding 4. All 924 unchunked rows are readable, including all 156 mode-1 rows. | Authenticated manifest | Confirmed (sample correlation) | A sample correlation, not a format rule. No encoding-4 row was available to test. |
| INV-F21 | The 823 unreadable rows are all `unsupported_transform`: 746 type-89 encoding-2 rows, 76 type-11 encoding-3 rows and one type-14 encoding-3 row. They were excluded from payload sampling, so no extraction was attempted for them. | Authenticated manifest | Confirmed (sample) | Row states only. The payload transform remains unsupported (RPF9-F113, RPF9-F116, RPF9-F117). |
| INV-F22 | No type-0 row occurs at any size in the 782 sampled depth-1 manifests. The depth-2 selection therefore has 0 candidates and the recursive sample stops at depth 1. This extends the 250-archive and 44-archive observations to a larger sample. | Authenticated manifest, sample audit | Confirmed (sample); Unknown (general) | 782 of 3,970 eligible type-0 rows were sampled. 3,188 eligible rows and 381 rows above 64 MiB were not extracted. Larger or unselected top-level type-0 rows may contain archives. |
| INV-F23 | All 144 payload attempts exited 0 with exact logical size; none failed. They produced 137 distinct SHA-256 fingerprints; 7 attempts repeated content already seen (`type 5`: 3, `type 79`: 1, `type 255`: 3). The attempts contain 116 encoding-2 rows, 27 encoding-3 rows and 1 row without a chunk table. 36 of 40 type IDs were sampled. Types 14 and 89 are unreadable, and the single type-96 and type-109 rows exceed the 1 MiB payload cap. | Native extraction, hash fingerprint, authenticated manifest | Confirmed (sample) | At most four payloads per type, all at or below 1 MiB. Most readable rows were not extracted. |
| INV-F24 | The 137 unique payloads fall into four prefix classes: 112 zero-prefix, 8 `PSIN`, 4 `RBF0` and 13 unrecognized. `RBF0` occurs only in type 11, across chunk encoding 3 and no chunk table, in two archives. `PSIN` occurs only in types 93 and 94, chunk encoding 3, across eight payloads from one archive. The 13 unrecognized samples are types 64, 66, 105 and 255 with chunk encoding 3, from six archives. The zero-prefix class spans 29 type IDs from 49 archives. No sample begins with `9FPR`, a zlib container header or another documented magic. | Payload prefix | Confirmed (classes and counts); Unknown (format identity) | First 8 bytes only. Exact prefixes stay in scratch. Each non-zero class comes from one or a few archives and a small number of rows. |
| INV-F25 | Type ID does not determine the sampled prefix class. The zero-prefix class spans 29 type IDs; `RBF0` covers type 11; `PSIN` covers types 93 and 94; unrecognized covers types 64, 66, 105 and 255. | Payload prefix | Confirmed (sample independence); Unknown (format identity) | 36 of 40 type IDs were sampled. An 8-byte prefix is weak evidence of format. |
| INV-F26 | Content-hash deduplication found no duplicate archive among the 782 extractions and seven duplicate payloads among 144 attempts. Sampling by name or row index alone would have counted those seven payload extractions twice. | Hash fingerprint | Confirmed (sample) | The archive duplicate count covers the 782 sampled archives, not the whole game. |

### Prior expanded sample (250 archives)

| ID | Claim |
| --- | --- |
| INV-F09 | 250 readable type-0 rows from 17 of 22 top-level archives; all 250 extractions exact; 843,608,368 archive bytes; 1,090,553 payload bytes. 42 archives larger than 8 MiB. |
| INV-F10 | 250 nested manifests hold 38,395 rows, 38,378 readable and 17 unreadable, with 36 type IDs. |
| INV-F11 | Layout R uses encoding 2; layout F uses encoding 3 or no chunk table; no encoding 4. |
| INV-F12 | The 17 unreadable rows are all `unsupported_transform`: 15 type-11 encoding-3, one type-14 encoding-3 and one type-89 encoding-2. |
| INV-F13 | No type-0 row occurs in the 250 depth-1 manifests; the sample stops at depth 1. |
| INV-F14 | 130 payload attempts, all exact; 122 distinct fingerprints and 8 duplicates. |
| INV-F15 | 122 unique payloads: 106 zero-prefix, 8 `PSIN`, 3 `RBF0` and 5 unrecognized. |
| INV-F16 | Type ID does not determine the sampled prefix class. |
| INV-F17 | No duplicate archive among 250; eight duplicate payloads among 130 attempts. |

### Original bounded sample (44 archives, INV-F01 to INV-F08)

| ID | Claim |
| --- | --- |
| INV-F01 | 44 readable type-0 rows from 17 of 22 top-level archives; all 44 extractions exact; 100,904,448 archive bytes; 39 payloads of 1,044,822 bytes. |
| INV-F02 | All 44 nested files begin with `9FPR` and authenticate under the same build; 44 distinct SHA-256 fingerprints. |
| INV-F03 | The 44 manifests hold 3,553 rows and 25 type IDs; 3,535 readable and 18 unreadable. |
| INV-F04 | Layout R uses encoding 2 and layout F uses encoding 3 or no chunk table in that sample; no encoding 4. |
| INV-F05 | All 44 archive and 39 payload extractions succeeded; 18 unreadable rows were not attempted. |
| INV-F06 | The 39 payloads split into 34 zero-prefix and 5 non-zero prefixes; no archive or zlib header prefix. |
| INV-F07 | Type ID does not determine the sampled prefix class; 18 type IDs share the zero-prefix class. |
| INV-F08 | No depth-1 archive contains a type-0 row, so the 44-archive sample stops at depth 1; larger and unselected archives were not examined. |

## Type histogram

Counts are rows in the 782 unique nested manifests. "Encoding" is the
chunk-table encoding; `none` means no chunk table.

| Type ID | Rows | Readable | Unreadable | Encoding |
| ---: | ---: | ---: | ---: | --- |
| 2 | 6,613 | 6,613 | 0 | 2 |
| 3 | 5,107 | 5,107 | 0 | 2 |
| 4 | 7,522 | 7,522 | 0 | 2 |
| 5 | 1,557 | 1,557 | 0 | 2 |
| 6 | 3,891 | 3,891 | 0 | 2 |
| 11 | 13,487 | 13,411 | 76 | 2: 4,507; 3: 8,824; none: 156 |
| 14 | 1 | 0 | 1 | 3 |
| 15 | 21,742 | 21,742 | 0 | 2 |
| 16 | 1,604 | 1,604 | 0 | 2 |
| 17 | 1,781 | 1,781 | 0 | 2 |
| 64 | 324 | 324 | 0 | 3 |
| 66 | 49 | 49 | 0 | 3 |
| 67 | 15,879 | 15,879 | 0 | 2 |
| 70 | 5,142 | 5,142 | 0 | 2 |
| 72 | 226 | 226 | 0 | 2 |
| 73 | 6,653 | 6,653 | 0 | 2 |
| 74 | 594 | 594 | 0 | 2 |
| 78 | 7,638 | 7,638 | 0 | 2 |
| 79 | 7,506 | 7,506 | 0 | 2 |
| 86 | 11 | 11 | 0 | 2 |
| 87 | 7,138 | 7,138 | 0 | 2 |
| 88 | 176 | 176 | 0 | 2 |
| 89 | 746 | 0 | 746 | 2 |
| 93 | 211 | 211 | 0 | 3 |
| 94 | 80 | 80 | 0 | 3 |
| 95 | 97 | 97 | 0 | 2 |
| 96 | 1 | 1 | 0 | 3 |
| 99 | 98 | 98 | 0 | 2 |
| 100 | 27,482 | 27,482 | 0 | 2 |
| 101 | 5 | 5 | 0 | 2 |
| 102 | 94 | 94 | 0 | 2 |
| 103 | 1,511 | 1,511 | 0 | 2 |
| 105 | 1,476 | 1,476 | 0 | 3 |
| 108 | 110 | 110 | 0 | 2 |
| 109 | 1 | 1 | 0 | 2 |
| 110 | 5 | 5 | 0 | 2 |
| 111 | 21,922 | 21,922 | 0 | 2 |
| 114 | 97 | 97 | 0 | 2 |
| 115 | 138 | 138 | 0 | 2 |
| 255 | 808 | 808 | 0 | 3: 40; none: 768 |

Type 0 does not appear in the nested manifests; it labels the top-level rows
used as archive containers in this sample.

## Extraction outcomes

| Measure | Result |
| --- | ---: |
| Nested archive attempts | 782 |
| Nested archive successes | 782 |
| Nested archive failures | 0 |
| Duplicate nested archives | 0 |
| Nested archive bytes | 7,988,951,648 |
| Payload attempts | 144 |
| Payload successes | 144 |
| Payload failures | 0 |
| Unique payload fingerprints | 137 |
| Duplicate payloads | 7 |
| Payload bytes | 1,415,428 |
| Total extracted bytes | 8,240,768,324 |
| Extraction failures | 0 |

## Payload signature classes

| Class | Unique payloads | Type IDs | Encoding | Archives |
| --- | ---: | --- | --- | ---: |
| zero-prefix | 112 | 2, 3, 4, 5, 6, 15, 16, 17, 67, 70, 72, 73, 74, 78, 79, 86, 87, 88, 95, 99, 100, 101, 102, 103, 108, 110, 111, 114, 115 | 2 | 49 |
| psin-magic | 8 | 93, 94 | 3 | 1 |
| rbf0-magic | 4 | 11 | 3, none | 2 |
| unrecognized | 13 | 64, 66, 105, 255 | 3 | 6 |
| rpf9-magic | 0 | none | none | 0 |
| zlib-container-header | 0 | none | none | 0 |

## Gaps

| Gap | Count |
| --- | ---: |
| Top-level archives with no type-0 row | 5 |
| Top-level readable type-0 rows not selected by the per-parent limit | 3,188 |
| Top-level readable type-0 rows above the 64 MiB archive cap | 381 |
| Nested type-0 rows beyond the depth cap | 0 |
| Readable nested payload rows not selected by the per-type limit | 163,826 |
| Readable nested payload rows above the 1 MiB payload cap | 4,730 |
| Unreadable nested rows | 823 |
| Archive extraction or manifest failures | 0 |
| Payload extraction failures | 0 |

The unselected top-level type-0 rows, especially the 381 above 64 MiB, are the
main unknown. They are the only sampled population that could contain further
nested archives; the 782 sampled depth-1 manifests contain none.

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
  byte budget.
