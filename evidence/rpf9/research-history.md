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

## Size columns were location records

**Old assumption.** Keys `0xBA18…`, `0x33F7…` and `0x4EAA…` were three size columns: a resource size and two plain sizes masked to 44 and 48 bits. The resource formula was `(w0 & 0xFFFFFFF0) + (w1 & 0x7FFFFFF0)`.

**Correction.** The three keys hold alternative layouts of one location record. Each layout has the payload offset, stored size, logical size, type ID and compression mode. The 44- and 48-bit values are fields at `+0x10` and `+0x08` inside the record, not the whole value. The resource formula has the masks the other way round: `(w1 & 0xFFFFFFF0) + (w0 & 0x7FFFFFF0)` (RPF9-F16, RPF9-F32).

## Stream read was a seek

**Old assumption.** `0x28CD3B0` was the stream reader and read payloads in 4 KiB blocks through a low-level block read at `0x314330`.

**Correction.** `0x28CD3B0` is a seek. It decodes and discards up to 4 KiB at a time only when a compressed stream seeks forward. `0x314330` is the read dispatcher (RPF9-F34, RPF9-F37).

## Enumeration base offset

**Old assumption.** Enumeration descriptor `+0x18` held the device base offset.

**Correction.** It holds the `u64` at file object `+0x30`. Payload reads add file object `+0x20` (RPF9-F21, RPF9-F33).

## Namespace column

**Old assumption.** Each row stored its name namespace in a column.

**Correction.** The namespace comes from a table in the executable, indexed by the row's type ID (RPF9-F31).

## Header field letters

Some earlier notes used "A" and "B" for `hdr[0x04]` and `hdr[0x08]`. Those letters name the prefix fields at `0x1A` and `0x1C`. Header fields are now referred to by offset.

## Open

- Descriptor bytes `+0x08` and `+0x12`.
- What selects location layout F over A, and whether real rows carry more than one layout.
- The content of the `B` sub-blocks.
- Whether the descriptors, primary cells and primary pool are stored transformed. One earlier note called them "post-transform". That was inferred from the order of initialization, not from cipher span coverage (RPF9-F28).
- The payload transform algorithm and key source.
- Directory structure.
