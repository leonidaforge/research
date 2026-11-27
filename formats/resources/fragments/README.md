# Fragments

This document describes the resource a fragment payload holds. The subject is
every row that carries local type ID 3 in the 27 extracted nested archives of
the inventory expansion that declare the type: 5,553 rows. All 5,553 were read
and all 5,553 hold the root and member form below. The type ID is a local CLI
assignment, not a format identity.

A first iteration decoded 40 rows of one nested archive and built the layout
table from the 24 of those that hold a member drawable. The whole-population run
confirms that layout and adds the answers the 40 rows could not give: a fragment
always holds exactly one member drawable, and its name always carries the `#ft`
suffix. No engine code path was traced. Field meanings are **Unknown** unless the
table says otherwise. Findings are cited as `FRAG-F01` to `FRAG-F08` and listed
in [evidence/fragments/INDEX.md](../../../evidence/fragments/INDEX.md).

## Corpus

| Quantity                                                     | Value |
| ------------------------------------------------------------ | ----- |
| Nested archives that declare type-3 rows                     | 27    |
| Type-3 rows found                                            | 5,553 |
| Rows with the root shape                                     | 5,553 |
| Rows with exactly one member drawable                        | 5,553 |
| Rows where a root slot other than `+0x18` reaches a drawable | 0     |
| Rows whose member name carries the `#ft` suffix              | 5,553 |
| Rows with two or more member drawables                       | 0     |

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

Sample D: two populated LOD slots, one model and one geometry each, one shader.
Sample E: four populated LOD slots, one model and two geometries each. Sample
F : two populated LOD slots, one model and four geometries each.

## Counts at `+0x30`

The four `u16` are not established. The first is `1` in 5,522 of the 5,553 rows
and `2` in the other 31; the second is `0` in 151 rows and the rest vary from
`1` to `80`; the third varies from `0` to `80` and the fourth from `0` to `266`.
Every row holds exactly one member drawable whatever the four values are, so a
reader MUST NOT read them as component counts (FRAG-F05, FRAG-F07).

## Assembly

Sample D's decoded geometry reproduces the member drawable's own bounds block:
minimum `(-0.0381, -0.0635, 0.0)`, maximum `(0.0381, 0.0635, 0.02002)` against
decoded `(-0.038086, -0.063476, 0.0)` to `(0.038086, 0.063476, 0.020019)`.
The vertex positions are therefore already in the space the header describes.
No additional transform is applied to a single-drawable fragment, and none is
invented.

The fragment scene is the member drawable's highest populated LOD. LOD
selection happens inside the drawable, as it does for a resource-level drawable;
the fragment root stores no LOD selector that was identified.

### Component, model and geometry

The three levels are separate and a reader MUST NOT use one word for another.

| Level     | What it is                                                    | Count in a fragment |
| --------- | ------------------------------------------------------------- | ------------------- |
| Component | One member drawable the root references                       | Always 1            |
| Mesh      | One model of that drawable's selected LOD slot                | 1 or more           |
| Primitive | One geometry record inside its model's mesh                   | 1 or more per mesh  |

A component is therefore not a mesh, and a mesh is not a component. Sample F is
the clearest case: one component, one model and four geometries in the slot
that decodes, so its scene holds one mesh with four primitives and four
materials. `prop_am_card_tarot_deck_01a.#ft` holds one component, one model and
one geometry, so its scene holds one mesh with one primitive.

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

- 5,553 decoded rows from 27 nested archives of one build. Other archives,
  other types and other builds were not inspected, and the inventory reached 27
  of the archives that declare the type.
- Only the member drawable at `+0x18` is understood. Multi-drawable fragments,
  child placements, damage-state selection and physics data were not observed
  in any row, so no assembly rule for them is published.
- The three other root pointers reach records that were not interpreted. The
  records behind `+0x10` hold a `u64` `2` and a name pointer, the ones behind
  `+0x20` hold repeated `0x3C00`/`0xBC00` words, and the ones behind `+0x28`
  begin with `0.70711` floats; none of them reaches a drawable in 5,553 rows.
  The shapes are consistent with collision and shape data, which this document
  does not interpret.
- No fragment root field that selects a damage state or a component subset was
  identified.
