# ADAT

`ADAT` (`41 44 41 54`) at offset 0 marks stored payloads of type 255 in depth-1
archives. The current depth-1 scan finds 768 rows in 65 parent archives under
four top-level archives: 729 rows in 59 of the 60 scanned depth-1 archives
reached from `audio.rpf`, and 39 rows in six depth-1 archives reached from
`shared_minigame000.rpf`, `story000.rpf` and `story000_restofworld.rpf`. The 768
rows are the result of collapsing 923 extracted ADAT rows by `(parent archive
identity, row index)`; each parent/row pair is counted once. The raw inputs and
the collapsed rows both span 65 distinct parent archives.

The archive names are provenance, not evidence of purpose. The magic occurs only
at payload offset 0; the substring inside `METADATA` is not a match.

## Population

The scan covers depth 1 only. No `ADAT` was found at offset 0 in the 6,079
inspected untransformed top-level rows. The remaining 455 top-level rows behind
the payload transform were not inspected, so the population is 0 confirmed
top-level rows and 768 depth-1 rows.

| Family | Rows | Archives | Stored bytes | Variant words |
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
| `+0x04` | `u32` | flags: low 16 bits are version 1; high 16 bits are the variant word | 768/768 | Confirmed (packing); variant meaning Unknown |
| `+0x08` | `u32` | stream count, 1 to 674 | 768/768 | Confirmed as the per-stream table count |
| `+0x0C` | `u32` | chunk-table end and data offset, 46 to 27,484 | 768/768 | Confirmed |

The packing is `flags == variant << 16 | 1` in every row. The earlier document
split `+0x04` and `+0x06` into a `u16` version and a `u16` variant; the bytes are
the same, read as one `u32`.

| Flags | Variant | Rows | Streams | Data offset | Record count |
| --- | --- | ---: | ---: | ---: | ---: |
| `0xFF020001` | `FF02` | 124 | 1 to 144 | 52 to 5,200 | 4 to 576 |
| `0xFF210001` | `FF21` | 283 | 1 to 231 | 46 to 9,690 | 2 to 920 |
| `0xFF250001` | `FF25` | 275 | 2 to 9 | 64 to 134 | 3 to 5 |
| `0xFF610001` | `FF61` | 86 | 6 to 674 | 228 to 27,484 | 18 to 2,590 |

The data offset is even in all 768 rows and lies after the variant tables and
before the stored size. The byte immediately before the offset is the last
chunk record's type byte: `A3` in 608 rows, `BD` in 117 and `76` in 43. The byte
at the offset begins the encoded stream.

## Per-stream tables

The common header is followed by a per-stream table selected by the variant.

| Variant | Per-stream table | Record run start | Support |
| --- | --- | ---: | ---: |
| `FF02` | `u32[streams]` at `+0x10` | `+0x10 + 4 * streams` | 124/124 |
| `FF21` | `u16[streams]` at `+0x10`, then an `8 * streams + 4`-byte region | `+0x14 + 10 * streams` | 283/283 |
| `FF25` | `u16[streams]` at `+0x10`, then an `8 * streams + 4`-byte region | `+0x14 + 10 * streams` | 275/275 |
| `FF61` | `u32` second offset at `+0x10`, `u16[streams]` at `+0x14`, then an `8 * streams + 4`-byte region | `+0x18 + 10 * streams` | 86/86 |

For `FF21`, `FF25` and `FF61`, the bytes between the `u16` table and the record
run are `8 * streams + 4` bytes. Their content and meaning are Unknown. The
`u16` table is non-decreasing in the 644 rows that carry it; no adjacent
increase exceeds 5 and the first post-table `u16` is far above the last entry
(`ADAT-F16`).

For `FF02`, each `u32` at `+0x10` has two fields: an identifier in the low 29
bits and a chunk count in the high 3 bits. The record run then holds
`sum(chunk_counts)` records. This gives the count formula below.

For `FF61`, the `u32` at `+0x10` is a second payload-relative offset. It is
greater than the data offset and smaller than the stored size in 86/86 rows. The
byte before it is `00` in all 86 rows, and its target begins a second encoded
region. Its role is Probable; no field name is assigned.

## Chunk records

The trailing part of the table is a run of 8-byte records ending exactly at the
data offset. Each record is a little-endian 64-bit word:

| Bits | Field | Observation |
| --- | --- | --- |
| 63 to 56 | type byte | one of the values in the table below |
| 55 to 28 | size | nonzero in all records |
| 27 to 0 | payload-relative offset | at or after the data offset |

