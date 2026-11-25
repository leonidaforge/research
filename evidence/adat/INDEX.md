# ADAT evidence index

`ADAT` (`41 44 41 54`) is a stored-payload signature of type-255 rows in depth-1
archives. This index records the population, the header structure, the variant
layouts, and the corrections to the earlier ADAT notes.

The earlier combined [GFX* and ADAT index](../gfx-adat/INDEX.md) first recorded
the signature from a scratch discovery sample. The GFX* evidence remains there.

## Sample frames

| Frame | Scope | ADAT rows | Signature reading |
| --- | --- | ---: | --- |
| Top-level stored-byte census (UPL-F01) | 22 top-level archives | 0 | First eight stored bytes of untransformed top-level rows |
| Newer scratch inventory, depth 1 | 782 archives | 768 | Stored payload offset 0 of type-255 rows |

The depth-1 frame is the `inventory-expansion` cache. Its summary records 782 of
3,970 candidate archives extracted at depth 1, with 381 type-0 rows above the
archive size cap. The cache contains 849 archive manifests after deduplication
of repeated `archives.jsonl` entries; 75 archives contain at least one type-255
row, and 65 contain ADAT rows.

The ADAT rows are all depth 1:

| Family | Rows | Archives | Top-level parent |
| --- | ---: | ---: | --- |
| `audio.rpf` depth 1 | 729 | 59 | `audio.rpf` |
| Other depth 1 | 39 | 6 | `shared_minigame000.rpf`, `story000.rpf`, `story000_restofworld.rpf` |

The 60th scanned `audio.rpf` archive supplies 18 type-255 rows whose stored
bytes begin a zlib stream (`78 DA`). They are not part of the 768. Elsewhere,
the same type ID carries `FORC` (`FORC_EMPTY_RPF`) and zlib payloads, so type 255
does not identify ADAT.

## Census

| Property | Observation | Support |
| --- | --- | --- |
| Stored size | 4,224 to 51,693,440 bytes | 768/768 |
| Logical size | equal to stored size in 659 rows; 109 add 2 to 14 even bytes | 768/768 |
| Chunk table | none | 768/768 |
| Compression mode | 0 | 768/768 |
| Payload transform | false | 768/768 |

Size distribution:

| Stored size | All rows | `audio.rpf` rows | Other rows |
| --- | ---: | ---: | ---: |
| under 16 KiB | 17 | 17 | 0 |
| 16 to 64 KiB | 54 | 52 | 2 |
| 64 to 256 KiB | 198 | 188 | 10 |
| 256 KiB to 1 MiB | 262 | 243 | 19 |
| 1 to 4 MiB | 188 | 182 | 6 |
| 4 to 16 MiB | 42 | 40 | 2 |
| 16 to 64 MiB | 7 | 7 | 0 |
| 64 MiB or more | 0 | 0 | 0 |

## Findings

`ADAT-F01` to `ADAT-F05` in the combined index are superseded. Those identifiers
are retired and are not reused; the findings below start at `ADAT-F06`.

