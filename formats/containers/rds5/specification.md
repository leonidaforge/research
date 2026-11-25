# RDS5 specification

All integers are little-endian. Offsets are absolute from the start of the file.
Values marked **Unknown** are observed fields whose meaning is not established.

Finding IDs such as `RDS5-F23` refer to [evidence/rds5/INDEX.md](../../../evidence/rds5/INDEX.md).
Independent verification of the same claims is recorded in
[evidence/rds5-verification/INDEX.md](../../../evidence/rds5-verification/INDEX.md).

The population is 57 stores, 62,217,061,888 bytes, 1,026,947 8-byte records and
1,026,833 block records. Descriptor counts are texture counts and are not block
counts.

## Header

| Offset | Type | Field | Meaning |
|---|---|---|---|
| `0x00` | 4 bytes | magic | ASCII `RDS5` |
| `0x04` | u32 | `record_count` | Number of 8-byte records. At least 3 |
| `0x08` | u32 | `size_low` | Low 32 bits of the virtual payload size |
| `0x0C` | u32 | `size_high` | Bit 0 is bit 32 of the virtual payload size. Bits 1..31 are `0x16000000` in all 57 stores and are **Unknown** |

The virtual payload size is therefore `size_low | ((size_high & 1) << 32)`.
It equals the end record's virtual position in 57 of 57 stores: 39 stores need
only `size_low`, and 18 raise bit 32 (RDS5-F30). On the two zlib-only stores it
also equals `0x1000 +` the sum of inflated block bytes; the general definition is
the end record's virtual position. The largest observed payload
size is 6,556,999,680 bytes, so the field is exercised above 4 GiB even though
no sampled file reaches 4 GiB.

A reader MUST reject a `size_high` word whose bits 1..31 differ from
`0x16000000`. It MUST NOT treat bit 0 as a version bit: in every sampled store
it is the payload-size bit 32.

The fixed header is 0x10 bytes and the record array starts at 0x10. There is no
separate header area between the records and 0x100. A 0x100-byte "header" appears
only when the record array plus its 0x100 padding ends at 0x100 (RDS5-F02).

The record offset field holds 24 bits of 0x100-byte units under the six-bit class
description, so a container cannot address 0x100000000 bytes or more (RDS5-F16).
The four-bit class description would give a 26-bit offset field; the population
does not distinguish the two descriptions (see the record array).

## Record array

`record_count` records of 8 bytes start at `0x10`. All records have the same
layout. The first word is `lo` and the second word is `hi`.

| Bits of `lo` | Field | Meaning |
|---|---|---|
| `0..23` | `offset24` | Absolute position, `value * 0x100` |
| `0..25` | `offset26` | Equivalent 26-bit reading of the same field |
| `24..29` | `storage_class` | Class id; all observed values are multiples of 4 |
| `26..29` | `storage_class` | The same class id read as four bits |
| `30..31` | `page_term` | Low two bits of the virtual page position |
| `24..25` | reserved | Zero in every one of the 1,026,947 records |
| `hi[0:19]` | `counter` | 20-bit virtual counter in 0x4000-byte units |
| `hi[20:31]` | `padding` | 12-bit trailing padding count of the stored span |

The two offset rows are alternative readings of the same low bits. They give the
same value while bits 24 and 25 are zero, which holds for every sampled record.

### Two equivalent class and offset descriptions

Only class ids `0x00`, `0x04`, `0x0C`, `0x10`, `0x14`, `0x18`, `0x1C` and
`0x20` are observed. Every value is a multiple of 4, and bits 24 and 25 are zero
in every record (RDS5-F23). Two descriptions fit the same bytes:

1. a six-bit class field in bits 24..29 with a 24-bit offset in bits 0..23;
2. a four-bit class field in bits 26..29 with a 26-bit offset in bits 0..25.

The value of the six-bit field is exactly four times the value of the four-bit
field. The population cannot discriminate the descriptions: every sampled store
is below 4 GiB, so no record needs bit 24 or bit 25 of the offset. The
observation that would discriminate them is a store at or above 4 GiB whose
record offsets set bit 24 or bit 25. Such a store would reject the 24-bit offset
reading. No such store is in the sample.

