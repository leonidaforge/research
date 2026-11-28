# 0DRP evidence index

Resource observations from the local Scarlett build. No executable code path was traced and no tool from this repository decodes the form; the walk was produced by the implementation's own decoder, which was built from these observations and then checked against every reachable resource. Every finding is **Private-evidence supported**. Corrected interpretations are recorded in [research-history.md](research-history.md).

## Sample

| Property | Value |
| -------- | ----- |
| Scope | `<GAME_ROOT>/data.rpf`, walked recursively |
| Root archives | 1 |
| Nested archives entered | 41 |
| Entries walked | 23,075 |
| Resources carrying the tag | 15,768 |
| Decoded to full extent | 15,767 |
| Partial | 1 |
| Distinct payloads | 15,672 by SHA-256 of the reconstructed payload |
| Row types | 1,286 type 11, 14,482 type 111 |
| Archives that hold them | 16 nested archives, one holding 1,247 and the rest up to 1,114 each |

The walk is the whole population of one archive, not a selection. A resource is counted only when its resource head carries the tag and its payload could be read, split into its two segments from the page table and page map, and decoded.

## Evidence types

| Type | Meaning |
| ---- | ------- |
| `BINARY` | Bytes read from decoded RPF9 resource payloads, not traced in executable code |
| `CROSS_SAMPLE` | A property compared across distinct resources |
| `SYNTHETIC` | Fixtures that exercise a decoder, not native semantics |

## Findings

