# ADAT evidence index

`ADAT` (`41 44 41 54`) is a stored-payload signature of type-255 rows in depth-1
archives. This index records the population, the header structure, the variant
layouts, and the corrections to the earlier ADAT notes.

The earlier combined [GFX* and ADAT index](../gfx-adat/INDEX.md) first recorded
the signature from a scratch discovery sample. The GFX* evidence remains there.

## Sample frames

| Frame | Scope | ADAT rows | Signature reading |
| --- | --- | ---: | --- |
| Top-level stored-byte census (UPL-F01) | 22 top-level archives; 6,079 untransformed rows inspected, 455 transformed rows not inspected | 0 | First eight stored bytes of untransformed top-level rows |
| Newer scratch inventory, depth 1 | 782 archives | 768 | Stored payload offset 0 of type-255 rows |

The depth-1 frame is the `inventory-expansion` cache. Its summary records 782 of
3,970 candidate archives extracted at depth 1, with 381 type-0 rows above the
archive size cap. The cache contains 849 archive manifests after deduplication
of repeated `archives.jsonl` entries; 75 archives contain at least one type-255
row, and 65 contain ADAT rows.

The raw scan holds 923 ADAT rows across 75 archive copies. The population is
deduplicated by `(parent archive identity, row index)`: repeated copies of the
same parent archive are collapsed, giving 768 rows in 65 parent archives. The
payload digest is not the deduplication key. The committed inspector reports
`samples=768` for an input list built from this deduplicated set.

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
| ADAT-F07 | All 768 rows share a 16-byte common header: magic, a `u32` flags word at `+0x04`, a `u32` stream count at `+0x08` and a `u32` data offset at `+0x0C`. The flags word is `variant << 16 | 1` in 768/768 rows. The variant is `FF02` (124 rows), `FF21` (283), `FF25` (275) or `FF61` (86). | `BINARY`, `CROSS_SAMPLE` | Confirmed (packing and values) | Variant meaning is Unknown |
| ADAT-F08 | The `u32` at `+0x08` is a stream count, not a record count. It indexes the per-stream table: `u32[streams]` for `FF02`, `u16[streams]` for `FF21`, `FF25` and `FF61`. In `FF02` the record count is `sum(chunk_counts)` and ranges from 4 to 576 while the stream count ranges from 1 to 144. In `FF25` the stream count is 2 to 9 and the record count is 3 to 5. | `BINARY`, `CROSS_SAMPLE` | Confirmed (sample) | The meaning of a stream is not established beyond the table length |
| ADAT-F09 | The `u32` at `+0x0C` is the chunk-table end and the payload-relative data offset. It is 46 to 27,484, even, follows the variant table and precedes the stored size in 768/768 rows. The byte immediately before it is the last record's type byte: `A3` (608 rows), `BD` (117) or `76` (43). The byte at the offset begins the encoded stream. | `BINARY`, `CROSS_SAMPLE` | Confirmed (boundary and byte counts) | The encoded stream is not interpreted |
| ADAT-F10 | `FF21` and `FF25` place a non-decreasing `u16[streams]` table at `+0x10`. `FF21` has no decrease and no equal adjacent pair in 283/283 rows; 26 of those rows have a single entry. `FF25` permits equal adjacent entries in 36/275 rows. | `BINARY`, `CROSS_SAMPLE` | Confirmed (sample) | Table-entry meaning is Unknown |
| ADAT-F11 | `FF61` places a second `u32` payload-relative offset at `+0x10` and a non-decreasing `u16[streams]` table at `+0x14`. The second offset is greater than the data offset and smaller than the stored size in 86/86 rows; the preceding byte is `00` in 86/86 rows. | `BINARY`, `CROSS_SAMPLE` | Confirmed (offset); Probable (second data region) | Role of the second offset is not established |
| ADAT-F12 | `FF02` rows carry `u32[streams]` at `+0x10`. Each entry holds an identifier in the low 29 bits and a chunk count in the high 3 bits. The data offset is `0x10 + 4 * streams + 8 * sum(chunk_counts)` in 124/124 rows. | `BINARY`, `CROSS_SAMPLE` | Confirmed (arithmetic) | Identifier and chunk-count meanings beyond the arithmetic are Unknown |
| ADAT-F13 | Archive family changes one observed `FF02` relation only. The width-36 rows are 113 `audio.rpf` depth-1 rows; the width-44, width-60 and mixed rows are in the other family. `FF21`, `FF25` and `FF61` show no family-correlated layout difference. | `CROSS_SAMPLE` | Confirmed (sample) | Placement is provenance; the sample cannot separate payload subvariant from selection |
| ADAT-F14 | The evidence supports one ADAT format family with four header variants, not four unrelated formats. The common header and shared record grammar hold across all 768 rows. | `CROSS_SAMPLE` | Confirmed (sample) | No codec identity or field purpose is assigned |
| ADAT-F15 | The earlier 21-row structural observation is superseded by the 768-row header census. All 768 rows were read at least to the data offset; the 21 earlier rows were the only ones previously inspected beyond eight bytes. | `BINARY`, `CROSS_SAMPLE` | Confirmed (scope) | Full payloads were not reconstructed |
| ADAT-F16 | In the 644 rows with a `u16[streams]` table, every table is non-decreasing. No adjacent increase exceeds 5 (5 in `FF21`, 3 in `FF25`, 5 in `FF61`). The `u16` after the table is at least 2,045 (`FF21`), 381 (`FF25`) and 5,700 (`FF61`) above the last entry. | `BINARY`, `CROSS_SAMPLE` | Confirmed (observations) | Empirical bounds from one build; `FF02` (124 rows) has no `u16` table; a genuine increment above 5 would fail the table-length test and none occurs |
| ADAT-F17 | The earlier post-table gap is now decomposed. For `FF21`, `FF25` and `FF61` it consists of an `8 * streams + 4`-byte region followed by the 8-byte record run. The gap is even and its length is `8 * streams + 4 + 8 * records`. The earlier positive association with the stream count is consistent with this decomposition. | `BINARY`, `CROSS_SAMPLE` | Confirmed (layout); Unknown (region meaning) | The region is not interpreted |
| ADAT-F18 | The 8-byte record run ends exactly at `+0x0C` in 768/768 rows with a 0-byte remainder. No record has size zero; no record's `offset + size` exceeds the payload; no record points before the data offset. The last record's type byte equals the byte before `+0x0C` in 768/768 rows. | `BINARY`, `CROSS_SAMPLE`, `SYNTHETIC` | Confirmed (768/768) | Synthetic tests validate the tool, not the native format |
| ADAT-F19 | A record is a little-endian 64-bit word: type in bits 63..56, size in bits 55..28 and payload-relative offset in bits 27..0. Record type bytes are `0x36`, `0x48`, `0x55`, `0x5C`, `0x76`, `0xA3`, `0xB2` and `0xBD`. `FF25` begins with `0x48` in 275/275 rows; `FF02` begins with `0x36` in 124/124 rows. No type byte is assigned a stream or codec meaning. | `BINARY`, `CROSS_SAMPLE` | Confirmed (fields and byte values) | Type meanings are Unknown |
| ADAT-F20 | The earlier `FF02` record-width heuristic explains 123 of 124 rows. Width 36 covers 113 `audio.rpf` rows, 44 covers 4 other rows and 60 covers 6 other rows. The remaining other row has mixed chunk counts, an integer width of 39 and no integral width; `ADAT-F12` explains it. | `BINARY`, `CROSS_SAMPLE` | Confirmed (sample) | The width relation holds only when every stream has the same chunk count |
| ADAT-F21 | `0x76` records carry a codec byte at `+0x1C` and a rate field at `+0x08`. The codec byte is `0x0B` in 15,038 descriptors and `0x02` in 227; no other value occurs. The 15,038 are 14,665 `0x76` records and 373 `0x48` entries. | `BINARY`, `CROSS_SAMPLE` | Confirmed (byte values and positions) | The codec byte is not assigned an identity; no decoder was run |
| ADAT-F22 | Every `0x0B` `0x55` record is a multiple of 2,048 bytes. Over 14,940 records and 505,723 blocks, 502,373 data blocks parse as `[u16 length][packet]`; a zero length terminates a block, the remainder is zero, and no length crosses the block end. There are 0 framing violations and 0 exceptions. The FF02, FF21 and FF61 variants have no metadata blocks. | `BINARY`, `CROSS_SAMPLE`, `SYNTHETIC` | Confirmed (framing) | The packets are not decoded; the framing does not identify a codec |
| ADAT-F23 | The 4,961,453 `0x0B` packets carry 951,673,715 payload bytes and 66,258,537 padding bytes. Packet lengths range from 3 to 480 bytes; the most common are 320, 80, 50, 160 and 240. The first packet byte has eight values, led by `0xFC` (2,463,483) and `0xF8` (1,276,418). | `BINARY`, `CROSS_SAMPLE` | Confirmed (values) | The first byte is not mapped to a frame duration without a decoder |
| ADAT-F24 | The `0x48` record is `12 + 16 * count` bytes: `u32` page count, `u32` page stride in bytes, `u32` sub-stream count, then 16-byte entries. The size relation holds in 275/275 records. `FF25` divides its one `0x55` record into pages of that stride. The block classes sum to 505,723: 502,373 data, 1,768 sentinel, 26 other metadata and 1,556 zero. The page count equals the field in 275/275 rows. The classifier treats every leading non-data, non-zero block as metadata; a corrupted first data block would be counted as metadata. | `BINARY`, `CROSS_SAMPLE`, `SYNTHETIC` | Confirmed (layout and counts) | The entry `unknown` and `decoded` fields are not interpreted. A 24-byte entry does not fit the observed sizes |
| ADAT-F25 | The rate field is the low `u16` at `0x76 +0x08`, not the descriptor's lowest `u16`. It is 48,000 in 14,625 records and 12,000 (30), 22,050 (8) or 11,025 (2) in 40 records from 14 rows in two depth-1 archives. `0x48` entries carry the rate in the high `u16` of the third entry word and are 48,000 in 373/373 entries. | `BINARY`, `CROSS_SAMPLE` | Confirmed (field position and values) | The decode rate and the meaning of the 40 non-48 kHz records are Unknown |
| ADAT-F26 | For codec byte `0x02`, the `0x55` size equals `4 * declared` in 227/227 records in 43 rows, where `declared` is the `0x76` `u32` at `+0x00`. | `BINARY`, `CROSS_SAMPLE` | Confirmed (size relation) | No sample type is established; the data is not decoded |
| ADAT-F27 | `0xA3` tables start at 0 and are non-decreasing in 14,940/14,940 paired `0x0B` streams. `FF02`, `FF21` and `FF61` have one entry per 2,048-byte block plus the initial 0 (14,665/14,665); `FF25` has one entry per page (275/275). The 227 `0x02` streams have no `0xA3` record; they occur in 43 `FF21` rows that also carry `0x0B` streams with `A3` tables. The entry width is 4 bytes. | `BINARY`, `CROSS_SAMPLE`, `SYNTHETIC` | Probable (position table); Confirmed (counts) | The unit and the terminal relation to decoded samples are Unknown |
| ADAT-F28 | No descriptor in the 768 rows carries codec byte `0x05` and no rate field is 32,000. The 15,265 codec positions are `0x0B` or `0x02`. No field or codec byte in the observed descriptors selects a stream for the second named codec hypothesis. | `BINARY`, `CROSS_SAMPLE` | Rejected (H2); Unknown (second codec selector) | Absence in this depth-1 sample does not rule out other archives or builds |

