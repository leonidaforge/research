# PSIN evidence index

Payload observations from the Scarlett build [e95020b2](../../builds/gta-vi/scarlett-e95020b2/README.md). No executable code path was traced. Every finding is **Private-evidence supported**: the selection and the tools are public, but the payloads remain outside this repository.

## Sample

| Property | Value |
| -------- | ----- |
| PSIN files | 918 decoded payloads |
| Unique payloads | 757 by SHA-256 of the decoded bytes |
| Family split | 695 `LSCH`, 62 `PMAP` |
| Sources | all readable type 11 rows from the 22 top-level archives and from 18 nested archives under `<GAME_ROOT>/data.rpf` at or below 2 MiB |
| Sizes | 216 to 17,406,784 bytes |
| First section offsets | 48 to 16,684,176 |
| Signature | `50 53 49 4E` at offset 0 in all 757 |

The 918 files collapse to 757 unique payloads because overlapping nested archives and repeated rows carry identical bytes. Uniqueness is the SHA-256 of the decoded payload.

### Relation to earlier counts

The PSIN-F01 claim in the earlier revision recorded 103 unique payloads: 18 earlier payloads plus 85 additional payloads. The 85 additions combine the deterministic top-level sample and the depth-1 payloads; duplicates are removed by SHA-256 before the total is taken. The rows for the 82 expanded-extraction payloads and the 13 depth-1 payloads describe the two source sets, not additional components. The full recount in this document is 757 unique payloads, with 695 `LSCH` and 62 `PMAP`.

## Evidence types

| Type | Meaning |
| ---- | ------- |
| `BINARY` | Bytes read from decoded RPF9 payloads, not traced in executable code |
| `CROSS_SAMPLE` | A property compared across distinct payloads |
| `SYNTHETIC` | Independently built fixtures that test the repository classifier and checksum implementation |

## Findings