A reader MUST reject a record with bit 24 or bit 25 set as out of the documented
model. It MUST NOT silently mask those bits or fold them into the class.

Record roles:

| Index | Role |
|---|---|
| `0` | Locates the ETPF chunk: `offset` equals the chunk position. `storage_class` is 0 in every sample. `hi` is 0 except for two samples that carry `0x10000000` and `0x20000000` (meaning **Unknown**) |
| `1 .. C-2` | One data block each. `offset` is the block start and `offset` of the next record is its end |
| `C-1` | End marker. `offset` equals the file size; `counter` and `page_term` encode the final virtual position |

Confirmed properties across 57 stores (RDS5-F03, RDS5-F04, RDS5-F05):

- `offset` is always a multiple of 0x100 and increases strictly with the record index.
- The last record's offset equals the file size in all 57 files.
- Record 0's offset equals `align_up(0x10 + 8 * record_count, 0x100)` in all 57
  files, and equals the ETPF chunk position.
- Blocks are contiguous: block `i` ends where block `i+1` starts. Trailing
  padding inside a block is counted by the `padding` field.
- Two samples place the ETPF chunk exactly at `0x10 + 8 * record_count`, which
  rules out a record-array start at 0x18 (RDS5-F03).

### Virtual position, padding and stored length

For every record (RDS5-F28, RDS5-F29):

```text
virtual  = (hi & 0xFFFFF) * 0x4000 + ((lo >> 30) & 3) * 0x1000
padding  = hi >> 20
length   = (next_offset - offset) - padding
```

The candidate relation `virtual = 0x1000 + (hi & 0xFFFFF) * 0x4000 + page_term *
0x1000` is **rejected**. The constant 0x1000 is not present in the fields. The
first block of `data/ttdb/ui/platform.ttpf` has counter 0 and page term 1 and
starts at virtual `0x1000`; the candidate would place it at `0x2000`, but the
payload size and the block length agree only with `0x1000`.

Validation:

- For 6,357 sampled zlib blocks, `virtual[next] - virtual[this]` equals the
  inflated byte count in 6,357 of 6,357.
- For the five class-`0x00` blocks, `span - padding` equals the same virtual
  difference in 5 of 5.
- The 20-bit `counter` takes 283,007 distinct values from 0 to 400,199. It does
  not wrap in the sample. Its top bit, `hi[19]`, is zero in every block, so the
  sample exercises only 19 counter bits; `hi[16:19]` takes the seven values 0..6.
- The 12-bit `padding` takes all 4,096 values from 0 to 4,095. It is a stored
  count, not a 0x100 alignment remainder: the sampled zlib blocks include padding
  counts well above 0xFF.
- The last `padding` bytes of every sampled stored span are zero: 5,754 blocks
  sampled across all eight classes and 0 non-zero. For zlib the stream ends
  exactly at `span - padding`, so those bytes are padding and not stream data.
- The 6,357 full zlib inflations agree with `consumed = span - padding` in every
  case.

These relations are validated for the zlib and stored classes only. They are
untested for the six undecoded classes, where the same fields can be read but
the payload length is not independently known.

The earlier reading of `hi[16:32]` as one 16-bit value with 19,174 distinct
values is superseded: `hi[16:19]` are counter bits and `hi[20:31]` are the
padding count. No unexplained bits remain in the second word for the validated
classes.

## Storage classes

The class id is read from bits 26..29 of `lo` (or the equivalent six-bit value
four times larger). It is not a two-bit selector: the old mask `(high_byte >> 2)
& 3` covered only bits 26 and 27 and could not separate ids that differ in bits
28 and 29 (RDS5-F24, RDS5-F26).

| Class id | Blocks | State | Evidence |
|---|---:|---|---|
| `0x00` | 5 | Stored bytes | `span - padding` equals the virtual length in 5 of 5; padding is zero |
| `0x04` | 102,725 | Storage class, payload not decoded | No zlib header; content **Unknown** |
| `0x0C` | 35 | Storage class, payload not decoded | No zlib header; content **Unknown** |
| `0x10` | 77 | Storage class, payload not decoded | No zlib header; content **Unknown** |
| `0x14` | 333 | Storage class, payload not decoded | No zlib header; content **Unknown** |
| `0x18` | 268 | Storage class, payload not decoded | No zlib header; content **Unknown** |
| `0x1C` | 5,167 | Storage class, payload not decoded | No zlib header; content **Unknown** |
| `0x20` | 918,223 | Complete zlib stream | First two bytes `78 DA` in 918,223 of 918,223; 6,357 full inflations, 0 failures |