The byte immediately before `+0x0C` is the last record's type byte. The record
run is aligned to the data offset: `(data_offset - record_start) % 8 == 0`.

Record-run checks over all 768 rows:

| Check | Result |
| --- | --- |
| Record run ends exactly at `+0x0C` | 768/768 |
| Remainder after the last record | 0 bytes, 768/768 |
| Records with size zero | 0 |
| Records with `offset + size` past the payload | 0 |
| Records pointing before the data offset | 0 |
| Last record type equals the byte before `+0x0C` | 768/768 |

The extent check uses the stored payload length. Record type bytes by variant:

| Variant | Type bytes (record count) |
| --- | --- |
| `FF02` | `0x36` 2,464; `0x55` 2,464; `0x76` 2,464; `0xA3` 2,464; `0x5C` 161; `0xB2` 21; `0xBD` 21 |
| `FF21` | `0x36` 6,073; `0x55` 8,396; `0x76` 8,396; `0xA3` 8,169; `0x5C` 6; `0xBD` 14 |
| `FF25` | `0x48` 275; `0x55` 275; `0xA3` 275; `0xBD` 111 |
| `FF61` | `0x36` 3,755; `0x55` 4,032; `0x76` 4,032; `0xA3` 4,032; `0x5C` 17; `0xBD` 23 |

First and last record types:

| Variant | First type | Last type |
| --- | --- | --- |
| `FF02` | `0x36` 124/124 | `0xA3` 118, `0xBD` 6 |
| `FF21` | `0x36` 240, `0x55` 43 | `0x76` 43, `0xA3` 238, `0xBD` 2 |
| `FF25` | `0x48` 275/275 | `0xA3` 167, `0xBD` 108 |
| `FF61` | `0x36` 84, `0x55` 2 | `0xA3` 85, `0xBD` 1 |

The type bytes are structural observations. No type byte is assigned a stream,
chunk or codec meaning.

## Stream descriptors

Two record types carry the per-stream descriptor. They do not establish a codec
name; they carry a codec byte and a rate field.

| Record | Offset | Field | Support |
| --- | --- | --- | ---: |
| `0x76` | `+0x00` | `u32` declared count | 14,665/14,665 |
| `0x76` | `+0x08` | low `u16` rate, high `u16` flags | 14,665/14,665 |
| `0x76` | `+0x1C` | codec byte in the first byte of the last `u32` | 14,665/14,665 |
| `0x48` | `+0x00` | `u32` page count | 275/275 |
| `0x48` | `+0x04` | `u32` page stride in bytes, a multiple of 2,048 | 275/275 |
| `0x48` | `+0x08` | `u32` sub-stream count | 275/275 |
| `0x48` | `+0x0C` | `sub-stream count` entries of 16 bytes | 275/275 |

A `0x76` record is 32 bytes. A `0x48` record is `12 + 16 * count` bytes; the
size relation holds in 275/275 records. A 24-byte per-sub-stream header does
not fit the observed sizes; the entry is 16 bytes.

```text
0x48 entry: [u32 unknown][u32 decoded][u32 rate_flags][u16 codec_word][u16 flags]
            rate = rate_flags >> 16, rate flags = rate_flags & 0xFFFF
            codec byte = low byte of codec_word
```

`FF25` carries one `0x48` record with one to eight entries and one `0x55`
record shared by those entries. `FF02`, `FF21` and `FF61` pair one `0x76` with
one `0x55` in record order.

Codec byte counts over the 768 rows:

| Codec byte | Descriptors | `0x55` records | Rows |
| --- | ---: | ---: | ---: |
| `0x0B` | 15,038 | 14,940 | 725 |
| `0x02` | 227 | 227 | 43 |
| any other | 0 | 0 | 0 |

The 725 `0x0B` rows and 43 `0x02` rows are disjoint; no row carries both
codec bytes. The 15,038 `0x0B` descriptors are 14,665 `0x76` records plus 373
`0x48` entries. All 373 entries carry codec byte `0x0B` and rate 48,000; no
record mixes codecs or rates. The codec byte is not assigned an identity.

| Candidate | Streams | Disposition |
| --- | ---: | --- |
| Codec byte `0x0B` | 14,940 | Framing validated; decode not run (no decoder) |
| Codec byte `0x02` | 227 | Size relation validated; decode not run (no decoder) |
| Codec byte `0x05` | 0 | `no-such-codec-byte` |
| Second named codec hypothesis | 0 | `selector-undefined` |

