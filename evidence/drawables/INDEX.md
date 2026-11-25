# Drawable evidence index

Payload observations from the Scarlett build
[e95020b2](../../builds/gta-vi/scarlett-e95020b2/README.md). No executable code
path was traced for this subject. Every finding is **Private-evidence
supported**: it is checkable against a local installation but not from this
repository alone. The synthetic fixtures validate the tool, not native
semantics.

The subject is the resource payload behind the local type ID 2. Findings are
cited from [formats/resources/drawables/README.md](../../formats/resources/drawables/README.md).

## Samples

The parent archive is `<GAME_ROOT>/levels.rpf`, row 5. That row is a nested
archive with SHA-256
`450B6A5A95578A31133F686AE5D1D8151B4C7A38197F039895311D44742DBC96`
and 22,172,864 stored bytes. It holds 316 rows: 92 of type ID 2 and 224 of type
ID 3.

| Sample | Row | Type | Stored | Decoded | Chunks | Pages | System | Graphics |
| ------ | --: | ---: | -----: | ------: | -----: | ----- | -----: | -------: |
| A | 5 | 2 | 2,352 | 7,840 | 2 | 1 system, 1 graphics | 5,872 (`0x16F0`) | 1,968 (`0x7B0`) |
| B | 10 | 2 | 54,752 | 90,624 | 3 | 1 system, 2 graphics | 16,624 (`0x40F0`) | 74,000 (`0x12110`) |

The page map offsets are system `0x14D0` for A and `0x3BB0` for B. The declared
pages equal the chunk counts, so no page is missing. The system/graphics byte
boundary is not stored; it is inferred and independently checked by the
graphics-base derivation (DRAW-F15).

## Evidence types

| Type | Use in this index |
| ---- | ----------------- |
| `BINARY` | Decoded payload bytes: offsets, widths, counts and structural relations |
| `CROSS_SAMPLE` | The same property checked on both samples, or on all walked geometries |
| `SYNTHETIC` | The inspector's fixtures. They validate the tool, not native behavior, and support no finding here |

The CLI supplied the decoded rows. The byte-level results come from the
published inspector, which reads the decoded payload and does not use
application code. The inspector's agreement with the CLI on sizes and page
counts is consistency, not independent evidence for the format. No zlib stream
was re-inflated independently for this index.

## Findings

