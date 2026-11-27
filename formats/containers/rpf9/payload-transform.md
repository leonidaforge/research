# RPF9 payload transform: storage integration and complete coverage

The payload transform is the per-entry counter-mode keystream applied to a
entry's stored bytes before they are decompressed. This document records what
the remaining 750 failures were, which property of each row caused them, and
the range and counter rules that now decode every transformed entry of the
tested installation.

Status: **Confirmed** on all 1,398 transformed entries of the installation,
with build applicability limited to executable `scarlett-e95020b2` (see
[Build applicability](#build-applicability)).

## The transform descriptor

The value of column `0x286030A358A789FB` is 64 bytes. The first 22 are the
cipher descriptor the engine's initializer consumes:

| Offset | Type | Meaning |
| --- | --- | --- |
| `+0x00` | `u32` | Key identifier |
| `+0x04` | `u16` | Cipher type; `0x11` selects the counter-mode keystream |
| `+0x06` | 16 bytes | Parameter: the initial 128-bit counter block |

The rest carries the stream fields that decide which stored bytes the
keystream covers:

| Offset | Type | Field | Meaning |
| --- | --- | --- | --- |
| `+0x18` | `u64` | `a` | First region component |
| `+0x20` | `u64` | `b` | First region component and later-buffer length |
| `+0x28` | `u64` | `c` | Gap before the first later buffer |
| `+0x30` | `u64` | `t` | Length of the trailing region |
| `+0x38` | `u32` | — | `4` in every observed descriptor; no reader uses it |

`a`, `b` and `c` are the fields recorded as `+0x18`, `+0x20` and `+0x28` in
RPF9-F134. `t` is the field this assignment found; ignoring it is one of the
two root causes below.

## Covered range

Positions are stored-payload offsets relative to the **first chunk byte**. The
stored 16-byte prefix of encoding 2 is outside the stream, so position 0 is
the first compressed byte. For a stream of `len` bytes the transform covers:

- every position below `a + b`;
- from each later buffer start `a + b + c + k * (b + c)`, the first `b` bytes,
  for `k = 0, 1, 2, ...`;
- the last `t` bytes of the stream.

For the common shape `a = b = 0x400`, `c = 0x1C00`, `t = 0` this is the first
2048 bytes, the first 1024 bytes of the buffers at 9216, 17408, 25600, ... and
no tail, exactly the range RPF9-F134 established. The whole-range shape
`a = 0`, `b = 0x1000`, `c = 0`, `t = 0` makes the buffers abut from 0, so the
whole stream is covered. A zero `a = b = c = t` describes no range and is
rejected.

The engine transforms whole 16-byte blocks: a block is transformed when its
start is in the range, and a block that straddles a region boundary is
transformed as a whole. The decoder does the same, so a partial read and a
whole-stream read produce the same bytes.

## Counter

The counter is the 16-byte parameter plus the block index of the
payload-relative stored position, big-endian, advancing by one per 16-byte
block. The position is measured from the first chunk byte, not from the
payload offset: on encoding 2 the 16-byte stored prefix does not advance the
counter. The engine stores the block-aligned position in the stream context
(RPF9-F110), which is why a seek continues the keystream at the same block.

## Observed shapes

| Shape | `a` | `b` | `c` | `t` | Entries | Storage / type |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Common partial | `0x400` | `0x400` | `0x1C00` | `0` | 648 | chunked-3; types 11, 14, 255 |
| Whole | `0` | `0x1000` | `0` | `0` | 2 | chunked-3; type 11 |
| Script | `0x1000` | `0x1000` | `0x31000` | `0x1000` | 746 | chunked-2; type 89 |
| Raw DEFLATE | `0x400` | `0x400` | `0x1C00` | `0` | 4 | raw DEFLATE; type 11 |

The third shape is new. With `a = 0x1000` it covers the first 8192 stored
bytes, then 4096 bytes at 208896 and every 204800 bytes after that, and the
last 4096 bytes. A 331,744-byte type-89 row needs the first and last regions
only; a long row needs the periodic ones too. The previous decoder hard-coded
the common and whole shapes, which is why every type-89 row failed even though
its key state and block program were correct.

The fourth shape is the common partial range on a row with no chunk table.
The previous decoder refused it before reading a byte, because its selection
path required a zlib chunk.

## Storage integration

The transform is applied to the stored bytes and only then decompressed, for
every storage representation.

**Chunked-2.** Chunk 0 starts at payload offset + 16, the stored prefix is 16
zero bytes and is not part of the stream, and the counter starts at the first
chunk byte. The chunk table's stored sizes plus the prefix equal the entry's
stored size. A type-89 row may have one or two zlib chunks; one row in the
sample has a zlib chunk followed by a copied chunk (`3,0`).

**Chunked-3.** Chunk 0 starts at the payload offset; there is no prefix. The
counter therefore starts at position 0 as before.

**Raw DEFLATE.** Mode 1 without a chunk table is one DEFLATE stream from the
payload offset. A row may store zero padding after the stream's end (13 bytes
on the observed rows); these are outside the DEFLATE stream and the transform's
later buffers. A transformed row is verified by decoding the whole stream to
its declared logical size; bytes after the end must be zero or the row is
refused.

**Stage.** The selection probe and the decoder apply the transform before
inflation. Chunk framing, the stored prefix and the range are all expressed in
stored bytes, so no stage of the decoder sees a decompressed offset.

## Why the previous decoder failed

**Every chunked-2 type-89 row (746).** The descriptor's stream fields select
the script shape, and `+0x30` adds a trailing region. The decoder had two
hard-coded range rules that did not match either property, so its zlib probe
could not verify any candidate and it refused the row. Two further details
belong to the same framing: the counter starts at the first chunk byte, and
the last region is measured from the stored end of the stream.

**Every raw-DEFLATE type-11 row (4).** The selection path required a chunk
table and refused the row before reading it. A raw DEFLATE stream has no
checksum, so the corrected path inflates the whole stream through the
transform and requires the declared logical size, stream end and zero
trailing bytes.

The failing operation in both cases was selection and framing, not the block
program, the key state, the descriptor parameter or a different transform
round. The same key states and block program already decoded the 648
chunked-3 rows.

## Integrity

| Path | Checks |
| --- | --- |
| Transformed zlib chunk | Every zlib chunk inflates to its declared logical size and its Adler-32 matches; the chunk consumes exactly its compressed bytes |
| Transformed raw DEFLATE | Stream end, exact declared logical size, and zero bytes after the stream |
| Transformed copy chunk | Exact stored size equals logical size; no checksum exists |
| Chunk table | Stored sizes, padding and logical sizes sum to the entry's declared sizes; prefix is 0 or 16 |
| Counter | Whole 16-byte blocks; no partial block is transformed |

A successfully inflated stream is not authentication. The metadata signature
covers no payload bytes. The SHA-256 digests in the verification evidence are
reproducible fingerprints of the decoded bytes, not expected values from the
game.

## Verification

All 1,398 transformed entries were decoded in full through a bounded stream and
hashed with `lforge archive verify --transform true`:

| Storage | Entries | Complete decodes | Failures |
| --- | ---: | ---: | ---: |
| chunked-2 | 746 | 746 | 0 |
| chunked-3 | 648 | 648 | 0 |
| raw DEFLATE | 4 | 4 | 0 |
| **Total** | **1,398** | **1,398** | **0** |

The 648 chunked-3 entries that decoded before the change were re-read with the
baseline build and compared entry by entry: all 648 digests and logical sizes
are identical. The aggregate digest of those 648 decoded digests is
`8a5d85cb346e08231399b426dabb725390baae4c1e6df89d6ede7e6a24c33f54`.

The 14,488 encoding-4 entries were re-read by their preserved archive chains:
all 14,488 digests are identical and the aggregate digest of digests is still
`80c4ec5b0c49fd17235b93ac2568f62e467515abab70d891ac071a8bf7a76cb9`.

### Representative rows

| Chain | Type | Storage | `a`/`b`/`c`/`t` | Logical bytes |
| --- | ---: | --- | --- | ---: |
| `script.rpf!0!0` | 89 | chunked-2, one chunk | `1000/1000/31000/1000` | 1,310,720 |
| `pack/story000/story000_script.rpf!1!0` | 89 | chunked-2, two chunks | `1000/1000/31000/1000` | 24,576 |
| `pack/story000/story000_script.rpf!3!12` | 89 | chunked-2, `3,0` | `1000/1000/31000/1000` | — |
| `pack/story000/story000.rpf!90!0` | 11 | raw DEFLATE | `400/400/1C00/0` | 1,073,528 |
| `common.rpf!55` | 255 | chunked-3 | `400/400/1C00/0` | 110,723 |

All paths are installation-relative. `!N` names row `N` of the archive before
it.

## Build applicability

The descriptor fields, the range formula and the counter origin are
observations of executable `scarlett-e95020b2` and the 22 root archives of one
installation. The shapes cover every transformed row of that installation, but
another build could use other field values. A reader MUST compute the range
from the fields rather than from the encoding or the type, and MUST reject a
descriptor whose fields describe no usable range.

## Limitations

Verification reads at most 8 MiB of stored bytes. A transformed entry whose
stored range is larger is refused, not decoded partially. No transformed entry
of this installation exceeds it: the largest stored range is 5,898,608 bytes.

## Reproduction

- `analysis/rpf9-transform-remaining/verify_roots2.py` — verify all 1,398 rows.
- `analysis/rpf9-transform-remaining/verify_baseline2.py` — pre-change digests.
- `analysis/rpf9-transform-remaining/compare_baseline.py` — digest comparison.
- `analysis/rpf9-transform-remaining/verify_encoding4_chains.py` — encoding-4
  regression.
- `analysis/rpf9-transform-remaining/census_all_full.py` — the new census.

The analysis directory is temporary. Only aggregate counts and digests belong
in the repository; no payload bytes, keys, key states, tables or executable
bytes are published.
