# PSIN

PSIN is a container identified by the four bytes `50 53 49 4E`, ASCII `PSIN`, at offset 0. It has one outer framing and two pre-section grammars, keyed by the first section tag: `LSCH` and `PMAP`. They are not separate file formats.

The `LSCH` family carries a self-describing document — a schema, instance blocks, references, arrays, maps and enumerations — which is documented in [metadata/psin](../../metadata/psin/README.md). This document covers the framing, the `PMAP` family and the parts of `LSCH` that the decoded form does not explain.

PSIN payloads occur in RPF9 type 11, 93 and 94 rows. The type ID does not identify PSIN: type 11 also carries `RBF0`. The name expands to nothing known.

## Status

| Part | Status |
| ---- | ------ |
| Magic and occurrence | Confirmed (757 unique payloads, PSIN-F01) |
| First section offset at `+0x04` | Confirmed (757/757, PSIN-F02) |
| Tagged section walk | Confirmed (757/757, PSIN-F04) |
| `+0x04` or `+0x06` as size or count | Rejected (PSIN-F03) |
| Shared outer framing | Confirmed (PSIN-F02, F04) |
| `LSCH` descriptor table and count | Confirmed (695/695, PSIN-F10) |
| `PMAP` header marker | Confirmed (62/62, PSIN-F12) |
| `PMAP` pre-section block table | Confirmed (62/62, PSIN-F15) |
| `PMAP` block padding and offset formula | Confirmed (62/62, PSIN-F16) |
| `PSCH` ID/offset table | Confirmed (62/62, PSIN-F17) |
| `PSCH` value internals | Unknown (bounded by offsets) |
| `LSCH` body marker run and tail | Confirmed (483/483, PSIN-F18) |
| `LENM` body framing | Confirmed (229/229 nonempty, PSIN-F19) |
| `LENM` chain and extra data | Unknown |
| `CHKS` integrity section | Confirmed (757/757, PSIN-F11) |
| Purpose, tag meanings, record semantics | Unknown |

## Population

The recount covers 918 decoded PSIN payloads, 757 unique by SHA-256 of the decoded bytes. The sources are all readable type 11 rows from the 22 top-level archives and from 18 nested archives under `<GAME_ROOT>/data.rpf` at or below 2 MiB. Sizes range from 216 to 17,406,784 bytes.

The family split is 695 `LSCH` and 62 `PMAP`. The first-section offset is aligned in 695 `LSCH` payloads; 10 of 62 `PMAP` payloads are unaligned.

### Earlier counts

The PSIN-F01 claim in the earlier revision recorded 103 unique payloads: 18 earlier payloads plus 85 additional payloads. The 85 additions combine the deterministic top-level sample and the depth-1 payloads; duplicates are removed by SHA-256 before the total is taken. The 82 PSIN payloads from the expanded top-level extraction and the 13 depth-1 payloads reported in the evidence index are the two source sets, not additional components. The full recount in this document is 757 unique payloads, with 695 `LSCH` and 62 `PMAP`. Uniqueness is the SHA-256 of the decoded payload; overlapping nested archives and repeated rows account for the difference between 918 files and 757 unique payloads.

## Shared outer framing

All payloads use the same outer structure.

| Offset | Type | Observation |
| ------ | ---- | ----------- |
| `+0x00` | 4 bytes | ASCII `PSIN` |
| `+0x04` | `u32` big-endian | Offset of the first tagged section |
| `+0x08` | family-specific | Pre-section area; see the two grammars below |
| `first_offset` | section | First tag and length |

A section is a four-byte printable tag followed by a big-endian `u32` length. The length includes the eight-byte tag and length header. The next section starts at `offset + length`. The walk ends exactly at the payload size in all 757 unique payloads.

`+0x06` is the low 16 bits of the `+0x04` offset, not an independent field. `+0x04` is not the payload size and not a section count.

### Tag sequences

| Sequence | Payloads |
| -------- | -------: |
| `LSCH` -> `LENM` -> `LSNS` -> `LGID` -> `LRSC` -> `CHKS` | 695 |
| `PMAP` -> `PSCH` -> `PSIG` -> `STNS` -> `CHKS` | 55 |
| `PMAP` -> `PSCH` -> `PSIG` -> `STDN` -> `STNS` -> `CHKS` | 6 |
| `PMAP` -> `PSCH` -> `PSIG` -> `STFN` -> `STNS` -> `CHKS` | 1 |