| ID | Claim | Evidence | Confidence | Limits |
| -- | ----- | -------- | ---------- | ------ |
| PSIN-F01 | Payloads start with ASCII `PSIN` (`0x4E495350`) at offset 0 | `BINARY`, `CROSS_SAMPLE` | Confirmed | 757 unique payloads, one build |
| PSIN-F02 | The big-endian `u32` at `+0x04` is the offset of the first tagged section. A printable four-byte tag starts there, and walking `tag + big-endian length` from that offset ends exactly at the payload size in 757 of 757 payloads. The length includes the eight-byte tag and length header | `BINARY`, `CROSS_SAMPLE` | Confirmed (sample) | Tag and body meanings are Unknown |
| PSIN-F03 | `+0x04` is not the payload size or a section count. 0 of 757 big-endian `u32` values at `+0x04` equal the payload size. `+0x06` is not the size either; it equals the low 16 bits of the `+0x04` offset, and 179 offsets are above `0xFFFF` | `CROSS_SAMPLE` | Confirmed (rejected readings) | Only the tested integer readings were rejected |
| PSIN-F04 | The tagged-section walk has four observed sequences: 695 payloads use `LSCH` -> `LENM` -> `LSNS` -> `LGID` -> `LRSC` -> `CHKS`; 55 use `PMAP` -> `PSCH` -> `PSIG` -> `STNS` -> `CHKS`; six insert `STDN` before `STNS`; one inserts `STFN` before `STNS` | `BINARY`, `CROSS_SAMPLE` | Confirmed (sequences) | Tag strings are raw bytes, not semantic names |
| PSIN-F05 | Several section bodies have repeated length properties: `LSCH` body is a multiple of 16 in 695 of 695; `LRSC` body is 80 in 695 of 695; `CHKS` body is 12 in 757 of 757; `PMAP` and `STNS` bodies are multiples of 16 in 62 of 62; `STDN` bodies are multiples of 16 in six of six. `PSCH`, `PSIG`, `LENM`, `LSNS` and `LGID` have no single body modulus | `CROSS_SAMPLE` | Confirmed (lengths); Unknown (meaning) | Body contents are not decoded into records |
| PSIN-F06 | Bytes `+0x08..+0x0F` are family-specific, not a single unknown header field. In `LSCH` they are the first descriptor word and length. In `PMAP` they are eight `0x70` bytes in 62 of 62 payloads. The earlier 84-value aggregate mixed the two families | `BINARY`, `CROSS_SAMPLE` | Confirmed (sample) | The `LSCH` descriptor word is uninterpreted |
| PSIN-F07 | Type ID does not identify PSIN. Decoded type 11 rows in this recount contain 757 PSIN payloads and 238 RBF0 payloads. An earlier inventory also found PSIN in type 93 and 94 rows; that claim is outside this type 11 recount | `BINARY`, `CROSS_SAMPLE` | Confirmed (sample) | Full type-ID population was not surveyed |
| PSIN-F08 | The first section offset is not always 16-byte aligned. All 695 `LSCH` payloads are aligned, while 10 of 62 `PMAP` payloads are unaligned. The unaligned offsets are 72, 104, 152, 152, 260, 344, 888, 2456, 307048 and 972552 | `CROSS_SAMPLE` | Confirmed (counterexamples) | Ten counterexamples in 757 unique payloads |
| PSIN-F09 | Runs of `0xAA` and `0x70` are partly structural. `LSCH` descriptors carry eight `0xAA` bytes at `+0x08`, and `PMAP` pre-section areas begin with eight `0x70` bytes. Other runs inside bodies or pre-section areas remain unassigned | `BINARY`, `CROSS_SAMPLE` | Confirmed (two markers); Speculative (other runs) | Other runs could be padding or data |
| PSIN-F10 | The `LSCH` pre-section area holds a 16-byte descriptor table at `+0x08`. Each descriptor is an uninterpreted little-endian `u32` at `+0x00`, a little-endian `u32` length at `+0x04`, and eight `0xAA` bytes at `+0x08`. The count `C` is unique in 695 of 695 payloads under `0x10 + 16 * C + sum(align16(length_i)) == first_section_offset`. `C` ranges from 1 to 1093. Without per-descriptor alignment the unique count falls to 96 of 695; a table at `+0x10` or a length at `+0x00` fits 0 of 695. The relation has no solution for all 62 `PMAP` payloads | `BINARY`, `CROSS_SAMPLE` | Confirmed (sample) | The `+0x00` word is not established as a name or hash; the formula is validated only on this container family |
| PSIN-F11 | The `CHKS` section has a 20-byte section length and a 12-byte body of big-endian total length, big-endian checksum, and ASCII `zppp`. The total-length word equals the payload size in 757 of 757 payloads. The checksum is a one-at-a-time hash over signed bytes seeded with `0x3FAC7125`, over the payload with the total-length and checksum words zeroed; it verifies in 757 of 757 payloads. An unsigned-byte variant matches 0 of 757 | `BINARY`, `CROSS_SAMPLE`, `SYNTHETIC` | Confirmed (sample) | The seed is unexplained; the variant is validated only on this container family |
| PSIN-F12 | The `PMAP` family has a stable header-area marker: eight `0x70` bytes at `+0x08` in 62 of 62 unique payloads. The marker is absent from the `LSCH` descriptors | `BINARY`, `CROSS_SAMPLE` | Confirmed (sample) | Marker meaning is Unknown |
| PSIN-F13 | The two families share the outer framing and the `CHKS` integrity section, but differ in the pre-section grammar. The descriptor arithmetic fits every `LSCH` payload and no `PMAP` payload; all unaligned first-section offsets are `PMAP`. They are two grammars of one container, not separate file formats | `BINARY`, `CROSS_SAMPLE` | Confirmed (sample) | Family purpose and record semantics are Unknown |
| PSIN-F14 | The `PMAP` pre-section area is not constant. The 62 unique areas have 62 distinct SHA-256 values; only the first eight bytes are constant. It is not a fixed-stride table: the number of `0x70` runs ranges from 1 to 41 and their positions vary. No tested compressed-stream signature occurs at `+0x10`, and zlib, gzip, bzip2 and LZMA produced no non-empty output. No `PSIN`, `RBF0` or section tag occurs inside the area. These negative tests stand; PSIN-F15 to PSIN-F17 supersede the earlier conclusion that the area had no decoded grammar | `BINARY`, `CROSS_SAMPLE` | Confirmed (negative tests) | Tests the old whole-area reading; the block table is now decoded at the block level |
| PSIN-F15 | The `PMAP` pre-section area is a block table. It is eight `0x70` bytes at `+0x08`, then blocks from `0x10`, with `0x70` padding between blocks to 16-byte boundaries and no padding after the last block. The directory is the `PMAP` section body: big-endian mode word, a second word that is zero in 61 of 62 payloads, a big-endian `u16` count `B`, six `0x70` bytes, then `B` 16-byte records of `{u32 id, u32 offset, u32 zero, u32 length}`. All 521 block offsets are 16-byte aligned, the first is `0x10`, the unused word is zero, and the ranges are in order and in bounds (62 of 62). The committed classifier checks each offset against the summed aligned lengths (`block_offsets_follow_lengths`, 62 of 62) | `BINARY`, `CROSS_SAMPLE`, `SYNTHETIC` | Confirmed (sample) | Block contents are opaque; the mode and second header word have no established meaning |
| PSIN-F16 | The block table predicts the first-section offset. The relation `first_offset = 0x10 + sum(align16(length_i) for i < B-1) + length_last` holds in 62 of 62 `PMAP` payloads. A model that also pads after the last block fits only the 52 payloads whose last length is a multiple of 16 and fails the ten unaligned payloads | `BINARY`, `CROSS_SAMPLE` | Confirmed (counterexample set) | The ten unaligned first-section offsets are 72, 104, 152, 152, 260, 344, 888, 2,456, 307,048 and 972,552 (PSIN-F08) |
| PSIN-F17 | The `PSCH` body is a count table. It holds a big-endian `u32` count `P`, `P` pairs of big-endian `u32` id and absolute body offset, eight uninterpreted bytes, then `P` values delimited by the offsets. The first value starts at the table end plus eight and the last ends at the body length in 62 of 62 payloads. Every `PMAP` block id at or above `0x100` (459 blocks) occurs in the `PSCH` id set; the small ids 1, 2, 6, 7, 8 and 12 (62 blocks) do not. The committed classifier checks both directions (`all_large_ids_in_psch`, `no_small_ids_in_psch`, 62 of 62). `tools/psin/value_probe.py` and `tools/psin/value-record.json` record the width and stream tests: the value common divisors 1 to 64 are `[1, 2, 4]`; no value or block yields a complete stream under the fixed decoder set | `BINARY`, `CROSS_SAMPLE`, `SYNTHETIC` | Confirmed (table); Unknown (value internals) | Value contents are not decoded; the eight-byte prefix is uninterpreted |
| PSIN-F18 | The `LSCH` section body has a fixed 16-byte header, a marker run and a variable tail. The body length is a multiple of 16 in 483 of 483 top-level `LSCH` payloads. At `+0x08` a little-endian `u32` is 512 (441), 768 (35) or 1024 (7); `+0x0C` is zero in 483 of 483. The marker run starts at `+0x10` in 483 of 483 and consists of 32-byte records that start with eight `0xAA` bytes. There are 10,537 records; every `0xAA` run in a body is one of them, and every consecutive pair is 32 bytes apart. Tails are variable and all are multiples of 16. The first four body bytes equal the last pre-section descriptor word in 191 of 483 payloads, so no universal cross-section reference is established | `BINARY`, `CROSS_SAMPLE` | Confirmed (sample) | The record fields and the tail are not decoded; the count is the 483 unique top-level payloads |
| PSIN-F19 | A nonempty `LENM` body has a `0x20`-byte header: eight arbitrary bytes, eight `0xEE` bytes at `+0x08`, a little-endian `u32` at `+0x10`, and 12 more bytes to `+0x20`. `length - 0x20` is a multiple of 8 in 229 of 229 nonempty bodies. For `N >= 1` the chain is `16N - 8` bytes, so `length = 0x18 + 16N + extra`; `extra` is 0 in 54 bodies and a positive multiple of 8 in 175. The rejected `length - 0x14` reading is not a multiple of 8 for the 54 zero-extra bodies. An empty body occurs in 254 top-level payloads | `BINARY`, `CROSS_SAMPLE` | Confirmed (header); Unknown (chain and extra region) | The count does not delimit the body; no field meaning is established |
| PSIN-F20 | Reproduction record. `tools/psin/pmap_heldout.py` applies both padding rules to the 62 `PMAP` payloads and writes `tools/psin/heldout-record.json` with the 52 aligned labels, the ten unaligned labels, the seeded random split and the results. Both padding models fit the aligned set, so the 52/10 split is a designed contrast, not a fit-and-predict hold-out. The random split (seed 20261125) reproduces 10 of 10 and is not blind either. The arithmetic relation is confirmed on all 62; the classifier reproduces all 62 `PMAP` and 483 `LSCH` structural checks | `CROSS_SAMPLE`, `SYNTHETIC` | Confirmed (arithmetic); the splits are not blind | One build and one local archive set; the rule is arithmetic and does not decode block contents |

