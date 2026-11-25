# RPF9 columnar schema

The RPF9 table of contents is a table with `E` rows and `C` columns. It is dictionary-encoded. A cell holds a small index, and the index selects a value from the column's value pool. Reading one field of one entry takes three steps:

1. Field key to column index, through the column descriptors.
2. Row and column to a compact index, through an index store.
3. Compact index to a value, through the column's value pool.

Region positions are in [metadata.md](metadata.md).

## Column descriptor

`C` descriptors of 24 bytes each.

| Offset | Type | Meaning | Confidence |
|---|---|---|---|
| `+0x00` | `u64` | Field key: a hash identifying the field | Confirmed (RPF9-F08) |
| `+0x08` | `u32` | Returned with the column's first value pointer by archive vtable `+0x408`. Meaning unknown | Confirmed (read, RPF9-F82), Unknown (meaning) |
| `+0x0C` | `u32` | Column base offset in the value pool | Confirmed (RPF9-F09) |
| `+0x10` | `u16` | Element width in bytes | Confirmed (RPF9-F09) |
| `+0x12` | 6 bytes | Unknown | Unknown |

The hash function behind the field keys is unknown. The key search reads only `+0x00`, and the value pointer reads only `+0x0C` and `+0x10`.

One archive method reads `+0x08` (RPF9-F82). Given a field key, it returns the address of the column's first value and the `u32` at `+0x08`. That pairing would fit a count of the column's values, but no caller of the method was found, so the meaning stays Unknown.

No traced accessor, layout routine or validation step reads `+0x12`. The validation chain signs and processes the whole descriptor table as opaque bytes (RPF9-F40). A reader SHOULD keep both fields as raw values.

The descriptor table as stored is probably not plain in the inspected archives. See [metadata.md](metadata.md#on-disk-bytes-and-the-metadata-view).

## Step 1: field key to column

The engine scans the descriptors in order and compares `+0x00` with the requested key. The first match gives the column index. No match gives `0xFFFF`, and the field accessor returns "absent" without failing (RPF9-F08).

## Step 2: row and column to compact index

The columns are split by `D` (RPF9-F10):

| Columns | Store | Stride | Local column |
|---|---|---|---|
| `0 .. C-D-1` | Primary index store | `C - D` | `column` |
| `C-D .. C-1` | Secondary index store | `D` | `column - (C - D)` |

Within a store, indices are row-major (RPF9-F11):

```text
compactIndexOffset = rowIndex * storeStride + localColumnIndex
```

The offset counts elements of `F` bytes. The engine loads one `F`-byte element at that position, so the byte offset is `compactIndexOffset * F`. That matches the store sizes `(C - D) * E * F` and `D * E * F`.

`D` is not fixed at 1. In the 1,440-archive sample it takes values 1 to 8, and 374 archives have `D > 1` (RPF9-F131). The secondary area then holds 2 to 8 columns. With the store starting at `align_F(hdr[0x08])`, the `D * E * F` index-store layout is a necessary size fit in all 374, and a direct layout with one fixed width in every secondary column is a necessary size fit in 140. Size alone decides no archive, so the models are not separated here (RPF9-F132).

| `F` | Load | Null sentinel |
|---|---|---|
| 1 | `u8` | `0xFF` |
| 2 | `u16` | `0xFFFF` |
| 4 | `u32` | none |

A sentinel means the row has no value in that column. The cell reader then returns `0xFFFFFFFF`. For `F = 4` the code has no sentinel test, so no null value is established for that width. `F = 4` has not been observed in archives.

`F` is the width of the index only. It says nothing about the width of the value.

## Step 3: compact index to value

```text
valuePointer = poolBase + columnBaseOffset + elementWidth * compactIndex
```

- `poolBase` is the primary value pool for primary columns and the secondary value pool for secondary columns.
- `columnBaseOffset` is descriptor `+0x0C`.
- `elementWidth` is descriptor `+0x10`.

(RPF9-F12)

Each column has its own run of fixed-width elements in its area's pool. A one-byte index can select a 16-byte value, because the width belongs to the pool element. Rows that share a value can share one pool element. No deduplication rule has been checked against data.

The value pointer is not checked against the pool. A compact index that is not the null sentinel is multiplied by the element width and added without comparison to any count, so an out-of-range index points past the column's elements. This holds for the traced accessor paths (RPF9-F40). The validation chain does not check counts, index values or pool bounds either (RPF9-F47). An archive that passes validation can therefore hold out-of-range indices, and the traced code would follow them. Code outside those paths was not searched.

The engine exposes two accessors on top of this. One returns whether the field is present. The other returns the value pointer, and callers read typed fields from it (RPF9-F14).

## Known columns

Field keys seen at engine use sites (RPF9-F17). Each meaning comes from how the callers use the value.

| Field key | Value | Meaning | Confidence | Finding |
|---|---|---|---|---|
| `0x73BCB72DCE74F11F` | `u64` | Name hash of 64-bit-class rows, see [names.md](names.md#path-to-row) | Confirmed | F30, F55 |
| `0xBA180AFB232D1B4B` | Location record R | See [entries.md](entries.md#location-records) | Confirmed (layout) | F32 |
| `0x33F70DFAF2C50989` | Location record F | See [entries.md](entries.md#location-records) | Confirmed (layout) | F32 |
| `0x4EAA16DD829995BC` | Location record A | See [entries.md](entries.md#location-records) | Confirmed (layout) | F32 |
| `0xE0C12D7A5D4884C5` | Chunk table, self-relative | See [payloads.md](payloads.md#chunk-table) | Confirmed (layout) | F36 |
| `0x286030A358A789FB` | Presence only | Routes stored bytes through the payload transform, see [payloads.md](payloads.md#payload-transform) | Confirmed (routing) | F38 |
| `0xC26722D233648AE7` | `u32` self-relative offset | Start of an RPF9 metadata area: 16-byte header, total size at `+4`. Batch path resolution copies its 16 header bytes. The preloaded construction path copies the whole area as a nested archive's metadata, see [names.md](names.md#preloaded-construction) | Confirmed (use), Probable (copy of the nested archive's stored metadata) | F21, F75 |
| `0xCBB68FF7B7078DB7` | `u32`, `0xFFFFFFFF` when absent | Read-source index. `0xFFFFFFFF` selects the main handle, other values the companion file of the same index in `B` sub-block 3, unchecked. See [payloads.md](payloads.md#read-source) | Confirmed | F41, F73, F81 |
| `0xB7076B6245D35FB5` | `u32` | 32-bit key of 32-bit-class rows, 0 on 64-bit-class rows in sorted archives, see [names.md](names.md#32-bit-key) | Confirmed (use), Probable (stored value is `joaat` of the stem) | F31, F57, F58 |

The type ID and compression mode are fields inside the location records, not columns of their own. The namespace is not stored in the archive.

## Worked example

Synthetic values: `C = 4`, `D = 1`, `E = 3`, `F = 1`. Column 1 has base offset `0x20` and element width 8. Find column 1 of row 2.

1. Column 1 is below `C - D = 3`, so it is primary. Stride 3, local column 1.
2. Index offset `2 * 3 + 1 = 7`, byte offset `7 * F = 7` in the primary index store. Suppose the byte there is `0x01`.
3. Value pointer `primaryPool + 0x20 + 8 * 1 = primaryPool + 0x28`. Read 8 bytes there.

If the byte at offset 7 were `0xFF`, row 2 would have no value in column 1.
