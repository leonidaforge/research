# RPF9 metadata layout

The metadata area runs from offset 0 to `hdr[0x04]`. It has two parts. The primary area ends at `hdr[0x08]` and the secondary area ends at `hdr[0x04]`. Field names `A` to `G` refer to the [header](header.md#schema-prefix).

## Primary area

The engine derives each region from the prefix counts (RPF9-F05). Region starts are rounded up from the end of the previous region. The code rounds to 16 bytes when `G` bit 0 is set and to 4 or 8 bytes otherwise. Which rounding applies to which region is not established from code. In observed archives, the primary index store starts at the next 8-byte boundary after the descriptors, for example `0x1F8` when `C = 3`. The primary value pool starts on a 16-byte boundary.

| Order | Region | Size | Role | Confidence |
|---|---|---|---|---|
| 1 | Header and prefix | `0x40` | Counts and flags | Confirmed |
| 2 | `A` table | `A * 8` | Index of sub-blocks in the `B` block, see [below](#a-table-and-b-block) | Confirmed (structure) |
| 3 | `B` block | `B` | Sub-blocks addressed through the `A` table | Unknown content |
| 4 | Column descriptors | `C * 24` | One descriptor per column, see [schema.md](schema.md#column-descriptor) | Confirmed |
| 5 | Primary index store | `(C - D) * E * F` | Compact indices for columns `0 .. C-D-1` | Confirmed |
| 6 | Primary value pool | to `hdr[0x08]` | Values of the primary columns | Confirmed |

The primary value pool has no size field. It fills the space up to `hdr[0x08]`.

With the observed `A = 4` and `B = 0x150`, the descriptor table starts at `0x1B0`.

### A table and B block

Each `A` record is 8 bytes (RPF9-F39):

| Offset | Type | Meaning |
|---|---|---|
| `+0x00` | `u16` | Sub-block ID |
| `+0x02` | 2 bytes | Not read on the traced path |
| `+0x04` | `u32` | Offset of the sub-block from the start of the `B` block |

A lookup scans the `A` records in order and returns `B + offset` for the first matching ID, or nothing. Validation step 3 asks for ID 1. What the sub-blocks contain, and what step 3 does with sub-block 1, is unknown. Neither region is read by the cell accessors.

Both regions lie inside the spans that validation step 1 processes (see [cryptography/rpf9](../../../cryptography/rpf9/README.md#processed-spans)). Step 3 runs after step 1, so this layout describes the bytes after processing. Whether the bytes on disk have the same layout is not established.

## Secondary area

| Order | Region | Size | Role | Confidence |
|---|---|---|---|---|
| 1 | Secondary index store | `D * E * F` | Compact indices for columns `C-D .. C-1` | Confirmed (RPF9-F06) |
| 2 | Secondary value pool | to `hdr[0x04]` | Values of the secondary columns | Confirmed |

The alignment of the secondary value pool is not established.

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

The engine does not read the regions in place. After the header read, it builds a view descriptor, runs the validation chain, and then stores one pointer per region in a metadata view inside the archive object (RPF9-F07). Every lookup goes through that view.

| View slot | Region |
|---|---|
| `+0x08` | Header and prefix |
| `+0x10` | `A` table |
| `+0x18` | `B` block |
| `+0x20` | Column descriptors |
| `+0x28` | Primary index store |
| `+0x30` | Primary value pool |
| `+0x38` | Secondary index store |
| `+0x40` | Secondary value pool |

The validation chain includes cryptographic processing of the `A` table, the `B` block and the secondary area (see [cryptography/rpf9](../../../cryptography/rpf9/README.md)). The descriptors, the primary index store and the primary value pool are outside the established spans. Two facts follow, and neither settles the question:

- What lookups read is the post-validation view. This is confirmed.
- Whether the bytes on disk differ from that view is not established for those three regions. Their high entropy does not decide it, because field-key hashes and packed values look random as well (RPF9-F28).

A parser MUST NOT assume either that those regions are plain or that they are encrypted.