## Counterexamples

| Reading | Counterexample |
| ------- | -------------- |
| `+0x04` as payload size | `packs.rpf` row 67 is 248 bytes with `+0x04` = 48; `anim.rpf` row 248 is 976,116 bytes with `+0x04` = 972,552 |
| `+0x06` as payload size | 0 of 757 `u16` values at `+0x06` equal the payload size |
| `+0x06` as an independent offset | `levels.rpf` row 2056 is 169,316 bytes with first offset 152,352 (`0x00025320`); `+0x06` is `0x5320`, or 21,280 |
| 16-byte alignment of `+0x04` | 10 `PMAP` payloads are unaligned, including offsets 260, 307,048 and 972,552 |
| Type ID 11 implies PSIN | The same rows include 238 unique RBF0 payloads |
| One header model | `PMAP` has no descriptor solution, while `LSCH` has a unique solution in 695 of 695 payloads |
| Padding after every `PMAP` block | The 10 unaligned `PMAP` first-section offsets (72 to 972,552) are produced by omitting padding after the last block; padding after it overshoots by 4 to 15 bytes |
| Fixed `PSCH` value width | Widths 1 to 64 do not divide all 1,170 value lengths; only 1, 2 and 4 do, and those are byte granularities |
| `PSCH` values as a compressed stream | No complete zlib, raw deflate, gzip, bzip2, xz, LZMA, zstd or LZ4 stream occurs across the 521 `PMAP` blocks |