Class `0x20` is validated only as zlib. Inflating the whole stored stream
reaches end-of-stream, the checksum is verified by the zlib decoder, and the
consumed length equals `span - padding`. The inflated sizes are multiples of
0x1000 in every measured case.

Class `0x00` is validated only as stored bytes. The five blocks are 4,096 or
16,384 bytes of content followed by zero padding; `span - padding` equals the
virtual length of each block.

The six remaining classes are storage classes distinguished by id. This
document does not name their payload format, does not assert a pixel format for
them, and does not claim that they are compressed. Their payloads are not
decoded in this iteration.

### The former 82-block anomaly

The previous text treated 82 blocks that carried the old selector value 0 without
a zlib header as an unexplained exception. With the class field extended to bits
26..29, those 82 blocks split into 77 class-`0x10` blocks and 5 class-`0x00`
blocks (RDS5-F27). The five class-`0x00` blocks are the stored blocks above and
satisfy the length identity. There is no anomaly class: the exception was an
artefact of the mask, which dropped bits 28 and 29.

### Observed format correlation

Some descriptors whose first block is not class `0x20` correlate with a format
id. The counts are over the 357,115 descriptors whose locator page is a block
start (RDS5-F34):

| Format id | First block `0x20` | First block another class |
|---|---:|---|
| 71 | 144,082 | `0x04` 30,592 |
| 72 | 81,748 | `0x04` 429 |
| 80 | 4,619 | `0x10` 37 |
| 83 | 6,882 | `0x14` 22 |
| 95 | 995 | `0x18` 5 |
| 96 | 18 | `0x18` 7 |
| 98 | 51,609 | `0x1C` 1,002; `0x00` 1 |
| 99 | 24,873 | `0x1C` 350; `0x00` 3 |
| 77 | 3,044 | `0x0C` 1 |

All 1,774 format-28 descriptors start with class `0x20`. This is a correlation
between a descriptor field and the first block's class. It is not a decode and
does not establish what the six undecoded classes contain.

## ETPF chunk

| Offset | Type | Field | Meaning |
|---|---|---|---|
| `+0x00` | 4 bytes | magic | ASCII `ETPF` |
| `+0x04` | u32 | `type` | `0x27A` in all 57 stores. A reader MUST reject a different value |
| `+0x08` | u32 | `descriptor_count` | Number of 16-byte descriptors and of 8-byte keys |
| `+0x0C` | u32 | `field_m` | Multiple of 16. Adds to the length of the region after the key table |
| `+0x10` | `N * 16` | descriptors | One 16-byte descriptor per texture |
| `+0x10 + 16N` | `N * 8` | keys | One 8-byte key per descriptor |
| `+0x10 + 24N` | `8N + M` | opaque | The rest of the nonzero region; content **Unknown** |

The nonzero region ends at `chunk_pos + 0x10 + 0x20*N + M` (RDS5-F09). The chunk
position is `align_up(0x10 + 8 * record_count, 0x100)` and equals record 0's
offset (RDS5-F03, RDS5-F07).

The first block does not follow immediately. This relation holds in 57 of 57
stores (RDS5-F17):

```text
first_block = pos + align_up(0x10 + 0x20*N + M, 0x1000)
                  + 0x100 * (record0.second_word >> 28)
```

The last term is 0 in 55 stores, `0x100` in one and `0x200` in another. Reading
it as a count of 0x100-byte units is unproven. A reader MUST NOT depend on the
relation. It MAY check it and report a mismatch.

All bytes from the content end to the first block are zero (57/57). Because both
the aligned boundary and the extra term fall inside that zero range, the split
between chunk content, chunk padding and block padding is not observable.

### Descriptor model

Each 16-byte descriptor is two 32-bit words and a 64-bit locator (RDS5-F31):

