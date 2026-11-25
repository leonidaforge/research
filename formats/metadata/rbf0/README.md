# RBF0

RBF0 is a binary encoding observed in payloads that carry inline ASCII field names. It is identified by the four bytes `52 42 46 30`, ASCII `RBF0`, at offset 0.

RBF0 payloads were observed in RPF9 rows of type ID 11 inside a nested archive. In the analysed payloads the root name is fixed, several field names repeat across files, and text values differ. The purpose of the document type is **Unknown**.

The name expands to nothing established. `RBF` is a descriptive label only.

## Status

| Part                                       | Status                                      |
| ------------------------------------------ | ------------------------------------------- |
| Magic                                      | Confirmed (8 rows, 1 archive, RBF0-F01)     |
| Little-endian integers                     | Probable (RBF0-F02, RBF0-F03)               |
| Fixed 12-byte header prefix                | Confirmed (same rows, RBF0-F02)             |
| Root name                                  | Confirmed for this document type (RBF0-F03) |
| Field names are structure, values are data | Probable (RBF0-F04)                         |
| Field tag grammar                          | Unknown                                     |
| Type system and numeric encoding           | Unknown                                     |
| Other document types and other archives    | Not investigated                            |

The `metadata/` category is used because the payloads carry length-prefixed names and repeated structure (RBF0-F04, **Probable**). The purpose of the document is not established by that placement.

## Header

The first 12 bytes are the same in all eight samples:

| Offset  | Type     | Value          | Meaning                              |
| ------- | -------- | -------------- | ------------------------------------ |
| `+0x00` | 4 bytes  | `52 42 46 30`  | Magic `RBF0`                         |
| `+0x04` | `u16`    | `0xFFFB`       | Unknown. Constant in the sample      |
| `+0x06` | `u32`    | `1`            | Unknown. Constant in the sample      |
| `+0x0A` | `u16`    | `0x0011` (17)  | Length of the root name that follows |
| `+0x0C` | 17 bytes | not reproduced | Root name; 17 bytes, no terminator   |

All integers observed so far are little-endian. `0xFFFB` and the value `1` may be a version pair; that is **Speculative**.

## Body

After the root name the body interleaves names and values:

- Field names appear as length-prefixed ASCII. A 17-byte root name and several shorter nested names were observed.
- A `u16` length precedes some names. Names recur across files with identical spelling.
- Markers `0x6003` and `0xFFFD` appear before some fields. `0xFFFF` follows some strings. The eight-byte terminator `FF FF FF FF FF FF FF FF` ends the payload.
- Printable ASCII text values are present. A `u32` length precedes at least one of them.

Because names repeat across files while values change, the names encode structure. That reading is **Probable**; the exact tag grammar is **Unknown**. The byte-level observations are in [evidence/rbf0/INDEX.md](../../../evidence/rbf0/INDEX.md).

## Sample

The nested archive, fingerprints and verified rows are recorded in [evidence/rbf0/INDEX.md](../../../evidence/rbf0/INDEX.md), findings RBF0-F01 to RBF0-F07. Rows were chosen from the archive's 156 type 11 rows to cover small, medium and large payloads. The selection was not random.

## Row storage

The nested archive's row records report mode 1 and no chunk table. The storage and extraction observation is recorded in RPF9-F118. The eight verified RBF0 payloads decode from that framing. One row of the archive failed with a DEFLATE error.

## Identification

The type ID is not used as an identifier in this research. Identification uses the payload bytes.

## Limits

- One archive, one document type, eight decoded rows. Other RBF0 documents may use a different root name and different tags.
- No executable code path was traced. Nothing here states how the engine selects this encoding or validates it.
- The payload text, including the root and field names, was not published. It is game content.
- The tag grammar was not decoded, so no general parser can be written from this document.

## Next experiments

- Parse the `u16` length/marker stream across all 156 rows of the nested archive and check whether the grammar is consistent.
- Compare with a second RBF0-bearing archive to test whether the root name identifies the document schema.
- Search the executable for the magic constant `0x30464252` and for references to the root name.
- Test whether repeated names form a fixed schema that can be recovered once per document type.
