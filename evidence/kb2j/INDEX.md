# KB2j and KB2n evidence index

This subject records the container family behind the `KB2j` and `KB2n`
signatures: header fields, section boundaries, frame index table and the local
tooling observations that connect them.

## Sample and method

| Property | Value |
| --- | --- |
| Archive | `movies.rpf`, SHA-256 `a0647c0325333dd42b25b00d85ee9b3915a55ce99127b97ef00662ef4866cba4` |
| Executable | `game_scarlett_master.exe`, SHA-256 `e95020b2fa4a721db3df59fdecf75621730ac559d8835252f6c3b658d5a08993` |
| Tooling | `lforge 0.1.0`, app `92af6e2`; FFmpeg/ffprobe 7.1.1 full build |
| Manifest | 515 rows, all type 255, layout F, no chunks, no payload transform |
| Census | Every row's first 48 header bytes read at its payload offset |
| Extraction | 10 `KB2j` rows and 2 `KB2n` rows, 12 payloads total |
| Frame validation | Frame index tables read for all 515 rows; tables capped at 8 MiB |

`<ARCHIVE>`, `<EXECUTABLE>`, `<WORK>` and `<PAYLOAD>` are local inputs. Payload
bytes are not reproduced. Header field values and sizes are reported because
they are the finding.

## Findings

| ID | Claim | Evidence | Confidence | Limits |
| --- | --- | --- | --- | --- |
| KB2-F01 | The local `movies.rpf` contains 515 rows, all type ID 255, layout F, without chunks or payload transform. 505 rows start with `KB2n` and 10 with `KB2j`. The earlier census count of 787 `KB2n` rows is not reproduced | Manifest, signature census | Confirmed (local) | One archive and one build; earlier count may come from another archive state |
| KB2-F02 | All 515 rows share the 48-byte header prefix. `u32 @+0x04` equals the logical (extracted) size minus 8 in every row, is little-endian, and differs from the RPF stored size minus 8 in 380 rows because of 16-byte row padding | Header census, extraction | Confirmed (515) | The field's own meaning beyond a size relation is Unknown |
| KB2-F03 | `+0x08` is the frame count and equals `+0x10` in all 515 rows. `+0x0C` is the largest frame size and no frame-index interval exceeds it. `+0x14`/`+0x18` are dimensions, `+0x1C` is the frame-rate numerator (30) and `+0x20` is its denominator (1) | Header census; FFmpeg mutations of `+0x08`, `+0x14`, `+0x18`, `+0x1C` and `+0x20` change duration, dimensions or rate; packet demux | Confirmed | One codec family; field names follow observable behavior |
| KB2-F04 | `+0x28` is an audio track count (0, 1, 2 or 4). Each track adds 12 bytes before the frame table. The descriptor is three field-wise `u32` arrays: a constant 145,920, a sample-rate/flags word, and a small track value. One-track sample yields one FFmpeg audio stream after signature substitution | Header census; descriptor parse; FFmpeg stream and mutation tests | Confirmed (count and layout); Unknown (array meanings) | 229 tracks; exact audio packet framing not established |
| KB2-F05 | The frame index table starts at `0x30 + 12 * audio_track_count`, holds `frame_count + 1` little-endian `u32` entries, is non-decreasing, ends at the logical file size and begins at the table end plus one. This holds in 515 of 515 rows | Header and table census | Confirmed (515) | First entry's role is Unknown; FFmpeg does not use it as a packet start |
| KB2-F06 | FFmpeg detects `KB2j` payloads as format `bink` with probe score 100 and demuxes exactly `frame_count` video packets. For all 10 `KB2j` samples the largest packet equals `+0x0C`. Decode stops with `Bink 2 video is not implemented`; no frame is decoded and no packet stream is copied | ffprobe `-show_streams`, `-show_packets`; ffmpeg copy attempt | Confirmed (detection, parse, demux); no decode | Ten video-only samples; FFmpeg 7.1.1 |
| KB2-F07 | Replacing only bytes 0..3 of `KB2n` rows 0 and 1 with `KB2j` makes FFmpeg parse them with the same header, dimensions, frame count and frame table. FFmpeg rejects the original `KB2n` signature. This supports a shared layout, not engine equivalence | Magic substitution on two extracted samples | Confirmed (diagnostic) | Two samples; not a compatible-tool test of the original files |
| KB2-F08 | The local `Bink2Scarlett.dll` (SHA-256 `9eaf045d004cd7d6a8382aaff0c6ea23a29fec4ef8bfacd726b54f5bc26fafd0`) contains a signature comparison sequence listing `KB2f` through `KB2n`, including `KB2j` and `KB2n`. The game executable references `Bink2Scarlett.dll` and contains Bink entry-point names such as `BinkOpen`, `BinkDoFrame` and `BinkGetKeyFrame` | Read-only string inspection | Confirmed (local) | String evidence only; no import table or decoder path was parsed |
| KB2-F09 | The 10 `KB2j` rows reduce to four unique payloads. Rows 54, 73 and 253 are byte-identical; rows 55, 277 and 417 are byte-identical; rows 99, 214 and 326 are byte-identical; row 53 is unique | SHA-256 of extracted payloads | Confirmed (10 rows) | Duplicate grouping does not explain why the archive stores copies |
| KB2-F10 | No ASCII identifier appears beyond the four-byte signature. Printable runs inside frame data are consistent with compressed data; `Bink`, `BIK` and `RAD` do not occur as stable markers | String scan of 12 extracted payloads | Confirmed (sample) | Absence in the sample does not rule out identifiers in other variants |
| KB2-F11 | `+0x24`, `+0x26` and `+0x2C` are observed but unexplained. `+0x24` is 18 or 19; `+0x26` is 0, 4, 16 or 20; `+0x2C` is `0x02070D00` for all `KB2j` rows and `0x87E90500`, `0x87E80400` or `0x87E70200` for `KB2n` rows | Header census | Confirmed (values); Unknown (meaning) | Values may be codec or encoder identifiers |

