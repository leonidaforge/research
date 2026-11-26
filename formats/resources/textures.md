# Texture dictionaries

A texture dictionary is one RAGE resource: a system segment that holds a sorted
name-hash array, a parallel value array, and a table of 0x70-byte texture
records, plus a graphics segment that holds the allocations. This document
describes the container grammar and the allocation bounds. It does not decode
pixels and does not establish a byte size for an allocation.

The layout is read from payload data of the Scarlett build
[e95020b2](../../builds/gta-vi/scarlett-e95020b2/README.md). No engine code path
was traced. Field positions are **Confirmed** on the sample below; field
meanings are **Probable** only where the text says so, and several remain
**Unknown**. The label "texture dictionary" is the subject name used by this
iteration, not a recovered symbol. Findings are cited as `RES-F36` and listed in
[evidence/resources/INDEX.md](../../evidence/resources/INDEX.md).

## Sample

The positive sample is every type-5 row of the 25 nested archives below: 1,440
resources, 5,484 records. The rows are type-0 rows of
`<GAME_ROOT>/textures.rpf` and `<GAME_ROOT>/data.rpf`. The selection rule is the
local CLI type ID 5 inside those nested archives. The counts and digests are in
[Sample locators](../../evidence/resources/INDEX.md#texture-dictionary-sample).

The negative sample is 469 rows of other local type IDs in the same nested
archives and two `levels.rpf` nested archives: 80 type 66, 224 type 3, 164 type
73 and 1 type 74. The type-66 rows are in the five `data.rpf` nested archives of
the sample table, the type-3 rows are in the `levels.rpf` row-5 archive and the
type-73/74 rows are in the `levels.rpf` row-153 archive. They were selected with
the same listing command and the type IDs stated here.

| Property                    | Value                                                       |
| --------------------------- | ----------------------------------------------------------- |
| Positive resources          | 1,440                                                       |
| Non-empty dictionaries      | 1,431                                                       |
| Empty dictionaries          | 9                                                           |
| Records                     | 5,484                                                       |
| Records per non-empty dictionary | 1 to 1,198                                         |
| Dimensions                  | 94 distinct pairs, 4×4 to 4,096×1,024                       |
| Format ids                  | 22 distinct values, `10` to `99`                            |
| Mip counts                  | 1 to 12                                                     |
| Distinct name hashes        | 2,852                                                       |
| Negative rows               | 469 selected, 0 accepted                                    |

## Recognition test

A reader applies these structural tests to a decoded resource:

1. The system segment starts with a zero `u64` and a system pointer at `+0x08`.
2. `+0x20` is a system pointer to a `u32` hash array; `+0x28` holds its `u16`
   count and `u16` capacity.
3. `+0x30` is a system pointer to a `u64` value array; `+0x38` holds its `u16`
   count and `u16` capacity.
4. The two counts are equal.
5. Each capacity is at least its count.
6. The hash array is in ascending order and has no duplicate.
7. Every value is a system pointer to a 0x70-byte record.

All 1,431 non-empty dictionaries pass steps 1–7. The 9 empty dictionaries have
zero pointers and counts and pass steps 1–5 trivially. The negative attribution
is:

| Type | Selected | Decode fail | Structural reject | Accepted |
| ---- | -------: | ----------: | ----------------: | -------: |
| 66   |       80 |          80 |                 0 |        0 |
| 3    |      224 |           0 |               224 |        0 |
| 73   |      164 |           0 |               164 |        0 |
| 74   |        1 |           0 |                 1 |        0 |
| all  |      469 |          80 |               389 |        0 |

The type-66 rows fail in `page_reconstruct`; the other 389 reach
`parse_dictionary` and are rejected by the structural test.

This is a structural test, not a proof of format identity. Steps 1–2 are generic
resource-header fields, and the positive sample was selected by type ID 5. Of
the 469 nearby resources of other types, 80 were rejected during stored-row
reconstruction and 389 by the structural test; none was accepted. The test does
not show that every type-5 resource is a dictionary or that another type cannot
pass.

The name hash is the 32-bit one-at-a-time hash (`joaat`) of the ASCII text
reached from the record's name pointer, with the text starting at the pointer
`+8`. The implementation folds `A`–`Z` and `\`, matching the published engine
behaviour (HSH-F04). The check reads at most 64 bytes and skips a record whose
text has no terminator inside that window. All 5,484 records match. The text and
the hashes are payload data and are not reproduced here. A name hash is a key,
not a recovered filename.

## Root header

Offsets are from the start of the system segment. Only the fields used by the
grammar are listed.

| Offset | Width | Content                                            | Confidence              |
| ------ | ----- | -------------------------------------------------- | ----------------------- |
| `+0x00` | 8    | zero                                               | Confirmed (sample)      |
| `+0x08` | 8    | system pointer to the page map                     | Confirmed (sample)      |
| `+0x18` | 8    | `1` in every dictionary of the sample              | Confirmed (sample); meaning **Unknown** |
| `+0x20` | 8    | system pointer to the hash array                   | Confirmed (sample)      |
| `+0x28` | 2×2  | `u16` hash count, `u16` hash capacity              | Confirmed (sample)      |
| `+0x30` | 8    | system pointer to the value array                  | Confirmed (sample)      |
| `+0x38` | 2×2  | `u16` value count, `u16` value capacity            | Confirmed (sample)      |
| `+0x48`, `+0x50`, `+0x58` | 8 each | present, values vary (68, 32 and 42 distinct values); not interpreted | Bytes confirmed; meanings **Unknown** |

The rest of the root header is not part of this grammar. A reader MUST NOT
require any other root field.

## Arrays

The hash array is `count` little-endian `u32` values in ascending order. The
value array is `count` 8-byte values in the same order: `hash[i]` and
`value[i]` describe the same texture. The value array is a set of distinct
record pointers; its order is not always the index order. The parser reports
`value_order_matches_index`. It compares each value entry's record address with
the sorted recorded addresses, not with a fixed stride, so the one 0x20-byte gap
does not by itself count as a mismatch. In 1,315 of the 1,422 multi-record
dictionaries the value order equals the index order, and in 107 it differs. A
reader MUST follow `value[i]`, not compute a record address from `i`.

Across the 2,852 distinct hashes, 2,842 occur in one record, 8 occur in two
records and 2 occur in 1,313 records. A hash is therefore not unique to one
dictionary; the same texture name can appear in many dictionaries.

The record table is normally a dense run of 0x70-byte records: 1,430 of the
1,431 non-empty dictionaries are dense. One dictionary of 1,198 records has one
gap. The census records the two record starts as `0x1ff70` and `0x20000`, a
delta of `0x90`, which leaves `0x20` bytes between the end of the first record
and the start of the second, on a `0x10000` boundary. A reader MUST therefore
accept a non-contiguous record table. The gap does not change the record width.

## Record

Each value points to a 0x70-byte record. The same shape was read in all 5,484
records.

| Offset | Width | Content                                                       | Confidence |
| ------ | ----- | ------------------------------------------------------------- | ---------- |
| `+0x00` | 8    | zero                                                          | Confirmed (sample) |
| `+0x08` | 4    | allocation unit count; byte scale **Unknown**                 | Bytes confirmed; meaning **Unknown** |
| `+0x0C` | 4    | two `u16`; not interpreted                                    | Bytes confirmed; meaning **Unknown** |
| `+0x10` | 8    | `2432` in 5,464 records and `2434` in 20; not interpreted      | Bytes confirmed; meaning **Unknown** |
| `+0x18` | 8    | graphics pointer to the allocation start                      | Confirmed (sample) |
| `+0x20` | 8    | zero                                                          | Confirmed (sample) |
| `+0x28` | 8    | system pointer to this record `+0x50`                         | Confirmed (sample) |
| `+0x30` | 8    | system pointer to a name record; ASCII text at pointer `+8`   | Confirmed (sample) |
| `+0x38` | 2    | candidate width                                               | Probable (position) |
| `+0x3A` | 2    | candidate height                                              | Probable (position) |
| `+0x3C` | 2    | `1` in 5,307 records; other small values; not interpreted      | Bytes confirmed; meaning **Unknown** |
| `+0x3E` | 1    | `1` in 5,363 records, `3` in 120, `2` in 1; not interpreted    | Bytes confirmed; meaning **Unknown** |
| `+0x3F` | 1    | format id; not mapped to an enum                              | Bytes confirmed; meaning **Unknown** |
| `+0x40` | 1    | swizzle id: `0` is row-major, `5` in every sampled record is 4 KiB tiled | Confirmed (sample) |
| `+0x42` | 2    | candidate mip count in bits 0..14; bit 15 is set in some records | Probable (position) |
| `+0x44` | 2    | zero                                                          | Confirmed (sample) |
| `+0x46` | 2    | `1`                                                           | Confirmed (sample) |
| `+0x48` | 8    | `0x0000000200000000` in every record                          | Confirmed (sample); meaning **Unknown** |
| `+0x50`, `+0x58` | 8 each | zero in every record                                  | Confirmed (sample) |
| `+0x60` | 8    | high 48 bits set; low 16 bits vary (`0x0241` in 5,307)         | Bytes confirmed; meaning **Unknown** |
| `+0x68` | 8    | zero                                                          | Confirmed (sample) |

Width, height, format id and mip count are the fields the acceptance criteria
require the parser to expose. Their positions are confirmed; their meanings are
**Probable at best**. The only arithmetic check is that the mip count is at most
`bit_length(max(width, height))` in 5,484 of 5,484 records, which is weak
because most records declare one mip level. No independent support for the four
meanings is claimed.

## Swizzled allocations

The byte at `+0x40` selects the graphics layout. Zero is row-major. A non-zero
value (`5` in every sampled record) stores the level as a grid of 4 KiB tiles
with a bit-interleaved element order.

One element is one 4 x 4 block for a block format and one texel for a linear
format. The tile holds:

| Element size | Tile elements | Pixels for a block format |
| ------------ | ------------- | ------------------------- |
| 16 bytes     | 16 x 16       | 64 x 64                   |
| 8 bytes      | 32 x 16       | 128 x 64                  |
| 4 bytes      | 32 x 32       | 32 x 32                   |
| 2 bytes      | 64 x 32       | 64 x 32                   |
| 1 byte       | 64 x 64       | 64 x 64                   |

The allocation is padded to whole tiles, so the stored size can exceed
`width x height x element size`. The element at local (x, y) is at the tile
offset given by this bit order, least significant bit first:

| Element size | Order |
| ------------ | ----- |
| 16 bytes     | y0 y1 x0 x1 y2 x2 y3 x3 |
| 8 bytes      | x0 y0 y1 x1 x2 y2 x3 y3 x4 |
| 4 bytes      | x0 x1 y0 y1 x2 y2 y3 x3 y4 x4 |
| 2 bytes      | x0 x1 x2 y0 y1 y2 x3 y3 x4 y4 x5 |
| 1 byte       | y0 y1 y2 x1 x0 x2 y3 x3 x4 y4 x5 y5 |

The 16-byte order is confirmed on two format-98 records: the row-major
reading fragments both, and the tile reorder yields a 1,920 x 1,080
photograph and a 1,024 x 512 UI layout. The 8-, 4-, 2- and 1-byte orders are
the same mapping at other element sizes; no simple-2D sample was checked, so
they are **Probable**.

When the mip count is above one, level 0 sits at the end of the allocation:
`allocation_start + allocation_extent - padded_level0_size`. Every sampled
record declares one mip, so the right-aligned multi-level placement is
**Probable**, not confirmed.

## Allocation bounds

The extent for a start is the next distinct start minus this start; the last
extent ends at the graphics end. The sum is therefore
`graphics_size - min(start)` when the starts are distinct.

The parser requires every record to have an allocation pointer, no two starts
to be equal, the first start to be zero, and the summed extents to equal the
graphics size. It reports these as `allocations_in_bounds`, `partition_ok` and
`starts_at_zero`. The weaker `allocation_sum_ok` is the `<=` check and is kept
for callers that only need a bound.

The equality is a consistency check between the extent table and the start
table, not independent evidence of a partition. With distinct starts and a zero
first start, the extents telescope to `graphics_size`, so the equality cannot
fail unless the extent computation is inconsistent. The 1,440 of 1,440 result
says the extent computation agrees with the start table in the sample; it does
not verify an independent allocation map. The 9 empty dictionaries have no
graphics bytes and pass trivially. All three checks hold in 1,440 of 1,440
resources.

A start equal to the graphics size is not accepted as in bounds; a missing
allocation pointer is not in bounds. If two records share a start, the parser
reports `allocation_duplicate` and the summed extents can exceed the graphics
size. If the first start is above zero, the parser reports
`allocation_front_gap`.

The extents are reader arithmetic on the sampled layout, not evidence of engine
allocation policy. The record's `+0x08` value is a unit count, not a byte count;
its byte scale is not established, and the parser does not multiply it.

An earlier draft fitted a unit table that made `units × unit` equal the extent
for each format id and reported a mip-chain comparison. That table was fitted
to the same extents it was then compared against, so it was not independent
evidence and the mip-chain comparison was not produced by committed code. The
table and its claims are withdrawn. The format id, the unit count and the
extent remain as separate observations.

## Competing models

| Candidate                                                       | Discriminating observation                                                                 | Result   |
| --------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | -------- |
| The record width is 0x50 or 0x38 because only part of the shape repeats | The value array points into a run whose sorted starts are 0x70 apart, and the run ends at the value array. The full 0x70 shape is identical in 5,484 records | Rejected |
| `hash[i]` describes the record at `record_base + i × 0x70`       | The value order differs from the index order in 107 of 1,422 multi-record dictionaries | Rejected |
| The allocation size is the unit count in bytes                   | The record stores a count, not a byte size; no stored byte size exists to compare against | Rejected as a size; the extent is an upper bound |
| A name hash is a 64-bit path hash                                 | Each stored hash equals 32-bit `joaat` of the referenced ASCII text (5,484/5,484) | Rejected |
| The capacity fields can be ignored                                | The parser now compares each capacity with its count; the sample has capacity ≥ count in 1,440/1,440 | Rejected as a free field |

## Empty and incomplete dictionaries

- An empty dictionary has a 96-byte system segment, a page map with one system
  page and zero graphics pages, and zero hash and value pointers. It has no
  records. Nine such resources occur; the census reports 9 of 9 at 96 bytes and
  page-map counts `1/0`.
- A dictionary whose hash count differs from its value count was not observed.
  A reader MUST report the mismatch instead of truncating silently.
- A dictionary whose value pointer leaves the system segment was not observed.
  A reader MUST report it, not resize the segment.

## References from drawables

A drawable names a texture in two places: a shader parameter entry selects a
slot, and a bound slot's texture record reaches a name record. The drawable
layout is documented in [drawables](drawables/README.md); only the reference
fields are repeated here.

| Family | Field | Reading | Confidence |
| ------ | ----- | ------- | ---------- |
| Shader texture parameter | `u32` at parameter entry `+0x04` | bits 0..1 are the entry class; class `0` means a texture entry and bits 2..31 are the slot index. `index = value >> 2`, accepted when `index < texture count` | Probable (969/969 texture entries, 0/7,920 non-texture entries) |
| Texture name record | `u32` at record `+0x18` when the `u64` at `+0x10` is `6` | a 32-bit value that shares the dictionary name-hash namespace | Probable (namespace match, see below) |
| Texture name record | `u64` at record `+0x08` | a separate 64-bit key; neither 32-bit half is a dictionary hash | Rejected as a dictionary reference |

The 64-bit key is not a dictionary hash, but it is the key the `.ttpf` stores
use. A store index built from `<GAME_ROOT>/data/ttdb` matched the distinct keys
of the two named drawable rows exactly: 12 keys matched one ETPF descriptor each
and the remaining key was a texture embedded in the drawable. A key found in
more than one store or descriptor is reported as ambiguous. The 32-bit hash at
record `+0x18` remains a dictionary-namespace value and is not used to select a
store.

The sample is the 92 type-2 drawables of the nested archive at
`<GAME_ROOT>/levels.rpf` row 5 (SHA-256
`450B6A5A95578A31133F686AE5D1D8151B4C7A38197F039895311D44742DBC96`). It holds
164 shaders and 969 texture parameters:

- all 969 parameters select a slot index in range; the index equals the
  parameter's position in the table in all 969;
- 770 slots hold a system texture record (4 to 29 per drawable; every drawable
  has at least 4), 199 are null and 0 are invalid;
- 678 name records have the `6` variant at `+0x10` and carry a 32-bit value at
  `+0x18`; 92 have a system pointer there and do not carry that value; 0 have no
  valid name record;
- the 678 values are 254 distinct values. 264 references to 4 distinct values
  match a name hash in the sampled dictionaries; 414 references to the other
  250 values do not. A matching hash is a namespace match, not a resolution to a
  specific resource: a hash can occur in more than one dictionary;
- of the 4 matched values, 2 occur in two dictionary records and 2 occur in one
  record each;
- 86 of the 92 drawables have at least one namespace match. Their per-drawable
  match counts are 1: 15, 2: 11, 3: 43, 4: 6, 5: 3, 6: 1, 7: 5, 8: 1, 10: 1;
- none of the 4 matched values equals one of the six constant texture-parameter
  values recorded by DRAW-F18 (`0xC8E8C282`, `0x739E3D0D`, `0x2C8D7182`,
  `0x0CD27763`, `0xC6F46E79`, `0x1E77BF4C`);
- no 32-bit half of the 64-bit key is a dictionary hash (0 of 770 lower halves
  and 0 of 770 upper halves; the key was read for all 770 bound slots).

The 92 pointer-variant name records and the 414 unmatched references are
unresolved. The sample does not show which dictionaries contain the unmatched
names; the containing dictionaries were not selected or were not available.

Control: 10,000 random `u32` values produce no accepted slot reference and no
dictionary-hash match; the threshold is 1% of the trials. The 7,920 non-texture
parameter words produce no accepted slot reference.

The `tools/resources/dictionary_census.py` script produces every count in this
section from caller-supplied archives and `lforge archive ls` listings. The
selection rule is the type ID in those listings.

## Pixel observations

The type-5 rows in the nested archive at row 7 of `textures.rpf` were read
through the same page reconstruction as the structural samples. Inner row 2
(68 records, 1,024 x 512, format 98) decoded as BC7 to a UI layout (outlined
boxes, a star row and a weapon icon) after the 4 KiB tile reorder; the
row-major reading scatters the elements. A 1,920 x 1,080 format-98 record
decoded the same way to a photograph. Inner row 1 (16 records, formats 71 and
77) decoded format 77 as BC3 to white glyphs on a transparent alpha
background. Inner row 0 (2 records, 64 x 64 and 512 x 512, format 77) decoded
as BC3. Inner row 3 holds 43 format-98 records. Inner row 5 holds four
records, two decodable format 77 and two format 95 records whose pixel layout
is unsupported. Inner row 4 is an empty dictionary with a 96-byte system
segment and no graphics bytes.

The page map of inner row 2 declares one system page and one graphics page. The
graphics page is stored as a 32 MiB chunk and a remainder, and the chunk table
gives a system segment of 11,840 bytes. Parsing the system segment at 0x2f00
also succeeds because the extra bytes are zero padding, but 11,840 is the page
boundary. This is a page-reconstruction observation, not a dictionary field.

These are image-consistency observations. They support BC3 for format 77 and
BC7 for format 98 in native dictionaries; they do not establish either codec
from engine code. The mapping remains **Probable**. The sampled records carry
no stored names, so the viewer's `Texture N` labels are synthesized. They are
not registered as a numbered finding; the row indices, counts and image checks
are the evidence.

Format 78 is a 16-byte block format. A sampled 512 x 128 record decoded as BC3
to a coherent ornament strip on a white background, and its 98,304-byte
descriptor range matches a BC3 level-0 size of 65,536 bytes plus one lower
level. Format 77 and 78 therefore form the BC3 linear/sRGB pair by layout and
numbering. The BC3 layout is **Probable** and the sRGB interpretation is
**Probable**; neither is traced from engine code.

## Limits

- One build. The positive sample is a census of the type-5 rows in 25 nested
  archives of two top-level archives; the negative sample is 469 rows of four
  other type IDs. This is not a game-wide census.
- The record grammar is established from payload bytes and structural checks. No
  engine code that builds, validates or uploads a dictionary was traced.
- Width, height, format id and mip count are exposed at confirmed positions.
  The pixel readings above are Probable image-consistency observations, not
  codec identities traced from engine code.
- The byte scale of the allocation unit count is **Unknown**. The reported
  allocation size is the extent upper bound.
- The meanings of `+0x08`, `+0x0C`, `+0x10`, `+0x3C`, `+0x3E`, `+0x48`,
  `+0x60` and the root `+0x18`/`+0x48`/`+0x50`/`+0x58` are **Unknown**.
- The 4 KiB tile geometry is confirmed for 16-byte elements only. The 8-, 4-,
  2- and 1-byte geometries and the right-aligned multi-level placement are
  **Probable**.
- The name text is payload data. It is read for the hash check only and is not
  published.
- The drawable reference sample is one nested archive of `levels.rpf`. The 414
  unmatched references are not shown to be absent from every dictionary. The
  slot index equals the parameter position in all 969 cases, so an independent
  cross-reference is not demonstrated.

## Tool

[tools/resources/texture_dictionary.py](../../tools/resources/texture_dictionary.py)
implements the dictionary grammar. It reads a decoded resource or a stored row
through `page_reconstruct`, bounds the counts, exposes every record field in the
table (including the uninterpreted ones) in its JSON report, and reports the
allocation extents and checks. It does not decode pixels.
[tools/resources/pool_reference.py](../../tools/resources/pool_reference.py)
reads the drawable slot and name-record references and reports them separately
from 0x5/0x6 pointers.
[tools/resources/dictionary_census.py](../../tools/resources/dictionary_census.py)
reproduces the aggregates in this document. Their synthetic tests are under
`tools/resources/tests/`.
