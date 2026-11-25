# RDS5 research history

## 2026-11-25: transfer from `research/textures-rds5`

The RDS5 container material was transferred from `research/textures-rds5` at branch
tip `5a54ae8`. The source branch was read with `git show` and was not rebased,
checked out or integrated. Each item below was classified before transfer.

| Source item | Subject | Classification | Current location |
|---|---|---|---|
| RDS5-F01 | Magic | Already on main as RDS5V-F02 | RDS5-F01 |
| RDS5-F02 | Fixed header | Already on main as RDS5V-F02 | RDS5-F02 |
| RDS5-F03 | Record array start and alignment; the two exact `0x10 + 8*C` samples | Confirmed-unintegrated detail; the aligned relation is already RDS5V-F02 | RDS5-F03 |
| RDS5-F04 | Record decode formula | Confirmed-unintegrated | RDS5-F04 |
| RDS5-F05 | Record roles and contiguity | Already on main as RDS5V-F02 and RDS5V-F03 | RDS5-F05 |
| RDS5-F06 | Version values and split | Already on main as RDS5V-F04 | RDS5-F06 |
| RDS5-F07 | ETPF chunk position and header fields | Positions already on main as RDS5V-F02 and RDS5V-F03; the field table is confirmed-unintegrated | RDS5-F07 |
| RDS5-F08 | ETPF entry table | Already on main as RDS5V-F03 | RDS5-F08 |
| RDS5-F09 | ETPF content end and region length | Already on main as RDS5V-F03; region length stays Probable | RDS5-F09 |
| RDS5-F10 | zlib first bytes and inflation | Already on main as RDS5V-F07 and RDS5V-F09 | RDS5-F10 |
| RDS5-F11 | Storage selector and negative codec results | Supported-with-limitations; the source omitted selector 2 and is superseded by the corrected table | RDS5-F11 |
| RDS5-F12 | Block-record counter and `uncompressed_total` | Supported-with-limitations; the counter is confirmed on two complete samples only | RDS5-F12 |
| RDS5-F13 | Upper 16 bits of the second word | Already on main as RDS5V-F11 | RDS5-F13 |
| RDS5-F14 | ETPF entry page counter | Supported-with-limitations; direct size correspondence on one sample | RDS5-F14 |
| RDS5-F15 | ETPF entry value sets | Already on main as RDS5V-F14 | RDS5-F15 |
| RDS5-F16 | 24-bit offset limit | Confirmed-unintegrated | RDS5-F16 |
| RDS5-F17 | First-block relation | Supported-with-limitations; relation confirmed, flag meaning Unknown | RDS5-F17 |
| RDS5-F18 | 82 selector-0 exceptions | Already on main as RDS5V-F09 | RDS5-F18 |
| RDS5-F19 | ETPF entry `+0x00` low-16 pattern | Already on main as RDS5V-F14 | RDS5-F19 |
| `tools/rds5/rds5.py` | Structural parser | Confirmed-unintegrated | [tools/rds5/rds5.py](../../tools/rds5/rds5.py) |
| `tools/rds5/test_rds5.py` | Synthetic parser tests, 33 cases | Confirmed-unintegrated; the suite passes under Python 3.15.0 | [tools/rds5/test_rds5.py](../../tools/rds5/test_rds5.py) |
| `tools/rds5/README.md` | Tool usage | Confirmed-unintegrated | [tools/rds5/README.md](../../tools/rds5/README.md) |
| `formats/containers/rds5/README.md` | Container overview | Confirmed-unintegrated | [formats/containers/rds5/README.md](../../formats/containers/rds5/README.md) |
| `formats/containers/rds5/specification.md` | Container specification | Confirmed-unintegrated | [formats/containers/rds5/specification.md](../../formats/containers/rds5/specification.md) |
| Per-file sample inventory | 57 paths, sizes and counts | Not transferred: a path list, and the aggregate counts are already on main | RDS5V-F01, RDS5V-F06 |
| LZ4 negative decoding | Non-zlib block test | Unsupported: independent verification could not reproduce it because no LZ4 module was available | Not carried |
| 0x100-byte header model | Small-file header impression | Superseded before transfer by the 0x10-byte header and record array | RDS5-F01, RDS5-F02 |

