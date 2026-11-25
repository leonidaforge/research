# ADAT

`ADAT` (`41 44 41 54`) at offset 0 marks stored payloads of type-255 rows inside
depth-1 archives reached from `audio.rpf`. In the newer scratch inventory, 729
rows in 59 of the 60 depth-1 `audio.rpf` archives begin with the magic. The
sixtieth archive holds 18 chunked type-255 rows whose stored bytes begin a zlib
stream instead.

The archive name is provenance, not evidence of purpose. Nothing about the
payload use, field meanings or relation to audio data is established.

## Samples

| Source | Nested rows | Type | Chunk table | Stored bytes | First eight bytes |
| --- | ---: | ---: | --- | --- | --- |
| `audio.rpf` row 42 | 11 | 255 | none | 69,728 to 741,488 | `41 44 41 54 01 00 25 FF` |
| `audio.rpf` row 77 | 10 | 255 | none | 4,224 to 33,984 | `41 44 41 54 01 00 21 FF` |

The 21 payloads from these two archives have distinct SHA-256 fingerprints. The
full census covers 729 rows from 4,224 to 51,693,440 bytes. All have no chunk
table, mode 0 and no payload transform. 630 store exactly their logical size;
99 add up to fourteen bytes of padding.

## Observed structure

| Offset | Observation | Status |
| --- | --- | --- |
| `+0x00` | `41 44 41 54` | Confirmed |
| `+0x04` | `u16` 1 in all 729 rows | Confirmed |
| `+0x06` | `u16` one of `0xFF02` (113 rows), `0xFF21` (276), `0xFF25` (256), `0xFF41` (84) | Confirmed; Unknown (meaning) |
| `+0x08` | `u32` from 1 to 231; 244 rows hold 2 | Confirmed; Unknown (meaning) |
| `+0x0C` | `u32` from 46 to 27,484, always below the payload size | Confirmed; Unknown (meaning) |
| after `+0x10` | Further values remain uninterpreted | Unknown |

The values at `+0x06`, `+0x08` and `+0x0C` are observations only. No count,
length, offset or table role is assigned.

## Identification

Identification MUST use the payload bytes. Type ID 255 also carries unrelated
payloads in this build (`EDUP`, `KB2j`, `KB2n`, `SGD5` and XML text), so the type
ID is not an identifier.

## Limits

- 60 of the 103 type-0 rows of `audio.rpf` were extracted; the other 43 are
  larger than the 64 MiB archive cap of that run.
- 21 rows from two archives were inspected beyond their first eight bytes. The
  other 708 rows were checked for the magic and manifest fields only.
- One of the 60 archives holds 18 chunked type-255 rows whose stored bytes are
  zlib streams. Their decoded payloads were not examined, so whether they also
  begin with `ADAT` is Unknown.
- No executable path was traced. The archive name and the field values do not
  establish a payload purpose or a format identity.

Evidence: [evidence/gfx-adat/INDEX.md](../../../evidence/gfx-adat/INDEX.md).