## Packet framing

The `0x55` records carry the encoded stream. For every `0x0B` `0x55` record,
the size is a multiple of 2,048 bytes and the data is a run of 2,048-byte
blocks. Over the 14,940 `0x0B` records:

| Measure | Value |
| --- | ---: |
| Blocks | 505,723 |
| Data blocks | 502,373 |
| Sentinel blocks | 1,768 |
| Other metadata blocks | 26 |
| Zero blocks | 1,556 |
| Unknown blocks | 0 |
| Packets | 4,961,453 |
| Packet payload bytes | 951,673,715 |
| Padding bytes | 66,258,537 |
| Framing violations | 0 |
| Structure exceptions | 0 |

A data block is a sequence of `[u16 length][packet]`. A zero length terminates
the block and the rest of the block is zero. A block that ends exactly at 2,048
bytes has no terminator. No length crosses the block end and no non-zero byte
follows a terminator. Packet lengths range from 3 to 480 bytes; the most common
are 320 (2,233,972 packets), 80 (730,611), 50 (474,247), 160 (249,660) and 240
(189,639). The first packet byte has eight observed values:

| First byte | Packets |
| --- | ---: |
| `0xFC` | 2,463,483 |
| `0xF8` | 1,276,418 |
| `0x78` | 821,494 |
| `0xD8` | 178,792 |
| `0x68` | 156,359 |
| `0xB8` | 39,528 |
| `0x48` | 20,314 |
| `0xDC` | 5,065 |

The `FF02`, `FF21` and `FF61` variants have no metadata blocks. Every one of
their `0x55` blocks is a data block. `FF25` divides the `0x55` record into pages
of the `0x48` page stride. A page starts with one sentinel block (`u32`
`0xFFFFFFFF`). Twenty-six pages also carry one other metadata block; the other
1,742 pages carry none. Data blocks follow, then zero blocks to the page
boundary. The page count equals the `0x48` page-count field in 275/275 rows.
The 1,768 pages come from 275 rows: 257 rows use a 256-block stride, 1 row uses
231, 15 use 60, 1 uses 882 and 1 uses 54. The four block classes sum to the
505,723 total: 502,373 data, 1,768 sentinel, 26 other metadata and 1,556 zero.
The classifier treats every leading non-data, non-zero block as metadata; a
corrupted first data block would therefore be counted as metadata and is not
distinguishable by this rule.

Codec byte `0x02` does not use the length framing. Its `0x55` record size is
`4 * declared` in 227/227 records, where `declared` is the `0x76` `u32` at
`+0x00`. The sample type is not established; no decoder was run.

## FF02 count formula

For `FF02`, let `streams` be the `u32` at `+0x08` and `chunks[i]` the high three
bits of the `i`-th `u32` at `+0x10`. Then:

```text
data_offset = 0x10 + 4 * streams + 8 * sum(chunks)
```

The formula holds in 124/124 `FF02` rows. The earlier reading used a fixed
record width and the relation `data_offset = 0x10 + width * streams`:

| Recorded width | Rows | Chunk counts | Width relation | Count formula |
| ---: | ---: | --- | --- | --- |
| 36 | 113 | 4 per stream | holds | holds |
| 44 | 4 | 5 per stream | holds | holds |
| 60 | 6 | 7 per stream | holds | holds |
| non-integral | 1 | mixed | fails | holds |

The width relation explains 123 of the 124 rows. The remaining row has mixed
chunk counts, so no single width exists; its integer width is 39 and its byte
count is not divisible by the stream count. The count formula explains that row
and all 123 fixed-width rows. The 113 width-36 rows are the `audio.rpf` family;
the 44 and 60 widths and the mixed row are in the other family.

The `u32` at `+0x08` is a stream count, not a record count. In `FF02` the record
count is `sum(chunks)`, which ranges from 4 to 576 while `streams` ranges from 1
to 144. In `FF21`, `FF25` and `FF61` the record count is not the `u16` table
length either: `FF25` has 2 to 9 streams but 3 to 5 records. The count at
`+0x08` indexes the per-stream table; it does not count chunk records.

## One format or several

The 768 rows share the magic, the version, the 16-byte header layout and the
count/offset semantics. The four values in the high half of `+0x04` select table
layouts, not independent signatures, so the evidence supports one format family
with four header variants. It does not support four unrelated formats.

