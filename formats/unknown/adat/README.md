# ADAT

`ADAT` (`41 44 41 54`) at offset 0 marks stored payloads of type 255 in depth-1
archives. The current depth-1 scan finds 768 such rows in 65 archives under four
top-level archives: 729 rows in 59 of the 60 scanned depth-1 archives reached
from `audio.rpf`, and 39 rows in six depth-1 archives reached from
`shared_minigame000.rpf`, `story000.rpf` and `story000_restofworld.rpf`.

The archive names are provenance, not evidence of purpose. The magic occurs only
at payload offset 0; the substring inside `METADATA` is not a match.

## Population

The scan covers depth 1 only. No top-level row carries `ADAT` in the stored-byte
census of 6,534 untransformed top-level rows, so the population is 0 top-level
and 768 depth-1 rows.

| Family | Rows | Archives | Stored bytes | Variant words at `+0x06` |
| --- | ---: | ---: | --- | --- |
| Depth-1 under `audio.rpf` | 729 | 59 | 4,224 to 51,693,440 | all four |
| Depth-1 under three other top-level archives | 39 | 6 | 41,728 to 6,187,200 | all four |
| Top-level | 0 | 0 | none | none |

The 60th scanned `audio.rpf` archive holds 18 type-255 rows whose stored bytes
begin a zlib stream (`78 DA`). They do not begin `ADAT` and are excluded from the
768. Type ID 255 also carries `FORC` and zlib payloads in other depth-1 archives,
so the type ID is not an identifier.

Size distribution of the 768 rows:

| Stored size | Rows |
| --- | ---: |
| under 16 KiB | 17 |
| 16 to 64 KiB | 54 |
| 64 to 256 KiB | 198 |
| 256 KiB to 1 MiB | 262 |
| 1 to 4 MiB | 188 |
| 4 to 16 MiB | 42 |
| 16 to 64 MiB | 7 |
| 64 MiB or more | 0 |

All 768 rows have no chunk table, mode 0 and no payload transform. 659 stored
sizes equal the logical size; 109 add an even amount of 2 to 14 bytes. The
smallest row is 4,224 bytes; the largest is 51,693,440 bytes.

## Common header

Every payload begins with the same six bytes `41 44 41 54 01 00`. The first 16
bytes form a common header; field support is counted over all 768 rows.

| Offset | Width | Observation | Support | Status |
| --- | --- | --- | ---: | --- |
| `+0x00` | 4 | `41 44 41 54` | 768/768 | Confirmed |
| `+0x04` | `u16` | version, always 1 | 768/768 | Confirmed |
| `+0x06` | `u16` | variant word, one of `FF02`, `FF21`, `FF25`, `FF61` | 768/768 | Confirmed; meaning Unknown |
| `+0x08` | `u32` | count from 1 to 674 | 768/768 | Confirmed as a count; unit is variant-specific |
| `+0x0C` | `u32` | data offset from 46 to 27,484 | 768/768 | Confirmed as a payload-relative byte offset |

The offset at `+0x0C` is even in all 768 rows and lies after the variant table
and before the stored size. The byte immediately before the offset is `A3` in
608 rows, `BD` in 117 and `76` in 43. Bytes at the offset begin the encoded
stream; the byte distribution changes there in the inspected samples.

Variant counts:

| Variant word | Rows | Family split | Stored size | Count range | Data offset |
| --- | ---: | --- | --- | ---: | ---: |
| `FF02` | 124 | 113 / 11 | 12,464 to 6,043,264 | 1 to 144 | 52 to 5,200 |
| `FF21` | 283 | 276 / 7 | 4,224 to 3,262,464 | 1 to 231 | 46 to 9,690 |
| `FF25` | 275 | 256 / 19 | 34,912 to 51,693,440 | 2 to 9 | 64 to 134 |
| `FF61` | 86 | 84 / 2 | 12,768 to 4,016,320 | 6 to 674 | 228 to 27,484 |

The family split is `audio.rpf` depth-1 rows / other depth-1 rows.

## Variant headers

The common header is followed by a variant-specific table. The count at `+0x08`
predicts the table length; the offset at `+0x0C` follows the table.

| Variant | Table layout | Support | Counterexamples |
| --- | --- | ---: | --- |
| `FF21` | non-decreasing `u16[count]` at `+0x10` | 283/283 | none |
| `FF25` | non-decreasing `u16[count]` at `+0x10` | 275/275 | none |
| `FF61` | `u32` second offset at `+0x10`; non-decreasing `u16[count]` at `+0x14` | 86/86 | none |
| `FF02` | `u16[count]` table is absent; a record region of `count` fixed-width records follows `+0x10` | 123/124 use a fixed width | one row at 138,736 bytes |

For `FF21`, `FF25` and `FF61`, the table length test uses the small increment
between adjacent entries. The entries increase by at most 5; the value after the
table jumps by at least 2,045 in `FF21`, 381 in `FF25` and 5,700 in `FF61`.
`FF25` permits equal adjacent entries in 36 rows; `FF21` and `FF61` are strictly
increasing in the sample.

For `FF61`, the `u32` at `+0x10` is a second payload-relative offset. It is
greater than the `+0x0C` offset and smaller than the stored size in all 86 rows.
The byte before it is `00` in all 86 rows, and its target begins a second
encoded region. Its role is Probable; no field name is assigned.

For `FF02`, the record width is explicit in 123 of 124 rows:

| Record width | Rows | Family |
| ---: | ---: | --- |
| 36 bytes | 113 | all `audio.rpf` depth-1 rows |
| 44 bytes | 4 | other depth-1 rows |
| 60 bytes | 6 | other depth-1 rows |
| not integral | 1 | other depth-1 rows |

In the fixed-width rows, `u32@+0x0C = 0x10 + width * u32@+0x08`. The single
non-integral row still has a valid data offset; only the fixed-width relation
fails.

## One format or several

The 768 rows share the magic, the version, the 16-byte header layout and the
count/offset semantics. The four values at `+0x06` select table layouts, not
independent signatures, so the evidence supports one format family with four
header variants. It does not support four unrelated formats.

Archive family changes only one observed header relation:

- `FF02` rows with `u32@+0x0C = 0x10 + 36 * u32@+0x08`: 113/113 `audio.rpf`
  rows, 0/11 other rows.
- `FF02` rows with a different record width: 0/113 `audio.rpf` rows, 10/11 other
  rows, plus one non-integral row.

No other family-correlated header difference was found. `FF21`, `FF25` and
`FF61` use the same table positions and count relation in both families. Archive
placement is provenance, so the predicate is stated over header arithmetic only.
The sample cannot decide whether the `FF02` split is a payload subvariant or a
placement-correlated selection.

## Identification

Identification MUST use the payload bytes. `ADAT` at offset 0 identifies the
signature; the type ID and archive name do not. The variant word at `+0x06` MUST
be recorded with the signature, because it selects the table layout.

## Limits

- One build and one local archive set.
- The depth-1 scan is a sample: 782 of 3,970 candidate archives were extracted,
  and 381 type-0 rows exceeded the archive size cap. The 768 rows are not a
  complete census of the build.
- The 18 zlib type-255 rows in one `audio.rpf` archive were not decoded, so
  whether they also begin `ADAT` is Unknown.
- The region between the variant table and the data offset is not interpreted
  beyond its boundaries and the `FF61` second offset.
- No executable path was traced. Field roles beyond count and offset are
  Unknown, and no codec identity is assigned.

Evidence: [evidence/adat/INDEX.md](../../../evidence/adat/INDEX.md).
