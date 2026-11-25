# GFX*

`GFX*` (`47 46 58 2A`) at offset 0 marks the decoded payload of 49 rows. All 49
rows are type 66, chunk encoding 3, mode 0, and no payload transform. Their
stored bytes at `payload_offset` begin with a zlib stream (`78 DA`), so the
signature is visible only after chunk decoding.

The archive parent, nested row, sizes and variant bytes are provenance and
observations only. No payload purpose, format name or field meaning is
established.

## Population and predicate

The recount used the 849 unique depth-1 manifests present in the cached
inventory, which hold 183,144 row records. The run summary records 782 unique
archives and 169,523 rows for its current sample; the cache directory holds 67
further unique archives. All six type-66 archives are in the current sample,
and the 67 further archives add no type-66 row.

The predicate is an exact four-byte match at offset 0 of the decoded payload.
It is not a whole-file hash and not a substring search anywhere in the payload.
The stored-byte predicate applies the same four bytes at the stored payload
offset and finds none of these rows, because every stored payload is a chunked
zlib stream. Decoding all 49 type-66 rows gives 49 matches and 0 counterexamples.

| Source | Nested rows | Decoded bytes | Variants | Multi-chunk |
| --- | ---: | ---: | --- | ---: |
| `data.rpf` row 1 | 5 | 2,251 to 1,379,793 | `70/0B`, `80/02`, `88/01` | 1 |
| `data.rpf` row 3 | 4 | 28,148 to 824,949 | `88/01` | 3 |
| `data.rpf` row 6 | 6 | 926,563 to 6,605,786 | `88/01` | 6 |
| `data.rpf` row 19 | 31 | 5,345 to 48,658 | `80/02`, `78/05`, `88/01` | 0 |
| `data.rpf` row 20 | 1 | 2,688 | `88/01` | 0 |
| `data.rpf` row 39 | 2 | 49,685 to 183,623 | `70/0A`, `88/01` | 1 |

The 49 rows were extracted end to end, including the 11 multi-chunk rows. The
extraction is exhaustive for the type-66 population, so it covers every observed
size and all six archive parents. In every row the decoded length equals the
manifest logical size and the `u32` at `+0x04` equals the decoded length.

## Decoded layout

The offsets below are relative to the start of the decoded payload. `name1` is
the first printable ASCII run and `name2` the second.

| Offset | Width | Observation | Support |
| --- | --- | --- | --- |
| `+0x00` | 4 | `GFX*` | 49/49 |
| `+0x04` | 4 | little-endian `u32` equal to the decoded length | 49/49 |
| `+0x08` | 1 | variant byte: `0x70`, `0x78`, `0x80` or `0x88` | 49/49 |
| `+0x09` | 1 | zero | 49/49 |
| `+0x0A` | 1 | variant byte: `0x01`, `0x02`, `0x05`, `0x0A` or `0x0B` | 49/49 |
| `+0x0B` | 10 to 12 | variant-dependent bytes; no length or count in this region predicts a later extent | 49/49 (positions); Unknown (values) |
| `name1 - 11` | 9 | the constant run `FA 01 04 00 00 00 00 0E 00` | 49/49 |
| `name1 - 2` | 2 | big-endian `u16` length of `name1`, 3 to 30, high byte zero | 49/49 |
| `name1` | 3 to 30 | printable ASCII run | 49/49 |
| `name1 end` | 15 | interstitial: ten constant bytes, then a three-byte group and a fourth byte, ending in `0x0A` | 49/49 |
| `name1 end + 15` | 17 to 54 | `name2`, printable ASCII, contains `name1` and ends `_Main` | 49/49 |
| after `name2` | variable | opaque body | 49/49 (positions); Unknown (content) |
| length - 10 | 10 | last ten bytes: a printable run ending `.Main`, a zero byte, then little-endian `u32` 64 | 49/49 |

The interstitial's three-byte group is `00 00 00` in 46 rows, `FF 00 00` in 2
and `FF FF FF` in 1. Its fourth byte takes values from 210 to 247. The values
are observations only.

The last four bytes of the variant-dependent region are `30 01 00 v` in 48 rows
and `18 01 00 v` in 1; `v` takes values from 15 to 42. This is a repeated
constant run with one observed exception, not an established field.

The constant run before `name1` is fixed relative to the name, so the header is
not a fixed-size structure. The first name starts at `+0x20` for the `70`
variants, `+0x21` for `78` and `80`, and `+0x22` for `88`. The first name and
body therefore need not be aligned: the 49 body starts take 13 different
residues modulo 16. The decoded lengths take 15 residues modulo 16.

## Variants

| Bytes at `+0x08` / `+0x0A` | First name offset | Rows | Multi-chunk |
| --- | ---: | ---: | ---: |
| `88` / `01` | `+0x22` | 17 | 11 |
| `80` / `02` | `+0x21` | 28 | 0 |
| `78` / `05` | `+0x21` | 2 | 0 |
| `70` / `0B` | `+0x20` | 1 | 0 |
| `70` / `0A` | `+0x20` | 1 | 0 |

These are observable variants, not claimed versions or payload kinds. They
co-occur within one archive: `data.rpf` row 1 contributes a `70/0B`, a `80/02`
and three `88/01` rows. The 11 multi-chunk rows are all `88/01` (11/11); the
`88/01` variant also covers 6 single-chunk rows, so multi-chunk implies the
variant but the variant does not imply multi-chunk.

## Comparison

- 49 distinct decoded lengths from 2,251 to 6,605,786 bytes; 49 distinct
  SHA-256 values, so no two payloads are byte-identical.
- The only prefix shared by all 49 is the four-byte signature; no pair shares
  the first eight bytes because the size field differs.
- The suffix shared by all 49 is the ten-byte trailer. 109 of 1,176 pairs share
  more than ten trailing bytes, up to 29; no pair shares more than 29.
- A search over every one-, two- and four-byte field in the first 64 bytes, in
  both byte orders, found no field equal to the body start, body length, first
  run length or second run length. The only matching field is the `u32` at
  `+0x04`, which equals the total decoded length (49/49).
- The three constant markers occur exactly once per payload: the pre-name run
  `FA 01 04 00 00 00 00 0E 00` (49/49), the ten-byte interstitial prefix
  (49/49) and the ten-byte trailer (49/49). None recurs in the body.
- The body starts between offsets 69 and 132. Its first two bytes take 21
  distinct pairs; the most common pair occurs in 15 of 49. The grammar that
  holds from offset 0 therefore stops being predictive at the first body byte.
  A final printable run and the fixed trailer are consistent from the end, but
  the distance from the body start to that run is not fixed.

## Limits

- One build
  ([scarlett-e95020b2](../../../builds/gta-vi/scarlett-e95020b2/README.md)) and
  one local archive set.
- All 49 type-66 rows in the population were decoded. The 37 non-type-66 rows
  in the six GFX archives, all type 5, were also decoded; 0 begin `GFX*`. The
  remaining 182,235 readable rows were read at their stored prefixes only; 0
  stored rows begin `GFX*`. A bounded sample across eight non-type-66 encoding-3
  types decoded 37 rows and found no `GFX*`; one type-14 row was behind the
  payload transform. This is a bounded cross-type sample, not a decoded census
  of every row.
- No executable path was traced. The archive name, type ID and signature are
  identifiers for this sample only; no field meaning is established.
- The inventory reached depth 1. Type-66 rows below that depth were not
  searched.
- The ASCII runs are not reproduced. Their presence, offsets and lengths are
  game-data observations, not format identity.

Evidence: [evidence/gfx/INDEX.md](../../../evidence/gfx/INDEX.md).
