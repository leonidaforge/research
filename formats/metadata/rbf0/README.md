# RBF0

RBF0 is a binary encoding observed in payloads that carry inline ASCII field names. It is identified by the four bytes `52 42 46 30`, ASCII `RBF0`, at offset 0.

RBF0 payloads were observed in RPF9 rows of type ID 11 inside a nested archive. In the 18 verified payloads the root name is one of two values, field names repeat across files, and text values differ. The purpose of the document type is **Unknown**.

The name expands to nothing established. `RBF` is a descriptive label only.

## Status

| Part                                      | Status                                                       |
| ----------------------------------------- | ------------------------------------------------------------ |
| Magic                                     | Confirmed (18 rows, 1 nested archive, RBF0-F01)              |
| Fixed 10-byte header prefix               | Confirmed (18 rows, RBF0-F02)                                |
| Root name length and bytes                | Confirmed (18 rows, RBF0-F03)                                |
| Object body and terminators               | Confirmed (18 rows, RBF0-F05, RBF0-F10)                      |
| Local field dictionary                    | Confirmed (18 rows, RBF0-F04)                                |
| Observed field identifier groups          | Confirmed for the observed groups (RBF0-F06)                 |
| String and attribute value encodings      | Confirmed (15,305 strings, 14,127 attributes, RBF0-F07, F08) |
| Fixed 8-byte value class                  | Observed in one row (RBF0-F09)                               |
| Field semantics                           | Unknown                                                      |
| Document purpose                          | Unknown                                                      |
| Other RBF0-bearing archives               | Not found in the surveyed inventory (RBF0-F11)               |

The `metadata/` category is used because the payloads carry length-prefixed names and a local field dictionary (RBF0-F04). The purpose of the document is not established by that placement.

## Header

The first 10 bytes are identical in all 18 verified samples:

| Offset  | Type     | Value         | Meaning                              |
| ------- | -------- | ------------- | ------------------------------------ |
| `+0x00` | 4 bytes  | `52 42 46 30` | Magic `RBF0`                         |
| `+0x04` | `u16`    | `0xFFFB`      | Unknown. Constant in the sample      |
| `+0x06` | `u32`    | `1`           | Unknown. Constant in the sample      |
| `+0x0A` | `u16`    | 17 or 15      | Length of the root name that follows |
| `+0x0C` | variable | not published | Root name; no terminator             |

Seventeen samples carry a 17-byte root name. One sample carries a 15-byte root name. The `u16` length at `+0x0A` precedes the name in every sample, so the old reading of a fixed 12-byte prefix was too strong (RBF0-F02).

All integers observed so far are little-endian. `0xFFFB` and the value `1` may be a version pair; that is **Speculative**.

## Body

The body after the root name is a recursive object stream. The grammar below is confirmed for the 18 verified rows:

```text
Document  := Header Object
Header    := "RBF0" u16(0xFFFB) u32(1) u16(root_name_len) root_name
Object    := u32(0) u16(attribute_count) Attribute* Field* u16(0xFFFF)
Attribute := FieldId [u16(name_len) name] u16(value_len) value
Field     := FieldId [u16(name_len) name] FieldValue
FieldId   := u16
```

The name part in brackets is present only on the first occurrence of a field identifier in a payload. Later occurrences omit both the `u16` length and the name bytes (RBF0-F04).

`FieldValue` has three observed forms:

| Form          | Field identifier     | Encoding                                                                            |
| ------------- | -------------------- | ----------------------------------------------------------------------------------- |
| Object        | `0x0001`, `0x0002`   | Another `Object`                                                                    |
| String        | `0x0004` to `0x000A` | `u32(0)` `u16(0)` `u16(0xFFFD)` `u32(byte_len)` bytes `u16(0xFFFF)`                 |
| Fixed 8 bytes | `0x1006`             | Eight bytes, no length prefix and no terminator (one row, all bytes `FF`, RBF0-F09) |

An attribute is not a `Field`. It is encoded as `u16(value_len)` followed by bytes, with no terminator (RBF0-F08).