## Variant table detail

| Variant | Family split | Streams | Data offset range | Layout |
| --- | --- | ---: | ---: | --- |
| `FF02` | 113 `audio.rpf` / 11 other | 1 to 144 | 52 to 5,200 | `u32[streams]` from `+0x10`; record run follows |
| `FF21` | 276 / 7 | 1 to 231 | 46 to 9,690 | `u16[streams]` at `+0x10`; `8 * streams + 4` bytes; record run |
| `FF25` | 256 / 19 | 2 to 9 | 64 to 134 | `u16[streams]` at `+0x10`; `8 * streams + 4` bytes; record run |
| `FF61` | 84 / 2 | 6 to 674 | 228 to 27,484 | `u32` offset at `+0x10`; `u16[streams]` at `+0x14`; `8 * streams + 4` bytes; record run |

The position gap between the end of the `u16[streams]` table and the data offset
is not independent of the stream count. `ADAT-F17` covers the 644 rows with such
a table. The gap is an `8 * streams + 4`-byte region plus the 8-byte record run;
the region itself remains uninterpreted.

| Variant | Rows | Gap range | Median | Pearson r | Spearman rho |
| --- | ---: | ---: | ---: | ---: | ---: |
| `FF21` | 283 | 28 to 9,212 | 604 | 0.996 | 0.997 |
| `FF25` | 275 | 44 to 100 | 44 | 0.895 | 0.627 |
| `FF61` | 86 | 196 to 26,116 | 1,540 | 0.9999 | 0.9998 |

