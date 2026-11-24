# RPF9 metadata layout

The metadata area runs from offset 0 to `hdr[0x04]`. It has two parts. The primary area ends at `hdr[0x08]` and the secondary area ends at `hdr[0x04]`. Field names `A` to `G` refer to the [header](header.md#schema-prefix).

## Primary area

The engine derives each region from the prefix counts (RPF9-F05). Region starts are rounded up from the end of the previous region. The layout builder rounds memory addresses, not file offsets:

| Region start                              | `G` bit 0 set | `G` bit 0 clear |
| ----------------------------------------- | ------------- | --------------- |
| `A` table, after the 0x40-byte header     | 16            | 4               |
| `B` block                                 | 16            | 8               |
| Column descriptors                        | 16            | 8               |
| Primary index store                       | `F`           | `F`             |
| Primary value pool, after the index store | 8             | 8               |

The index store size `(C - D) * E * F` is computed as a 32-bit product. The builder also computes a 16-byte-aligned address after the pool start, but does not store it in the view (RPF9-F05). These offsets equal file offsets only when the metadata buffer starts on a 16-byte boundary. The buffer's alignment is not traced. In observed archives the primary index store starts at the next 8-byte boundary after the descriptors, for example `0x1F8` when `C = 3`. All inspected archives have `G` bit 0 set.

The cryptographic spans compute the `B` block and descriptor starts with their own formula, which can disagree with this table for some values of `A`, `B` and `G` (see [cryptography/rpf9](../../../cryptography/rpf9/README.md#processed-spans), RPF9-F49).

| Order | Region              | Size              | Role                                                                    | Confidence            |
| ----- | ------------------- | ----------------- | ----------------------------------------------------------------------- | --------------------- |
| 1     | Header and prefix   | `0x40`            | Counts and flags                                                        | Confirmed             |
| 2     | `A` table           | `A * 8`           | Index of sub-blocks in the `B` block, see [below](#a-table-and-b-block) | Confirmed (structure) |
| 3     | `B` block           | `B`               | Sub-blocks addressed through the `A` table                              | Unknown content       |
| 4     | Column descriptors  | `C * 24`          | One descriptor per column, see [schema.md](schema.md#column-descriptor) | Confirmed             |
| 5     | Primary index store | `(C - D) * E * F` | Compact indices for columns `0 .. C-D-1`                                | Confirmed             |
| 6     | Primary value pool  | to `hdr[0x08]`    | Values of the primary columns                                           | Confirmed             |

The primary value pool has no size field. It fills the space up to `hdr[0x08]`.

With the observed `A = 4` and `B = 0x150`, the descriptor table starts at `0x1B0`.

### A table and B block

Each `A` record is 8 bytes (RPF9-F39):

| Offset  | Type    | Meaning                                                 |
| ------- | ------- | ------------------------------------------------------- |
| `+0x00` | `u16`   | Sub-block ID                                            |
| `+0x02` | 2 bytes | Not read on the traced path                             |
| `+0x04` | `u32`   | Offset of the sub-block from the start of the `B` block |

A lookup scans the `A` records in order and returns `B + offset` for the first matching ID, or nothing. Neither the lookup nor any traced caller checks that the offset lies inside the `B` block. Neither region is read by the cell accessors.

Sub-block IDs used by the engine (RPF9-F39, RPF9-F43):

| ID  | Content                                             | Used by                                                                                                                                     | Confidence                   |
| --- | --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------- |
| 1   | Per-archive cipher descriptor                       | Steps 4 and 5 of the [validation chain](../../../cryptography/rpf9/README.md#validation-chain). Optional: without it those steps do not run | Confirmed (use)              |
| 2   | Key identifier and 256-byte signature               | Signature check, if sub-block 6 is missing                                                                                                  | Confirmed (layout)           |
| 3   | List of companion files, see [below](#sub-block-3)  | Opened after validation as the file object's alternate read sources. Optional                                                               | Confirmed (RPF9-F81)         |
| 6   | Message type, key identifier and 256-byte signature | Signature check, first choice                                                                                                               | Confirmed (layout)           |
| 9   | `u8` count `n`, then `n` `u8` type IDs              | Type classification fingerprint, when header `u8@0x2D` bit 3 is set, see [names.md](names.md#sorted-flag)                                   | Confirmed (layout, RPF9-F63) |

#### Sub-block 3

| Offset  | Type              | Meaning           | Confidence |
| ------- | ----------------- | ----------------- | ---------- |
| `+0x00` | `u32`             | Record count `n`  | Confirmed  |
| `+0x04` | 4 bytes           | Not read          | Unknown    |
| `+0x08` | `n` × 0x108 bytes | Companion records | Confirmed  |

Each record (RPF9-F81):

| Offset   | Type                          | Meaning                                                        |
| -------- | ----------------------------- | -------------------------------------------------------------- |
| `+0x000` | `char[0x100]`, NUL-terminated | File name, relative to the directory of the archive's own path |
| `+0x100` | `u64`                         | Identifier the companion's header must carry                   |

After the first successful validation of a file object, the engine processes the records in order:

1. It builds `<directory of the archive path>/<name>`, at most 255 bytes, and removes `/../` components.
2. It opens that path through the archive's device. If the open fails, it stops and ignores the remaining records.
3. It reads the companion's first 16 bytes. The first 8 bytes MUST be `00 00 00 39 56 46 50 52`, the next 8 bytes MUST equal the record's identifier. That magic differs from the RPF9 header magic. Nothing else in the companion is checked.
4. It appends the handle to the file object's alternate handle array, or -1 if the check failed.

Record `i` therefore becomes the source that [read-source index](payloads.md#read-source) `i` selects.

The open passes the archive's own base offset field as the output for the companion's base (RPF9-F83, RPF9-F84):

- The physical file device writes 0 there and opens a new read-only file handle. A root archive opened through that device already has base 0, so nothing changes.
- The archive device writes the companion row's payload offset there and returns the parent's handle. For a nested archive with sub-block 3, every companion path that resolves in the parent replaces the nested archive's base, and nothing restores it. This happens after the nested archive's metadata was read, so its later payload reads use the companion's base. A reader MUST NOT reproduce this.
- An open that fails on the archive device writes nothing.

Only the companion check reads companion bytes outside entry payloads. No other parser for the companion format exists in the executable.

Both regions lie inside the spans that validation step 1 processes (see [cryptography/rpf9](../../../cryptography/rpf9/README.md#processed-spans)). The lookups run after step 1, so this layout describes the bytes after processing. In the inspected archives the stored bytes are ciphertext, step 1 decryption produces this layout, and the metadata signature over it verifies (RPF9-F100, RPF9-F102).

## Secondary area

| Order | Region                | Size           | Role                                     | Confidence           |
| ----- | --------------------- | -------------- | ---------------------------------------- | -------------------- |
| 1     | Secondary index store | `D * E * F`    | Compact indices for columns `C-D .. C-1` | Confirmed (RPF9-F06) |
| 2     | Secondary value pool  | to `hdr[0x04]` | Values of the secondary columns          | Confirmed            |

The secondary index store starts at `hdr[0x08]` rounded up to `F` bytes. The secondary value pool starts at the end of the store, `D * E * F` as a 32-bit product, rounded up to 8 bytes (RPF9-F06). With read mode 1 the secondary area is a separate buffer, and the rounding applies to that buffer's address.

## Diagram

```text
0x00   +----------------------------+
       | header + prefix (0x40)     |
       +----------------------------+
       | A table (A * 8)            |
       | B block (B)                |
       | column descriptors (C * 24)|
       | primary index store        |  (C-D) * E * F
       | primary value pool         |
hdr[0x08] +-------------------------+
       | secondary index store      |  D * E * F
       | secondary value pool       |
hdr[0x04] +-------------------------+
       payload data
```

## Consistency with archive data

The region arithmetic matches the plain header fields of real archives. The primary regions end before `hdr[0x08]`, the secondary index store fits before `hdr[0x04]`, and both pools have non-negative size. Observed values are `C` 3 to 7, `D` 1, `E` 2 to 699 and `F` 1 or 2. `F` is 1 for small row counts, up to 22 observed, and 2 for large ones, from 418 observed. These are observations, not format limits.

This consistency covers offsets and sizes only. It does not confirm the decoded values.

## On-disk bytes and the metadata view

After the header read, the engine lays out a temporary view over the metadata buffers, runs the validation chain on it, and then stores one pointer per region in a metadata view inside the archive object (RPF9-F07). Both views point into the same buffers. Every lookup goes through the archive's view and sees the bytes as the chain left them.

| View slot | Region                |
| --------- | --------------------- |
| `+0x08`   | Header and prefix     |
| `+0x10`   | `A` table             |
| `+0x18`   | `B` block             |
| `+0x20`   | Column descriptors    |
| `+0x28`   | Primary index store   |
| `+0x30`   | Primary value pool    |
| `+0x38`   | Secondary index store |
| `+0x40`   | Secondary value pool  |

The chain processes these regions in place (see [cryptography/rpf9](../../../cryptography/rpf9/README.md#processed-spans)):

| Region                                                                   | Processed by | Condition               |
| ------------------------------------------------------------------------ | ------------ | ----------------------- |
| `A` table, `B` block                                                     | Step 1       | `hdr[0x2E] != 0`        |
| `B` trailer, column descriptors, primary index store, primary value pool | Step 4       | `B` sub-block 1 present |
| Secondary area                                                           | Step 5       | `B` sub-block 1 present |

What lookups read is the post-validation state. This is confirmed (RPF9-F28).

For the primary area, archive data narrows the question. In the inspected sample of archives none of the known field keys occurs anywhere in the stored bytes, although the engine must find one in every archive. Those archives store the primary area transformed. Step 4 runs with a non-no-op `B` sub-block 1 descriptor, the decoded metadata is consistent, and its signature verifies (RPF9-F48, RPF9-F100, RPF9-F102). How many bytes change is not established. For other archives and other regions this is not established.

A parser MUST NOT assume that the stored descriptors, index stores or value pools are plain. It MUST NOT assume that a stored region is transformed unless the region lies in a processed span that runs for that archive.
