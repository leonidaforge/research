# Fragment evidence index

Payload observations from the Scarlett build
[e95020b2](../../builds/gta-vi/scarlett-e95020b2/README.md). No executable code
path was traced for this subject. Every finding is **Private-evidence
supported**: it is checkable against a local installation but not from this
repository alone.

The subject is the decoded payload structure of every row that carries local
type ID 3 in the 27 extracted nested archives that declare the type: 5,553
rows. Findings are cited from
[formats/resources/fragments/README.md](../../formats/resources/fragments/README.md).

## Coverage

The first iteration decoded 40 rows of one nested archive and built the layout
table from the 24 that hold a member drawable. The whole-population run reads
all 5,553 rows and confirms the layout.

| Quantity                                                  | Value |
| --------------------------------------------------------- | ----- |
| Nested archives that declare type-3 rows                  | 27    |
| Type-3 rows found                                         | 5,553 |
| Rows with the root shape                                  | 5,553 |
| Rows with exactly one member drawable                     | 5,553 |
| Rows where `+0x10`, `+0x20` or `+0x28` reaches a drawable | 0     |
| Rows whose member name carries the `#ft` suffix           | 5,553 |
| Rows with two or more member drawables                    | 0     |

## Samples

The detailed samples come from `<GAME_ROOT>/levels.rpf`, row 5, SHA-256
`450B6A5A95578A31133F686AE5D1D8151B4C7A38197F039895311D44742DBC96`.

| Sample | Row | Decoded bytes | System | Member name                       |
| ------ | --: | ------------: | -----: | --------------------------------- |
| D      |   0 |        11,456 |  6,528 | `prop_am_card_tarot_deck_01a.#ft` |
| E      |   1 |        75,344 | 15,552 | `prop_am_candlestick_02a.#ft`     |
| F      |   8 |     2,423,888 | 48,064 | `mint_peacock_taxidermy_01.#ft`   |

## Findings

| Finding  | Claim                                                                                                                                                                                                  | Evidence                                                                                 | Strength                    |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------- | --------------------------- |
| FRAG-F01 | The fragment root header holds a zero word at `+0x00`, a system page-map pointer at `+0x08`, three further system pointers at `+0x10`, `+0x20` and `+0x28`, and the member-drawable pointer at `+0x18` | `CROSS_SAMPLE` 5,553 rows                                                                | Confirmed                   |
| FRAG-F02 | The target of `+0x18` is an `rmcDrawable` at the resource-level offsets whose page-map word is zero and whose `+0xB8` word is `3`                                                                      | `CROSS_SAMPLE` 5,553 rows; the chain resolves to geometries with graphics vertex buffers | Confirmed                   |
| FRAG-F03 | Every decoded row holds exactly one member drawable; the three other root pointers never reach a drawable                                                                                              | `CROSS_SAMPLE` 5,553 rows; every slot tested                                             | Confirmed                   |
| FRAG-F04 | The member name carries the `#ft` suffix                                                                                                                                                               | `CROSS_SAMPLE` 5,553 rows                                                                | Confirmed                   |
| FRAG-F05 | The four `u16` at `+0x30` are not component counts; the first is `1` in 5,522 rows and `2` in 31, and the row with `[1, 2, 2, 2]` still holds one drawable                                             | `CROSS_SAMPLE` 5,553 rows, one drawable each                                             | Confirmed                   |
| FRAG-F06 | No drawable dictionary member table is located in a fragment root                                                                                                                                      | `CROSS_SAMPLE` 5,553 rows; the same table was located in the type-4 population           | Confirmed within fragments  |
| FRAG-F07 | No fragment row carries components, child placements or a damage-state table                                                                                                                           | `CROSS_SAMPLE` 5,553 rows; every root slot tested for the member form                    | Confirmed within the corpus |
| FRAG-F08 | A fragment is recognised by its root structure, not by the member name's `#ft` suffix                                                                                                                  | `BINARY` root slots; `CROSS_SAMPLE` 5,553 rows carry the suffix                          | Confirmed                   |

FRAG-F06 corrects an earlier claim. The first iteration reported that no drawable
dictionary member table existed, on the basis of 40 decoded type-3 rows of one
nested archive. That search covered fragments only. The table does exist in this
build, in the 8,209 rows that carry local type ID 4; its grammar is documented in
[drawable-dictionaries](../drawable-dictionaries/INDEX.md).

## Validation

- Sample D's decoded scene bounds equal the member drawable's bounds block to
  quantisation error, so the geometry needs no extra placement.
- The member drawable decodes through the same walker as a resource-level
  drawable once the page-map word is allowed to be zero.
- The whole-population run tested every root slot of every row for the member
  form: only `+0x18` ever holds a drawable. The records behind the other three
  pointers hold float matrices, fixed-point `0x3C00`/`0xBC00` words and a `u64`
  `2` with a name pointer; their shapes are consistent with collision and shape
  data, which was not interpreted.
- Assumptions rejected: the `+0x30` words are not drawable counts
  (`prop_am_orn_modern_04a.#ft` stores two and holds one drawable); the other
  root pointers are not component arrays; the member-name suffix is not the
  discriminator.