The gap is even in all 644 rows. All three variant correlations are positive.
The gap is not a fixed function of the stream count: the 26 `FF21` rows with
stream count 1 take four gap values (28, 36, 44 and 52), and a least-squares fit
of gap on stream count leaves residual standard deviations of 110 (`FF21`), 4.1 (`FF25`) and 44
(`FF61`) bytes. Counterexamples: none to the positive association.
Exclusions: the 124 `FF02` rows have a record region instead of a `u16`
table, so the gap is undefined there; the 18 zlib type-255 rows are outside
the 768. The `8 * streams + 4`-byte region inside the gap remains
uninterpreted; no size role is assigned to it.

## Table-end test

`ADAT-F16` covers every deduplicated ADAT row whose variant carries a
`u16[streams]` table: 283 `FF21`, 275 `FF25` and 86 `FF61`, 644 rows in total.
The table starts at `+0x10` for `FF21` and `FF25`, and at `+0x14` for `FF61`.
The 644 rows are the whole ADAT table population in the extracted depth-1
sample, not a subsample.

| Variant | Rows | Streams 1 | Adjacent pairs | No decrease | Equal pairs | Max increase | Min post-table delta |
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

## Atypical rate records

The 40 `0x76` records whose rate field is not 48,000 occur in 14 rows in two
depth-1 archives. Stream index is the zero-based `0x55` record index within the
row. Every record is codec byte `0x0B`.

