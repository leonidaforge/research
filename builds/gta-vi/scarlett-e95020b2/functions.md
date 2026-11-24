# RPF9 functions in build e95020b2

RVAs for image base `0x140000000`. Roles are descriptive labels, not recovered symbol names. Finding IDs refer to the [evidence index](../../../evidence/rpf9/INDEX.md).

## Archive open

| RVA | Role | Confidence | Finding |
|---|---|---|---|
| `0xFC21C0` | File object factory: allocates 0x60 bytes, constructs, frees on failure. Optional magic check on a caller-supplied block (compare at `0xFC21D9`) | Confirmed | F01, F07 |
| `0xFC2240` | File object constructor. Resolves the device, opens the handle, reads size and time | Confirmed | F07 |
| `0xFC2490` | Allocates the 0x80-byte archive object | Confirmed | F07 |
| `0xFC2540` | Archive object constructor: header read, view descriptor, validation, view layout | Confirmed | F07 |
| `0x1FB2600` | Header and metadata reader. Magic compares at `0x1FB2619` (preloaded header) and `0x1FB2692` (disk) | Confirmed | F01, F02 |
| `0x28CDFC0` | Mode-0 metadata read helper, archive vtable `+0x398` | Confirmed | F02 |
| `0x1FB2780` | Builds the metadata view descriptor | Confirmed | F07 |
| `0x87AEC0` | Writes region pointers into the metadata view | Confirmed | F07 |
| `0x87AF70`, `0x87AFF0` | Read prefix counts, compute primary region offsets with alignment | Confirmed | F04, F05 |
| `0x87B0B0`, `0x87B0F0` | Compute secondary region offsets | Confirmed | F06 |

Callers of `0xFC21C0`: `0xFC20D0`, `0x1D4C980`, `0x1DEE6C0`, `0x22372C0`, `0x2758210`. A second path at `0xFA87F9`/`0xFA8805` runs the same layout and validation. It was not traced.

## Validation and cryptography

| RVA | Role | Confidence | Finding |
|---|---|---|---|
| `0x8EC200` | Validation chain entry. Every step must succeed | Confirmed | F23 |
| `0xA348A0` | Step 1: reads selector `0x2E`, picks descriptor and span set, processes `A` and `B` spans | Confirmed | F24, F26 |
| `0xA349A0` | Builds the two static cipher descriptors | Confirmed | F24 |
| `0x28CE530` | Conditional step 2. Branches to `0x1FB2370`, `0x28CE5B0`, `0x28CE5C0` and `0xDAED40`, none analyzed. Role unknown | Unknown | |
| `0x1FB2300` | Step 3. Looks up `B` sub-block 1 through the `A` table. Use of the result unknown | Confirmed (lookup) | F39 |
| `0x4E6F740` | `A` table lookup: returns `B + offset` for an ID, or null | Confirmed | F39 |
| `0x4E6F780` | Linear search of the `A` records by `u16` ID, `0xFFFF` if absent | Confirmed | F39 |
| `0x6BD040` | Step 4. Builds a context with `0x6BD090` and calls the span runner `0x6BD160` with one span. Which span is not traced | Confirmed (calls) | |
| `0x8EC360` | Step 5: processes the secondary area | Confirmed | F26 |
| `0x6BD160` | Span runner: init from descriptor, in-place `update` per span, boolean `final` | Confirmed | F27 |
| `0x536A70` | Cipher type to algorithm ID, 19-entry table | Confirmed | F25 |
| `0x613880` | Creates the algorithm object and resolves the key by identifier. Internals not analyzed | Confirmed (role) | F25 |
| `0x193F90` | Key lookup by identifier, called from `0x613880`. Not analyzed | Confirmed (call) | F25 |

## Schema access

| RVA | Role | Confidence | Finding |
|---|---|---|---|
| `0x28CE0A0` | Field value getter thunk: archive object `+0x28`, entry ID truncated to 16 bits | Confirmed | F14 |
| `0x28CE0B0` | Field pointer getter thunk, same adjustments | Confirmed | F14 |
| `0x28CE1B0` | Value accessor: present or absent | Confirmed | F14 |
| `0x38300` | Pointer accessor: returns the value pointer. No bounds check | Confirmed | F14, F40 |
| `0x28CD240` | Field key to column index, `0xFFFF` if absent | Confirmed | F08 |
| `0x4DB65B0` | Selects index store and stride, rebases secondary columns | Confirmed | F10 |
| `0x4DB6600` | Reads one compact index of `F` bytes, sentinel handling | Confirmed | F11 |
| `0x55B2600` | Builds the value pointer from pool, column base offset and element width. No bounds check | Confirmed | F12, F40 |
| `0x5305880` | Row resolver, returns `0xFFFF` when not found | Probable | F15 |
| `0x5305EC0` | Returns the `u16` at file object `+0x0C`, the entry ID high half. Reached only through the vtable | Confirmed | F15 |

## Entries, names, payloads

Location records:

| RVA | Role | Confidence | Finding |
|---|---|---|---|
| `0x1331670` | Logical size from R, F or A | Confirmed | F16 |
| `0x1330AD0` | Stored size from R, F or A | Confirmed | F32 |
| `0xC6950` | Payload offset from R, F or A | Confirmed | F32 |
| `0xF62E0` | Compression mode byte from R, F or A | Confirmed | F32, F35 |
| `0x4F885C0` | Compression mode is nonzero | Confirmed | F32 |
| `0x5305ED0` | Type ID of a row, through `0x56ED70` | Confirmed | F32 |
| `0x56ED70` | Type ID byte from R, F or A, using `0x4E3FA90`, `0x5568AE0`, `0x28CD220` | Confirmed | F32 |
| `0x4E3FA90`, `0x5568AE0`, `0x28CD220` | Pointer lookups of keys R, F and A on the metadata view. `0x28CD220` was decompiled. The other two were identified by their key constant and call site | Confirmed (`0x28CD220`), Probable (others) | F32 |

Names:

| RVA | Role | Confidence | Finding |
|---|---|---|---|
| `0x28CD5B0` | Open by path: linear row scan with name rebuild and substring match | Confirmed | F20 |
| `0x4DAC8F0` | Builds the 0x118-byte entry descriptor after a path match | Confirmed (call) | F20 |
| `0x5520AC0` | Name hash, key `0x73BCB72DCE74F11F` | Confirmed | F30 |
| `0x5305F10` | Namespace from the table at `0x7A0B100` by type ID | Confirmed | F31 |
| `0x55B2520` | Fallback namespace from the table at `0x7A0B000` by type ID | Confirmed | F31 |
| `0x5305EE0` | `u32` of key `0xB7076B6245D35FB5`, gate for the fallback name path | Confirmed (read) | F31 |
| `0x56C9290` | Guarded one-time initializer run before the namespace table read. Not analyzed | Confirmed (call) | F31 |
| `0x4DA8040` | Fallback name lookup. Arguments not verified | Confirmed (call) | F31 |
| `0x553D070` | Hashed-string dictionary lookup by namespace and hash | Confirmed | F18 |
| `0x4EBBC30` | Extension string from type ID. Default string at `0x678832B` | Confirmed | F19 |

Enumeration:

| RVA | Role | Confidence | Finding |
|---|---|---|---|
| `0x28CDA50` | Child enumeration into 0x20-byte descriptors | Confirmed | F21 |
| `0x28C6B20` | Batch open, read and collect over an ID array | Confirmed | F21 |

Reads and seeks:

| RVA | Role | Confidence | Finding |
|---|---|---|---|
| `0x314330` | Read dispatcher: chunk fast path, compressed stream or plain | Confirmed | F34 |
| `0x28CD3B0` | Seek: modes 0, 1, 2, clamp to logical size, 4 KiB decode-and-discard for compressed forward seeks | Confirmed | F37 |
| `0x28CF820` | Called by seek for chunked entries without the transform flag. Not analyzed | Confirmed (call) | F37 |
| `0x28CF940` | Plain read, clamped to the logical size | Confirmed | F34 |
| `0x13308E0` | Compressed stream read: fills the stream buffer in pieces of up to 0x10000 bytes, then decodes | Confirmed | F34 |
| `0x1330B60` | Stored-byte read. Branches on the payload transform flag | Confirmed | F33, F38 |
| `0x1330C10` | Device read at `fileObject[+0x20] + payloadOffset + position` | Confirmed | F33 |
| `0x4F60AB0` | Read-source index, key `0xCBB68FF7B7078DB7`, `0xFFFFFFFF` if absent | Confirmed (read) | F41 |
| `0x4F60A90` | Selects the read handle from the source index, file object `+0x18` and `+0x50` | Probable | F41 |
| `0x1331470` | Transform read: positions the context at a 16-byte boundary, processes whole blocks, handles partial blocks | Confirmed | F38 |
| `0x19C380` | Positions the payload transform context. Not analyzed | Confirmed (call) | F38 |
| `0x1616150` | Processes whole 16-byte blocks in place. Not analyzed | Confirmed (call) | F38 |
| `0x28CF9C0` | Reads a partial block for the transform. Not analyzed | Confirmed (call) | F38 |

Decoding and chunks:

| RVA | Role | Confidence | Finding |
|---|---|---|---|
| `0x1330A50` | Decode dispatch: chunk decoder if the chunk table is present, else by entry compression mode | Confirmed | F35 |
| `0x1331380` | Decode by entry mode: 0 copy, 2 fail, other codec table slot | Confirmed | F35 |
| `0x1331210` | Codec decode slot. Drives a zlib `z_stream`-shaped structure, end of stream on return value 1 | Confirmed (structure), Probable (zlib) | F35 |
| `0x5532220` | Inner decode call of `0x1331210`. Not analyzed | Probable (`inflate`) | F35 |
| `0x13315F0` | Resets the stream decoder for an entry | Confirmed | F37 |
| `0x1330CD0` | Chunk decoder: per-chunk method, codec or copy | Confirmed | F36 |
| `0x550DB40` | Decodes one chunk table entry, encodings 2, 3 and 4 | Confirmed | F36 |
| `0x13310F0`, `0x1331110` | Chunk method 3 selects the codec object. Other methods select copy | Confirmed | F36 |
| `0x141D8A0` | Tests whether the chunk fast path applies | Confirmed | F36 |
| `0x1330560` | Chunk fast path read: groups chunks into runs | Confirmed | F36 |
| `0x13307E0` | Submits a chunk run with its disk address to the decompression service through `0x28CFA70` | Confirmed | F36 |

