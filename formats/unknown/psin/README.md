# PSIN

PSIN is an unresolved payload encoding identified by the four bytes `50 53 49 4E`, ASCII `PSIN`, at offset 0. It occurs in RPF9 rows of types 11, 93 and 94. The type ID is not a PSIN test: sampled type 11 rows also begin with `RBF0`.

Nothing about the purpose, field meanings or record semantics is established. The name expands to nothing known.

## Status

| Part                                      | Status                                        |
| ----------------------------------------- | --------------------------------------------- |
| Magic and occurrence                      | Confirmed (103 unique payloads, PSIN-F01)     |
| First section offset at `+0x04`           | Confirmed (103/103, PSIN-F02)                 |
| `+0x04` or `+0x06` as payload size or count | Rejected (PSIN-F03)                          |
| Tagged section walk                       | Confirmed (103/103, PSIN-F04)                 |
| Repeated section body lengths             | Confirmed (PSIN-F05); body meaning Unknown    |
| Bytes `+0x08..+0x0F`                      | Unknown (PSIN-F06)                            |
| Purpose                                   | Unknown                                       |

## Samples

The corpus contains 103 unique PSIN payloads: the earlier 18 plus 85 additional payloads. The additions come from a deterministic sample of decoded type 11 rows at or below 1 MiB across nine top-level archives and from depth-1 payloads. Sizes range from 216 to 1,032,656 bytes. The sample is a convenience sample, not a population. The sample list, selection rule and reproduction are in [evidence/psin/INDEX.md](../../../evidence/psin/INDEX.md).

## Observed header

| Offset  | Reading  | Observation                                                                 | Confidence        |
| ------- | -------- | --------------------------------------------------------------------------- | ----------------- |
| `+0x00` | 4 bytes  | `50 53 49 4E`, ASCII `PSIN`                                                 | Confirmed         |
| `+0x04` | `u32` BE | Offset of the first tagged section; 48 to 972,552 in the sample             | Confirmed (103/103) |
| `+0x06` | `u16` BE | Low 16 bits of the `+0x04` offset; not an independent field                 | Confirmed (103/103) |
| `+0x08` | `u32` BE | Candidate integer reading; no tested relation to size or section lengths    | Unknown           |
| `+0x0C` | `u32` LE | Candidate integer reading; no tested relation to size or section lengths    | Unknown           |

The eight bytes at `+0x08..+0x0F` take 84 distinct values in the 103 payloads. Nine payloads store eight `0x70` bytes there. The two integer readings above are probable readings only; neither was assigned a meaning.

An earlier note read `+0x04` as a `u16` that was `00 00` in most samples and `00 02` in one. That was the high half of the big-endian offset: the `00 02` sample has an offset of `0x00025320`. The correction is recorded in the [research history](../../../evidence/psin/research-history.md).

## Tagged sections

At the offset stored in `+0x04`, each section starts with a four-byte printable tag and a big-endian `u32` length. The length includes the eight-byte tag and length header. The next section starts at `offset + length`. In all 103 payloads the walk ends exactly at the payload size.

| Tag sequence                                        | Payloads |
| --------------------------------------------------- | -------: |
| `LSCH` -> `LENM` -> `LSNS` -> `LGID` -> `LRSC` -> `CHKS` |       94 |
| `PMAP` -> `PSCH` -> `PSIG` -> `STNS` -> `CHKS`      |        7 |
| `PMAP` -> `PSCH` -> `PSIG` -> `STDN` -> `STNS` -> `CHKS` |     2 |

The first section offset is not always a multiple of 16. It is aligned in 100 payloads and unaligned in three. Section tags and lengths are observations; the tag strings are not semantic names.

## Repeated structures

| Section | Observed length | Repeated observation                       |
| ------- | --------------: | ------------------------------------------ |
| `LSCH`  |       88 to 28,184 | Body length is a multiple of 16 in 94/94 |
| `LRSC`  |              88 | Body length is 80 in 94/94                 |
| `CHKS`  |              20 | Body length is 12 in 103/103               |
| `PMAP`  |        56 to 264 | Body length is a multiple of 16 in 9/9     |
| `STNS`  |       24 to 1,352 | Body length is a multiple of 16 in 9/9    |
| `STDN`  |        88 to 264 | Body length is a multiple of 16 in 2/2     |
| `PSCH`, `PSIG`, `LENM`, `LSNS`, `LGID` | variable | No single body modulus across the sample |

Runs of `0xAA` and `0x70` occur inside section bodies and in the region before the first section. Their meaning is **Speculative** (PSIN-F09). No section body was decoded.

## Size and count tests

The `u32` reading at `+0x04` is not the payload size: 0 of 103 values equal the file size. The offset is as small as 48 in a 248-byte payload and as large as 972,552 in a 976,116-byte payload. It is also not a section count: it points at an in-file tag, and values such as 972,552 cannot count the five or six observed sections.

The `u16` reading at `+0x06` is not the payload size either: 0 of 103 values equal the file size. It equals the low 16 bits of the `+0x04` offset in 103 of 103 payloads. In 28 payloads the offset is above `0xFFFF`, so `+0x06` alone is not the offset. For a 169,316-byte payload the offset is 152,352 (`0x00025320`) while `+0x06` reads `0x5320`, or 21,280.

## Identification

Identification MUST use the payload bytes. The RPF9 type ID alone is not sufficient.

## Limits

- Purpose unknown. The rows have no resolved names, so no contextual label is available.
- No executable path was traced and no historical RAGE format is claimed as a match.
- The sample is bounded at 1 MiB for the new top-level extraction and is not random. It does not establish the type's full size or type-ID range.
- No field or tag was assigned a meaning. Reading any field as a count, size, hash or identifier would be a guess.
- Section body contents were not decoded beyond their lengths and repeated byte patterns.
