# RDS5 evidence index

Container observations from the 57 sampled RDS5 containers. The material was
transferred from `research/textures-rds5` at branch tip `5a54ae8` as single-parent
commits; that branch was read with `git show` and was not rebased or integrated.
Per-file sample paths are not reproduced. Independent verification of the same
subject is in [rds5-verification/INDEX.md](../rds5-verification/INDEX.md); this index
does not repeat its method or its counterexample checks.

## Evidence types

| Method | Policy type | Meaning |
|---|---|---|
| Header scan | `BINARY`, `CROSS_SAMPLE` | Fields read from the first bytes of every sample, compared across all 57 files |
| Record scan | `BINARY`, `CROSS_SAMPLE` | The 8-byte record array decoded for all 57 files and every record checked against the file size |
| Block header census | `BINARY`, `CROSS_SAMPLE` | First two bytes of every block, used to separate zlib headers from other first bytes |
| Full inflate | `BINARY`, `CROSS_SAMPLE` | Complete zlib streams inflated with a checked end-of-stream and checksum; sizes, consumed length and padding recorded |
| Padding scan | `BINARY`, `CROSS_SAMPLE` | The trailing `padding` bytes of a stored span read and checked for zero |
| Arithmetic | `BINARY`, `CROSS_SAMPLE` | A layout formula checked against every sample or a named sample |
| Descriptor scan | `BINARY`, `CROSS_SAMPLE` | The 16-byte descriptor table decoded for every entry and the field ranges compared |
| Key scan | `BINARY`, `CROSS_SAMPLE` | The 8-byte key table compared for strict ordering without publishing values |
| Parser tests | `SYNTHETIC` | Authored fixtures and mutation cases for the parser and decoder |
| App inspection | `BINARY` | An independent implementation reads the same header, records, descriptors and block headers |

`BINARY` and `CROSS_SAMPLE` findings depend on a local `<ROOT>`. They are
private-evidence supported under `RESEARCH-POLICY.md` and reproducible from a lawful
copy of the same samples. `SYNTHETIC` findings exercise the parser contract, not the
native format.

## Sample

The transferred claims use the 57 containers whose aggregate counts are in RDS5V-F01
and RDS5V-F06. The current census over the same 57 files measured:

| Measure | Value |
|---|---:|
| Stores | 57 |
| Total size | 62,217,061,888 bytes |
| 8-byte records | 1,026,947 |
| Block records | 1,026,833 |
| Descriptors | 357,115 |

Representative local samples:

| Label | Size | Purpose |
|---|---:|---|
| vfx sample | 238,897,664 | First-block relation with a nonzero flag term |
| five-entry sample | 38,656 | Entry page counter, descriptors and payload-size relation |
| platform sample | 222,976 | Single zlib-only texture chain with one descriptor |
| largest-payload sample | 890,206,208 | Payload size above 4 GiB in virtual space |

No game file was opened for writing. No block payload was printed or stored. Block
content is never reproduced. Decoded images stay in scratch and are not committed.

## Findings

