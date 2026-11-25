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

### Expanded run

- Input: 22 unique top-level archives from 23 manifest files. One duplicate
  manifest path was ignored. A recursive `*.rpf` enumeration under `<GAME_ROOT>`
  returned the same 22 files: 12 in the root and 10 under `pack/`.
- Authentication: every top-level manifest header reports a verified metadata
  signature. All 250 extracted nested manifests report `authenticated`. The
  sampler does not re-check signatures.
- Top-level population: 6,534 rows. 17 archives contain 4,351 readable type-0
  rows; 3,077 are at or below 16 MiB and 1,274 are above it. Five archives
  contain no type-0 row: `appdata0.rpf`, `common.rpf`, `movies.rpf`,
  `story000_bvh4.rpf` and `shaders.rpf`.
- Rule: per parent, order readable type-0 rows at or below 16 MiB by
  `(logical size, row)` and take quantile-spaced indices, including the smallest
  and largest. The limits are 24 rows per top-level archive, 6 per depth-1
  archive and 3 per depth-2 archive. The tool is
  [tools/inventory](../../tools/inventory/README.md).
- Result: 250 unique depth-1 archives from 17 top-level archives. Eight
  top-level archives contributed 24 samples, `story000_restofworld.rpf` 17,
  `textures.rpf` 16, `core_restofworld.rpf` 8, `shared_minigame000_bvh4.rpf` 6,
  `navmeshes.rpf` 5, `script.rpf` 2, `story000_script.rpf` 2,
  `core_licenses_data.rpf` 1 and `core_restofworld001.rpf` 1.
- Caps: depth 3, 400 unique archives, 3 GiB extracted bytes, 16 MiB per archive,
  4 payloads per type at or below 1 MiB. Used: 250 archives, 843,608,368 archive
  bytes and 1,090,553 payload bytes (844,698,921 bytes in total).
- Depth 2: none of the 250 depth-1 manifests contains a type-0 row at any size,
  so the depth-2 selection has 0 candidates and the maximum depth reached is 1.
- Payload sample: 130 attempts, 122 distinct SHA-256 fingerprints, 8 duplicates.
- Run date: 2026-11-25. All inputs were opened read-only.

### Prior bounded sample

The earlier run sampled 44 depth-1 archives and 3,553 nested rows with 25 type
IDs, using 3 samples per top-level archive and an 8 MiB archive cap. It found no
type-0 row in its 44 depth-1 manifests. Its findings remain valid for that frame
and are listed below as INV-F01 to INV-F08.

## Top-level coverage

Type-0 counts are readable rows. `Within 16 MiB` rows were eligible for the
per-parent rule; `Not selected` rows were skipped by the 24-sample limit. The
`Over 16 MiB` column is the archive size-cap gap. The five archives with zero
type-0 rows were skipped because they contain no archive container row.

| Archive | Rows | Type-0 | Within 16 MiB | Over 16 MiB | Selected | Extracted | Not selected |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `anim.rpf` | 265 | 235 | 190 | 45 | 24 | 24 | 166 |
| `appdata0.rpf` | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| `audio.rpf` | 103 | 103 | 35 | 68 | 24 | 24 | 11 |
| `common.rpf` | 418 | 0 | 0 | 0 | 0 | 0 | 0 |
| `data.rpf` | 699 | 41 | 38 | 3 | 24 | 24 | 14 |
| `levels.rpf` | 2,078 | 2,050 | 1,138 | 912 | 24 | 24 | 1,114 |
| `movies.rpf` | 515 | 0 | 0 | 0 | 0 | 0 | 0 |
| `navmeshes.rpf` | 29 | 28 | 5 | 23 | 5 | 5 | 0 |
| `core_bvh4.rpf` | 1,286 | 1,281 | 1,207 | 74 | 24 | 24 | 1,183 |
| `core_licenses_data.rpf` | 4 | 1 | 1 | 0 | 1 | 1 | 0 |
| `core_restofworld001.rpf` | 6 | 1 | 1 | 0 | 1 | 1 | 0 |
| `core_restofworld.rpf` | 39 | 10 | 8 | 2 | 8 | 8 | 0 |
| `shared_minigame000.rpf` | 68 | 49 | 43 | 6 | 24 | 24 | 19 |
| `shared_minigame000_bvh4.rpf` | 13 | 8 | 6 | 2 | 6 | 6 | 0 |
| `story000.rpf` | 763 | 441 | 340 | 101 | 24 | 24 | 316 |
| `story000_script.rpf` | 4 | 4 | 2 | 2 | 2 | 2 | 0 |
| `story000_bvh4.rpf` | 4 | 0 | 0 | 0 | 0 | 0 | 0 |
| `story000_restofworld.rpf` | 39 | 18 | 17 | 1 | 17 | 17 | 0 |
| `packs.rpf` | 172 | 59 | 28 | 31 | 24 | 24 | 4 |
| `script.rpf` | 2 | 2 | 2 | 0 | 2 | 2 | 0 |
| `shaders.rpf` | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| `textures.rpf` | 22 | 20 | 16 | 4 | 16 | 16 | 0 |

