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

- `fileObject[+0x20]` is the archive base offset in the file object. The device's open method sets it. For a nested archive it is the payload offset of its row in the parent.
- `payloadOffset` is the location record's offset field shifted left by 4, see [entries.md](entries.md#derived-values). Offsets are therefore in 16-byte units and relative to the archive base.
- `position` is the logical position for plain reads and the stored-byte cursor for compressed reads.

The device read goes through the device object at file object `+0x10`, vtable slot `+0x60`.

### Read source

The handle for the read comes from the entry's read-source index, the `u32` value of key `0xCBB68FF7B7078DB7` (RPF9-F41, RPF9-F73):

| Index | Handle |
|---|---|
| `0xFFFFFFFF`, also when the column is absent or the cell is null | The file object's main handle |
| Any other value `i` | Entry `i` of the file object's alternate handle array |

- The engine does not check `i` against the number of alternate handles, does not check that the array exists, and does not check the handle it gets. An index past the end reads past the array.
- The handle choice does not change the address. The same `fileObject[+0x20] + payloadOffset + position` goes to the device whichever handle is chosen.
- What an alternate handle refers to is unknown. Whether it reaches the same data as the main handle is not established.

The alternate array starts empty when the file object is constructed, and the destructor releases its entries. No code that adds entries was found (RPF9-F74). Whether the array is ever filled in this build is unknown.

A reader SHOULD treat an absent index or `0xFFFFFFFF` as the main source. Any other value SHOULD be bounds-checked against the sources the reader actually has.

### Offset frames

| Frame | Meaning |
|---|---|
| Logical position | Position in the decoded entry, clamped to the logical size. Kept by the entry stream |
| Stored position | Position in the entry's stored bytes. Equal to the logical position for plain reads, the stored-byte cursor for compressed reads |
| Archive-relative | `payloadOffset + stored position` |
| Device-relative | `fileObject[+0x20] + archive-relative`, passed to the device |
| Physical | Device-relative positions summed over all device layers |

For a root archive opened from a file, the device is the physical file device. For a nested archive, the device is the parent archive (RPF9-F70).

### Nested reads

An archive object passes raw reads on to its own device (RPF9-F71):

```text
read(archive, handle, pos, length):
  n = (pos + length <= size) ? length : size - pos      # 32-bit result
  device.read(handle, pos + base, n)
```

`size` is file object `+0x28` and `base` is file object `+0x20`. The read is positional, so it keeps no cursor.

For an entry `e` of a nested archive `C`, which is row `r` of parent `P`:

```text
physical = base(P) + payloadOffset_P(r) + payloadOffset_C(e) + storedPosition
```

The child's read first reaches `P`'s raw read, clamped to `C`'s size (the logical size of `r`). Then it reaches `P`'s device, clamped to `P`'s size. Every further level of nesting adds one such step. Confirmed for the call structure. No depth limit and no cycle check were found.

The native clamp has a weakness. `size - pos` is truncated to 32 bits, and nothing rejects `pos > size`. A position past the end yields a negative length, which is passed to the next device unchanged. How the physical device handles that is not established. A reader MUST check `pos <= size` and compute lengths in 64 bits.