| ID | Claim | Evidence | Confidence | Independent check | Limits |
|---|---|---|---|---|---|
| RDS5-F01 | The magic is ASCII `RDS5` at offset 0 in all 57 stores | Header scan (`BINARY`, `CROSS_SAMPLE`) | Confirmed | RDS5V-F02 | One installation |
| RDS5-F02 | The fixed header is 0x10 bytes: `record_count` at `0x04`, `size_low` at `0x08`, `size_high` at `0x0C`. There is no separate header area between the records and 0x100; the 0x100 impression comes from small record arrays | Header scan (`BINARY`, `CROSS_SAMPLE`) | Confirmed | RDS5V-F02 | The 0x100-byte "header" only appears when the record array plus padding ends at 0x100 |
| RDS5-F03 | The record array starts at `0x10` and holds `record_count` 8-byte records. `align_up(0x10 + 8*C, 0x100)` equals the ETPF offset and record 0's offset in 57 of 57. Two stores place ETPF exactly at `0x10 + 8*C`, which rules out a `0x18` start | Record scan, arithmetic (`BINARY`, `CROSS_SAMPLE`) | Confirmed | RDS5V-F02 for the aligned relation | The exact `0x10 + 8*C` case rests on the two transferred samples; the independent check did not name them |
| RDS5-F04 | Record decode: `offset = (lo & 0xFFFFFF) * 0x100`, `offset_26 = (lo & 0x3FFFFFF) * 0x100`, `storage_class = ((lo >> 26) & 0xF) << 2`, `page_term = (lo >> 30) & 3`, `virtual = (hi & 0xFFFFF) * 0x4000 + page_term * 0x1000`, `padding = hi >> 20`. Bits 24..25 are reported as ambiguous, not folded into the class | Record scan, arithmetic (`BINARY`, `CROSS_SAMPLE`) | Confirmed | RDS5V-F02, RDS5V-F13 | The 24-bit offset and the equivalent 26-bit reading are not discriminated (RDS5-F23) |
| RDS5-F05 | Record 0 locates the ETPF chunk. Records `1..C-2` are data blocks with strictly increasing, 0x100-aligned offsets. Record `C-1` equals the file size in 57 of 57. Blocks are contiguous up to the recorded padding | Record scan (`BINARY`, `CROSS_SAMPLE`) | Confirmed | RDS5V-F02, RDS5V-F03 | Record 0's `hi` carries `0x10000000` in one store and `0x20000000` in another; meaning **Unknown** |
| RDS5-F06 | The word at `+0x0C` has bit 0 equal to bit 32 of the virtual payload size and bits 1..31 equal to `0x16000000` in 57 of 57 stores. The earlier "version" reading is superseded | Header scan, arithmetic (`BINARY`, `CROSS_SAMPLE`) | Confirmed (bit-32 relation and constant upper bits), Unknown (meaning of the upper bits) | RDS5V-F04 | The sample does not show whether the upper bits are a version, a marker or another field |
| RDS5-F07 | The ETPF chunk sits at `align_up(0x10 + 8*C, 0x100)` with ASCII `ETPF`, a constant `0x27A` at `+0x04`, a descriptor count at `+0x08` and `field_m` at `+0x0C` | Header scan (`BINARY`, `CROSS_SAMPLE`) | Confirmed (positions, constant in 57 of 57) | RDS5V-F02, RDS5V-F03 | `0x27A` is not shown to be a version |
| RDS5-F08 | `descriptor_count` 16-byte descriptors follow the ETPF header. The descriptor table is fully consumed by `descriptor_count` records in every store | Header scan (`BINARY`, `CROSS_SAMPLE`) | Confirmed | RDS5V-F03 | Other field meanings are covered by RDS5-F31 |
| RDS5-F09 | The nonzero ETPF content ends at `chunk_pos + 0x10 + 0x20*N + M`. The byte before that offset is nonzero and the byte at it is zero in 57 of 57. The region after the descriptor table is `16*N + M` bytes: `N*8` keys and `8N + M` opaque bytes | Header scan, arithmetic (`BINARY`, `CROSS_SAMPLE`) | Confirmed (nonzero end), Probable (region length) | RDS5V-F03 | The chunk length is not stored, so a longer region followed by zero padding cannot be excluded |
| RDS5-F10 | All 918,223 class-`0x20` blocks start `0x78 0xDA`. A 6,357-block sample was fully inflated with a verified checksum and end-of-stream; 6,357 succeeded, 0 failed, and consumed length equalled `span - padding` in every case | Block header census, full inflate (`BINARY`, `CROSS_SAMPLE`) | Confirmed | RDS5V-F07, RDS5V-F09 | First two bytes checked for all 918,223 blocks. Full inflate sampled up to 150 blocks per store, evenly spaced |
| RDS5-F11 | **Superseded** by RDS5-F23 and RDS5-F26. The storage form is not a two-bit selector `(high_byte >> 2) & 3`; that mask covers only bits 26..27 and merges distinct classes | Block header census (`BINARY`, `CROSS_SAMPLE`) | Rejected | RDS5V-F08, RDS5V-F10 | Kept for traceability; see RDS5-F27 for the 82-block reading |
| RDS5-F12 | Block records' `hi[0:19]` is the 20-bit virtual counter `floor(virtual / 0x4000)`; `hi[20:31]` is the padding count. `virtual[next] - virtual[this]` equals the inflated byte count in 6,357 of 6,357 sampled zlib blocks | Full inflate, arithmetic (`BINARY`, `CROSS_SAMPLE`) | Confirmed for zlib and stored classes; untested for undecoded classes | RDS5V-F12 for the payload size | The earlier `hi[0:16]` counter reading is superseded; the 20-bit counter does not wrap in the sample |
| RDS5-F13 | **Superseded** by RDS5-F29. `hi[16:32]` is not one unknown 16-bit value: bits 16..19 are counter bits and bits 20..31 are the padding count | Record scan, padding scan (`BINARY`, `CROSS_SAMPLE`) | Rejected as a single field | RDS5V-F11 | Kept for traceability |
| RDS5-F14 | The low bits of each descriptor locator are a page counter in 0x1000-byte units. The five-entry sample holds pages `1, 0x11, 0x21, 0x31, 0x41` and five blocks of 0x10000 bytes. Every locator page is a block start in 357,115 of 357,115 descriptors | Header scan, bounded inflate, arithmetic (`BINARY`, `CROSS_SAMPLE`) | Confirmed on one sample; Probable generally | RDS5V-F12, RDS5-F33 | Direct size correspondence is shown on one store only |
| RDS5-F15 | **Superseded** by RDS5-F31. The 16-byte items are descriptors with dimensions, mip field, flags, format id, array field, kind, tile mode and locator | Header scan (`BINARY`, `CROSS_SAMPLE`) | Confirmed (structure), Unknown (several meanings) | RDS5V-F14 | Kept for traceability |
| RDS5-F16 | The record offset field is 24 bits of 0x100-byte units under the six-bit class description, so a container cannot address 4 GiB or more. The four-bit class description would give 26 bits; the population does not discriminate them | Arithmetic (`BINARY`, `CROSS_SAMPLE`) | Confirmed for the 24-bit reading; Unknown between the two readings | — | The largest file is 2,828,296,704 bytes |
| RDS5-F17 | The first block is at `chunk_pos + align_up(0x10 + 0x20*N + M, 0x1000) + 0x100 * (record0.second_word >> 28)`. The extra term is 0 in 55 stores, `0x100` in one and `0x200` in another | Header scan, arithmetic (`BINARY`, `CROSS_SAMPLE`) | Confirmed (relation in 57 of 57), Unknown (flag meaning) | RDS5V-F13, RDS5-F20 | Reading the term as a count of 0x100-byte units is unproven. A reader should report a mismatch, not reject |
| RDS5-F18 | **Superseded** by RDS5-F27. The 82 blocks that the old mask left unexplained split into 77 class-`0x10` and 5 class-`0x00` blocks | Block header census (`BINARY`, `CROSS_SAMPLE`) | Rejected as an anomaly class | RDS5V-F09 | Kept for traceability |
| RDS5-F19 | Descriptor `w0` low bits encode `width - 1` and part of `height - 1`. The earlier `0xC000 \| ((1 << k) - 1)` pattern on the low 16 bits is a consequence of power-of-two dimensions | Header scan (`BINARY`, `CROSS_SAMPLE`) | Confirmed (field positions), Unknown (remaining bits) | RDS5V-F14 | The pattern is not universal and must not be used as a validator |
| RDS5-F20 | In the 238,897,664-byte vfx sample the application and the parser both place the first block at `0x24000`: ETPF at `0x8E00`, `descriptor_count` 1,722, `field_m` 54,816, content end `0x23B70`, 0x1000-aligned end `0x23E00`, flag term `0x200` | App inspection, header scan, arithmetic (`BINARY`) | Confirmed (one sample) | RDS5-F17, RDS5V-F13 | One sample. The application reports 4,526 blocks: class `0x20` 4,333, `0x04` 85, `0x0C` 3, `0x14` 44, `0x18` 4 and `0x1C` 57 |
| RDS5-F21 | In the 38,656-byte five-entry sample the application and the parser agree: five descriptors hold pages `1, 0x11, 0x21, 0x31, 0x41`, five zlib blocks decode to 327,680 bytes, `field_m` is 144, content end `0x240`, first block `0x1100`, and the payload size is 331,776 | App inspection, bounded inflate, header scan (`BINARY`) | Confirmed (one sample) | RDS5-F14, RDS5V-F12 | One sample. Page counter unit is 0x1000 on this sample; general mapping to blocks is not established |
| RDS5-F22 | No counterexample to RDS5-F17 or RDS5-F21 was found. On the vfx sample the application reports 751,046,656 decoded zlib bytes against the declared 766,107,648, but 193 blocks use unidentified classes and are not decoded, so the declared total cannot be checked on that file | App inspection, bounded inflate (`BINARY`) | Confirmed (observation) | — | The difference is a boundary of the zlib-only check, not a contradiction of the layout relation |
| RDS5-F23 | The storage class is read as bits 26..29, reported as the six-bit id `four_bit << 2`; the same class under the four-bit reading is that id divided by four. The eight observed ids are `0x00` 5, `0x04` 102,725, `0x0C` 35, `0x10` 77, `0x14` 333, `0x18` 268, `0x1C` 5,167 and `0x20` 918,223. Bits 24 and 25 are zero in all 1,026,947 records; all ids are multiples of four. A record with either bit set is accepted and reported as ambiguous | Record scan (`BINARY`, `CROSS_SAMPLE`) | Confirmed (distribution and zero bits), Unknown (which field description is intended) | RDS5V-F08, RDS5V-F09 | A store at or above 4 GiB would discriminate the six-bit/24-bit-offset and four-bit/26-bit-offset descriptions; none is in the sample. See RDS5-F37 |
| RDS5-F24 | Class `0x20` is a complete zlib stream. All 918,223 class-`0x20` blocks start `0x78 0xDA`; 6,357 sampled blocks inflate to end-of-stream with the checksum verified, 0 fail, and `consumed = span - padding` in 6,357 of 6,357 | Block header census, full inflate, padding scan (`BINARY`, `CROSS_SAMPLE`) | Confirmed | RDS5V-F07, RDS5V-F09 | First two bytes cover all class-`0x20` blocks; full inflate is a sample |
| RDS5-F25 | Class `0x00` is stored bytes. A decoder returns the first `span - padding` bytes verbatim. The five blocks have `span - padding` equal to the virtual length and zero padding; sizes are 4,096 or 16,384 bytes. A stored block whose length differs from the declared virtual length is reported | Full inflate, padding scan, arithmetic (`BINARY`, `CROSS_SAMPLE`) | Confirmed | RDS5V-F09 | Five blocks in two stores |
| RDS5-F26 | Six storage classes are not decoded: `0x04` 102,725, `0x0C` 35, `0x10` 77, `0x14` 333, `0x18` 268, `0x1C` 5,167. None starts with a zlib header | Block header census (`BINARY`, `CROSS_SAMPLE`) | Confirmed (counts and absent zlib header), Unknown (payload format) | RDS5V-F08, RDS5V-F10 | The payload format and any pixel format are not established |
| RDS5-F27 | The former 82-block anomaly is explained by the too-narrow mask. The 82 blocks are 77 class-`0x10` and 5 class-`0x00`; the five class-`0x00` blocks satisfy the stored length identity. There is no anomaly class | Block header census, arithmetic (`BINARY`, `CROSS_SAMPLE`) | Confirmed | RDS5V-F09 | The old mask `(high_byte >> 2) & 3` drops bits 28 and 29 |
| RDS5-F28 | The validated virtual position is `virtual = (hi & 0xFFFFF) * 0x4000 + ((lo >> 30) & 3) * 0x1000`. The candidate form with an extra `+0x1000` constant is rejected. For zlib, `virtual[next] - virtual[this]` equals the inflated byte count in 6,357 of 6,357 | Full inflate, arithmetic (`BINARY`, `CROSS_SAMPLE`) | Confirmed for zlib and stored classes | RDS5V-F13 | Counterexamples: none in the sample. Untested for undecoded classes |
| RDS5-F29 | The second word is a 20-bit counter plus a 12-bit padding count: `padding = hi >> 20`, `stored length = span - padding`. The 12-bit field takes all 4,096 values. The counter's top bit `hi[19]` is zero in every block, so only 19 counter bits are exercised; `hi[16:19]` takes 0..6. The trailing `padding` bytes were zero in 5,754 blocks sampled across all eight classes, with 0 non-zero | Record scan, padding scan (`BINARY`, `CROSS_SAMPLE`) | Confirmed for zlib and stored classes; observed for all classes | RDS5V-F11 | The zero-padding rule was checked on a sample of up to 40 blocks per class per store, not on every block. The 20th counter bit is untested |
| RDS5-F30 | The payload size is `size_low | ((size_high & 1) << 32)` and equals the end record's virtual position in 57 of 57 stores: 39 below 4 GiB and 18 with bit 32 set. The largest payload is 6,556,999,680 bytes | Header scan, record scan, arithmetic (`BINARY`, `CROSS_SAMPLE`) | Confirmed | RDS5V-F12 | The upper bits of `size_high` remain **Unknown** |
| RDS5-F31 | Descriptors are 16 bytes: `w0` width-1, height-1 and mip; `w1` flags, format id, array field, kind and tile mode; a 64-bit locator. Across 357,115 descriptors the observed ranges are width 4..4,096, height 2..4,096, mip 0..9, format id 10..99, array 0..63, kind {2,4,6,10}, tile {0..3,9..12}, flags 0..3. No range violation was found | Descriptor scan (`BINARY`, `CROSS_SAMPLE`) | Confirmed (field positions and distributions), Unknown (several meanings) | RDS5V-F14 | The descriptor count is a texture count, not a block count |
| RDS5-F32 | The `N*8` bytes after the descriptor table are `N` little-endian 64-bit keys. In all 56 stores with at least two descriptors the keys are strictly increasing; the 57th has one descriptor and cannot test ordering | Key scan (`BINARY`, `CROSS_SAMPLE`) | Confirmed | — | Key values are not named or published. The remaining `8N + M` bytes are opaque |
| RDS5-F33 | The low 21 bits of every descriptor locator equal the first virtual page of a block. All 357,115 descriptor pages are block starts. Descriptor 0's page equals the first block's page in 57 of 57, and locator pages increase with descriptor order in every store with at least two descriptors | Descriptor scan, record scan (`BINARY`, `CROSS_SAMPLE`) | Confirmed | RDS5V-F13 | The upper 43 bits of the locator are nonzero in 267,867 descriptors and remain **Unknown** |
| RDS5-F34 | Among descriptors whose first block is not class `0x20`, the class correlates with the format id: `0x04` with formats 71 and 72, `0x1C` with 98 and 99, `0x10` with 80, `0x14` with 83, `0x18` with 95 and 96, `0x0C` with 77, and `0x00` with 98 and 99. All 1,774 format-28 descriptors start with class `0x20` | Descriptor scan, block header census (`BINARY`, `CROSS_SAMPLE`) | Confirmed (correlation), not a decode | — | The correlation does not establish what the six undecoded classes contain or any pixel format |
| RDS5-F35 | One byte-level texture chain is established in the platform sample: descriptor format id 98, 1,024 x 512, mip 0, kind 2, tile mode 0, locator page 1; one class-`0x20` block from virtual `0x1000` to `0x81000`; 524,288 inflated bytes; `inflated = width * height * 1`; the payload size equals the end record; one level is present | Header scan, descriptor scan, full inflate, arithmetic (`BINARY`) | Confirmed (byte level) | — | The block encoding, the tile-mode meaning and the element order are **Unknown** |
| RDS5-F36 | A pixel attempt under a documented 16-byte 4 x 4 endpoint layout (8-byte colour endpoints and indices, 8-byte alpha endpoints and indices) gives legal endpoints by construction and an adjacent-pixel difference of 44.6, against 77.8 for a raw 16-byte-per-tile reading. 12,719 of 32,768 tiles use the three-colour branch and 13,989 use the six-alpha branch; alpha correlates with luminance at -0.12 | Full inflate, arithmetic (`BINARY`), synthetic fixtures (`SYNTHETIC`) | Speculative (consistency only) | — | No lower mip exists, so the box-downsample test is not applicable. This is not a codec identification and not a confirmed pixel decode |
| RDS5-F37 | Open discrimination candidate: a record with bit 24 or bit 25 set. No such record is in the 57-store sample. The parser accepts it, takes the class from bits 26..29, and reports the six-bit reading as ambiguous. The first such record that is consistent with the four-bit offset reading or the six-bit class reading would be the first evidence to discriminate the two field descriptions | Record scan (`BINARY`, `SYNTHETIC`) | Unknown (no sample record) | — | A record with a set bit alone does not decide the question; the offset consistency must also be checked |
| RDS5-F38 | The control sample byte chain was reproduced independently of the committed parser: 1,024 x 512, mip 0, flags 1, format 98, kind 2, tile 0, page 1; one class-`0x20` block, stored span 218,624, padding 213, stream 218,411; zlib to end-of-stream, 524,288 bytes, consumed 218,411; virtual `0x1000` to `0x81000`; end record equals the payload size; the level count is unique at 1 | Header, record, descriptor and payload data; independent scratch parser (`BINARY`) | Confirmed | RDS5-F35 | One sample. No pixel format, element order or codec identity |
| RDS5-F39 | Observed storage units by format id: 28 = 4 bytes per texel, 54 = 2 bytes per texel, 71/72/80 = 8 bytes per 4 x 4 tile, 83/98/99 = 16 bytes per 4 x 4 tile. For 98 and 99 the extent is degenerate with 1 byte per texel on dimensions divisible by 4. These are size fits, not codec names | Descriptor scan, decoded extents, size model (`BINARY`, `CROSS_SAMPLE`) | Confirmed for 54, 71 and 72 on the tested class; Probable for 28, 80, 83, 98 and 99 | RDS5-F40, RDS5-F41 | The unit is not a pixel-format identity. Other format ids in the descriptor table are not mapped |
| RDS5-F40 | Mip check over block-aligned levels with a stated candidate decoder: passing checks were observed for format ids 71, 72, 77, 80 and 83 at tile modes 1, 2 and 3, on both 8-byte and 16-byte block candidates. Selection: up to 40 clean simple-2D descriptors per `(format id, tile mode)` with decoded extent at most 1 MiB. Candidate decoders: BC1 for 71 and 72, single-plane BC4 for 77 and 80, two-plane BC4 for 83. Threshold 25.0 mean absolute error. Levels are peeled only while their start is an observed block start. The per-class pass rate is not uniform across tile modes and formats | Descriptor scan, bounded decode, arithmetic (`BINARY`, `CROSS_SAMPLE`) | Probable (the decoders are candidate specifications; the level layout is observed) | RDS5-F39 | The exact per-class counts depend on a scratch-only selection driver and are not reproducible from this repository alone. The non-uniform rate means the candidate decoder is incomplete for those classes. The check covers only whole-block levels and excludes tile mode 0. No codec identity follows |
| RDS5-F41 | Linear 1-byte-per-texel is rejected for format 98 and 99 and for the control sample by block-first-byte structure. For the control sample, 32,768 candidate 16-byte blocks have no zero first byte, 65.54% of block-first bytes are multiples of 16 against 32.53% over all decoded bytes, and the lowest-set-bit histogram occupies only bits 0..7. A row-major 8-bit image would preserve the all-byte fraction in a 1-in-16 subsample. The observation supports a mode-prefixed 16-byte block, not a named codec | Payload data, arithmetic (`BINARY`) | Confirmed (observation and rejection of the linear reading); Probable (16-byte block interpretation) | RDS5-F39 | The test does not identify the block encoding, its element order, or that every format-98 block uses the same mode |
| RDS5-F42 | Candidate pixel interpretations rejected on measured error, not visual appearance: BC4 for format 71 and nibbles for format 71 produced larger scratch errors than the BC1 candidate; BC1, BC3 and linear 8-bit decode of format 98 stayed far above the 25.0 threshold in a scratch mip comparison. The exact scratch values are not committed, so the rejections are private-evidence supported only | Bounded decode, arithmetic (`BINARY`) | Rejected (candidates) | RDS5-F40 | A rejection applies to the tested sample and candidate, not to every texture with the same format id. The scratch errors cannot be reproduced from the repository alone |
| RDS5-F43 | Provisional level stream model for format 71: levels are stored smallest mip first, each in a slot of `max(size, 0x100)` bytes, right-aligned inside a 0x1000-multiple stream. On a 512 x 512 sample the 16 x 16, 32 x 32, 64 x 64 and 128 x 128 levels start at 1,280, 1,536, 2,048 and 4,096; the 16 x 16 level has 128 content bytes in a 256-byte slot | Full inflate, mip comparison, arithmetic (`BINARY`) | Probable | RDS5-F40 | The 0x100 minimum slot and the prelude rule are not established for formats or tile modes other than the sampled class |
| RDS5-F44 | The descriptor `mip` field is not a recovered level count. A size model over 305,253 clean simple-2D descriptors admits no count for some rows, one count for others and several counts when the smallest slots stay inside the same page. Where a count is unique it equals `mip` for some classes and `mip + 1` for others. Level-count recovery is therefore ambiguous and is not used to decide a pixel layout | Descriptor scan, size model, mip comparison (`BINARY`, `CROSS_SAMPLE`) | Unknown (field meaning and count rule) | — | The tail slots and the `flags` field may carry part of the missing rule. A content search that scans offsets was not accepted as evidence because it can fit noise |

