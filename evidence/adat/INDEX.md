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
| ADAT-F06 | `ADAT` begins 768 stored type-255 payloads in 65 depth-1 archives under four top-level archives. The rows split into 729 rows in 59 `audio.rpf` archives and 39 rows in six archives under three other top-level archives. | Authenticated manifests, cached archive bytes | Confirmed (sample) | Depth-1 sample only; 18 zlib type-255 rows in one `audio.rpf` archive are excluded |
| ADAT-F07 | All 768 rows share a 16-byte common header: magic, `u16` version 1, `u16` variant word, `u32` count and `u32` data offset. The variant word is one of `FF02` (124 rows), `FF21` (283), `FF25` (275) and `FF61` (86). | Payload heads | Confirmed (values) | Variant-word meaning is Unknown |
| ADAT-F08 | The `u32` at `+0x08` is a count from 1 to 674. For `FF21`, `FF25` and `FF61` it equals the number of `u16` entries in the table at `+0x10` or `+0x14` in 644/644 rows. For `FF02` it equals the number of fixed-width records in 123/124 rows. | Payload heads | Confirmed (boundary) | One `FF02` row has a non-integral record width |
| ADAT-F09 | The `u32` at `+0x0C` is a payload-relative data offset from 46 to 27,484. It is even, follows the variant table and precedes the stored size in 768/768 rows. The byte before it is `A3` (608 rows), `BD` (117) or `76` (43). | Payload heads | Confirmed (boundary) | The table before the offset is only partly interpreted |
| ADAT-F10 | `FF21` and `FF25` place a non-decreasing `u16[count]` table at `+0x10`. `FF21` is strictly increasing in 283/283 rows; `FF25` permits equal adjacent entries in 36/275 rows. | Payload heads | Confirmed (sample) | Table-entry meaning is Unknown |
| ADAT-F11 | `FF61` places a second `u32` payload-relative offset at `+0x10` and a non-decreasing `u16[count]` table at `+0x14`. The second offset is greater than the data offset and smaller than the stored size in 86/86 rows; the preceding byte is `00` in 86/86 rows. | Payload heads | Confirmed (offset); Probable (second data region) | Role of the second offset is not established |
| ADAT-F12 | `FF02` rows carry a record region instead of a `u16` index table. The data offset equals `0x10 + width * count`; width is 36 bytes in 113/113 `audio.rpf` rows and 44 or 60 bytes in 10/11 other rows. | Payload heads | Confirmed (arithmetic) | One other row has no integral width; record contents are not interpreted |
| ADAT-F13 | Archive family changes one header relation only. `u32@+0x0C = 0x10 + 36 * u32@+0x08` holds for 113/113 `audio.rpf` `FF02` rows and 0/11 other `FF02` rows. `FF21`, `FF25` and `FF61` show no family-correlated layout difference. | Payload heads | Confirmed (sample) | Placement is provenance; the sample cannot separate payload subvariant from selection |
| ADAT-F14 | The evidence supports one ADAT format family with four header variants, not four unrelated formats. The common header and shared count/offset semantics hold across all 768 rows. | Payload heads | Confirmed (sample) | No codec identity or field purpose is assigned |
| ADAT-F15 | The earlier 21-row structural observation is superseded by the 768-row header census. All 768 rows were read at least to the data offset; the 21 earlier rows were the only ones previously inspected beyond eight bytes. | Cached archive bytes | Confirmed (scope) | Full payloads were not reconstructed |

## Variant table detail

| Variant | Family split | Count range | Data offset range | Layout |
| --- | --- | ---: | ---: | --- |
| `FF02` | 113 `audio.rpf` / 11 other | 1 to 144 | 52 to 5,200 | record region from `+0x10` |
| `FF21` | 276 / 7 | 1 to 231 | 46 to 9,690 | `u16[count]` at `+0x10` |
| `FF25` | 256 / 19 | 2 to 9 | 64 to 134 | `u16[count]` at `+0x10` |
| `FF61` | 84 / 2 | 6 to 674 | 228 to 27,484 | `u32` offset at `+0x10`; `u16[count]` at `+0x14` |

The gap between the last table entry and the data offset varies independently of
the count. It remains uninterpreted; no size role is assigned to it.

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

## Limits

- One build and one local archive set.
- The depth-1 frame is a selection, not a census; 381 type-0 rows were above the
  archive size cap.
- The 18 zlib type-255 rows in one `audio.rpf` archive were not decoded.
- The region between the variant table and the data offset is not interpreted.
- No executable path was traced. Field meaning beyond count and offset is
  Unknown, and no codec identity is assigned.
