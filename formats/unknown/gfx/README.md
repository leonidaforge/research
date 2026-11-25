# GFx container

`GFX` (`47 46 58`) with version byte `0x2A` at offset 0 identifies the decoded
payload of 49 rows as a GFx container. The header is the documented GFx shape:
a three-byte magic, a version byte, a little-endian `u32` file length, then an
SWF header and SWF tags.

The archive parent, type ID, stored sizes and decoded sizes are provenance.
The container, its header and its tag framing are established below. Tag
contents, ActionScript, playback and rendering are not.

## Population

All 49 rows are type 66 in six depth-1 archives reached from `data.rpf` rows 1,
3, 6, 19, 20 and 39. Every row uses chunk encoding 3, mode 0 and no payload
transform; the stored payload is a zlib stream, so the signature is visible only
after chunk decoding. The 49 decoded payloads are distinct and range from 2,251
to 6,605,786 bytes.

The wider 849-manifest cache holds 183,144 row records. A stored-byte scan
covers all 182,321 readable rows and finds no stored `GFX` prefix. The 49
type-66 rows and the 37 type-5 rows in the same six archives were decoded; the
type-5 rows do not begin `GFX`. The remaining 182,235 readable rows were checked
only at the stored prefix.

## Identification

| Part | Observation | Support | Status |
| --- | --- | --- | --- |
| Signature | `47 46 58` at `+0x00` | 49/49 | Confirmed |
| Version | `0x2A` (42) at `+0x03` | 49/49 | Confirmed |
| Length | little-endian `u32` at `+0x04` equals the payload length | 49/49 | Confirmed |
| SWF header | RECT, frame rate and frame count follow the length | 49/49 | Confirmed |
| Tag framing | `u16` record headers with a long form | 49/49 | Confirmed |
| Family name | GFx container, from the signature and header shape | 49/49 header shape; no executable path traced | Confirmed (header shape) |

No payload has a version other than 42 and no payload has a length mismatch.
The earlier document called the family unidentified. It is identified by the
container header and tag framing; the contents of the tags remain uninterpreted.

## Header

Offsets are from the start of the decoded payload.

| Offset | Width | Observation | Support | Status |
| --- | ---: | --- | --- | --- |
| `+0x00` | 3 | `47 46 58` (`GFX`) | 49/49 | Confirmed |
| `+0x03` | 1 | version `0x2A` | 49/49 | Confirmed |
| `+0x04` | 4 | little-endian `u32` total length, equal to the payload length | 49/49 | Confirmed |
| `+0x08` | 1 | RECT first byte; `nbits = byte >> 3` | 49/49 | Confirmed (size); coordinate bits not decoded |
| `+0x08` | `ceil((5 + 4 * nbits) / 8)` | bit-packed RECT, 8, 9 or 10 bytes | 49/49 | Confirmed (size); content Unknown |
| RECT end | 2 | little-endian `u16` frame rate in 8.8 fixed point | 49/49 | Confirmed; 30.0 in 48, 24.0 in 1 |
| RECT end + 2 | 2 | little-endian `u16` frame count | 49/49 | Confirmed; always 1 |
| RECT end + 4 | | first tag | 49/49 | Confirmed |

RECT sizes and first tag offsets:

| `nbits` | RECT bytes | First tag offset | Rows |
| ---: | ---: | ---: | ---: |
| 14 | 8 | `+0x14` | 2 |
| 15 | 9 | `+0x15` | 2 |
| 16 | 9 | `+0x15` | 28 |
| 17 | 10 | `+0x16` | 17 |

The earlier document read `+0x08` and `+0x0A` as five variant byte pairs and
`+0x09` as a zero. Both bytes are inside the RECT. The five pairs are RECT byte
patterns, not payload variants, and the byte at `+0x0A` is not a selector.

## Tag grammar

After the frame header, the payload is a stream of tag records:

- A record starts with a little-endian `u16` header. `code = header >> 6` and
  `length = header & 0x3F`.
- If `length == 0x3F`, a little-endian `u32` extended length follows the
  `u16` header.
- The body follows and is `length` bytes long.
- Code 1 is ShowFrame and code 0 is End; both are zero-length in this sample.
- Code 39 is a sprite. Its body starts with a `u16` sprite ID and a `u16` frame
  count, followed by nested tag records. The walker uses this to track nesting.

The final four bytes are two adjacent zero-length tag headers, not a `u32`
field. The first header is ShowFrame (`0x40 0x00`) and the second is End
(`0x00 0x00`), so the four bytes are `40 00 00 00`. The earlier document
recorded this as a little-endian `u32` value 64 and as a ten-byte trailer with a
printable run. The ten-byte suffix still exists, but its last four bytes are the
two tag headers.

## Tag walk results

The walker starts at the first tag and stops only when the top-level stream
reaches the payload end. A partial parse is a failure.

| Result | Count |
| --- | ---: |
| Payloads attempted | 49 |
| Parsed to the payload end | 49 |
| Failed | 0 |
| Top-level tag count range | 8 to 2,839 |
| Top-level tags, total | 12,167 |
| Payloads containing sprites | 41 |
| Sprite tags, total | 1,025 |
| Nested tags, total | 102,306 |
| Maximum nesting | 1 |
| Total tags including nested | 114,473 |

There are no failures, so there is no first failing offset or tag code to
report. The first tag is code 1000 in 49/49 payloads and its length ranges from
15 to 42 bytes. The last two top-level codes are 1 and 0 in 49/49.

Three payloads in the sample have 11, 28 and 261 top-level tags. Those counts
reproduce the earlier report. The counts that include sprite bodies are larger;
for the same three payloads they are 13, 5,616 and 4,227. The difference is the
nested tags inside sprite bodies, so a tag count MUST state whether it includes
nested records.

The frame rate is 30.0 in 48 payloads and 24.0 in one. The frame count is 1 in
all 49. The single 24.0 payload is a counterexample to a uniform 30.0 reading.

## First tag contents

The earlier document recorded a printable-run grammar over the raw byte stream.
Tag parsing shows that only the first run lies inside the first tag.

- The first tag body is a ten-byte prefix, a printable run of 3 to 30 bytes and
  two further bytes. The run is preceded by a big-endian `u16` length that equals
  its length in 49/49 rows.
- The run end is followed by 15 bytes: the first two are the last two bytes of
  the first tag body, then the next tag's two-byte header and eleven body bytes.
  The 15-byte group is ten constant bytes, a three-byte group and a final
  `0x0A`; the group is zero in 46 rows, `FF 00 00` in 2 and `FF FF FF` in 1.
- A second printable run starts 13 bytes after the first tag ends, in the
  following tag stream. It contains the first run, ends in a constant five-byte
  suffix and is followed by a zero byte.
- The remaining bytes of the payload are further tag records. The earlier
  document stopped at the second run and called the rest an opaque body.

The earlier raw-byte grammar therefore crosses a tag boundary. It is not a
single tag layout. The payload strings and class names are not reproduced.

## Limits

- One build and one local archive set.
- The 49 rows are the type-66 population of the cached depth-1 manifests. A
  bounded cross-type sample decoded 37 non-type-66 rows and found no `GFX`
  prefix; that is not a decoded census of every row.
- The RECT bits, tag bodies, ActionScript and rendering are not decoded. Only
  tag codes 0 and 1 are named as documented SWF tags.
- The inventory reached depth 1. Type-66 rows below that depth were not searched.
- No executable path was traced. The GFx name rests on the header shape, not on
  a recovered symbol or loader.
- Movie strings and class names are not reproduced.

Evidence: [evidence/gfx/INDEX.md](../../../evidence/gfx/INDEX.md).
