# PSIN

PSIN is a container identified by the four bytes `50 53 49 4E`, ASCII `PSIN`, at offset 0. It has one outer framing and two pre-section grammars, keyed by the first section tag: `LSCH` and `PMAP`. They are not separate file formats.

PSIN payloads occur in RPF9 type 11, 93 and 94 rows. The type ID does not identify PSIN: type 11 also carries `RBF0`. Nothing about the purpose, field meanings or record semantics is established. The name expands to nothing known.

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
| `PMAP` pre-section grammar | Unknown (PSIN-F14) |
| `CHKS` integrity section | Confirmed (757/757, PSIN-F11) |
| Purpose, tag meanings, record semantics | Unknown |

## Population

The recount covers 918 decoded PSIN payloads, 757 unique by SHA-256 of the decoded bytes. The sources are all readable type 11 rows from the 22 top-level archives and from 18 nested archives under `<GAME_ROOT>/data.rpf` at or below 2 MiB. Sizes range from 216 to 17,406,784 bytes.

The family split is 695 `LSCH` and 62 `PMAP`. The first-section offset is aligned in 695 `LSCH` payloads; 10 of 62 `PMAP` payloads are unaligned.

### Earlier counts

The previously recorded 103 unique payloads describe a narrower convenience sample: 18 earlier payloads, 85 additional top-level payloads at or below 1 MiB selected by a per-archive quantile rule, and 13 depth-1 payloads. A separate private count of 109 payloads (100 `LSCH`, 9 `PMAP`) came from another unpublished selection. Neither figure is the full reachable population. Uniqueness in this document is the SHA-256 of the decoded payload; overlapping nested archives and repeated rows account for the difference between 918 files and 757 unique payloads.

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

The first section is `PMAP`. The pre-section area begins with eight `0x70` bytes at `+0x08` in 62 of 62 unique payloads. The descriptor relation has no solution for any `PMAP` payload, and the unaligned first-section offsets all belong to this family.

The remaining pre-section area is not constant:

| Test | Outcome |
| ---- | ------- |
| Constant bytes | Negative. The 62 areas have 62 distinct SHA-256 values; only the first eight bytes are constant |
| Fixed-stride table | Negative. The number of `0x70` runs ranges from 1 to 41 and their positions vary |
| Compressed data | Negative for the tested signatures and decoders. No zlib, gzip, xz, bzip2, LZ4 or zstd signature occurs at `+0x10`; zlib, gzip, bzip2 and LZMA produced no non-empty output |
| Embedded payload | Negative. No `PSIN`, `RBF0` or section tag occurs inside the pre-section area |
| Length pattern | The area length is 16-byte aligned after the first eight bytes in 52 of 62 payloads, with nine length-8 and one length-4 exceptions |

The cheapest first case is the 216-byte payload: a 40-byte pre-section area with two `0x70` runs, zero bytes and two small big-endian words. It does not decode as a compressed stream or an embedded payload.

The area is probably a structured record area with `0x70` padding, but its grammar is **Unknown**. The marker alone is enough to classify the family, not to decode the records.

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

- `LSCH` is reported with its descriptor count and formula result.
- `PMAP` is reported as a second grammar with its `0x70` marker and pre-section length, not as a failed parse.
- An unknown first tag is reported as `OTHER`.

The RPF9 type ID alone is not sufficient.

## Tools

`tools/psin/psin_inspect.py` reports the shared framing, the family, the descriptor count, and the integrity result. It does not decode section bodies or print payload text.

```text
python tools/psin/psin_inspect.py <sample> [<sample> ...] [--json]
```

`--max-bytes` and `--max-sections` bound the read and the section walk. The tool reads inputs read-only and has no default pointing at a game installation.

Synthetic fixtures are generated by `tools/psin/synthetic.py`. Tests include a valid `LSCH` document, a `PMAP` document, an unaligned `PMAP` document, and a corrupted payload that must fail the checksum:

```text
python -m unittest discover -s tools/psin
```

## Limits

- The sample is not random. It covers readable type 11 rows in the selected archives and a nested-archive bound of 2 MiB.
- One build and one local archive set were examined.
- The 103 and 109 figures describe narrower selections; neither is the full reachable population.
- No executable path was traced and no historical RAGE format is claimed as a match.
- Tags and section bodies were not assigned meanings. The `PMAP` pre-section grammar is undecoded.
- The descriptor `+0x00` word is uninterpreted.
- The checksum seed is unexplained, and the algorithm is validated only on this container family.
- Exact payload bytes stay outside this repository.

## Open questions

- What selects the `LSCH` and `PMAP` grammars?
- Is the `PMAP` pre-section area a record table, a packed structure or another encoding layer?
- Do the `LSCH` descriptor words identify data blocks, schemas or record counts?
- Do the section tags map to records, and does the `CHKS` body protect only the payload bytes?
- Does the same framing occur in type 93 and 94 rows with the same two families?
