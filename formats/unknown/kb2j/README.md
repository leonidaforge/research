# KB2j and KB2n

`KB2j` (`4B 42 32 6A`) and `KB2n` (`4B 42 32 6E`) appear at offset 0 of 515
rows in the local `movies.rpf`, all type ID 255, stored without chunks and
without the payload transform. The local archive contains 505 `KB2n` rows and
10 `KB2j` rows. An earlier census reported 787 `KB2n` rows over a different
797-row `movies.rpf` population; its manifest is not preserved (KB2-F01,
KB2-F12).

The `KB2n` stored prefix is not confined to `movies.rpf`. A stored-byte census
over the top-level rows found it in 787 rows across four archives: `movies.rpf`
505, `story000.rpf` 264, `core_restofworld.rpf` 11 and
`story000_restofworld.rpf` 7. Only the `movies.rpf` 515-row population has been
inspected structurally. The four-archive total of 787 and the historical 787
over a 797-row population are different measurements;
they MUST NOT be treated as one figure (KB2-F13).

| Signature | Rows | Logical size range          | Audio tracks |
| --------- | ---- | --------------------------- | ------------ |
| `KB2n`    | 505  | 82,320 to 373,705,456 bytes | 0, 1, 2 or 4 |
| `KB2j`    | 10   | 50,552 to 4,004,896 bytes   | 0            |

## Status

The two signatures belong to one container family with at least two signature
variants. All 515 rows share the same header prefix, little-endian frame index
table and frame-data region. The fourth signature byte selects a variant; what
it selects is **Unknown**.

A similarity to the Bink 2 container family is **Speculative**. FFmpeg 7.1.1
detects `KB2j` as format `bink`, parses the header and demuxes packets, then
stops with `Bink 2 video is not implemented`. The local `Bink2Scarlett.dll`
contains one signature comparison sequence for `KB2f` through `KB2n`, including
both signatures. Both observations are external-tool names and local strings,
not decoded frames or an engine call path. They do not establish container
identity, engine compatibility or a decoder implementation.

| Part                             | Status                               |
| -------------------------------- | ------------------------------------ |
| Magic and occurrence             | Confirmed (515 rows, one archive)    |
| Common header and frame table    | Confirmed (515 rows)                 |
| One family, two variants         | Probable                             |
| Bink 2 similarity                | Speculative (external tooling names) |
| Meaning of the fourth magic byte | Unknown                              |
| Frame encoding and decode        | Unknown                              |

## Common header

All 515 rows share a 48-byte header. Multi-byte fields are little-endian.
Fields at `+0x24`, `+0x26` and `+0x2C` are observed but not explained.

| Offset  | Size | Observation                                                                 |
| ------- | ---- | --------------------------------------------------------------------------- |
| `+0x00` | 4    | `KB2j` or `KB2n`                                                            |
| `+0x04` | 4    | Logical size minus 8. Not the RPF stored size when alignment padding exists |
| `+0x08` | 4    | Frame count                                                                 |
| `+0x0C` | 4    | Largest frame size. No frame-index interval exceeds it                      |
| `+0x10` | 4    | Equal to `+0x08` in all 515 rows                                            |
| `+0x14` | 4    | Width                                                                       |
| `+0x18` | 4    | Height                                                                      |
| `+0x1C` | 4    | Frame-rate numerator. 30 in all 515 rows                                    |
| `+0x20` | 4    | Frame-rate denominator. 1 in all 515 rows                                   |
| `+0x24` | 2    | 18 or 19. Meaning **Unknown**                                               |
| `+0x26` | 2    | 0, 4, 16 or 20. Meaning **Unknown**                                         |
| `+0x28` | 4    | Audio track count: 0, 1, 2 or 4                                             |
| `+0x2C` | 4    | Variant identifier. Meaning **Unknown**                                     |

`+0x04` equals the extracted payload size minus 8 in all 515 rows. The RPF row
is padded to a 16-byte boundary, so the stored size can be 4, 8 or 12 bytes
larger than the extracted size. Consequently, the stored size minus 8 differs
from the field in 380 of the 515 rows (KB2-F02).

Observed `+0x2C` values:

