# RDS5 texture candidates

This document covers the decoded bytes of an RDS5 descriptor's virtual range.
It does not name a codec and does not treat a storage class as a pixel format.
Storage classes and the virtual mapping are defined in
[specification.md](specification.md); the byte-level control chain is
RDS5-F35 and the measurements here are RDS5-F38 to RDS5-F44.

Population: 57 local stores and 357,115 descriptors, as in the committed `scan`
summary. A **clean descriptor** here means every block in its virtual range has
storage class `0x00` or `0x20`, so its bytes can be decoded. A **clean simple-2D
descriptor** additionally has kind 2 and array size 1. Counts of the clean
subsets depend on a scratch driver and are not cited. The input set is private
evidence; the tool and the synthetic tests are public.

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

## Storage-unit fits by format id

A unit is the number of bytes each level needs per element. The table records
**the unit sizes that reproduce the observed allocation extents in this sample**.
It is a fit. It is not a codec name, not a pixel-format identification, and not
independently confirmed for any format id.

The last column states whether any consequence independent of the extent fit was
tested. A mip check is independent of the fit only in the sense that it compares
neighbouring levels; it uses the same unit to size them. Format 54 has no such
consequence in this iteration.

| Format id | Unit | Bytes | Extent fit | Independent consequence |
|---|---|---|---|---|
| 28 | L4 | 4 per texel | single-level rows fit; multi-level tile-0 rows do not all fit and are excluded | **none**; no independent test was run |
| 54 | L2 | 2 per texel | sampled rows fit | **none**; no multi-level sample was tested |
| 71 | B8 | 8 per 4 x 4 tile | total fits | BC1 candidate mip check passes on a private sample; BC4 single-channel and nibble candidates rejected |
| 72 | B8 | 8 per 4 x 4 tile | total fits | BC1 candidate mip check passes on a private sample |
| 77 | B16 | 16 per 4 x 4 tile | total fits | single-plane BC4 candidate mip check passes on a few tile-mode 2 and 3 samples |
| 80 | B8 | 8 per 4 x 4 tile | total fits | single-plane BC4 candidate mip check passes on a private sample |
| 83 | B16 | 16 per 4 x 4 tile | total fits | two-plane BC4 candidate mip check passes on a private sample |
| 98 | B16 | 16 per 4 x 4 tile | total fits; degenerate with 1 byte per texel on dimensions divisible by 4 | linear 8-bit rejected at tile mode 3 by the F42 mip comparison |
| 99 | B16 | 16 per 4 x 4 tile | total fits; degenerate with 1 byte per texel on dimensions divisible by 4 | **none**; no equivalent tile-mode-3 linear test was run |

For formats 98 and 99 the total alone cannot separate 16 bytes per 4 x 4 tile
from 1 byte per texel: with dimensions divisible by 4 both give the same level
sizes. The size fit therefore selects neither reading. At format 98 tile mode 3
the separate F42 mip comparison rejects the linear reading; no equivalent test
exists for format 99.

## Mip-check population

Selection rule: for each `(format id, tile mode)` pair, up to 40 clean simple-2D
descriptors with a decoded extent at most 1 MiB, decoded through the table above.
Candidate decoders: BC1 for formats 71 and 72; single-plane BC4 for formats 77
and 80; two-plane BC4 for format 83.

Passing checks were observed for every class in this measured coverage:

| Format id | Tile modes tested | Block candidate |
|---|---|---|
| 71 | 1, 2, 3 | 8 bytes |
| 72 | 1, 2, 3 | 8 bytes |
| 77 | 2, 3 | 16 bytes |
| 80 | 1, 2, 3 | 8 bytes |
| 83 | 2, 3 | 16 bytes |

The exact counts and the selection driver are scratch-only and are not
committed, so they are not cited. The per-class rate is not uniform across tile
modes and formats. A mixed rate means the candidate decoder is incomplete for
that class, not that the texture has no mip relation. Rejected pairs stay
rejected.

The claim is private-evidence supported and is not reproducible from this
repository alone.

The check covers only levels that are whole storage blocks. The mip tail below
those levels is not part of the pass count.

## Rejected candidates