## Reproduction

The following commands ran on 2026-11-25 with the `lforge` CLI built from `leonidaforge/leonida-forge` commit `92af6e2ef26f1f2819a757457a97003fd52029b4` and the release `0.1.0` binary. `<GAME_ROOT>` is a local installation, `<WORK>` a scratch directory outside it, and `<EXECUTABLE>` the game executable that matches the archive.

```text
lforge archive manifest <ARCHIVE> --executable <EXECUTABLE> --format jsonl --output <WORK>/rows.jsonl
lforge archive extract <ARCHIVE> --row <ROW> --output <WORK>/row.bin --executable <EXECUTABLE> --overwrite
python tools/psin/psin_inspect.py <WORK>/row.bin --json
```

The tool tests build synthetic `LSCH` and `PMAP` payloads, including a block-table `PMAP`, an unaligned `PMAP` and a corrupted payload:

```text
python -m unittest discover -s tools/psin
```

## Limits

- The sample is not random. It covers readable type 11 rows in the selected archives and a nested-archive bound of 2 MiB.
- One build and one local archive set were examined.
- The earlier 103 figure describes a narrower selection; the 757 figure covers the stated scope.
- No executable path was traced and no historical RAGE format is claimed as a match.
- Fields and tags were not assigned meanings. `PSCH` value internals, `LSCH` body fields and tail, and the `LENM` chain and extra region were not decoded.
- The `LSCH`/`LENM` body counts use the 483 unique top-level `LSCH` payloads; the 695 family total includes nested payloads that were not re-extracted in this pass.
- The `PMAP` block table and `PSCH` table cover all 62 unique `PMAP` payloads.
- Exact payload bytes stay outside this repository.
