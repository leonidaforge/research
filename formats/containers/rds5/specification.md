# RDS5 specification

All integers are little-endian. Offsets are absolute from the start of the file.
Values marked **Unknown** are observed fields whose meaning is not established.

Finding IDs such as `RDS5-F04` refer to [evidence/rds5/INDEX.md](../../../evidence/rds5/INDEX.md).
Independent verification of the same claims is recorded in
[evidence/rds5-verification/INDEX.md](../../../evidence/rds5-verification/INDEX.md).

## Header

| Offset | Type | Field | Meaning |
|---|---|---|---|
| `0x00` | 4 bytes | magic | ASCII `RDS5` |
| `0x04` | u32 | `record_count` | Number of 8-byte records. At least 3 |
| `0x08` | u32 | `uncompressed_total` | `0x1000 +` the sum of all block uncompressed sizes. Always a multiple of 0x1000 in the samples. Confirmed on two complete samples (RDS5-F12) and **Probable** elsewhere |
| `0x0C` | u32 | `version` | `0x16000000` (39 samples) or `0x16000001` (18 samples). Other values are not known; a reader MUST reject them |

The fixed header is 0x10 bytes and the record array starts at 0x10. There is no
separate header area between the records and 0x100. A 0x100-byte "header" appears only
when the record array plus its 0x100 padding ends at 0x100 (RDS5-F02).

`version` `0x16000001` appears on exactly 18 samples. It is not a property of a
directory class: containers in the same observed directory groups carry
`0x16000000`. The bit that differs is bit 0. Its meaning is **Unknown**, and no
structural rule differs between the two groups (RDS5-F06).

The record offset field holds 24 bits of 0x100-byte units, so a container cannot
address 0x100000000 bytes or more (RDS5-F16).

## Record array

`record_count` records of 8 bytes start at `0x10`. All records have the same layout.

| Bits | Field | Meaning |
|---|---|---|
| `lo[0:24]` | `offset` | Absolute position, `value * 0x100` |
| `lo[24:32]` | `high_byte` | Observed values listed below. Selects the block storage form on block records |
| `hi` | second word | Block records: `hi[0:16]` behaves as a 16-bit, wrapping counter of uncompressed position in 0x4000-byte units. `hi[16:32]` is **Unknown** |

Record roles:

| Index | Role |
|---|---|
| `0` | Locates the ETPF chunk: `offset` equals the chunk position. `high_byte` is 0 in every sample. `hi` is 0 except for two samples that carry `0x10000000` and `0x20000000` (meaning **Unknown**) |
| `1 .. C-2` | One data block each. `offset` is the block start and `offset` of the next record is its end |
| `C-1` | End marker. `offset` equals the file size |

Confirmed properties across 57 samples (RDS5-F03, RDS5-F04, RDS5-F05):

- `offset` is always a multiple of 0x100 and increases strictly with the record index.
- The last record's offset equals the file size in all 57 files.
- Record 0's offset equals `align_up(0x10 + 8 * record_count, 0x100)` in all 57 files,
  and equals the ETPF chunk position.
- Blocks are contiguous: block `i` ends where block `i+1` starts. Trailing alignment
  padding inside a block is possible because the next offset is rounded up to 0x100.
- Two samples place the ETPF chunk exactly at `0x10 + 8 * record_count`, which rules
  out a record-array start at 0x18 (RDS5-F03).

### Second word of a block record

- `hi[0:16]` behaves as `floor(cumulative_uncompressed_before_block / 0x4000) mod
  0x10000`. It matches exactly in the two samples that were fully decompressed and
  matches the sampled blocks of three more files (RDS5-F12). A reader SHOULD NOT treat
  it as an exact byte size: it quantises to 0x4000 bytes and wraps at 65536 counters
  (1 GiB of uncompressed data).
- `hi[16:32]` takes 19,174 distinct values across 1,026,833 block records, with a
  maximum of `0xFFF3`. It does not correlate with block size. It is **Unknown**,
  probably a checksum or hash, not demonstrated (RDS5-F13).
