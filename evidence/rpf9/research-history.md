# RPF9 research history

Interpretations that were once used for RPF9 and later corrected. The current model is in the [specification](../../formats/containers/rpf9/README.md).

## Metadata thought to be opaque

**Old assumption.** Everything after the 16-byte header was encrypted. Tools could use only the magic and the metadata size, and had to recover payloads by scanning for zlib streams.

**Correction.** The loader reads bytes `0x10..0x3F` directly as counts and flags and computes region offsets from them. Only selected spans go through the cipher (RPF9-F04, RPF9-F26).

## Entry records were column descriptors

**Old assumption.** The `C` records of 24 bytes were file entries, and `C` was the entry count.

**Correction.** The loader never reads these records at fixed field offsets. A field is fetched by a hashed key, and the key search compares the first 8 bytes of each record. The records are column descriptors and `C` is the column count. The entry count is `E` (RPF9-F08, RPF9-F13).

## Cells hold dictionary indices

**Old assumption.** The cell regions held the field values, and `F` was the value width.

**Correction.** A cell holds an `F`-byte index into the column's value pool, with all-ones as null. The value width comes from descriptor `+0x10`. This is how a one-byte cell can refer to a 16-byte value (RPF9-F09, RPF9-F11, RPF9-F12).

## Row-major addressing

**Old assumption.** Each column's cells were stored contiguously, column-major.

**Correction.** The cell reader computes `row * stride + column` within each store. The stride is `C - D` for the primary store and `D` for the secondary store (RPF9-F10, RPF9-F11).

## Per-column value pools

**Old assumption.** The bytes between the primary cells and `hdr[0x08]` had no known consumer.

**Correction.** They are the primary value pool. The secondary area ends with a second pool. The value pointer adds the descriptor's column base offset to the pool start (RPF9-F12).

## Entry ID tag

**Old assumption.** The high 16 bits of an entry ID were a computed section index.

**Correction.** The getter returns the `u16` stored at file object `+0x0C`. It is the index of the file object's slot in a global registry, assigned when the file object is created (RPF9-F15, RPF9-F64).
## Names

**Old assumption.** Names were rebuilt by the engine, and the hashes could be compared with the name hashes of earlier RPF versions.

**Correction.** A row stores a 64-bit hash of its path. The hash function is RPF9-specific and is described in the specification (RPF9-F18, RPF9-F56).

## Names resolved in reverse

**Old assumption.** The engine turned each row's hash into a name through the runtime dictionary, rebuilt `name.extension` and matched the requested path against it with a substring search. Without the dictionary nothing could be opened.

**Correction.** Opening by path is forward hashing. The resolver strips the mount prefix, hashes the stem and searches the rows by hash and type ID (RPF9-F55). The dictionary is a separate facility that is not filled from archives (RPF9-F60). The substring lookup does exist, but it searches the dictionary string, never reads its rebuilt `name.extension` buffer, and returns the first match in row order (RPF9-F20).

## Fallback name path

**Old assumption.** Key `0xB7076B6245D35FB5` was an unexplained gate for a fallback name lookup.

**Correction.** It is the 32-bit key of rows whose type uses the 32-bit class. Every type uses exactly one of the two classes (RPF9-F57, RPF9-F59).

## Linear row scan only

**Old assumption.** All row lookups scanned the rows linearly. No sorted index existed.

**Correction.** The resolver's row lookups use a binary search when the archive's sorted flag is set. Only the substring lookup is always linear (RPF9-F58).

## Child enumeration

**Old assumption.** `0x28CDA50` enumerated an archive's children from an array of entry IDs.

**Correction.** It resolves an array of caller-supplied path strings. No native enumeration of all rows was found (RPF9-F21).

## Size columns were location records

**Old assumption.** Keys `0xBA18…`, `0x33F7…` and `0x4EAA…` were three size columns: a resource size and two plain sizes masked to 44 and 48 bits. The resource formula was `(w0 & 0xFFFFFFF0) + (w1 & 0x7FFFFFF0)`.

**Correction.** The three keys hold alternative layouts of one location record. Each layout has the payload offset, stored size, logical size, type ID and compression mode. The 44- and 48-bit values are fields at `+0x10` and `+0x08` inside the record, not the whole value. The resource formula has the masks the other way round: `(w1 & 0xFFFFFFF0) + (w0 & 0x7FFFFFF0)` (RPF9-F16, RPF9-F32).

## Stream read was a seek

**Old assumption.** `0x28CD3B0` was the stream reader and read payloads in 4 KiB blocks through a low-level block read at `0x314330`.