Archive family changes only one observed relation: the `FF02` width-36 rows are
`audio.rpf` depth-1 rows, while the wider and mixed rows are in the other
family. `FF21`, `FF25` and `FF61` use the same positions and formulas in both
families. Archive placement is provenance; the predicates are header arithmetic.

## Hypothesis results

| Hypothesis | Result | Population | Confidence |
| --- | --- | --- | --- |
| H1: codec byte `0x0B` and `[u16 length][packet]` framing in 2,048-byte blocks | Framing rule holds with zero violations and zero exceptions. The byte is consistent with a codec selector; its identity is not established | 14,940 `0x55` records, 4,961,453 packets | Confirmed (framing); Unknown (codec identity) |
| H2: codec byte `0x05` is a 32 kHz mono stream | Rejected for this population: no descriptor carries `0x05` and no rate field is 32,000 | 15,265 descriptor entries | Rejected (absence) |
| H3: codec byte `0x02` is 4 bytes per declared sample | `size == 4 * declared` in 227/227 records | 227 records in 43 rows | Confirmed (size relation); Unknown (sample type) |
| H4: low `u16` of the `0x76` descriptor is a source rate | The rate is the low `u16` at `+0x08`, not the descriptor's lowest `u16`. It is 48,000 in 14,625 `0x76` records and 12,000, 22,050 or 11,025 in 40 records. `0x48` entries carry the rate in the high `u16` of their third word. 48 kHz decode is not verified | 14,665 `0x76` records, 373 `0x48` entries | Confirmed (field position and values); Unknown (decode rate) |
| H5: a `0xA3` entry is a seek position | An entry is a 4-byte `u32`. Every `A3` table starts at 0 and is non-decreasing. `FF02`/`FF21`/`FF61` have one entry per 2,048-byte block plus the initial 0 (14,665/14,665); `FF25` has one entry per page (275/275). The unit and the terminal relation to decoded samples are Unknown | 14,940 paired streams | Probable (position table); Unknown (unit) |

The 227 `0x02` streams have no `0xA3` record and are outside the H5 count. They
occur in 43 `FF21` rows that carry only `0x02` streams; the `0x0B` streams and
their `A3` tables are in the other 240 `FF21` rows. The 40 non-48 kHz `0x76`
records occur in 14 rows in two depth-1 archives under `audio.rpf`; the evidence
index lists each record.

## Decode dependency

No decoder was installed, copied or run, and no decoder is authorized for this
task. The 20-stream decode criterion is therefore unmet. The framing result is a
container result: it shows that the blocks and packet boundaries are consistent,
not that the packets decode.

To confirm codec identity and the declared sample count, an authorized decoder
must decode the `0x0B` packets and compare the decoded sample count with the
container's declared count (`0x76` at `+0x00`, `0x48` entry at `+0x04`) and with
the terminal `0xA3` entry. The same test decides whether `0x02` is a float
sample stream. No `0x05` stream exists in the 768-row sample, so a decoder
cannot be tested against that hypothesis here.

## Identification

Identification MUST use the payload bytes. `ADAT` at offset 0 identifies the
signature; the type ID and archive name do not. The `u32` flags at `+0x04` MUST
be recorded with the signature, because the high half selects the table layout.

## Limits

- One build and one local archive set.
- The depth-1 scan is a sample: 782 of 3,970 candidate archives were extracted,
  and 381 type-0 rows exceeded the archive size cap. The 768 rows are not a
  complete census of the build.
- The 18 zlib type-255 rows in one `audio.rpf` archive were not decoded, so
  whether they also begin `ADAT` is Unknown.
- The `8 * streams + 4`-byte region between the `u16` table and the record run is
  uninterpreted.
- The record type bytes and the second `FF61` offset have no established
  meaning.
- No executable path was traced and no decoder was run. The codec bytes, the
  packet framing and the `0x48` page fields are structural observations; no
  codec identity is assigned.
- The `0x48` entry fields `unknown` and `decoded`, the `0x76` declared count and
  the `0xA3` unit are not mapped to decoded samples.

## Open questions

- What do the record type bytes select?
- What are the `8 * streams + 4` bytes before the record run?
- What is the second `FF61` offset pointing to?
- Which codec decodes each codec byte, and does the decoded sample count match
  the descriptor count?
- Do the 40 non-48 kHz `0x76` records describe a resampled source or a different
  stream role?
- Why do 18 type-255 rows in one `audio.rpf` archive begin a zlib stream instead
  of `ADAT`?

Evidence: [evidence/adat/INDEX.md](../../../evidence/adat/INDEX.md).
