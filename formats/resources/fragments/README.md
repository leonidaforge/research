# Fragments

This document describes the resource a fragment payload holds. The subject is
the 224 rows that carry local type ID 3 in row 5 of `levels.rpf`. A previous
iteration read that nested archive for its type-2 drawables; the same rows are
the fragment corpus here. The type ID is a local CLI assignment, not a format
identity.

Forty of the 224 rows were decoded and walked; 24 of those hold a member
drawable and are the basis for every claim below. No engine code path was
traced. Field meanings are **Unknown** unless the table says otherwise.
Findings are cited as `FRAG-F01` to `FRAG-F06` and listed in
[evidence/fragments/INDEX.md](../../../evidence/fragments/INDEX.md).

## Sample locators

The parent archive is `<GAME_ROOT>/levels.rpf`, row 5: a nested archive with
SHA-256 `450B6A5A95578A31133F686AE5D1D8151B4C7A38197F039895311D44742DBC96`
and 22,172,864 stored bytes, holding 316 rows of local type 2 and 3.

| Sample | Row | Type | Decoded bytes | System bytes | Graphics bytes | Member name |
| ------ | --: | ---: | ------------: | -----------: | -------------: | ----------- |
| D | 0 | 3 | 11,456 | 6,528 (`0x1980`) | 4,928 (`0x1340`) | `prop_am_card_tarot_deck_01a.#ft` |
| E | 1 | 3 | 75,344 | 15,552 (`0x3CC0`) | 59,792 (`0xE990`) | `prop_am_candlestick_02a.#ft` |
| F | 8 | 3 | 2,423,888 | 48,064 (`0xBBC0`) | 2,375,824 | `mint_peacock_taxidermy_01.#ft` |

The system length is the split the shared offset/pointer inference recovers
from the vertex-buffer graphics pointers and the mesh-blob marker; for a native
row the archive page metadata supplies the same number. The page map sits at
system `+0x17D0`, `+0x3950` and `+0x4410` for D, E and F and declares one
system page in each.

## Root header

Offsets are system-relative. Values are from sample D unless stated.

| Offset | Size | Observation | D | E | Notes |
| -----: | ---: | ----------- | - | - | ----- |
| `+0x00` | 8 | Observed in 24/24 | `0` | `0` | A parser MUST require the zero word |
| `+0x08` | 8 | Observed in 24/24 | `0x500017D0` | `0x50003950` | Page-map pointer, same slot as a resource-level drawable |
| `+0x10` | 8 | Observed in 24/24 | `0x50000AE0` | `0x50001F90` | Reaches a record with a `u64` `2` at `+0x10` and a name pointer at `+0x18`; meaning **Unknown** |
| `+0x18` | 8 | Observed in 24/24 | `0x500006B0` | `0x50001890` | **The member drawable**; see below |
| `+0x20` | 8 | Observed in 24/24 | `0x50001048` | `0x50001DC8` | Reaches a record with repeated `0x3C00`/`0xBC00` words; meaning **Unknown** |
| `+0x28` | 8 | Observed in 24/24 | `0x50001270` | `0x50000390` | Reaches a record beginning with `0.70711` floats; meaning **Unknown** |
| `+0x30` | 8 | Observed in 24/24 | `[1, 1, 1, 1]` | `[1, 1, 2, 6]` | Four `u16`; see [counts](#counts-at-0x30) |

Only `+0x18` is followed to a drawable. The other three pointers are not
scanned for further drawables: no sample reaches one, so treating them as
component tables would be an invention.

## Member drawable

The target of `+0x18` is an `rmcDrawable`. Its header uses the same offsets as
[the resource-level drawable](../drawables/README.md), with two differences:

| Field | Resource-level drawable | Fragment member |
| ----- | ----------------------- | --------------- |
| `drawable +0x08` | System page-map pointer | Zero in 24/24; the containing resource owns the page map |
| `drawable +0xB8` | `0x103` in both named drawable rows | `3` in 24/24 |

Everything else was read at the same offsets: shader group `+0x10`, skeleton
`+0x18`, the bounds block `+0x20..+0x4F`, four LOD slots `+0x50..+0x6F`, LOD
distances `+0x70`, flag words `+0x80`, the name pointer `+0xA8` and the list
pointer `+0xB0`. The name pointer holds the fragment name, for example
`prop_am_card_tarot_deck_01a.#ft`; the `#ft` suffix appears in all 24 samples.
The suffix is the content evidence the explorer uses to distinguish a fragment
from a plain drawable, not a local type ID.

Sample D: two populated LOD slots, one model and one geometry each, one shader.
Sample E: four populated LOD slots, one model and two geometries each. Sample
F : two populated LOD slots, one model and four geometries each.

## Counts at `+0x30`

The four `u16` are not established. The first is `1` in all 24 samples; the
others vary from `1` to `49`. One row, `prop_am_orn_modern_04a.#ft`, stores
`[1, 2, 2, 2]` and still holds exactly one member drawable, so the second word
is not a drawable count. The values are exposed as stored and MUST NOT be read
as component counts.

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

## Drawable dictionaries

No row in the 40 decoded samples holds a table of drawable references. The 224
type-3 rows name themselves `#ft`. `FRAG-F06` records that no drawable
dictionary member table was located: the assignments for member enumeration and
member selection therefore remain unimplemented, and a parser MUST NOT invent a
member table from the fragment root.

## Limits

- 24 decoded rows from one nested archive, one build. Other archives, types and
  builds were not inspected.
- Only the member drawable at `+0x18` is understood. Multi-drawable fragments,
  child placements, damage-state selection and physics data were not observed.
- The three other root pointers reach records that were not interpreted.
- No fragment root field that selects a damage state or a component subset was
  identified.
