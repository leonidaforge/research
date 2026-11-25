# Type 14

One row in the 22 top-level archives carries type ID 14: `data.rpf` row 262,
layout F, mode 0, one chunk with entry encoding 3. It decodes to 1,280 bytes.
The expanded nested manifests contain a second type 14 row behind the
unsupported payload transform; its bytes were not compared.

The payload has no printable magic at offset 0.

## Header

All offsets are from the start of the decoded payload. Offsets and lengths
stored in the header are file-relative.

| Offset | Read | Value | Observation |
| --- | --- | --- | --- |
| `+0x00` | `u16` | `0x0330` | Matches the string table start |
| `+0x02` | `u16` | `0x0001` | Unknown |
| `+0x04` | `u32` | `0x00000500` | Equals the payload size |
| `+0x08` | `u16` | `0x0001` | Unknown |
| `+0x0A` | `u16` | `0x0010` | Unknown |
| `+0x0C` | `u16` | `0x0043` | Equals the string table length |
| `+0x0E` | `u16` | `0x0330` | Same value as `+0x00` |
| `+0x10` | `u16` | `0x0320` | `0x10` below the string table start; meaning unknown |
| `+0x12` | `u16` | `0x1000` | Unknown |
| `+0x14` | `u16` | `0x0001` | Unknown |
| `+0x16` | `u16` | `0x0010` | Unknown |
| `+0x18` | `u16` | `0x0008` | Equals the number of strings and records |
| `+0x1A` | `u16` | `0x0000` | Unknown |
| `+0x1C` | `u32` | `0x000003B0` | `0x10` below the record table start; meaning unknown |
| `+0x20` | `u32` | `0xCD172571` | Unknown |
| `+0x24` | `u32` | `0xC0010280` | Unknown |
| `+0x28` | `u32` | `0x00004000` | Unknown |

## Layout

| Range | Content |
| --- | --- |
| `+0x2C` to `+0x1A7` | Zero fill |
| `+0x1A8` to `+0x32F` | `0xCD` fill |
| `+0x330` to `+0x372` | String table, 67 bytes |
| `+0x373` to `+0x3BF` | `0xCD` fill |
| `+0x3C0` to `+0x4FF` | Record table, 8 records of `0x28` bytes |

The string table holds 8 NUL-terminated ASCII strings. Their
terminator-inclusive lengths are 8, 7, 5, 13, 11, 5, 7 and 11 bytes and sum to
67. The count matches `+0x18`.

Each record has this layout:

| Offset | Type | Use |
| --- | --- | --- |
| `+0x00` | `u32` | Identifier, uninterpreted |
| `+0x04` | `u16` | Name length |
| `+0x06` | bytes | ASCII name |
| remainder | bytes | Zero padding to `+0x28` |

All 8 records pass the length, ASCII and zero-padding checks. The record name
lengths are 7, 6, 4, 12, 16, 4, 6 and 10 bytes. Seven match the string-table
lengths; the fifth entry differs (16 bytes in the record, 10 in the string
table). A scan of strides 8 to `0x80` found no other record table ending at the
payload end.

## Hypothesis checks

A repeated `u16` is not evidence of a table count:

- The repeated `0x0330` would imply 816 entries. At two bytes per entry this
  exceeds the 1,280-byte payload. It is the string table offset instead.
- `0x0500` equals the whole payload size, so it cannot count table entries.
- The repeated `0x0010` at `+0x0A` and `+0x16` does not match either table. Both
  tables have 8 entries, the value at `+0x18`.

A repeated fixed-size structure does not start at offset 0. The first `0x2C`
bytes are header fields, followed by zero and `0xCD` fill. The first record
starts at `+0x3C0`.

## Standalone file or serialized structure

Observations that support a serialized structure:

- No magic or signature at offset 0.
- Header fields store internal offsets, a length and a count.
- Two tables with the same count and mostly matching name lengths are present.
- Fill regions separate the header and the two tables.

Observations that support a standalone file:

- The `u32` at `+0x04` equals the total size.
- The record table ends exactly at that size, and all offsets are internal.

The payload is probably a serialized structure rather than a typical standalone
file, but an unlabelled standalone file is not excluded. Its purpose and name
remain unknown.

## Confidence

| Part | Status |
| --- | --- |
| Top-level occurrence and size | Confirmed (1 row) |
| Header values | Confirmed (one payload) |
| String and record tables | Confirmed (one payload) |
| Header and table relations | Confirmed (values); Unknown (meaning) |
| Serialized or standalone | Probable (serialized); Unknown (identity) |
| Field purposes and record IDs | Unknown |

## Limits

- One decoded payload. The second type 14 row is behind the payload transform
  and was not compared.
- A local scan of 293 extracted files found no other payload beginning `30 03`
  or sharing the first 16 bytes. This is not a game-wide census.
- The high-entropy header values and the record IDs are not interpreted.
- No executable code path was traced.
- String contents are game data and are not reproduced here.

Evidence: [evidence/type14/INDEX.md](../../../evidence/type14/INDEX.md).