No layer of this path decompresses, decrypts or applies the payload transform. Decoding happens only inside the archive that owns an entry, as described [below](#engine-read-path). See [names.md](names.md#nested-archives) for what this implies for nested archive storage.

## Engine read path

The read dispatcher takes an archive, an open stream, a destination and a length. It picks one of three paths (RPF9-F34):

1. **Chunk fast path.** The chunk table is present, the payload transform flag is clear, a decompression service exists, the archive's device matches the one that service is bound to, and the request fits the stream's current chunk position. Runs of chunks go to that service with their disk address. What implements the service is not established.
2. **Compressed stream.** The entry's compression mode is nonzero, or the chunk table is present. The engine reads stored bytes into the stream's buffer in pieces of at most 0x10000 bytes, up to the stored size, and decodes them. A failed decode traps.
3. **Plain.** Otherwise the engine reads `min(length, logicalSize - position)` bytes directly.

Outside the chunk fast path, all stored-byte reads go through one routine. It reads through the device when the payload transform flag is clear. When the flag is set, it uses the [payload transform](#payload-transform). The transform flag is independent of the compression mode and the chunk table. A transformed compressed entry is first transformed, then decoded.

The decoder behind the chunk fast path is reached through an indirect call on a global service object and was not resolved (RPF9-F36). It reads the same chunk table and stored bytes as the compressed stream path.

### Failure handling

The compressed stream path handles errors as follows (RPF9-F80):

- A decoder failure traps the process.
- A failed device read returns without an error status and without moving the position.
- When no stored bytes are left, the read ends short.
- A decoder that makes no progress still returns success. If stored bytes remain, the read loop calls it again.

The native reader does not compare decoded sizes with the entry's logical size or with the chunk sizes. See [reader requirements](#reader-requirements).

## Seek

The archive's stream seek takes an offset and a mode: 0 from the start, 1 from the current position, 2 from the logical end. Other modes return -1. The result is clamped to the logical size (RPF9-F37).

- Plain stream: the engine stores the new position. With the transform flag set, it also repositions the transform context.
- Compressed stream, backward seek: the engine resets the decoder and both positions to zero, then decodes forward.
- Compressed stream, forward seek: the engine decodes and discards in steps of at most 0x1000 bytes until it reaches the target.
- Compressed stream with a chunk table and the transform flag clear: before the loop, the engine finds the chunk that contains the target (RPF9-F79). If the target lies outside the current chunk, it sets the logical position to that chunk's logical start, the stored cursor to its stored start, and resets the decoder for that chunk. A seek then decodes at most one chunk. Backward seeks into an earlier chunk do not restart from zero.

The chunk walk sums logical and stored sizes in 32 bits. The skip loop truncates the remaining distance to 32 bits.

The 0x1000-byte (4 KiB) step exists only in this skip loop. It is not the block size of payload reads.

## Decoding

Two numeric codes select a decoder. They come from different fields and use different numbering.

### Entry compression mode

The mode byte of the location record (RPF9-F35):

| Mode | Effect |
|---|---|
| 0 | Plain path. The decoder also has a copy branch for 0, but no traced path reaches it with mode 0 |
| 1 | Raw DEFLATE through the codec in slot 1 of the codec table (RPF9-F77) |
| 2 | Decoding fails |
| other | Codec table slot `mode`. Slots 0 and 2 are empty. The bytes after slot 2 are not pointers, so the engine would call through data. No codec for higher modes is established |

With a chunk table present, the entry's mode does not pick the decoder. Each chunk carries its own method instead.

### Codec

Codec table slot 1 holds the codec object at RVA `0x6DD5B08`. It drives a DEFLATE decoder through a structure with the Win64 layout of zlib's `z_stream` (RPF9-F35, RPF9-F77).

The decoder's initialization takes a window parameter with the semantics of zlib's `inflateInit2`: the sign selects the container, the magnitude the window size, and sizes below 2^8 are rejected. The engine uses two settings:

| Use | Window parameter | Container |
|---|---|---|
| Whole entry, mode 1, no chunk table | -15 | Raw DEFLATE (RFC 1951). No header, no checksum |
| Each chunk with method 3 | 15 | zlib (RFC 1950). Two-byte header, DEFLATE data, Adler-32 trailer |

The decoder loop treats a negative result as failure and 1 as end of stream. It references zlib's diagnostic messages for header, distance and checksum errors.

A second, one-shot decoder handles a whole method-3 chunk when the full chunk fits in the input and output buffers. It checks the zlib header itself: compression method 8, no preset dictionary, header check value divisible by 31. It then decodes the DEFLATE data and compares a checksum seeded with 1 against the big-endian `u32` trailer. The container format is therefore Confirmed. That the checksum is Adler-32 is Probable.

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

In encoding 3 the padding field, bits 16..19, lies inside the field the compressed size comes from, bits 16..31. With `X` = bits 16..31, the compressed size is `0x10000 - X` and the padding `X & 0xF`, so the stored size is `0x10000 - (X & 0xFFF0)`. Padding is the fill from the end of the compressed data to the next 16-byte boundary. In encodings 2 and 4 the stored size is in 16-byte units. Every chunk is therefore a multiple of 16 bytes long (RPF9-F78).

#### Chunk layout and decoding

Chunks are stored back to back. Chunk `i` starts at the sum of the stored sizes of chunks `0` to `i-1`, relative to the entry's payload offset. Within a chunk, the compressed bytes come first, then the padding (RPF9-F78).

| Chunk method | Decoding |
|---|---|
| 3 | One zlib stream. The decoder is released and initialized again at the start of every such chunk, so no state carries over between chunks |
| 0, 1, 2 | Copy. The engine copies the compressed bytes unchanged |

The engine finishes a chunk only when it has consumed exactly the compressed size and produced exactly the logical size. Then it skips the padding and decodes the next entry. A copy chunk whose compressed size differs from its logical size never finishes. A method-3 chunk that ends early or would produce more output does not finish either. The engine does not report either case as an error. The last chunk has no special handling.

The one-shot decoder credits the full logical size of the chunk after any successful decode. It does not compare the number of bytes produced with that size.

### Reader requirements

The native code checks less than a reader can afford to. A reader that decodes entries without the payload transform SHOULD follow these rules (RPF9-F80):

- Reject entries with the payload transform flag. Decoding them is outside non-cryptographic reading.
- Without a chunk table:
  - read mode 0 as plain data;
  - for mode 1, raw-inflate at most the stored size, and require end of stream with output equal to the logical size;
  - reject every other mode.
- With a chunk table:
  - check that the table and its entries lie inside the value pool;
  - reject encodings other than 2, 3 and 4;
  - compute all offsets in 64 bits;
  - require the stored sizes to sum to at most the entry's stored size and the logical sizes to sum to its logical size.
- For each chunk:
  - with method 3, zlib-inflate exactly the compressed bytes, and require end of stream, a valid checksum and output equal to the logical size;
  - with any other method, require the compressed size to equal the logical size and copy;
  - then skip the padding.
- Seek through the chunk table and decode only the chunk that holds the target.
- Report every failure as an error. A reader MUST NOT trap, loop without progress, or return bytes the decoder did not produce.

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
| zlib streams that inflate completely | Chunk method 3 decodes one zlib stream per chunk |
| One stream per 64 KiB of inflated data | Chunk encoding 3 measures sizes from 0x10000 |

These agree. The data observations were made by scanning, not by following native offsets. Entries with mode 1 and no chunk table hold raw DEFLATE, which the scan does not detect. Whether the data contains such entries is not established.

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
- Data that is stored uncompressed, as raw DEFLATE or with another method is not found as zlib streams.
- Entries behind the payload transform are found as zlib streams only if the transform leaves the stored bytes in that form, which is not established.
- Chunk grouping assumes consecutive streams belong together. A gap or an unrelated stream ends a group.

The native table of contents would remove these limits. See the [blockers](README.md#blockers-for-native-toc-extraction).