- Record 0's second word uses the top nibble as a layout flag: 0 in 55 samples,
  `0x10000000` in one sample and `0x20000000` in one. See the ETPF chunk section
  (RDS5-F17).

### `high_byte` values

Observed values across 1,026,833 block records: `0x04 0x0C 0x10 0x14 0x18 0x1C 0x20
0x40 0x44 0x4C 0x50 0x54 0x58 0x5C 0x60 0x80 0x84 0x8C 0x90 0x94 0x98 0x9C 0xA0
0xC4 0xCC 0xD0 0xD4 0xD8 0xDC 0xE0`.

| `high_byte & 0x0F` | Block count | Storage |
|---|---:|---|
| `0x0` | 918,305 | 918,223 zlib, 82 not zlib |
| `0x4` | 103,058 | not zlib |
| `0x8` | 268 | not zlib |
| `0xC` | 5,202 | not zlib |

Bits 2-3 of `high_byte` (mask `0x0C`) behave as a 2-bit storage selector with the
value `(high_byte >> 2) & 3` (RDS5-F11, RDS5-F18):

| Selector | Blocks | Observed storage |
|---|---:|---|
| 0 | 918,305 | zlib in 918,223; 82 carry no zlib header |
| 1 | 103,058 | codec **Unknown** |
| 2 | 268 | codec **Unknown**; every block has `high_byte` `0x18` |
| 3 | 5,202 | codec **Unknown** |

Value 0 selects zlib in 918,223 of the 918,305 blocks that carry it. The other 82 carry
value 0 but do not start with a zlib header, so the byte alone does not determine the
storage form. These 82 blocks are an unexplained storage form or a flag exception
(RDS5-F18):

- they sit in three samples;
- their high bytes are `0x10`, `0x40`, `0x50`, `0x80`, `0x90` and `0xD0`;
- 77 begin with `0x30` to `0x36` followed by `0xDE`; the other 5 begin with a byte
  outside that range.

A reader MUST NOT infer a codec from the selector alone.

## ETPF chunk

| Offset | Type | Field | Meaning |
|---|---|---|---|
| `+0x00` | 4 bytes | magic | ASCII `ETPF` |
| `+0x04` | u32 | `type` | `0x27A` in all 57 samples. A reader MUST reject a different value |
| `+0x08` | u32 | `entry_count` | Number of 16-byte entries |
| `+0x0C` | u32 | `field_m` | Multiple of 16. Adds to the length of the region after the entry table |
| `+0x10` | `N * 16` | entries | One 16-byte entry per `entry_count` |
| `+0x10 + 16N` | `16N + M` | high-entropy region | Not zlib. Length **Probable**, content **Unknown** |

The chunk position is `align_up(0x10 + 8 * record_count, 0x100)` and equals record 0's
offset (RDS5-F03, RDS5-F07). The entry table is fully consumed by `entry_count`
records (RDS5-F08).

Nonzero content ends at `pos + 0x10 + 0x20*N + M` (RDS5-F09). The byte before that
offset is nonzero and the byte at it is zero in all 57 samples, so the end of the
nonzero content is Confirmed. The chunk's own length is not stored: `16N + M` is the
smallest length consistent with the data, and a longer chunk followed by zero padding
cannot be excluded. The region length is therefore **Probable**.

The first block does not follow immediately. This relation holds in 57 of 57 samples
(RDS5-F17):

```text
first_block = pos + align_up(0x10 + 0x20*N + M, 0x1000)
                  + 0x100 * (record0.second_word >> 28)
```

The last term is 0 in 55 samples, `0x100` in one and `0x200` in another. Reading it as
a count of 0x100-byte units is unproven. A reader MUST NOT depend on the relation. It
MAY check it and report a mismatch.

All bytes from the content end to the first block are zero (57/57). Because both the
aligned boundary and the extra term fall inside that zero range, the split between
chunk content, chunk padding and block padding is not observable.

