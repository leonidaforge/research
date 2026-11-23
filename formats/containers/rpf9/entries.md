# RPF9 entries

An entry is one row of the [columnar schema](schema.md). The format has no separate entry record.

## Entry IDs

The engine addresses an entry by a 32-bit ID (RPF9-F15):

```text
entryId = (tag << 16) | rowIndex
```

| Bits | Meaning | Confidence |
|---|---|---|
| 0 to 15 | Row index, `0 .. E-1` | Confirmed |
| 16 to 31 | The `u16` tag stored in the archive's file object at `+0x0C` | Confirmed (read), Probable (identifies the mounted archive) |

The schema accessors keep only the low 16 bits (RPF9-F14). One archive can therefore address at most 65,536 rows, and the high half never reaches the schema. Where the tag value comes from at mount time is not traced. `0xFFFF` is the invalid row index, returned by the field-key search and by the row resolver.

## Row count

`E` at prefix `0x24` is the row count (RPF9-F13).

## Enumeration

The archive interface has two bulk operations (RPF9-F21):

- Child enumeration takes an array of entry IDs and writes one 0x20-byte descriptor per entry. Each descriptor holds an offset-like value read through the field getters, and the device base offset at `+0x18`. The other descriptor fields are unknown.
- Batch open takes an array of entry IDs. For each one it opens the entry, optionally reads it, releases it and collects one field.

Neither operation shows how the input ID array is built for a directory.

## Path lookup

Opening by path works as follows (RPF9-F20):

1. Split the requested path on `/`.
2. For every row `0 .. E-1`, read the name hash and namespace from their columns. Resolve the name through the [name dictionary](names.md). Append the extension for the row's type ID.
3. Compare the rebuilt name with the requested component using a substring search.
4. On a match, build an in-memory entry descriptor of 0x118 bytes and open the entry.

The lookup is a linear scan over all rows. No sorted hash index is used, and there is no binary search. A substring search can match more than one row. Which match the engine keeps, and whether it rejects partial matches, is not established.

## Sizes

The engine's size helper reads size columns through the value pointer (RPF9-F16):

| Entry kind | Computation | Column |
|---|---|---|
| Resource | `(word0 & 0xFFFFFFF0) + (word1 & 0x7FFFFFF0)` over two 32-bit words | `0xBA180AFB232D1B4B` |
| Other | value masked to 44 bits | `0x33F70DFAF2C50989` |
| Other, alternate | value masked to 48 bits | `0x4EAA16DD829995BC` |

What each of the two words means on its own is not established. How the helper decides between the resource and non-resource paths is not documented. The result is the full data size that the stream reader clamps to. Whether it is the stored or the inflated size is not established.

## Directory hierarchy

Unknown. No parent or child record has been found. Path lookup matches components against a flat set of rows and does not walk a tree. No column has been identified that distinguishes directories from files. Whether the high-half tag or a column encodes hierarchy is open.

## Relation to payload reads

An opened entry is read through the stream reader, see [payloads.md](payloads.md#engine-read-path). How a row's columns become an absolute archive offset is not traced.
