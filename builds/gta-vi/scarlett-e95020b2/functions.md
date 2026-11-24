# RPF9 functions in build e95020b2

RVAs for image base `0x140000000`. Roles are descriptive labels, not recovered symbol names. Finding IDs refer to the [evidence index](../../../evidence/rpf9/INDEX.md).

## Archive open

| RVA | Role | Confidence | Finding |
|---|---|---|---|
| `0xFC21C0` | File object factory: allocates 0x60 bytes, constructs, frees on failure. Optional magic check on a caller-supplied block (compare at `0xFC21D9`) | Confirmed | F01, F07 |
| `0xFC2240` | File object constructor. Resolves the path and device, opens the handle, reads size and time or sizes from the parent archive, registers the tag | Confirmed | F07, F62, F64, F65 |
| `0x56EB30` | Tries each search root, normalizes the candidate, keeps the first one whose device reports existence | Confirmed | F62 |
| `0x128BB70`, `0x128BAE0` | Path normalizers called by `0x56EB30`. Not analyzed | Confirmed (call) | F62 |
| `0x968490` | Device lookup for a path. Not analyzed | Confirmed (call) | F62, F65 |
| `0x55B2550` | Claims the first free slot from 1 upwards in the global file object registry and returns its index | Confirmed | F64 |
| `0x28CD1A0` | Offset of the file name in a path, stored at file object `+0x0E` | Probable | F64 |
| `0xFC2490` | Allocates the 0x80-byte archive object. File object vtable `+0x08`. Can cache the archive at file object `+0x58` | Confirmed | F07 |
| `0x11A8970` | Preloaded archive factory, file object vtable `+0x10`. Caches the archive at file object `+0x58`. No open check | Confirmed | F75 |
| `0x11A89C0` | Preloaded archive constructor. Same vtable `0x62FD480`. Metadata from the parent's `0xC267…` copy or a device read of `hdr[0x04]` bytes. No header read, layout or validation | Confirmed | F75 |
| `0x1FB22A0` | Parent metadata copy available: device is a version-9 archive with laid-out metadata and column `0xC26722D233648AE7` | Confirmed | F75 |
| `0x1941B0` | Synchronous read through the global read service. Traps on failure | Confirmed | F75 |
| `0x1DEE6C0` | Batch archive loader. Only traced caller of file object vtable `+0x10` | Confirmed | F76 |
| `0x1FB2260` | Device is the same underlying device as a fixed global device. Gates the preloaded construction in the batch loader | Confirmed | F76 |
| `0xDAB760` | Copies a 0x20-byte preload block from a global index record | Confirmed | F76 |
| `0x23D9500`, `0xFA8740` | Parallel job worker of the batch loader. Calls archive `+0x3A8` when `+0x3A0` is false | Confirmed | F76 |
| `0xA57F70` | Derives the default mount prefix from the file object path. Archive vtable `+0x3C0` | Confirmed | F61 |
| `0x54524E0` | End of the directory part of a path, with the `memory:` exception | Confirmed | F61 |
| `0xA58030` | Stores the prefix length and folded hash in the archive object. Called at construction and by the mount method | Confirmed | F61 |
| `0x12C5630` | Archive mount method, vtable `+0x3B8`: mounts with flag 1, then stores the mount prefix as resolver prefix | Confirmed | F61, F69 |
| `0x22372C0` | Mount routine: creates the file object and archive for a path, mounts the archive, keeps both in owner lists | Confirmed | F69 |
| `0x56DD530` | File object destructor: releases the registry slot, releases handles through the device, frees the path | Confirmed | F72 |
| `0x56DD5F0` | Releases a file object registry slot | Confirmed (call) | F72 |

## Devices and mount table

