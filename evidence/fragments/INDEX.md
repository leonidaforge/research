# Fragment evidence index

Payload observations from the Scarlett build
[e95020b2](../../builds/gta-vi/scarlett-e95020b2/README.md). No executable code
path was traced for this subject. Every finding is **Private-evidence
supported**: it is checkable against a local installation but not from this
repository alone.

The subject is the decoded payload structure of the 224 rows that carry local
type ID 3 in row 5 of `levels.rpf`. Findings are cited from
[formats/resources/fragments/README.md](../../formats/resources/fragments/README.md).

## Samples

The parent archive is `<GAME_ROOT>/levels.rpf`, row 5, SHA-256
`450B6A5A95578A31133F686AE5D1D8151B4C7A38197F039895311D44742DBC96`. Forty
type-3 rows were decoded; 24 hold a member drawable and are the basis for the
findings.

| Sample | Row | Decoded bytes | System | Member name |
| ------ | --: | ------------: | -----: | ----------- |
| D | 0 | 11,456 | 6,528 | `prop_am_card_tarot_deck_01a.#ft` |
| E | 1 | 75,344 | 15,552 | `prop_am_candlestick_02a.#ft` |
| F | 8 | 2,423,888 | 48,064 | `mint_peacock_taxidermy_01.#ft` |

## Findings

| Finding | Claim | Evidence | Strength |
| ------- | ----- | -------- | -------- |
| FRAG-F01 | The fragment root header holds a zero word at `+0x00`, a system page-map pointer at `+0x08`, three further system pointers at `+0x10`, `+0x20` and `+0x28`, and the member-drawable pointer at `+0x18` | 24/24 decoded rows | Confirmed |
| FRAG-F02 | The target of `+0x18` is an `rmcDrawable` at the resource-level offsets whose page-map word is zero and whose `+0xB8` word is `3` | 24/24 decoded rows; the chain resolves to geometries with graphics vertex buffers | Confirmed |
| FRAG-F03 | Every decoded row holds exactly one member drawable; the three other root pointers never reach a drawable | 24/24 rows; the reachable records were dumped | Sample-verified |
| FRAG-F04 | The member name carries the `#ft` suffix | 24/24 rows | Confirmed |
| FRAG-F05 | The four `u16` at `+0x30` are not component counts; the first is `1` in every row and the row with `[1, 2, 2, 2]` still holds one drawable | 24/24 rows | Sample-verified |
| FRAG-F06 | No drawable dictionary member table was located in the decoded samples | 40 decoded rows; no table of drawable references | Null result, not exhaustive |

## Validation

- Sample D's decoded scene bounds equal the member drawable's bounds block to
  quantisation error, so the geometry needs no extra placement.
- The member drawable decodes through the same walker as a resource-level
  drawable once the page-map word is allowed to be zero.
- Assumptions rejected: the `+0x30` words are not drawable counts
  (`prop_am_orn_modern_04a.#ft` stores two and holds one drawable); the other
  root pointers are not component arrays.
