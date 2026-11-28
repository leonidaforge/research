# RBF0

RBF0 is a binary token stream identified by the four bytes `52 42 46 30`, ASCII `RBF0`, at offset 0. It carries a per-document name table, nested elements, typed values and text nodes. The document is markup: a named root element holds named children, and those hold attributes, values and text. The name expands to nothing established.

RBF0 payloads occur in RPF9 type 11 rows, but the type ID does not identify the encoding. The same type also carries `PSIN` payloads.

## Status

| Part | Status |
| ---- | ------ |
| Magic | Confirmed (238 unique payloads, RBF0-F01) |
| Versioned and versionless headers | Confirmed (1,459 and 3 payloads of `data.rpf`, RBF0-F02, RBF0-F17, RBF0-F23) |
| Token word and name table | Confirmed (RBF0-F04, RBF0-F11) |
| Element form | Confirmed (RBF0-F05, RBF0-F18) |
| Value widths | Confirmed (RBF0-F16, RBF0-F20) |
| Number classes | Confirmed: type 1 is an integer, type 4 a double (RBF0-F21) |
| Text nodes | Confirmed; each ends with one NUL outside its value (RBF0-F12, RBF0-F19) |
| Attributes | Confirmed token form and position (RBF0-F08) |
| Terminators | Confirmed; the trailing `FF` run is the close of the open elements (RBF0-F10, RBF0-F14) |
| Nesting and document size | Confirmed to 35 levels and 2,372,401 bytes (RBF0-F22) |
| Document family | Confirmed at family level: UI description and tuning documents (RBF0-F25) |
| Field semantics | Unknown |
| Whether the name set identifies a schema | Unknown |
| Versionless variant as a family or a rare form | Unknown |

The `metadata/` category is used because the payloads carry a name table and typed records. The family of document is now established (RBF0-F25); the meaning of individual fields is not.

## Population

Two populations were examined, and they are not the same thing.

**The exhaustive census of `data.rpf`.** A recursive walk of `<GAME_ROOT>/data.rpf` decoded every reachable RBF0 payload and nothing was sampled: 41 archives opened, 23,075 entries walked, 1,462 payloads whose first four bytes are the magic, 1,462 decoded to the end of the root element, 0 failures and 0 limit refusals. They are 1,395 distinct payloads by SHA-256 of the decoded bytes. Sizes run from 98 to 2,372,401 bytes, element counts from 1 to 68,398, name tables from 4 to 204 names, and the deepest document nests 35 levels. This is the population the counts below describe (RBF0-F23).

**The earlier convenience sample.** 447 decoded occurrences and 238 unique payloads, selected from 18 nested archives at or below 2 MiB plus every readable type 11 RBF0 row of the 22 top-level archives. It establishes the grammar; it does not estimate a population. Its counts stay in this document where they describe a property the wider census confirms.

Selection of the earlier sample:

- Nested archives: the 18 RPF9 archives stored as type 0 rows of `<GAME_ROOT>/data.rpf` with logical size at or below 2 MiB, namely rows 0, 1, 3, 7, 8, 9, 13, 14, 15, 16, 19, 20, 23, 31, 32, 35, 37 and 38. Every readable type 11 row from each was extracted.
- Top-level archives: all 22 `.rpf` files in the game root and the `pack/` tree. Every readable type 11 row whose decoded payload begins with `RBF0` was included.

The independent parser consumes 238 of 238 unique payloads and 447 of 447 decoded occurrences with no unsupported token. The original 18-row sample remains a subset.

**Outside `data.rpf`.** 19 other archives were walked under a 60,000-entry bound each, 296,590 entries in total. Five payloads beginning with `RBF0` were found — one in `textures.rpf`, one in `anim.rpf` and three in `pack/core_restofworld` — and all five decoded. `audio.rpf` holds audio streams and was not walked. RBF0 is effectively a `data.rpf` format in this installation (RBF0-F26).

## Header variants

All integers are little-endian unless stated otherwise.

### Versioned form

| Offset | Type | Value | Meaning |
| ------ | ---- | ----- | ------- |
| `+0x00` | 4 bytes | `52 42 46 30` | Magic `RBF0` |
| `+0x04` | `u16` | `0xFFFB` | Unknown. Candidate version marker; interpretation **Speculative** |
| `+0x06` | `u16` | `1` in every observed sample | Unknown. Candidate version; interpretation **Speculative** |
| `+0x08` | token stream | first token `0x0000` | Root element token |

