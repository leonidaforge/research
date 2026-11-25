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
| Block header read | `BINARY`, `CROSS_SAMPLE` | First two bytes of each block, used to count storage forms |
| Bounded inflate | `BINARY` | zlib streams inflated with a fixed output cap; only sizes and end-of-stream state are recorded |
| Negative decode | `BINARY` | A stored range offered to zlib, gzip and raw DEFLATE, with the whole range required to decode as one stream |
| Arithmetic | `BINARY`, `CROSS_SAMPLE` | A layout formula checked against every sample |
| Parser tests | `SYNTHETIC` | Authored fixtures and mutation cases for the transferred parser |
| App inspection | `BINARY` | An independent implementation reads the same header, records, entries and block headers |

`BINARY` and `CROSS_SAMPLE` findings depend on a local `<ROOT>`. They are
private-evidence supported under `RESEARCH-POLICY.md` and reproducible from a lawful
copy of the same samples. `SYNTHETIC` findings exercise the parser contract, not the
native format.

## Sample

The transferred claims use the 57 containers whose aggregate counts are in RDS5V-F01
and RDS5V-F06. Two containers were rechecked locally with the application CLI:

| Label | Size | Purpose |
|---|---:|---|
| vfx sample | 238,897,664 | First-block relation with a nonzero flag term |
| five-entry sample | 38,656 | Entry page counter and `uncompressed_total` |

No game file was opened for writing. No block payload was printed or stored. Block
content is never reproduced.

## Findings