| Archive | Row | Stream | Rate | Declared | Size |
| --- | ---: | ---: | ---: | ---: | ---: |
| `d1:audio.rpf:72` | 51 | 0 | 11,025 | 158,651 | 14,336 |
| `d1:audio.rpf:72` | 51 | 1 | 11,025 | 158,484 | 14,336 |
| `d1:audio.rpf:72` | 51 | 3 | 22,050 | 55,125 | 6,144 |
| `d1:audio.rpf:72` | 51 | 18 | 22,050 | 54,780 | 6,144 |
| `d1:audio.rpf:72` | 78 | 0 | 22,050 | 260,460 | 24,576 |
| `d1:audio.rpf:72` | 78 | 13 | 22,050 | 152,972 | 14,336 |
| `d1:audio.rpf:72` | 92 | 5 | 22,050 | 97,182 | 8,192 |
| `d1:audio.rpf:72` | 92 | 35 | 22,050 | 97,182 | 8,192 |
| `d1:audio.rpf:72` | 95 | 1 | 22,050 | 97,182 | 8,192 |
| `d1:audio.rpf:72` | 95 | 51 | 22,050 | 97,182 | 8,192 |
| `d1:audio.rpf:77` | 0 | 0 | 12,000 | 61,537 | 6,144 |
| `d1:audio.rpf:77` | 1 | 0 | 12,000 | 82,862 | 8,192 |
| `d1:audio.rpf:77` | 2 | 0 | 12,000 | 76,011 | 8,192 |
| `d1:audio.rpf:77` | 3 | 0 | 12,000 | 19,514 | 2,048 |
| `d1:audio.rpf:77` | 3 | 1 | 12,000 | 16,001 | 2,048 |
| `d1:audio.rpf:77` | 3 | 2 | 12,000 | 21,154 | 4,096 |
| `d1:audio.rpf:77` | 3 | 3 | 12,000 | 23,202 | 4,096 |
| `d1:audio.rpf:77` | 3 | 4 | 12,000 | 13,989 | 2,048 |
| `d1:audio.rpf:77` | 4 | 0 | 12,000 | 74,316 | 8,192 |
| `d1:audio.rpf:77` | 4 | 1 | 12,000 | 4,139 | 2,048 |
| `d1:audio.rpf:77` | 5 | 0 | 12,000 | 76,011 | 8,192 |
| `d1:audio.rpf:77` | 6 | 0 | 12,000 | 3,807 | 2,048 |
| `d1:audio.rpf:77` | 6 | 1 | 12,000 | 3,807 | 2,048 |
| `d1:audio.rpf:77` | 6 | 2 | 12,000 | 3,807 | 2,048 |
| `d1:audio.rpf:77` | 6 | 3 | 12,000 | 3,807 | 2,048 |
| `d1:audio.rpf:77` | 6 | 4 | 12,000 | 3,807 | 2,048 |
| `d1:audio.rpf:77` | 6 | 5 | 12,000 | 3,807 | 2,048 |
| `d1:audio.rpf:77` | 6 | 6 | 12,000 | 3,807 | 2,048 |
| `d1:audio.rpf:77` | 6 | 7 | 12,000 | 3,807 | 2,048 |
| `d1:audio.rpf:77` | 6 | 8 | 12,000 | 3,807 | 2,048 |
| `d1:audio.rpf:77` | 6 | 9 | 12,000 | 3,807 | 2,048 |
| `d1:audio.rpf:77` | 6 | 10 | 12,000 | 3,807 | 2,048 |
| `d1:audio.rpf:77` | 6 | 11 | 12,000 | 3,807 | 2,048 |
| `d1:audio.rpf:77` | 6 | 12 | 12,000 | 3,807 | 2,048 |
| `d1:audio.rpf:77` | 6 | 13 | 12,000 | 3,807 | 2,048 |
| `d1:audio.rpf:77` | 6 | 14 | 12,000 | 3,807 | 2,048 |
| `d1:audio.rpf:77` | 6 | 15 | 12,000 | 3,807 | 2,048 |
| `d1:audio.rpf:77` | 7 | 0 | 12,000 | 76,011 | 8,192 |
| `d1:audio.rpf:77` | 8 | 0 | 12,000 | 76,011 | 8,192 |
| `d1:audio.rpf:77` | 9 | 0 | 12,000 | 40,847 | 4,096 |

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