| Candidate | Format / sample | Observation | Status |
|---|---|---|---|
| BC4, single channel | 71 | A scratch comparison of local spatial differences gave a larger error than the BC1 candidate; the exact scratch values are not committed | Rejected (scratch measurement, private evidence) |
| Nibbles, 4 bits per texel | 71 | The same scratch comparison gave an error at the random level; the exact scratch values are not committed | Rejected (scratch measurement) |
| BC1, BC3 and linear 8-bit | 98, tile 3 | A scratch mip comparison stayed far above the 25.0 threshold; the exact scratch values are not committed | Rejected (scratch measurement) |
| 16 bytes per 4 x 4 tile identifies a codec | all | A block size is not a mode format; BC1, BC4, BC5-class and BC7-class candidates share byte ratios | Rejected as a claim |

Linear 1 byte per texel is **rejected for format 98 at tile mode 3** by the
mip comparison in RDS5-F42, and is **untested in every other class**. The
separate block-first-byte argument is withdrawn (RDS5-F41): it did not
discriminate the two layouts.

## Control sample

The **control sample** is the single-descriptor file
`data/ttdb/ui/platform.ttpf` (RDS5-F38). Its byte chain was reproduced with the
committed tools and with a separate scratch parser:

| Component | Measured | Confidence |
|---|---|---|
| Descriptor | 1,024 x 512, mip 0, flags 1, format 98, kind 2, tile 0, page 1 | Confirmed (private-evidence supported) |
| Stored blocks | one block, class `0x20`, stored span 218,624, padding 213, stream 218,411 | Confirmed (private-evidence supported) |
| Decompression | zlib to end-of-stream, 524,288 bytes, consumed 218,411 | Confirmed (private-evidence supported) |
| Virtual range | 0x1000 to 0x81000, 524,288 bytes; end record equals payload size | Confirmed (private-evidence supported) |
| Size check | one level of 524,288 bytes; unit B16 and unit L1 are degenerate | Fit only; no unit selected |
| Pixel interpretation | 16 bytes per 4 x 4 tile or 1 byte per texel; neither selected | Unknown |
| Element ordering | order of the elements inside a 16-byte block | Unknown |
| Mip selection | one level; the mip check is not applicable and tile mode 0 is not covered | Not established |
| Output dimensions | descriptor 1,024 x 512; decoded 524,288 = width x height | Probable (private-evidence supported); arrangement unknown |

The block-first-byte statistics that the committed tool prints are descriptive.
They do not discriminate a linear layout from a blocked layout: the stride-16
sample and the all-byte baseline are not independent, and a low-bit histogram
cannot show a mode field. No layout is selected for this sample.

## Eight components of a validated image

| Component | Status | Basis |
|---|---|---|
| Descriptor interpretation | Established | RDS5-F31, RDS5-F35, RDS5-F38 |
| Stored block selection | Established | RDS5-F33, RDS5-F38 |
| Decompression | Established | RDS5-F24, RDS5-F38 |
| Virtual reconstruction | Established | RDS5-F28, RDS5-F38 |
| Pixel-format interpretation | Fit only; codec unidentified; candidate layouts pass mip checks for 71, 72, 77, 80 and 83; linear rejected for 98 at tile 3 | RDS5-F39, RDS5-F40, RDS5-F42 |
| Element ordering | Unknown; BC1 row-major candidates exist for 71 and 72 | RDS5-F40 |
| Mip selection | Not established for the control sample; level-count recovery unresolved | RDS5-F44 |
| Output dimensions and arrangement | Dimensions probable; arrangement unknown | RDS5-F38 |

No complete image is claimed: the element ordering and the 16-byte block
encoding remain speculative.

## Limits

- The storage units are extent fits. No unit is individually confirmed, and
  formats 28, 54 and 99 have no consequence independent of the fit.
- The candidate decoders are standard specifications used as hypotheses. A
  passing mip check supports the element ordering and level layout, not a codec
  identity or a pixel format.
- Linear is rejected for format 98 at tile mode 3 by the F42 mip comparison and
  is untested elsewhere. The block-first-byte argument is withdrawn because it
  did not discriminate the two layouts.
- Format 83 is only tested as two independent 8-byte single-channel planes.
  Other partitionings were not tested.
- Tile mode 0 is not covered by the mip check: its block starts do not coincide
  with level starts in the sampled descriptors, so no level is peeled.
- Only storage classes `0x00` and `0x20` contribute. Descriptors with any other
  class in their range are excluded from every count.
- The 0x100 minimum slot and the prelude rule are Probable and may differ for
  formats not tested here.
