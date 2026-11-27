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
