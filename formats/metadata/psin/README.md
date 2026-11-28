# PSIN, `LSCH` family (decoded metadata)

A GTA VI `.zmt` row holds a `PSIN` container whose first section is `LSCH`. Inside it is a complete, self-describing document: a schema of structures and fields, optional enumerations, an instance block table, and a copy of the metadata resource header. This document records what was established by decoding those containers from a local game installation.

The framing — the section walk, the `LSCH` descriptor table, the `PMAP` family and the `CHKS` checksum — is documented separately in [unknown/psin](../../unknown/psin/README.md). Findings there keep their `PSIN-F` numbers; the findings here use `PSIN-D` numbers.

Numbers as of 2026-11-28. Confidence is **confirmed**, **inferred** or **unknown**, in the sense the rest of this repository uses.

## Status

| Part | Status |
| ---- | ------ |
| `.zmt` rows hold `PSIN` containers | Confirmed on the 865 decoded rows of 9,365 reachable (PSIN-D01) |
| Instance block table | Confirmed (775 containers, PSIN-D03) |
| Structure and field tables | Confirmed (PSIN-D04, PSIN-D05) |
| Enumeration table | Confirmed on 431 containers (PSIN-D06) |
| Copied resource header and its counts | Confirmed (775 containers, PSIN-D07) |
| References | Confirmed (PSIN-D08) |
| Arrays and maps | Confirmed (PSIN-D09, PSIN-D10) |
| Field and structure name hashing | Confirmed (PSIN-D12) |
| Type codes and their widths | Inferred from an external specification, corroborated by decoding (PSIN-D11) |
| Field semantics | Unknown |
| Every structure block decodable | **No**: 116 blocks in 89 containers hold no structure the schema defines |
| `PMAP` family decoded | **No**: 62 containers stop at the framing |
| The 8,500 rows inside nested archives | **No**: reachable, not decoded |

## Population

A search of `<GAME_ROOT>` for readable `.zmt` rows found **865** rows in **10** archives: 657 in `data.rpf`, 113 in `packs.rpf`, 30 in `anim.rpf`, 28 in `levels.rpf`, 25 in `story000.rpf`, 7 in `core_restofworld.rpf`, 2 in `shared_minigame000.rpf` and one each in `navmeshes.rpf`, `story000_restofworld.rpf` and `textures.rpf`. The four archives named without a parent are nested under `pack/`; the search reports only their leaf name. Every row is RPF9 type 11.

Those 865 rows are only the `.zmt` rows of archives that are files on disk. Most archives in this installation are stored **inside** `data.rpf` and `packs.rpf`, and the search as it stood did not enter them, so it never saw their rows. Entering the archive a row holds (the search's `--recursive`, the census's walk) raises the count fourfold:

| Root | Rows at the searched file | Rows after entering the archives it holds | Archives opened |
| ---- | ------------------------: | ----------------------------------------: | --------------: |
| `data.rpf` | 657 | 5,321 | 42 |
| `packs.rpf` | 113 | 2,268 | 60 |
| `navmeshes.rpf` | 1 | 1,210 | 29 |
| `story000.rpf` | 25 | 184 | 64 or more |
| `levels.rpf` | 28 | 239 | 64 or more |
| `shared_minigame000.rpf` | 2 | 74 | 50 |
| `anim.rpf` | 30 | 30 | 64 or more |
| `story000_restofworld.rpf` | 1 | 29 | 19 |
| `core_restofworld.rpf` | 7 | 9 | 11 |
| `textures.rpf` | 1 | 1 | 21 |

The `64 or more` rows are roots where the walk stopped at a 64-archive budget, so their counts are floors. No nested archive needed temporary storage: every one was stored byte-for-byte in its row and could be read where it lies.

**9,365 `.zmt` rows are reachable** across these ten roots and the archives inside them, against 865 without entering an archive, and the figure is a floor.

Sizes of the 865 rows decoded here range from 215 to 17,406,784 bytes.

| Outcome | Rows |
| ------- | ---: |
| Decoded completely | 686 |
| Decoded partially: at least one block is not a structure the schema defines | 89 |
| Not decoded: the `PMAP` family | 62 |
| Not a `PSIN` container: `RBF0` payload | 27 |
| Not a `PSIN` container: the metadata resource form (`0DRP`) | 1 |