Finding IDs `RDS5-F01` to `RDS5-F22` keep the numbering of the transferred
evidence. `RDS5-F23` to `RDS5-F37` are the iteration 10 measurements and the
open discrimination candidate. Superseded rows stay in the table so the earlier
reading is traceable; the corrections are recorded in the
[research history](research-history.md).

## Reproduction

The parser tests need no game files:

```sh
python -m unittest discover -s tools/rds5 -p "test_*.py"
```

The current suite reports 70 tests and 0 failures.

Texture candidate analysis over one descriptor:

```sh
python tools/rds5/textures.py probe <CONTAINER> --descriptor <N> --unit B8 --decoder bc1 --json
python tools/rds5/textures.py units
```

Structural inspection of a sample container:

```sh
python tools/rds5/rds5.py inspect <CONTAINER> --json --records --descriptors --headers
python tools/rds5/rds5.py scan <ROOT> --headers
python tools/rds5/rds5.py descriptors <CONTAINER> --json
python tools/rds5/rds5.py decode <CONTAINER> --block <N>
python tools/rds5/rds5.py reconstruct <CONTAINER> --descriptor <N> --bytes-per-texel 1 --levels 1
python tools/rds5/rds5.py reconstruct <CONTAINER> --descriptor <N> --max-total-bytes <B>
```

