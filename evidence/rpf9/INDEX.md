# RPF9 evidence index

Executable findings refer to build [scarlett-e95020b2](../../builds/gta-vi/scarlett-e95020b2/README.md), SHA-256 `e95020b2fa4a721db3df59fdecf75621730ac559d8835252f6c3b658d5a08993`, image base `0x140000000`. Function roles are listed in the [function catalog](../../builds/gta-vi/scarlett-e95020b2/functions.md).

## Evidence types

| Type | Meaning |
|---|---|
| Disassembly | Instruction-level reading of the function at the given RVA, including its call sites |
| Decompilation | Decompiled control flow and data access of the function at the given RVA, checked against its callers |
| Header data | Layout arithmetic checked against the plain header fields of real archives. Offsets and sizes only, no decoded values |
| Payload data | Structure observed in archive payload bytes. Not traced in game code |
| Executable data | Pointers or table slots read from the executable image at the given RVA |
| Byte search | Every occurrence of a constant in `.text`, mapped to its containing function |

Where a decompilation produced a recorded evidence ID, the first 8 hex digits are given. The ID identifies an unpublished analysis record. It shows provenance only. The RVA and the evidence type are what allow independent checking.

## Findings

| ID | Claim | Evidence | RVA | Evidence ID | Confidence | Limits |
|---|---|---|---|---|---|---|
| RPF9-F01 | The engine recognizes RPF9 by comparing the first `u32` with `0x52504639` | Disassembly, decompilation | `0x1FB2692`, `0x1FB2619`, `0xFC21D9` | | Confirmed | |
| RPF9-F02 | The header reader reads exactly 16 bytes, then `hdr[0x04]` bytes (mode 0) or `hdr[0x08]` bytes (mode 1) from the archive base. Mode 1 reads `hdr[0x04] - hdr[0x08]` more bytes from `base + hdr[0x08]` into a second buffer | Disassembly, decompilation | `0x1FB2600` | | Confirmed | Mode origin per caller not traced |
| RPF9-F03 | `hdr[0x0C]` is not read on any traced path. Its value can exceed `hdr[0x04]` | Disassembly, decompilation, header data | | | Unknown | |
| RPF9-F04 | Bytes `0x10..0x3F` are read directly as counts and flags. They are not transformed before use | Disassembly | `0x87AF70`, `0x87AFF0` | | Confirmed | Fields at `0x10`, `0x18`, `0x28`, `0x2F`, `0x34..0x3F` unexplained |
| RPF9-F05 | Region order and sizes of the primary area: header, `A*8`, `B`, `C*24`, `(C-D)*E*F`, pool up to `hdr[0x08]`. Offsets are rounded up, to 16 bytes when bit 0 of `u8@0x2D` is set, else 4 or 8 | Disassembly, decompilation, header data | `0x87AFF0` | `ev_9a67127a` | Confirmed | Rounding per region not recorded. In observed archives the index store is 8-byte aligned and the pool 16-byte aligned |
| RPF9-F06 | The secondary area holds `D*E*F` bytes of cells followed by a pool up to `hdr[0x04]` | Disassembly, decompilation | `0x87B0F0` | | Confirmed | Secondary pool alignment not recorded |
| RPF9-F07 | The archive constructor runs header read, view descriptor, validation, then writes region pointers into the metadata view. A failed read or validation abandons the archive | Disassembly, decompilation | `0xFC2540`, `0x87AEC0` | `ev_d192a75d` | Confirmed | |
| RPF9-F08 | `C` 24-byte records are column descriptors. The key search compares the `u64` at `+0x00` with a field key and returns a column index or `0xFFFF` | Decompilation | `0x28CD240` | | Confirmed | |
| RPF9-F09 | Descriptor `+0x0C` is a `u32` column base offset into the pool. `+0x10` is a `u16` element width | Decompilation | `0x55B2600` | `ev_f8713c59` | Confirmed | `+0x08` and `+0x12` unknown |
| RPF9-F10 | Columns `[0, C-D)` use the primary cell store with stride `C-D`. Columns `[C-D, C)` use the secondary store with stride `D`, rebased by `C-D` | Decompilation | `0x4DB65B0` | | Confirmed | |
| RPF9-F11 | Cell index `row * stride + column`. `F` gives the cell width: 1 (null `0xFF`), 2 (null `0xFFFF`), 4 (no null). A null returns `0xFFFFFFFF` | Decompilation | `0x4DB6600` | `ev_a6a8ab58` | Confirmed | `F = 4` handled in code, not observed in archives |
| RPF9-F12 | Value pointer `poolBase + columnBaseOffset + elementWidth * cellIndex`, with the primary or secondary pool by column range | Decompilation | `0x55B2600` | `ev_f8713c59` | Confirmed | Value types and signedness unknown |
| RPF9-F13 | `E = u32@0x24` is the row count. Path open iterates all `E` rows | Decompilation | `0x28CD5B0` | | Confirmed | |
| RPF9-F14 | Field getters add `0x28` to the archive object and keep only the low 16 bits of the entry ID before the schema accessor runs | Disassembly, decompilation | `0x28CE0A0`, `0x28CE0B0` | | Confirmed | |
| RPF9-F15 | Entry ID = `(tag << 16) \| row`. The tag is the `u16` at file object `+0x0C` | Disassembly, decompilation | `0x5305EC0` | `ev_309e1fb7` | Confirmed (read), Probable (one tag per mounted archive) | Assignment of the tag not traced |
| RPF9-F16 | Logical size: R `(u32@+4 & 0xFFFFFFF0) + (u32@+0 & 0x7FFFFFF0)`, F `u64@+0x10 & 0xFFFFFFFFFFF`, A `u64@+0x08 & 0xFFFFFFFFFFFF`, tested in the order R, F, A | Decompilation | `0x1331670` | `ev_3274f61a` | Confirmed (arithmetic), Probable (R words as page sizes) | Meaning of the two R words and their masked bits not established |
| RPF9-F17 | Field keys observed at use sites. Meanings per key in [schema.md](../../formats/containers/rpf9/schema.md#known-columns) and the findings named there | Decompilation, byte search | `0x1331670`, `0x28CDA50`, `0x314330`, `0x5520AC0` | | Per key | Key hash algorithm unknown |
| RPF9-F18 | Names are resolved by `(namespace, u64 hash)` lookup in a runtime dictionary, which returns a string or null | Decompilation | `0x553D070` | | Confirmed | Hash algorithm and namespace values unknown |
| RPF9-F19 | Extensions come from a numeric type ID. `0xFF` means no extension. Unknown IDs give a default string | Decompilation | `0x4EBBC30` | | Confirmed | Type ID table not decoded |
| RPF9-F20 | Path open takes the path after the first `/`, rebuilds name plus extension for every row, and matches with a substring search | Decompilation | `0x28CD5B0` | `ev_ec1bb128` | Confirmed | Choice among several matches not established |
| RPF9-F21 | Child enumeration writes one 0x20-byte descriptor per entry ID: `+0x00` 16 bytes read at the payload offset or copied from key `0xC26722D233648AE7`, `+0x10` stored size, `+0x18` the `u64` at file object `+0x30`. Batch open iterates an ID array | Decompilation | `0x28CDA50`, `0x28C6B20` | `ev_bc48c80a` | Confirmed (fields), Probable (16 bytes are the payload start) | Meaning of file object `+0x30` unknown |
| RPF9-F22 | Superseded by RPF9-F34 and RPF9-F37. `0x28CD3B0` is a seek, not a read | | | | | |
| RPF9-F23 | Cryptographic processing runs inside the validation chain after the metadata read. Failure rejects the archive | Disassembly | `0x8EC200` | | Confirmed | |
| RPF9-F24 | `u8@0x2E` selects processing: 0 none, bit 0 span set, `value >> 1` descriptor index with a default fallback | Disassembly | `0xA348A0`, `0xA349A0` | | Confirmed | |
| RPF9-F25 | A descriptor holds a 32-bit key identifier, a `u16` cipher type and a 16-byte parameter. The type maps to an algorithm through a 19-entry table. The key is looked up by identifier at runtime | Disassembly | `0x536A70`, `0x613880` | | Confirmed (structure) | Algorithm and key lookup not analyzed |
| RPF9-F26 | Processed spans: the `A` table and the `B` block minus its last `u32@0x30` bytes, plus a separate pass over the secondary area | Disassembly | `0xA348A0`, `0x8EC360` | | Confirmed | Span set for bit 0 clear not described |
| RPF9-F27 | The span runner calls `update` with identical input and output pointers, then a `final` that returns bool. This fits authenticated in-place decryption with a 16-byte tag | Disassembly | `0x6BD160` | | Probable | Verify-only use not excluded |
| RPF9-F28 | Lookups read the view built after validation. Whether the descriptors, primary cells and primary pool are transformed on disk is not established | Disassembly, decompilation | `0xFC2540` | | Confirmed (order), Unknown (storage state) | See [cryptography](../../cryptography/rpf9/README.md#open-questions) |
| RPF9-F29 | Payload storage: zlib streams at 16-byte aligned offsets after the metadata, 64 KiB inflated chunks, resources as one stream per page | Payload data | | | Probable | Consistent with RPF9-F33, F35, F36. Not checked by following native offsets |
| RPF9-F30 | The name hash is the `u64` value of key `0x73BCB72DCE74F11F`. It is the only use site of that key | Decompilation, byte search | `0x5520AC0`, `0x28CD5B0` | `ev_61be8a7b` | Confirmed | Hash function unknown |
| RPF9-F31 | The name namespace is `u8` table `0x7A0B100` indexed by type ID, not an archive field. A fallback path uses table `0x7A0B000` and requires a nonzero `u32` of key `0xB7076B6245D35FB5` | Decompilation | `0x5305F10`, `0x55B2520`, `0x5305EE0`, `0x28CD5B0` | `ev_9917a12e` | Confirmed (lookup), Unknown (table contents, fallback arguments) | Initializer `0x56C9290` not analyzed |
| RPF9-F32 | Keys `0xBA180AFB232D1B4B` (R), `0x33F70DFAF2C50989` (F) and `0x4EAA16DD829995BC` (A) hold alternative location record layouts with payload offset, stored size, logical size, type ID and compression mode. Accessors test R, then F, then A, and dereference A without a null check | Decompilation, byte search | `0xC6950`, `0x1330AD0`, `0x1331670`, `0xF62E0`, `0x56ED70` | `ev_153a17a0` | Confirmed (layouts, order) | Exclusivity in real data not checked. Selection between F and A unknown |
| RPF9-F33 | A payload read address is `fileObject[+0x20] + (offsetField << 4) + position`. Offsets and stored sizes are in 16-byte units, relative to the archive base | Decompilation | `0x1330C10`, `0x13307E0` | `ev_95706daf` | Confirmed | |
| RPF9-F34 | The read dispatcher picks the chunk fast path, the compressed stream path (nonzero mode or chunk table present) or the plain path. Compressed reads fill a buffer in pieces of up to 0x10000 stored bytes. Plain reads clamp to the logical size | Decompilation | `0x314330`, `0x13308E0`, `0x28CF940` | `ev_e9e6bd9a` | Confirmed | |
| RPF9-F35 | Decoding without a chunk table dispatches on the entry compression mode: 0 copy, 2 fail, others through the codec table at `0x66FDD10`, whose slot 1 holds codec `0x6DD5B08`. The codec's decode slot drives a zlib `z_stream`-shaped structure and stops on return value 1 | Decompilation, executable data | `0x1330A50`, `0x1331380`, `0x1331210`, `0x66FDD10` | `ev_5e45406b` | Confirmed (dispatch), Probable (zlib inflate) | `0x5532220` not analyzed. No codec for modes above 2 established |
| RPF9-F36 | Key `0xE0C12D7A5D4884C5` is a chunk table: `u32` self-relative entry offset, `u16` count at `+4`, `u8` encoding at `+7`. Entries are `u64` in encodings 2, 3, 4 giving logical size, stored size, padding and a 2-bit chunk method. Chunk method 3 uses the codec object of entry mode 1. Other methods copy | Decompilation | `0x550DB40`, `0x1330560`, `0x1330CD0`, `0x1331110` | `ev_84915d3a` | Confirmed | Overlapping padding and size bits in encoding 3 unexplained. Decompression service behind the fast path not analyzed |
| RPF9-F37 | `0x28CD3B0` is a seek with modes 0, 1, 2, clamped to the logical size. Compressed streams reset on backward seeks and decode and discard forward in steps of at most 0x1000 bytes | Decompilation | `0x28CD3B0`, `0x13315F0` | `ev_1c7df613` | Confirmed | `0x28CF820` not analyzed |
| RPF9-F38 | With key `0x286030A358A789FB` present, stored bytes are read in 16-byte blocks through a per-stream context positioned at `position & ~0xF`, with separate handling of partial blocks. The same flag disables the chunk fast path | Decompilation | `0x1330B60`, `0x1331470`, `0x141D8A0` | `ev_05d7fcec` | Confirmed (routing), Unknown (algorithm, key source) | `0x19C380`, `0x1616150`, `0x28CF9C0` not analyzed |
| RPF9-F39 | The `A` table holds `{u16 id, u32 offset}` records that index sub-blocks of the `B` block. Validation step 3 looks up ID 1 | Decompilation | `0x1FB2300`, `0x4E6F740`, `0x4E6F780` | `ev_91bcfd06` | Confirmed (structure) | Layout describes bytes after validation step 1. `B` content unknown |
| RPF9-F40 | On the traced accessor paths, no code reads descriptor `+0x08` or `+0x12`, and the value pointer is not bounds-checked against the pool | Decompilation | `0x28CD240`, `0x55B2600`, `0x38300`, `0x28CE1B0` | `ev_f8713c59` | Confirmed (on traced paths) | Validation steps 2 and 4 not analyzed |
| RPF9-F41 | Key `0xCBB68FF7B7078DB7` is a `u32` read-source index, `0xFFFFFFFF` when absent, used to select the handle payload reads go through | Decompilation | `0x4F60AB0`, `0x1330C10` | `ev_78429516` | Probable | Index values and handle selection `0x4F60A90` not analyzed |

The field keys behind RPF9-F17 are listed in [schema.md](../../formats/containers/rpf9/schema.md#known-columns).

## Rejected

| Claim | Rejected by |
|---|---|
| The magic matches are accidental byte matches | RPF9-F01: all three are compare instructions |
| The whole metadata area is opaque | RPF9-F04 |
| The `C*24` records are file entries read at fixed offsets | RPF9-F08 |
| `C` is the entry count | RPF9-F08, RPF9-F13 |
| `F` is the width of the stored value | RPF9-F11, RPF9-F09 |
| Cells are stored column-major | RPF9-F11 |
| Cells hold the logical values | RPF9-F12 |
| The entry ID high half is a computed section counter | RPF9-F15 |
| Path lookup is a binary search over sorted hashes | RPF9-F20 |
| Header offsets `0x10` and `0x18` hold the archive size and timestamp | Header data: the values do not match either |
| Keys `0xBA18…`, `0x33F7…`, `0x4EAA…` are size columns | RPF9-F32 |
| Resource size `(w0 & 0xFFFFFFF0) + (w1 & 0x7FFFFFF0)` | RPF9-F16: the masks are the other way round |
| `0x28CD3B0` reads payloads in 4 KiB blocks | RPF9-F37 |
| Enumeration descriptor `+0x18` holds the archive base offset | RPF9-F21, RPF9-F33 |
| The name namespace is stored in a column | RPF9-F31 |

The [research history](research-history.md) explains the main corrections.
