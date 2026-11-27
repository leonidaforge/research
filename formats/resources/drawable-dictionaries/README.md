# Drawable dictionaries

A drawable dictionary is a resource whose system segment starts with a
`pgDictionary`-shaped root and whose values are member drawables. This document
describes the whole population that the inventory reached, not a sample: 8,209
rows that carry local type ID 4 in 53 extracted nested archives. Every one of
them was read and every one has the structure below.

The type ID is a local CLI assignment, not a format identity. The label
"drawable dictionary" is the subject name used by this iteration. The rows come
from the Scarlett build
[e95020b2](../../../builds/gta-vi/scarlett-e95020b2/README.md).

No engine code path was traced. Field meanings are **Unknown** unless the table
says otherwise. Pointers use the encoding in [pointers.md](../pointers.md).
Findings are cited as `DDICT-F01` to `DDICT-F08` and listed in
[evidence/drawable-dictionaries/INDEX.md](../../../evidence/drawable-dictionaries/INDEX.md).

## Corpus

The 8,209 rows were enumerated from the extracted archives of the inventory
expansion, which sampled 53 nested archives out of the 782 it could read. Each
row was reconstructed with its native page split, so no boundary was inferred.

A metadata-only census of the installation counts 48,584 type-4 entries in 179
archives. The 8,209 rows below are the subset the survey read; they are not the
whole population, and no claim here extends to the unread 40,375 entries.

| Quantity                                   | Value  |
| ------------------------------------------ | ------ |
| Nested archives with type-4 rows           | 53     |
| Type-4 rows found                          | 8,209  |
| Rows read                                  | 8,209  |
| Rows with the dictionary root form         | 8,209  |
| Rows accepted by the content classifier    | 8,209  |
| Members enumerated                         | 12,480 |
| Members whose value resolves to a drawable | 12,480 |
| Members without a stored name              | 0      |
| Empty dictionaries                         | 0      |
| Rows whose hash array is not sorted        | 0      |
| Rows whose counts disagree                 | 0      |

Member counts are not uniform: 7,181 dictionaries hold one member, and the rest
hold 2, 3, 4, 6, 8, 11, 12, 13, 15, 16, 17, 27, 48, 83 or 108. The largest
observed dictionary holds 108 member drawables.

The counts are reproduced by the two ignored real-resource tests
`surveys_native_type_4_rows` and `surveys_native_type_3_rows` in
`apps/desktop/src/files/model.rs`. Their inputs are a list of extracted archives
and the executable that supplies the archive keys; they print the aggregates
this document quotes and fail on a structural issue, a hash mismatch or an
unreadable row.

## Root

Offsets are system-relative; pointer values are shown as stored.

| Offset  | Size  | Observation      | Notes                                                                 |
| ------- | ----- | ---------------- | --------------------------------------------------------------------- |
| `+0x00` | 8     | Zero in 8,209    | A parser MUST require it (DDICT-F01)                                  |
| `+0x08` | 8     | Page-map pointer | The same slot a resource-level drawable holds (DDICT-F01)             |
| `+0x10` | 8     | Zero in 8,209    | Meaning **Unknown**; a parser MUST NOT read it as a member count      |
| `+0x18` | 8     | `1` in 8,209     | Meaning **Unknown**; not the member count (DDICT-F02)                 |
| `+0x20` | 8     | System pointer   | Hash-array pointer, or zero when the dictionary is empty (DDICT-F03)  |
| `+0x28` | 2 + 2 | Count, capacity  | Hash count and hash capacity                                          |
| `+0x30` | 8     | System pointer   | Value-array pointer, or zero when the dictionary is empty (DDICT-F03) |
| `+0x38` | 2 + 2 | Count, capacity  | Value count and value capacity                                        |

The root is positional: entry `i` of the value array is the member whose name
hash is entry `i` of the hash array.

## Tables

The hash array holds `u32` entries with stride 4. It is ascending and
duplicate-free in all 8,209 rows (DDICT-F04). The value array holds `u64`
entries with stride 8 (DDICT-F05).

The two counts are equal in all 8,209 rows, and each count equals its capacity
in all 8,209 rows: the observed pairs are `(1,1)`, `(2,2)`, `(3,3)`, `(4,4)`,
`(6,6)`, `(8,8)`, `(11,11)`, `(12,12)`, `(13,13)`, `(15,15)`, `(16,16)`,
`(17,17)`, `(27,27)`, `(48,48)`, `(83,83)` and `(108,108)`. A reader SHOULD
require `hash count == value count` and MUST require `count <= capacity`, which
is the weaker condition the data actually supports.

## Name hash