Tag strings are raw bytes. They are not semantic names.

## `LSCH` family

The first section is `LSCH`. The pre-section area starts at `+0x08` with a 16-byte descriptor table.

### Descriptor table

| Offset in descriptor | Type | Observation |
| -------------------- | ---- | ----------- |
| `+0x00` | `u32` little-endian | Uninterpreted word. Not established as a name or hash |
| `+0x04` | `u32` little-endian | Length of one data block |
| `+0x08` | 8 bytes | `AA AA AA AA AA AA AA AA` in every descriptor |

Descriptors are contiguous from `+0x08`. Data blocks follow the table. Each block occupies `align16(length)` bytes. The first section offset `F` satisfies

```text
0x10 + 16 * C + sum(align16(length_i)) == F
```

where `C` is the descriptor count. The `0x10` constant is the eight-byte file header plus eight bytes of pre-section padding; the descriptor table itself begins at `+0x08`.

| Observation | Value |
| ----------- | ----- |
| Payloads with a unique `C` | 695 of 695 |
| Descriptor counts | 1 to 1093 |
| Descriptor marker | Eight `0xAA` bytes at `+0x08` in every descriptor |
| No-descriptor case | `C = 0` fits the relation and has a synthetic test |

The count is required to be unique. The result applies only to this container family. The descriptor `+0x00` word remains uninterpreted, and no field name is confirmed for it.

### Variant tests

| Descriptor table | Formula constant | Length field | Per-descriptor alignment | `LSCH` payloads with a unique `C` |
| ---------------- | ---------------- | ------------ | ------------------------ | ---------------------------------: |
| `+0x08` | `0x10` | `+0x04` | `align16` | 695 of 695 |
| `+0x08` | `0x10` | `+0x04` | none | 96 of 695 |
| `+0x10` | `0x10` | `+0x04` | `align16` | 0 of 695 |
| `+0x08` | `0x10` | `+0x00` | `align16` | 0 of 695 |

The aligned `+0x04` form is the only variant that fits every `LSCH` payload. The table at `+0x08` and the `0x10` constant are both required.

## `PMAP` family

The first section is `PMAP`. The family is separate from `LSCH`: it has no descriptor table, its block directory is inside the `PMAP` section, and all unaligned first-section offsets in the sample belong to it. All 62 `PMAP` payloads use `PMAP` -> `PSCH` -> `PSIG` -> [`STDN` or `STFN`] -> `STNS` -> `CHKS`; 55 carry neither extra section, six carry `STDN` and one carries `STFN`. The tag match rate is 62 of 62.

The earlier whole-area negatives remain valid and are not replaced by the block table:

| Test | Outcome |
| ---- | ------- |
| Constant bytes | Negative. The 62 areas have 62 distinct SHA-256 values; only the first eight bytes are constant |
| Fixed-stride table | Negative. The number of `0x70` runs ranges from 1 to 41 and their positions vary |
| Compressed data | Negative for the tested signatures and decoders. No zlib, gzip, xz, bzip2, LZ4 or zstd signature occurs at `+0x10`; zlib, gzip, bzip2 and LZMA produced no non-empty output. LZ4 and zstd are signature checks only; no LZ4 or zstd decoder was run |
| Embedded payload | Negative. No `PSIN`, `RBF0` or section tag occurs inside the pre-section area |
| Length pattern | In 52 of 62 payloads `(pre_section_length - 8) mod 16` is 0; nine have remainder 8 and one has remainder 4 |

These tests describe the area as one unit. The block table below is a different partition of the same bytes.

### Pre-section block table

The pre-section area starts at `+0x08`. It is the concatenation of a fixed prefix, one or more blocks, and `0x70` padding between blocks.

| Offset | Type | Observation |
| ------ | ---- | ----------- |
| `+0x08` | 8 bytes | `0x70` in 62 of 62 payloads |
| `+0x10` | block 0 | First block; every block starts on a 16-byte boundary |
| between blocks | bytes | `0x70` padding to the next 16-byte boundary |
| after the last block | none | The last block ends at the first-section offset, with no trailing padding |