| ID | Claim | Evidence | Confidence | Limits |
| --- | --- | --- | --- | --- |
| ADAT-F06 | `ADAT` begins 768 stored type-255 payloads in 65 depth-1 archives under four top-level archives. The rows split into 729 rows in 59 `audio.rpf` archives and 39 rows in six archives under three other top-level archives. | `BINARY`, `CROSS_SAMPLE` | Confirmed (sample) | Depth-1 sample only; 18 zlib type-255 rows in one `audio.rpf` archive are excluded |
| ADAT-F07 | All 768 rows share a 16-byte common header: magic, `u16` version 1, `u16` variant word, `u32` count and `u32` data offset. The variant word is one of `FF02` (124 rows), `FF21` (283), `FF25` (275) and `FF61` (86). | `BINARY`, `CROSS_SAMPLE` | Confirmed (values) | Variant-word meaning is Unknown |
| ADAT-F08 | The `u32` at `+0x08` is a count from 1 to 674. For `FF21`, `FF25` and `FF61` it equals the number of `u16` entries in the table at `+0x10` or `+0x14` in 644/644 rows. For `FF02` it equals the number of fixed-width records in 123/124 rows. | `BINARY`, `CROSS_SAMPLE` | Confirmed (boundary) | One `FF02` row has a non-integral record width |
| ADAT-F09 | The `u32` at `+0x0C` is a payload-relative data offset from 46 to 27,484. It is even, follows the variant table and precedes the stored size in 768/768 rows. The byte before it is `A3` (608 rows), `BD` (117) or `76` (43); the byte at it takes 158 values (`00` 367, `A0` 115). The one-byte distributions immediately before and at the offset have total variation distance 0.997. | `BINARY`, `CROSS_SAMPLE` | Confirmed (boundary and byte counts) | The table before the offset is only partly interpreted; the byte comparison uses one byte on each side |
| ADAT-F10 | `FF21` and `FF25` place a non-decreasing `u16[count]` table at `+0x10`. `FF21` has no decrease and no equal adjacent pair in 283/283 rows; 26 of those rows have a single entry. `FF25` permits equal adjacent entries in 36/275 rows. | `BINARY`, `CROSS_SAMPLE` | Confirmed (sample) | Table-entry meaning is Unknown |
| ADAT-F11 | `FF61` places a second `u32` payload-relative offset at `+0x10` and a non-decreasing `u16[count]` table at `+0x14`. The second offset is greater than the data offset and smaller than the stored size in 86/86 rows; the preceding byte is `00` in 86/86 rows. | `BINARY`, `CROSS_SAMPLE` | Confirmed (offset); Probable (second data region) | Role of the second offset is not established |
| ADAT-F12 | `FF02` rows carry a record region instead of a `u16` index table. The data offset equals `0x10 + width * count`; width is 36 bytes in 113/113 `audio.rpf` rows and 44 or 60 bytes in 10/11 other rows. | `BINARY`, `CROSS_SAMPLE` | Confirmed (arithmetic) | One other row has no integral width; record contents are not interpreted |
| ADAT-F13 | Archive family changes one header relation only. `u32@+0x0C = 0x10 + 36 * u32@+0x08` holds for 113/113 `audio.rpf` `FF02` rows and 0/11 other `FF02` rows. `FF21`, `FF25` and `FF61` show no family-correlated layout difference. | `CROSS_SAMPLE` | Confirmed (sample) | Placement is provenance; the sample cannot separate payload subvariant from selection |
| ADAT-F14 | The evidence supports one ADAT format family with four header variants, not four unrelated formats. The common header and shared count/offset semantics hold across all 768 rows. | `CROSS_SAMPLE` | Confirmed (sample) | No codec identity or field purpose is assigned |
| ADAT-F15 | The earlier 21-row structural observation is superseded by the 768-row header census. All 768 rows were read at least to the data offset; the 21 earlier rows were the only ones previously inspected beyond eight bytes. | `BINARY`, `CROSS_SAMPLE` | Confirmed (scope) | Full payloads were not reconstructed |
| ADAT-F16 | In the 644 rows with a `u16[count]` table, every table is non-decreasing. No adjacent increase exceeds 5 (5 in `FF21`, 3 in `FF25`, 5 in `FF61`). The `u16` after the table is at least 2,045 (`FF21`), 381 (`FF25`) and 5,700 (`FF61`) above the last entry. | `BINARY`, `CROSS_SAMPLE` | Confirmed (observations) | Empirical bounds from one build; `FF02` (124 rows) has no `u16` table; a genuine increment above 5 would fail the table-length test and none occurs |
| ADAT-F17 | In the same 644 rows the position gap between the `u16[count]` table end and the data offset is 28 to 26,116 bytes and is positively associated with the count: Pearson r 0.996/0.895/0.9999 and Spearman rho 0.997/0.627/0.9998 for `FF21`/`FF25`/`FF61`. The gap is even in all 644 rows. | `BINARY`, `CROSS_SAMPLE` | Confirmed (association) | The gap is uninterpreted; the association is not a fixed formula; the earlier independence wording is withdrawn |

## Variant table detail

| Variant | Family split | Count range | Data offset range | Layout |
| --- | --- | ---: | ---: | --- |
| `FF02` | 113 `audio.rpf` / 11 other | 1 to 144 | 52 to 5,200 | record region from `+0x10` |
| `FF21` | 276 / 7 | 1 to 231 | 46 to 9,690 | `u16[count]` at `+0x10` |
| `FF25` | 256 / 19 | 2 to 9 | 64 to 134 | `u16[count]` at `+0x10` |
| `FF61` | 84 / 2 | 6 to 674 | 228 to 27,484 | `u32` offset at `+0x10`; `u16[count]` at `+0x14` |

