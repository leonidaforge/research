# PSIN

PSIN is an unresolved payload encoding identified by the four bytes `50 53 49 4E`, ASCII `PSIN`, at offset 0. It was observed in RPF9 rows of type ID 11 (PSIN-F05).

The name expands to nothing established. Nothing about its purpose, its field meanings or its record structure is known.

## Status

| Part                   | Status                                       |
| ---------------------- | -------------------------------------------- |
| Magic and occurrence   | Confirmed (18 rows, five archives, PSIN-F01) |
| Bytes at `+0x04`       | Confirmed (PSIN-F02)                         |
| Reading them as a little-endian `u16` | Probable (PSIN-F02) |
| Header fields          | Unknown                                      |
| No payload-size field in the first 32 bytes | Confirmed for 18 samples (PSIN-F03) |
| Record structure       | Unknown                                      |
| Purpose                | Unknown                                      |

## Samples

18 rows from five archives were sampled. The canonical sample list, sizes, selection rule and reproduction are in [evidence/psin/INDEX.md](../../../evidence/psin/INDEX.md). Rows were selected as the first successfully extracted type 11 rows per archive, up to four per archive.

## Observed header

| Offset  | Observation                                           |
| ------- | ----------------------------------------------------- |
| `+0x00` | `50 53 49 4E` (PSIN-F01)                              |
| `+0x04` | Bytes `00 00` in 17 samples and `00 02` in one; a `u16` reading gives 0 and `0x0200` (Probable) (PSIN-F02) |

No checked header field in the first 32 bytes equals the payload size (PSIN-F03). No field was assigned a meaning. Runs of `0xAA` and `0x70` appear in parts of many payloads; their meaning is **Speculative** (PSIN-F04).

## Identification

Identification MUST use the payload bytes. The RPF9 type ID alone is not sufficient.

## Limits

- Purpose unknown. The rows have no resolved names, so no contextual label is available.
- No executable path was traced and no historical RAGE format is claimed as a match.
- The sample selection was not random and does not establish the type's full size range.
- Fields were not assigned names. Reading any field as a count, size or hash would be a guess.