| Bits | Field | Observed |
|---|---|---|
| `w0[0:13]` | `width - 1` | Width 4 to 4,096; 11 distinct values |
| `w0[14:27]` | `height - 1` | Height 2 to 4,096; 12 distinct values |
| `w0[28:31]` | `mip` | 0 to 9; 10 distinct values |
| `w1[0:2]` | `flags` | 0 to 3 |
| `w1[3:9]` | `format_id` | 20 distinct values, 10 to 99 |
| `w1[10:19]` | `array_minus_one` | 0 to 63; 9 distinct values |
| `w1[20:23]` | `kind` | 2, 4, 6 and 10 |
| `w1[24:27]` | `tile_mode` | 0 to 3 and 9 to 12 |
| `w1[28:31]` | **Unknown** | 0 in 356,982 descriptors, 1 in 133 |
| `locator[0:20]` | first 4 KiB page | 1 to 1,600,782; every value is a block start |
| `locator[21:63]` | **Unknown** | Nonzero in 267,867 descriptors |

The descriptor count is a texture count: 357,115 descriptors across 57 stores,
against 1,026,833 block records. No descriptor had a width or height below 1,
and no field exceeded its declared bit width, so there is no range violation in
the sample.

Observed distributions (RDS5-F31):

| Field | Most frequent values |
|---|---|
| width | 1,024 (115,152); 512 (102,063); 256 (72,226); 128 (44,961) |
| height | 1,024 (108,577); 512 (99,455); 256 (76,333); 128 (47,562) |
| mip | 6 (162,424); 5 (101,648); 0 (52,676); 4 (12,851) |
| format id | 71 (174,674); 72 (82,177); 98 (52,612); 99 (25,226) |
| array size | 1 (356,418); 6 (567); 3 (99); 2 (19) |
| kind | 2 (356,402); 4 (567); 10 (143); 6 (3) |
| tile mode | 2 (195,957); 1 (70,497); 3 (50,811); 0 (39,283) |
| flags | 3 (206,882); 1 (99,947); 0 (50,056); 2 (230) |

Kind 4 occurs only with array value 5 (array size 6) in all 567 cases. Kind 10
takes array values 0, 1, 2, 7, 15, 31, 47 and 63; kind 6 takes 7 and 31. The
array and kind fields are not shown to describe cube or 3D resources.

### Key table

The first `8N` bytes after the descriptor table are `N` little-endian 64-bit
keys. In every store with at least two descriptors (56 of 57; one store has a
single descriptor) the keys are strictly increasing (RDS5-F32). Key values are
not named here and MUST NOT be published.

The remaining `8N + M` bytes of the region are opaque. They do not form a second
sorted key table in the sample.

### Descriptor first-page relation

The low 21 bits of every locator equal the first virtual page of a block. In all
357,115 descriptors the page is a block start, with no counterexample (RDS5-F33).
Descriptor 0's page equals the first block's page in 57 of 57 stores, and the
locator pages increase with descriptor order in every store with at least two
descriptors.

The relation is observational. A reader MAY use it to associate a descriptor
with a block range, and MUST report a descriptor whose page is not a block
start instead of repairing it.

## Block storage

Each block is a byte range `[offset_i, offset_{i+1})`. The `padding` field gives
the number of trailing zero bytes. The stored stream or content is the first
`span - padding` bytes.

Class `0x20`: the stored stream is one complete zlib stream (RDS5-F24). All
918,223 class-`0x20` blocks start `0x78 0xDA`. A sample of 6,357 blocks (up to 150
per store, evenly spaced) was inflated to end-of-stream with the checksum
verified; all 6,357 succeeded, `consumed` equaled `span - padding`, and the
padding bytes were zero.

Class `0x00`: the first `span - padding` bytes are stored content (RDS5-F25).
The five blocks are 4,096 or 16,384 bytes; `span - padding` equals the virtual
length of the block, and the padding is zero.

Classes `0x04`, `0x0C`, `0x10`, `0x14`, `0x18` and `0x1C`: not decoded. Their
first bytes are not `0x78` in any of the 108,605 blocks, and this iteration does
not establish what they contain.

## Texture reconstruction

The byte-level chain is established for one texture, the single descriptor of
`data/ttdb/ui/platform.ttpf` (RDS5-F35). The store is 222,976 bytes.