Numbers in this form are 8 bytes. The versioned form occurs in 235 of the 238 unique payloads.

The header split and the number-width difference are confirmed. The labels `version marker` and `version` are descriptive; the reading of the two words as a version pair is **Speculative**.

### Versionless form

| Offset | Type | Value | Meaning |
| ------ | ---- | ----- | ------- |
| `+0x00` | 4 bytes | `52 42 46 30` | Magic `RBF0` |
| `+0x04` | token stream | first token `0x0000` | Root element token |

Numbers in this form are 4 bytes. The versionless form occurs in three unique payloads. Whether it is a stable family or a rare variant is **Unknown**.

The earlier reading of a fixed 10-byte prefix `52 42 46 30 FB FF 01 00 00 00` combined the versioned header with the first token. The header ends at `+0x08`; the token `00 00` at `+0x08` is the root element token, and the root name length follows it. The correction is recorded in the [research history](../../../evidence/rbf0/research-history.md).

## Token grammar

```text
Document   := "RBF0" VersionHeader? Element
VersionHeader := u16(0xFFFB) u16(version)
Element    := Token(type=0) Name? u32(reserved) u16(attribute_count)
              Attribute* BodyToken* u16(0xFFFF)
Attribute  := Token(type=1..6) Name? Value
BodyToken  := Element | Value | Text | u16(0xFFFF)
Value      := Token(type=1..6) Name? bytes
Text       := u16(0xFFFD) u32(byte_length) bytes
Token      := u16(name_index | (type_code << 12))
```

`Name?` is present only when the token's 12-bit name index equals the current name-table length. In that case a `u16` name length and the name bytes follow. A lower index reuses an earlier name. An index above the table length is an error.

- The name table is global to the document, not to an element.
- The root element uses name index 0 and defines the root name.
- The first token is `0x0000` in all 238 unique payloads.
- The reserved word is zero in every observed element. A nonzero value is reported but not rejected.

### Token classes

| Type code | Form | Observed value width | Occurrences in 238 unique payloads |
| --------- | ---- | -------------------- | ---------------------------------: |
| 0 | Element | `u32` reserved, `u16` attribute count, attributes, body, `u16 0xFFFF` | 90,321 elements |
| 1 | Integer | 8 bytes versioned, 4 bytes versionless | 21,671 / 201 |
| 2 | Zero-byte value | 0 bytes | 10 |
| 3 | Zero-byte value | 0 bytes | 11 |
| 4 | Double | 8 bytes versioned, 4 bytes versionless | 8,970 / 23 |
| 5 | Fixed value | 12 bytes | 1 |
| 6 | Length-prefixed bytes | `u16` length, then bytes | 31,780 attribute values; no field-position observation |
| `0xFFFD` | Text node | `u32` length, then bytes | 46,701 |
| `0xFFFF` | Close element | none | one per element |

The counts are the 238 unique payloads of the earlier sample. The exhaustive census of `data.rpf` counts 30,663 class 1, 3,627 class 2, 3,747 class 3, 39,291 class 4, 110,051 class 6 and 287,297 text nodes, with no class 5 value (RBF0-F23).

The table states widths and, for classes 1 and 4, the encoding. Types 2 and 3 carry no value bytes in any observation; whether they encode flags or something else is **Unknown**. Type 5 has one observation. Type 6 values appear in counted attribute positions and in body positions in the census.

Type codes 7 to 14 were not observed. The parser reports them as unsupported token classes; it does not skip them.

## Attributes

An attribute uses the same `name index | type code` word as a body token, followed by a value of that type. Attributes are counted by the element's `u16` attribute count and precede the body tokens.

| Observation | Value |
| ----------- | ----- |
| Attribute counts | 0, 1 or 2 |
| Observed attribute type codes | 1, 4 and 6 |
| Observed attribute name indices | 1, 3, 4, 6, 9, 11, 20, 21, 38 and 39 |
| Type 6 value form | `u16` length followed by bytes, no terminator |
| Distinct attribute names in `data.rpf` | 11, two of which carry the great majority of observations |

The earlier closed attribute set `0x6003`/`0x6004` is withdrawn. Those words are type 6 tokens with name indices 3 and 4. Attribute position outside the counted prefix is **Unresolved**: no observation shows an attribute between body fields.

## Names

A name is defined once per document on first use. The low 12 bits of a token are the name index; the index space is 0 to 4095. The earlier sample holds name tables of 5 to 41 names. The census of `data.rpf` holds 4 to 204 names per document and 518 distinct element names and 11 distinct attribute names across the population.