Each `u32` hash equals `joaat` of a member drawable's name with its final
extension removed: 12,480 of 12,480 members (DDICT-F06). Every member name ends
in `.#dr`, and hashing the name with that suffix produces a different value in
all 12,480 cases. The suffix is therefore part of the stored name text and not
part of the hashed string.

| Name form                  | Equals the stored hash |
| -------------------------- | ---------------------- |
| `farlod_structures_03.#dr` | No                     |
| `farlod_structures_03`     | Yes                    |

Example: the hash `0xE727331E` is `joaat("farlod_structures_03")`; the member's
stored name is `farlod_structures_03.#dr`.
The hash is a derived label, not the member's identity. A reader MUST select a
member by its index in the arrays, because that identifies one entry even when
two entries share a hash or point at the same drawable. The public API exposes
the stored hash and the hash computed from the stored name independently, so a
mismatch is visible rather than silently repaired.

## Member states

Enumerating a dictionary never stops at the first member it cannot resolve.
Each entry is reported as one of four states: a drawable, null, not a system
pointer, or a system pointer without the member-drawable form. A null or
malformed member does not invalidate its neighbours, and the classifier still
accepts the dictionary when at least one member resolves (DDICT-F07).

## Native and inferred boundaries

The archive's page metadata is authoritative for the system/graphics boundary.
The standalone inference in `model::split_resource_reason` disagrees with it on
1,521 of the 8,209 rows of the 53-archive corpus. On every one of those rows the
inference produces no boundary at all: no candidate passes the page-map check, or
several candidates tie and the tie is refused instead of broken. No row of that
corpus yields a dictionary root form with members from the inferred boundary, so
a standalone open there fails loudly instead of misreading the resource
(DDICT-F09).

The installation-wide survey finds the exception that the 53-archive corpus does
not contain. Of the 48,584 type-4 entries the census counts, 45,200 were resolved
through their original chains and 45,200 were read; 45,199 carry a native split,
and 6,304 of those disagree with the inferred boundary. Of the disagreements,
6,278 have no candidate, 1 has no dictionary root form, and 25 still yield a root
form whose members all resolve. The inference can therefore land on a boundary
that parses completely but is not the native one, which is why the app uses
native page metadata whenever it is available and marks an inferred boundary as
inferred.

The 25 rows are located, and reading one explains what the overlap is. 22 sit in
the `levels.rpf` rivers and canals groups
(`levels.rpf!1355!3` is one), and 3 in `pack/story000/story000.rpf!235`. Read
`levels.rpf!1355!3` at its native boundary `0x1080` and the single member
`lo_rvr_04_water_fh_rvr_1sa_001_lod.#dr` decodes to 2,449 vertices and 4,534
triangles. Read at the inferred `0x553e`, the same dictionary enumerates: same
page map, same one member, same name, state `drawable`. The member then fails to
decode with `the drawable yielded no renderable mesh`, because the system segment
was cut past the member's own records. The overlap is therefore a boundary that
enumerates but cannot assemble, not one that silently misplaces geometry, and the
standalone open still fails loudly, one step later than on the other 6,279 rows.

The failure is reported as a layout problem, with the reason it could not be
inferred or the boundaries that tie, and it says that native page metadata is
required. It is not reported as evidence that the resource is something other
than a drawable dictionary: a resource whose boundary cannot be inferred is
unmeasured, and opening it from its archive supplies the authoritative layout.
A failed inference is never counted as a negative in the corpus numbers above.

## Member values

Every value is a system pointer to an `rmcDrawable` at the offsets documented in
[the resource-level drawable](../drawables/README.md), with the embedded form a
fragment member uses: the page-map word at `drawable +0x08` is zero because the
containing resource owns the page map (DDICT-F07). No value is null, no value
fails to decode as a pointer, and no value points at system data that lacks the
member form.

A member drawable's LOD chain is walked exactly as it is for a standalone
drawable. The highest populated LOD is the one a viewer shows, and LOD
selection happens inside the member, not in the dictionary root.

## Empty dictionaries

No empty dictionary was observed. The empty case is accepted on structure
alone: zero counts, arrays that are zero or in bounds, and the root words the
populated rows carry. Because an empty root has no member to confirm the form, a
reader SHOULD also require the `+0x18` word to be `1`, the value every observed
root stores; a root that fails that word is not reported as a dictionary
(DDICT-F08).

## Multi-part drawables

A dictionary is where this build stores several drawables in one resource. It is
the container a viewer needs for a multi-part object: the members are enumerated
from the two tables, each member decodes on its own, and each member's bounds
are its own. The root stores no placement, transform or child table beyond the
two arrays: the words at `+0x10` and `+0x18` are constant in the whole corpus,
so a reader MUST NOT invent per-member transforms from them.

