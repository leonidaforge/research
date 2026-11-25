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

A similarity to a known video-container family is **Speculative**. An external
demuxer recognizes `KB2j` as that family, parses the header and demuxes packets,
then stops at an unimplemented video decoder. A local decoder DLL contains one
signature comparison sequence for `KB2f` through `KB2n`, including both
signatures. Both observations are external-tool behavior and
local strings, not decoded frames or an engine call path. They do not establish
container identity, engine compatibility or a decoder implementation.

| Part                             | Status                               |
| -------------------------------- | ------------------------------------ |
| Magic and occurrence             | Confirmed (515 rows, one archive)    |
| Common header and frame table    | Confirmed (515 rows)                 |
| One family, two variants         | Probable                             |
| Known video-family similarity    | Speculative (external tooling behavior) |
| Meaning of the fourth magic byte | Unknown                              |
| Frame encoding and decode        | Unknown                              |

## Common header

All 515 rows share a 48-byte header. Multi-byte fields are little-endian.
The flags word at `+0x24` and the field at `+0x2C` are observed but not
explained.

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
| `+0x24` | 4    | Flags word. Low `u16` is `0x12` or `0x13`; high `u16` is 0, 4, 16 or 20. Bit `0x100000` is set in 40 rows. Meaning **Unknown** |
| `+0x28` | 4    | Audio track count: 0, 1, 2 or 4                                             |
| `+0x2C` | 4    | Variant identifier. Meaning **Unknown**                                     |

`+0x04` equals the extracted payload size minus 8 in all 515 rows. The RPF row
is padded to a 16-byte boundary, so the stored size can be 4, 8 or 12 bytes
larger than the extracted size. Consequently, the stored size minus 8 differs
from the field in 380 of the 515 rows (KB2-F02).

Observed `+0x24` flags words:

| Flags | Rows | Low `u16` | High `u16` | `0x100000` |
| --- | ---: | --- | --- | --- |
| `0x00040013` | 441 | `0x13` | 4 | clear |
| `0x00040012` | 33 | `0x12` | 4 | clear |
| `0x00140012` | 29 | `0x12` | 20 | set |
| `0x00100012` | 9 | `0x12` | 16 | set |
| `0x00140013` | 2 | `0x13` | 20 | set |
| `0x00000012` | 1 | `0x12` | 0 | clear |

The earlier document read `+0x24` and `+0x26` as two `u16` fields. The bytes
are the same; the `u32` read shows one flags word and is the current form. The
`0x100000` bit is observed but is not proven to mean alpha: no decoded frame
carries an independent alpha observation.

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
| `+0x30`    | 145,920 (`0x23A00`) in all 229 tracks. Equals the largest decoded byte count in 196/196 audio rows. Meaning **Probable** (maximum decoded record size) |
| `+0x30+4n` | Low 16 bits are the sample rate, 48,000 in all 229 tracks. High 16 bits are flags: `0x7000` in 227 tracks and `0x3000` in 2 |
| `+0x30+8n` | Track id. A permutation of `0..n-1` in 187 of the 196 audio rows; nine rows use a value outside that range            |

The first array is not the largest compressed record: the largest record in
the audio frames is 36,436 bytes, while the array value is 145,920. It matches
the largest decoded byte count in every audio row.

The track-id exceptions are nine two-track rows with ids `[3,1]`, `[1,3]` or
`[0,2]`; their row indices are listed in the evidence index. The high 16 bits
are observed flags; the meaning of each flag bit is **Unknown**. The two
`0x3000` tracks are in two rows.

The external demuxer reports one audio stream for the one-track sample after
its signature is substituted (KB2-F04). The audio record framing is described
below.

## Frame index table

The table starts at `0x30 + 12 * audio_track_count` and contains
`frame_count + 1` little-endian `u32` entries.

Across all 515 rows:

- entries are non-decreasing before and after masking bit 0,
- masking bit 0 of the first entry gives the table end,
- the last entry equals the logical file size and has bit 0 clear,
- every masked entry lies between the table end and the file size,
- no masked interval exceeds `+0x0C`.

Every row has at least one entry with bit 0 set; the first entry is always set.
The number of set entries per row ranges from 1 to 107. The bit is a keyframe
flag by hypothesis; no decoded frame confirms it.

For the 10 video-only `KB2j` samples, the external demuxer demuxes exactly
`frame_count` packets. Packet 0 starts at the end of the table; packet `i` starts at entry
`i` for `i >= 1`; packet `i` ends at entry `i + 1`. The first entry is not used
as a packet start by that demuxer; masking bit 0 gives the table end. The
largest demuxed packet equals `+0x0C` in all 10 samples.

## Audio frame records