The position gap between the end of the `u16[count]` table and the data offset
is not independent of the count. `ADAT-F17` covers the 644 rows with such a
table.

| Variant | Rows | Gap range | Median | Pearson r | Spearman rho |
| --- | ---: | ---: | ---: | ---: | ---: |
| `FF21` | 283 | 28 to 9,212 | 604 | 0.996 | 0.997 |
| `FF25` | 275 | 44 to 100 | 44 | 0.895 | 0.627 |
| `FF61` | 86 | 196 to 26,116 | 1,540 | 0.9999 | 0.9998 |

The gap is even in all 644 rows. All three variant correlations are positive.
The gap is not a fixed function of the count: the 26 `FF21` rows with count 1
take four gap values (28, 36, 44 and 52), and a least-squares fit of gap on
count leaves residual standard deviations of 110 (`FF21`), 4.1 (`FF25`) and 44
(`FF61`) bytes. Counterexamples: none to the positive association.
Exclusions: the 124 `FF02` rows have a record region instead of a `u16`
table, so the gap is undefined there; the 18 zlib type-255 rows are outside
the 768. The gap remains uninterpreted; no size role is assigned to it.

## Table-end test

`ADAT-F16` covers every deduplicated ADAT row whose variant carries a
`u16[count]` table: 283 `FF21`, 275 `FF25` and 86 `FF61`, 644 rows in total.
The table starts at `+0x10` for `FF21` and `FF25`, and at `+0x14` for `FF61`.
The 644 rows are the whole ADAT table population in the extracted depth-1
sample, not a subsample.

| Variant | Rows | Count 1 | Adjacent pairs | No decrease | Equal pairs | Max increase | Min post-table delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `FF21` | 283 | 26 | 8,113 | 283 | 0 | 5 | 2,045 |
| `FF25` | 275 | 0 | 373 | 275 | 87 | 3 | 381 |
| `FF61` | 86 | 0 | 3,946 | 86 | 0 | 5 | 5,700 |

Supporting observations: the minimum post-table delta occurs once in `FF21`
(last entry 116, next `u16` 2,161), twice in `FF25` (3 to 384) and once in
`FF61` (260 to 5,960). No adjacent pair decreases, and no increase exceeds 5.

Counterexamples: none in the 644 rows. Exclusions: the 124 `FF02` rows have no
`u16` table; the 18 zlib type-255 rows are outside the 768.

Remaining limitation: the maximum increase of 5 and the minimum jumps are
empirical bounds from one build. The test finds the table end from the jump, so a genuine
adjacent increase above 5 would be read as the end of the table. No such row
occurs in the sample.

## Data-offset byte boundary

`ADAT-F09` covers all 768 deduplicated ADAT rows of the depth-1 sample. For each
row, compare the byte at `payload + u32@+0x0C - 1` with the byte at
`payload + u32@+0x0C`.

| Byte position | Distinct values | Most frequent |
| --- | ---: | --- |
| offset - 1 | 3 | `A3` 608, `BD` 117, `76` 43 |
| offset | 158 | `00` 367, `A0` 115, `80` 14, `03` 11, `58` 11, `C0` 11 |

The two one-byte distributions have total variation distance 0.997. Their
supports overlap only at `76` and `BD`, each once at the offset, and no row has
the same byte on both sides.

Counterexamples: none; the counts are exhaustive over all 768 rows. Exclusions:
none in the 768; the 18 zlib type-255 rows are outside the population.

Remaining limitation: the comparison uses one byte on each side of the
boundary. It does not characterise the encoded stream, and no codec identity
follows.

## Bounded search procedure

1. Open the inventory cache and select manifests whose parent is a depth-1
   archive.
2. For every type-255 row, read bytes at the manifest `payload_offset` and
   require `41 44 41 54` at offset 0.
3. For chunked rows, decode the first chunk before classifying. The ADAT sample
   has no chunked rows.