**Correction.** `0x28CD3B0` is a seek. It decodes and discards up to 4 KiB at a time only when a compressed stream seeks forward. `0x314330` is the read dispatcher (RPF9-F34, RPF9-F37).

## Enumeration base offset

**Old assumption.** The descriptor written by `0x28CDA50` held the device base offset at `+0x18`.

**Correction.** It holds the `u64` at file object `+0x30`. Payload reads add file object `+0x20` (RPF9-F21, RPF9-F33).

## Namespace column

**Old assumption.** Each row stored its name namespace in a column.

**Correction.** The namespace comes from a table in the executable, indexed by the row's type ID (RPF9-F31).

## Validation step 3 was a lookup

**Old assumption.** The validation chain had five steps. Steps 2 to 4 had unknown roles, and step 3 looked up `B` sub-block 1.

**Correction.** Step 2 is a conditional signature check. The third operation is a lookup of the per-archive cipher descriptor in sub-block 1. If that sub-block is missing, the chain ends with success and steps 4 and 5 do not run. Step 4 processes the primary area (RPF9-F42, RPF9-F43, RPF9-F45).

## Primary regions outside the cipher spans

**Old assumption.** The column descriptors, primary index store and primary value pool lay outside every processed span, so their stored state was open with no code-level lead.

**Correction.** They lie in the step 4 span. In the inspected archives none of the known field keys occurs in the stored primary area, so those archives probably store it transformed (RPF9-F45, RPF9-F48).

## B trailer as authentication tag

**Old assumption.** The `B` trailer, left out of step 1, was a plausible authentication tag.

**Correction.** The trailer starts the step 4 span and is part of the signed message. Nothing in the code supports the tag reading any more. Its role is unknown (RPF9-F45).

## Authenticated decryption was CBC decryption

**Old assumption.** The span runner calls `update` in place and checks a boolean `final`, so the metadata cipher was probably authenticated decryption with a 16-byte tag.

**Correction.** Algorithm `0x10`, which the observed static descriptor selects, is CBC decryption. Its `final` resets the IV and always succeeds. The cipher therefore authenticates nothing. The separate signature check remains the chain's only integrity check, and it is conditional (RPF9-F43, RPF9-F44, RPF9-F53).

## Initializer label

**Old assumption.** `0x536A70` was the table that maps cipher types to algorithm IDs.

**Correction.** `0x536A70` is the initializer. It calls the table lookup `0x536AC0` and then the factory and key setup `0x613880` (RPF9-F25).

## Mount prefix from the archive path

**Old assumption.** An archive's resolver prefix always came from the directory of its own resolved path, so it was a property of the archive and never a mount point supplied by a caller.

**Correction.** The directory-derived prefix is only the default set during construction. Mounting the archive through its mount method replaces it with the caller's mount prefix. Mounted archives therefore resolve entries under the mount prefix (RPF9-F61, RPF9-F69).

## Preloaded blocks from batch resolution

**Old assumption.** A parent's batch path resolution built the preload blocks for nested archives, which were then mounted in bulk from the parent's metadata copies. This rested on matching record layouts.

**Correction.** The traced caller of the preloaded path is a batch loader that takes its blocks from a global index. What fills that index is unknown. Whether the parent copy is used on this path was not established (RPF9-F76).

## Header field letters

Some earlier notes used "A" and "B" for `hdr[0x04]` and `hdr[0x08]`. Those letters name the prefix fields at `0x1A` and `0x1C`. Header fields are now referred to by offset.

## Open

- Descriptor bytes `+0x08` and `+0x12`.
- What selects location layout F over A, and whether real rows carry more than one layout.
- The content of the `B` sub-blocks.
- The stored state of the secondary area and of archives other than the inspected ones. One earlier note called the primary regions "post-transform" from the order of initialization alone. The step 4 span and the archive scan now support that for the inspected archives (RPF9-F28, RPF9-F48).
- The signature algorithm, cipher algorithms 1, 2, `0x11` and `0x12`, AES equivalence of algorithm `0x10`, and the role of the `B` trailer.
- The payload transform algorithm and key source.
- Directory structure outside the traced paths, and enumeration in the device layer or above.
- CityHash32 identity of the fingerprint hash, the concrete startup fingerprint and the contents of `B` sub-block 9 in real archives.
- Path normalization, the physical device implementation, and the mount prefixes the game uses.
- Whether any nested archive is stored compressed or transformed, which the native nested read path cannot read.
