# RDS5 texture candidates

This document covers the decoded bytes of an RDS5 descriptor's virtual range.
It does not name a codec and does not treat a storage class as a pixel format.
Storage classes and the virtual mapping are defined in
[specification.md](specification.md); the byte-level control chain is
RDS5-F35 and the measurements here are RDS5-F38 to RDS5-F44.

Population: 57 local stores, 357,115 descriptors, 305,959 descriptors whose
whole virtual range uses storage classes `0x00` or `0x20`, and 305,253 of those
with kind 2 and array size 1. All counts below come from that second subset
unless a selection rule says otherwise. The input set is private evidence; the
tool and the synthetic tests are public.

## Method

A descriptor's range is `[first_page * 0x1000, next first_page * 0x1000)` and
the last descriptor ends at the payload size. Every block whose virtual position
falls in the range is decoded through its storage class, so only classes `0x00`
and `0x20` contribute. The decoded bytes are one stream.

Two checks are used and reported separately:

- **Size check**: the decoded extent equals the reverse-order level model in
  [Level stream model](#level-stream-model) for a level count. If more than one
  count matches, the result is ambiguous and no count is claimed.
- **Mip check**: levels are peeled from the end of the stream while each level's
  start is an observed block start. Consecutive peeled levels are decoded with a
  stated candidate decoder and compared by mean absolute error between
  `box_down(level i)` and `level i+1`. The check passes only when at least two
  levels are peeled and every pair is below 25.0. The stop reason is recorded.

The level count is never guessed. A texture with fewer than two block-aligned
levels is reported as not checked. Levels whose start is not a block boundary
are excluded and do not silently enlarge the check.

## Level stream model

For a level count `k`, level sizes are

```text
size(i) = blocks_x(width >> i) * blocks_y(height >> i) * unit_bytes
slot(i) = max(size(i), 0x100)
total   = align_up(sum(slot(i)), 0x1000)
```

Levels are stored smallest mip first. Each level starts at the end of the
previous slot; the stream is right-aligned in `total` with a zero-length or
positive prelude. The model was checked on the tail of one 512 x 512 format-71
texture, where levels 4, 3 and 2 start at 1,536, 2,048 and 4,096 and the
16 x 16 level starts at 1,280 inside its 256-byte slot (RDS5-F43). The model is
**Probable**, not Confirmed: it explains the observed starts but the 0x100
minimum slot and the prelude rule are not established for every format.

The descriptor `mip` field is not the recovered level count in this model. For
the samples where the check is unambiguous, the recovered count can equal `mip`
or `mip + 1`, and the size model can admit more than one count when the smallest
slots stay inside the same 0x1000 page. The field relation remains **Unknown**
(RDS5-F44).

## Storage units by format id

A unit is the number of bytes each level needs per element. It is a size fit,
not a codec name.

| Format id | Unit | Bytes | Evidence | Confidence |
|---|---|---|---|---|
| 28 | L4 | 4 per texel | 1,604 of 1,759 rows fit the L4 level-size model; the 155 multi-level tile-0 rows are excluded | Probable for the tested class |
| 54 | L2 | 2 per texel | 946 of 946 rows fit the L2 level-size model | Confirmed for the tested class |
| 71, 72 | B8 | 8 per 4 x 4 tile | total fits and BC1 mip check below | Confirmed for the tested class |
| 80 | B8 | 8 per 4 x 4 tile | total fits and BC4 candidate mip check | Probable |
| 83 | B16 | 16 per 4 x 4 tile | total fits; two 8-byte single-channel candidates pass the mip check | Probable |
| 98, 99 | B16 | 16 per 4 x 4 tile | total fits; block-first-byte structure below | Probable; degenerate with L1 |

For formats 98 and 99 the total alone cannot separate 16 bytes per 4 x 4 tile
from 1 byte per texel: with dimensions divisible by 4 both give the same level
sizes. The discriminator is the block-first-byte structure in RDS5-F41.

## Mip-check population

Selection rule: for each `(format id, tile mode)` pair, the 40 largest clean
simple-2D descriptors with a decoded extent at most 1 MiB, decoded through the
table above. Candidate decoders: BC1 for formats 71 and 72; single-plane BC4 for
formats 77 and 80; two-plane BC4 for format 83. The rule is deterministic from
the local sample order and extent.

| Format | Tile modes | Checked | Pass |
|---|---:|---:|---:|
| 71 | 1, 2, 3 | 120 | 97 |
| 72 | 1, 2, 3 | 120 | 67 |
| 77 | 2, 3 | 20 | 15 |
| 80 | 1, 2, 3 | 120 | 75 |
| 83 | 2, 3 | 80 | 44 |
| **Total** | | **460** | **298** |

298 textures pass the mip check across five format ids and both 8-byte and
16-byte block candidates. The per-class rate is not uniform: format 71 mode 1
and mode 3 pass 40/40 and 39/40, while format 71 mode 2 passes 18/40. A mixed
rate means the candidate decoder is incomplete for that class, not that the
texture has no mip relation. Rejected pairs stay rejected.

The check covers only levels that are whole storage blocks. For 512 x 512
format 71 that is levels 0 to 2 and for 1024 x 1024 it is levels 0 to 3. The
mip tail below those levels is not part of the pass count.

## Rejected candidates

| Candidate | Format / sample | Observation | Status |
|---|---|---|---|
| 1 byte per texel, row-major | 98, 99, smoke sample | 65.54% of 16-byte block-first bytes are multiples of 16 against 32.53% over all bytes; the lowest-set-bit histogram covers only bits 0..7 with a mode-prefix shape | Rejected |
| BC4, single channel | 71 | Mip error 48.5 / 46.2 on local/spatial differences, worse than BC1 | Rejected |
| Nibbles, 4 bits per texel | 71 | Mip error 64.5 / 66.3, at the random level | Rejected |
| BC1, BC3 and linear 8-bit | 98, tile 3 | Mip error 63 to 77 against a 25.0 threshold | Rejected for the tested class |
| 16 bytes per 4 x 4 tile identifies a codec | all | A block size is not a mode format; BC1, BC4, BC5-class and BC7-class candidates share byte ratios | Rejected as a claim |

## Control sample

`data/ttdb/ui/platform.ttpf` has one descriptor. The byte chain was reproduced
independently of the committed parser with a separate scratch parser (RDS5-F38):

| Component | Measured | Confidence |
|---|---|---|
| Descriptor | 1,024 x 512, mip 0, flags 1, format 98, kind 2, tile 0, page 1 | Confirmed |
| Stored blocks | one block, class `0x20`, stored span 218,624, padding 213, stream 218,411 | Confirmed |
| Decompression | zlib to end-of-stream, 524,288 bytes, consumed 218,411 | Confirmed |
| Virtual range | 0x1000 to 0x81000, 524,288 bytes; end record equals payload size | Confirmed |
| Size check | level 1, unit B16 and unit L1 both give 524,288; the count is unique | Confirmed |
| Block-first-byte structure | 32,768 blocks; 0 zero first bytes; 65.54% multiples of 16; all-byte fraction 32.53% | Confirmed |
| Pixel interpretation | 16 bytes per 4 x 4 tile, mode-prefixed blocks; no codec name | Provisional |
| Element ordering | order of the four elements inside a 16-byte block | Unknown |
| Mip selection | one level, no lower level in the range; mip check not applicable | Confirmed |
| Output dimensions | 1,024 x 512 texels | Confirmed |

The block-first-byte test rejects the linear 1 byte per texel reading of the
same extent. It does not identify the block encoding: a mode prefix and a
1-byte-per-texel size are compatible with more than one 16-byte block format.
Visual plausibility is not used as evidence.

## Eight components of a validated image

| Component | Status | Basis |
|---|---|---|
| Descriptor interpretation | Established | RDS5-F31, RDS5-F35, RDS5-F38 |
| Stored block selection | Established | RDS5-F33, RDS5-F38 |
| Decompression | Established | RDS5-F24, RDS5-F38 |
| Virtual reconstruction | Established | RDS5-F28, RDS5-F38 |
| Pixel-format interpretation | Partial: unit established, codec not identified | RDS5-F39, RDS5-F41 |
| Element ordering | Unknown for 16-byte blocks; row-major validated for 71 under BC1 only | RDS5-F40 |
| Mip selection | Established for the control sample; level-count recovery unresolved | RDS5-F44 |
| Output dimensions and arrangement | Dimensions established; arrangement inside a 16-byte block unknown | RDS5-F38 |

No complete image is claimed: the element ordering and the 16-byte block
encoding remain speculative.

## Limits

- The candidate decoders are standard specifications used as hypotheses. A
  passing mip check supports the element ordering and level layout, not a codec
  identity.
- Format 83 is only tested as two independent 8-byte single-channel planes.
  Other partitionings were not tested.
- Tile mode 0 is not covered by the mip check: its block starts do not coincide
  with level starts in the sampled descriptors, so no level is peeled.
- Only storage classes `0x00` and `0x20` contribute. Descriptors with any other
  class in their range are excluded from every count.
- The 0x100 minimum slot and the prelude rule are Probable and may differ for
  formats not tested here.
