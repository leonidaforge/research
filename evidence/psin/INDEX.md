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

The earlier public figure of 103 unique payloads describes a narrower convenience sample: the first 18 type 11 payloads, 85 additional payloads from nine top-level archives at or below 1 MiB selected by a per-archive quantile rule, and 13 depth-1 payloads. That figure remains a subset scope.

A separate private count of 109 payloads (100 `LSCH`, 9 `PMAP`) came from a selection that is not published. It is not reproduced here. The full recount in this document is 757 unique payloads, with 695 `LSCH` and 62 `PMAP`.

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
| PSIN-F14 | The `PMAP` pre-section area is not constant. The 62 unique areas have 62 distinct SHA-256 values; only the first eight bytes are constant. It is not a fixed-stride table: the number of `0x70` runs ranges from 1 to 41 and their positions vary. No tested compressed-stream signature occurs at `+0x10`, and zlib, gzip, bzip2 and LZMA produced no non-empty output. No `PSIN`, `RBF0` or section tag occurs inside the area. It is probably a structured record area with `0x70` padding, but its grammar is not decoded | `BINARY`, `CROSS_SAMPLE` | Confirmed (negative tests); Speculative (structured area) | The 216-byte payload is the smallest case; larger areas were not decoded |

## Counterexamples

| Reading | Counterexample |
| ------- | -------------- |
| `+0x04` as payload size | `packs.rpf` row 67 is 248 bytes with `+0x04` = 48; `anim.rpf` row 248 is 976,116 bytes with `+0x04` = 972,552 |
| `+0x06` as payload size | 0 of 757 `u16` values at `+0x06` equal the payload size |
| `+0x06` as an independent offset | `levels.rpf` row 2056 is 169,316 bytes with first offset 152,352 (`0x00025320`); `+0x06` is `0x5320`, or 21,280 |
| 16-byte alignment of `+0x04` | 10 `PMAP` payloads are unaligned, including offsets 260, 307,048 and 972,552 |
| Type ID 11 implies PSIN | The same rows include 238 unique RBF0 payloads |
| One header model | `PMAP` has no descriptor solution, while `LSCH` has a unique solution in 695 of 695 payloads |

## Reproduction

The following commands ran on 2026-11-25 with the `lforge` CLI built from `leonidaforge/leonida-forge` commit `92af6e2ef26f1f2819a757457a97003fd52029b4` and the release `0.1.0` binary. `<GAME_ROOT>` is a local installation, `<WORK>` a scratch directory outside it, and `<EXECUTABLE>` the game executable that matches the archive.

```text
lforge archive manifest <ARCHIVE> --executable <EXECUTABLE> --format jsonl --output <WORK>/rows.jsonl
lforge archive extract <ARCHIVE> --row <ROW> --output <WORK>/row.bin --executable <EXECUTABLE> --overwrite
python tools/psin/psin_inspect.py <WORK>/row.bin --json
```

The tool tests build synthetic `LSCH` and `PMAP` payloads, including a corrupted payload:

```text
python -m unittest discover -s tools/psin
```

## Limits

- The sample is not random. It covers readable type 11 rows in the selected archives and a nested-archive bound of 2 MiB.
- One build and one local archive set were examined.
- The 103 and 109 figures describe narrower selections; neither is the full reachable population.
- No executable path was traced and no historical RAGE format is claimed as a match.
- Fields and tags were not assigned meanings. Section bodies were not decoded into records.
- The `PMAP` pre-section grammar is Unknown.
- Exact payload bytes stay outside this repository.