### Entry layout

| Offset | Type | Observed |
|---|---|---|
| `+0x00` | u32 | 202 distinct values. Bits 0, 1 and 14 are set in every entry, bit 15 in all but one. Low 16 bits take 12 values: `0xC000 \| ((1 << k) - 1)` in 357,114 entries, and `0x40FF` in one entry with `w0 = 0x100040FF` (RDS5-F15, RDS5-F19). Meaning **Unknown** |
| `+0x04` | u32 | 133 distinct values. High 16 bits take 16 values in the range `0x0020..0x1320`, low 16 bits 80 values. Meaning **Unknown** |
| `+0x08` | u32 | Low 16 bits behave as a page counter in 0x1000-byte units (below). The word has 349,703 distinct values across 357,115 entries and its high 16 bits take 613 values; probably a hash or identifier fragment, **Unknown** |
| `+0x0C` | u32 | 24 distinct values. Splits into two 16-bit values with 16 and 12 observed values. Meaning **Unknown** |

Page counter evidence (RDS5-F14):

- Consecutive differences of the low 16 bits, taken modulo 65536, are at most `0x1560`
  in all 57 files, so the field is a wrapping counter rather than a hash.
- In one 38,656-byte sample the five entries hold `1, 0x11, 0x21, 0x31, 0x41` and the
  five blocks each inflate to `0x10000` bytes. The field advances by
  `0x10000 / 0x1000` per entry, so the unit is 0x1000 bytes and the first data page is
  page 1.
- The same +1 origin explains `uncompressed_total = 0x1000 + sum(block sizes)` on the
  two complete samples (RDS5-F12).

The pattern in `+0x00` is not universal and MUST NOT be used as a validator.

## Block storage

Each block is a byte range `[offset_i, offset_{i+1})`. The next offset is rounded up to
0x100, so up to 0xFF padding bytes can trail a stream.

zlib blocks: first byte `0x78`, second byte `0xDA` in all 918,223 zlib blocks
(RDS5-F10). Inflating the whole range yields the block's content and the stream
reaches end-of-stream inside the range. That was verified for 2,173 blocks: every
zlib block of nine files and eight sampled blocks of a tenth. The remaining 916,050
zlib blocks were classified by their first two bytes only. Uncompressed sizes are
multiples of 0x1000 in every measured case, up to 4 MiB.

Non-zlib blocks (RDS5-F11, RDS5-F18): 108,610 ranges carry high-entropy data. They are
not zlib, gzip or raw DEFLATE, under the rule that the whole stored range must decode
as one stream with no leftover bytes. The test allowed the stream to start at offset 0
to 8. The codec is **Unknown**. No LZ4 result is claimed here because independent
verification could not reproduce one.

## Reader requirements

A reader MUST:

- reject a file shorter than 0x10 bytes, a wrong magic, an unsupported `version` and a
  `record_count` below 3;
- bound `record_count`, `entry_count`, the block span and the file size before
  allocating or reading a block;
- reject a record array that exceeds the file, an out-of-order record, a record offset
  outside the file, record 0 not pointing at the ETPF chunk, and a last record not
  equal to the file size;
- reject a wrong ETPF magic or type, a `field_m` that is not a multiple of 16, content
  that overruns the first block, and a non-zero byte between the content end and the
  first block;
- reject a zlib stream that does not reach end-of-stream, and cap decompression output;
- refuse to guess the non-zlib codec, including the 82 blocks that carry the zlib
  selector value but no zlib header.

A reader MUST NOT load the whole gap between the ETPF content and the first block, or a
whole block, into memory when a bounded scan is enough. The reference tool streams both
in 1 MiB pieces.

A reader SHOULD NOT enforce the observed first-block relation (RDS5-F17). Its flag term
is not understood. Reporting a mismatch is appropriate; rejecting the file is not.

A reader MUST scan the zero padding between the content end and the first block in
bounded pieces and reject a non-zero byte there.
