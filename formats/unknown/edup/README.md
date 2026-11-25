# EDUP

`EDUP` (`45 44 55 50`) at offset 0 marks five rows in five archives, all type ID 255:

| Archive                    | Row | Stored  | Logical | Chunks |
| -------------------------- | --: | ------: | ------: | -----: |
| `pack/core_restofworld001` |   1 |      32 |      28 |      1 |
| `pack/core_restofworld`    |  15 |   1,552 |   1,548 |      1 |
| `pack/shared_minigame000`  |  53 |     240 |     236 |      1 |
| `pack/story000`            | 532 |      32 |      28 |      1 |
| `textures.rpf`             |  20 | 916,256 | 965,964 |     15 |

All five are chunked with entry encoding 3 and none carries the payload transform. All share `name_hash` `0x21E7013DF19FB4FA` and `name_key` `0x3BE189DE`; no other row in the 22-archive inventory has that key.

The stored-byte census sees `EDUP` in only three of the five rows. The other two store zlib chunks; their `EDUP` signature appears only after decoding. A decoded-content scan of all 290 unique readable type-255 rows at or below 64 KiB found four `EDUP` rows; the fifth is 965,964 bytes and was located through the shared name key.

## Observed structure

| Offset                    | Field                                              |
| ------------------------- | -------------------------------------------------- |
| `+0x00`                   | `45 44 55 50`                                      |
| `+0x04`                   | `u32` entry count, little-endian                   |
| `+0x08`                   | `count` entries of 16 bytes                        |
| `+0x08 + 16 × count`      | `u32` trailing-blob length, little-endian          |
| `+0x0C + 16 × count`      | trailing blob, `length` bytes                      |

The four distinct payloads satisfy `size = 8 + 16 × count + 4 + length` exactly:

| Size    | Count  | Entry bytes | Length offset | Blob length |
| ------: | -----: | ----------: | ------------: | ----------: |
|      28 |      0 |           0 |        `0x08` |          16 |
|     236 |      4 |          64 |        `0x48` |         160 |
|   1,548 |     33 |         528 |       `0x218` |       1,008 |
| 965,964 | 17,431 |     278,896 |     `0x44178` |     687,056 |

Each payload has exactly one 4-byte-aligned `u32`, relative to its start, equal to the number of bytes after it, and that field lies at the predicted `8 + 16 × count` offset. Testing entry widths from 1 to 64 bytes leaves only 16 bytes as a fit for all five payloads.

The count and length fields read as little-endian. Big-endian counts would be 0, 67,108,864, 553,648,128 and 390,332,416, all implausible for payloads of these sizes. Big-endian lengths exceed the payload size. The values at `+0x04` are consistent with a count and not with a byte offset or byte length. The little-endian reading is **Probable**: it is the only one that yields plausible values, but no executable code was traced to confirm the load width.

Counterexamples to simpler readings: in the 236-byte payload the `u32` at `+0x04` is 4, so it is neither the payload length (236) nor an offset to the trailing data (which starts at `+0x4C`). The `u32` at `+0x08` is 16 in the 28-byte payload but a different, large value in the 236-byte payload, so `+0x08` is not a universal length field. The count-driven offset explains both.

## Entries and trailing blob

The entries are not sorted by their 128-bit value in either byte order. Every entry is distinct within its payload. In the 4-entry, 33-entry and 17,431-entry payloads, the first 8 bytes are all distinct; the last 8 bytes take 4, 21 and 6,845 distinct values respectively. In the 17,431-entry payload every byte position takes all 256 values, so the repeats are whole 8-byte values, not a constant byte. No entry contains the shared name hash or key in either byte order. This pattern does not support treating an entry as a uniform 128-bit value; it may hold two 8-byte components, whose meanings are Unknown.

The trailing blob is length-delimited and opaque at this level. The 687,056-byte blob has entropy about 8.0 bits/byte and the 1,008-byte blob about 7.8; none of the zlib, gzip, bzip2 or LZMA decoders accepts either, and no entry appears inside the blob. Every blob length is a multiple of 16 bytes, so every payload size is `12 mod 16`. Whether the blob is content, a digest, compressed data or encrypted data is Unknown.

The count-0 payload has a 16-byte trailing blob, constant across the two byte-identical rows. It does not match the first or last 16 bytes of MD5, SHA-1, SHA-256, SHA-512 or BLAKE2 digests of the five payloads, and the byte at `+0x06` does not take a standard UUID version nibble. Its identity remains Unknown; calling it a digest would be a guess.

## Classification

| Part                                  | Status                                         |
| ------------------------------------- | ---------------------------------------------- |
| Magic and occurrence                  | Confirmed (5 rows, 5 archives)                 |
| Stored-byte signature census          | Confirmed (3 rows of the 22-archive inventory) |
| Decoded-content occurrence            | Confirmed (5 rows; bounded scan for small rows) |
| Count, length and 16-byte entry width | Confirmed (four distinct payloads)             |
| Little-endian field reading           | Probable                                       |
| Field meanings after the count        | Unknown                                        |
| Independent format                    | Probable                                       |

The magic and the count/length framing are self-contained and fit all five payloads; no documented format is claimed as a match. The format is probably independent, but its role as metadata, container or embedded structure is not established. The count-0 and larger payloads share one framing, so they are not treated as separate variants.

## Limits

- Five rows and four distinct payloads. The two hidden rows were found through the shared name key; the full 1,735-row type-255 set, about 14 GB logical, was not decoded.
- The entry and blob contents are not interpreted. No executable path was traced and no earlier RAGE format is claimed as a match.
- The 16-byte blob is not named. A digest, a fixed marker and an opaque value are all consistent with the bytes.
- The stored-byte census remains three; it is a lower bound for decoded signatures that a zlib chunk can hide.

Evidence: [evidence/unknown-payloads/INDEX.md](../../../evidence/unknown-payloads/INDEX.md).