The block directory is the `PMAP` section body, not the pre-section area.

| Body offset | Type | Observation |
| ----------- | ---- | ----------- |
| `+0x00` | `u32` big-endian | Mode word. Observed values 1, 2, 3, 4, 9, 10 and 170; meaning **Unknown** |
| `+0x04` | `u32` big-endian | Zero in 61 of 62 payloads; 41 in one. Meaning **Unknown** |
| `+0x08` | `u16` big-endian | Block count `B` |
| `+0x0A` | 6 bytes | `0x70` in 62 of 62 payloads |
| `+0x10` | `B * 16` | Blocks, 16 bytes each |

Each block record is four big-endian words:

| Record offset | Type | Observation |
| ------------- | ---- | ----------- |
| `+0x00` | `u32` | Block id |
| `+0x04` | `u32` | Absolute payload offset |
| `+0x08` | `u32` | Zero in 62 of 62 payloads |
| `+0x0C` | `u32` | Block length in bytes |

The table consumes the pre-section exactly:

```text
block[0].offset                == 0x10
block[i].offset                == 0x10 + sum(align16(block[j].length)) for j < i
first_section_offset           == 0x10 + sum(align16(block[j].length)) for j < B-1
                                  + block[B-1].length
```

The second relation omits padding after the last block. That omission is required: a model that pads after every block fits the 52 payloads whose last length is a multiple of 16 and fails the other ten. The ten unaligned first-section offsets are therefore predicted by the block table, not exceptional.

The split and prediction are committed in `tools/psin/heldout-record.json` and can be regenerated with `tools/psin/pmap_heldout.py`. The 52/10 split is defined by first-offset alignment, the property that distinguishes the two models. It is a designed contrast, not a blind hold-out. The record also carries a seeded random reproduction split (seed 20261125); that split is a reproduction check, not a blind one. The arithmetic relation itself is confirmed on all 62 payloads.

### Block ids

Block ids are not uniform.

| Class | Ids | Blocks | Observation |
| ----- | --- | -----: | ----------- |
| Small (below `0x100`) | 1, 2, 6, 7, 8, 12 | 62 | Do not occur in the `PSCH` id table |
| Other | all other observed ids | 459 | Every other id occurs in the `PSCH` id table (62 of 62 payloads) |

Id 1 marks a name block in 41 payloads. The block body ends with a NUL in 41 of 41 and splits into NUL-separated parts; 8,342 of those parts are entirely printable ASCII, 1,385 distinct, with repeats across payloads. The probe drops empty and non-printable parts, so the count covers printable parts and does not establish that every part of every block is printable. `tools/psin/body-record.json` records these counts. The names are data, not format semantics. The other block bodies are opaque.

### `PSCH` section

The `PSCH` body holds a count and a table of `(id, offset)` pairs, followed by one value per id.

| Body offset | Type | Observation |
| ----------- | ---- | ----------- |
| `+0x00` | `u32` big-endian | Count `P` |
| `+0x04` | `P * 8` | Pairs of big-endian `u32` id and absolute body offset |
| table end | 8 bytes | Uninterpreted; values start after it |
| value `i` | bytes | `[offset_i, offset_{i+1})`, or to the body end for the last value |

The table tiles the body exactly in 62 of 62 payloads: the first offset is the table end plus 8, offsets increase, and the last value ends at the body length. The value bytes are opaque. Their internal layout is not decoded.

The `PSCH` id set contains every other `PMAP` block id in 62 of 62 payloads. The reverse does not hold: `tools/psin/body-record.json` records 711 `PSCH` ids that no `PMAP` block uses across the 62 payloads.

### Negative tests for the values