The 775 decoded containers hold 3,929,948 records between them. Every one of the 775 has a verified `CHKS` checksum and a copied resource header whose structure, enum and block counts equal the tables that were read (PSIN-D07).

### What the rest of the reachable population is

A recursive classification census of `data.rpf` — `archive census data.rpf --recursive --entries`, classifying each entry from a bounded decoded head and deserializing nothing — opened 42 archives and probed all 23,075 entries. It finished complete, with no failed archive and nothing stopped by a limit. **5,321** of those entries are RPF9 type 11, spread over 31 of the 42 archives:

| Recognised form | Entries |
| --------------- | ------: |
| `PSIN` signature | 2,573 |
| `RBF0` payload | 1,462 |
| `0DRP` resource form | 1,286 |

The census cannot tell the two `PSIN` families apart, because both carry the same magic. A sample of 129 of the 2,573 rows, every twentieth in census order, extracted each payload and read the first section tag: **126 are `LSCH` and 3 are `PMAP`**. That is a sample, not a count; the 3:126 ratio is consistent with the 62 `PMAP` rows of the 837 `PSIN` rows in the decoded population.

None of the 5,321 is text. The `0DRP` form is far more common inside nested archives than at the top level, where only one row of 865 is one.


## Container

Seven sections tile the payload exactly, the first of them being the `PSIN` section itself:

| Section | Contents |
| ------- | -------- |
| `PSIN` | the instance block table and the blocks |
| `LSCH` | the structure and field tables |
| `LENM` | the enumeration table; empty in 344 of 775 containers |
| `LSNS` | not decoded; empty in the studied `.zmt` population |
| `LGID` | not decoded; empty in the studied `.zmt` population |
| `LRSC` | a copy of the metadata resource header |
| `CHKS` | the integrity section |

The big-endian length at `+0x04` is the length of the `PSIN` section. A section with no body is eight bytes: the tag and the length.

## Instance block table

The table follows the `LSCH` descriptor relation: each entry is a little-endian `(type, byte length)` pair followed by eight `0xAA` bytes, the entries begin at `+0x08`, and eight `0x70` bytes end the table. Blocks follow in table order, each beginning on a 16-byte boundary and padded to one with zeros.

| Property | Observation |
| -------- | ----------- |
| First block | `0x10 + 16 × entries` |
| Entry | `u32` type word, `u32` byte length, 8 × `0xAA` |
| Terminator | 8 × `0x70` |
| Block alignment | 16 bytes; padding is zero in every accepted container |
| Block count | 1 to 1,093 |

A block's type word decides what it holds:

- If the type equals exactly one structure's name, the block holds that structure's records, each `size` bytes, and the block length must be a whole multiple of `size`.
- Otherwise the block is a value pool, keyed by one of the pool type words below.

A container may name more than one structure with the same name; a block whose type names several is then reported as unsupported rather than guessed at. No container in the studied population does this.

## Schema

All structure records come first, then every field record, in structure order.

| Record | Layout |
| ------ | ------ |
| structure, 32 bytes | `u32` name hash, `u32` signature, `u32` flags, `u32` zero, 8 × `0xAA`, `u32` record size, `u16` zero, `u16` field count |
| field, 16 bytes | `u32` name hash, `u32` byte offset, `u32` type word, `u32` auxiliary word |

The eight `0xAA` bytes stand where the resource form of the same metadata stores a pointer to the structure's member list, so the layout is the one the resource form uses with the pointer replaced by a marker.

The flags word is `0x200`, `0x300` or `0x400` in the studied population. The low byte is `0x0C` or `0x24` on the generated helper structures, which are numbered from `0x100` instead of hashed (PSIN-D13).

A field whose name hash is `0x100` is an element descriptor: it describes an array's element, or a map's key or value, and occupies no storage of its own. Its offset is zero whether or not the owning structure stores anything at zero.

## Type word

The low 16 bits are the type code; the high 16 bits qualify it and, for arrays, hold an index into the owning structure's field list. The auxiliary word holds an embedded structure's name, an enumeration's hash, or a map's key and value descriptor indices.