Fragments are the opposite case: every type-3 fragment in the wider corpus holds
exactly one member drawable, see [fragments](../fragments/README.md).

## Verified members

These members were decoded and rendered offscreen with the maintained example
`crates/model/examples/dictionary_render.rs`, which uses only the shared
`lforge-model`, `lforge-texture` and `lforge-renderer` crates. Every report below
came from that example; the images were written outside the repository.

| Selector                                            | Members | Index | Stored hash  | Name                                    | Meshes | Primitives | Vertices | Triangles | Materials | Bindings | Resolved | Reconstructed | Geometry | Textures               |
| --------------------------------------------------- | ------: | ----: | ------------ | --------------------------------------- | -----: | ---------: | -------: | --------: | --------: | -------: | -------: | ------------: | -------- | ---------------------- |
| `data.rpf!7!0`                                      |       4 |     0 | `0x460270D3` | `farlod_structures_01.#dr`              |      1 |          1 |   15,794 |    19,079 |         1 |        0 |        0 |             0 | Complete | Not referenced         |
| `data.rpf!7!0`                                      |       4 |     1 | `0x8D887FDE` | `farlod_structures_04.#dr`              |      1 |          1 |   10,392 |    12,542 |         1 |        0 |        0 |             0 | Complete | Not referenced         |
| `core_restofworld.rpf!6!0`                          |      13 |     0 | `0x03546CA1` | `ptfx_model_gore_bone_02.#dr`           |      1 |          1 |      254 |       375 |         1 |        4 |        2 |             2 | Complete | Partial (1 missing)    |
| `core_restofworld.rpf!6!0`                          |      13 |    12 | `0xFA0B55BD` | `ptfx_model_gore_brain_l.#dr`           |      1 |          1 |    1,250 |     1,836 |         1 |        4 |        4 |             4 | Complete | Complete               |
| `<nested archive>!8` (108 members, see below)        |     108 |     0 | `0x0365537D` | `ptfx_model_debris_glass_bottle_01.#dr` |      1 |          1 |      229 |       198 |         1 |        4 |        2 |             2 | Complete | Partial (1 missing)    |
| `<nested archive>!8` (108 members, see below)        |     108 |   107 | `0xFFE1DF83` | `ptfx_model_metal_shard_02.#dr`         |      1 |          1 |      251 |       214 |         1 |        6 |        3 |             3 | Complete | Partial (1 missing)    |

The 108-member dictionary is `Row 00008` of the nested archive with SHA-256
`FDE95440F5F0DBC24D8B188D9C2338430EC00F962ADBD130D53A22804E42324B`, whose
system segment is `0x489F0` bytes and whose page map is at `0x3F810`. The same
archive also holds an 83-member dictionary at `Row 00006`. Both were enumerated
in full and one member was decoded from each; enumerating a dictionary does not
decode its members.

The two `farlod_structures` members have no material texture binding at all,
which is the zero-texture-parameter shader case: geometry `Complete`, textures
`NotReferenced`. The restofworld members resolve through the shared store scan
(46 stores, 352,461 descriptors) and render with their textures; the
`Partial (1 missing)` members each bind a texture key no store carries.

## Comparison with the texture and batch dictionaries

The census normalises the headers of types 4, 5 and 16 into one variant, so the
framing was compared on real rows instead of assumed (DDICT-F11):

| Type | Extension | Rows read | Root words `(+0x00, +0x10, +0x18)` | Drawable dictionary parser | Texture dictionary parser |
| ---: | --------- | --------: | ---------------------------------- | -------------------------- | ------------------------- |
|    4 | `zdd`     |     8,209 | `(0, 0, 1)`                        | 8,209 of 8,209             | 0 of 8,209                |
|    5 | `ztd`     |         3 | `(0, 0, 1)`                        | 0 of 3                     | 3 of 3                    |
|   16 | `zbdd`    |       285 | `(0, 0, 1)`                        | 0 of 285                   | 263 of 285                |

The three roots share the zero word, the page map and the `+0x18` word, and
nothing else. Type 16 is a texture-dictionary-shaped container, not a drawable
dictionary, and the `b` in its extension does not change that. The two parsers
therefore stay separate: their member arrays, member kinds and name rules differ,
and a shared abstraction over them would have to invent a common member type.

## Limits

- The corpus is every type-4 row of 53 nested archives of one build. Other
  archives, other builds, and type-4 rows the inventory did not select were not
  inspected.
- The words at `+0x10` and `+0x18` are reported as stored. Their meanings are
  not established by this corpus.
- Member order is the hash order, which is the array order. No authored order
  was observed and none should be reported.
- Nothing here decodes geometry or materials; that is the drawable structure's
  subject.
