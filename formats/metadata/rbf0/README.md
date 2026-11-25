# RBF0

RBF0 is a binary token stream identified by the four bytes `52 42 46 30`, ASCII `RBF0`, at offset 0. It carries a per-document name table, nested elements, typed values and text nodes. The purpose of the document type is **Unknown**. The name expands to nothing established.

RBF0 payloads occur in RPF9 type 11 rows, but the type ID does not identify the encoding. The same type also carries `PSIN` payloads.

## Status

| Part | Status |
| ---- | ------ |
| Magic | Confirmed (238 unique payloads, RBF0-F01) |
| Versioned and versionless headers | Confirmed (235 and 3 unique payloads, RBF0-F02, RBF0-F17) |
| Token word and name table | Confirmed (RBF0-F04, RBF0-F11) |
| Element form | Confirmed (RBF0-F05) |
| Value widths | Confirmed widths; meanings Unknown (RBF0-F16) |
| Text nodes | Confirmed (46,701 nodes, RBF0-F12) |
| Attributes | Confirmed token form; position outside the counted prefix Unknown (RBF0-F08) |
| Terminators | Confirmed; eight-byte trailer not universal (RBF0-F10) |
| Root name lengths | Confirmed (RBF0-F03) |
| Field semantics | Unknown |
| Document purpose | Unknown |
| Whether the name set identifies a schema | Unknown |
| Versionless variant as a family or a rare form | Unknown |

The `metadata/` category is used because the payloads carry a name table and typed records. The purpose of the document is not established by that placement.

## Population

The tested population is 447 decoded RBF0 payloads, 238 unique by SHA-256 of the decoded bytes:

- 156 type 11 rows of the original nested archive, row 0 of `<GAME_ROOT>/data.rpf`;
- all readable type 11 rows of 17 more RPF9 archives extracted from `<GAME_ROOT>/data.rpf`, selected at or below 2 MiB;
- all readable top-level type 11 rows that begin with `RBF0`, nine unique payloads.

The independent parser consumes 238 of 238 unique payloads and 447 of 447 decoded occurrences with no unsupported token. The original 18-row sample remains a subset.

An earlier private walker reported 31 of 31 payloads: 18 nested rows plus 13 top-level payloads. That 31-payload selection is not published. The 18 nested rows are reproducible, and every reachable top-level RBF0 row adds nine unique payloads (27 total), all of which parse. The full recount is larger, so the private 31-payload figure is treated as a subset result, not as the tested population.

## Header variants

All integers are little-endian unless stated otherwise.

### Versioned form

| Offset | Type | Value | Meaning |
| ------ | ---- | ----- | ------- |
| `+0x00` | 4 bytes | `52 42 46 30` | Magic `RBF0` |
| `+0x04` | `u16` | `0xFFFB` | Version marker |
| `+0x06` | `u16` | `1` in every observed sample | Version |
| `+0x08` | token stream | first token `0x0000` | Root element token |

Numbers in this form are 8 bytes. The versioned form occurs in 235 of the 238 unique payloads.

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
| 1 | Number | 8 bytes versioned, 4 bytes versionless | 21,671 / 201 |
| 2 | Zero-byte value | 0 bytes | 10 |
| 3 | Zero-byte value | 0 bytes | 11 |
| 4 | Number | 8 bytes versioned, 4 bytes versionless | 8,970 / 23 |
| 5 | Fixed value | 12 bytes | 1 |
| 6 | Length-prefixed bytes | `u16` length, then bytes | 31,780 attribute values; no field-position observation |
| `0xFFFD` | Text node | `u32` length, then bytes | 46,701 |
| `0xFFFF` | Close element | none | one per element |

The table states widths, not semantics. Types 2 and 3 carry no value bytes in 21 observations; whether they encode flags or something else is **Unknown**. Type 5 has one observation. Type 6 appears only in counted attribute positions in this population.

Type codes 7 to 14 were not observed. The parser reports them as unsupported token classes; it does not skip them.

## Attributes

An attribute uses the same `name index | type code` word as a body token, followed by a value of that type. Attributes are counted by the element's `u16` attribute count and precede the body tokens.

| Observation | Value |
| ----------- | ----- |
| Attribute counts | 0, 1 or 2 |
| Observed attribute type codes | 1, 4 and 6 |
| Observed attribute name indices | 1, 3, 4, 6, 9, 11, 20, 21, 38 and 39 |
| Type 6 value form | `u16` length followed by bytes, no terminator |

The earlier closed attribute set `0x6003`/`0x6004` is withdrawn. Those words are type 6 tokens with name indices 3 and 4. Attribute position outside the counted prefix is **Unresolved**: the sample does not show an attribute between body fields.

## Names

A name is defined once per document on first use. The low 12 bits of a token are the name index; the index space is 0 to 4095. Observed name tables hold 5 to 41 names. The original 18-row subset holds 118 definitions and 18 distinct names.

Root name lengths are 15, 17, 21, 22, 23, 29, 30 and 35 bytes. Names are game content and are not published. Whether the name set identifies a document schema is **Unknown**.

## Text and typed values

A text node is `u16 0xFFFD`, `u32` byte length, then bytes. The 238 unique payloads contain 46,701 text nodes, 2 to 2360 bytes long. Text content is not published.

A value token of type 1 or 4 carries a number whose width follows the header variant: 8 bytes in a versioned document and 4 bytes in a versionless document. The former special field `0x1006` is type 1 with name index 6; it is not a separate value class.

Type 6 values are `u16` length followed by bytes. In the tested population they occur in attribute positions. The same token form is accepted in a field position by the grammar, but no field-position observation supports a claim about it.

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

## The original 18-row subset

The original sample keeps its counts as a subset: 18 unique payloads, 15,305 text nodes, 14,127 attributes and 44 type 1 values. Those figures agree with the token parser. They do not describe the wider population.

The original rows are 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 72, 78, 90, 141, 154 and 155 of the nested archive. Sizes and fingerprints are in [evidence/rbf0/INDEX.md](../../../evidence/rbf0/INDEX.md).

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

## Limits

- One build and one local archive set were examined. The nested archives are bounded at 2 MiB and the sample is not random.
- No executable code path was traced. The loader, the encoding name and the document purpose are **Unknown**.
- Field semantics, the meaning of the reserved word and the meaning of the type codes beyond their widths are **Unknown**.
- Types 2 and 3 have 21 observations; type 5 has one. Field-position type 6 is unobserved.
- Attribute position outside the counted prefix is **Unresolved**.
- The versionless variant has three samples.
- Names and text values are game content and are not copied into this repository.

## Next experiments

- Find more versionless payloads and test whether they form a stable family.
- Decode all type 11 rows above the 2 MiB nested bound and compare the token classes.
- Test type 6 in a field position and types 2, 3 and 5 against documents that carry numeric or flag values.
- Search the executable for the magic constant `0x30464252` and for references to the root names to establish the loader and the encoding name, without publishing key material.
- Test whether the name set predicts a document schema across files that share a root name.