| RVA | Role | Confidence | Finding |
|---|---|---|---|
| `0x968490` | Device for a path: fixed schemes and drive prefixes, else the mount table | Confirmed | F68 |
| `0x28C8EC0` | Mount table lookup: longest prefix, then the newest device whose existence test succeeds, else the fallback device | Confirmed | F68 |
| `0x12C5670` | Mounts a device at a prefix, or sets the fallback device for `default` | Confirmed | F68 |
| `0x55B2370` | Bounded prefix compare, ASCII case-insensitive, `\` equal to `/` | Confirmed | F68 |
| `0x28CB450` | Unmounts a prefix. Does not release devices | Confirmed | F68 |
| `0x28CB640` | Removes one device from every prefix. Does not release it | Confirmed | F68 |
| `0x28C33E0`, `0x28CB380` | Clear the mount table. `0x28CB380` also stops the request worker | Confirmed | F68 |
| `0x78F5EC8`, `0x78F5EC4`, `0x78F5EC0`, `0x78F5ED0` | Mount table array of 0x20-byte records, count, capacity, lock | Confirmed | F68 |
| `0x693A270` | Fallback device pointer. Initially the physical file device `0x78F5EB0` | Confirmed | F68, F83 |
| `0x28C21A9` | Static initializer: stores vtable `0x62FDAE0` into the physical file device object `0x78F5EB0` | Confirmed | F83 |
| `0x28C8220` | Physical device open, vtable `+0x28`: writes base 0, then `CreateFileW` read-only | Confirmed | F83 |
| `0x314200` | Physical device read, vtable `+0x60`: positional `ReadFile` loop, unbounded retry on unexpected errors | Confirmed | F83 |
| `0x28C8400` | Physical device release, vtable `+0x90`: `CloseHandle` | Confirmed | F83 |

Mount record, 0x20 bytes:

| Offset | Content | Confidence |
|---|---|---|
| `+0x00` | Prefix string | Confirmed |
| `+0x08` | `u16` flag. Lookups with mode 0 skip the record when it is set | Confirmed (use), Probable (read-only) |
| `+0x0A` | `u16` prefix length | Confirmed |
| `+0x10` | `u32` device array capacity | Confirmed |
| `+0x14` | `u32` device count | Confirmed |
| `+0x18` | Device pointer array | Confirmed |
| `0xFC2540` | Archive object constructor: header read, view descriptor, validation, view layout | Confirmed | F07 |
| `0x1FB2600` | Header and metadata reader. Magic compares at `0x1FB2619` (preloaded header) and `0x1FB2692` (disk) | Confirmed | F01, F02 |
| `0x28CDFC0` | Mode-0 metadata read helper, archive vtable `+0x398` | Confirmed | F02 |
| `0x1FB2780` | Builds the metadata view descriptor | Confirmed | F07 |
| `0x87AEC0` | Writes region pointers into a metadata view. Used for the validation view and again for the archive view | Confirmed | F07 |
| `0x87AF70`, `0x87AFF0` | Read prefix counts, compute primary region offsets with alignment. No bounds checks | Confirmed | F04, F05, F47 |
| `0x87B0B0`, `0x87B0F0` | Compute secondary region offsets | Confirmed | F06 |

Callers of `0xFC21C0`: `0xFC20D0`, `0x1D4C980`, `0x1DEE6C0`, `0x22372C0`, `0x2758210`. Archive vtable `+0x3A8`, `0xFA87E0`, reruns view layout and validation on the existing buffers, then calls `0x28CE230` when file object `+0x08` bit 0 is clear.

## Validation and cryptography

| RVA | Role | Confidence | Finding |
|---|---|---|---|
| `0x8EC200` | Validation entry. Passes "file object `+0x08` bit 0 clear" as the step 2 condition to `0x8EC210` | Confirmed | F23, F42 |
| `0x8EC210` | Validation chain: step 1, step 2 if enabled, sub-block 1 lookup, then steps 4 and 5 if sub-block 1 exists | Confirmed | F42 |
| `0xA348A0` | Step 1: reads selector `0x2E`, picks descriptor and span set, processes `A` and `B` spans. Does nothing for selector 0 | Confirmed | F24, F26 |
| `0xA349A0` | Builds the two static cipher descriptors | Confirmed | F24 |
| `0x28CEB20` | Step 1 span for selector bit 0 clear: `A` and all of `B` as one span | Confirmed | F26 |
| `0x28CE530` | Step 2: signature check with sub-block 6, else sub-block 2 | Confirmed | F43 |
| `0x1FB2370`, `0x28CE5B0` | Look up `B` sub-blocks 6 and 2 | Confirmed | F43 |
| `0xDAED40`, `0x28CE5C0` | Build the check request from sub-block 6 or 2 | Confirmed | F43 |
| `0xDAED80` | Checks that the signature lies in `B`, builds the message, looks up the key and runs the verifier | Confirmed | F43, F92 |
| `0x28CE970`, `0x1FB2380` | Message span lists for message types 0 and 1 | Confirmed | F43 |
| `0x28CEA80`, `0x28CEAB0` | Message length and concatenation | Confirmed | F43 |
| `0xDAF010` | Verifier init: resolves the record's key identifier through the static key registry, then imports the key | Confirmed | F43, F93 |
| `0xDAEFD0`, `0x1171770`, `0x11717F8` | Verifier entry, scheme wrapper and hash call: SHA-256 over the message, DigestInfo encoding, core call with RSA type 3 | Confirmed | F92 |
| `0x216E7B5` | Signature core: size check, RSA public operation, payload length and DigestInfo compare. Returns 0 on success | Confirmed | F92 |
| `0x216CCAD`, `0x216C9A7` | RSA public operation entry and modular exponentiation | Confirmed | F92 |
| `0x216BC9E` | Padding decoder: mode 0 requires `00 01 FF...FF 00`, mode 1 is the other path | Confirmed | F92 |
| `0x218FA76`, `0x218F82D`, `0x218FC97` | SHA-256 one-shot, hash length table lookup and hash dispatch | Confirmed | F92 |
| `0x216E99A`, `0x2166CBA` | DigestInfo length selection and DER DigestInfo writer | Confirmed (OID and writer), Probable (standard layout) | F92 |
| `0xB2DF40`, `0x2165694` | Key import and DER SubjectPublicKeyInfo parse | Confirmed | F93 |
| `0x28CE230` | After a successful open with step 2 enabled: opens the companions of sub-block 3, sets file object `+0x09` bit 0 from the fingerprint check, sets `+0x08` bit 0 | Confirmed | F44, F63, F81 |
| `0x28CE280` | Opens each sub-block 3 companion, checks its header and appends the handle, or -1, to the alternate array. Stops at the first failed open | Confirmed | F81 |
| `0x28CE450` | Reads the sub-block 3 count and record pointer | Confirmed | F81 |
| `0x28CE460` | Builds `<archive directory>/<name>` in a 0x108-byte buffer and removes `/../` | Confirmed | F81 |
| `0x28CE4D0` | Companion check: 16 bytes at the base, magic `0x5250465639000000` and identifier | Confirmed | F81 |
| `0xC63230` | Fingerprint check: header `u32@0x28` against the startup value or the sub-block 9 value, chosen by `u8@0x2D` bit 3 | Confirmed | F63 |
| `0xC632E0`, `0xC632F0` | Look up `B` sub-block 9 and read its count and type ID list | Confirmed | F63 |
| `0xC63300` | Builds the type classification bit mask for the listed type IDs and hashes it | Confirmed | F63 |
| `0xC63390` | 32-bit hash over the bit mask. CityHash32 structure | Confirmed (call), Probable (CityHash32) | F63 |
| `0x1DFBD20`, `0x5C0B8E0` | Startup fingerprint over all 256 type IDs, stored at `0x7A0B204` | Confirmed | F63 |
| `0x1FB2300` | Looks up `B` sub-block 1, the per-archive descriptor. Not a validation step | Confirmed | F39, F42 |
| `0x4E6F740` | `A` table lookup: returns `B + offset` for an ID, or null. Offset not checked | Confirmed | F39, F47 |
| `0x4E6F780` | Linear search of the `A` records by `u16` ID, `0xFFFF` if absent | Confirmed | F39 |
| `0x6BD040` | Step 4: one span from `0x6BD090`, span runner with the sub-block 1 descriptor | Confirmed | F45 |
| `0x6BD090`, `0x6BD100`, `0x6BD110`, `0x6BD150` | Step 4 span: `B` trailer through `hdr[0x08]` | Confirmed | F45, F49 |
| `0x8EC360` | Step 5: secondary area with the sub-block 1 descriptor | Confirmed | F26, F45 |
| `0x6BD160` | Span runner: init from descriptor, in-place `update` per span, `final` after each span and at the end for cipher types 3 to 5, else once | Confirmed | F27, F46, F53 |
| `0x536A70` | Cipher initializer: maps the descriptor type through `0x536AC0`, then calls `0x613880` with mode 1, key identifier and parameter | Confirmed | F25 |
| `0x536AC0` | Cipher type to algorithm ID, 19-entry table at `0x62FE860`. Types of 19 or more give 0 | Confirmed | F25, F51 |
| `0x1FB2310` | Returns the per-thread cipher context | Confirmed | F50 |
| `0x613880` | Replaces the algorithm object when the algorithm ID changes, looks up the key and initializes the object | Confirmed | F25, F50 |
| `0x193F90` | Key lookup by identifier, algorithm ID and mode, called from `0x613880`. Not analyzed | Confirmed (call) | F25 |
| `0x4C11250` | Algorithm object factory by algorithm ID. Traps for `0x0D` to `0x0F` | Confirmed | F50, F51 |
| `0x613720`, `0x613740` | `update` and `final` dispatch to algorithm object slots `+0x18` and `+0x20` | Confirmed | F50 |
| `0x19056F0` | Creates the algorithm `0x10` object: mode 0 engine null, mode 1 engine from `0x19057B0` | Confirmed | F53 |
| `0x4C115E0` | Algorithm `0x10` init: selects the engine by mode, initializes it, stores the 16-byte parameter | Confirmed | F53 |
| `0x6137D0` | Algorithm `0x10` `update`: requires output at least as long as input, runs the engine | Confirmed | F53 |
| `0x613760`, `0x613780` | Algorithm `0x10` `final`: resets the engine IV to the stored parameter and returns success | Confirmed | F53 |
| `0x55DC660` | Engine setup: checks the key-material magic `0x4E3B9B8E`, copies a 240-byte schedule, 16 × 256-byte final-round tables and the IV into the 0x1100-byte state | Confirmed | F53, F54, F88 |
| `0x55DBCF0` | Engine CBC decryption over whole 16-byte blocks, keeps the last stored block as the next IV | Confirmed | F53 |
| `0x55DBA30` | Engine IV reset | Confirmed | F53 |
| `0x5642C50` | 128-bit block decryption: encoded AES-256 decryption (affine pre-stage, 13 table rounds, substitution-only final round) | Confirmed (instruction-derived model, S-box, linear layers) | F54, F85, F86, F87, F88, F89, F90, F91 |
| `0x5643140` | CBC XOR with the IV and previous stored blocks, then copy to the output | Confirmed | F53 |

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
| `0x5305880` | Path to row resolver: mount prefix check, extension to type, stem hash, row lookup. Returns `0xFFFF` when not found | Confirmed | F55 |
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
| `0x56F130` | Row lookup by 64-bit name hash and type ID. Linear scan, or binary search when file object `+0x09` bit 0 is set | Confirmed | F58 |
| `0x56EC70` | Row lookup by 32-bit key and type ID, same two methods | Confirmed | F58 |
| `0x56F250` | Lower-bound binary search for the 64-bit lookup | Confirmed | F58 |
| `0x56EDC0` | Lower-bound binary search for the 32-bit lookup. Not decompiled | Confirmed (call) | F58 |
| `0x56EE50` | Extension to type ID: case-sensitive string compares, then registered handlers, else `0xFF` | Confirmed | F59 |
| `0x4F66800` | 64-bit hash dispatch through the namespace's hash function pointer | Confirmed | F56 |
| `0x4F66DE0` | Folded MurmurHash3 x64-128 variant | Confirmed | F56 |
| `0x4F67220` | Same hash without folding | Confirmed | F56 |
| `0x4FC21D0` | joaat: core `0x4FC21F0` plus the final avalanche | Confirmed | F57 |
| `0x4FC21F0` | joaat core with folding and the leading-quote rule | Confirmed | F57 |
| `0x28CD5B0` | Substring lookup: reverse lookup of every row through the dictionaries, `strstr` on the dictionary string, first match in row order | Confirmed | F20 |
| `0x4DAC8F0` | Bounded string copy. Copies the matched dictionary string into the result record | Confirmed | F20 |
| `0x28CF380`, `0x28CF7A0` | Append a 0x120-byte match record, return the first record | Confirmed | F20 |
| `0x5520AC0` | Name hash, key `0x73BCB72DCE74F11F` | Confirmed | F30 |
| `0x5305F10` | Namespace of the 64-bit class from the table at `0x7A0B100` by type ID | Confirmed | F31 |
| `0x55B2520` | Namespace of the 32-bit class from the table at `0x7A0B000` by type ID | Confirmed | F31 |
| `0x5305EE0` | `u32` of key `0xB7076B6245D35FB5`, the 32-bit key | Confirmed | F31, F57 |
| `0x5305F30` | Guarded call of `0x56C9290` | Confirmed | F59 |
| `0x56C9290` | Fills both per-type namespace tables. The 32-bit table is seeded from `0x62FC510` | Confirmed | F59 |
| `0x4DA8040` | 32-bit dictionary lookup by namespace and key | Confirmed | F31, F60 |
| `0x553D070` | 64-bit dictionary lookup by namespace and hash | Confirmed | F18 |
| `0x4FD8E70` | 64-bit dictionary insert. Gated by namespace flag bit 1, first insert wins | Confirmed | F60 |
| `0x554AE00` | 32-bit dictionary insert | Confirmed (call) | F60 |
| `0x541F000` | Inserts a list of strings into one 32-bit namespace | Confirmed | F60 |
| `0x4FD9E60` | UTF-8 check before insertion | Confirmed | F60 |
| `0xC3EEF0`, `0x4061230` | Structured-data field setters that hash and insert strings | Confirmed | F60 |
| `0x1E1CCE0` | Allocates the 64-bit dictionaries and their control blocks | Confirmed | F60 |
| `0x5C34FD0` | Initializes the namespace control blocks: hash functions and flags | Confirmed | F60 |
| `0x4EBBC30` | Extension string from type ID. Default string at `0x678832B` | Confirmed | F19 |

Batch operations:

| RVA | Role | Confidence | Finding |
|---|---|---|---|
| `0x28CDA50` | Batch path resolution into 0x20-byte descriptors | Confirmed | F21 |
| `0x28C6B20` | Batch open, read and collect over an ID array | Confirmed | F21 |

Reads and seeks:

| RVA | Role | Confidence | Finding |
|---|---|---|---|
| `0x314330` | Read dispatcher: chunk fast path, compressed stream or plain | Confirmed | F34 |
| `0x28CD3B0` | Seek: modes 0, 1, 2, clamp to logical size, 4 KiB decode-and-discard for compressed forward seeks | Confirmed | F37 |
| `0x28CF820` | Seek helper for chunked entries: finds the chunk holding the target with 32-bit sums, moves position and stored cursor to its start | Confirmed | F37, F79 |
| `0x13307C0` | Sets the current chunk index and clears the per-chunk decoder counters | Confirmed | F79 |
| `0x28CF940` | Plain read, clamped to the logical size | Confirmed | F34 |
| `0x13308E0` | Compressed stream read: fills the stream buffer in pieces of up to 0x10000 bytes, then decodes. Traps on decoder failure, returns without status on read failure | Confirmed | F34, F80 |
| `0x1330B60` | Stored-byte read. Branches on the payload transform flag | Confirmed | F33, F38 |
| `0x1330C10` | Device read at `fileObject[+0x20] + payloadOffset + position` | Confirmed | F33 |
| `0x4F60AB0` | Read-source index, key `0xCBB68FF7B7078DB7`, `0xFFFFFFFF` if absent | Confirmed | F41 |
| `0x4F60A90` | Read handle: main handle for `0xFFFFFFFF`, else `alternates[index]` without bounds or null checks | Confirmed (assembly) | F41, F73 |
| `0x1331470` | Transform read: positions the context at a 16-byte boundary, processes whole blocks, handles partial blocks | Confirmed | F38 |
| `0x19C380` | Positions the payload transform context. Not analyzed | Confirmed (call) | F38 |
| `0x1616150` | Processes whole 16-byte blocks in place. Not analyzed | Confirmed (call) | F38 |
| `0x28CF9C0` | Reads a partial block for the transform. Not analyzed | Confirmed (call) | F38 |

Decoding and chunks:

| RVA | Role | Confidence | Finding |
|---|---|---|---|
| `0x1330A50` | Decode dispatch: chunk decoder if the chunk table is present, else by entry compression mode | Confirmed | F35 |
| `0x1331380` | Decode by entry mode: 0 copy, 2 fail, other codec table slot | Confirmed | F35 |
| `0x1331210` | Codec decode slot `+0x30`. Drives a zlib `z_stream`-shaped structure, failure on negative result, end of stream on 1 | Confirmed | F35, F77 |
| `0x5532220` | DEFLATE decoder state machine with zlib's error messages | Confirmed (DEFLATE), Probable (zlib `inflate`) | F35, F77 |
| `0x13B9050` | Decoder initializer with `inflateInit2` semantics: window sign selects raw or zlib container | Confirmed | F77 |
| `0x1331190` | Sets up the `z_stream` of a decoder slot and calls `0x13B9050` with the caller's window parameter | Confirmed | F77 |
| `0x1331660` | Codec slot `+0x28`: initializes with window -15, raw DEFLATE | Confirmed | F77 |
| `0x1331100` | Codec slot `+0x38`: releases the decoder before a chunk is reinitialized | Probable | F78 |
| `0x1331310` | One-shot chunk decode through `0x2158744`. Credits the full chunk sizes on success | Confirmed | F78, F80 |
| `0x2158744` | One-shot zlib decode: checks the RFC 1950 header, decodes, compares the checksum trailer | Confirmed | F77 |
| `0x13315F0` | Resets the stream decoder for an entry: chunk index 0, decoder slot 1 initialized as raw DEFLATE | Confirmed | F37, F77 |
| `0x1330CD0` | Chunk decoder: per-chunk method, zlib decoder reinitialized per method-3 chunk, or copy. Finishes a chunk on exact compressed and logical sizes, then skips padding | Confirmed | F36, F78 |
| `0x550DB40` | Decodes one chunk table entry, encodings 2, 3 and 4 | Confirmed | F36 |
| `0x13310F0`, `0x1331110` | Chunk method 3 selects decoder slot 1 and the codec object. Other methods select copy | Confirmed | F36, F78 |
| `0x141D8A0` | Tests whether the chunk fast path applies | Confirmed | F36 |
| `0x1330560` | Chunk fast path read: groups chunks into runs | Confirmed | F36 |
| `0x13307E0` | Submits a chunk run with its disk address to the decompression service through `0x28CFA70` | Confirmed | F36 |
| `0x28CFA70` | Calls the decompression service through slot `+0x230` of its inner object. Target not resolved | Confirmed (call) | F36 |

Data:

| RVA | Content | Confidence | Finding |
|---|---|---|---|
| `0x66FDD10` | Codec table by entry compression mode. Slot 0 null, slot 1 `0x6DD5B08`, slot 2 null | Confirmed | F35 |
| `0x6DD5B08` | Codec object, vtable `0x66FDD40`: `+0x28` raw init, `+0x30` decode, `+0x38` release | Confirmed | F35, F77 |
| `0x79F6D70` | Pointer to the decompression service used by the chunk fast path | Confirmed (use) | F36 |
| `0x7A0B000`, `0x7A0B100` | Namespace tables of the 32-bit and 64-bit class, `u8` per type ID, filled at runtime | Confirmed | F31, F59 |
| `0x65B23B0` | 256-byte folding table: ASCII upper case to lower case, `\` to `/` | Confirmed | F56 |
| `0x62FCD30` | Type-to-extension pointer table, 19 types per variant | Confirmed (use) | F19, F59 |
| `0x99FED28`, `0x99FED30` | 64-bit dictionary maps and their 0x58-byte control blocks | Confirmed | F60 |
| `0x99FED10`, `0x99FED18` | 32-bit dictionary maps and their control blocks | Confirmed | F60 |
| `0x62FE540` | Verifier vtable for step 2 | Confirmed | F43 |
| `0x62FE720`, `0x62FE760` | Message builder vtables for message types 0 and 1. `0x62FE740` serves other types and always fails | Confirmed | F43 |
| `0x66FDB70` | Algorithm 0 vtable: every operation returns success | Confirmed | F52 |
| `0x66FDBB0` | Vtable for unknown algorithm IDs: every operation fails | Confirmed | F51 |
| `0x66FDB10` | Algorithm `0x10` vtable | Confirmed | F53 |
| `0x674B040` | Algorithm `0x10` mode 1 engine vtable | Confirmed | F53 |

## Archive vtable

Archive object vtable at RVA `0x62FD480`.

| Slot | RVA | Role | Confidence |
|---|---|---|---|
| `+0x28` | `0x28CD2E0` | Open by path: row payload offset as base, own handle selected by the row's read source, -1 if unresolved | Confirmed |
| `+0x30` | `0x2758940` | Open entry, variant with an extra argument | Probable |
| `+0x60` | `0x28CD360` | Positional raw read: 32-bit clamp to file object `+0x28`, adds `+0x20`, forwards to the device | Confirmed |
| `+0x80` | `0x28CD3B0` | Seek | Confirmed |
| `+0x90` | `0x503F490` | Release handle. Returns 0 without action | Confirmed |
| `+0x108` | `0x28CD580` | Fetch an entry field or size by ID | Probable |
| `+0x120` | `0x28CD5B0` | Substring lookup | Confirmed |
| `+0x168` | `0x5305860` | Path exists, through the resolver | Confirmed |
| `+0x1A0` | `0x28CDA50` | Batch path resolution | Confirmed |
| `+0x1B0` | `0x28C6B20` | Batch open | Confirmed |
| `+0x1D0` | `0x4870` | Archive-backed device test, returns 1 | Confirmed |
| `+0x1D8` | `0x528F750` | Archive version, returns 9 | Confirmed |
| `+0x1E0` | `0x6151A0` | Parent archive, returns the object itself | Confirmed |
| `+0x298` | `0x56F130` | Row lookup by 64-bit name hash | Confirmed |
| `+0x2A0` | `0x56EC70` | Row lookup by 32-bit key | Confirmed |
| `+0x2A8` | `0x5305880` | Path to row resolver | Confirmed |
| `+0x2B0` | `0x5305EE0` | 32-bit key of a row | Confirmed |
| `+0x2B8` | `0x5520AC0` | Name hash of a row | Confirmed |
| `+0x2C0` | `0x5305ED0` | Type ID of a row | Confirmed |
| `+0x2E0` | `0x1330AD0` | Stored size | Confirmed |
| `+0x2E8` | `0x1331670` | Logical size | Confirmed |
| `+0x2F0` | `0x4F885C0` | Compression mode is nonzero | Confirmed |
| `+0x2F8` | `0xF62E0` | Compression mode | Confirmed |
| `+0x398` | `0x28CDFC0` | Mode-0 metadata read | Confirmed |
| `+0x3A0` | `0xFC2530` | Metadata laid out: header pointer `+0x30` nonzero | Confirmed |
| `+0x3A8` | `0xFA87E0` | Lays out the view over buffer `+0x18` in mode 0 and runs validation. Completes the preloaded construction. A validation failure is not signaled | Confirmed |
| `+0x3B8` | `0x12C5630` | Mount at a prefix | Confirmed |
| `+0x3C0` | `0xA57F70` | Mount prefix setup | Confirmed |
| `+0x3D0` | `0x5305EC0` | Entry ID high half | Confirmed |
| `+0x3E8` | `0x5568B00` | `B` sub-block lookup on the view, through `0x4E6F740` | Confirmed |
| `+0x3F0` | `0x28CE0A0` | Field value getter | Confirmed |
| `+0x3F8` | `0x28CE0B0` | Field pointer getter | Confirmed |
| `+0x400` | `0x28CE0C0` | Column key present, through `0x28CE190` | Confirmed |
| `+0x408` | `0x28CE0E0` | Field key to `{address of the column's first value, descriptor u32@+0x08}`, through `0x28CE110` | Confirmed |

Enumeration search (RPF9-F66). Further inspected slots, none of which iterates rows:

| Slot | RVA | Role | Confidence |
|---|---|---|---|
| `+0x58` | `0x28C6480` | Open, read N bytes, close | Confirmed |
| `+0xF0` | `0x28C6500` | Batch over a path list through slot `+0xF8` | Confirmed |
| `+0x100` | `0x28C6610` | Batch over a path list through slot `+0x108` | Confirmed |
| `+0x128` | `0x28CD920` | Opens a stream from a substring lookup result | Confirmed |
| `+0x190` | `0x28C68E0` | Read loop until N bytes | Confirmed |
| `+0x1A8` | `0x28CDDD0` | Path to descriptor, through the resolver | Confirmed |
| `+0x1C8` | `0x28CDE50` | Path to payload offset, through the resolver | Confirmed |
| `+0x210` | `0x28C6E40` | Allocates a request batch | Confirmed |
| `+0x240` | `0x28C6F40` | Queues a request and starts a worker | Confirmed |

Stub slots:

| Return value | Stub RVA | Slots |
|---|---|---|
| -1 | `0x222F7C0` | `+0x38`, `+0x48`, `+0x118`, `+0x200` |
| 0 | `0x4810` | `+0xA8` to `+0xE0`, `+0x110`, `+0x150`, `+0x170`, `+0x1B8`, `+0x1E8`, `+0x220`, `+0x230`, `+0x250`, `+0x340` |
| 1 | `0x4870` | `+0x1C0`, `+0x1D0` |
| none | `0x4380` | `+0x158`, `+0x160`, `+0x258`, `+0x3D8` |

Slots neither listed here nor above were not inspected.

File object vtable at RVA `0x62FD890`.

| Slot | RVA | Role | Confidence |
|---|---|---|---|
| `+0x00` | `0x56DD500` | Destructor wrapper | Probable |
| `+0x08` | `0xFC2490` | Creates the RPF9 archive object | Confirmed |
| `+0x10` | `0x11A8970` | Creates an RPF9 archive object from a preloaded block, through `0x11A89C0` | Confirmed |
| `+0x18` | `0x9ED970` | Flags bit 0 | Confirmed |
| `+0x20` | `0xE0EE80` | Returns 9 | Confirmed |
| `+0x28` | `0x55B25C0` | Tag at `+0x0C` | Confirmed |
| `+0x30` | `0x80B2C0` | Device at `+0x10` | Confirmed |
| `+0x40` | `0x12D2AC0` | Base offset at `+0x20` | Confirmed |
| `+0x48` | `0x459930` | Size at `+0x28` | Confirmed |
| `+0x50` | `0x1321020` | Value at `+0x30` | Confirmed |
| `+0x58` | `0x28CD1D0` | Sets `+0x30` | Confirmed |

No slot writes the alternate handle array (RPF9-F74). `0x28CE280` fills it (RPF9-F81).

## Object layouts

Archive object, 0x80 bytes:

| Offset | Content | Confidence |
|---|---|---|
| `+0x00` | Vtable | Confirmed |
| `+0x08` | File object pointer. Cleared when the open fails | Confirmed |
| `+0x18` | Primary metadata buffer | Confirmed |
| `+0x20` | Secondary metadata buffer | Confirmed |
| `+0x28` | Metadata view, see below | Confirmed |
| `+0x70` | `u64` folded hash of the mount prefix | Confirmed |
| `+0x78` | `u32` mount prefix length | Confirmed |
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
| `+0x08` | Flags. Bit 0 clear enables the signature check. Set after the first successful open | Confirmed |
| `+0x09` | Bit 0 enables the sorted row lookup. Cleared by the constructor, set by `0x28CE230` | Confirmed |
| `+0x0C` | `u16` tag, high half of entry IDs. `0xFFFF` until registration | Confirmed |
| `+0x0E` | `u16` offset of the file name in the stored path | Probable |
| `+0x10` | Device. Payload reads call its vtable slot `+0x60` | Confirmed |
| `+0x18` | Handle from the device's open method, -1 when the open failed. For a nested archive the parent handle selected by the row's read source. Input to the read-handle selection `0x4F60A90` | Confirmed |
| `+0x20` | Base offset written by the device's open method. Added to every read. For a nested archive the row's payload offset in the parent | Confirmed |
| `+0x28` | Archive size: device slot `+0xF8`, the caller block, or the parent row's logical size | Confirmed |
| `+0x30` | `u64` from device slot `+0x108` or the caller block. Copied into batch resolution and substring lookup records. Probably the modification time | Confirmed (source), Probable (meaning) |
| `+0x38` | Resolved path, 16-byte string object, inline when the sign bit of `+0x47` is set | Confirmed |
| `+0x48` | `u32` capacity of the alternate handle array. Zeroed by the constructor and the destructor | Probable |
| `+0x4C` | `u32` count of alternate handles. Zeroed by the constructor, read by the destructor. Incremented by `0x28CE280` | Confirmed |
| `+0x50` | Alternate handle array, 8-byte handles, -1 for unused. Indexed by `0x4F60A90` without bounds, released and freed by the destructor. Filled by `0x28CE280` from sub-block 3 | Confirmed |
| `+0x58` | Cached archive object | Confirmed (use) |

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
