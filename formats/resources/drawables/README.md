# Drawables

A drawable is the resource payload behind the local type ID 2. It carries a
header, up to four LOD slots, model and geometry records, vertex-buffer and
index records, and a shader/material chain. This document describes the
reconstructed layout observed in two decoded payloads of the Scarlett build
[e95020b2](../../../builds/gta-vi/scarlett-e95020b2/README.md).

No engine code path was traced. Segment names follow RAGE convention and are
**Probable**. Field meanings are **Unknown** unless the table says otherwise.
Pointers use the encoding in [pointers.md](../pointers.md). Findings are cited
as `DRAW-F01` and listed in
[evidence/drawables/INDEX.md](../../../evidence/drawables/INDEX.md).

## Sample locators

The parent archive is `<GAME_ROOT>/levels.rpf`, row 5. That row is a nested
archive of 22,172,864 bytes with SHA-256
`450B6A5A95578A31133F686AE5D1D8151B4C7A38197F039895311D44742DBC96`.
It holds 316 rows: 92 of type ID 2 and 224 of type ID 3.

| Sample | Row | Type | Stored bytes | Decoded bytes | Chunks | Declared pages | System bytes | Graphics bytes |
| ------ | --: | ---: | -----------: | ------------: | -----: | -------------- | -----------: | -------------: |
| A      |   5 |    2 |        2,352 |         7,840 |      2 | 1 system, 1 graphics | 5,872 (`0x16F0`) | 1,968 (`0x7B0`) |
| B      |  10 |    2 |       54,752 |        90,624 |      3 | 1 system, 2 graphics | 16,624 (`0x40F0`) | 74,000 (`0x12110`) |