Fixed record widths 1 to 64 do not consume all 1,170 `PSCH` values: the value common divisors are 1, 2 and 4, which are byte granularities, not records. The classifier records this as `value_common_divisors_1_to_64` in `value-record.json`. No zlib, gzip, bzip2, xz, LZMA, zstd or LZ4 signature occurs at a `PSCH` value or a block start. The zstd and LZ4 checks are signature checks only; no zstd or LZ4 decoder was run. No value or block yields a complete stream under raw deflate, zlib, gzip, bzip2, LZMA or LZMA-alone. Permissive calls can return partial output; those are not accepted as streams. Unlike the earlier whole-area test, this test isolates each value and block and checks end-of-stream. The value and block internals remain **Unknown**.

## `LSCH` and `LENM` section bodies

The two bodies are separate structures. They are described structurally; no field is assigned a semantic name. All 483 top-level `LSCH` payloads use the established `LSCH` -> `LENM` -> `LSNS` -> `LGID` -> `LRSC` -> `CHKS` tag sequence; the tag match rate is 483 of 483.

### `LSCH` body

The body length is a multiple of 16 in 483 of 483 top-level `LSCH` payloads.

| Body offset | Type | Observation |
| ----------- | ---- | ----------- |
| `+0x00` | 8 bytes | Uninterpreted |
| `+0x08` | `u32` little-endian | Observed 768 (441), 512 (35), 1024 (7). Meaning **Unknown** |
| `+0x0C` | 4 bytes | Zero in 483 of 483 |
| `+0x10` | `M * 32` | Marker records |
| after the records | bytes | Tail, a multiple of 16 bytes |

A marker record is 32 bytes and starts with eight `0xAA` bytes.

| Record offset | Type | Observation |
| ------------- | ---- | ----------- |
| `+0x00` | 8 bytes | `0xAA` in every marker record |
| `+0x08` | `u32` little-endian | Uninterpreted |
| `+0x0C` | `u16` little-endian | Zero in the sampled records |
| `+0x0E` | `u16` little-endian | Uninterpreted |
| `+0x10` | 16 bytes | Uninterpreted |

The marker run is exact. Every `0xAA` run in the body is a marker record, all 10,537 records start at a 16-byte boundary, and every consecutive pair is 32 bytes apart. The run starts at `+0x10` in 483 of 483 payloads. The tail has no marker. Tails are variable and all are multiples of 16 bytes; the tail grammar and the record fields are **Unknown**.

A cross-section reference is not established. The first four body bytes equal the last pre-section descriptor word in 191 of 483 payloads; the relation is not universal and is not used by the parser.

### `LENM` body

The body is empty in 254 top-level payloads. The 229 nonempty bodies share a `0x20`-byte header:

| Body offset | Type | Observation |
| ----------- | ---- | ----------- |
| `+0x00` | 8 bytes | Uninterpreted |
| `+0x08` | 8 bytes | `0xEE` in 229 of 229 |
| `+0x10` | `u32` little-endian | Count-like word `N`; meaning **Unknown** |
| `+0x14` | 12 bytes | Remaining header to `+0x20`. Twelve zero bytes in 42 of 229; other contents **Unknown** |

The header is `0x20` bytes, and `length - 0x20` is a multiple of 8 in 229 of 229 nonempty payloads.

`N` does not delimit the body. For `N >= 1`, the chain is `16 * N - 8` bytes, so `length == 0x20 + (16N - 8) + extra == 0x18 + 16N + extra`. The `extra` term is 0 in 54 of 229 bodies and a positive multiple of 8 in the other 175; `tools/psin/body-record.json` records these counts. The chain and the extra region are **Unknown**; an 8-byte table is possible but not decoded.

The arithmetic is consistent with the header test: `(0x18 + 16N + extra) - 0x20 = 16N - 8 + extra`, which is a multiple of 8 for every `N` and every multiple-of-8 `extra`. The rejected reading `length - 0x14` is not a multiple of 8 for the 54 bodies with `extra = 0`; for example, a 72-byte body with `N = 3` gives 52.

Neither body contains a co-located plaintext name. The printable-byte ratio is at most 0.24 for `LSCH` and 0.20 for `LENM`; the short printable runs in `LSNS` and `LGID` are not names. No semantic label is assigned.

## `CHKS` integrity section

Both families end with a `CHKS` section. Its section length is 20 bytes and its body is 12 bytes.