`<CONTAINER>` is a local read-only copy. `decode` and `reconstruct` print sizes,
offsets and per-class state. `--out` writes decoded bytes to an explicit path
through a temporary file and refuses a path that resolves to the input.
`reconstruct` applies `--max-total-bytes` per block and to the running total.

Expected values for the 57-store scan:

```text
summary: files=57 failures=0 blocks=1026833 descriptors=357115 layout_mismatches=0
classes[0x00=5 0x04=102725 0x0c=35 0x10=77 0x14=333 0x18=268 0x1c=5167 0x20=918223]
zlib_headers=918223 other_headers=108610
```

Expected platform reconstruction:

```text
range_start: 4096
range_end: 528384
block_count: 1
decoded_bytes: 524288
level_sizes: [524288]
size_matches: True
```

## Limits

- The meaning of the upper bits of `+0x0C`, the record `page_term` beyond the
  virtual arithmetic, the first-block flag and the descriptor tile mode remains
  **Unknown**.
- The payload format of classes `0x04`, `0x0C`, `0x10`, `0x14`, `0x18` and
  `0x1C` is **Unknown**. They are not decoded.
- The content and internal split of the `8N + M` region after the key table are
  **Unknown**.
- Full inflation covers 6,357 sampled zlib blocks. The remaining class-`0x20`
  blocks were classified by their first two bytes only.
- The virtual and padding relations are validated for zlib and stored classes
  only.
- No sampled record sets bit 24 or bit 25, so the class-field and offset-width
  descriptions remain undiscriminated (RDS5-F37).
- No pixel format, codec identity or asset name is claimed.