### Iteration 10 header packing and chunk-record model

The earlier findings read `+0x04` as a `u16` version and `+0x06` as a `u16`
variant word, described `+0x08` as a count whose unit depended on the variant,
left the post-table gap uninterpreted, and used a fixed record width for
`FF02`.

The 768-row re-read changes those readings:

- `+0x04` is one little-endian `u32` flags word: `variant << 16 | 1` in 768/768
  rows. The earlier two `u16` fields are the low and high halves.
- `+0x08` is a stream count. It indexes the per-stream table and does not count
  chunk records. In `FF02` the record count is `sum(chunk_counts)`; in `FF25`
  the stream count is 2 to 9 while the record count is 3 to 5.
- `+0x0C` is the chunk-table end and data offset. The byte before it is the last
  record's type byte.
- The trailing gap is an aligned run of 8-byte records ending exactly at
  `+0x0C`. A record is a little-endian 64-bit word with a type byte in bits
  63..56, a size in bits 55..28 and an offset in bits 27..0. All 768 rows pass
  the end, size and extent checks.
- `FF02` uses `data_offset = 0x10 + 4 * streams + 8 * sum(chunk_counts)` in
  124/124 rows. The fixed-width relation explains 123 rows and fails on the one
  row with mixed chunk counts.
- The earlier post-table gap association is decomposed into an
  `8 * streams + 4`-byte region and the record run. The region remains
  uninterpreted.