The CLI decoded both rows as chunked resources. The stored and decoded sizes,
the chunk counts and the page counts are observations. The system/graphics byte
boundary is **not stored**: it is inferred from the highest resolved system
pointer and from the graphics-base derivation in
[Geometry](#geometry-chain). For A, the page map is at system `0x14D0`; for B,
at `0x3BB0`. The declared pages equal the stored chunk counts (1+1=2 and 1+2=3),
so no page is missing. B's graphics length also splits as `0x10000 + 0x2110`,
consistent with its two declared graphics pages ([pages.md](../pages.md)); A has
one graphics page. The boundary is still a derived quantity, and claims that
depend on it are marked as sample-verified rather than stored.

## Header

The candidate offsets were checked against both samples. Values are
system-relative; pointer values are shown as stored.

| Offset | Size | Observation | Sample A | Sample B | Notes |
| -----: | ---: | ----------- | -------- | -------- | ----- |
| `+0x00` | 8 | Observed both | `0` | `0` | Zero in both; a parser SHOULD require it |
| `+0x08` | 8 | Observed both | `0x500014D0` | `0x50003BB0` | Page-map pointer; both in the system segment |
| `+0x10` | 8 | Observed both | `0x500012A0` | `0x50003960` | Shader-group pointer; both in range |
| `+0x18` | 8 | Observed both | `0` | `0` | Skeleton pointer candidate; null in both, so its populated form is **Unknown** |
| `+0x20` | 12 | Observed both | centre `(-0.000022, -0.004008, 1.521267)` | centre `(0, -0.021860, 0.000889)` | Three `f32`; the next field starts at `+0x2C` |
| `+0x2C` | 4 | Observed both | `0.707118` | `0.514099` | Equals half the AABB diagonal to the displayed precision in both samples |
| `+0x30` | 12 | Observed both | min `(-0.500022, -0.008038, 1.021267)` | min `(-0.293922, -0.042744, -0.420385)` | Three `f32`; the fourth word at `+0x3C` is `0.0` in both |
| `+0x40` | 12 | Observed both | max `(0.499978, 0.000021, 2.021267)` | max `(0.293922, -0.000976, 0.422164)` | Three `f32`; the fourth word at `+0x4C` is `0.0` in both |
| `+0x50` | 32 | Observed both | `[0x50001660, 0, 0, 0]` | `[0x50003FC0, 0x50003FE0, 0x50004000, 0x50004020]` | Four LOD-slot pointers; a zero slot is unpopulated |
| `+0x70` | 16 | Observed both | `[9998, 9998, 9998, 9998]` | `[8.994199, 12.711224, 17.967813, 9998]` | Four `f32`; the candidate's "one sample only" is contradicted |
| `+0x80` | 16 | Observed both | `[0x0000FF01, 0, 0, 0]` | `[0x0000FF01, 0x0000FF01, 0x0000FF01, 0x0000FF01]` | Four `u32`; one per LOD slot, nonzero for the populated slots in these samples; uninterpreted |
| `+0xA8` | 8 | Observed both | `0x50001420` | `0x50003E80` | Name pointer; the target is ASCII payload data and is not reproduced |
| `+0xB0` | 8 | Observed both | `0x50000D00` | `0x50002CA0` | List pointer; the candidate's "one sample only" is contradicted |
| `+0xB8` | 8 | Observed both | `0x103` | `0x103` | Uninterpreted |
| `+0xC0` | 8 | Observed both | `0` | `0` | Zero in both; later bytes were not interpreted |

The header is **not** fixed-size. Fields through `+0xB8` were observed and
`+0xC0` was zero in both samples, but no single header length is published. A
parser MUST treat every pointer slot as nullable and MUST NOT assume that the
bytes after the fields it knows are absent or zero.

Invariant in these two samples: the zero word at `+0x00`, the non-null page-map
and shader-group pointers at `+0x08` and `+0x10`, the bounds block at
`+0x20..+0x4F`, the non-null name pointer at `+0xA8`, the word `0x103` at
`+0xB8` and zero at `+0xC0`. Optional or nullable: the skeleton pointer at
`+0x18` (zero in both), the four LOD slots at `+0x50..+0x6F` (sparse in A), the
list pointer at `+0xB0` (present in both but still a nullable slot), the flag
words at `+0x80..+0x8F` and the shader-group `+0x08` pointer (absent in B).

### Candidate fields not adopted

- The candidate placed the four `f32` distances at `+0x70` in one sample only.
  They are present in both. In A all four are the sentinel `9998`; in B three
  are distances and the fourth is `9998`. Presence is confirmed, meaning is
  **Unknown**.
- The candidate placed the optional list pointer at `+0xB0` in one sample only.
  It is nonzero in both. The target shape is the same in both: five `{u64
  pointer, u16 count, u16 capacity}` records at `+0x00`, `+0x10`, `+0x20`,
  `+0x30` and `+0x40`; the first counts are 8 and 32. The meaning is **Unknown**.
- The genuine optional field found in this pair is the shader-group pointer at
  group `+0x08`: `0x500012E0` in A and `0` in B. A parser MUST treat it as
  optional or version-dependent.

## LOD and model chain

A populated LOD slot points to a 0x20-byte group. The group points to an array
of model pointers. Each model points to an array of geometry pointers.

| Record | Offset | Size | Observation | Notes |
| ------ | -----: | ---: | ----------- | ----- |
| LOD group | `+0x00` | 8 | Observed | `u64` pointer to the model pointer array |
| LOD group | `+0x08` | 2 | Observed | `u16` model count |
| LOD group | `+0x0A` | 2 | Observed | `u16` capacity; equals the count in both samples |
| LOD group | `+0x10` | 8 | Observed | Two `u16` shader indices; observed `[0, 1]` |
| LOD group | `+0x18` | 8 | Observed | `0` in both; uninterpreted |
| Model | `+0x00` | 8 | Observed | `0` in both |
| Model | `+0x08` | 8 | Observed | `u64` pointer to the geometry pointer array |
| Model | `+0x10` | 2 | Observed | `u16` geometry count |
| Model | `+0x12` | 2 | Observed | `u16` capacity; equals the count in both samples |
| Model | `+0x14` | 4 | Observed | `0x00020000` in all five models |
| Model | `+0x18` | 8 | Observed | AABB pointer; the target starts with the model min/max `f32` values |
| Model | `+0x20` | 8 | Observed | Shader-index array pointer; it aliases the owning LOD group's `+0x10` |
| Model | `+0x28` | 8 | Observed | `0` in both |
| Model | `+0x30` | 8 | Observed | Flags; values differ per model and are uninterpreted |

| Sample | Populated slots | Models | Geometries | Shader indices |
| ------ | --------------- | -----: | ---------: | -------------- |
| A | slot 0 only (three null) | 1 | 2 | `[0, 1]` |
| B | slots 0, 1, 2, 3 | 4 | 8 (two per model) | `[0, 1]` per model |

The reported observation is confirmed: A has one populated LOD slot and one
model with two geometries and a two-entry shader-index array. B has four
populated LOD slots, each with one model; in addition, each B model has two
geometries.

The LOD slot index is the index of one of the four header pointers. The model
list index is the index inside a group's model pointer array, in
`0..count-1`. They are distinct: each populated group in these samples has one
model, so every model list index is `0` while the LOD slot indices are `0` and
`0..3`. A parser MUST NOT use the LOD slot index as a model index.

## Geometry chain

A geometry record points at a vertex buffer and at an index descriptor. The
vertex buffer points at a graphics buffer and at a layout. The layout is a
52-entry structure-of-arrays description.

### Geometry record

| Offset | Size | Observation | Notes |
| -----: | ---: | ----------- | ----- |
| `+0x08` | 8 | Observed in 10/10 geometries | `u64` pointer to the vertex buffer record |
| `+0x30` | 8 | Observed in 10/10 | Nonzero `u64`; not a pointer because the upper half is nonzero; uninterpreted |
| `+0x40` | 8 | Observed in 10/10 | `u64` pointer to the index descriptor |
| other | | | Zero in the observed records; a parser MUST NOT require the record to end at `+0x48` |

### Vertex buffer and layout

| Offset | Size | Observation | Notes |
| -----: | ---: | ----------- | ----- |
| `+0x08` | 4 | Observed in 10/10 | `u32` element count |
| `+0x0C` | 2 | Observed in 10/10 | `u16` element unit; always `4`. Read as a `u32` at `+0x0C`, the value is `0x00090004`; the high half is the `9` below |
| `+0x0E` | 2 | Observed in 10/10 | `9`; uninterpreted |
| `+0x10` | 4 | Observed in 10/10 | `0x00001601`; uninterpreted |
| `+0x18` | 8 | Observed in 10/10 | Graphics pointer |
| `+0x28` | 8 | Observed in 10/10 | System pointer to the index descriptor `+0x20`; uninterpreted |
| `+0x40` | 8 | Observed in 10/10 | System pointer to the layout |

The layout is 0x13C bytes:

| Offset | Size | Observation | Notes |
| -----: | ---: | ----------- | ----- |
| `+0x00` | 208 | Observed in 10/10 | 52 `u32` byte offsets into the vertex buffer |
| `+0xD0` | 52 | Observed in 10/10 | One `u8` size per entry |
| `+0x104` | 52 | Observed in 10/10 | One `u8` format code per entry |
| `+0x138` | 4 | Observed in 10/10 | Packed vertex count (`count << 10` plus flags) |

An entry is present when its size or format is nonzero. Unused entries have
size `0`, format `0` and offset `0x80`. The present semantic indices are
`0, 4, 24, 28` for A geometry 1 and `0, 4, 24, 28, 29` for the other nine
geometries. The indices are positions in the table, not recovered names.

| Geometry | Vertex buffer | Elements | Bytes | Graphics | Layout | Packed | Vertices | Attributes |
| -------- | ------------: | -------: | ----: | -------: | -----: | -----: | -------: | ---------: |
| A-1 | `0x11B0` | 192 | 768 | `0x60000300` | `0x730` | `0x8051` | 32 | 4 |
| A-2 | `0x1250` | 56 | 224 | `0x60000600` | `0x870` | `0x1061` | 4 | 5 |
| B-1 | `0x34B0` | 5,444 | 21,776 | `0x60000000` | `0x1890` | `0xE1861` | 902 | 5 |
| B-2 | `0x3550` | 1,574 | 6,296 | `0x6000A2F0` | `0x19D0` | `0x40461` | 257 | 5 |
| B-3 | `0x35F0` | 3,272 | 13,088 | `0x60005510` | `0x1B10` | `0x87061` | 540 | 5 |
| B-4 | `0x3690` | 638 | 2,552 | `0x60010000` | `0x1C50` | `0x19461` | 101 | 5 |
| B-5 | `0x3730` | 1,712 | 6,848 | `0x60008830` | `0x1D90` | `0x46061` | 280 | 5 |
| B-6 | `0x37D0` | 446 | 1,784 | `0x60010A00` | `0x1ED0` | `0x11461` | 69 | 5 |
| B-7 | `0x3870` | 1,034 | 4,136 | `0x6000D380` | `0x2010` | `0x29C61` | 167 | 5 |
| B-8 | `0x3910` | 188 | 752 | `0x60011B00` | `0x2150` | `0x6861` | 26 | 5 |

Attribute entries for the ten geometries:

| Geometry set | Semantic indices | Offsets | Sizes | Format codes |
| ------------ | ---------------- | ------- | ----- | ------------ |
| A-1 | `0, 4, 24, 28` | `0x80, 0x180, 0x200, 0x280` | `8, 4, 4, 4` | `0x10, 0x29, 0x1C, 0x26` |
| A-2 and all B | `0, 4, 24, 28, 29` | first `0x80`; the rest are separated by `size × vertex_count` | `8, 4, 4, 4, 4` | `0x10, 0x29, 0x1C, 0x26, 0x26` |

The per-geometry offsets in the second set are determined by the vertex count;
for example B-1 starts at `0x80`, `0x1CB0`, `0x2AC8`, `0x38E0` and `0x46F8`.
The format codes are observable bytes, not decoded formats.

### Buffer sizing

For all ten geometries:

- `element_count × element_unit` equals the declared buffer bytes.
- `max(offset + size × vertex_count)` over the present entries equals the same
  declared buffer bytes exactly.
- `vertex_count × sum(size)` equals `declared bytes − 0x80`. The first attribute
  starts at offset `0x80`, and the 0x80-byte prefix before it is not described
  by the table.

Examples: A-1 declares 768 bytes; 32 vertices with sizes 8+4+4+4 = 20 bytes
give 640 bytes, and the attributes end at 768 because the first array starts at
`0x80`. B-1 declares 21,776 bytes; 902 vertices with sizes 24 give 21,648
bytes, again 128 bytes short of the declared size. The prefix is **Unknown**.

Vertex positions were **not** checked against the AABB. The position semantic
and the format codes are not established, so a plausible point cloud would not
validate the reading.

The candidate's packed form `count << 10 | 1` is **contradicted**. The observed
low ten bits are `0x51` (A-1) and `0x61` (the other nine); the count is the high
bits. The low bits are uninterpreted flags. A parser MUST NOT require the low
bits to be `1`.

The candidate also read the first 16 `u32` words at the graphics pointer as
attribute descriptors of the form `format | size << 3 | offset << 7`. That was
**not observed** (DRAW-F21). Each vertex-buffer graphics target begins with a
0x80-byte prefix whose first four bytes are `42 40 00 00`; the attribute table
is the 52-entry layout reached from the vertex buffer's `+0x40` pointer. The
first 16 words were not parsed as descriptors and the packed form was not used.

### Graphics base

The graphics base is **not stored**. It is derived from two or more graphics
pointers whose targets are identified in the reconstructed row:

- A has vertex-buffer graphics pointers `0x60000300` and `0x60000600`. Their
  targets are at file offsets `0x19F0` and `0x1CF0`; both start with the four
  bytes `42 40 00 00`. The target difference `0x300` equals the pointer
  difference, so the base is `0x19F0 − 0x300 = 0x16F0`.
- B has eight vertex-buffer graphics pointers. `0x60000000` targets `0x40F0`
  and `0x6000A2F0` targets `0xE3E0`; both start with `42 40 00 00`. The bases
  agree at `0x40F0`, and all eight pointers then land on the same marker.

`42 40 00 00` is an observation, not a format signature. The base is
over-determined by independent pointers in both samples; the tool requires at
least two supporting pointers before reporting one.

### Index descriptor and index buffer

The geometry `+0x40` pointer targets a 0x20-byte descriptor:

| Offset | Size | Observation | Notes |
| -----: | ---: | ----------- | ----- |
| `+0x00` | 8 | Observed in 10/10 | System pointer to the index-buffer record |
| `+0x08` | 2 | Observed in 10/10 | `u16` cluster count |
| `+0x0A` | 2 | Observed in 10/10 | Uninterpreted |
| `+0x0C` | 4 | Observed in 10/10 | Uninterpreted |
| `+0x10` | 16 | Observed in 10/10 | Zero |

The descriptor is followed at `+0x20` by another 0x20-byte record whose `+0x10`
word is the constant `0xFFFFFFFFFFFF0214`. The vertex buffer's `+0x28` pointer
targets that record. Its meaning is **Unknown**.

The index-buffer record has the same shape as a vertex buffer:

| Offset | Size | Observation | Notes |
| -----: | ---: | ----------- | ----- |
| `+0x08` | 4 | Observed in 10/10 | `u32` element count |
| `+0x0C` | 2 | Observed in 10/10 | `u16` element unit; always `4` |
| `+0x18` | 8 | Observed in 10/10 | Graphics pointer to the index bytes |
| `+0x28` | 8 | Observed in 10/10 | System pointer; uninterpreted |

| Geometry | Clusters | Elements | Bytes | Graphics range | In bounds |
| -------- | -------: | -------: | ----: | -------------- | --------- |
| A-1 | 1 | 40 | 160 | `0x6E0..0x780` | yes |
| A-2 | 1 | 12 | 48 | `0x780..0x7B0` | yes; ends at the graphics end |
| B-1 | 9 | 1,532 | 6,128 | `0xBB90..0xD380` | yes |
| B-2 | 4 | 660 | 2,640 | `0xF1A0..0xFBF0` | yes |
| B-3 | 5 | 892 | 3,568 | `0xE3B0..0xF1A0` | yes |
| B-4 | 2 | 216 | 864 | `0x117A0..0x11B00` | yes |
| B-5 | 3 | 424 | 1,696 | `0x11100..0x117A0` | yes |
| B-6 | 1 | 148 | 592 | `0x11DF0..0x12040` | yes |
| B-7 | 2 | 252 | 1,008 | `0xFBF0..0xFFE0` | yes |
| B-8 | 1 | 52 | 208 | `0x12040..0x12110` | yes; ends at the graphics end |

No triangles were reconstructed. The element counts, byte sizes and bounds are
structural; the cluster count is the only index field read as a count.

The walked vertex-buffer and index-buffer ranges do not cover every graphics
byte. In A they cover `0x300..0x7B0`; the first `0x300` bytes of the graphics
segment are not addressed by the walked pointers. In B the ranges are
interleaved with small gaps and do not start at `0x0`. The unaddressed bytes
were not interpreted.

## Materials (structure only)

This section is **unvalidated beyond structure**. No key is resolved to a
texture, no parameter hash is named and no material name is claimed. The
`u32` at shader `+0x00` is not a name.

### Chain

The header `+0x10` pointer targets a 0x20-byte shader group:

| Offset | Size | Observation | Notes |
| -----: | ---: | ----------- | ----- |
| `+0x08` | 8 | Observed A only | `0x500012E0` in A, `0` in B; optional |
| `+0x10` | 8 | Observed both | Shader pointer array |
| `+0x18` | 2 | Observed both | `u16` shader count |
| `+0x1A` | 2 | Observed both | `u16` capacity |

A: group `0x12A0`, count 2, array `0x16B0`, shaders `0x1320` and `0x1360`.
B: group `0x3960`, count 2, array `0x4060`, shaders `0x39A0` and `0x39E0`.

A shader is a 0x40-byte record:

| Offset | Size | Observation | Notes |
| -----: | ---: | ----------- | ----- |
| `+0x00` | 4 | Observed both | Uninterpreted `u32`; not a name |
| `+0x04` | 4 | Observed both | Constant `0x6D657461` |
| `+0x08` | 8 | Observed both | Uninterpreted system pointer |
| `+0x10` | 8 | Observed both | Texture-slot table pointer |
| `+0x20` | 8 | Observed both | Parameter-table pointer |

### Parameter table

| Offset | Size | Observation | Notes |
| -----: | ---: | ----------- | ----- |
| `+0x00` | 1 | Observed both | `1`; uninterpreted |
| `+0x01` | 1 | Observed both | Texture-parameter count |
| `+0x02` | 2 | Observed both | `0` |
| `+0x04` | 2 | Observed both | Total parameter count |
| `+0x06` | 2 | Observed both | `0x0800`; uninterpreted |
| `+0x08` | `8 × total` | Observed both | `{u32 name hash, u32 packed}` pairs |

The first `texture count` pairs are the texture parameters. Their `packed`
values are `0, 4, 8, ...`, i.e. four times the slot index. The remaining pairs
are non-texture parameters with other packed values. A declared parameter is
**not** a bound texture.

### Slot table, texture record and name record

The slot table is an array of `u64` pointers. In the four observed tables it
holds one entry per texture parameter: 6, 6, 7 and 6. A null entry is a declared
but unbound slot. A non-null entry targets a 0x50-byte texture record; its
`+0x30` pointer targets a 0x20-byte name record. The name record has a string
pointer at `+0x00` and a 64-bit key at `+0x08`. The string is payload text and is
not reproduced; the key is not resolved.

### Counts

| Sample | Shader | Texture parameters | Total parameters | Bound slots | Unbound slots | Distinct keys |
| ------ | -----: | -----------------: | ---------------: | ----------: | ------------: | ------------: |
| A | 0 | 6 | 55 | 5 | 1 | 5 |
| A | 1 | 6 | 54 | 4 | 2 | 4 |
| B | 0 | 7 | 68 | 5 | 2 | 5 |
| B | 1 | 6 | 54 | 4 | 2 | 4 |

The two A parameter tables carry the same six texture-parameter `u32` hashes:
`0xC8E8C282`, `0x739E3D0D`, `0x2C8D7182`, `0x0CD27763`, `0xC6F46E79` and
`0x1E77BF4C`. They are reported as uninterpreted values, not names.

In A shader 0, slot 3 is null, so the fourth texture parameter is declared but
unbound. In A shader 1, slots 2 and 3 are null. The union of the two A shaders
has six distinct keys; shader 0 has five and shader 1 has four. The reported
"six texture parameters and 55 total parameters; five bound slots and one
declared-but-unbound slot; five distinct keys" matches A shader 0. The second
shader is a second counterexample to "parameter count equals bound count".

No local texture store was reached from these samples. Resolving a key depends
on a resource-side texture dictionary or store reference path that was not
found. That dependency is **Unknown**.

## Optional and version-dependent fields

- The header `+0x70` distance block and the `+0xB0` list pointer are present in
  both samples; the candidate's "one sample only" is rejected for this pair.
- The shader group `+0x08` pointer is nonzero in A and zero in B. It is optional.
- The header `+0x18` skeleton pointer is zero in both; its populated form was
  not observed.
- LOD slots are sparse: A has three null slots, B has none.
- The `+0x80` words are `0x0000FF01` for populated slots and `0` for null slots
  in these samples; a parser MUST NOT require a fixed count of nonzero words.
- The `+0x70` values are sentinel `9998` in A; a parser MUST NOT read the block
  as absent or as real distances without checking the value.

A parser MUST therefore treat pointer slots as nullable, LOD distance values as
possibly sentinel, and the header as variable-length. No single fixed header
size is published.

## Status

| Sample | Reconstruction state | Verified chain elements | Structure only | Remaining dependencies |
| ------ | -------------------- | ----------------------- | -------------- | ---------------------- |
| A (row 5) | Decoded payload; page map 1/1; 2 chunks; system/graphics split `0x16F0`/`0x7B0` derived | Header, one LOD slot, one model, two geometries, both vertex buffers, layout entries, buffer sizes, graphics base, index bounds, shader group and two parameter tables | Attribute semantics, format codes, 0x80 prefix, 0x4042 marker, index cluster layout, material keys, parameter meanings | Texture store/key resolution; engine record meanings; independent re-inflation |
| B (row 10) | Decoded payload; page map 1/2; 3 chunks; split `0x40F0`/`0x12110` derived | Header, four LOD slots, four models, eight geometries, eight vertex buffers, layout entries, buffer sizes, graphics base, index bounds, shader group and two parameter tables | Same as A | Same as A |

The drawable is **not** reconstructed in the engine sense. The decoded payload
is split into two segments at an inferred boundary. No texture is resolved.

"Verified" in the status table means the bytes, pointer targets and counts were
checked. It does not mean the field meanings are known; the structure-only
column lists what remains uninterpreted.

## Unknowns

- The meaning of the 52-entry semantic indices and the `u8` format codes.
- The 0x80-byte prefix before the first vertex attribute array.
- The `42 40 00 00` vertex-buffer marker, the `0x00001601` vertex-buffer word and
  the `0x00020000` model word.
- The model flags at `+0x30`, the geometry `+0x30` word and the
  `0xFFFFFFFFFFFF0214` constant.
- The index descriptor `+0x0A` and `+0x0C` fields, the cluster layout and how the
  index bytes form triangles.
- The parameter-table `+0x00` and `+0x06` words, the shader `+0x08` pointer, the
  shader `+0x00` word, the name-record `+0x10`/`+0x18` fields and the 64-bit key
  namespace.
- The header `+0xB0` list and the header `+0x80` flag words.
- The LOD distance sentinel and the `+0x70` values in A.
- Whether any of these layouts change with another type ID, archive family or
  build. Only two rows of one nested archive were inspected.

## Limits

- Two rows, one nested archive, one build. The cross-sample evidence is within
  this population.
- Type ID 2 is the local CLI assignment, not a format identity.
- The stored rows were decoded by the CLI; the zlib streams were not
  independently re-inflated for this document.
- The system/graphics boundary is derived from pointers and page counts, not
  stored.
- No engine code path was traced. Pointer validation, allocation and runtime
  meanings remain **Unknown**.
- Payload ASCII names are not reproduced.
- The material section is structural only. No key, texture or material name is
  resolved.
