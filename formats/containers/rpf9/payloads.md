# RPF9 payloads

Payload data follows the metadata area. Two kinds of knowledge exist about it, and they do not overlap yet:

- The engine read path, traced in code. It shows how an opened entry is read but not where its bytes are or how they are decompressed.
- The storage layout observed in archive data. It is enough to recover payloads without the table of contents, but no game code confirms it.

## Engine read path

The archive stream reader (RPF9-F22):

- supports seeking from the start, the current position and the end,
- clamps reads to the entry size from the [size helper](entries.md#sizes),
- reads through a low-level block read in `0x1000`-byte (4 KiB) blocks.

The 4 KiB block size belongs to this read loop. It is unrelated to the 64 KiB stream chunks below, and how the two layers connect is not traced.

Unknown in code:

- how a row's columns give the payload's archive offset,
- where decompression happens and which compression methods exist,
- whether payloads pass through the [cryptographic span runner](../../../cryptography/rpf9/README.md) or another transform,
- what the two stream flag columns mean ([schema.md](schema.md#known-columns)).

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
- Chunk grouping assumes consecutive streams belong together. A gap or an unrelated stream ends a group.

The native table of contents would remove these limits. See the [blockers](README.md#blockers-for-native-toc-extraction).
