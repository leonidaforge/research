# RPF9 evidence index

Executable findings refer to build [scarlett-e95020b2](../../builds/gta-vi/scarlett-e95020b2/README.md), SHA-256 `e95020b2fa4a721db3df59fdecf75621730ac559d8835252f6c3b658d5a08993`, image base `0x140000000`. Function roles are listed in the [function catalog](../../builds/gta-vi/scarlett-e95020b2/functions.md).

## Evidence types

| Type | Meaning |
|---|---|
| Disassembly | Instruction-level reading of the function at the given RVA, including its call sites |
| Decompilation | Decompiled control flow and data access of the function at the given RVA, checked against its callers |
| Header data | Layout arithmetic checked against the plain header fields of real archives. Offsets and sizes only, no decoded values |
| Payload data | Structure observed in archive payload bytes. Not traced in game code |

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
| RPF9-F16 | Size helper: resource size `(w0 & 0xFFFFFFF0) + (w1 & 0x7FFFFFF0)` from a two-word pooled value. Other columns are masked to 44 and 48 bits | Decompilation | `0x1331670` | | Confirmed (arithmetic), Probable (column meanings) | Meaning of the two words not established |
| RPF9-F17 | Field keys observed at use sites, with probable column meanings | Decompilation | `0x1331670`, `0x28CD3B0`, `0x28CDA50` | | Probable, one Speculative | Key hash algorithm unknown |
| RPF9-F18 | Names are resolved by `(namespace, u64 hash)` lookup in a runtime dictionary, which returns a string or null | Decompilation | `0x553D070` | | Confirmed | Hash algorithm and namespace values unknown |
| RPF9-F19 | Extensions come from a numeric type ID. `0xFF` means no extension. Unknown IDs give a default string | Decompilation | `0x4EBBC30` | | Confirmed | Type ID table not decoded |
| RPF9-F20 | Path open splits on `/`, rebuilds name plus extension for every row, and matches with a substring search | Decompilation | `0x28CD5B0` | | Confirmed | |
| RPF9-F21 | Child enumeration writes one 0x20-byte descriptor per entry ID. Batch open iterates an ID array | Decompilation | `0x28CDA50`, `0x28C6B20` | | Confirmed (shape) | Descriptor fields beyond an offset-like value and the device base unknown |
| RPF9-F22 | Stream read supports set, current and end seeks, clamps to the entry size and reads in `0x1000`-byte blocks | Decompilation | `0x28CD3B0`, `0x314330` | | Confirmed | Decompression call not traced |
| RPF9-F23 | Cryptographic processing runs inside the validation chain after the metadata read. Failure rejects the archive | Disassembly | `0x8EC200` | | Confirmed | |
| RPF9-F24 | `u8@0x2E` selects processing: 0 none, bit 0 span set, `value >> 1` descriptor index with a default fallback | Disassembly | `0xA348A0`, `0xA349A0` | | Confirmed | |
| RPF9-F25 | A descriptor holds a 32-bit key identifier, a `u16` cipher type and a 16-byte parameter. The type maps to an algorithm through a 19-entry table. The key is looked up by identifier at runtime | Disassembly | `0x536A70`, `0x613880` | | Confirmed (structure) | Algorithm and key lookup not analyzed |
| RPF9-F26 | Processed spans: the `A` table and the `B` block minus its last `u32@0x30` bytes, plus a separate pass over the secondary area | Disassembly | `0xA348A0`, `0x8EC360` | | Confirmed | Span set for bit 0 clear not described |
| RPF9-F27 | The span runner calls `update` with identical input and output pointers, then a `final` that returns bool. This fits authenticated in-place decryption with a 16-byte tag | Disassembly | `0x6BD160` | | Probable | Verify-only use not excluded |
| RPF9-F28 | Lookups read the view built after validation. Whether the descriptors, primary cells and primary pool are transformed on disk is not established | Disassembly, decompilation | `0xFC2540` | | Confirmed (order), Unknown (storage state) | See [cryptography](../../cryptography/rpf9/README.md#open-questions) |
| RPF9-F29 | Payload storage: zlib streams at 16-byte aligned offsets after the metadata, 64 KiB inflated chunks, resources as one stream per page | Payload data | | | Probable | Not traced in game code |

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

The [research history](research-history.md) explains the main corrections.