| ID | Claim | Evidence | Confidence | Independent check | Limits |
|---|---|---|---|---|---|
| RDS5-F01 | The magic is ASCII `RDS5` at offset 0 in all 57 samples | Header scan (`BINARY`, `CROSS_SAMPLE`) | Confirmed | RDS5V-F02 | One installation |
| RDS5-F02 | The fixed header is 0x10 bytes: `record_count` at `0x04`, `uncompressed_total` at `0x08`, `version` at `0x0C`. There is no separate header area between the records and 0x100; the 0x100 impression comes from small record arrays | Header scan (`BINARY`, `CROSS_SAMPLE`) | Confirmed | RDS5V-F02 | The 0x100-byte "header" only appears when the record array plus padding ends at 0x100 |
| RDS5-F03 | The record array starts at `0x10` and holds `record_count` 8-byte records. `align_up(0x10 + 8*C, 0x100)` equals the ETPF offset and record 0's offset in 57 of 57. Two samples place ETPF exactly at `0x10 + 8*C`, which rules out a `0x18` start | Record scan, arithmetic (`BINARY`, `CROSS_SAMPLE`) | Confirmed | RDS5V-F02 for the aligned relation | The exact `0x10 + 8*C` case rests on the two transferred samples; the independent check did not name them |
| RDS5-F04 | Record decode: `offset = (lo & 0xFFFFFF) * 0x100`, `high_byte = lo >> 24`, second word `hi` | Record scan (`BINARY`, `CROSS_SAMPLE`) | Confirmed | — | `hi[16:32]` meaning unknown (RDS5-F13) |
| RDS5-F05 | Record 0 locates the ETPF chunk. Records `1..C-2` are data blocks with strictly increasing, 0x100-aligned offsets. Record `C-1` equals the file size in 57 of 57. Blocks are contiguous up to 0x100 alignment | Record scan (`BINARY`, `CROSS_SAMPLE`) | Confirmed | RDS5V-F02, RDS5V-F03 | Record 0's `hi` carries `0x10000000` in one sample and `0x20000000` in another; meaning **Unknown** |
| RDS5-F06 | `version` is `0x16000000` (39 samples) or `0x16000001` (18). No structural field or formula differs between the groups. The value does not follow the observed directory class | Header scan, arithmetic (`BINARY`, `CROSS_SAMPLE`) | Confirmed (values and invariants), Unknown (meaning of bit 0) | RDS5V-F04 | The sample does not prove that both versions are semantically equivalent |
| RDS5-F07 | The ETPF chunk sits at `align_up(0x10 + 8*C, 0x100)` with ASCII `ETPF`, a constant `0x27A` at `+0x04`, an entry count at `+0x08` and `field_m` at `+0x0C` | Header scan (`BINARY`, `CROSS_SAMPLE`) | Confirmed (positions, constant in 57 of 57) | RDS5V-F02, RDS5V-F03 | `0x27A` is not shown to be a version |
| RDS5-F08 | `entry_count` 16-byte entries follow the ETPF header. The entry table is fully consumed by `entry_count` records in every sample | Header scan (`BINARY`, `CROSS_SAMPLE`) | Confirmed | RDS5V-F03 | Field meanings mostly **Unknown** (RDS5-F15) |
| RDS5-F09 | Nonzero content of the ETPF chunk ends at `chunk_pos + 0x10 + 0x20*N + M`. The byte before that offset is nonzero and the byte after it is zero in 57 of 57. The region after the entry table is `16*N + M` bytes | Header scan, arithmetic (`BINARY`, `CROSS_SAMPLE`) | Confirmed (nonzero end), Probable (region length) | RDS5V-F03 | The chunk length is not stored, so a longer region followed by zero padding cannot be excluded |
| RDS5-F10 | Block payloads selected as zlib start with `0x78 0xDA` in all 918,223 zlib blocks; inflating the whole block range succeeds, reaches end-of-stream and yields a multiple of 0x1000 bytes | Bounded inflate, block header read (`BINARY`, `CROSS_SAMPLE`) | Confirmed | RDS5V-F07, RDS5V-F09 | First two bytes checked for all 918,223 zlib blocks. Clean inflate verified for 2,173 blocks |
| RDS5-F11 | Storage form follows `(high_byte >> 2) & 3` for all but 82 blocks. Value 0 selects zlib (918,223 blocks); values 1, 2 and 3 an unidentified codec. Non-zlib data does not decode as zlib, gzip or raw DEFLATE with a 0..8-byte prefix under a whole-range criterion | Block header read, negative decode (`BINARY`, `CROSS_SAMPLE`) | Confirmed (correlation, negative results), Unknown (codec) | RDS5V-F08, RDS5V-F09, RDS5V-F10 | Codec attempts covered a small block sample. Selector 2 covers 268 blocks with `high_byte` `0x18`; the transferred text originally omitted it |
| RDS5-F12 | Block records' `hi[0:16]` is `floor(cumulative_uncompressed / 0x4000) mod 0x10000`. `uncompressed_total = 0x1000 + sum(uncompressed block sizes)` | Bounded inflate, arithmetic (`BINARY`, `CROSS_SAMPLE`) | Confirmed for two complete samples; Probable elsewhere | RDS5V-F12 for `uncompressed_total` | Rounding to 0x4000 hides up to 16 KiB per block; the counter wraps at 1 GiB. The record counter was not independently rechecked |
| RDS5-F13 | Block records' `hi[16:32]` is a 16-bit value with 19,174 distinct values across 1,026,833 records, maximum `0xFFF3`, uncorrelated with block size | Record scan (`BINARY`, `CROSS_SAMPLE`) | Unknown | RDS5V-F11 | Probably a checksum or hash, not demonstrated |
| RDS5-F14 | ETPF entry `+0x08`: the low 16 bits are a wrapping page counter in 0x1000-byte units, ordered across entries. Consecutive differences modulo 65536 are at most `0x1560` in all 57 files | Header scan, bounded inflate, arithmetic (`BINARY`, `CROSS_SAMPLE`) | Confirmed on one sample; Probable generally | RDS5V-F12 | Direct size correspondence shown on one five-entry sample |
| RDS5-F15 | ETPF entry `+0x00`, `+0x04` and `+0x0C` hold structured bit fields with small value sets (202, 133 and 24 distinct values) | Header scan (`BINARY`, `CROSS_SAMPLE`) | Unknown | RDS5V-F14 | No meaning established |
| RDS5-F16 | The record offset field is 24 bits of 0x100-byte units, so a container cannot address 4 GiB or more | Arithmetic (`BINARY`, `CROSS_SAMPLE`) | Confirmed | — | The largest sample is 2,828,296,704 bytes |
| RDS5-F17 | The first block is at `chunk_pos + align_up(0x10 + 0x20*N + M, 0x1000) + 0x100 * (record0.second_word >> 28)`. The extra term is 0 in 55 samples, `0x100` in one and `0x200` in another | Header scan, arithmetic (`BINARY`, `CROSS_SAMPLE`) | Confirmed (relation in 57 of 57), Unknown (flag meaning) | RDS5V-F13, RDS5-F20 | Reading the term as a count of 0x100-byte units is unproven. A reader should report a mismatch, not reject |
| RDS5-F18 | 82 blocks carry `high_byte & 0x0F` = 0 but do not start with `0x78`. Their high bytes are `0x10`, `0x40`, `0x50`, `0x80`, `0x90` and `0xD0`. 77 start with `0x30`-`0x36` then `0xDE`; 5 start with other bytes | Block header read (`BINARY`, `CROSS_SAMPLE`) | Confirmed (observation), Unknown (storage form) | RDS5V-F09 | Negative decode used the whole-range criterion. Census over all 57 containers |
| RDS5-F19 | ETPF entry `+0x00` low 16 bits equal `0xC000 \| ((1 << k) - 1)` in 357,114 of 357,115 entries. The exception is `w0 = 0x100040FF` (low 16 bits `0x40FF`, bit 15 clear) | Header scan (`BINARY`, `CROSS_SAMPLE`) | Confirmed (observation), Unknown (meaning) | RDS5V-F14 | The pattern is not universal and must not be used as a validator |
| RDS5-F20 | In the 238,897,664-byte vfx sample the application and the branch parser both place the first block at `0x24000`: ETPF at `0x8E00`, `entry_count` 1,722, `field_m` 54,816, content end `0x23B70`, 0x1000-aligned end `0x23E00`, flag term `0x200` | App inspection, header scan, arithmetic (`BINARY`) | Confirmed (one sample) | RDS5-F17, RDS5V-F13 | One sample. The application reports 4,526 blocks: 4,333 zlib, 129 selector 1, 4 selector 2 and 60 selector 3 |
| RDS5-F21 | In the 38,656-byte five-entry sample the application and the branch parser agree: five entries hold pages `1, 0x11, 0x21, 0x31, 0x41`, five zlib blocks decode to 327,680 bytes, `field_m` is 144, `content_end` is `0x240`, the first block is `0x1100`, and `uncompressed_total` is 331,776 | App inspection, bounded inflate, header scan (`BINARY`) | Confirmed (one sample) | RDS5-F14, RDS5V-F12 | One sample. Page counter unit is 0x1000 on this sample; general mapping to blocks is not established |
| RDS5-F22 | No counterexample to RDS5-F17 or RDS5-F21 was found. On the vfx sample the application reports 751,046,656 decoded zlib bytes against the declared 766,107,648, but 193 blocks use unidentified selectors and are not decoded, so the declared total cannot be checked on that file | App inspection, bounded inflate (`BINARY`) | Confirmed (observation) | — | The difference is a boundary of the zlib-only check, not a contradiction of the layout relation |

