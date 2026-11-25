# GFX*

`GFX*` (`47 46 58 2A`) at offset 0 marks the decoded payload of 49 type-66
rows. All 49 rows occur in six depth-1 archives reached from `data.rpf` rows 1,
3, 6, 19, 20 and 39. Every row is chunked with entry encoding 3, mode 0, and no
payload transform.

The stored bytes at each type-66 payload offset are a zlib stream beginning
`78 DA`. The magic is visible only after chunk decoding, so a stored-byte
census records these rows as compressed data.

## Samples

| Source | Nested row | Stored bytes | Logical bytes | First eight decoded bytes |
| --- | ---: | ---: | ---: | --- |
| `data.rpf` row 20 | 0 | 1,632 | 2,688 | `47 46 58 2A 80 0A 00 00` |
| `data.rpf` row 1 | 4 | 6,288 | 12,107 | `47 46 58 2A 4B 2F 00 00` |
| `data.rpf` row 1 | 6 | 1,408 | 2,251 | `47 46 58 2A CB 08 00 00` |
| `data.rpf` row 1 | 7 | 3,072 | 6,250 | `47 46 58 2A 6A 18 00 00` |
| `data.rpf` row 19 | 45 | 2,432 | 5,345 | `47 46 58 2A E1 14 00 00` |
| `data.rpf` row 19 | 48 | 2,816 | 5,463 | `47 46 58 2A 57 15 00 00` |

The six payloads are distinct. All 49 rows share two decoded-head properties:
the first decoded chunk begins `GFX*`, and the `u32` at `+0x04` equals the
row's logical size.

## Observed structure

| Offset | Observation | Status |
| --- | --- | --- |
| `+0x00` | `47 46 58 2A` | Confirmed |
| `+0x04` | `u32` equal to the logical payload size in all 49 rows | Confirmed |
| `+0x08` | `88 00 01 xx` in three samples; `80 00 02 xx` in three | Confirmed (two forms); Unknown (meaning) |
| `+0x20` | A length field and a printable ASCII run. The field is a `u16` in the `88` form and a `u8` in the `80` form | Confirmed (positions); Unknown (meaning) |
| `+0x37` | Start of a second printable ASCII run in the two payloads inspected for it | Confirmed (two payloads); Unknown (meaning) |
| after the prefix | Remaining bytes are high-entropy | Unknown |

The ASCII runs are not reproduced. Their presence, offsets and lengths are game
data observations, not format identity.

## Limits

- Six distinct payloads were inspected structurally. The other 43 type-66 rows
  were checked only for the first decoded chunk and the size field.
- 38 rows are one chunk; 11 are multi-chunk and were not reconstructed end to
  end.
- The two header forms may be versions or different payload kinds; neither is
  established.
- No executable path was traced. `GFX*` is a byte signature, not a confirmed
  format, and the type ID 66 is not an identifier outside this sample.

Evidence: [evidence/gfx-adat/INDEX.md](../../../evidence/gfx-adat/INDEX.md).