| ID | Claim | Evidence | Confidence | Limits |
| -- | ----- | -------- | ---------- | ------ |
| DRAW-F01 | The nested archive has 316 rows: 92 type 2 and 224 type 3. Rows 5 and 10 are type 2, decode to 7,840 and 90,624 bytes, use 2 and 3 chunks, and declare 1/1 and 1/2 system/graphics pages. | `BINARY`, `CROSS_SAMPLE` | Confirmed (sample) | One nested archive, two rows |
| DRAW-F02 | The header has a zero `u64` at `+0x00`, a system page-map pointer at `+0x08`, a shader-group pointer at `+0x10`, a zero skeleton pointer at `+0x18`, four LOD-slot pointers at `+0x50`, a name pointer at `+0xA8`, a list pointer at `+0xB0`, `0x103` at `+0xB8` and zero at `+0xC0`. | `BINARY`, `CROSS_SAMPLE` | Confirmed (bytes); field meanings partly Unknown | Two samples; the populated skeleton form was not observed |
| DRAW-F03 | The centre at `+0x20`, radius at `+0x2C`, AABB minimum at `+0x30` and AABB maximum at `+0x40` are three/two/three/three `f32` fields; the radius equals half the AABB diagonal to the displayed precision in both samples. The model AABB targets repeat min/max values consistent with the drawable AABB: A's single model matches within about 2e-4, and B's four model bounds lie inside the drawable bounds. | `BINARY` | Confirmed (arithmetic); Probable (bounds reading) | Two samples, five models; vertex positions were not checked against the AABB |
| DRAW-F04 | Four LOD-slot pointers occupy `+0x50..+0x6F`. A has one populated slot (slot 0) and three null slots; B has four populated slots. A zero slot is unpopulated. | `BINARY`, `CROSS_SAMPLE` | Confirmed | Two samples |
| DRAW-F05 | A populated LOD slot points to a 0x20-byte group with a model pointer array, a `u16` count and capacity at `+0x08`, a two-`u16` shader-index value at `+0x10`, and a zero tail. A has one model with two geometries; B has four models with two geometries each. The LOD slot index is distinct from the model list index. | `BINARY`, `CROSS_SAMPLE` | Confirmed (bytes and counts) | Five models, ten geometries |
| DRAW-F06 | A model is at least 0x38 bytes: geometry pointer array at `+0x08`, `u16` count and capacity at `+0x10`, `0x00020000` at `+0x14`, AABB pointer at `+0x18`, shader-index pointer at `+0x20`, zero at `+0x28` and flags at `+0x30`. The `+0x20` pointer aliases the owning LOD group's `+0x10`. | `BINARY`, `CROSS_SAMPLE` | Confirmed (offsets); Unknown (flags and `+0x14`) | Five models |
| DRAW-F07 | The four `f32` at `+0x70` are present in both samples. A holds the sentinel `9998` four times; B holds 8.994199, 12.711224, 17.967813 and 9998. The candidate's "one sample only" is contradicted. | `BINARY`, `CROSS_SAMPLE` | Confirmed (presence); Unknown (meaning) | Two samples |
| DRAW-F08 | The `+0xB0` list pointer is nonzero in both samples and targets five `{u64 pointer, u16 count, u16 capacity}` records. The first counts are 8 in A and 32 in B. The candidate's "one sample only" is contradicted. | `BINARY`, `CROSS_SAMPLE` | Confirmed (presence and shape); Unknown (meaning) | Two samples |
| DRAW-F09 | In system data, A holds 81 system-shaped and 5 graphics-shaped `u64` values with 0 outside; B holds 171 and 17 with one graphics-shaped value outside at system `0x3EE8` (`0x606B29BE`). That value sits in a name-record table and is best read as a 32-bit hash, not a pointer. | `BINARY`, `CROSS_SAMPLE` | Confirmed (counts); Probable (false-positive identity) | Two samples; the sweep matches the pointer encoding, not engine validation |
| DRAW-F10 | A geometry record points at a vertex buffer at `+0x08` and an index descriptor at `+0x40`, and carries a nonzero non-pointer `u64` at `+0x30`. The offsets hold in all ten geometries. | `BINARY`, `CROSS_SAMPLE` | Confirmed (offsets) | Ten geometries |
| DRAW-F11 | A vertex buffer declares an element count at `+0x08`, an element unit of `4` at `+0x0C`, `9` at `+0x0E`, `0x00001601` at `+0x10`, a graphics pointer at `+0x18`, a system pointer at `+0x28` and a layout pointer at `+0x40`. The offsets hold in all ten geometries. | `BINARY`, `CROSS_SAMPLE` | Confirmed (offsets and values); Unknown (`+0x0E`, `+0x10`, `+0x28`) | Ten geometries |
| DRAW-F12 | The layout has 52 `u32` offsets at `+0x00`, 52 `u8` sizes at `+0xD0`, 52 `u8` format codes at `+0x104` and a packed count at `+0x138`. Entries are present when size or format is nonzero; unused entries have size 0, format 0 and offset `0x80`. Present semantic indices are `0,4,24,28` for A-1 and `0,4,24,28,29` for the other nine geometries. | `BINARY`, `CROSS_SAMPLE` | Confirmed (positions and counts); Unknown (semantic and format meanings) | Ten geometries |
| DRAW-F13 | The packed word is `vertex_count << 10` plus flags; the observed values are `0x8051` (32 vertices), `0x1061` (4) and eight larger values. The low bits are `0x51` or `0x61`, not `1`. The candidate's `count << 10` plus `1` is contradicted. | `BINARY`, `CROSS_SAMPLE` | Confirmed (arithmetic); Unknown (flags) | Ten geometries |
| DRAW-F14 | For all ten geometries, `element_count × element_unit` equals `max(offset + size × vertex_count)` exactly. `vertex_count × sum(size)` equals the declared bytes minus `0x80`, so the first attribute array starts at `0x80` and the prefix is not described by the table. | `BINARY`, `CROSS_SAMPLE` | Confirmed (arithmetic) | Ten geometries; the prefix is not interpreted |
| DRAW-F15 | The graphics base is not stored. A two-pointer derivation gives `0x16F0` for A (`0x60000300`/`0x60000600` target `0x19F0`/`0x1CF0`); B gives `0x40F0` from two of its eight pointers (`0x60000000`/`0x6000A2F0` target `0x40F0`/`0xE3E0`). Every vertex-buffer target starts with `42 40 00 00`. | `BINARY`, `CROSS_SAMPLE` | Confirmed (base); Unknown (marker meaning) | Two samples; the marker is an observation, not a format signature |
| DRAW-F16 | The index descriptor is 0x20 bytes with an index-buffer pointer at `+0x00`, a `u16` cluster count at `+0x08`, uninterpreted `+0x0A` and `+0x0C` fields, and zeros at `+0x10`. A second 0x20-byte record follows at `+0x20` with the constant `0xFFFFFFFFFFFF0214` at its `+0x10`. The index-buffer record declares an element count at `+0x08`, unit `4` at `+0x0C` and a graphics pointer at `+0x18`. All ten index ranges lie inside their graphics segment; A-2 and B-8 end exactly at the segment end. | `BINARY`, `CROSS_SAMPLE` | Confirmed (offsets, counts and bounds); Unknown (cluster layout) | Ten geometries; no triangles reconstructed |
| DRAW-F17 | The shader group has an optional pointer at `+0x08`, a shader pointer array at `+0x10`, and `u16` count and capacity at `+0x18`. A shader is 0x40 bytes with an uninterpreted `u32` at `+0x00`, the constant `0x6D657461` at `+0x04`, a system pointer at `+0x08`, a slot table at `+0x10` and a parameter table at `+0x20`. The parameter table has a texture count at `+0x01`, a total count at `+0x04`, and `{u32 hash, u32 packed}` pairs from `+0x08`. A non-null slot targets a texture record whose `+0x30` name record holds a string pointer at `+0x00` and a 64-bit key at `+0x08`. The slot table has one entry per texture parameter in the four observed tables. | `BINARY`, `CROSS_SAMPLE` | Confirmed (structure and counts); Unknown (all meanings) | Two samples, four shaders |
| DRAW-F18 | In A, shader 0 declares 6 texture parameters and 55 total, binds 5 slots and leaves 1 unbound, with 5 distinct keys. Shader 1 declares 6 and 54, binds 4 and leaves 2 unbound, with 4 distinct keys. The union has 6 distinct keys. The two tables carry the same six texture-parameter `u32` hashes. | `BINARY`, `CROSS_SAMPLE` | Confirmed (counts); Unknown (meanings) | A is counted; B gives 7/68/5/2/5 and 6/54/4/2/4 as a structure check. Declared is not bound |
| DRAW-F19 | No key was resolved to a texture and no texture store was reached from these samples. Resolution depends on a resource-side texture-dictionary or store-reference path that was not found. | `BINARY` (absence), `CROSS_SAMPLE` | Confirmed (absence in samples); Unknown (dependency) | No texture dependency path |
| DRAW-F20 | The shader-group `+0x08` pointer is nonzero in A and zero in B. The header skeleton `+0x18` is null in both. LOD slots are sparse. The header distance values can be the sentinel `9998`. No single fixed header size is established. | `BINARY`, `CROSS_SAMPLE` | Confirmed (presence); Unknown (versioning rule) | Two samples |
| DRAW-F21 | The first 16 `u32` words at a graphics pointer were not attribute descriptors. Each vertex-buffer target begins with a 0x80-byte prefix whose first four bytes are `42 40 00 00`; the attributes are the separate offset, size and format arrays in the layout at vertex buffer `+0x40`. The candidate packed form (`format`, `size << 3`, `offset << 7`) was not observed. | `BINARY`, `CROSS_SAMPLE` | Rejected (candidate descriptor reading) | Ten geometries; the prefix is not interpreted |

