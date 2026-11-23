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
| `+0x08` | 4 bytes | Unknown | Unknown |
| `+0x0C` | `u32` | Column base offset in the value pool | Confirmed (RPF9-F09) |
| `+0x10` | `u16` | Element width in bytes | Confirmed (RPF9-F09) |
| `+0x12` | 6 bytes | Unknown | Unknown |

The hash function behind the field keys is unknown.

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

The engine exposes two accessors on top of this. One returns whether the field is present. The other returns the value pointer, and callers read typed fields from it (RPF9-F14).

## Known columns

Field keys seen at engine use sites (RPF9-F17). Meanings come from how the caller uses the value.

| Field key | Element use | Probable meaning | Confidence |
|---|---|---|---|
| `0xBA180AFB232D1B4B` | Two 32-bit words, masked and added | Resource size flags, see [entries.md](entries.md#sizes) | Probable |
| `0x33F70DFAF2C50989` | Masked to 44 bits | Size of a non-resource entry | Probable |
| `0x4EAA16DD829995BC` | Masked to 48 bits | Alternate size | Probable |
| `0xE0C12D7A5D4884C5` | Read by the stream reader | Stream flags or state | Probable |
| `0x286030A358A789FB` | Read by the stream reader | Stream flags or state | Probable |
| `0xC26722D233648AE7` | 16-byte value, read during enumeration | Unknown | Speculative |

The keys of the name-hash, namespace and extension-type columns used by path lookup are not recorded. Neither are the payload offset and compression columns.

## Worked example

Synthetic values: `C = 4`, `D = 1`, `E = 3`, `F = 1`. Column 1 has base offset `0x20` and element width 8. Find column 1 of row 2.

1. Column 1 is below `C - D = 3`, so it is primary. Stride 3, local column 1.
2. Index offset `2 * 3 + 1 = 7`, byte offset `7 * F = 7` in the primary index store. Suppose the byte there is `0x01`.
3. Value pointer `primaryPool + 0x20 + 8 * 1 = primaryPool + 0x28`. Read 8 bytes there.

If the byte at offset 7 were `0xFF`, row 2 would have no value in column 1.