Finding IDs `RDS5-F01` to `RDS5-F19` keep the numbering of the transferred evidence.
`RDS5-F20` to `RDS5-F22` are the local application checks added during transfer. The
mapping and the changes to earlier claims are recorded in the
[research history](research-history.md).

## Reproduction

The parser tests need no game files:

```sh
python -m unittest discover -s tools/rds5 -p "test_*.py"
```

The transferred suite reports 33 tests and 0 failures.

Structural inspection of a sample container:

```sh
python tools/rds5/rds5.py inspect <CONTAINER> --json --records --block <N> --inflate
lforge binary inspect <CONTAINER> --json --blocks --verify
```

`<CONTAINER>` is a local read-only copy. The application command prints structure and
decoded sizes only.

The local `lforge` reports `lforge 0.1.0`. Its RDS5 parser and inspection path are
unchanged from `leonidaforge/leonida-forge` app commit `92af6e2`; the local binary was
built from a later commit, and the RDS5 module and its inspection path show no diff
between the two. The two local checks above used this build.

Expected values:

| Sample | `record_count` | Blocks | Entries | `field_m` | First block | Other |
|---|---:|---:|---:|---:|---:|---|
| vfx sample | 4,528 | 4,526 | 1,722 | 54,816 | `0x24000` | flag term `0x200`; 4,333 zlib |
| five-entry sample | 7 | 5 | 5 | 144 | `0x1100` | pages `1, 0x11, 0x21, 0x31, 0x41`; 327,680 decoded bytes |

## Limits

- The meaning of the version bit, the record `high_byte` upper bits, the second word's
  high 16 bits and every ETPF entry field except the page counter remains **Unknown**.
- The identity of the non-zlib codec is **Unknown**. Selectors 1, 2 and 3 and the 82
  selector-0 exceptions are not decoded.
- The content and internal split of the `16*N + M` region are **Unknown**.
- Only nine files had all their zlib blocks inflated, plus eight sampled blocks of a
  tenth. The remaining zlib blocks were classified by their first two bytes only.
- Entry count equals block count in only 3 of 57 samples, and no relationship between
  ETPF entries and block boundaries is established.
- No pixel format, texture decode, asset reconstruction or RAGE resource relationship
  is claimed.
