# RDS5

RDS5 is a flat record container. Every sampled file starts with the ASCII magic
`RDS5` and carries one ETPF chunk followed by data blocks. The observed samples use
the `.ttpf` extension. The extension and the observed directory names are provenance,
not evidence of the content model.

The container is a flat layout, not a hierarchical archive:

```text
0x00  header (0x10 bytes)
0x10  record array, C * 8 bytes
      zero padding to the next 0x100 boundary
      ETPF chunk at that boundary: 0x10-byte header, N * 16-byte entries,
      16N + M bytes of content
      zero padding to a 0x1000 boundary measured from the chunk start,
      plus 0x100 * (record 0 second word >> 28)
      data blocks, each starting on a 0x100 boundary
```

Record 0 locates the ETPF chunk. Records 1 to C-2 each locate one data block, and
record C-1 equals the file size. A 2-bit field in each block record selects the
storage form. One value selects zlib in 918,223 of the 918,305 blocks that carry it;
82 blocks carry that value without a zlib header and are an unexplained exception.
The codec behind the other selector values is **Unknown**.

## Documents

| Document | Content |
|---|---|
| [specification.md](specification.md) | Header, records, ETPF chunk, entry layout, block storage, reader rules |

Evidence: [evidence/rds5/INDEX.md](../../../evidence/rds5/INDEX.md). Corrections and
transfer history: [research-history.md](../../../evidence/rds5/research-history.md).
Independent verification: [evidence/rds5-verification/INDEX.md](../../../evidence/rds5-verification/INDEX.md).

## Status

| Part | Status |
|---|---|
| Magic, fixed header, record array position | Confirmed |
| `count`, `uncompressed_total`, version field | Confirmed for offsets and observed values. The `uncompressed_total` arithmetic is confirmed on two complete samples and **Probable** elsewhere |
| Record fields: offset, high byte, second word | Confirmed (offset, high byte). Second word: low 16 bits **Probable** as a counter of uncompressed position; high 16 bits **Unknown** |
| Record 0 as ETPF locator | Confirmed |
| ETPF chunk position and header | Confirmed |
| ETPF chunk end and first-block position | Nonzero end confirmed. The alignment plus flag-dependent extra is an observed relation; the flag meaning is **Unknown** |
| ETPF entry table | Confirmed (position, count, 16-byte stride). Field meanings mostly **Unknown** |
| Region after the entry table | Nonzero content ends at `0x10 + 0x20*N + M` bytes into the chunk (Confirmed). Length `16N + M` **Probable**, content **Unknown** |
| Block storage | zlib by stream header in 918,223 of 1,026,833 blocks. Clean inflate and end-of-stream verified for 2,173 zlib blocks. 108,610 blocks are not zlib; the selector byte explains all but 82, and the codec is **Unknown** |
| Block size accounting | `uncompressed_total = 0x1000 + sum(uncompressed block sizes)` confirmed on two complete samples; **Probable** elsewhere |
| Texture decoding | Not supported. No pixel format and no image output |
| Reconstruction | Not supported. Entry-to-block mapping and asset assembly are **Unknown** |

## Boundaries

These layers are separate and MUST NOT be conflated:

1. **Container parsing** reads the header, record array, ETPF header and entry table,
   and checks their bounds and alignment. It yields offsets and counts, not payload
   content.
2. **Encoded payload extraction** locates a block's stored range and inflates it only
   when the stream carries a zlib header. The output is still encoded texture or
   resource data, not pixels.
3. **Texture decoding** would interpret the inflated bytes as an image. It is not
   implemented and no pixel format is established.
4. **Reconstruction** would map ETPF entries to blocks or assets and rebuild them.
   Entry count equals block count in only 3 of 57 samples, and no mapping is known.

The storage selector is not a codec identity. Values 1, 2 and 3 are unidentified, and
the 82 selector-0 exceptions have no identified codec.

## Not to be assumed

- The 0x100-byte header impression comes from small files. The fixed header is 0x10
  bytes; the record array and its 0x100 padding only reach 0x100 when the record count
  is small.
- The ETPF type word `0x27A` is constant in all 57 samples. It is not known to be a
  version number.
- The 16-byte ETPF entries are not shown to be texture descriptors. Field meanings
  derived from position alone are marked **Unknown** in the specification.
- `.ttpf` and the observed directory names are naming conventions, not evidence of the
  content model.
- Nothing in this document claims a pixel format, a resource relationship or a texture
  reconstruction.

## Limits

- The record offset field is 24 bits in units of 0x100 bytes, so a container cannot
  address 4 GiB or more. The largest sampled file is 2,828,296,704 bytes.
- A reader MUST bounds-check every count and offset. The format carries no checksum
  over its records and no structural validation was observed.
- Non-zlib blocks cannot be extracted. The 82 selector-0 exceptions cannot be
  extracted either.
- The meaning of the version bit, the first-block flag and the block record's upper
  second word remains **Unknown**.
