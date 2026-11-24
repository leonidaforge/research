# RPF9 entries

An entry is one row of the [columnar schema](schema.md). The format has no separate entry record. Where an entry's data lives is stored in one of three location record layouts, described below.

## Entry IDs

The engine addresses an entry by a 32-bit ID (RPF9-F15):

```text
entryId = (tag << 16) | rowIndex
```

| Bits | Meaning | Confidence |
|---|---|---|
| 0 to 15 | Row index, `0 .. E-1` | Confirmed |
| 16 to 31 | The `u16` tag stored in the archive's file object at `+0x0C` | Confirmed (read), Probable (identifies the mounted archive) |

The schema accessors keep only the low 16 bits (RPF9-F14). One archive can therefore address at most 65,536 rows, and the high half never reaches the schema. Path lookup also reads `E` as a `u16`. Where the tag value comes from at mount time is not traced. `0xFFFF` is the invalid row index, returned by the field-key search and by the row resolver.

## Row count

`E` at prefix `0x24` is the row count (RPF9-F13).

## Location records

Three field keys hold alternative layouts of the same information: payload offset, stored size, logical size, type ID and compression mode (RPF9-F32). Every native accessor tests them in the same order:

1. R, key `0xBA180AFB232D1B4B`
2. F, key `0x33F70DFAF2C50989`
3. A, key `0x4EAA16DD829995BC`

The first key present wins. The accessors dereference the A record without a null check, so they assume every row has a usable record. Whether a row in real archive data ever carries more than one of the three is not established.

Offsets in the tables are relative to the value pointer.

### Layout R

| Offset | Type | Use |
|---|---|---|
| `+0x00` | `u32` | Logical-size word 0 |
| `+0x04` | `u32` | Logical-size word 1 |
| `+0x08` | `u32` | Stored size in 16-byte units |
| `+0x0C` | `u32` | Payload offset in 16-byte units |
| `+0x10` | `u8` | Type ID |
| `+0x11` | `u8` | Compression mode |

### Layout F

| Offset | Type | Use |
|---|---|---|
| `+0x00` | `u64`, bits 0 to 39 | Payload offset in 16-byte units |
| `+0x05` | `u8`, bits 40 to 47 of the `u64` at `+0x00` | Type ID |
| `+0x06` | `u8`, bits 48 to 55 of the `u64` at `+0x00` | Compression mode |
| `+0x08` | `u64`, bits 0 to 39 | Stored size in 16-byte units |
| `+0x10` | `u64`, bits 0 to 43 | Logical size in bytes |

### Layout A

| Offset | Type | Use |
|---|---|---|
| `+0x00` | `u32` | Stored size in 16-byte units |
| `+0x04` | `u32` | Payload offset in 16-byte units |
| `+0x08` | `u64`, bits 0 to 47 | Logical size in bytes |
| `+0x0E` | `u8`, bits 48 to 55 of the `u64` at `+0x08` | Type ID |
| `+0x0F` | `u8`, bits 56 to 63 of the `u64` at `+0x08` | Compression mode |

### Derived values

| Value | R | F | A | Accessor RVA |
|---|---|---|---|---|
| Payload offset | `u32@+0x0C << 4` | `(u64@+0x00 & 0xFFFFFFFFFF) << 4` | `u32@+0x04 << 4` | `0xC6950` |
| Stored size | `u32@+0x08 << 4`, 32-bit result | `(u64@+0x08 & 0xFFFFFFFFFF) << 4` | `u32@+0x00 << 4`, 32-bit result | `0x1330AD0` |
| Logical size | `(u32@+0x04 & 0xFFFFFFF0) + (u32@+0x00 & 0x7FFFFFF0)` | `u64@+0x10 & 0xFFFFFFFFFFF` | `u64@+0x08 & 0xFFFFFFFFFFFF` | `0x1331670` |
| Type ID | `u8@+0x10` | `u8@+0x05` | `u8@+0x0E` | `0x56ED70` |
| Compression mode | `u8@+0x11` | `u8@+0x06` | `u8@+0x0F` | `0xF62E0` |

For R and A the accessor shifts the stored-size field in 32-bit arithmetic, so the result wraps above 4 GiB. Offsets are computed in 64 bits. How payload offsets become read addresses is in [payloads.md](payloads.md#payload-address).

The stored size bounds reads of compressed data. The logical size is the decoded size. Seeks and plain reads clamp to it (RPF9-F16, RPF9-F37).

Not established:

- The meaning of the two R words on their own, of their masked low nibbles and of bit 31 of word 0. The engine adds them, which fits the system and graphics page sizes of a resource. That reading is Probable.
- What selects layout F over layout A.
- The bits that no traced accessor reads: bits 56 to 63 of F `+0x00`, bits 40 to 63 of F `+0x08`, bits 44 to 63 of F `+0x10`.

## Enumeration

The archive interface has two bulk operations (RPF9-F21):

- Child enumeration takes an array of entry IDs and writes one 0x20-byte descriptor per entry.
- Batch open takes an array of entry IDs. For each one it opens the entry, optionally reads it, releases it and collects one field.

The enumeration descriptor:

| Offset | Content | Confidence |
|---|---|---|
| `+0x00` | 16 bytes. One code path reads them from the archive at the payload offset. Another copies them from the 16-byte value of key `0xC26722D233648AE7` | Confirmed (sources), Probable (first 16 payload bytes) |
| `+0x10` | Stored size | Confirmed |
| `+0x18` | The `u64` at file object `+0x30` | Confirmed (source), Unknown (meaning) |

The descriptor does not hold the archive base offset. Reads add file object `+0x20`, not `+0x30`.

Neither operation shows how the input ID array is built for a directory.

## Path lookup

Opening by path works as follows (RPF9-F20):

1. Take the part of the requested path after the first `/`.
2. For every row `0 .. E-1`, resolve the row's name as described in [names.md](names.md#name-lookup), and append `.` plus the extension for the row's type ID.
3. Search for the requested part inside the rebuilt name with a substring search.
4. On a match, build an in-memory entry descriptor of 0x118 bytes with the logical size and file object `+0x30`, and open the entry.

The lookup is a linear scan over all rows. No sorted hash index is used, and there is no binary search. A substring search can match more than one row. Which match the engine keeps, and whether it rejects partial matches, is not established.

## Directory hierarchy

Unknown. No parent or child record has been found. Path lookup matches components against a flat set of rows and does not walk a tree. No column has been identified that distinguishes directories from files. Whether the high-half tag or a column encodes hierarchy is open.

## Relation to payload reads

An opened entry is read and decoded as described in [payloads.md](payloads.md#engine-read-path).
