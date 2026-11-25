# Drawable evidence index

Payload observations from the Scarlett build
[e95020b2](../../builds/gta-vi/scarlett-e95020b2/README.md). No executable code
path was traced for this subject. Every finding is **Private-evidence
supported**: it is checkable against a local installation but not from this
repository alone. The synthetic fixtures validate the tool, not native
semantics.

The subject is the decoded payload structure observed in two named rows that
carry local type ID 2, plus recovered resources from the same `levels.rpf` used
for the AABB and material checks. The type ID is a local CLI assignment, not a
format identity. Findings are cited from
[formats/resources/drawables/README.md](../../formats/resources/drawables/README.md).

## Samples

The parent archive is `<GAME_ROOT>/levels.rpf`, row 5. That row is a nested
archive with SHA-256
`450B6A5A95578A31133F686AE5D1D8151B4C7A38197F039895311D44742DBC96`
and 22,172,864 stored bytes. It holds 316 rows: 92 of local type ID 2 and 224 of
local type ID 3.

| Sample | Row | Local type | Stored | Decoded | Chunks | Pages | System | Graphics |
| ------ | --: | ---------: | -----: | ------: | -----: | ----- | -----: | -------: |
| A | 5 | 2 | 2,352 | 7,840 | 2 | 1 system, 1 graphics | 5,872 (`0x16F0`) | 1,968 (`0x7B0`) |
| B | 10 | 2 | 54,752 | 90,624 | 3 | 1 system, 2 graphics | 16,624 (`0x40F0`) | 74,000 (`0x12110`) |

The page map offsets are system `0x14D0` for A and `0x3BB0` for B. The page
counts match the chunk counts and the sample B page-size split is consistent.
The system/graphics byte boundary is not stored; it is inferred and
independently checked by the graphics-base derivation (DRAW-F15).

## Evidence types

| Type | Use in this index |
| ---- | ----------------- |
| `BINARY` | Decoded payload bytes: offsets, widths, counts and structural relations |
| `CROSS_SAMPLE` | The same property checked on both samples, or on all walked geometries |
| `SYNTHETIC` | The inspector's fixtures. They validate the tool, not native behavior, and support no finding here |