| Code | Meaning | Width | Confidence |
| ---- | ------- | ----- | ---------- |
| `0x01` | Boolean | 1 | Inferred |
| `0x05` | embedded structure | the structure's size | Confirmed |
| `0x07` | reference | 8 | Confirmed |
| `0x08` | `u64` | 8 | Inferred |
| `0x10` / `0x11` / `0x12` / `0x13` | `i8` / `u8` / `i16` / `u16` | 1 / 1 / 2 / 2 | Inferred |
| `0x15` / `0x16` | `u32` / `i32` | 4 | Inferred |
| `0x20` / `0x21` | `f16` / `f32` | 2 / 4 | Inferred |
| `0x32` / `0x33` / `0x34` | 3 or 4 `f32` components | 12 / 16 / 16 | Inferred |
| `0x44` | text slot | 16 | Unknown layout |
| `0x4a` | 32-bit hash | 4 | Confirmed |
| `0x4d` | 64-bit hash | 8 | Inferred |
| `0x4f` | identifier, qualifier 5 | 8 | Inferred |
| `0x50` | inline array: `auxiliary` elements of the descriptor | count × element | Inferred |
| `0x52` / `0x5c` | array | 16 | Confirmed |
| `0x60` / `0x62` | enumeration value | 1 / 4 | Inferred |
| `0x65` | bit set | 16 | Inferred |
| `0x71` / `0x75` | map | 24 / 16 | Confirmed |

The width of a field is also available from the schema itself: the next named field's offset, or the structure's size for the last field. That extent is reported for every field, so a field whose type is not in the table still has a known byte range.

Type codes not in this table are not read. Their bytes are kept and the field is reported as unresolved.

## Enumerations

| Record | Layout |
| ------ | ------ |
| enumeration, 24 bytes | `u32` name hash, `u32` signature, 8 × `0xEE`, `u32` value count, `u32` zero |
| value, 16 bytes | `u64` value, `u32` name hash, `u32` zero |

The `0xEE` marker stands where the resource form stores the pointer to the value list. A 32-bit enum field matches a value whose low 32 bits are equal, so a value stored as a sign-extended 32-bit negative number matches too. Signedness itself is not established.

## Copied resource header

The `LRSC` body starts with `0DRP` and the object type byte `0x7A`. In this container the interesting words are:

| Offset | Type | Observation |
| ------ | ---- | ----------- |
| `+0x04` | `u8` | object type; `0x7A` in 775 of 775 |
| `+0x10` | `u32` little-endian | number of root objects |
| `+0x38` | `u16` little-endian | structure count |
| `+0x3A` | `u16` little-endian | enumeration count |
| `+0x3C` | `u16` little-endian | block count |

The three counts equal the tables that were read in 775 of 775 containers. That agreement is the strongest single validation of the decode: the section walk, the block table and the schema table are three independent reads of the same container, and a misread of any of them would break the equality.

The root-object count does not equal the number of structures nothing embeds, and no rule connecting the two is established.

## References

A reference is a `u64`:

```
word = (byte offset within the block << 20) | block
```

The block is counted from one; zero is the null reference. The offset must be a whole multiple of the target structure's size and the record it names must lie inside the block. Over the 775 decoded containers, every nonzero reference either satisfies that or names a block whose type is a value pool; a reference that satisfies neither is reported with the reason and not followed.

No pointer above `0x5FF…` occurs: `0x5xxxxxxx` and `0x6xxxxxxx` values are not resource pointers here, because the low 20 bits are a block number.

## Arrays and maps

| Form | Header |
| ---- | ------ |
| array `0x52` | `u64` reference, `u16` length, `u16` capacity, `u32` zero |
| array `0x5c` | `u16` length, `u16` capacity, `u64` reference, `u32` zero |
| map `0x71` | `u64` one, `u64` reference, `u16` length, `u16` capacity, `u32` zero |
| map `0x75` | `u16` length, `u16` capacity, `u64` reference, `u32` zero |

In every observed header the length and capacity words are equal and the trailing word is zero. The reference names the block that holds the elements, and the element descriptor's index in the owning structure's field list is the type word's qualifier for an array and the low and high halves of the auxiliary word for a map.

An array's element descriptor may name:

- a structure: the block holds that structure's records, and each element is a whole record;
- a reference: the block is a reference pool and the array selects 8-byte words;
- a 32-bit hash: the block is a hash pool and the array selects 4-byte words;
- an enumeration: the block is a 32-bit value pool.

A map's reference names a block of entry structures; each entry is a record of that structure, and its fields are the stored key and value.

## Value pools