`RDS5-F01` to `RDS5-F19` keep the source order. The local application checks are
`RDS5-F20` to `RDS5-F22`.

## Disproved readings

Interpretations that were tested and failed. They are kept so the same reading is
not retried without new evidence. Each was disproved by the source branch's
measurements, which the verification on `main` re-read.

| Reading | Why it fails |
| --- | --- |
| The header is `0x100` bytes in every file | True only when the record array plus padding fits in `0x100` bytes. One sample places its ETPF chunk at `0x3100`, another at `0x24F00` |
| The record array starts at `0x18` | Two samples place ETPF exactly at `0x10 + 8*C`; a `0x18` start would overlap the chunk by 8 bytes |
| The record offset field is 16 bits | Files above 16 MiB need the offset's high bits; reading the low 16 bits alone gives positions far below the file size in every large sample |
| The high 16 bits of the ETPF entry `+0x08` are an uncompressed size | They do not track the page-counter differences or the block sizes |
| Block records' `hi[16:32]` is `crc32` or `adler32` of the stored or unpacked block | Checked on 5 blocks; no match |
| Non-zlib blocks are stored uncompressed | Their stored range is smaller than the uncompressed size derived from the counter |
| The first block follows the ETPF content at the next `0x100` boundary | The first block sits at a `0x1000` boundary measured from the chunk start in 55 samples, and two carry an extra `0x100` or `0x200` |
| Block storage is a two-bit selector `(high_byte >> 2) & 3` | The mask covers bits 26..27 only. Class ids also use bits 28..29; the eight observed ids are `0x00`, `0x04`, `0x0C`, `0x10`, `0x14`, `0x18`, `0x1C` and `0x20` |
| The 82 selector-0 blocks without a zlib header are an unexplained storage form | They are 77 class-`0x10` and 5 class-`0x00` blocks. The five class-`0x00` blocks satisfy the stored length identity |
| `virtual = 0x1000 + counter*0x4000 + page_term*0x1000` | The `+0x1000` constant is not present. In the platform sample the first block has counter 0 and page term 1 and starts at `0x1000`, not `0x2000` |
| The word at `+0x0C` is a version | Bit 0 equals bit 32 of the virtual payload size in 57 of 57 stores. The upper bits are constant at `0x16000000`, but their meaning is unknown |
| Block records' `hi[16:32]` is one unknown 16-bit hash | Bits 16..19 are counter bits and bits 20..31 are the padding count, which explains the observed value set |

## 2026-11-25: selector 2 added

The source text named selectors 1 and 3 as the unidentified codec and omitted selector
2, although its own low-nibble table listed the `0x8` group. The corrected selector
table now names value 0 as zlib with 82 exceptions, and values 1, 2 and 3 as
unidentified. Selector 2 covers 268 blocks, all with `high_byte` `0x18`. This is a
documentation gap, not a contradiction of the counts.

## 2026-11-25: confidence reduced where the sample is narrow

Three claims were narrowed during transfer:

- the block-record second-word counter is confirmed on two complete samples and
  **Probable** elsewhere;
- the ETPF entry page counter is confirmed on one five-entry sample and **Probable**
  generally;
- the ETPF region length stays **Probable** because a longer region followed by zero
  padding cannot be excluded.

The first-block relation is confirmed as a relation in 57 of 57 samples. The meaning of
its flag term remains **Unknown**, and a reader MUST NOT enforce the relation.

## 2026-11-25: local application check

Two representative claims were checked with the application CLI and the transferred
parser. The CLI reports `lforge 0.1.0`; its RDS5 parser and inspection path are
unchanged from `leonidaforge/leonida-forge` app commit `92af6e2`, and the local binary
was built from a later commit with no diff in that module or path.

- First-block relation with a nonzero flag term: the 238,897,664-byte vfx sample puts
  ETPF at `0x8E00`, content end at `0x23B70`, the 0x1000-aligned end at `0x23E00`,
  the flag term at `0x200` and the first block at `0x24000`. Both implementations
  agree.
- Entry page counter: the 38,656-byte five-entry sample holds pages
  `1, 0x11, 0x21, 0x31, 0x41`, five zlib blocks decode to 327,680 bytes, and
  `uncompressed_total` is 331,776. Both implementations agree.