| Body offset | Type | Observation |
| ----------- | ---- | ----------- |
| `+0x00` | `u32` big-endian | Total-length word; equals the payload size in 757 of 757 |
| `+0x04` | `u32` big-endian | Stored checksum |
| `+0x08` | 4 bytes | ASCII `zppp` |

The checksum is a one-at-a-time hash over signed bytes, seeded with `0x3FAC7125`. It covers the whole payload with the total-length and checksum words zeroed.

```text
hash = 0x3FAC7125
for byte in payload_with_zeroed_words:
    signed = byte if byte < 128 else byte - 256
    hash = (hash + signed) & 0xFFFFFFFF
    hash = (hash + (hash << 10)) & 0xFFFFFFFF
    hash = hash ^ (hash >> 6)
hash = (hash + (hash << 3)) & 0xFFFFFFFF
hash = hash ^ (hash >> 11)
hash = (hash + (hash << 15)) & 0xFFFFFFFF
```

The checksum verifies in 757 of 757 unique payloads. An unsigned-byte variant matches 0 of 757. The seed has no established origin. This variant is validated only on this container family; it is not a general claim about other PSIN-like data.

The total-length word is a descriptive label supported by equality across the sample, not a recovered field name.

## Identification

Identification MUST use the payload bytes. The classifier reports the family from the first section tag:

- `LSCH` is reported with its descriptor count, formula result, and the `LSCH`/`LENM` body structure.
- `PMAP` is reported with its block table, padding result, `PSCH` tiling result and name-block summary, not as a failed parse.
- An unknown first tag is reported as `OTHER`; `first_tag` reports the raw tag bytes.

The RPF9 type ID alone is not sufficient.

## Tools

`tools/psin/psin_inspect.py` reports the shared framing, the family, the `LSCH` descriptor count, the `PMAP` block table, the `PSCH` table, the `LSCH`/`LENM` body structure and the integrity result. It does not decode value internals, print payload text or print block names.

```text
python tools/psin/psin_inspect.py <sample> [<sample> ...] [--json]
```

`tools/psin/pmap_heldout.py` writes the committed prediction record, `tools/psin/value_probe.py` writes the committed value and block test record, and `tools/psin/body_probe.py` writes the committed LSCH/LENM body and PMAP name record:

```text
python tools/psin/pmap_heldout.py --samples <DIRECTORY> --output heldout-record.json
python tools/psin/value_probe.py --samples <DIRECTORY> --summary-only --output value-record.json
python tools/psin/body_probe.py --samples <DIRECTORY> --summary-only --output body-record.json
```

`--max-bytes` and `--max-sections` on the classifier bound the read and the section walk. The tools read inputs read-only and have no default pointing at a game installation.

Synthetic fixtures are generated by `tools/psin/synthetic.py`. Tests include a valid `LSCH` document, a `PMAP` document with a block table, an unaligned `PMAP` document, and a corrupted payload that must fail the checksum:

```text
python -m unittest discover -s tools/psin
```

## Limits

- The sample is not random. It covers readable type 11 rows in the selected archives and a nested-archive bound of 2 MiB. The `LSCH`/`LENM` body counts use the 483 unique top-level `LSCH` payloads; the earlier 695 figure adds nested payloads that were not re-extracted in this pass.
- One build and one local archive set were examined.
- The earlier 103 figure describes a narrower selection; the 757 figure covers the stated scope.
- No executable path was traced and no historical RAGE format is claimed as a match.
- No tag or value was assigned a semantic name. The `PSCH` value internals, the `LSCH` body tail, and the `LENM` chain and extra region are undecoded.
- The descriptor `+0x00` word is uninterpreted.
- The checksum seed is unexplained, and the algorithm is validated only on this container family.
- Exact payload bytes stay outside this repository.

## Open questions

- What selects the `LSCH` and `PMAP` grammars?
- What do the `PSCH` values encode, and why does every `PMAP` block id at or above `0x100` occur in `PSCH`?
- What do the `LSCH` marker-record fields and tail encode?
- What does the `LENM` count delimit, and what follows the first chain?
- Do the `LSCH` descriptor words identify data blocks, schemas or record counts?
- Do the section tags map to records, and does the `CHKS` body protect only the payload bytes?
- Does the same framing occur in type 93 and 94 rows with the same two families?
