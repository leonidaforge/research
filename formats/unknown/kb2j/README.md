# KB2j and KB2n

`KB2j` (`4B 42 32 6A`) and `KB2n` (`4B 42 32 6E`) appear at offset 0 of 797 rows, all in `movies.rpf`, all type ID 255, all stored without a chunk table and without the payload transform.

| Signature | Rows | Stored size range            |
| --------- | ---- | ---------------------------- |
| `KB2n`    | 787  | 1,866,836 to 5,469,232 bytes |
| `KB2j`    | 10   | 50,552 to 4,004,896 bytes    |

## Observed header

The four extracted `KB2j` payloads share this layout:

| Offset           | Observation                                                          |
| ---------------- | -------------------------------------------------------------------- |
| `+0x00`          | `4B 42 32 6A`                                                        |
| `+0x04`          | `u32` equal to the stored size minus 8 in all four extracted samples |
| `+0x08`          | `u32` 15 in all four samples                                         |
| `+0x0C`          | `u32` varies: 14,720, 16,560, 14,720, 18,048                         |
| `+0x10`          | `u32` 15 in all four samples                                         |
| `+0x14`, `+0x18` | `u32` 512 in all four samples                                        |
| `+0x1C`, `+0x20` | `u32` 30 and 1 in all four samples                                   |

The next bytes are identical across those four samples. The four samples were extracted from rows 54, 55, 73 and 99; rows 53, 54, 55, 73 and 99 were read directly from stored bytes.

## Confidence

| Part                               | Status                            |
| ---------------------------------- | --------------------------------- |
| Magic and occurrence               | Confirmed (797 rows, one archive) |
| `+0x04` equals stored size minus 8 | Confirmed (4 extracted samples)   |
| `+0x08` and `+0x10` equal 15       | Confirmed (4)                     |
| Identity of the format             | Unknown                           |
| Meaning of the remaining fields    | Unknown                           |

The two signatures differ only in the fourth byte. Whether they are variants of one format, or two formats, is **Unknown**. A similarity to Bink video container headers is **Speculative**: it is based on public naming, not on any observation in this repository, and is not treated as evidence.

## Limits

- One archive. No `KB2j` or `KB2n` payload was found outside `movies.rpf`.
- Four payloads were extracted; the rest were counted from stored bytes only.
- No executable path was traced. The row type ID 255 is shared with unrelated payloads, so it carries no format identity.

Evidence: [evidence/unknown-payloads/INDEX.md](../../../evidence/unknown-payloads/INDEX.md).
