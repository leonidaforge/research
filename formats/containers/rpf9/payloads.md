# RPF9 payloads

Payload data follows the metadata area. This document has two kinds of knowledge about it:

- The engine read path, traced in code: where an entry's bytes are, how they are read, and how they are decoded.
- The storage layout observed in archive data. It is enough to recover payloads without the table of contents.

The two agree where they overlap (see [below](#relation-between-code-and-data)). No archive has yet been decoded by following the native field values.

## Payload address

Every payload read goes to (RPF9-F33):

```text
address = fileObject[+0x20] + payloadOffset + position
```

- `fileObject[+0x20]` is the archive base offset in the file object.
- `payloadOffset` is the location record's offset field shifted left by 4, see [entries.md](entries.md#derived-values). Offsets are therefore in 16-byte units and relative to the archive base.
- `position` is the logical position for plain reads and the stored-byte cursor for compressed reads.

The device read goes through the device object at file object `+0x10`, vtable slot `+0x60`. The handle comes from a helper that combines file object `+0x18`, file object `+0x50` and the read-source index of key `0xCBB68FF7B7078DB7` (RPF9-F41).

## Engine read path

The read dispatcher takes an archive, an open stream, a destination and a length. It picks one of three paths (RPF9-F34):

1. **Chunk fast path.** The chunk table is present, the payload transform flag is clear, a decompression service exists, the archive's device matches the one that service is bound to, and the request fits the stream's current chunk position. Runs of chunks go to that service with their disk address. What implements the service is not established.
2. **Compressed stream.** The entry's compression mode is nonzero, or the chunk table is present. The engine reads stored bytes into the stream's buffer in pieces of at most 0x10000 bytes, up to the stored size, and decodes them. A failed decode traps.
3. **Plain.** Otherwise the engine reads `min(length, logicalSize - position)` bytes directly.

Outside the chunk fast path, all stored-byte reads go through one routine. It reads through the device when the payload transform flag is clear. When the flag is set, it uses the [payload transform](#payload-transform).

## Seek

The archive's stream seek takes an offset and a mode: 0 from the start, 1 from the current position, 2 from the logical end. Other modes return -1. The result is clamped to the logical size (RPF9-F37).

- Plain stream: the engine stores the new position. With the transform flag set, it also repositions the transform context.
- Compressed stream, backward seek: the engine resets the decoder and both positions to zero, then decodes forward.
- Compressed stream, forward seek: the engine decodes and discards in steps of at most 0x1000 bytes until it reaches the target.
- Compressed stream with a chunk table and the transform flag clear: the engine calls RVA `0x28CF820` before the loop. That function was not analyzed.

The 0x1000-byte (4 KiB) step exists only in this skip loop. It is not the block size of payload reads.

## Decoding

Two numeric codes select a decoder. They come from different fields and use different numbering.

### Entry compression mode

The mode byte of the location record (RPF9-F35):

| Mode | Effect |
|---|---|
| 0 | Plain path. The decoder also has a copy branch for 0, but no traced path reaches it with mode 0 |
| 1 | Codec in slot 1 of the codec table |
| 2 | Decoding fails |
| other | Codec table slot `mode`. Slots 0 and 2 are empty. The bytes after slot 2 are not pointers, so no codec for higher modes is established |

With a chunk table present, the entry's mode does not pick the decoder. Each chunk carries its own method instead.

### Codec

Codec table slot 1 holds the codec object at RVA `0x6DD5B08`. Its decode slot drives a structure whose field offsets match the Win64 layout of zlib's `z_stream`: `next_in`, `avail_in`, `total_in`, `next_out`, `avail_out`, `total_out`. It loops on one function and treats return value 1 as end of stream. That function is probably zlib `inflate` (Probable, RPF9-F35). It was not analyzed further.

### Chunk table

The value of key `0xE0C12D7A5D4884C5` describes the chunks of one payload (RPF9-F36):

| Offset | Type | Meaning |
|---|---|---|
| `+0x00` | `u32` | Offset of the entry array, relative to the start of this value |
| `+0x04` | `u16` | Chunk count |
| `+0x07` | `u8` | Entry encoding: 2, 3 or 4 |

Each entry is a `u64`. The decoder produces five values:

- the logical size of the chunk;
- its stored size on disk;
- padding;
- compressed size, always `stored - padding`;
- a 2-bit chunk method.

| Encoding | Logical size | Stored size | Padding | Method |
|---|---|---|---|---|
| 2 | `bits 0..23 << 4` | `bits 32..55 << 4` | bits 58..61 | bits 62..63 |
| 3 | `0x10000 - bits 0..15` | `padding + (0x10000 - bits 16..31)` | bits 16..19 | bits 60..61 |
| 4 | bits 0..27 | `bits 28..51 << 4` | bits 52..55 | bits 56..57 |

Any other encoding decodes to all zeros.

In encoding 3 the padding field, bits 16..19, lies inside the field the compressed size comes from, bits 16..31. The code reads both from the same bits. The reason is not known.

Chunk method 3 selects the same codec object as entry mode 1. Any other chunk method copies the chunk unchanged.

## Payload transform

When key `0x286030A358A789FB` is present, stored bytes do not come straight from the device (RPF9-F38):

1. The engine positions a per-stream context at `position & ~0xF`.
2. It reads whole 16-byte blocks through the device and passes them in place through a processing routine.
3. Partial blocks at the start and end go through a separate routine.

The same flag disables the chunk fast path. Seeks reposition the context. The algorithm and its key source are unknown. See [cryptography/rpf9](../../../cryptography/rpf9/README.md#payload-transform).

## Relation between code and data

| Data observation (RPF9-F29) | Code finding |
|---|---|
| Streams start on 16-byte boundaries | Payload offsets and stored sizes are in 16-byte units |
| zlib streams that inflate completely | The codec's driver matches zlib `inflate` (Probable) |
| One stream per 64 KiB of inflated data | Chunk encoding 3 measures sizes from 0x10000 |

These agree. The data observations were made by scanning, not by following native offsets.

## Observed storage layout

Archive payload data follows the rules below (RPF9-F29). They are observations from data, not a specification. Payloads can be recovered with them without the table of contents.

| Observation | Detail |
|---|---|
| Data start | At or after `hdr[0x04]`, rounded up to 16 bytes |
| Stream alignment | Every zlib stream starts on a 16-byte boundary |
| Compression | zlib streams that inflate completely, including the Adler-32 check |
| Chunking | Files over 64 KiB are stored as one stream per 64 KiB of inflated data. The last chunk is shorter |
| Resources | 16 zero bytes, then one zlib stream per resource page, system pages first |
| Large pages | Pages over 32 MiB are split into streams of 32 MiB inflated data |

Resources in GTA VI data show this page map and pointer layout:

- System data starts with a zero `u64` followed by a pointer to the page map.
- Pointers are `u64` values with high nibble 5 (system) or 6 (graphics). The low 28 bits are an offset into that segment's pages.
- The page map is 16 bytes with the system and graphics page counts at `+8` and `+9`, followed by one zeroed 8-byte slot per page.

Page sizes are not stored in the resource. They come from the stream lengths, so a missing page can be detected but its size cannot. Resource serialization will get its own document under `formats/resources/` once code-level evidence exists.

## Recovery limits

Recovering payloads by scanning has these limits:

- No names, paths or directory structure. Entries are known only by their offsets.
- An entry that does not start with a recognized signature cannot be told apart from a chunk of a larger file.
- Data that is stored uncompressed or with another method is not found as zlib streams.
- Entries behind the payload transform are found as zlib streams only if the transform leaves the stored bytes in that form, which is not established.
- Chunk grouping assumes consecutive streams belong together. A gap or an unrelated stream ends a group.

The native table of contents would remove these limits. See the [blockers](README.md#blockers-for-native-toc-extraction).