| Step | Observation |
|---|---|
| Descriptor | `w0 = 0x007FC3FF` gives 1,024 x 512, mip 0. `w1 = 0x00200311` gives flags 1, format id 98, array size 1, kind 2, tile mode 0. Locator page 1 |
| Referenced range | Virtual `0x1000` to `0x81000`; descriptor 0 is the only descriptor |
| Blocks | One block record, class `0x20`, stored span 218,624 bytes |
| Decompression | zlib inflates to 524,288 bytes; consumed 218,411; padding 213 zero bytes |
| Virtual space | The end record's virtual position is `0x81000`, equal to the payload size |
| Dimensions | 1,024 x 512 = 524,288 texels |
| Format interpretation | 524,288 inflated bytes / 524,288 texels = 1 byte per texel, or 16 bytes per 4 x 4 tile |
| Mip boundaries | The inflated size equals exactly one level at 1 byte per texel, so one level is present; the mip field is 0 and no lower mip is in the range |
| Layout | Tile mode 0. The meaning of the tile mode and the element order is **Unknown** |
| Block decode | Attempted under a documented 16-byte 4 x 4 endpoint layout (8-byte colour endpoints and indices, 8-byte alpha endpoints and indices); see below |
| Independent check | No lower mip exists, so the prescribed box-downsample comparison is not applicable |

Established: the descriptor fields, the referenced virtual range, the single
class-`0x20` block, the full zlib stream, the 524,288-byte output, the identity
`inflated = width * height * 1`, and the single-level boundary. The block
boundary coincides with the whole referenced range.

Not established: that format id 98 is the endpoint layout used for the pixel
attempt, the meaning of tile mode 0, the element order inside a tile, and any
pixel format name. Because the tile-mode meaning is unknown, the byte level is
the stopping point for the established reconstruction; the pixel attempt is a
consistency observation, not a reconstruction (RDS5-F36). Under the 8+8 endpoint
layout every colour endpoint is a 16-bit RGB565 value and every alpha endpoint is
an 8-bit value, so no endpoint is out of range by construction. The decoded image
has a smaller mean adjacent-pixel
difference (44.6) than a raw 16-byte-per-tile reading (77.8), 12,719 of 32,768
tiles use the three-colour branch and 13,989 use the six-alpha branch, and the
decoded alpha correlates with luminance at -0.12. Those are consistency
observations only. No game image is stored in this repository; decoded output
stays in scratch.

## Reader requirements

A reader MUST:

- reject a file shorter than 0x10 bytes, a wrong magic, a `size_high` word whose
  bits 1..31 differ from `0x16000000`, and a `record_count` below 3;
- reject a record whose bits 24 or 25 are set, instead of folding them into the
  class or the offset;
- bound `record_count`, `descriptor_count`, `field_m`, the block span and the
  file size before allocating or reading a block;
- reject a record array that exceeds the file, an out-of-order record, a record
  offset outside the file, record 0 not pointing at the ETPF chunk, and a last
  record not equal to the file size;
- reject a wrong ETPF magic or type, a `field_m` that is not a multiple of 16, a
  descriptor or key table that overruns the file, content that overruns the
  first block, and a non-zero byte between the content end and the first block;
- reject a `padding` value larger than the stored span, a non-zero padding byte,
  and a zlib stream whose consumed length is not `span - padding`;
- reject a zlib stream that does not reach end-of-stream, and cap decompression
  output;
- dispatch blocks by class id and refuse to guess an undecoded class. It MUST
  report the class id and MUST NOT fall back to another decoder.

A reader MUST NOT load the whole gap between the ETPF content and the first
block into memory. It SHOULD stream a zlib block and inspect only the padding
tail when it needs the decoded size. The reference tool scans the gap in 1 MiB
pieces.

A reader SHOULD NOT enforce the observed first-block relation (RDS5-F17). Its
flag term is not understood. Reporting a mismatch is appropriate; rejecting the
file is not.

A reader SHOULD compare the end record's virtual position with the payload size
and report a mismatch. The relation holds in 57 of 57 sampled stores but is not a
substitute for bounds checks.

A reader MUST NOT use the old two-bit selector `(high_byte >> 2) & 3`. The class
id is four or six bits wide as described above, and the two-bit mask merges
distinct classes.