## Findings

### Expanded run

| ID | Claim | Evidence | Confidence | Limits |
| --- | --- | --- | --- | --- |
| INV-F09 | The expanded rule selected 250 readable type-0 rows from 17 of 22 top-level archives. All 250 native extractions exited 0 with output size equal to the logical size. Their SHA-256 fingerprints are distinct, so no duplicate nested archive content was found. The archives total 843,608,368 bytes; the smallest is 720 bytes and the largest 16,714,192 bytes. 42 are larger than 8 MiB. | Sample audit, native extraction, hash fingerprint | Confirmed (sample) | Readable type-0 rows at or below 16 MiB only. 1,274 larger type-0 rows were not extracted. Five top-level archives have no type-0 row. The total number of nested archives is unknown. |
| INV-F10 | The 250 nested manifests hold 38,395 rows, 38,378 readable and 17 unreadable, with 36 distinct type IDs. Three type IDs dominate: 11 (11,040 rows), 111 (10,181) and 100 (4,896). Compared with the prior 25-type sample, 12 type IDs are new: 6, 17, 93, 94, 95, 99, 100, 101, 102, 108, 110 and 114. Type 109 was present in the prior sample but absent here. Every row reports read source `main`. | Authenticated manifest | Confirmed (sample) | One build and sample. Type IDs are row labels; this index assigns no payload format to them. Names remain unresolved hashes. |
| INV-F11 | Layout and chunk encoding correlate in the expanded sample. All 35,548 layout-R rows use chunk encoding 2. Layout F covers 2,847 rows: 2,536 use encoding 3 and 311 have no chunk table. Compression mode 0 covers 38,239 rows and mode 1 covers 156. No row uses encoding 4. All 311 unchunked rows are readable, including all 156 mode-1 rows. | Authenticated manifest | Confirmed (sample correlation) | A sample correlation, not a format rule. No encoding-4 row was available to test. |
| INV-F12 | The 17 unreadable rows are all `unsupported_transform`: 15 type-11 encoding-3 rows, one type-14 encoding-3 row and one type-89 encoding-2 row. They were excluded from payload sampling, so no extraction was attempted for them. | Authenticated manifest | Confirmed (sample) | Row states only. The payload transform remains unsupported (RPF9-F113, RPF9-F116, RPF9-F117). |
| INV-F13 | No type-0 row occurs at any size in the 250 sampled depth-1 manifests. The depth-2 selection therefore has 0 candidates and the recursive sample stops at depth 1. This extends the prior 44-archive observation to a larger sample. | Authenticated manifest, sample audit | Confirmed (sample); Unknown (general) | 250 of 3,077 eligible type-0 rows were sampled. 2,827 eligible rows and 1,274 rows above 16 MiB were not extracted. Larger or unselected top-level type-0 rows may contain archives. |
| INV-F14 | All 130 payload attempts exited 0 with exact logical size; none failed. They produced 122 distinct SHA-256 fingerprints; 8 attempts repeated content already seen (`type 5`: 3, `type 255`: 3, `type 11`: 1, `type 79`: 1). The sample contains 110 encoding-2 rows, 16 encoding-3 rows and 4 unchunked mode-1 rows. 33 of 36 type IDs were sampled. Types 14 and 89 are unreadable, and the single type-96 row exceeds the 1 MiB payload cap. | Native extraction, hash fingerprint, authenticated manifest | Confirmed (sample) | At most four payloads per type, all at or below 1 MiB. Most readable rows were not extracted. |
| INV-F15 | The 122 unique payloads fall into four prefix classes: 106 zero-prefix, 8 `PSIN`, 3 `RBF0` and 5 unrecognized. `RBF0` occurs only in type 11, mode 1 without a chunk table, across three payloads from one archive. `PSIN` occurs only in types 93 and 94, chunk encoding 3, across eight payloads from one archive. The five unrecognized samples are type 66 and type 255 with chunk encoding 3. No sample begins with `9FPR`, a zlib container header or another documented magic. | Payload prefix | Confirmed (classes and counts); Unknown (format identity) | First 8 bytes only. Exact prefixes stay in scratch. Each non-zero class comes from one archive and a small number of rows. |
| INV-F16 | Type ID does not determine the sampled prefix class. The zero-prefix class spans 28 type IDs; `RBF0` covers type 11; `PSIN` covers types 93 and 94; unrecognized covers types 66 and 255. Type 255 carried several distinct signatures in the prior sample and one unrecognized class here. | Payload prefix | Confirmed (sample independence); Unknown (format identity) | 33 of 36 type IDs were sampled. An 8-byte prefix is weak evidence of format. |
| INV-F17 | Content-hash deduplication found no duplicate archive among the 250 extractions and eight duplicate payloads among 130 attempts. Sampling by name or row index alone would have counted those eight payload extractions twice. | Hash fingerprint | Confirmed (sample) | The archive duplicate count covers the 250 sampled archives, not the whole game. |