The CLI supplied the decoded rows. The published inspector reproduces the chain
and count findings marked `inspector` in [Method per finding](#method-per-finding).
The bounds arithmetic, the `+0xB0` list shape, the system-wide pointer sweep and
the texture-store absence are manual byte observations and are not produced by
the inspector. The inspector's agreement with the CLI on sizes and page counts is
consistency, not independent evidence for the format. No zlib stream was
re-inflated independently for this index.

## Findings

| ID | Claim | Evidence | Confidence | Limits |
| -- | ----- | -------- | ---------- | ------ |
| DRAW-F01 | The nested archive has 316 rows: 92 of local type 2 and 224 of local type 3. Rows 5 and 10 carry local type 2, decode to 7,840 and 90,624 bytes, use 2 and 3 chunks, and declare 1/1 and 1/2 system/graphics pages. | `BINARY`, `CROSS_SAMPLE` | Confirmed (sample) | One nested archive, two rows |
| DRAW-F02 | The header has a zero `u64` at `+0x00`, a system page-map pointer at `+0x08`, a shader-group pointer at `+0x10`, a zero skeleton pointer at `+0x18`, four LOD-slot pointers at `+0x50`, a name pointer at `+0xA8`, a list pointer at `+0xB0`, `0x103` at `+0xB8` and zero at `+0xC0`. | `BINARY`, `CROSS_SAMPLE` | Confirmed (bytes); field meanings partly Unknown | Two samples; the populated skeleton form was not observed |
| DRAW-F03 | The centre at `+0x20` is three `f32`, the radius at `+0x2C` is one `f32`, and the AABB minimum at `+0x30` and maximum at `+0x40` are three `f32` each; the radius equals half the AABB diagonal to the displayed precision in both samples. The model `+0x18` target is a record array, not one box (DRAW-F22); record 0 equals the header AABB in the sampled models. | `BINARY` | Confirmed (arithmetic); Probable (bounds reading) | Two samples, five models; vertex positions were not checked against the AABB |
| DRAW-F04 | Four LOD-slot pointers occupy `+0x50..+0x6F`. A has one populated slot (slot 0) and three null slots; B has four populated slots. A zero slot is unpopulated. | `BINARY`, `CROSS_SAMPLE` | Confirmed | Two samples |
| DRAW-F05 | A populated LOD slot points to a 0x20-byte group with a model pointer array, a `u16` count and capacity at `+0x08`, a two-`u16` shader-index value at `+0x10`, and a zero tail. A has one model with two geometries; B has four models with two geometries each. The LOD slot index is distinct from the model list index. | `BINARY`, `CROSS_SAMPLE` | Confirmed (bytes and counts) | Five models, ten geometries |
| DRAW-F06 | A model is at least 0x38 bytes: geometry pointer array at `+0x08`, `u16` count and capacity at `+0x10`, `0x00020000` at `+0x14`, AABB-array pointer at `+0x18`, shader-index pointer at `+0x20`, zero at `+0x28` and flags at `+0x30`. The `+0x20` pointer aliases the owning LOD group's `+0x10`. The `+0x18` target is the record array in DRAW-F22. | `BINARY`, `CROSS_SAMPLE` | Confirmed (offsets); Unknown (flags and `+0x14`) | Five models |
| DRAW-F07 | The four `f32` at `+0x70` are present in both samples. A holds the sentinel `9998` four times; B holds 8.994199, 12.711224, 17.967813 and 9998. The candidate's "one sample only" is contradicted. | `BINARY`, `CROSS_SAMPLE` | Confirmed (presence); Unknown (meaning) | Two samples |
| DRAW-F08 | The `+0xB0` list pointer is nonzero in both samples and targets five `{u64 pointer, u16 count, u16 capacity}` records. The first counts are 8 in A and 32 in B. The candidate's "one sample only" is contradicted. | `BINARY`, `CROSS_SAMPLE` | Confirmed (presence and shape); Unknown (meaning) | Two samples |
| DRAW-F09 | In system data, A holds 81 system-shaped and 5 graphics-shaped `u64` values with 0 outside; B holds 171 and 17 with one graphics-shaped value outside at system `0x3EE8` (`0x606B29BE`). That value sits in a name-record table and is best read as a 32-bit hash, not a pointer. | `BINARY`, `CROSS_SAMPLE` | Confirmed (counts); Probable (false-positive identity) | Two samples; the sweep matches the pointer encoding, not engine validation |
| DRAW-F10 | A geometry record points at a vertex buffer at `+0x08` and an index descriptor at `+0x40`, and carries a nonzero non-pointer `u64` at `+0x30`. The offsets hold in all ten geometries. | `BINARY`, `CROSS_SAMPLE` | Confirmed (offsets) | Ten geometries |
| DRAW-F11 | A vertex buffer declares an element count at `+0x08`, an element unit of `4` at `+0x0C`, `9` at `+0x0E`, `0x00001601` at `+0x10`, a graphics pointer at `+0x18`, a system pointer at `+0x28` and a layout pointer at `+0x40`. The offsets hold in all ten geometries. | `BINARY`, `CROSS_SAMPLE` | Confirmed (offsets and values); Unknown (`+0x0E`, `+0x10`, `+0x28`) | Ten geometries |
| DRAW-F12 | The layout has 52 `u32` offsets at `+0x00`, 52 `u8` sizes at `+0xD0`, 52 `u8` format codes at `+0x104` and a packed count at `+0x138`. Entries are present when size or format is nonzero; unused entries have size 0, format 0 and offset `0x80`. Present semantic indices are `0,4,24,28` for A-1 and `0,4,24,28,29` for the other nine geometries. | `BINARY`, `CROSS_SAMPLE` | Confirmed (positions and counts); Unknown (semantic and format meanings) | Ten geometries |
| DRAW-F13 | The packed word is `vertex_count << 10` plus flags; the observed values are `0x8051` (32 vertices), `0x1061` (4) and eight larger values. The low bits are `0x51` or `0x61`, not `1`. The candidate's `count << 10` plus `1` is contradicted. | `BINARY`, `CROSS_SAMPLE` | Confirmed (arithmetic); Unknown (flags) | Ten geometries |
| DRAW-F14 | For all ten geometries, `element_count × element_unit` equals `max(offset + size × vertex_count)` exactly. `vertex_count × sum(size)` equals the declared bytes minus `0x80`, so the first attribute array starts at `0x80` and the prefix is not described by the table. | `BINARY`, `CROSS_SAMPLE` | Confirmed (arithmetic) | Ten geometries; the prefix is not interpreted |
| DRAW-F15 | The graphics base is not stored. A two-pointer derivation gives `0x16F0` for A (`0x60000300`/`0x60000600` target `0x19F0`/`0x1CF0`); B gives `0x40F0` from two of its eight pointers (`0x60000000`/`0x6000A2F0` target `0x40F0`/`0xE3E0`). Every vertex-buffer target starts with `42 40 00 00`. | `BINARY`, `CROSS_SAMPLE` | Confirmed (base); Unknown (marker meaning) | Two samples; the marker is an observation, not a format signature |
| DRAW-F16 | The index descriptor is 0x20 bytes with an index-buffer pointer at `+0x00`, a `u16` cluster count at `+0x08`, count A at `+0x0A`, count B in bits 8..23 of `+0x0C`, and zeros at `+0x10` (DRAW-F25). A second 0x20-byte record follows at `+0x20` with the constant `0xFFFFFFFFFFFF0214` at its `+0x10`. The index-buffer record declares an element count at `+0x08`, unit `4` at `+0x0C` and a graphics pointer at `+0x18`. All ten index ranges lie inside their graphics segment; A-2 and B-8 end exactly at the segment end. | `BINARY`, `CROSS_SAMPLE` | Confirmed (offsets, counts and bounds); Unknown (cluster layout) | Ten geometries; no triangles reconstructed |
| DRAW-F17 | The shader group has an optional pointer at `+0x08`, a shader pointer array at `+0x10`, and `u16` count and capacity at `+0x18`. A shader is 0x40 bytes with a probable shader hash at `+0x00` (DRAW-F27), the constant `0x6D657461` at `+0x04`, a system pointer at `+0x08`, a slot table at `+0x10` and a parameter table at `+0x20`. The parameter table has a texture count at `+0x01`, a total count at `+0x04`, and `{u32 hash, u32 packed}` pairs from `+0x08`. A non-null slot targets a texture record whose `+0x30` name record holds a string pointer at `+0x00` and a 64-bit key at `+0x08`. The slot table has one entry per texture parameter in the four observed tables. | `BINARY`, `CROSS_SAMPLE` | Confirmed (structure and counts); Unknown (all meanings) | Two samples, four shaders |
| DRAW-F18 | In A, shader 0 declares 6 texture parameters and 55 total, binds 5 slots and leaves 1 unbound, with 5 distinct keys. Shader 1 declares 6 and 54, binds 4 and leaves 2 unbound, with 4 distinct keys. The union has 6 distinct keys. The two tables carry the same six texture-parameter `u32` values; four of them resolve to `joaat` preimages (DRAW-F28). | `BINARY`, `CROSS_SAMPLE` | Confirmed (counts); Unknown (meanings) | A is counted; B gives 7/68/5/2/5 and 6/54/4/2/4 as a structure check. Declared is not bound |
| DRAW-F19 | No key was resolved to a texture and no texture store was reached from these samples. Resolution depends on a resource-side texture-dictionary or store-reference path that was not found. | `BINARY` (absence), `CROSS_SAMPLE` | Confirmed (absence in samples); Unknown (dependency) | No texture dependency path |
| DRAW-F20 | The shader-group `+0x08` pointer is nonzero in A and zero in B. The header skeleton `+0x18` is null in both. LOD slots are sparse. The header distance values can be the sentinel `9998`. No single fixed header size is established. | `BINARY`, `CROSS_SAMPLE` | Confirmed (presence); Unknown (versioning rule) | Two samples |
| DRAW-F21 | The first 16 `u32` words at a graphics pointer were not attribute descriptors. Each vertex-buffer target begins with a 0x80-byte prefix whose first four bytes are `42 40 00 00`; the attributes are the separate offset, size and format arrays in the layout at vertex buffer `+0x40`. The candidate packed form (`format`, `size << 3`, `offset << 7`) was not observed. | `BINARY`, `CROSS_SAMPLE` | Rejected (candidate descriptor reading) | Ten geometries; the prefix is not interpreted |
| DRAW-F22 | The model `+0x18` target is an array of eight-`f32` records: `minimum.xyz`, `minimum.x`, `maximum.xyz`, `maximum.x`. The fourth word duplicated the first in all 9,579 records read. Record 0 is the aggregate; records 1..N are per-geometry AABBs in geometry-array order. A single-geometry model stores only record 0. In the census: 2,006 models, 669 with one geometry, 1,337 with at least two; all 1,337 multi-geometry models pass the union check. Header union passes in 1,932 of 1,990 drawables. Of 58 exceptions, 57 have exactly three null LOD slots and a header wider than the present-model union, consistent with the absent LOD models; one (`0x01066B9010`) has four populated slots and a z-min 0.1849 below the header, cause not established. This supersedes the "model min/max at the target start" part of DRAW-F03/F06. | `BINARY`, `CROSS_SAMPLE` | Confirmed (values and union) | First 6,000 `levels.rpf` recovery candidates with the resource signature, decoded size ≤ 400,000 bytes and 1-4 streams; the manifest is not published |
| DRAW-F23 | A vertex-buffer graphics prefix begins with a declaration table: each `u32` is `u8 format` in bits 0..7 and `offset / 2` in bits 8..31; a zero word ends it. One entry exists per present attribute, in position-first order, and every entry offset equals a layout offset. The table format byte is not the layout `u8` format code. | `BINARY`, `CROSS_SAMPLE` | Confirmed (positions and offsets); Unknown (format byte meaning) | Ten geometries; the entry order and byte meaning are not generalised |
| DRAW-F24 | The first declaration entry has format `0x42`, points at the `0x80` offset and covers the 8-byte layout entry. Those eight bytes are four 16-bit lanes. A-2's two varying lanes span 288 and 256 raw units, ratio `1.125`; its per-geometry AABB long axes span `0.996094` and `0.995606`, ratio `1.00049`. This rules out a uniform scalar across the lanes, an `f32` pair (NaN), an `f16` quartet (non-finite) and `4.0/2^k` for `k = 8..15` for A-2. A per-axis affine remains untested and is not excluded. No position was accepted. | `BINARY`, `CROSS_SAMPLE` | Confirmed (layout); Unknown (semantics) | One four-vertex geometry and the ten baseline geometries; the negatives are scoped to A-2 |
| DRAW-F25 | The index descriptor `+0x0A` is count A and `+0x0C` bits 8..23 are count B; the low byte of `+0x0C` is zero in all ten samples. The index bytes begin with `0x80000000 \| cluster_count`, then count A and count B, and the header matches the descriptor in 10/10 geometries. | `BINARY`, `CROSS_SAMPLE` | Confirmed (counts and header) | Ten geometries; the low byte is uninterpreted |
| DRAW-F26 | Each sampled index body contains an ascending `u16` run starting at zero. The run length is not the vertex count in general: A-1 32/32, A-2 4/4, B-1 115/902, B-3 114/540. The run is cluster-local; the cluster boundaries and the triangle grammar are Unknown, and no flat triangle list was produced. | `BINARY`, `CROSS_SAMPLE` | Confirmed (run structure); Unknown (grammar) | Ten geometries; no triangles reconstructed |
| DRAW-F27 | The shader `+0x00` `u32` is stable for a parameter schema: `0xBCF03FC1` carries 6 texture and 55 total parameters, `0x512937B5` carries 7 and 68, and `0xF28992E6` carries 6 and 54 in both A and B and in recovered drawables. It is a probable shader hash, not a per-material identifier or a name. | `BINARY`, `CROSS_SAMPLE` | Probable (stable hash) | Ten shader hashes over eight drawables; the hash namespace is Unknown |
| DRAW-F28 | Five texture-parameter hashes equal folded `joaat` of a researcher-supplied candidate spelling: `0xC8E8C282` = `DiffuseTex` (48 occurrences), `0x1E77BF4C` = `BumpTex` (48), `0xC6F46E79` = `SpecularTex` (48), `0x739E3D0D` = `SpecularTex2` (47) and `0x0DF47048` = `DiffuseTex2` (7). `0x2C8D7182` and `0x0CD27763` stay hashes (52 each). The candidates were not extracted from game data or the executable; each was hashed and compared to the observed value. Counts come from `material_census.py` over the eight-drawable manifest. The control `joaat("alpha/beta") = 0x75438640` reproduces. A match proves a preimage, not the original spelling. | `BINARY`, `SYNTHETIC` (control) | Confirmed (hash match); candidate names | Eight drawables; `DiffuseTex2` has 7 occurrences; no name dictionary for the remaining hashes |
| DRAW-F29 | `material_census.py` over the first eight decoded drawables in recovery order with at least two shaders reports 8 drawables, 52 shaders and 348 declared texture slots: 278 bound, 70 unbound and 0 null keys. All 278 bound slots carry a nonzero 64-bit key; every unbound slot is reported with key `0x0000000000000000`. No store join was attempted, so no key was resolved and the resolved count is unset rather than zero. | `BINARY`, `CROSS_SAMPLE` | Confirmed (bound, unbound and null counts); Unknown (store) | No texture store was reached; no direct-store or EDUP count is claimed |
| DRAW-F30 | The two named rows were re-located in the `levels.rpf` recovery population at archive offsets `0x10112BE010` (A, 7,840 bytes, 2 streams) and `0x1010FBD010` (B, 90,624 bytes, 3 streams); their header bounds and chain counts match the named rows. | `BINARY`, `CROSS_SAMPLE` | Confirmed (reproduction) | One archive; recovery offsets are not native row indices |

## Method per finding

`Yes` means the published inspector (or, for the aggregate, the committed census)
reads the value. `No` means the value is a manual byte observation. `Partly`
means the published tools supply part of the evidence and a manual step supplies
the rest.

| ID | Method | Inspector |
| -- | ------ | --------- |
| DRAW-F01 | CLI row metadata; inspector segment sizes and page map | Partly |
| DRAW-F02 | Inspector header read | Yes |
| DRAW-F03 | Inspector bounds values; manual radius and AABB arithmetic | No |
| DRAW-F04 | Inspector LOD-slot read | Yes |
| DRAW-F05 | Inspector LOD, model and geometry counts | Yes |
| DRAW-F06 | Inspector model record read | Yes |
| DRAW-F07 | Inspector header distance read | Yes |
| DRAW-F08 | Manual `+0xB0` target read; inspector resolves only the header pointer | No |
| DRAW-F09 | Manual system-wide pointer sweep | No |
| DRAW-F10 | Inspector geometry record read | Yes |
| DRAW-F11 | Inspector vertex-buffer read | Yes |
| DRAW-F12 | Inspector layout read | Yes |
| DRAW-F13 | Inspector packed-count read | Yes |
| DRAW-F14 | Inspector buffer-size arithmetic | Yes |
| DRAW-F15 | Inspector graphics-base derivation | Yes |
| DRAW-F16 | Inspector index descriptor and buffer read | Yes |
| DRAW-F17 | Inspector material-chain read | Yes |
| DRAW-F18 | Inspector material counts | Yes |
| DRAW-F19 | Manual absence check; no texture store was reached | No |
| DRAW-F20 | Inspector optional-field read | Yes |
| DRAW-F21 | Inspector layout and marker read; manual candidate rejection | Partly |
| DRAW-F22 | Inspector per-model AABB read and union check; committed `aabb_census.py` for the header union and exception causes | Yes |
| DRAW-F23 | Inspector declaration-table read | Yes |
| DRAW-F24 | Inspector layout read; manual lane-span comparison | Partly |
| DRAW-F25 | Inspector index descriptor and header read | Yes |
| DRAW-F26 | Inspector ascending-run read | Yes |
| DRAW-F27 | Inspector shader-hash read; cross-drawable comparison | Yes |
| DRAW-F28 | Manual `joaat` comparison over candidate names; `material_census.py` occurrence counts; synthetic control vector | No |
| DRAW-F29 | `material_census.py` over eight drawables | Yes |
| DRAW-F30 | Recovery export and inspector comparison with the named rows | Partly |

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
- **One graphics-shaped value is outside its segment.** It sits in a name-record
  table and is best read as a 32-bit hash, not a pointer (DRAW-F09).
- **The "model min/max at the pointer start" reading is superseded.** The target
  is a record array with a per-geometry record, not a single model box
  (DRAW-F22).
- **The `+0x0C` index field is not an opaque `u32`.** Its bits 8..23 equal the
  index-buffer count B (DRAW-F25).
- **The ascending index run is not a flat triangle list.** Its length is not
  the vertex count in general (DRAW-F26).
- **No vertex position is accepted.** For A-2, an `f32` pair, an `f16`
  quartet, a uniform scalar across the lanes and `4.0/2^k` are excluded; a
  per-axis affine remains untested and is not excluded (DRAW-F24).
- **No texture is resolved.** No local texture store was reached
  (DRAW-F19, DRAW-F29).

## Reproduction

`<GAME_ROOT>`, `<EXECUTABLE>` and `<WORK>` are local inputs. Payloads and
decoded resources are not part of this repository.

```text
lforge archive extract <GAME_ROOT>/levels.rpf --row 5 --output <WORK>/nested.rpf --executable <EXECUTABLE>
lforge archive ls <WORK>/nested.rpf --executable <EXECUTABLE> --limit 316 --json
lforge archive extract <WORK>/nested.rpf --row 5 --output <WORK>/draw5.bin --executable <EXECUTABLE>
lforge archive extract <WORK>/nested.rpf --row 10 --output <WORK>/draw10.bin --executable <EXECUTABLE>
lforge archive recover <GAME_ROOT>/levels.rpf --list --json
lforge archive recover <GAME_ROOT>/levels.rpf --id 0x10112BE010 --output <WORK>/drawA.bin --overwrite
lforge archive recover <GAME_ROOT>/levels.rpf --id 0x1010FBD010 --output <WORK>/drawB.bin --overwrite
python tools/drawables/drawable_inspect.py inspect --file <WORK>/drawA.bin --system-length 0x16F0 --json
python tools/drawables/drawable_inspect.py inspect --file <WORK>/drawB.bin --system-length 0x40F0 --json
python tools/drawables/aabb_census.py --manifest <WORK>/census.jsonl --json
python tools/drawables/material_census.py --manifest <WORK>/materials.jsonl --json
python -m unittest discover -s tools/drawables -p "test_*.py"
```

The census manifest is JSON Lines with `{"id", "file", "system_length"}` per
decoded resource. The selection and the manifest are local inputs; the manifest
is not published.

The `archive ls` output supplies the row type IDs, stored sizes, decoded sizes
and chunk counts. The recovery commands reproduce the two named rows by archive
offset; a recovery offset is not a native row index. The inspector commands
reproduce the findings marked `Yes` or `Partly` above. The census reproduces
DRAW-F22's header counts and exception causes, and the material census
reproduces DRAW-F28 and DRAW-F29. The manual reads do not reproduce
DRAW-F08, DRAW-F09, DRAW-F28 or DRAW-F19; DRAW-F19 remains not demonstrated. The system-length values
are derived from the graphics targets and the page counts, not from a stored
field.

## Limits

- One build. The named rows are two rows of one nested archive. The AABB census
  selects the first 6,000 `levels.rpf` recovery candidates with the resource
  signature, decoded size ≤ 400,000 bytes and 1-4 streams; it yields 1,990
  drawables and 2,006 models. The material checks cover the first 8 drawables in
  recovery order with at least two shaders. Other type IDs and builds were not
  inspected.
- The local type ID 2 is a CLI assignment, not a format identity; the label
  "drawable" is the subject name used by this iteration.
- The cross-sample evidence covers the named rows and the recovered population
  stated per finding.
- The stored rows were decoded by the CLI; no independent re-inflation was
  performed.
- The system/graphics boundary is derived, not stored.
- No engine code path was traced.
- ASCII payload names are not reproduced.
- No vertex position is accepted (DRAW-F24); no triangles were reconstructed
  (DRAW-F26).
- Five texture parameter hashes resolve to `joaat` preimages; the rest stay
  hashes. The material section is not a resolved material graph.
- The inspector's synthetic tests are `SYNTHETIC` and support no native claim.
- Findings DRAW-F08, DRAW-F09, DRAW-F28 and DRAW-F19 are not reproduced by a
  single inspector run.

## Candidate corrections

The candidate field table and the private measurements were checked, not
adopted. Corrections that change a structural rule are recorded in
[research-history.md](research-history.md).