| ID | Claim | Evidence | Confidence | Limits |
| -- | ----- | -------- | ---------- | ------ |
| ODRP-F01 | A metadata resource carries ASCII `0DRP` at system `+0x10` and the byte `0x7A` at `+0x14`. All 15,768 resources of `data.rpf` carry both. `0x7A` is the only object type observed and its meaning is **Unknown** | `BINARY`, `CROSS_SAMPLE` | Confirmed (tag); Unknown (object type) | One build |
| ODRP-F02 | The header is a zero `u64`, a system pointer to the page map at `+0x08`, the tag at `+0x10`, the object type at `+0x14`, a zero `u64` at `+0x18`, the root block at `+0x20`, system pointers to the structure table at `+0x28`, the enumeration table at `+0x30` and the block table at `+0x38`, a fourth system pointer at `+0x40` whose target is not established, and four `u16` at `+0x48` holding the structure, enumeration and block counts then a word of unknown meaning observed as 0 in 14,919 resources, as 1 to 15 in most of the rest and as up to 1,077 in a handful | `BINARY`, `CROSS_SAMPLE` | Confirmed (layout); Unknown (`+0x40`, `+0x4E`) | One build |
| ODRP-F03 | A structure record is 32 bytes: `{u32 name, u32 signature, u32 flags, u32 zero, u64 system pointer to field records, u32 record size, u16 zero, u16 field count}`. The resource stores the pointer where a `PSIN` container stores eight `0xAA` bytes; every other field is the container's. The signature is a second hash beside the name and differs from it | `BINARY`, `CROSS_SAMPLE` | Confirmed | One build; no resource storing the `0xAA` form and a pointer form of the same schema was compared |
| ODRP-F04 | A field record is the same 16 bytes `PSIN` stores: `{u32 name, u32 offset, u32 type word, u32 auxiliary}`, and the type word is a low-16 code with a high-16 qualifier over the same code vocabulary: 85 distinct type words were observed, led by `0x4A` (29,327), `0x07` (28,966), `0x05` (17,224), `0x11` (14,722), `0x42` (14,544), `0x75` (14,483), `0x50` with qualifier 2 (14,482), `0x21` (9,298), `0x14` (2,786) and `0x60` (451) | `BINARY`, `CROSS_SAMPLE` | Confirmed (layout); Confirmed for the listed codes | Field semantics Unknown |
| ODRP-F05 | An enumeration record is 24 bytes: `{u32 name, u32 signature, u64 system pointer to values, u32 count, u32 zero}`, followed by `count` records of `{u64 value, u32 name, u32 zero}`. 1,310 resources carry 2,780 values in total and the rest carry none | `BINARY`, `CROSS_SAMPLE` | Confirmed | One build |
| ODRP-F06 | A block record is 16 bytes: `{u32 type word, u32 byte length, u64 pointer}`. The pointer names the segment and the offset, so the table addresses blocks in either segment without a rule of its own | `BINARY`, `CROSS_SAMPLE` | Confirmed | No observed resource placed a block in a graphics segment |
| ODRP-F07 | A reference is `(byte offset << 20) | block`, the block counted from one, zero for null. The offset is the byte offset, not an element index, and the shift is 20, not 16. The block names the segment, so no pointer value appears inside instance data | `BINARY`, `CROSS_SAMPLE` | Confirmed | Verified by resolving every reference of the population: 0 of 15,768 resources leaves a reference unbound |
| ODRP-F08 | `0x52` arrays store `{u64 reference, u16 length, u16 capacity, u32 zero}`, as the container form does. `0x5C` arrays and `0x75` maps store `{u32 length, u32 capacity, u64 reference}` — the order is reversed and the words are wider. A map's two words are its bucket-record count and its entry count, and both are read as records of their structures | `BINARY`, `CROSS_SAMPLE` | Confirmed (layouts); Probable (bucket and entry roles) | One build |
| ODRP-F09 | A `0x42` field is an 8-byte reference into a `0x10` block whose bytes are NUL-terminated UTF-8 strings. The population resolves 4,215,226 such values and none fails to bind | `BINARY`, `CROSS_SAMPLE` | Confirmed | Text is game content and is not recorded |
| ODRP-F10 | Two type widths differ from the container form because a resource stores a pointer where a container stores a marker: a `0x42` text reference is 8 bytes and a `0x65` bit set is 8 bytes. Other codes keep their container width, `0x5C`, `0x75`, `0x50` and `0x52` being 16 bytes for that reason | `BINARY`, `CROSS_SAMPLE` | Confirmed (widths) | Widths are established from the tables, not from a traced reader |
| ODRP-F11 | The recursive walk of `data.rpf` reaches every resource carrying the tag: 15,768 discovered, opened, split and decoded, of which 15,767 reach `decoded` and one is partial. There are 15,672 distinct payloads, sizes 848 to 14,876,672 bytes, 2 to 182 structures, 2 to 186 blocks, 3 to 192,488 records and 4,215,226 resolved text values, and no limit refusal and no unbound reference | `BINARY`, `CROSS_SAMPLE` | Confirmed | One archive, one build |
| ODRP-F12 | Every observed resource has one or two system pages and no graphics page: 15,609 with one system page and 159 with two. The graphics segment therefore holds no observed block | `BINARY`, `CROSS_SAMPLE` | Confirmed (sample) | The graphics path is unexercised by real data |
| ODRP-F13 | The `u32` at `+0x20` is the block the header names as the root, counted from one. Deriving the roots independently — every structure block no decoded reference reaches — yields exactly that block in 15,768 of 15,768 resources. Observed values are 2 (14,485 resources), 1 (1,247), 3 (35) and 89 (1), which are block numbers rather than document counts: an earlier reading as a count of roots is rejected | `BINARY`, `CROSS_SAMPLE` | Confirmed | One build; whether a resource may name several roots is Unknown |
| ODRP-F14 | A block's type word is one of three things. The name hash of one structure, in which case the block is `length / size` whole records of it. A pool code of the container vocabulary (`0x10` text, 14,520 blocks; `0x4A` hash, `0x14` word32, `0x16` word64, `0x33` word128, `7` reference64). Or a field code with an established width, read as a pool of that type. 194 distinct type words were observed, 182 of them once, which is the count of distinct structures those resources define | `BINARY`, `CROSS_SAMPLE` | Confirmed for structure and pool blocks | A type word that is none of the three keeps its bytes |
| ODRP-F15 | The type word `0x101` is a one-byte element block in 14,482 resources, the same count as the type 111 rows those resources come from, so the type 111 form stores its per-record bytes as a separate block of that type | `BINARY`, `CROSS_SAMPLE` | Probable | No reader was traced; the reading rests on the width table and on element values that are all 0 or 1 |
| ODRP-F16 | A `0x44` field is 16 bytes inside the record. The observed bytes hold a length, a capacity and a reference-shaped word, but no string reads at the offsets the container form uses, so the layout stays **Unknown** and the bytes are kept | `BINARY` | Unknown | No rule established |
| ODRP-F17 | Four blocks in the whole population cannot be read as records, pool elements or typed elements, all in `data.rpf` row 476: `0x31` (768 bytes, no established width), `0x4D` (68 bytes, not a whole number of 8-byte elements), `0x4F` (248 bytes, a qualifier the width table does not establish) and `0x5C` (8,272 bytes, whose elements are headers with a reference rather than scalars). They make that resource the one partial document | `BINARY` | Confirmed | One resource |
| ODRP-F18 | The earlier census count of 1,286 resources of this form is the type 11 subset: it classified rows from their head in the archives on disk. A recursive walk that counts every row carrying the tag finds 15,768, of which 14,482 are type 111 rows inside nested archives. Both counts describe different populations and neither contradicts the other | `BINARY`, `CROSS_SAMPLE` | Confirmed | The recursive walk enters nested archives; the census did not |
| ODRP-F19 | The observed documents are display text and the tables that organise it. The `zldbmt` resource opened by hand holds 19 records in 4 blocks with 16 text values, one sentence per record; the first two rows of its archive hold 23 records with 20 text values and 410 records with 377. The type 11 row 476 holds 182 structures, 38 enumerations, 186 blocks and 290,795 records with no text value, an object graph of single references | `BINARY`, `CROSS_SAMPLE` | Confirmed (family level) | Field semantics Unknown; names and text are game content |
| ODRP-F20 | Enumerations are rare beside structures: 1,310 of 15,768 resources declare any, with 2,780 values in total, and the largest single resource declares 38 | `BINARY`, `CROSS_SAMPLE` | Confirmed | One build |

## Reproduction

The walk ran through the implementation's decoder, which splits each payload from the row's page table and page map and then reads the tables. `<GAME_ROOT>` is a local installation and `<EXECUTABLE>` the game executable that matches the archive.

```text
cargo run -p lforge-rage9 --release --example odrp_population -- \
    "<GAME_ROOT>/data.rpf" --executable "<EXECUTABLE>" --recursive --types
lforge archive inspect "<GAME_ROOT>/data.rpf" --row 476 --metadata-output doc.json
lforge archive inspect "<GAME_ROOT>/data.rpf" --enter row:2 --row 0 --metadata-output doc.xml --metadata-xml
```

The harness records one JSON line per resource with the counts and the decoder's notes, and writes no payload bytes. The desktop Metadata Viewer was used to confirm that a real resource renders, on `data.rpf` row 476 and on the `zldbmt` resource of the nested archive `data.rpf!2`.

## Limits

- One build and one local installation were examined.
- No executable code path was traced. The document purpose, the object type byte and every field's meaning are Unknown.
- The graphics segment holds no observed block, so nothing here is established about it.
- Text, names and hashes are game content and are not recorded.
- The readings rest on a decoder built from these observations. A reading that is wrong in a way that still yields whole records and bound references would not be caught by the walk; the count of 0 unbound references is evidence of self-consistency, not of semantics.