### Prior bounded sample (INV-F01 to INV-F08)

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

Counts are rows in the 250 unique nested manifests. "Encoding" is the chunk-table
encoding; `none` means no chunk table.

| Type ID | Rows | Readable | Unreadable | Encoding |
| ---: | ---: | ---: | ---: | --- |
| 2 | 996 | 996 | 0 | 2 |
| 3 | 446 | 446 | 0 | 2 |
| 4 | 687 | 687 | 0 | 2 |
| 5 | 191 | 191 | 0 | 2 |
| 6 | 275 | 275 | 0 | 2 |
| 11 | 11,040 | 11,025 | 15 | 2: 8,673, 3: 2,211, none: 156 |
| 14 | 1 | 0 | 1 | 3 |
| 15 | 2,719 | 2,719 | 0 | 2 |
| 16 | 120 | 120 | 0 | 2 |
| 17 | 293 | 293 | 0 | 2 |
| 66 | 12 | 12 | 0 | 3 |
| 67 | 803 | 803 | 0 | 2 |
| 70 | 1,249 | 1,249 | 0 | 2 |
| 72 | 149 | 149 | 0 | 2 |
| 73 | 1,044 | 1,044 | 0 | 2 |
| 74 | 106 | 106 | 0 | 2 |
| 78 | 1,037 | 1,037 | 0 | 2 |
| 79 | 162 | 162 | 0 | 2 |
| 87 | 580 | 580 | 0 | 2 |
| 88 | 140 | 140 | 0 | 2 |
| 89 | 1 | 0 | 1 | 2 |
| 93 | 211 | 211 | 0 | 3 |
| 94 | 80 | 80 | 0 | 3 |
| 95 | 97 | 97 | 0 | 2 |
| 96 | 1 | 1 | 0 | 3 |
| 99 | 98 | 98 | 0 | 2 |
| 100 | 4,896 | 4,896 | 0 | 2 |
| 101 | 5 | 5 | 0 | 2 |
| 102 | 93 | 93 | 0 | 2 |
| 103 | 266 | 266 | 0 | 2 |
| 108 | 3 | 3 | 0 | 2 |
| 110 | 3 | 3 | 0 | 2 |
| 111 | 10,181 | 10,181 | 0 | 2 |
| 114 | 97 | 97 | 0 | 2 |
| 115 | 138 | 138 | 0 | 2 |
| 255 | 175 | 175 | 0 | 3: 20, none: 155 |

Type 0 does not appear in the nested manifests; it labels the top-level rows
used as archive containers in this sample.

## Extraction outcomes

| Measure | Result |
| --- | ---: |
| Nested archive attempts | 250 |
| Nested archive successes | 250 |
| Nested archive failures | 0 |
| Duplicate nested archives | 0 |
| Nested archive bytes | 843,608,368 |
| Payload attempts | 130 |
| Payload successes | 130 |
| Payload failures | 0 |
| Unique payload fingerprints | 122 |
| Duplicate payloads | 8 |
| Payload bytes | 1,090,553 |
| Extraction failures | 0 |

## Payload signature classes

| Class | Unique payloads | Type IDs | Encoding | Archives |
| --- | ---: | --- | --- | ---: |
| zero-prefix | 106 | 2, 3, 4, 5, 6, 15, 16, 17, 67, 70, 72, 73, 74, 78, 79, 87, 88, 95, 99, 100, 101, 102, 103, 108, 110, 111, 114, 115 | 2 | 41 |
| psin-magic | 8 | 93, 94 | 3 | 1 |
| rbf0-magic | 3 | 11 | none (mode 1) | 1 |
| unrecognized | 5 | 66, 255 | 3 | 3 |
| rpf9-magic | 0 | none | none | 0 |
| zlib-container-header | 0 | none | none | 0 |

## Gaps

| Gap | Count |
| --- | ---: |
| Top-level archives with no type-0 row | 5 |
| Top-level readable type-0 rows not selected by the per-parent limit | 2,827 |
| Top-level readable type-0 rows above the 16 MiB archive cap | 1,274 |
| Nested type-0 rows beyond the depth cap | 0 |
| Readable nested payload rows not selected by the per-type limit | 37,690 |
| Readable nested payload rows above the 1 MiB payload cap | 558 |
| Unreadable nested rows | 17 |
| Archive extraction or manifest failures | 0 |
| Payload extraction failures | 0 |

The unselected top-level type-0 rows, especially the 1,274 above 16 MiB, are the
main unknown. They are the only sampled population that could contain further
nested archives; the 250 sampled depth-1 manifests contain none.

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
  bounded by the per-parent limits, the 16 MiB archive cap and the 3 GiB byte
  cap.