| Signature | `+0x2C`      | Rows |
| --------- | ------------ | ---: |
| `KB2j`    | `0x02070D00` |   10 |
| `KB2n`    | `0x87E90500` |  491 |
| `KB2n`    | `0x87E80400` |   13 |
| `KB2n`    | `0x87E70200` |    1 |

The value is constant per payload and does not track dimensions, frame count
or audio track count.

## Audio descriptors

When `+0x28` is `n > 0`, `3n` little-endian `u32` values follow the header,
grouped by field, not interleaved per track. The frame index table starts after
these `12n` bytes.

| Array      | Observed content                                                                                                        |
| ---------- | ----------------------------------------------------------------------------------------------------------------------- |
| `+0x30`    | 145,920 (`0x23A00`) in all 229 tracks. Meaning **Unknown**                                                              |
| `+0x30+4n` | Low 16 bits are the sample rate, 48,000 in all tracks. High 16 bits are flags: `0x7000` in 227 tracks and `0x3000` in 2 |
| `+0x30+8n` | Small integer, usually in `0..n-1` but not always ordered. Meaning **Unknown**                                          |

FFmpeg reports one audio stream for the one-track sample after its signature
is substituted (KB2-F04). The high 16 bits are observed flags; the meaning of
each flag bit is **Unknown**.

The exact packet framing when audio is present is **Unknown**. No mapping from
the descriptor arrays to audio packets is established.

## Frame index table

The table starts at `0x30 + 12 * audio_track_count` and contains
`frame_count + 1` little-endian `u32` entries.

Across all 515 rows:

- entries are non-decreasing,
- the last entry equals the logical file size,
- the first entry equals the end of the table plus one.

For the 10 video-only `KB2j` samples, FFmpeg demuxes exactly `frame_count`
packets. Packet 0 starts at the end of the table; packet `i` starts at entry
`i` for `i >= 1`; packet `i` ends at entry `i + 1`. The first entry is not used
as a packet start by that demuxer; its role is **Unknown**. The largest
demuxed packet equals `+0x0C` in all 10 samples.

## Frame data

Frame data starts at the end of the frame index table and ends at the logical
file size. No trailing section is observed. No ASCII identifier appears beyond
the four-byte signature; printable runs in the payload are consistent with
compressed data.

For `KB2n`, the original signature is rejected by the FFmpeg demuxer. Replacing
only those four bytes with `KB2j` makes the sample parse with the same header,
dimensions, frame count and frame table (KB2-F07). The substitution is a
diagnostic, not evidence that the engine treats the variants as equivalent.

## Variant relationship

`KB2j` and `KB2n` have the same header size, frame table layout and frame-data
region. `KB2n` additionally uses audio track counts above zero and spans a
wider range of dimensions and frame counts. All 10 `KB2j` rows are video-only
and reduce to four unique payloads; three of those payloads occur three times
each.

The local `Bink2Scarlett.dll` signature comparison sequence lists `KB2f`
through `KB2n` as one contiguous range. What the fourth byte encodes, and why
the engine stores both `KB2j` and `KB2n`, is **Unknown**.

## Limits

- One archive was inspected structurally. The `KB2n` stored prefix occurs in
  three further top-level archives (282 rows, counted by prefix only); no
  `KB2j` prefix was found outside `movies.rpf`. No other `KB2n` row was parsed
  or decoded (KB2-F13).
- The earlier 787 `KB2n` count covers a different `movies.rpf` population whose
  manifest is not preserved. The current 505 count covers the 515-row manifest;
  the figures are not interchangeable (KB2-F12).
- The Bink 2 similarity rests on FFmpeg format naming and local DLL strings. No
  decoded frame or engine call path confirms it.
- No frame was decoded and no payload was played back. FFmpeg demuxes `KB2j`
  without a decoder for the video bitstream.
- The meanings of `+0x24`, `+0x26`, `+0x2C`, the audio size array and the
  audio packet framing are not established.
- No decoder call path was traced. The local executable and DLL were inspected
  as data only.

Evidence: [evidence/kb2j/INDEX.md](../../../evidence/kb2j/INDEX.md).
