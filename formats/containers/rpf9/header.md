# RPF9 header

The engine reads a 16-byte header first. The following 48 bytes, up to offset `0x40`, form the schema prefix. Together they are the 0x40-byte header that [metadata.md](metadata.md) builds on.

## 16-byte header

| Offset | Type | Meaning | Confidence |
|---|---|---|---|
| `0x00` | `u32` | Magic `0x52504639`, bytes `39 46 50 52` (`9FPR`) | Confirmed (RPF9-F01) |
| `0x04` | `u32` | Total metadata size: the end of the metadata area | Confirmed (RPF9-F02) |
| `0x08` | `u32` | Size of the primary area, start of the secondary area | Confirmed (RPF9-F02) |
| `0x0C` | `u32` | Unknown | Unknown (RPF9-F03) |

`hdr[0x0C]` is not read on any traced path. It is not bounded by `hdr[0x04]`, so it is not an offset inside the metadata.

## Schema prefix

The loader reads these fields directly. They are stored in plain form (RPF9-F04). The *Observed* column lists values seen in real archives. They are not format limits.

| Offset | Type | Name | Meaning | Observed | Confidence |
|---|---|---|---|---|---|
| `0x10` | 8 bytes | | Unknown. Varies per archive. Not a size or timestamp | | Unknown |
| `0x18` | `u16` | | Unknown | | Unknown |
| `0x1A` | `u16` | `A` | Number of 8-byte records in the `A` table, an index into the `B` block | 4 | Confirmed (RPF9-F39) |
| `0x1C` | `u32` | `B` | Size of the `B` block in bytes | `0x150` | Confirmed (size). Content unknown |
| `0x20` | `u16` | `C` | Column count | 3 to 7 | Confirmed (RPF9-F08) |
| `0x22` | `u16` | `D` | Columns stored in the secondary area | 1 | Confirmed (RPF9-F10) |
| `0x24` | `u32` | `E` | Row (entry) count | 2 to 699 | Confirmed (RPF9-F13) |
| `0x28` | `u32` | | Unknown | | Unknown |
| `0x2C` | `u8` | `F` | Width of a compact cell index in bytes: 1, 2 or 4 | 1 or 2 | Confirmed (RPF9-F11) |
| `0x2D` | `u8` | `G` | Bit 0 selects 16-byte region alignment. Other bits unknown | | Confirmed (bit 0) |
| `0x2E` | `u8` | | Cryptographic selector, see [cryptography/rpf9](../../../cryptography/rpf9/README.md#selection) | 9 | Confirmed (RPF9-F24) |
| `0x2F` | `u8` | | Unknown | | Unknown |
| `0x30` | `u32` | | Length of the `B` block trailer left out of the cipher span | `0x10` | Confirmed (RPF9-F26) |
| `0x34` | 12 bytes | | Unknown | | Unknown |

The 8 bytes at `0x18` hold the same value in all observed archives. This fits the constant `A` and `B` values inside them.

## Read modes

The header reader takes a mode from its caller (RPF9-F02):

1. Read 16 bytes at the archive base. Fail unless exactly 16 bytes arrive.
2. Fail unless the magic matches.
3. Mode 0: allocate `hdr[0x04]` bytes, copy the header in, and read the rest from `0x10`. The buffer then holds the whole metadata area.
4. Mode 1: allocate `hdr[0x08]` bytes and fill them the same way. If `hdr[0x04] != hdr[0x08]`, read `hdr[0x04] - hdr[0x08]` bytes from `hdr[0x08]` into a second buffer.

Mode 1 keeps the primary and secondary areas in separate buffers. Which callers use which mode is not traced beyond the two direct callers.

A caller can also pass in a header that is already in memory. The magic is checked there as well.

## Validation

Known checks before an archive is accepted:

- exact 16-byte header read,
- magic,
- the validation chain run after layout, which includes the cryptographic pass and rejects the archive on failure (RPF9-F23).

Of the other validation steps, only step 3 is partly known. It looks up `B` sub-block 1 through the `A` table (RPF9-F39). Steps 2 and 4 are not analyzed. No bounds checks on the prefix counts have been documented.

A reader SHOULD at least require `0x40 <= hdr[0x08] <= hdr[0x04] <= file size`. This is a sanity rule consistent with observed archives, not a check found in the engine.