Data:

| RVA | Content | Confidence | Finding |
|---|---|---|---|
| `0x66FDD10` | Codec table by entry compression mode. Slot 0 null, slot 1 `0x6DD5B08`, slot 2 null | Confirmed | F35 |
| `0x6DD5B08` | Codec object, vtable `0x66FDD40`, decode slot `+0x30` | Confirmed | F35 |
| `0x79F6D70` | Pointer to the decompression service used by the chunk fast path | Confirmed (use) | F36 |
| `0x7A0B000`, `0x7A0B100` | Fallback and primary namespace tables, `u8` per type ID | Confirmed (use) | F31 |

## Archive vtable

Archive object vtable at RVA `0x62FD480`.

| Slot | RVA | Role | Confidence |
|---|---|---|---|
| `+0x28` | `0x28CD2E0` | Open entry by key, returns a handle or -1 | Probable |
| `+0x30` | `0x2758940` | Open entry, variant with an extra argument | Probable |
| `+0x60` | `0x28CD360` | Read or seek on a handle | Probable |
| `+0x80` | `0x28CD3B0` | Seek | Confirmed |
| `+0x90` | `0x503F490` | Release handle | Probable |
| `+0x108` | `0x28CD580` | Fetch an entry field or size by ID | Probable |
| `+0x120` | `0x28CD5B0` | Open by path | Confirmed |
| `+0x1A0` | `0x28CDA50` | Child enumeration | Confirmed |
| `+0x1B0` | `0x28C6B20` | Batch open | Confirmed |
| `+0x2E0` | `0x1330AD0` | Stored size | Confirmed |
| `+0x2E8` | `0x1331670` | Logical size | Confirmed |
| `+0x2F0` | `0x4F885C0` | Compression mode is nonzero | Confirmed |
| `+0x2F8` | `0xF62E0` | Compression mode | Confirmed |
| `+0x398` | `0x28CDFC0` | Mode-0 metadata read | Confirmed |
| `+0x3D0` | `0x5305EC0` | Entry ID high half | Confirmed |
| `+0x3F0` | `0x28CE0A0` | Field value getter | Confirmed |
| `+0x3F8` | `0x28CE0B0` | Field pointer getter | Confirmed |

File object vtable at RVA `0x62FD890`.

## Object layouts

Archive object, 0x80 bytes:

| Offset | Content | Confidence |
|---|---|---|
| `+0x00` | Vtable | Confirmed |
| `+0x08` | File object pointer. Cleared when the open fails | Confirmed |
| `+0x18` | Primary metadata buffer | Confirmed |
| `+0x20` | Secondary metadata buffer | Confirmed |
| `+0x28` | Metadata view, see below | Confirmed |
| `+0x7C` | Flags byte | Confirmed (presence) |

Metadata view at archive object `+0x28`:

| Offset | Content |
|---|---|
| `+0x00` | State word, set to 2 by the constructor |
| `+0x08` | Header and prefix |
| `+0x10` | `A` table |
| `+0x18` | `B` block |
| `+0x20` | Column descriptors |
| `+0x28` | Primary index store |
| `+0x30` | Primary value pool |
| `+0x38` | Secondary index store |
| `+0x40` | Secondary value pool |

File object, 0x60 bytes:

| Offset | Content | Confidence |
|---|---|---|
| `+0x0C` | `u16` tag, high half of entry IDs | Confirmed |
| `+0x10` | Device. Payload reads call its vtable slot `+0x60` | Confirmed |
| `+0x18` | Handle, -1 when the open failed. Input to the read-handle selection `0x4F60A90` | Probable |
| `+0x20` | Archive base offset. Added to every payload read address | Confirmed (use) |
| `+0x30` | `u64` copied into enumeration and path-lookup descriptors. Meaning unknown | Confirmed (use) |
| `+0x50` | Input to the read-handle selection `0x4F60A90` | Confirmed (use) |

The device interface reads through vtable slot `+0x60` and reports size and time through `+0xF8` and `+0x108`. The device read implementation is not traced.

Stream object, used by seek and the read paths:

| Offset | Content | Confidence |
|---|---|---|
| `+0x00` | Buffer for stored bytes, filled in pieces of up to 0x10000 bytes | Probable |
| `+0x10008` | Handle that resolves to the entry ID | Confirmed (use) |
| `+0x10010` | Logical position | Confirmed |
| `+0x10018` | Stored-byte cursor of compressed reads | Confirmed |
| `+0x10020` | Decoder state | Confirmed (use) |
| `+0x10028` | Payload transform context | Confirmed (use) |
