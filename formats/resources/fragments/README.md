# Fragments

This document describes the resource a fragment payload holds. A metadata-only
census of the installation counts 55,488 type-3 entries in 265 archives. The
survey read 7,311 of those rows from 28 archives: all 5,553 rows of the 27
extracted archives of the inventory expansion, plus all 1,758 rows of
`data.rpf!26`. Every read row holds the root and member form below. The type ID
is a local CLI assignment, not a format identity.

A first iteration decoded 40 rows of one nested archive and built the layout
table from the 24 of those that hold a member drawable. The wider runs confirm
that layout and add what the 40 rows could not show: every one of the 7,311 rows
read holds exactly one member drawable, the member references a skeleton, list
and shader group in every read row, and a fragment whose object has several
parts carries them as models and geometry records of that one drawable. Those
are properties of the rows read, not rules for the type: the 48,177 unread rows
are not claimed. No engine code path was traced. Field meanings are **Unknown**
unless the table says otherwise. Findings are cited as `FRAG-F01` to `FRAG-F12`
and listed in
[evidence/fragments/INDEX.md](../../../evidence/fragments/INDEX.md).

## Corpus

| Quantity                                                     | Value  |
| ------------------------------------------------------------ | ------ |
| Type-3 entries the installation census counts                | 55,488 |
| Archives holding them                                        | 265    |
| Rows this survey read                                        | 7,311  |
| Archives this survey read                                    | 28     |
| Rows with the root shape                                     | 7,311  |
| Rows with exactly one member drawable                        | 7,311  |
| Rows where a root slot other than `+0x18` reaches a drawable | 0      |
| Rows whose member name carries the `#ft` suffix              | 7,311  |
| Rows with two or more member drawables                       | 0      |

The unread 48,177 rows are not claimed. The census counts them from metadata
without decoding them, and the survey reads rows in place, so covering every
archive costs one folder walk of the archive that holds it; 28 archives were
read inside this iteration's budget.

## Sample locators

The detailed samples come from `<GAME_ROOT>/levels.rpf`, row 5: a nested
archive with SHA-256
`450B6A5A95578A31133F686AE5D1D8151B4C7A38197F039895311D44742DBC96`
and 22,172,864 stored bytes, holding 316 rows of local type 2 and 3.

| Sample | Row | Type | Decoded bytes |      System bytes |    Graphics bytes | Member name                       |
| ------ | --: | ---: | ------------: | ----------------: | ----------------: | --------------------------------- |
| D      |   0 |    3 |        11,456 |  6,528 (`0x1980`) |  4,928 (`0x1340`) | `prop_am_card_tarot_deck_01a.#ft` |
| E      |   1 |    3 |        75,344 | 15,552 (`0x3CC0`) | 59,792 (`0xE990`) | `prop_am_candlestick_02a.#ft`     |
| F      |   8 |    3 |     2,423,888 | 48,064 (`0xBBC0`) |         2,375,824 | `mint_peacock_taxidermy_01.#ft`   |

The system length is the split the shared offset/pointer inference recovers
from the vertex-buffer graphics pointers and the mesh-blob marker; for a native
row the archive page metadata supplies the same number. The page map sits at
system `+0x17D0`, `+0x3950` and `+0x4410` for D, E and F and declares one
system page in each.

## Root header

Offsets are system-relative. Values are from sample D unless stated.

