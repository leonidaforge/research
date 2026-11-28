# 0DRP metadata resources

`0DRP` is the four bytes some RAGE metadata resources carry at system `+0x10`. It identifies a resource that stores the same self-describing tables a `PSIN` container holds — a structure schema, an enumeration table and blocks of typed records — as a resource with a system and a graphics segment instead of a container with sections.

The tag is a signature. Nothing here claims the bytes spell a format name, and no executable code path was traced.

## Status

| Part | Status |
| ---- | ------ |
| Tag and object type | Confirmed (ODRP-F01) |
| Header | Confirmed (ODRP-F02) |
| Structure table and its member pointer | Confirmed (ODRP-F03) |
| Field records and type word | Confirmed (ODRP-F04) |
| Enumeration table | Confirmed (ODRP-F05) |
| Block table and segment pointers | Confirmed (ODRP-F06) |
| Reference encoding | Confirmed (ODRP-F07) |
| Array, map and inline-array layouts | Confirmed (ODRP-F08) |
| Text references into a text block | Confirmed (ODRP-F09) |
| Root block | Confirmed (ODRP-F13) |
| Block type words | Confirmed for structure-typed record blocks and pools (ODRP-F14) |
| 16-byte text slot | Unknown (ODRP-F16) |
| Population | Confirmed, exhaustive for one archive (ODRP-F11) |
| Document family | Partial: label and dialogue tables, and one large object graph (ODRP-F19) |
| Field semantics | Unknown |

## Population

A recursive walk of `<GAME_ROOT>/data.rpf` found every row whose resource head carries the tag and decoded all of them:

| Measure | Value |
| ------- | ----- |
| Root archives walked | 1 |
| Nested archives entered | 41 |
| Entries walked | 23,075 |
| Resources carrying the tag | 15,768 |
| Decoded to full extent | 15,767 |
| Partial | 1, for four blocks no structure, pool element or established width describes (ODRP-F17) |
| Distinct payloads by SHA-256 | 15,672 |
| Row types | 1,286 type 11, 14,482 type 111 (ODRP-F18) |
| Sizes | 848 to 14,876,672 bytes |
| Structures per resource | 2 to 182 |
| Blocks per resource | 2 to 186 |
| Records per resource | 3 to 192,488 |
| Resolved text values | 4,215,226 |
| Deepest embedded structure | 3 levels |
| Resources carrying enumerations | 1,310, with 2,780 values in total (ODRP-F20) |
| Object type byte | `0x7A` in all 15,768 |

The 15,768 rows come from 16 distinct nested archives: `data.rpf` itself and 15 rows inside it. One nested archive holds 1,247 of them and the rest are spread over the others, up to 1,114 each.

## Stored layout

All words are little-endian. Offsets are in the reconstructed system segment.

| Offset | Type | Value | Meaning |
| ------ | ---- | ----- | ------- |
| `+0x00` | `u64` | 0 | Zero |
| `+0x08` | `u64` | system pointer | Address of the page map |
| `+0x10` | 4 bytes | `30 44 52 50`, ASCII `0DRP` | Tag |
| `+0x14` | `u8` | `0x7A` | Object type. Meaning **Unknown** |
| `+0x18` | `u64` | 0 | Zero |
| `+0x20` | `u32` | 1 to 89 | Root block, counted from one (ODRP-F13) |
| `+0x28` | `u64` | system pointer | Structure table |
| `+0x30` | `u64` | system pointer, 0 when absent | Enumeration table |
| `+0x38` | `u64` | system pointer | Block table |
| `+0x40` | `u64` | system pointer | Target not established (ODRP-F02) |
| `+0x48` | `u16` | — | Structure count |
| `+0x4A` | `u16` | — | Enumeration count |
| `+0x4C` | `u16` | — | Block count |
| `+0x4E` | `u16` | 0 to 8, mostly 0 | Meaning **Unknown** (ODRP-F02) |

A page map at `+0x08` follows the resource conventions: the resource states how many system pages and how many graphics pages it has, and the map stores each page's stream bytes. Every observed resource has one or two system pages and no graphics page (ODRP-F12).

## Schema tables

A structure record is 32 bytes:

| Offset | Type | Meaning |
| ------ | ---- | ------- |
| `+0x00` | `u32` | Structure name hash |
| `+0x04` | `u32` | Signature, a second hash beside the name |
| `+0x08` | `u32` | Flags |
| `+0x0C` | `u32` | Zero |
| `+0x10` | `u64` | System pointer to this structure's field records |
| `+0x18` | `u32` | Record size in bytes |
| `+0x1C` | `u16` | Zero |
| `+0x1E` | `u16` | Field count |

Where a `PSIN` container stores eight `0xAA` bytes in that record, the resource stores a pointer to the structure's fields (ODRP-F03). That one substitution is what separates the two forms: the schema record is otherwise the same 32 bytes.

A field record is the same 16 bytes `PSIN` stores (ODRP-F04): `{u32 name, u32 offset, u32 type word, u32 auxiliary}`. The type word is a low-16 type code and a high-16 qualifier, the same split `PSIN` uses, and the observed codes are the `PSIN` vocabulary. Two widths differ, because a resource stores a pointer where a container stores a marker (ODRP-F10): a `0x42` text reference is 8 bytes and a `0x65` bit set is 8 bytes here.

An enumeration record is 24 bytes: `{u32 name, u32 signature, u64 system pointer to values, u32 count, u32 zero}`, followed by `count` records of `{u64 value, u32 name, u32 zero}` (ODRP-F05).

