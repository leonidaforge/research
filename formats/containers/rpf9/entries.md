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

The schema accessors keep only the low 16 bits (RPF9-F14). The high half never reaches the schema. Because `0xFFFF` is reserved as the invalid row index, one archive can address at most 65,535 rows, `0` to `0xFFFE`. The substring lookup also reads `E` as a `u16`. `0xFFFF` is the invalid row index, returned by the field-key search and by the row resolver.

### Tag allocation

The file object constructor sets the tag to `0xFFFF`. After the device open succeeds, it registers the file object in a global registry and stores the slot index as the tag (RPF9-F64):

- Slots are searched from 1 upwards. The first free slot is claimed with an atomic compare-and-swap. Slot 0 is never used.
- The registry has two tables, slots 1 to 999 and slots from 1000 up to a stored capacity. A full registry traps.
- A failed device open leaves the tag at `0xFFFF`.

Destroying a file object releases its slot and resets the tag to `0xFFFF` (RPF9-F72). A later file object can then receive the same tag.

The tag depends on the order in which file objects are created and on which slots are free. It is not derived from the archive. That tags are not stable across sessions or mount orders is Probable.

A tool MUST NOT persist tags or use them as archive identifiers. Row indices are stable only within one archive.

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

## Path resolution

Entries are found by path. The resolver hashes the path relative to the archive's mount prefix and searches the rows for the hash and the type ID, see [names.md](names.md#path-to-row) (RPF9-F55, RPF9-F58). A second, dictionary-based path lookup uses a substring search, see [names.md](names.md#substring-lookup) (RPF9-F20).

## Batch operations

The archive interface has two bulk operations (RPF9-F21):

- Batch path resolution takes an array of path strings. It resolves each one and writes one 0x20-byte descriptor per input. An unresolved path leaves its descriptor zeroed.
- Batch open takes an array of entry IDs. For each one it opens the entry, optionally reads it, releases it and collects one field.

The batch resolution descriptor:

| Offset | Content | Confidence |
|---|---|---|
| `+0x00` | 16 bytes. One code path reads them from the archive at the payload offset. Another copies the 16-byte header at the start of the value of key `0xC26722D233648AE7` | Confirmed (sources), Probable (the entry's RPF9 header) |
| `+0x10` | Stored size | Confirmed |
| `+0x18` | The `u64` at file object `+0x30`, the device's second attribute after the size | Confirmed (source), Probable (modification time, RPF9-F65) |

The descriptor does not hold the archive base offset. Reads add file object `+0x20`, not `+0x30`.

The descriptor has the same layout as the caller-supplied block a file object can be constructed from: an RPF9 header first, then size and time (RPF9-F75). See [names.md](names.md#preloaded-construction).

## Enumeration

No archive operation that iterates all rows and returns them was found (RPF9-F66). The only traced loop over all rows is the substring lookup, which returns one match.

Search scope: about twenty implemented methods of the archive interface were inspected. All of them work on a path the caller supplies, on an open handle or on a request queue. Many other slots are stubs that return a constant. If the base device interface has a find-first and find-next pair, it would sit in one of those stubs for this archive class. Which stub that would be is not known, because the base interface was not mapped.

Not covered: the uninspected interface methods, the device layer, and any resource manager above it. They may still enumerate. The inspected and stubbed slots are listed in the [build catalog](../../../builds/gta-vi/scarlett-e95020b2/functions.md#archive-vtable).

## Directory hierarchy

No directory model exists on the traced paths. The resolver hashes the whole stem, subdirectories included, and matches it against a flat set of rows. No row type, column or record for directories or parent links has been found. A hierarchy shows up only as `/` inside the hashed path. The traced code does not show whether rows exist that stand for directories.

A tool that shows a tree therefore has to build it from the paths of matched rows.

## Relation to payload reads

An opened entry is read and decoded as described in [payloads.md](payloads.md#engine-read-path).
