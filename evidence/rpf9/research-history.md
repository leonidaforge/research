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

**Correction.** The getter returns the `u16` stored at file object `+0x0C`. It is a stored tag. Where its value comes from is still open (RPF9-F15).

## Names

**Old assumption.** Names were rebuilt by the engine, and the hashes could be compared with the name hashes of earlier RPF versions.

**Correction.** A row stores a 64-bit hash, which a runtime dictionary resolves to a string. No hash function has been identified (RPF9-F18).

## Header field letters

Some earlier notes used "A" and "B" for `hdr[0x04]` and `hdr[0x08]`. Those letters name the prefix fields at `0x1A` and `0x1C`. Header fields are now referred to by offset.

## Open

- Descriptor bytes `+0x08` and `+0x12`.
- Column identities beyond the size columns.
- Roles of the `A` table and the `B` block.
- Whether the descriptors, primary cells and primary pool are stored transformed. One earlier note called them "post-transform". That was inferred from the order of initialization, not from cipher span coverage (RPF9-F28).
- Directory structure, payload offsets and the decompression path.
