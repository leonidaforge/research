# Drawable dictionary evidence index

Payload observations from the Scarlett build
[e95020b2](../../builds/gta-vi/scarlett-e95020b2/README.md). No executable code
path was traced for this subject. Every finding is **Private-evidence
supported**: it is checkable against a local installation but not from this
repository alone.

The subject is the decoded payload structure of the 8,209 rows that carry local
type ID 4 in 53 extracted nested archives of the inventory expansion. Findings
are cited from
[formats/resources/drawable-dictionaries/README.md](../../formats/resources/drawable-dictionaries/README.md).

## Coverage

| Quantity                                 | Value  |
| ---------------------------------------- | ------ |
| Nested archives that declare type-4 rows | 53     |
| Type-4 rows found                        | 8,209  |
| Rows read                                | 8,209  |
| Rows that hold the dictionary root form  | 8,209  |
| Rows accepted by the content classifier  | 8,209  |
| Members enumerated                       | 12,480 |
| Rows that failed any structural check    | 0      |

Each row was reconstructed with its native page split. The archive page
metadata was present for all 8,209 rows, so no row depends on an inferred
system/graphics boundary. The shared offset/pointer inference disagrees with the
native split on 1,521 of the 8,209 rows, which is why the reported results use
the native split and why an inferred split is not evidence of a wrong resource.

Member counts, number of dictionaries: 1 → 7,181; 2 → 56; 3 → 5; 4 → 878; 6 → 1;
8 → 10; 11 → 1; 12 → 8; 13 → 2; 15 → 4; 16 → 55; 17 → 1; 27 → 2; 48 → 1; 83 → 2;
108 → 2.

## Findings

| Finding   | Claim                                                                                                                                                                                                                                                                                    | Evidence (type)                                                                                                                                                                                                                                                                                                                                | Strength                                                                 |
| --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| DDICT-F01 | The system segment starts with a zero word, then a system page-map pointer at `+0x08`                                                                                                                                                                                                    | `CROSS_SAMPLE` 8,209/8,209 rows                                                                                                                                                                                                                                                                                                                | Confirmed                                                                |
| DDICT-F02 | The words at `+0x10` and `+0x18` are `0` and `1` in every row; neither is the member count                                                                                                                                                                                               | `CROSS_SAMPLE` 8,209/8,209 rows                                                                                                                                                                                                                                                                                                                | Confirmed                                                                |
| DDICT-F03 | The root holds a `u32` hash array behind `+0x20` with count and capacity at `+0x28`, and a `u64` value array behind `+0x30` with count and capacity at `+0x38`                                                                                                                           | `CROSS_SAMPLE` 8,209/8,209 rows                                                                                                                                                                                                                                                                                                                | Confirmed                                                                |
| DDICT-F04 | The hash array is ascending and duplicate-free                                                                                                                                                                                                                                           | `CROSS_SAMPLE` 8,209/8,209 rows                                                                                                                                                                                                                                                                                                                | Confirmed                                                                |
| DDICT-F05 | Hash count equals value count, and each count equals its capacity                                                                                                                                                                                                                        | `CROSS_SAMPLE` 8,209/8,209 rows                                                                                                                                                                                                                                                                                                                | Confirmed                                                                |
| DDICT-F06 | Each hash equals `joaat` of a member drawable's name with its final extension (`.#dr`) removed                                                                                                                                                                                           | `CROSS_SAMPLE` 12,480/12,480 members                                                                                                                                                                                                                                                                                                           | Confirmed                                                                |
| DDICT-F07 | Every value is a system pointer to a member drawable whose page-map word is zero                                                                                                                                                                                                         | `CROSS_SAMPLE` 12,480/12,480 members                                                                                                                                                                                                                                                                                                           | Confirmed                                                                |
| DDICT-F08 | No empty dictionary was observed; the empty case is accepted only on structure plus the `+0x18` word                                                                                                                                                                                     | `CROSS_SAMPLE` 0 empty rows in 8,209                                                                                                                                                                                                                                                                                                           | Null result                                                              |
| DDICT-F09 | The inferred system/graphics boundary yields no usable dictionary on every row of the 53-archive corpus where it disagrees with native metadata; in the installation-wide rows it enumerates the dictionary on 25 of the 6,304 disagreements but cannot decode the member geometry there | `CROSS_SAMPLE` 1,521 disagreements of 8,209 rows: 1,521 no candidate, 0 usable; `CROSS_SAMPLE` 45,200 read rows: 6,304 disagreements (6,278 no candidate, 1 no root form), of which 25 enumerate every member; `BINARY` `levels.rpf!1355!3` at native `0x1080` gives 2,449 vertices, at inferred `0x553e` the member yields no renderable mesh | Confirmed for both corpora; the inferred boundary is never authoritative |
| DDICT-F10 | Member identity is the array position; a repeated hash or a shared drawable pointer does not remove an entry                                                                                                                                                                             | `BINARY` parser rules; `SYNTHETIC` duplicate fixtures                                                                                                                                                                                                                                                                                          | Confirmed                                                                |
| DDICT-F11 | Types 4, 5 and 16 share only the zero word, the page map and the `+0x18` word; in the rows read type 16 parses as a texture dictionary and not as a drawable dictionary                                                                                                                  | `CROSS_SAMPLE` 8,209 type-4, 3 type-5 and 285 type-16 rows; scoped to those rows                                                                                                                                                                                                                                                               | Confirmed for the sampled rows                                           |

## Validation

- Every member value was resolved with the member-drawable test and with the
  structural walk, so a row that reads as a dictionary also decodes as one.
- The hash rule was checked in both directions: the suffix-bearing name never
  matches and the stem always does, over 12,480 members of 8,209 dictionaries.
- The classifier and the parser agree on all 8,209 rows, so a declared type-4
  row is never accepted on its declaration alone.
- Assumptions rejected: the `+0x18` word is not the member count; the member
  name is not hashed with its extension; the capacity is not distinct from the
  count in this corpus; the root stores no per-member transform.
- Coverage limit: the corpus is one build and the 53 nested archives the
  inventory could read. It is not the whole installation, and no claim here
  extends to build variants.

## Reproducing the aggregates

Two ignored tests in `apps/desktop/src/files/model.rs` produce every number
above:

- `surveys_native_type_4_rows` walks the caller-named archives, selects the
  declared type-4 rows, and prints the counts, the member-state histogram, the
  hash match counts, the root words and every failure with its reason.
- `surveys_native_type_3_rows` does the same for type-3 rows and prints how many
  member drawables each root slot reaches.

They are ignored by default and read only caller-supplied paths:
`LF_TEST_ARCHIVE_LIST` names a file of extracted archives, `LF_TEST_CHAIN_LIST`
names a file of census chains (`data.rpf!7!0`) that the survey resolves to the
archives that hold them, and `LF_TEST_EXECUTABLE` names the executable that
supplies the archive keys. `LF_SURVEY_SELECTORS` prints the exact locator of
every dictionary with at least that many members.

The rendered members in the format document come from
`cargo run -p lforge-model --example dictionary_render -- <resource> --split
<hex|infer> [--member <index>]... [--textures <dir>] [--out <dir>]`, which is a
maintained, compile-checked consumer of the public API and depends on no desktop
code.