## Counters and negative results

- **The candidate's `+0x70` "one sample only" is rejected.** The block is
  present in both samples (DRAW-F07).
- **The candidate's `+0xB0` "one sample only" is rejected.** The pointer is
  nonzero in both samples (DRAW-F08).
- **The candidate's packed `|1` is rejected.** The low bits are `0x51` or
  `0x61` (DRAW-F13).
- **Parameter count is not bound texture count.** A shader 0 has one unbound
  slot; shader 1 has two (DRAW-F18).
- **The one-LOD and four-LOD observations are confirmed.** A has one populated
  LOD slot and one model with two geometries; B has four populated slots and
  four models. B additionally gives each model two geometries (DRAW-F04,
  DRAW-F05).
- **One graphics-shaped value is outside its segment.** It is a 32-bit hash in a
  name-record table, not a pointer (DRAW-F09).
- **No texture is resolved.** No local texture store was reached (DRAW-F19).

## Reproduction

`<GAME_ROOT>`, `<EXECUTABLE>` and `<WORK>` are local inputs. Payloads and
decoded resources are not part of this repository.

```text
lforge archive extract <GAME_ROOT>/levels.rpf --row 5 --output <WORK>/nested.rpf --executable <EXECUTABLE>
lforge archive ls <WORK>/nested.rpf --executable <EXECUTABLE> --limit 316 --json
lforge archive extract <WORK>/nested.rpf --row 5 --output <WORK>/draw5.bin --executable <EXECUTABLE>
lforge archive extract <WORK>/nested.rpf --row 10 --output <WORK>/draw10.bin --executable <EXECUTABLE>
python tools/drawables/drawable_inspect.py inspect --file <WORK>/draw5.bin --system-length 0x16F0 --json
python tools/drawables/drawable_inspect.py inspect --file <WORK>/draw10.bin --system-length 0x40F0 --json
python -m unittest discover -s tools/drawables/tests
```

The `archive ls` output supplies the row type IDs, stored sizes, decoded sizes
and chunk counts. The inspector supplies the header, LOD/model/geometry chain,
layout entries, graphics base, index bounds and material counts. The
system-length values are derived from the graphics targets and the page counts,
not from a stored field.

## Limits

- One build, one nested archive, two rows.
- The cross-sample evidence covers two drawables, five models and ten
  geometries.
- The stored rows were decoded by the CLI; no independent re-inflation was
  performed.
- The system/graphics boundary is derived, not stored.
- No engine code path was traced.
- ASCII payload names are not reproduced.
- The material section is structure-only; no key, texture or material name is
  resolved.
- The inspector's synthetic tests are `SYNTHETIC` and support no native claim.

## Candidate corrections

The candidate field table and the private measurements were checked, not
adopted. Corrections that change a structural rule are recorded in
[research-history.md](research-history.md).