The low 12 bits of a field identifier are a definition slot. The observed payloads allocate slots `1, 2, 3, ...` in first-definition order. The high nibble groups the observed encodings: `0x0` for object and string identifiers, `0x1` for the fixed 8-byte value, and `0x6` for attributes. The meaning of the high nibble beyond these groups is **Unknown**.

Field identifiers are local to one payload. A recurring name can receive different identifiers in different files, and the same identifier can name different fields (RBF0-F04). Field names are the stable part of the vocabulary, not the identifiers.

## Field names

Across the 18 samples there are 118 field definitions and 18 distinct names. Names are ASCII, 4 to 17 bytes, and contain no NUL. The first two definitions are always the object fields; the third is an attribute in every sample. The attribute count changes later slot numbers: a payload with two attributes starts its first string field at slot 5 instead of slot 4 (RBF0-F06).

Because names repeat across files while identifiers are reassigned, the names are a per-payload dictionary rather than a fixed global table. Whether the set of names identifies a document schema is **Unknown**.

## String and attribute values

The string value form puts the length before the bytes. Across the 18 samples:

| Property                       | String values (RBF0-F07) | Attribute values (RBF0-F08) |
| ------------------------------ | ------------------------ | --------------------------- |
| Count                          | 15,305                   | 14,127                      |
| Length field                   | `u32`, includes NUL      | `u16`, excludes NUL         |
| Terminator inside value        | One `00` at the end      | None                        |
| Encoding                       | UTF-8                    | ASCII                       |
| Non-ASCII values               | 334                      | 0                           |
| Empty values                   | None observed            | None observed               |
| Length range (bytes)           | 2 to 1,990               | 8 to 26                     |

Every string value is followed by `u16(0xFFFF)`. Attribute values have no terminator; the next identifier follows immediately.

## Terminators

An object ends with `u16(0xFFFF)`. A string value also ends with `u16(0xFFFF)`. All 18 payloads end with exactly eight `FF` bytes, which is four consecutive `0xFFFF` words: the last string value, its object, the container object and the root object (RBF0-F10).

## Sample

Eighteen rows of one nested archive decode as RBF0: rows 1, 5, 15, 72, 78, 90, 141 and 155 (the original selection), plus rows 0, 2, 3, 4, 6, 7, 8, 9, 10 and 154 (decoded in this iteration). Sizes and fingerprints are in [evidence/rbf0/INDEX.md](../../../evidence/rbf0/INDEX.md), findings RBF0-F01 to RBF0-F13. The selection is not random.

A second nested archive in the inventory carries 155 type ID 11 rows. Three decoded rows start with `PSIN`, not `RBF0`. Four sampled type ID 11 rows from top-level pack archives also start with `PSIN`. Type ID 11 is therefore not an RBF0 identifier (RBF0-F11).

## Row storage

The RBF0-bearing nested archive's row records report mode 1 and no chunk table. The storage and extraction observation is recorded in RPF9-F118. The verified payloads decode from that framing (RBF0-F12). One row of the archive failed with a DEFLATE error in an earlier pass.

## Identification

The type ID is not used as an identifier in this research. Identification uses the payload bytes.

## Tools

`tools/rbf0/rbf0_inspect.py` parses the observed grammar and reports unsupported tags. It prints lengths, offsets and name hashes, not payload strings. Synthetic tests are in `tools/rbf0/test_rbf0_inspect.py`.

## Limits

- One RBF0-bearing archive, 18 of 156 rows. Not all rows were decoded.
- The sample is not random; rows were chosen for size coverage and for the grammar check.
- No executable code path was traced. Nothing here states how the engine selects this encoding or validates it.
- Field names and text values are game content and are not published.
- The meaning of the two root names, the field identifiers, the high-nibble groups and the header words `0xFFFB` and `1` are **Unknown**.
- The parser handles only the observed forms. Unknown identifiers, value tags or header markers are reported as unsupported.

## Next experiments

- Decode all 156 rows and check the grammar and terminator counts against the full set.
- Search a second RBF0-bearing archive; inventory type ID 11 alone does not identify RBF0.
- Test other high-nibble groups against documents that carry numeric or binary values.
- Search the executable for the magic constant `0x30464252` and for references to the root names to establish the loader and the encoding name, without publishing key material.
- Test whether the name set predicts a document schema across files that share a root name.
