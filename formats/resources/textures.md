# Texture dictionaries

A texture dictionary is one RAGE resource: a system segment that holds a sorted
name-hash array, a parallel value array, and a dense table of 0x70-byte texture
records, plus a graphics segment that holds the texture allocations. This
document describes the container grammar and the allocation arithmetic. It does
not decode pixels.

The layout is read from payload data of the Scarlett build
[e95020b2](../../builds/gta-vi/scarlett-e95020b2/README.md). No engine code
path was traced. Field positions are **Confirmed** on the sample below; field
meanings are **Probable** unless a row says otherwise. The label "texture
dictionary" is the subject name used by this iteration, not a recovered symbol.
Findings are cited as `RES-F36` and listed in
[evidence/resources/INDEX.md](../../evidence/resources/INDEX.md).

## Sample

The sample is every type-5 row of the 25 nested archives below: 1,440
resources, 5,484 records. The rows are type-0 rows of `<GAME_ROOT>/textures.rpf`
and `<GAME_ROOT>/data.rpf`. The selection rule is the local CLI type ID 5 inside
those nested archives; no other type-5 row was found in the scanned archives.
The counts and digests are in
[Sample locators](../../evidence/resources/INDEX.md#texture-dictionary-sample).

| Property                    | Value                                                       |
| --------------------------- | ----------------------------------------------------------- |
| Resources                   | 1,440                                                       |
| Non-empty dictionaries      | 1,431                                                       |
| Empty dictionaries          | 9                                                           |
| Records                     | 5,484                                                       |
| Records per dictionary      | 1 to 1,198                                                  |
| Dimensions                  | 94 distinct pairs, 4×4 to 4,096×1,024                       |
| Format ids                  | 22 distinct values, `10` to `99`                            |
| Mip counts                  | 1 to 12                                                     |
| Allocation bytes            | 794,218,496 of 795,594,752 graphics bytes                   |
| Resources with `sum(sizes) == graphics` | 1,375 (non-empty)                              |
| Resources with `sum(sizes) < graphics`  | 56 (non-empty)                                  |

## Recognition rule

A reader can recognise a texture dictionary by arithmetic, not by a name or a
type ID:

1. The system segment starts with a zero `u64` and a system pointer at `+0x08`.
2. `+0x20` is a system pointer to a `u32` hash array; `+0x28` holds its `u16`
   count and `u16` capacity.
3. `+0x30` is a system pointer to a `u64` value array; `+0x38` holds its `u16`
   count and `u16` capacity.
4. The two counts are equal and the two capacities are at least the count.
5. The hash array is in ascending order and has no duplicate.
6. Every value is a system pointer to a 0x70-byte record table.
7. Every record's `+0x18` value is a graphics pointer and
   `allocation_units × unit_bytes` stays inside the graphics segment.

All 1,431 non-empty dictionaries pass steps 1–7. The 9 empty dictionaries have
zero hash and value pointers and zero counts; their system segment is 96 bytes
and the page map declares one system page and no graphics page.

The name hash is the 32-bit one-at-a-time hash (`joaat`) of the ASCII text
reached from the record's name pointer, with the text starting at the pointer
`+8`. All 5,484 records match. The text and the hashes are payload data and are
not reproduced here. A name hash is a key, not a recovered filename.

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
| `+0x48`, `+0x50`, `+0x58` | 8 each | present, values vary; not interpreted | Bytes confirmed; meanings **Unknown** |

The rest of the root header is not part of this grammar. A reader MUST NOT
require any other root field.

## Arrays

The hash array is `count` little-endian `u32` values in ascending order. The
value array is `count` 8-byte values in the same order: `hash[i]` and
`value[i]` describe the same texture. The value array is a permutation of the
record table; a reader MUST follow `value[i]`, not compute a record address from
`i`.

The record table is normally a dense run of 0x70-byte records. One dictionary
of 1,198 records has a 0x20-byte gap at system `0x1ff70..0x20000`, on a
`0x10000` boundary. A reader MUST therefore accept a non-contiguous record
table. The gap does not change the record width.

## Record

Each value points to a 0x70-byte record. The same shape was read in all 5,484
records.

| Offset | Width | Content                                                       | Confidence |
| ------ | ----- | ------------------------------------------------------------- | ---------- |
| `+0x00` | 8    | zero                                                          | Confirmed (sample) |
| `+0x08` | 4    | allocation size in format units                               | Confirmed (arithmetic) |
| `+0x0C` | 4    | two `u16`; not interpreted                                    | Bytes confirmed; meaning **Unknown** |
| `+0x10` | 8    | `2432` in 5,464 records and `2434` in 20; not interpreted      | Bytes confirmed; meaning **Unknown** |
| `+0x18` | 8    | graphics pointer to the allocation start                      | Confirmed (arithmetic) |
| `+0x20` | 8    | zero                                                          | Confirmed (sample) |
| `+0x28` | 8    | system pointer to this record `+0x50`                         | Confirmed (sample) |
| `+0x30` | 8    | system pointer to a name record; ASCII text at pointer `+8`   | Confirmed (sample) |
| `+0x38` | 2    | width                                                         | Probable (arithmetic) |
| `+0x3A` | 2    | height                                                        | Probable (arithmetic) |
| `+0x3C` | 2    | `1` in 5,307 records; other small values; not interpreted      | Bytes confirmed; meaning **Unknown** |
| `+0x3E` | 1    | `1` in 5,363 records, `3` in 120, `2` in 1; not interpreted    | Bytes confirmed; meaning **Unknown** |
| `+0x3F` | 1    | format id                                                     | Probable (arithmetic) |
| `+0x40` | 2    | `5` in every record; not interpreted                          | Bytes confirmed; meaning **Unknown** |
| `+0x42` | 2    | mip count in bits 0..14; bit 15 is set in some records         | Probable (arithmetic) |
| `+0x44` | 2    | zero                                                          | Confirmed (sample) |
| `+0x46` | 2    | `1`                                                           | Confirmed (sample) |
| `+0x48` | 8    | `0x0000000200000000` in every record                          | Confirmed (sample); meaning **Unknown** |
| `+0x50`, `+0x58` | 8 each | zero in every record                                  | Confirmed (sample) |
| `+0x60` | 8    | high 48 bits set; low 16 bits vary (`0x0241` in 5,307)         | Bytes confirmed; meaning **Unknown** |
| `+0x68` | 8    | zero                                                          | Confirmed (sample) |

## Allocation arithmetic

`allocation_size = allocation_units × unit_bytes(format id)`. The unit is the
number of bytes in one 4×4 block for the block formats or one pixel for the
uncompressed formats. The unit values below are the ones that reproduce the
allocation extents; they are not a pixel decoder.

| Format id | Unit bytes | Format id | Unit bytes | Format id | Unit bytes |
| --------: | ---------: | --------: | ---------: | --------: | ---------: |
| 10 | 8 | 41 | 4 | 78 | 16 |
| 24 | 4 | 49 | 2 | 80 | 8 |
| 28 | 4 | 54 | 2 | 83 | 16 |
| 29 | 4 | 56 | 2 | 87 | 4 |
| 34 | 4 | 61 | 1 | 95 | 16 |
| 65 | 1 | 71 | 8 | 98 | 16 |
| 72 | 8 | 74 | 16 | 99 | 16 |
| 77 | 16 | | | | |

The id values coincide with DXGI format numbers, but this document does not
decode pixels and does not state a channel layout, a swizzle, sRGB handling or a
block layout. The arithmetic only establishes the unit width.

Checks over the 5,484 records:

- every allocation starts inside the graphics segment;
- `allocation_offset + allocation_size` never leaves the graphics segment;
- the allocation sizes sum to at most the graphics size in all 1,431 non-empty
  resources (equality in 1,375, strict inequality in 56); the 9 empty
  dictionaries have no graphics segment;
- no two records share an allocation start;
- the 4 KiB-aligned mip-chain size computed from width, height, format unit and
  mip count is at most `allocation_size` in 5,484 of 5,484 records;
- it equals `allocation_size` in 4,901 records; the other 583 are larger, which
  is consistent with padding or additional surfaces not modelled here.

The gap between successive distinct allocation starts (last to the graphics
end) is an upper bound on the allocation. In the 56 resources where the stored
sizes sum to less than the graphics size, that gap is larger than the stored
size. A reader that needs a bound MUST use the gap; a reader that needs the
stored size MUST use the unit count.

## Competing models

| Candidate                                                       | Discriminating observation                                                                 | Result   |
| --------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | -------- |
| The record width is 0x50 or 0x38 because only part of the shape repeats | The value array points into a run whose sorted starts are 0x70 apart, and the run ends at the value array. The full 0x70 shape is identical in 5,484 records | Rejected |
| `hash[i]` describes the record at `record_base + i × 0x70`       | The value array is a permutation of the record run; the record order differs from the hash order in every dictionary with more than one record | Rejected |
| The allocation size is the gap to the next allocation            | In 56 resources the gaps sum to more than the stored sizes, and the stored unit count never exceeds the gap. The gap is an upper bound | Rejected as the size; kept as a bound |
| The mip count is the `u16` at `+0x3C`                            | `+0x3C` is `1` in most records and does not track the dimensions or the allocation; `+0x42` is at most the maximum level for the dimensions in 5,484 of 5,484 | Rejected |
| The `u8` at `+0x3F` is an opaque flag                            | Dividing the allocation by the stored unit count gives one consistent unit per value; the 22 values fall into unit groups of 1, 2, 4, 8 and 16 bytes and reproduce the extents | Rejected |
| A name hash is a 64-bit path hash                                 | Each stored hash equals the 32-bit one-at-a-time hash of the ASCII name text in 5,484 of 5,484 records | Rejected |

## Empty and incomplete dictionaries

- An empty dictionary has a 96-byte system segment, a page map with one system
  page and zero graphics pages, and zero hash and value pointers. It has no
  records. Nine such resources occur.
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
| Texture name record | `u32` at record `+0x18` when the `u64` at `+0x10` is `6` | a 32-bit dictionary name hash | Probable (264 matches, see below) |
| Texture name record | `u64` at record `+0x08` | a separate 64-bit key; neither 32-bit half is a dictionary hash | Rejected as a dictionary reference |

The sample is the 92 type-2 drawables of the nested archive at
`<GAME_ROOT>/levels.rpf` row 5 (SHA-256
`450B6A5A95578A31133F686AE5D1D8151B4C7A38197F039895311D44742DBC96`). It holds
164 shaders and 969 texture parameters:

- all 969 parameters resolve to a slot index in range; the index equals the
  parameter's position in the table in all 969;
- 770 slots hold a system texture record (4 to 29 per drawable; every drawable
  has at least 4), 199 are null and 0 are invalid;
- 678 name records have the `6` variant at `+0x10`; 92 have a system pointer
  there and do not carry the dictionary hash;
- of the 678 hash-bearing records, 264 match a name hash in the 1,440 sampled
  dictionaries and 414 do not. The 414 are unresolved, not false: the sampled
  dictionary set does not cover every texture name. The 264 matches cover 4
  distinct hashes and 86 of the 92 drawables; a hash can occur in more than one
  dictionary;
- all 404 dictionary records reached by the 264 references have an in-bounds
  allocation;
- no 32-bit half of the 64-bit key is a dictionary hash (0 of 770).

Control: 10,000 random `u32` values produce no accepted slot reference and no
dictionary-hash match. The 7,920 non-texture parameter words produce no
accepted slot reference.

## Limits

- One build, two top-level archives, 25 nested archives. The sample is a census
  of the type-5 rows in those nested archives, not of the game.
- The record grammar is established from payload bytes and arithmetic. No
  engine code that builds, validates or uploads a dictionary was traced.
- Width, height, format id and mip count are supported by the allocation
  arithmetic, not by pixel decoding. A separate texture-format document would be
  needed to decode pixels.
- The meanings of `+0x08`'s high half, `+0x10`, `+0x3C`, `+0x3E`, `+0x40`,
  `+0x48`, `+0x60` and the root `+0x18`/`+0x48`/`+0x50`/`+0x58` are **Unknown**.
- The 583 records whose allocation exceeds the 4 KiB-aligned mip chain are not
  explained. Additional surfaces, padding or an unread count are candidates.
  None was established.
- The name text is payload data. It is read for the hash check only and is not
  published.
- The drawable reference sample is one nested archive of `levels.rpf` and one
  build. The 414 unresolved references are not shown to be absent from every
  dictionary. The slot index equals the parameter position in all 969 cases, so
  an independent cross-reference is not demonstrated.

## Tool

[tools/resources/texture_dictionary.py](../../tools/resources/texture_dictionary.py)
implements the dictionary grammar. It reads a decoded resource or a stored row
through `page_reconstruct`, bounds the counts, reports every record field and
the allocation checks, and does not decode pixels.
[tools/resources/pool_reference.py](../../tools/resources/pool_reference.py)
reads the drawable slot and name-record references and reports them separately
from 0x5/0x6 pointers. Their synthetic tests are under `tools/resources/tests/`.