| Type word | Contents | Width |
| --------- | -------- | ----- |
| `0x10` | NUL-terminated printable ASCII | variable |
| `0x4a` | 32-bit hashes | 4 |
| `0x07` | 64-bit reference words, not followed | 8 |
| `0x14` | 32-bit words of no established meaning | 4 |
| `0x16` | 64-bit words of no established meaning | 8 |
| `0x33` | 16-byte words of no established meaning | 16 |

A text pool's bytes must be printable ASCII with NUL separators and a final NUL; otherwise the block is reported as unsupported rather than split on a guess.

## Names

Structure and field names are the **case-sensitive** Jenkins one-at-a-time hash of the name as written. This is not the archive path hash, which folds case.

```python
def metadata_hash(name):
    h = 0
    for c in name.encode():
        h = (h + c) & 0xffffffff
        h = (h + (h << 10)) & 0xffffffff
        h ^= h >> 6
    h = (h + (h << 3)) & 0xffffffff
    h ^= h >> 11
    return (h + (h << 15)) & 0xffffffff

assert metadata_hash("Key") == 0x6098a50e
assert metadata_hash("Item") == 0x063fa3f2
assert metadata_hash("Position") == 0x0c928991
assert metadata_hash("Flags") == 0x4b621302
assert metadata_hash("CMloRoomDef") == 0x0b1811f1
assert metadata_hash("Position") != metadata_hash("position")
```

`Key` and `Item` are the two fields of the map entry structure in the studied `.zmt` population (PSIN-D13); the other three come from the map-format and vehicle specifications and are reproduced here only to show that the algorithm is the same one. A stored hash stays the identity: a name that reproduces it is an addition, and a hash with no name stays unresolved.

The map entry check is independent: the five entry records of `data/effects/focusmodetrailinfo` carry the field hashes `0x6098A50E` and `0x063FA3F2`, a name table holding `Key` and `Item` resolves exactly those two and nothing else, and the references in the `Item` fields bind to whole records of the block the map names. Both the hash and the map entry layout therefore agree with the map-format specification, which was derived without these payloads.

No other structure or field hash in the studied population was resolved by the built-in name tables. The names of most structures and fields are therefore still unknown, and the field semantics that would follow from them are unknown too.

## The blocks no structure defines

89 of the 775 decoded containers hold a block whose type names neither a structure nor one of the six pool types above: 116 blocks in all. Their type words are not arbitrary. Every one of them is a code the schema also uses as a field type:

| Block type word | Field meaning elsewhere in the schema | Blocks |
| --------------- | ------------------------------------- | -----: |
| `0x4f` | identifier, 8 bytes | 23 |
| `0x08` | `u64`, 8 bytes | 21 |
| `0x4d` | 64-bit hash, 8 bytes | 18 |
| `0x21` | `f32`, 4 bytes | 12 |
| `0x34` | four `f32`, 16 bytes | 12 |
| `0x15` | `u32`, 4 bytes | 8 |
| `0x31` | three `f32`, 12 bytes | 7 |
| `0x44` | text slot, 16 bytes | 3 |
| `0x11` | `u8`, 1 byte | 3 |
| `0x42` | not in the type table | 2 |
| `0x13` | `u16`, 2 bytes | 1 |
| `0x5c` | array, 16 bytes | 1 |
| `0x01`, `0x17`, `0x30`, `0x32`, `0x52` | various | 1 each |

That a pool is typed by a schema field code is a **candidate** reading, not a confirmed rule: the block length is a whole multiple of that code's field width for ten of the thirteen codes, but not for every one. `0x4d` blocks are 500, 36, 132 and 472 bytes long, none divisible by the 8-byte field width, and every one of them is divisible by 4; `0x31` blocks are 112 and 448 bytes, divisible by 4 but not by the 12-byte field width. A block type therefore does not always carry the field width of the same-numbered field type.

The check that would settle it has not been run: an array field whose element descriptor is one of these codes names the block and carries the element count in its own header, so a block of length `L` reached by an array of `n` elements implies a width of `L / n`. If two independent arrays agree on one width for one code, the rule is established for that code. Until then the 116 blocks keep their bytes and stay reported as unsupported.

## What counts as a decoded container

A container is decoded only when all of the following hold. A container whose outer RPF row inflated is not thereby decoded.

