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
record C-1 equals the file size. Each block record carries a storage-class id.
Unless a sentence says otherwise, an id in this document is the six-bit value of
bits 24..29; the four-bit value of bits 26..29 is that id divided by four.

Eight class ids are observed: `0x00`, `0x04`, `0x0C`, `0x10`, `0x14`, `0x18`,
`0x1C` and `0x20`. Class `0x20` is a complete zlib stream and accounts for
918,223 of the 1,026,833 blocks. Class `0x00` is stored bytes and accounts for 5
blocks. The other 108,605 blocks carry the six remaining class ids; their payload
format is **Unknown** and this container does not name it. The
[specification](specification.md) maps each six-bit id to its four-bit reading.

Bits 24 and 25 are zero in every sampled record. A record with either bit set is
accepted: the class is taken from bits 26..29 and the six-bit reading is reported
as ambiguous. The first such record is the first candidate that could
discriminate the two field descriptions.

The ETPF chunk holds 357,115 descriptors across the 57 sampled stores. A
descriptor is 1,024 x 512 or another power-of-two size, with a format id, a
resource kind, a tile mode and a locator whose low 21 bits are a block's first
4 KiB virtual page. Descriptor count is a texture count, not a block count.

## Documents

| Document | Content |
|---|---|
| [specification.md](specification.md) | Header, records, storage classes, virtual space, ETPF descriptors and keys, reader rules |
| [textures.md](textures.md) | Candidate texture units, mip checks, rejected candidates and limits |

Evidence: [evidence/rds5/INDEX.md](../../../evidence/rds5/INDEX.md). Corrections and
transfer history: [research-history.md](../../../evidence/rds5/research-history.md).
Independent verification: [evidence/rds5-verification/INDEX.md](../../../evidence/rds5-verification/INDEX.md).

## Viewer decoding

The Leonida Forge viewer reads the store directly and decodes mip 0 of the
textures a drawable references. The fields it relies on were checked on the
same stores:

| Field | Reading |
| --- | --- |
| ETPF `d0` bits 0..13 | `width - 1` |
| ETPF `d0` bits 14..27 | `height - 1` |
| ETPF `d0` bits 28..31 | mip count minus one; tile mode 1 with field 1 is one mip |
| ETPF `d1` bits 3..9 | DXGI format |
| ETPF `d1` bits 10..19 | array size minus one |
| ETPF `d1` bits 20..23 | kind: 2 = 2D, 10 = 2D array; 4 (cube) and 6 (3D) are not decoded |
| ETPF `d1` bits 24..27 | tile mode: 0 = `SW_64KB_D`, 1..3 = `SW_4KB_S` |
| ETPF locator low 21 bits | virtual page; `page * 0x1000 + 0x1000` |

- Mips are stored smallest first and the descriptor range is right-aligned, so
  level 0 occupies `encoded_len - level0_len` bytes at the end of the range.
  The viewer exposes level 0 and does not descend to lower mips.
- Chunk classes `0x00` (stored) and `0x20` (zlib) decode. A level whose range
  includes another class is reported as unsupported instead of being decoded by
  guesswork.
- Tile mode 0 uses the 64 KiB Gfx10 layout; tile modes 1 through 3 use the
  4 KiB layout. The viewer reads level 0 from `encoded_len - level0_len`, so a
  multi-level allocation is right-aligned. The 64 KiB path was checked against
  the original model viewer on six sampled tile-0 textures: the reconstructed
  level-0 bytes are identical. The corrected 4 KiB placement produced complete
  images for multi-level samples where the earlier mip layout returned only
  partial content.
- A full `.ttpf` census over the 46 stores below `data/ttdb` selected 38,542
  simple 2D, supported-format tile-0 descriptors. 38,303 have an encoded range
  equal to the 64 KiB mip-chain total, and all 38,542 fit within it. The
  reproducible probe is the `tile_zero_64k_corpus_census` test in the
  application's texture crate. The earlier 37,175/37,413 figures are not
  reproducible with the recorded selection and are superseded by this census.
