# Type 14

One row in the 22 top-level archives carries type ID 14: `data.rpf` row 262, stored as one chunk with entry encoding 3. It extracts to 1,280 bytes.

The payload has no printable magic at offset 0.

## Observations

| Offset  | Observation                               |
| ------- | ----------------------------------------- |
| `+0x00` | `u16` `0x0330`; the next `u16` is 1       |
| `+0x04` | `u16` `0x0500`; the next `u16` is 0       |
| `+0x0C` | `u16` `0x0043`                            |
| `+0x0E` | `u16` `0x0330`, the same value as `+0x00` |
| `+0x1C` | `u32` 944                                 |
| `+0x20` | `u32` `0xCD172571`                        |
| `+0x24` | `u32` `0xC0010280`                        |

`0x0330` appears at `+0x00` and `+0x0E`. `0x0010` appears at `+0x0A` and `+0x16`, while `+0x12` reads `0x1000`. The rest of the payload was not described. The high-entropy `u32` values at `+0x20` and `+0x24` are not interpreted.

## Confidence

| Part                | Status                  |
| ------------------- | ----------------------- |
| Occurrence and size | Confirmed (1 row)       |
| Values above        | Confirmed (one payload) |
| Field meanings      | Unknown                 |
| Format identity     | Unknown                 |

## Limits

- One row. No second type 14 row exists in the 22 top-level archives.
- A repeated `u16` is not evidence of a table count or an offset. No structural boundary was established.
- The payload may be a serialized structure rather than a file format. That question is open.

Evidence: [evidence/unknown-payloads/INDEX.md](../../../evidence/unknown-payloads/INDEX.md).