1. The sections tile the payload and end at its last byte.
2. The block table satisfies the descriptor relation, and the blocks end at the `PSIN` section's length.
3. The `CHKS` checksum verifies.
4. The structure and field tables cover the `LSCH` body exactly.
5. The copied resource header's three counts equal the tables that were read.
6. Every block is either a whole number of records of one structure the schema defines, or a recognised value pool.

Partial means 1 to 5 hold but some block is neither. Unsupported means the container belongs to a family this document does not describe.

## Unsupported containers

| Variant | Rows | Evidence |
| ------- | ---: | -------- |
| `PMAP` family | 62 | the first section tag is `PMAP`; the pre-section area is a block directory, not a descriptor table |
| `RBF0` payload | 27 | the payload starts with `RBF0`, not `PSIN` |
| metadata resource form | 1 | `0DRP` and object type `0x7A` at `+0x10`, no `PSIN` magic |

The `PMAP` family is the older GTA V layout: sections `PMAP`, `PSCH`, `PSIG`, optionally `STDN` or `STFN`, then `STNS` and `CHKS`, with the block directory inside `PMAP`. Its instance data is not decoded here.

The metadata resource form carries the same self-describing tables in a resource rather than a `PSIN` container. Its own layout is not decoded here.

## Reproduction

```text
archive search <GAME_ROOT> --extension zmt --limit 100000 --json
archive search <ARCHIVE> --recursive --extension zmt --limit 100000 --json
archive inspect <ARCHIVE> --row <ROW> --json --sample 1
archive inspect <ARCHIVE> --row <ROW> --blocks --metadata-output <FILE> --json
archive inspect <ARCHIVE> --row <ROW> --metadata-output <FILE> --metadata-xml --json
```

The first search yields the 865 rows of the archives that are files on disk. The second yields, for one archive, the rows of the archives stored inside it as well; `--max-archives` bounds how many archives one search opens. The third command reports, per row, whether the container decoded and what its counts are; the last two write the decoded document as JSON or XML. Four archives are nested under `pack/` and must be named by their full path, and a row inside a nested archive is selected with `--enter row:<ROW>`.

No game bytes, table dumps or extracted payloads are stored in this repository.

## Limits

- One build (`scarlett-e95020b2`) and one local installation were examined.
- The findings are confirmed on the 865 rows that were decoded. The other 4,664 rows reachable inside `data.rpf` are the same RPF9 type and one of the same three recognised forms, but they were classified from a head and not decoded: no count below covers them, and only the `LSCH` share of them is likely to have a schema at all.
- The search enters a nested archive only when the row's type declares the archive type. A row whose type is undeclared but whose payload is an archive is not entered, so the 9,365 figure is a floor for a second reason.
- The block-table, schema and header findings are confirmed on the containers that decoded. The 62 `PMAP` containers are outside everything here except their section tags.
- The type codes are adopted from a community specification and corroborated only in the weak sense that the values they produce are coherent (floats that look like positions and colours, references that bind to whole records, arrays whose lengths match their blocks). They are not derived from game code.
- 116 blocks in 89 containers hold a type the schema does not define. Their bytes are kept but not interpreted. Their type words are codes the schema uses for fields, and the candidate reading that such a block is a pool of that scalar type is recorded above.
- No field meaning is established, so no structure is assigned a purpose.
- The `.zmt` rows in this installation hold gameplay, effect, AI, container, UI and level metadata. Nothing in the population was established to be a vehicle, ped or weapon definition; see the note on vehicle names below.

## Open questions

- What do the 116 blocks whose type no structure defines hold? Their type words are field type codes, but the element width does not follow the field width for every code; an array's element count against the block length would decide it.
- What is the `PMAP` family's instance layout?
- What does the structure signature word protect or identify?
- What do the `0x14`, `0x16` and `0x33` pools hold?
- Which fields are pointers into other resources, and how are those resources named?
- Does the `LRSC` root count have a structural rule?

## Note: vehicle names in `data/ai/vehiclelayoutsets`

`data/ai/vehiclelayoutsets` (1,497,144 bytes, 14 structures, 10 blocks) holds a 3,431-element `0x4a` hash pool. Nine distinct values in the decoded document equal the case-sensitive hash of a curated GTA VI vehicle model name, including `manana` (36 occurrences) and `caddy` (8). The values sit in 32-bit hash arrays whose owning field and element descriptor are not named, and the structures' names do not resolve, so **no vehicle-to-record mapping is established**. It is recorded as a lead, not a finding.