- The 4 KiB reorder uses the observed element-bit orders for RGBA8, R16,
  BC1/BC4 and BC3/BC5/BC7 and drops the padding tiles. The tiled result was
  validated by decoding BC1, BC3, BC4, BC5 and BC7 surfaces from actual stores
  and rendering the resulting drawables.
- The 64-bit ETPF key is the same key a drawable's texture name record carries.
  In the two named drawable rows, 12 distinct keys matched one store descriptor
  each and the remaining key was a texture embedded in the drawable itself.
- A scan of `<GAME_ROOT>/data/ttdb` in the Scarlett install found 46 stores.
  Keys are matched exactly; a key present in more than one store or descriptor
  is reported as ambiguous, not resolved by preference. The sampled RDS5
  store holds 912 descriptors: 886 have a supported simple-2D layout and 872
  reconstruct at level 0; the remaining levels use an undecoded storage class
  or an unsupported kind.

The viewer does not decode the six undecoded storage classes, BCPack payloads,
cube faces, 3D textures or array layers.

## Status

| Part | Status |
|---|---|
| Magic, fixed header, record array position | Confirmed |
| `record_count`, payload-size field | Confirmed for offsets and observed values. Bit 0 of `+0x0C` is payload-size bit 32 in 57 of 57; the upper bits are **Unknown** |
| Storage-class field | Confirmed as a four-bit or six-bit field; the population cannot distinguish the two descriptions. Bits 24..25 are zero in every record. A record with either bit set is accepted and reported as ambiguous |
| Storage classes | `0x20` validated as zlib (918,223 blocks; 6,357 full inflations, 0 failures). `0x00` validated as stored (5 blocks; payload returned verbatim and the virtual-length identity checked). Six classes **Unknown** |
| Virtual position and padding | Validated for zlib and stored blocks: 6,357 of 6,357 zlib blocks and 5 of 5 stored blocks. Untested for the six undecoded classes |
| Record 0 as ETPF locator | Confirmed |
| ETPF chunk position and header | Confirmed |
| Descriptor table | Confirmed (16-byte stride). Field ranges observed; meanings of some fields **Unknown** |
| Key table | Sorted 64-bit keys confirmed in 56 of 56 stores with at least two descriptors. Key values are not published |
| Descriptor first page | Every locator page is a block start in 357,115 of 357,115 descriptors |
| Block size accounting | End record equals the 33-bit payload size in 57 of 57 stores |
| Texture decoding | Level 0 of zlib/stored blocks decoded for BC1, BC3, BC4, BC5 and BC7 and several uncompressed DXGI formats through the tiled native layout. The six other storage classes and BCPack payloads are not decoded. One byte-level chain is also established for one texture |
| Reconstruction of undecoded classes | Not supported |

## Boundaries

These layers are separate and MUST NOT be conflated:

1. **Container parsing** reads the header, record array, ETPF header, descriptor
   table and key table, and checks their bounds and alignment. It yields
   offsets, counts and descriptors, not payload content.
2. **Class dispatch** decodes a block only when its class id is `0x20` (zlib) or
   `0x00` (stored). Any other class is reported by id and not guessed.
3. **Texture decoding** interprets inflated bytes as an image for the supported
   formats and tile modes. The pixel mapping is image-consistency evidence, not
   an engine codec trace.
4. **Reconstruction** maps a descriptor to a virtual block range with the
   locator page. This is established for zlib and stored blocks across the
   sampled stores.

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
  formats 77, 83, 98 and 99, but that does not identify the block encoding.

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
  descriptor's tile modes outside 0..3 remains **Unknown**. Modes 0 and 1..3
  map to the observed 64 KiB and 4 KiB native layouts.
- The payload size reaches 6,556,999,680 bytes in one store even though no file
  reaches 4 GiB. Virtual space is not the file offset space.