|  Offset | Size | Observation       | D              | E              | Notes                                                                                           |
| ------: | ---: | ----------------- | -------------- | -------------- | ----------------------------------------------------------------------------------------------- |
| `+0x00` |    8 | Observed in 24/24 | `0`            | `0`            | A parser MUST require the zero word                                                             |
| `+0x08` |    8 | Observed in 24/24 | `0x500017D0`   | `0x50003950`   | Page-map pointer, same slot as a resource-level drawable                                        |
| `+0x10` |    8 | Observed in 24/24 | `0x50000AE0`   | `0x50001F90`   | Reaches a record with a `u64` `2` at `+0x10` and a name pointer at `+0x18`; meaning **Unknown** |
| `+0x18` |    8 | Observed in 24/24 | `0x500006B0`   | `0x50001890`   | **The member drawable**; see below                                                              |
| `+0x20` |    8 | Observed in 24/24 | `0x50001048`   | `0x50001DC8`   | Reaches a record with repeated `0x3C00`/`0xBC00` words; meaning **Unknown**                     |
| `+0x28` |    8 | Observed in 24/24 | `0x50001270`   | `0x50000390`   | Reaches a record beginning with `0.70711` floats; meaning **Unknown**                           |
| `+0x30` |    8 | Observed in 24/24 | `[1, 1, 1, 1]` | `[1, 1, 2, 6]` | Four `u16`; see [counts](#counts-at-0x30)                                                       |

Only `+0x18` is followed to a drawable. The other three pointers are not
scanned for further drawables: no sample reaches one, so treating them as
component tables would be an invention.

## Member drawable

The target of `+0x18` is an `rmcDrawable`. Its header uses the same offsets as
[the resource-level drawable](../drawables/README.md), with two differences:

| Field            | Resource-level drawable             | Fragment member                                                |
| ---------------- | ----------------------------------- | -------------------------------------------------------------- |
| `drawable +0x08` | System page-map pointer             | Zero in 5,553/5,553; the containing resource owns the page map |
| `drawable +0xB8` | `0x103` in both named drawable rows | `3` in 24/24 of the first sample set                           |

Everything else was read at the same offsets: shader group `+0x10`, skeleton
`+0x18`, the bounds block `+0x20..+0x4F`, four LOD slots `+0x50..+0x6F`, LOD
distances `+0x70`, flag words `+0x80`, the name pointer `+0xA8` and the list
pointer `+0xB0`. The name pointer holds the fragment name, for example
`prop_am_card_tarot_deck_01a.#ft`; the `#ft` suffix appears in all 5,553 rows.

The suffix is an observation about the stored name, not the discriminator. A
reader identifies a fragment by the root structure: a zero word at `+0x00`, a
page-map pointer at `+0x08`, a member-drawable pointer at `+0x18` whose target
walks as an `rmcDrawable` with a zero page-map word, and no drawable at zero. The
declared resource type selects the candidate; the structure decides. A fragment
whose member carries another suffix is still the fragment its structure says it
is, and the suffix is reported as a fact rather than required (FRAG-F08).

The two interpretations can overlap: a fragment root's `+0x50` LOD slot can hold
a pointer, which is also what a resource-level drawable header reads. When both
readings hold, the name separates them and the overlap is reported instead of
being resolved silently; a root that overlaps without a fragment name is refused
rather than guessed. Neither reading is validated more loosely to make the
choice.

Sample D: two populated LOD slots, one model and one geometry each, one shader.
Sample E: four populated LOD slots, one model and two geometries each. Sample
F : two populated LOD slots, one model and four geometries each.

## Counts at `+0x30`

The four `u16` are not established. The first is `1` in 5,522 of the 5,553 rows
and `2` in the other 31; the second is `0` in 151 rows and the rest vary from
`1` to `80`; the third varies from `0` to `80` and the fourth from `0` to `266`.
Every row read holds exactly one member drawable whatever the four values are, so
a reader MUST NOT read them as component counts (FRAG-F05, FRAG-F07).

## Assembly

Sample D's decoded geometry reproduces the member drawable's own bounds block:
minimum `(-0.0381, -0.0635, 0.0)`, maximum `(0.0381, 0.0635, 0.02002)` against
decoded `(-0.038086, -0.063476, 0.0)` to `(0.038086, 0.063476, 0.020019)`. The
decoded positions of that sample therefore already sit in the space its bounds
block describes.

No additional transform is applied to a single-drawable fragment, and none is
invented. That is a statement about this implementation and about the samples:
no root field was identified as a placement matrix, so there is nothing to apply
in its place. It is not a claim that every fragment's geometry is authored in
final resource space. The member's skeleton reference is recorded and not
parsed *in this document*, so a fragment whose parts are posed through a
skeleton could render in its bind pose instead of its posed form; see the
follow-up in [Limits](#limits). The skeleton record itself is documented in
[skeletons](../skeletons/README.md) (SKEL-F01 to SKEL-F14).

The fragment scene is the member drawable's highest populated LOD. LOD
selection happens inside the drawable, as it does for a resource-level drawable;
the fragment root stores no LOD selector that was identified.

### Component, model and geometry

The three levels are separate and a reader MUST NOT use one word for another.

| Level     | What it is                                     | Count in a fragment |
| --------- | ---------------------------------------------- | ------------------- |
| Component | One member drawable the root references        | Always 1            |
| Mesh      | One model of that drawable's selected LOD slot | 1 or more           |
| Primitive | One geometry record inside its model's mesh    | 1 or more per mesh  |

A component is therefore not a mesh, and a mesh is not a component. Sample F is
the clearest case: one component, one model and four geometries in the slot
that decodes, so its scene holds one mesh with four primitives and four
materials. `prop_am_card_tarot_deck_01a.#ft` holds one component, one model and
one geometry, so its scene holds one mesh with one primitive.

## What a member drawable holds

Read across 5,553 rows of the 27 extracted archives and 1,758 rows of
`data.rpf!26` (FRAG-F10):

| Quantity                       | Observed values                                                    |
| ------------------------------ | ------------------------------------------------------------------ |
| Populated LOD slots            | 1 (3,659), 2 (454), 3 (472), 4 (968) — and 1 or 2 in `data.rpf!26` |
| Models in the member           | 1 (3,647), 2 (443), 3 (453), 4 (922), 5 (75), 6 (11), 7 (2)        |
| Geometry records in the member | 1 to 71; 1,115 of the 1,758 `data.rpf!26` members hold one         |
| Skeleton pointer `+0x18`       | Non-null in every read row (7,311 of 7,311)                        |
| List pointer `+0xB0`           | Non-null in every read row                                         |
| Shader group `+0x10`           | Non-null in every read row                                         |

The skeleton reference is the notable difference from the two sampled
resource-level drawables, where that slot is null. The reference is non-null in
every row read, which is consistent with a rigged member drawable; whether the
record is a skeleton and whether it changes the rendered pose is not
established *here*. This document does not interpret the skeleton; it records
that the reference exists in every row and that the static representation was
validated without it. The record is read in [skeletons](../skeletons/README.md):
the sampled fragments store vertex positions in the bind pose, which is why the
static representation validates without a pose transform.

## Static placement

The decoded vertex positions sit in the space the member drawable's bounds
describe in every sample read, and a fragment's parts are separate models or
geometry records of that one drawable rather than separate drawables:

- `w_sg_goodwin_01_bolt_01_mid.#ft` (`data.rpf!26!9`) decodes to one component,
  one model and one geometry record: 620 vertices, 372 triangles, one material
  and three reconstructed textures. Its render shows the bolt body with two
  parallel rails, all correctly positioned relative to each other.
- `mint_peacock_taxidermy_01.#ft` decodes to one component, one model and four
  geometry records: 41,613 vertices, 45,132 triangles and four materials.
- The 1,758 `data.rpf!26` rows are weapon parts (`w_*` names): 1,172 hold one
  model and 586 hold two, and every one holds exactly one member drawable.

No transform was needed to obtain those renders, and none was applied. No
fragment root field was identified as a placement table: the two models of a
weapon part are models of one drawable and decode in the drawable's own space.
This is support for the static, single-primary-drawable representation. It does
not show that skeleton-driven placement is unnecessary in general; a skeleton
driven pose is untested because the skeleton is not parsed.

## Root variants

The census normalises type-3 headers into two variants, and both occur (FRAG-F09):

| Variant                | `+0x10`        | Rows in the 27 extracted archives | Rows in `data.rpf!26` |
| ---------------------- | -------------- | --------------------------------: | --------------------: |
| `s5:ptr:seg5+ptr:seg5` | System pointer |                             5,402 |                 1,758 |
| `s5:zero+ptr:seg5`     | Zero           |                               151 |                     0 |

The 151 zero-`+0x10` rows are the ones whose four `u16` at `+0x30` are
`[1, 0, 0, 0]`; every other row stores a non-zero second word. Both variants
hold exactly one member drawable at `+0x18` and behave identically for assembly,
so the difference is reported and not interpreted.

## Sibling types

Three other types share the resource header family, so the framing was compared
on real rows rather than assumed (FRAG-F12):

| Type | Extension | Rows read | Root words `(+0x00, +0x10, +0x18)`      | Parseable as                                               |
| ---: | --------- | --------: | --------------------------------------- | ---------------------------------------------------------- |
|    3 | `zft`     |     7,311 | `(0, pointer, member-drawable pointer)` | fragment root with a member drawable                       |
|   17 | `zbft`    |        47 | `(0, 1 or 2, 0x500000A0 / 0x500000D0)`  | fragment root form, but `+0x18` is not a member drawable   |
|    5 | `ztd`     |         3 | `(0, 0, 1)`                             | texture dictionary, not a drawable dictionary              |
|   16 | `zbdd`    |       285 | `(0, 0, 1)`                             | texture dictionary (263 of 285), not a drawable dictionary |

The `.zbft` rows therefore are not `.zft` rows with another name: their `+0x10`
holds a small integer and their `+0x18` points near the start of the system
segment, at no member drawable. In the 285 rows read, type 16 has the framing of
a texture dictionary and not that of a drawable dictionary, so the `b` in the
extension is not evidence of a drawable container. That is a statement about the
rows read: neither type is decoded here, and nothing establishes type 16 as
equivalent to a normal texture dictionary everywhere.

## Drawable dictionaries

An earlier iteration reported that no drawable dictionary member table was
located. That search was bounded: it decoded 40 type-3 rows of one nested
archive and looked for a table of drawable references inside those rows
(FRAG-F06, now corrected). It was not a search of the type-4 population.

A drawable dictionary table does exist in this build, in the rows that carry
local type ID 4. Every one of 8,209 such rows holds a `u32` name-hash array and
a parallel `u64` array of member-drawable pointers; the grammar, the hash rule
and the member counts are in
[drawable-dictionaries](../drawable-dictionaries/README.md).

The two containers are distinct: a type-3 fragment root holds one member
drawable and no dictionary table, and a type-4 resource is a dictionary root
whose members are the drawables. A parser MUST NOT read a member table out of a
fragment root, and MUST NOT read a fragment's single-drawable form as a claim
about dictionaries.

## Limits

- 7,311 decoded rows from 28 archives of one build. The installation census
  counts 55,488 type-3 entries in 265 archives; the remaining 48,177 rows and
  237 archives were not read, so no claim here extends to them.
- Only the member drawable at `+0x18` is understood. No read row holds two
  member drawables, child placements or a damage-state table, so no assembly
  rule for them is published. The absence of such a row in 7,311 samples is not
  proof that a multi-drawable fragment cannot exist in a row that was not read.
- The three other root pointers reach records that were not interpreted. The
  records behind `+0x10` hold a `u64` `2` and a name pointer, the ones behind
  `+0x20` hold repeated `0x3C00`/`0xBC00` words, and the ones behind `+0x28`
  begin with `0.70711` floats; none of them reaches a drawable in 7,311 rows.
  The shapes resemble collision or shape data; this document does not interpret
  them and does not claim they are collision data.
- The skeleton reference is recorded but not parsed. Whether a fragment member's
  bind pose is always the rendered pose is not established; the sampled renders
  show the objects assembled correctly without applying a pose.
- Follow-up work: parse the member's skeleton reference and decide whether a
  bind-pose placement is needed. Until that is done, a fragment whose parts are
  posed through its skeleton renders as authored, and this document does not
  claim that is the posed result.
- No fragment root field that selects a damage state or a component subset was
  identified.
