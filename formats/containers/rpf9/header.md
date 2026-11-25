# RPF9 header

The engine reads a 16-byte header first. The following 48 bytes, up to offset `0x40`, form the schema prefix. Together they are the 0x40-byte header that [metadata.md](metadata.md) builds on.

## 16-byte header

| Offset | Type | Meaning | Confidence |
|---|---|---|---|
| `0x00` | `u32` | Magic `0x52504639`, bytes `39 46 50 52` (`9FPR`) | Confirmed (RPF9-F01) |
| `0x04` | `u32` | Total metadata size: the end of the metadata area | Confirmed (RPF9-F02) |
| `0x08` | `u32` | Size of the primary area, start of the secondary area | Confirmed (RPF9-F02) |
| `0x0C` | `u32` | Byte length of the trailing region after the stored payload data | Confirmed from data (RPF9-F129); not read on traced paths (RPF9-F03) |

`hdr[0x0C]` is not read on any traced path, so its role comes from archive data. In every reachable archive `file_size - hdr[0x0C]` is a 16-byte-aligned boundary above the metadata end. Stored payload data ends at that boundary. The length is not an offset inside the metadata.

## Schema prefix

The loader reads these fields directly. They are stored in plain form (RPF9-F04). The *Observed* column lists values seen in real archives. They are not format limits.

| Offset | Type | Name | Meaning | Observed | Confidence |
|---|---|---|---|---|---|
| `0x10` | 8 bytes | | Unknown. Varies per archive. Not a size or timestamp. Neither processed nor signed by the validation chain | | Unknown |
| `0x18` | `u16` | | Unknown | `0x7A00` | Unknown |
| `0x1A` | `u16` | `A` | Number of 8-byte records in the `A` table, an index into the `B` block | 4 to 6 | Confirmed (RPF9-F39) |
| `0x1C` | `u32` | `B` | Size of the `B` block in bytes. Known sub-blocks in [metadata.md](metadata.md#a-table-and-b-block) | `0x150` to `0x2E0` | Confirmed (size) |
| `0x20` | `u16` | `C` | Column count | 3 to 13 | Confirmed (RPF9-F08) |
| `0x22` | `u16` | `D` | Columns stored in the secondary area | 1 to 8 | Confirmed (RPF9-F10, RPF9-F131) |
| `0x24` | `u32` | `E` | Row (entry) count | 1 to 2,896 | Confirmed (RPF9-F13) |
| `0x28` | `u32` | | Type classification fingerprint. The engine enables its sorted row lookup only when this equals its own fingerprint, see [names.md](names.md#sorted-flag) | | Confirmed (use, RPF9-F63), Probable (meaning) |
| `0x2C` | `u8` | `F` | Width of a compact cell index in bytes: 1, 2 or 4 | 1 or 2 | Confirmed (RPF9-F11) |
| `0x2D` | `u8` | `G` | Bit 0 selects 16-byte region alignment. Bit 3 selects the fingerprint from `B` sub-block 9 for the `0x28` comparison. Bits 1, 2 and 4 to 7 unknown | bit 0 set | Confirmed (bits 0 and 3, RPF9-F63) |
| `0x2E` | `u8` | | Cryptographic selector, see [cryptography/rpf9](../../../cryptography/rpf9/README.md#selection) | 9 | Confirmed (RPF9-F24) |
| `0x2F` | `u8` | | Unknown | | Unknown |
| `0x30` | `u32` | | Length of the `B` block trailer. Left out of the step 1 span when `0x2E` bit 0 is set. Start of the step 4 span | `0x10` | Confirmed (RPF9-F26, RPF9-F45) |
| `0x34` | 12 bytes | | Unknown | | Unknown |

The `u16` at `0x18` is `0x7A00` in the sample. The 8 bytes at `0x18` also contain `A` at `0x1A` and `B` at `0x1C`, so the combined value varies with those fields; a set in which `A` and `B` do not change makes the bytes look constant (RPF9-F131).

## Read modes

The header reader takes a mode from its caller (RPF9-F02):

1. Read 16 bytes at the archive base. Fail unless exactly 16 bytes arrive.
2. Fail unless the magic matches.
3. Mode 0: allocate `hdr[0x04]` bytes, copy the header in, and read the rest from `0x10`. The buffer then holds the whole metadata area.
4. Mode 1: allocate `hdr[0x08]` bytes and fill them the same way. If `hdr[0x04] != hdr[0x08]`, read `hdr[0x04] - hdr[0x08]` bytes from `hdr[0x08]` into a second buffer.

Mode 1 keeps the primary and secondary areas in separate buffers. Which callers use which mode is not traced beyond the two direct callers.

A caller can also pass in a header that is already in memory. The magic is checked there as well.

## Trailing region

An archive ends with a region whose byte length is `hdr[0x0C]`. Its start, and therefore the end of stored payload data, is `file_size - hdr[0x0C]`.

A survey of 1,440 archives (22 top-level and 1,418 nested) found no violation of four bounds (RPF9-F129):

- the boundary is 16-byte aligned;
- it lies above the metadata end `hdr[0x04]`;
- it lies below the file size;
- every row's `payload_offset + stored_size` is at or below it.

The observed trailing lengths range from 48 to 178,576 bytes and take 281 distinct values. The content is **undecoded**. The survey compared only lengths, offsets and equality classes; it did not interpret bytes or examine them for text.

Equality between trailers is not determined by the header shape alone (RPF9-F130). Thirty archives of 720 bytes share one header shape and a byte-identical 64-byte trailing region. Among 40 header-shape groups that contain more than one archive, only four groups have a single full-trailer class, each 544 bytes; the other groups differ in at least the first 16 bytes.

## Validation

Known checks before an archive is accepted:

- exact 16-byte header read,
- magic,
- the [validation chain](../../../cryptography/rpf9/README.md#validation-chain): cipher passes, a conditional signature check, and a check that the signature lies inside the `B` block (RPF9-F23, RPF9-F42, RPF9-F43).

The validation chain and the layout builder do not check the prefix counts, region sizes, index stores or `A` offsets against each other or against `hdr[0x08]` and `hdr[0x04]` (RPF9-F47). Code outside those paths was not searched.

A reader SHOULD at least require `0x40 <= hdr[0x08] <= hdr[0x04] <= file_size - hdr[0x0C] < file_size`, with `file_size - hdr[0x0C]` a multiple of 16. It SHOULD also require every row's stored range to end at or below that boundary, and MUST treat the trailing region as opaque. These are sanity rules consistent with observed archives, not checks found in the engine.