## Blocks and references

A block record is 16 bytes: `{u32 type word, u32 byte length, u64 pointer}`. The pointer names the segment and the offset of the block's bytes, so the block table addresses both segments (ODRP-F06).

A reference is a `u64` of `(byte offset << 20) | block`, the block counted from one, zero for null (ODRP-F07). Because the block names the segment, one reference word reaches either segment and no pointer value appears inside instance data. A decoder that reads the offset alone, or shifts by 16 rather than 20, misplaces every target.

The type word says what the block holds (ODRP-F14):

| Type word | Contents | Observations in `data.rpf` |
| --------- | -------- | -------------------------- |
| A structure's name hash | `length / size` whole records of that structure | 174 of 186 blocks in the largest resource |
| `0x10` | NUL-terminated text pool | 14,520 |
| `0x101` | One-byte boolean elements | 14,482 |
| `0x4A`, `0x14`, `0x16`, `0x33`, `7` | Hash, word and reference pools | 5 blocks in the largest resource |
| A field code with an established width | Elements of that type | 3 blocks in the largest resource |

A reference64 pool (`7`) is a list of references that no record field names; its entries still count as inbound when roots are derived.

Four blocks in the whole population are none of these (ODRP-F17). Their type words are `0x31` (768 bytes), `0x4D` (68 bytes), `0x4F` (248 bytes) and `0x5C` (8,272 bytes). Each has a reason: `0x31` has no established width, `0x4D`'s length is not a whole number of its 8-byte elements, `0x4F`'s qualifier is not one the width table establishes, and a `0x5C` element is a header with a reference rather than a scalar, so a block of them cannot be read as bare elements. The bytes are kept; nothing is guessed.

## Values

Container layouts are the ones `PSIN` stores, with one divergent pair (ODRP-F08):

| Code | Form | Layout |
| ---- | ---- | ------ |
| `0x52` | Array | `{u64 reference, u16 length, u16 capacity, u32 zero}` |
| `0x5C` | Array | `{u32 length, u32 capacity, u64 reference}` |
| `0x75` | Map | `{u32 length, u32 capacity, u64 reference}`; the two words are the number of bucket records and the number of entries they hold |
| `0x50` | Inline array | The elements themselves, inside the record |

A map's buckets and entries are records of a structure the schema defines: the bucket records carry the key hash and a reference to the entry records. Both are read as records of their structures, not as raw words.

A `0x42` field is an 8-byte reference into a `0x10` text block. The referenced string runs to the next NUL; the block as a whole is a run of NUL-terminated UTF-8 strings (ODRP-F09). 4,215,226 text values resolve across the population.

A `0x44` field is a 16-byte slot in the record itself. The observed bytes hold a length, a capacity and a reference-shaped word, but no string can be read from them at the offsets the container form uses, so the layout stays **Unknown** (ODRP-F16). The bytes are kept.

## Roots

The header names one root block, and the derivation from the decoded references — every structure block no reference reaches — agrees with it in 15,768 of 15,768 resources (ODRP-F13). The two readings are independent: one is a stored word, the other a walk of every reference, so the agreement is evidence that the word is a root block rather than a count.

That agreement also explains the word's small range. It is 2 in 14,485 resources, 1 in 1,247, 3 in 35 and 89 in one; those are block numbers, not document counts.

## Document family

Partial, at family level (ODRP-F19).

- The type 111 rows arrive with a native extension. The one opened by hand is a `zldbmt` file inside the nested archive `data.rpf!2`: 4 structures, 4 blocks, 19 records and 16 resolved text values, and every record holds one sentence as a `0x42` text reference — one label per record. The first row of that archive holds 23 records and 20 text values, and the second 410 records and 377 text values, so the archive is a label table of a few dozen to a few hundred sentences per resource.
- The type 11 row `data.rpf` 476 is 14,876,672 bytes with 182 structures, 38 enumerations, 186 blocks and 290,795 records, and no text values. It is an object graph whose blocks reference each other through single references; its structure names stay unknown hashes.

So the observed population is display text and the tables that organise it, not asset geometry, vehicles, weapons or textures. Nothing in the decoded values names a mesh, a texture or a model.

## Unknowns

- The object type byte `0x7A`, the `u16` at `+0x4E` and the pointer at `+0x40`.
- The layout of a `0x44` 16-byte slot.
- The four blocks of ODRP-F17.
- Every field's meaning. The decoder reports storage, not semantics.
- Whether a resource may carry a graphics-segment block: none was observed, because no resource had a graphics page.

## Reproduction

The walk was produced with the implementation's own decoder, which splits each payload from the row's page table and the page map and then reads the tables:

```text
cargo run -p lforge-rage9 --release --example odrp_population -- \
    "<GAME_ROOT>/data.rpf" --executable "<EXECUTABLE>" --recursive --types
lforge archive inspect "<GAME_ROOT>/data.rpf" --row 476 --metadata-output doc.json
lforge archive inspect "<GAME_ROOT>/data.rpf" --enter row:2 --row 0 --metadata-output doc.xml --metadata-xml
```

No tool in this repository decodes the form. The archive and resource conventions it builds on are in [RPF9](../../containers/rpf9/README.md) and [resources](../../resources/README.md).

## Limits

- One build and one local installation were examined.
- The graphics segment is untested against real data.
- Text and names are game content. Only counts, layouts and structure are recorded here.
- No executable code path was traced, so no claim rests on engine code.