## Reproduction

```text
lforge archive manifest <ARCHIVE> --executable <EXECUTABLE> --format jsonl --output <WORK>/rows.jsonl
lforge archive extract <ARCHIVE> --row <ROW> --executable <EXECUTABLE> --output <WORK>/row.bin
python tools/kb2j/kb2_probe.py <WORK>/row.bin
ffprobe -show_streams -show_packets <WORK>/row.bin
```

The header census reads 48 bytes at each row's `payload_offset`. The frame-table
census uses the audio track count at `+0x28` to find the table start and reads
`4 * (frame_count + 1)` bytes, capped at 8 MiB.

## Research history

- 2026-11-25: `UPL-F05` said `u32 @+0x04` equals the stored size minus 8 in four
  extracted `KB2j` samples. Re-census shows the field equals the extracted
  (logical) size minus 8 in all 515 rows and differs from stored size minus 8 in
  380 rows because rows are padded to 16 bytes. The values 15 at `+0x08` and
  `+0x10` are frame counts, not format constants.
- 2026-11-25: The earlier count of 787 `KB2n` rows is not reproduced by the
  local archive used here; the local re-manifest reads 505 `KB2n` rows and 10
  `KB2j` rows. The relation between the signatures is no longer Unknown: all
  515 rows share one container layout, with the fourth signature byte selecting
  a variant.

## Open questions

- What the fourth signature byte and the `+0x2C` variant identifier select.
- Whether the meanings of `+0x24`, `+0x26` and the audio descriptor arrays can be
  derived from a decoder call path.
- How audio and video packets are framed when `+0x28` is non-zero.
- Why the archive stores three copies of three `KB2j` payloads.
- Whether the engine decodes these rows through `Bink2Scarlett.dll`; no call path
  was traced.