No counterexample was found. The vfx application report shows 751,046,656 decoded zlib
bytes against the declared 766,107,648; the difference comes from 193 blocks with
unidentified selectors that are not decoded. That limits the `uncompressed_total`
check on that file but does not contradict the layout relation.

## 2026-11-25: storage classes replace the two-bit selector

The specification treated the block storage form as a two-bit selector
`(high_byte >> 2) & 3`, with value 0 selecting zlib and 82 blocks as an unexplained
exception. That model cannot separate the observed classes: the mask covers bits
26..27 and ignores bits 28 and 29, which are part of the class id.

The current measurement over the same 57 stores reads bits 24..29 of the first
record word and obtains eight ids: `0x20` 918,223; `0x04` 102,725; `0x0C` 35;
`0x10` 77; `0x14` 333; `0x18` 268; `0x1C` 5,167; `0x00` 5. Bits 24 and 25 are
zero in all 1,026,947 records, so a six-bit class field in bits 24..29 with a
24-bit offset and a four-bit class field in bits 26..29 with a 26-bit offset
describe the same bytes. The population cannot discriminate them because no
store reaches 4 GiB. A store at or above 4 GiB would.

The 82 former exceptions are 77 class-`0x10` and 5 class-`0x00` blocks. The five
class-`0x00` blocks satisfy `span - padding = virtual length`. The anomaly class
is deleted from the specification.

Class `0x20` remains zlib: all 918,223 class-`0x20` blocks start `0x78 0xDA`, and
6,357 sampled blocks inflate to end-of-stream with the checksum verified and
`consumed = span - padding`. Class `0x00` is stored bytes. The six remaining
classes are storage classes whose payloads are not decoded.

## 2026-11-25: virtual position, padding and the payload size

The candidate relation `virtual = 0x1000 + (hi & 0xFFFFF) * 0x4000 +
page_term * 0x1000` does not fit. The `+0x1000` constant is absent: the platform
sample's first block has counter 0 and page term 1 and starts at `0x1000`, while
the candidate places it at `0x2000`. The validated relation is

```text
virtual = (hi & 0xFFFFF) * 0x4000 + ((lo >> 30) & 3) * 0x1000
padding = hi >> 20
length  = span - padding
```

For 6,357 sampled zlib blocks, `virtual[next] - virtual[this]` equals the inflated
byte count. For the five class-`0x00` blocks, `span - padding` equals the same
difference. The padding field takes all 4,096 values, and the trailing padding
bytes were zero in 5,754 blocks sampled across all eight classes.

The `hi[0:16]` counter reading is extended to 20 bits. Bits 16..19 are counter
bits, not part of an unknown hash. The earlier `hi[16:32]` value set is explained
by the counter and padding fields.

The word at `+0x0C` was called a version. Its bit 0 equals bit 32 of the virtual
payload size in all 57 stores: 39 stores need only `size_low`, and 18 set bit 32.
The end record's virtual position equals the payload size in 57 of 57. The upper
bits stay `0x16000000` and their meaning is unknown. The version reading is
superseded.

## 2026-11-25: descriptor model and the first byte-level texture

The 16-byte ETPF items are descriptors: `w0` holds `width - 1`, `height - 1` and
a mip field; `w1` holds flags, format id, an array field, kind and tile mode; a
64-bit locator's low 21 bits are the first 4 KiB page. Across 357,115 descriptors
the observed field ranges are recorded in RDS5-F31. Descriptor count is a texture
count, not a block count.

The first `8N` bytes after the descriptor table are sorted little-endian 64-bit
keys in all 56 stores with at least two descriptors. The remaining `8N + M` bytes
are opaque. Key values are not published.

Every locator page is a block start in 357,115 of 357,115 descriptors, and
descriptor 0 matches the first block in 57 of 57. This gives an observational
descriptor-to-block-range map.

One byte-level chain is established for the single descriptor of the platform
sample: 1,024 x 512, format id 98, mip 0, kind 2, tile mode 0, one class-`0x20`
block from virtual `0x1000` to `0x81000`, 524,288 inflated bytes, and
`inflated = width * height * 1`. The block encoding, the tile-mode meaning and
the element order are not established. A pixel attempt under a documented 16-byte
4 x 4 endpoint layout is recorded as **Speculative**; no lower mip exists, so the
box-downsample check is not applicable.
