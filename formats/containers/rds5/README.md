# RDS5

RDS5 is a flat record container. Every sampled file starts with the ASCII magic
`RDS5` and carries one ETPF chunk followed by data blocks. The observed samples
use the `.ttpf` extension. The extension and the observed directory names are
provenance, not evidence of the content model.

The container is a flat layout, not a hierarchical archive:

```text
0x00  header (0x10 bytes)
0x10  record array, C * 8 bytes
      zero padding to the next 0x100 boundary
      ETPF chunk at that boundary: 0x10-byte header, N * 16-byte descriptors,
      N * 8-byte keys, then 8N + M opaque bytes
      zero padding to a 0x1000 boundary measured from the chunk start,
      plus 0x100 * (record 0 second word >> 28)
      data blocks, each starting on a 0x100 boundary
```

Record 0 locates the ETPF chunk. Records 1 to C-2 each locate one data block, and
record C-1 equals the file size. Each block record carries a storage-class id in
bits 26..29 of its first word; the bits 24..29 reading is four times that value.

Eight class ids are observed: `0x00`, `0x04`, `0x0C`, `0x10`, `0x14`, `0x18`,
`0x1C` and `0x20`. Class `0x20` is a complete zlib stream and accounts for
918,223 of the 1,026,833 blocks. Class `0x00` is stored bytes and accounts for 5
blocks. The other 108,605 blocks carry the six remaining class ids; their payload
format is **Unknown** and this container does not name it.

The ETPF chunk holds 357,115 descriptors across the 57 sampled stores. A
descriptor is 1,024 x 512 or another power-of-two size, with a format id, a
resource kind, a tile mode and a locator whose low 21 bits are a block's first
4 KiB virtual page. Descriptor count is a texture count, not a block count.

## Documents

| Document | Content |
|---|---|
| [specification.md](specification.md) | Header, records, storage classes, virtual space, ETPF descriptors and keys, reader rules |

Evidence: [evidence/rds5/INDEX.md](../../../evidence/rds5/INDEX.md). Corrections and
transfer history: [research-history.md](../../../evidence/rds5/research-history.md).
Independent verification: [evidence/rds5-verification/INDEX.md](../../../evidence/rds5-verification/INDEX.md).

## Status

| Part | Status |
|---|---|
| Magic, fixed header, record array position | Confirmed |
| `record_count`, payload-size field | Confirmed for offsets and observed values. Bit 0 of `+0x0C` is payload-size bit 32 in 57 of 57; the upper bits are **Unknown** |
| Storage-class field | Confirmed as a four-bit or six-bit field; the population cannot distinguish the two descriptions. Bits 24..25 are zero in every record |
| Storage classes | `0x20` validated as zlib (918,223 blocks; 6,357 full inflations, 0 failures). `0x00` validated as stored (5 blocks). Six classes **Unknown** |
| Virtual position and padding | Validated for zlib and stored blocks: 6,357 of 6,357 zlib blocks and 5 of 5 stored blocks. Untested for the six undecoded classes |
| Record 0 as ETPF locator | Confirmed |
| ETPF chunk position and header | Confirmed |
| Descriptor table | Confirmed (16-byte stride). Field ranges observed; meanings of some fields **Unknown** |
| Key table | Sorted 64-bit keys confirmed in 56 of 56 stores with at least two descriptors. Key values are not published |
| Descriptor first page | Every locator page is a block start in 357,115 of 357,115 descriptors |
| Block size accounting | End record equals the 33-bit payload size in 57 of 57 stores |
| Texture decoding | One byte-level chain reconstructed for one texture. No pixel format or codec identity is established |
| Reconstruction of undecoded classes | Not supported |

## Boundaries

These layers are separate and MUST NOT be conflated:

1. **Container parsing** reads the header, record array, ETPF header, descriptor
   table and key table, and checks their bounds and alignment. It yields
   offsets, counts and descriptors, not payload content.
2. **Class dispatch** decodes a block only when its class id is `0x20` (zlib) or
   `0x00` (stored). Any other class is reported by id and not guessed.
3. **Texture decoding** would interpret the inflated bytes as an image. One
   byte-level chain is established for a single texture; the pixel layout and
   the meaning of the tile mode are not.
4. **Reconstruction** maps a descriptor to a virtual block range with the
   locator page. This is shown for one texture and is observational.

The storage class is not a codec identity. Class `0x20` is zlib and class `0x00`
is stored bytes; the other six classes are storage classes whose payloads are not
decoded.

## Not to be assumed

- The 0x100-byte header impression comes from small files. The fixed header is
  0x10 bytes; the record array and its 0x100 padding only reach 0x100 when the
  record count is small.
- The ETPF type word `0x27A` is constant in all 57 stores. It is not known to be
  a version number.
- The 16-byte ETPF items are descriptors in the sense of dimensions, format id,
  kind, tile mode and locator. Other field meanings remain **Unknown**.
- The 8-byte keys are not named and their values are not published.
- `.ttpf` and the observed directory names are naming conventions, not evidence
  of the content model.
- A format id is not a codec name. The sample shows 16 bytes per 4 x 4 tile for
  one format id, but that does not identify the block encoding.

## Limits

- The record offset field is 24 bits in units of 0x100 bytes under the six-bit
  class description, so a container cannot address 4 GiB or more. The largest
  sampled file is 2,828,296,704 bytes. The four-bit class description would give
  a 26-bit offset field, but no sample reaches 4 GiB, so the descriptions are not
  discriminated.
- A reader MUST bounds-check every count and offset. The format carries no
  checksum over its records and no structural validation was observed.
- The six undecoded classes cannot be extracted. The tool fails explicitly for
  them.
- The meaning of the upper bits of `+0x0C`, the first-block flag and the
  descriptor's tile mode remains **Unknown**.
- The payload size reaches 6,556,999,680 bytes in one store even though no file
  reaches 4 GiB. Virtual space is not the file offset space.