The four variants remain one format family. No codec, AWC identity or packet
framing is assigned.

### Iteration 11 descriptor and framing model

The earlier index left every record type and the encoded stream uninterpreted.
The 768-row re-read adds a structural stream model without assigning a codec:

- `0x76` records carry a declared count, a rate/flags word and a codec byte at
  `+0x1C`. `0x48` records carry a page count, a page stride, a sub-stream count
  and 16-byte entries. The earlier 24-byte entry hypothesis is rejected.
- Every `0x0B` `0x55` record is block-framed: 505,723 blocks, 4,961,453
  packets, no length crossing a block and no non-zero padding.
- `FF25` adds pages from the `0x48` stride. The page count matches the `0x48`
  field in 275/275 rows and every page block is classified.
- `0x02` records satisfy `size == 4 * declared` in 227/227 records.
- The rate field is `0x76 +0x08` low `u16`, not the descriptor's lowest `u16`.
- `0xA3` is a non-decreasing position table, with one entry per block for the
  three non-music variants and one per page for `FF25`. Its unit is Unknown.
- No `0x05` descriptor and no 32 kHz rate occur. The `0x05` hypothesis is
  rejected for this population and no selector for the second codec hypothesis
  is established.

No decoder was installed or run. The framing result does not establish a codec
identity or a decoded sample count.

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

For the table-end test, read `u16[streams]` at `+0x10` (`FF21`, `FF25`) or
`+0x14` (`FF61`), compare adjacent entries, and read the next `u16`. For the
record run, use `tools/adat/adat_inspect.py`. Add `--framing` to walk the
`0x55` blocks, classify the `FF25` pages and count packets. For the population
aggregate, write the deduplicated sample paths to an input list and run:

```text
python tools/adat/adat_inspect.py --input-list <WORK>/adat-inputs.txt --summary --json
```

The summary reproduces `samples=768`, 14,940 `0x0B` streams, 14,665 `0x76`
records, 373 `0x48` entries, 227 `0x02` records, 505,723 blocks split into
502,373 data, 1,768 sentinel, 26 other metadata and 1,556 zero, and the `A3`
count relations. For the post-table gap, subtract the table end from the
`+0x0C` offset. For the byte boundary, compare the bytes at `offset - 1` and
`offset`.

## Limits

- One build and one local archive set.
- The depth-1 frame is a selection, not a census; 381 type-0 rows were above the
  archive size cap.
- The 18 zlib type-255 rows in one `audio.rpf` archive were not decoded.
- The region between the variant table and the data offset is not interpreted.
- No executable path was traced and no decoder was run. The framing and codec
  bytes are container observations; no codec identity, decoded sample count or
  playback result is established.
- The `0x48` entry fields, the `0x76` declared count and the `0xA3` unit are not
  mapped to decoded samples.