Root name lengths are 15, 17, 21, 22, 23, 29, 30 and 35 bytes in the earlier sample. The census finds 30 distinct root names. Names are game content and are not published. Whether the name set identifies a document schema is **Unknown**, though 611 of the 1,462 payloads share one root name and that group has one shape (RBF0-F18).

## Document shape

An element is a node with a name, an optional set of counted attributes, and a body that may hold nested elements, value tokens and text nodes, in the order the bytes store them. Repeated sibling elements are how the format writes a list: the grammar has no array token, and the census shows lists 68,000 elements long written as repeated children of one element (RBF0-F18).

The nesting is therefore unbounded by the grammar and bounded only by the document: the deepest payload of `data.rpf` nests 35 levels (RBF0-F22).

A decoded document is a tree, not a table: there is no schema section, no block table and no reference word. A name is the document's own, reused by index, and a value is the bytes its token class declares.

## Text and typed values

A text node is `u16 0xFFFD`, `u32` byte length, then bytes. The 238 unique payloads contain 46,701 text nodes, 2 to 2,360 bytes long. Text content is not published.

A text node's declared length includes one trailing `0x00` that is not part of the text: 287,267 of the 287,297 text nodes in `data.rpf` end with it. The 30 that do not are also not valid UTF-8, so no text value is observed to end without a terminator while being text (RBF0-F19).

A value token of type 1 or 4 carries a number whose width follows the header variant: 8 bytes in a versioned document and 4 bytes in a versionless document. The former special field `0x1006` is type 1 with name index 6; it is not a separate value class.

Type 6 values are `u16` length followed by bytes, with **no** terminator: none of the 110,051 observations in `data.rpf` ends with a NUL (RBF0-F20). Thirty of them contain a NUL before their end or are not valid UTF-8, and are kept as bytes.

## Number classes

Type 1 and type 4 are the same width but not the same encoding.

| Class | Encoding | Observations in `data.rpf` | Range |
| ----- | -------- | -------------------------- | ----- |
| 1 | 64-bit integer, little-endian | 30,663; 30,655 fit in `i32`, 1,079 negative | -2,125,891,426 to 4,289,044,108 |
| 4 | IEEE-754 binary64, little-endian | 39,291; every one finite, 27,169 integral | -431,602,080 to 65,536 |

The decisive observation is that one number is written both ways: `1` is `01 00 00 00 00 00 00 00` as class 1 and `00 00 00 00 00 00 F0 3F` as class 4. Read the other way round, the class 4 population is 64-bit integers in the range ±4.6 × 10¹⁸ and the class 1 population is denormal doubles, so each class has exactly one reading that makes the whole population coherent (RBF0-F21).

No field meaning follows from that: the classes establish how a number is stored, not what it describes. Classes 2 and 3 store no bytes, so their meaning cannot be recovered from the bytes at all.

## Terminators

`u16 0xFFFF` closes the innermost open element. Every element in the tested population has a close token.

Every payload ends with at least one close token, but the eight-byte trailer is not universal. Trailing `FF` bytes are 2 to 14 long across the 238 unique payloads:

| Trailing `FF` bytes | Payloads |
| ------------------- | -------: |
| 2 | 1 |
| 6 | 130 |
| 8 | 101 |
| 10 | 5 |
| 14 | 1 |

The earlier claim that every payload ends with exactly four close words is rejected as a universal statement. Individual close words in a longer trailer have no observed per-word role.

A payload whose root element closes exactly at its last byte is what the census of `data.rpf` observes: all 1,462 payloads end with the close word of the root element, and the run of `FFFF` words before it is the close of each element still open, deepest first (RBF0-F23).

## The original 18-row subset

The original sample keeps its counts as a subset: 18 unique payloads, 15,305 text nodes, 14,127 attributes and 44 type 1 values. Those figures agree with the token parser. They do not describe the wider population.

The original rows are 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 72, 78, 90, 141, 154 and 155 of the nested archive. Sizes and fingerprints are in [evidence/rbf0/INDEX.md](../../../evidence/rbf0/INDEX.md).

## Document families

The census of `data.rpf` finds 30 distinct root element names among the 1,462 payloads. The table names each family by the SHA-256 of its root name, in the order of its population, and states the category the document falls in. Root names and text are game content and are not copied here (RBF0-F25).