When `+0x28` is `n > 0`, the start of each frame carries `n` track records in
track order. Each record is:

```text
[u32 record_bytes][u32 decoded_bytes][record_bytes - 4 bytes of packet data]
```

A zero `record_bytes` is a four-byte empty record with no decoded word. The next
track record follows immediately after the previous packet. The bytes after the
last track record are video data and are not interpreted here.

Over the 196 audio rows:

| Measure | Value |
| --- | ---: |
| Frames | 372,043 |
| Non-empty packet records | 398,992 |
| Zero-size records | 84,662 |
| Largest `record_bytes` | 36,436 |
| Largest `decoded_bytes` | 145,920 |
| Record-boundary violations | 0 |

This refines the hypothesis that `n` sizes form a contiguous array: each size is
the leading field of its own track record, and the first record starts at the
frame start. The `decoded_bytes` word is present on every non-empty record.

## Frame data

Frame data starts at the end of the frame index table and ends at the logical
file size. No trailing section is observed. No ASCII identifier appears beyond
the four-byte signature; printable runs in the payload are consistent with
compressed data.

For `KB2n`, the original signature is rejected by the external demuxer.
Replacing only those four bytes with `KB2j` makes the sample parse with the same
header, dimensions, frame count and frame table (KB2-F07). The substitution is a
diagnostic, not evidence that the engine treats the variants as equivalent.

## Variant relationship

`KB2j` and `KB2n` have the same header size, frame table layout and frame-data
region. `KB2n` additionally uses audio track counts above zero and spans a
wider range of dimensions and frame counts. All 10 `KB2j` rows are video-only
and reduce to four unique payloads; three of those payloads occur three times
each.

The local decoder DLL's signature comparison sequence lists `KB2f` through
`KB2n` as one contiguous range. What the fourth byte encodes, and why the
engine stores both `KB2j` and `KB2n`, is **Unknown**.

## Validation

The 515-row `movies.rpf` manifest was re-read at every payload offset. The
following structural results hold on the full manifest.

| Hypothesis | Result | Exceptions |
| --- | --- | --- |
| H1: `+0x24` is a little-endian `u32` flags field; `0x100000` is alpha | The `u32` read is consistent in 515/515 rows. Bit `0x100000` is set in 40 rows. Alpha semantics are not verified | None for the `u32`; alpha meaning Unknown |
| H2: entry 0 is `table_end + 1`; bit 0 is a keyframe flag | 515/515 rows. Masking bit 0 gives the table end. Bit 0 is set on a subset of entries; keyframe meaning is Probable | None |
| H3: `entry[i] & ~1` is a frame offset; bit 0 is keyframe; last entry is the file size with bit 0 clear | 515/515 rows for the mask, monotonicity, range and last-entry relation. Keyframe meaning is Probable | None |
| H4: array 1 is the largest packet size; array 2 is rate and flags; array 3 is the track id | Array 1 equals the largest decoded count in 196/196 audio rows, but not the largest compressed record. Rate is 48,000 in 229/229 tracks. Track ids are a permutation of `0..n-1` in 187/196 audio rows | Nine two-track rows use an out-of-range id; listed in the evidence index |
| H5: frame start carries `n` packet sizes and each non-empty payload starts with a decoded count | 372,043 frames, 398,992 non-empty records, 84,662 zero records, 0 boundary violations | None. The sizes are the leading word of per-track records, not one contiguous array |

No video or audio payload was decoded. The audio record fields are container
observations; the codec and the meaning of `decoded_bytes` are not established.

## Limits

- One archive was inspected structurally. The `KB2n` stored prefix occurs in
  three further top-level archives (282 rows, counted by prefix only); no
  `KB2j` prefix was found outside `movies.rpf`. No other `KB2n` row was parsed
  or decoded (KB2-F13).
- The earlier 787 `KB2n` count covers a different `movies.rpf` population whose
  manifest is not preserved. The current 505 count covers the 515-row manifest;
  the figures are not interchangeable (KB2-F12).
- The video-family similarity rests on external demuxer format naming and local
  DLL strings. No decoded frame or engine call path confirms it.
- No frame was decoded and no payload was played back. The external demuxer
  demuxes `KB2j` without a decoder for the video bitstream.
- The meanings of the `+0x24` flag bits, `+0x2C`, the audio flag bits and the
  `decoded_bytes` word are not established. The bit-0 keyframe reading is
  Probable, not decoded.
- The audio record counts cover 196 rows of the 515-row manifest. The 319
  video-only rows carry no audio records to validate.
- No decoder call path was traced and no codec was run. The local executable and
  DLL were inspected as data only.

Evidence: [evidence/kb2j/INDEX.md](../../../evidence/kb2j/INDEX.md).