4. Treat `ADAT` inside printable XML as a false positive; require offset 0.
5. Record the archive, row, stored and logical sizes, chunk state, transform
   state and the first 16 payload bytes. Keep payload extracts outside Git.

Applied to the `inventory-expansion` cache, the procedure finds 768 rows. The
counts are sample counts because the depth-1 frame selected 782 of 3,970
candidate archives.

## Stratified extraction

A stratified sample of 76 payloads was staged outside Git from the 768 rows. The
strata are:

- archive family: `audio.rpf` depth 1 and the six other depth-1 archives;
- variant word: all four values;
- stored-size buckets: under 16 KiB to 16 to 64 MiB;
- the smallest and largest row in each occupied stratum;
- the global smallest and largest rows;
- the smallest row of every other depth-1 archive.

The sample total is 203,051,648 bytes. A JSONL manifest records the file name,
family, parent archive, archive SHA-256, row, variant word, count, data offset,
sizes and payload SHA-256. The payload files and manifest are not part of this
repository.

## Research history

### Iteration 7 scope and variant-word correction

The earlier ADAT record stated 729 rows in 59 depth-1 archives under
`audio.rpf`, and gave the fourth variant word as `0xFF41` with 84 rows.

- The 729 count is correct for the `audio.rpf` depth-1 family, but it is not the
  full depth-1 population. The same scan also holds 39 ADAT rows in six depth-1
  archives under `shared_minigame000.rpf`, `story000.rpf` and
  `story000_restofworld.rpf`. The corrected total is 768 rows in 65 archives.
- The fourth variant word is `0xFF61` (bytes `61 FF`), not `0xFF41`. The 84-row
  count belongs to `0xFF61`; the earlier value was a transcription error. With
  the 39 other rows, `0xFF61` occurs in 86 rows.
- The earlier `+0x06`, `+0x08` and `+0x0C` values were recorded as observations
  only. `+0x08` is now a count with a table-length boundary, and `+0x0C` is a
  data offset. The table layouts and family-correlated `FF02` width are new.

### Iteration 8 evidence types and boundary correction

- `ADAT-F06` to `ADAT-F15` now record policy evidence types in place of method
  prose. They rest on cached payload bytes and cross-row comparisons, so they
  use `BINARY` and `CROSS_SAMPLE`; `ADAT-F13` and `ADAT-F14` are comparative
  claims and carry `CROSS_SAMPLE` alone. No `STATIC_CODE`, `RUNTIME`,
  `HISTORICAL` or `SYNTHETIC` evidence supports them.
- The statement that the post-table gap "varies independently of the count" is
  withdrawn. Over the 644 rows with a `u16[count]` table the gap is positively
  associated with the count (Pearson r 0.895 to 0.9999 and Spearman rho 0.627
  to 0.9998 by variant). The gap remains uninterpreted.
- The byte-boundary statement now names its population: all 768 rows, one byte
  on each side of the data offset. The two one-byte distributions have total
  variation distance 0.997.
- The table-end bounds are recorded in `ADAT-F16` with their 644-row population
  and no counterexamples. `FF21` has 26 single-entry rows, where the
  adjacent-entry test is vacuous.

## Reproduction

`<WORK>` is a scratch directory outside the repository. The cache paths and
archive names are local inputs, not format evidence.

```text
lforge archive manifest <WORK>/audio-row77.rpf --executable <EXECUTABLE> --format jsonl
```

For each cached depth-1 archive, read the row's `payload_offset` and test the
first four bytes. For the header fields, read 16 bytes at the same offset. The
data offset at `+0x0C` is relative to the payload start, not to the row or
archive. No payload file is committed.

For the table-end test, read `u16[count]` at `+0x10` (`FF21`, `FF25`) or
`+0x14` (`FF61`), compare adjacent entries, and read the next `u16`. For the
post-table gap, subtract the table end from the `+0x0C` offset. For the byte
boundary, compare the bytes at `offset - 1` and `offset`.

## Limits

- One build and one local archive set.
- The depth-1 frame is a selection, not a census; 381 type-0 rows were above the
  archive size cap.
- The 18 zlib type-255 rows in one `audio.rpf` archive were not decoded.
- The region between the variant table and the data offset is not interpreted.
- No executable path was traced. Field meaning beyond count and offset is
  Unknown, and no codec identity is assigned.