| Root name SHA-256 (first 16 hex) | Payloads | Category |
| -------------------------------- | -------: | -------- |
| `7bde64afe51f9997` | 611 | UI prefab definition |
| `ad2747782d11cbec` | 191 | UI animation node graph |
| `8e55e354b56f6fab` | 146 | UI screen |
| `65f40fea396e3a8c` | 136 | Credits page |
| `704b31c180650bdc` | 125 | Movie subtitle container |
| `db86519e8bb54b8b` | 70 | Movie view |
| `9d64d9313349baa7` | 65 | UI flow block |
| `de4a6d551c42ef15` | 32 | UI feedback context |
| `2529a7b69e97a7b4` | 20 | Credits configuration |
| `aa7c28fe4c0a4e4e` | 14 | UI subscreen prefab |
| `cd72942b74b73808` | 11 | UI core control prefab |
| `f2c868151aae8531` | 10 | UI panel |
| `1a09f611ed7179bc` | 6 | UI grid |
| `0e80d20d9125b494` | 5 | Progress dataset |
| `cf96e2ac735cbf34` | 4 | Safe-area configuration |
| `e4a870e1d7aff5d2` | 2 | Tuning file |
| 14 further roots | 1 each | One tuning file, one combat tunables table, one font mapping, and eleven single-instance UI stores and settings collections |

The shapes agree with the categories. A prefab document is a root, one container child and repeated item children, each item carrying one or two attributes whose type-6 values name an engine class, and optionally a text node. A credits page is the same shape with text nodes in place of class names. A UI screen is a deeper tree: repeated layout nodes with a path, a name, an alignment pair and a parameter block. Depth follows the category: the deepest documents are screens and animation graphs.

Element names are drawn from the engine's UI vocabulary: 518 distinct element names, 11 distinct attribute names of which two carry the great majority of attribute observations, and type-6 values that read as engine class names. A type-6 value is a class name rather than a value, which is why documents of one family share a vocabulary.

That establishes what RBF0 is for, at family level: it serialises the engine's UI description and tuning data. It does not establish what any single field means.

## Tools

`tools/rbf0/rbf0_inspect.py` parses the grammar and reports header variants, token counts, value widths and name hashes. It does not print names or text values.

```text
python tools/rbf0/rbf0_inspect.py <payload> [--json] [--max-depth 256]
```

Exit code 0 means the document was consumed to the end with no unsupported token. Exit code 2 means a structural or token error; the report includes the first failing offset and a token class. The parser rejects a truncated token, a length past the end, a name index beyond the table, an unterminated element and excessive nesting depth.

Synthetic fixtures are generated by `tools/rbf0/synthetic.py`. Tests use those fixtures:

```text
python -m unittest discover -s tools/rbf0 -p "test_*.py"
```

The exhaustive census is produced by the implementation's own decoder, which walks the archives, decodes every payload and tallies the outcomes without writing any document out:

```text
cargo run -p lforge-rage9 --release --example rbf0_population -- \
    <GAME_ROOT>/data.rpf --executable <EXECUTABLE> --recursive --values
```

The command and what it reports are described in the implementation repository; see [RBF0 metadata decoding](https://github.com/leonidaforge/leonida-forge/blob/main/docs/formats/rbf0.md).

## Limits

- One build and one local installation were examined. `data.rpf` was walked exhaustively; the other archives were walked under a bound and are reported separately in the evidence index.
- No executable code path was traced. The loader and the encoding name are **Unknown**.
- Field semantics and the meaning of the reserved word are **Unknown**. The number classes establish a storage encoding, not a meaning.
- Types 2 and 3 have 3,627 and 3,747 observations and carry no bytes; type 5 has one observation in the earlier sample and none in `data.rpf`.
- Attribute position outside the counted prefix is **Unresolved**.
- The versionless variant has three samples in `data.rpf`, all in the same archive set.
- Names and text values are game content and are not copied into this repository.

## Next experiments

- Find more versionless payloads and test whether they form a stable family.
- Test types 2 and 3 against documents whose numeric or flag fields can be predicted, since the bytes carry no value.
- Test whether the type-6 class names and the element names reproduce the 32-bit hashes a `PSIN` schema stores, which would make one format's vocabulary the other's dictionary. A first measurement over 13 `PSIN` documents finds 16 of 1,092 stored hashes reproduced, all generic field and enum-member names and no structure name (RBF0-F27); the test should be repeated over the whole `PSIN` population before any claim about coverage.
- Search the executable for the magic constant `0x30464252` and for the loader that reads these documents, without publishing key material.
- Test whether the name set predicts a document schema across files that share a root name; the census shows 30 root families, so the test now has 30 groups to run over.
