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

The entries are not sorted by their 128-bit value in either byte order. Every entry is distinct within its payload. In the 4-entry, 33-entry and 17,431-entry payloads, the first 8 bytes are all distinct; the last 8 bytes take 4, 21 and 6,845 distinct values respectively. In the 17,431-entry payload every byte position takes all 256 values, so the repeats are whole 8-byte values, not a constant byte. No entry contains the shared name hash or key in either byte order. The entry is therefore two 8-byte fields, not one 128-bit value.

## Key relationship

The two 8-byte fields read as little-endian keys. The first field is unique in every nonempty table. The second field repeats. The two key sets are disjoint in every nonempty table: no second-field value occurs as a first-field value, and no first-field value occurs as a second-field value.

The second field was tested against the 64-bit key tables of the local RDS5/ETPF texture stores. The store population is the 46 `.ttpf` files present under the local texture data directory: 352,461 keys, 352,417 distinct across the set.

| Table                 | Entries | Distinct first | Distinct second | First in store keys | Second in store keys |
| --------------------- | ------: | -------------: | --------------: | ------------------: | -------------------: |
| `textures.rpf` row 20 |  17,431 |         17,431 |           6,845 |                   0 |               17,431 |
| `core_restofworld` 15 |      33 |             33 |              21 |                   0 |                    0 |
| `shared_minigame000` 53 |     4 |              4 |               4 |                   0 |                    0 |

In the 17,431-entry table every first-field key is absent from every store key table and every second-field key is present. The second field is therefore the stored texture key in that table. The mapping direction is first-field key to stored key, not stored key to first-field key. The first field is a separate key space that no sampled store indexes; the table does not show where that key is referenced.

The match uses the little-endian reading. The big-endian reading of the same 16 bytes matches 0 of 17,431 second-field keys, which confirms the entry-field endianness for this table. The first field's byte order is not independently confirmed; its counts and disjointness do not depend on it.

The table maps 17,431 first-field keys to 6,845 distinct stored keys; 1,176 of those stored keys have more than one first-field key, and the largest group is 723.

The direction is **Confirmed** for `textures.rpf` row 20 and **Unknown** for the other two nonempty tables. Their second-field keys do not occur in the 46-store set. The local set is smaller than the 57-store sample used by the RDS5 document, so a missing store is the first explanation to test. No table inverts the relation: no table has a first-field key present in a store while its second-field key is absent.

## Trailing blob

The blob is length-delimited and opaque. Every blob length is a multiple of 16 bytes, so every payload size is `12 mod 16`. The four blob lengths are 16, 160, 1,008 and 687,056 bytes.

Tested record widths 1 to 64: only widths 1, 2 and 4 divide every blob length. No width produces a record table whose count equals the entry count or the distinct second-field count, and no fixed-offset 4-byte field is strictly increasing. The 16-byte records are all distinct in every blob. No 8-byte word matches a store key.

Tested decoders on the complete blob: zlib, raw deflate, gzip, bzip2, xz and LZMA-alone. All fail; raw deflate and LZMA also produce no complete stream with zero unused input. No zstd or LZ4 frame signature occurs at the blob start. Entropy is 3.9, 6.8, 7.8 and 8.0 bits/byte for the four blobs.

The count-0 payload has a 16-byte blob, constant across the two byte-identical rows. It does not match the first or last 16 bytes of MD5, SHA-1, SHA-256, SHA-512 or BLAKE2 digests of the five payloads, and the byte at `+0x06` does not take a standard UUID version nibble. Its identity remains Unknown. The blob is kept opaque: content, a digest table, compressed data and encrypted data are all consistent with the negative tests.

## Classification

| Part                                  | Status                                         |
| ------------------------------------- | ---------------------------------------------- |
| Magic and occurrence                  | Confirmed (5 rows, 5 archives)                 |
| Stored-byte signature census          | Confirmed (3 rows of the 22-archive inventory) |
| Decoded-content occurrence            | Confirmed (5 rows; bounded scan for small rows) |
| Count, length and 16-byte entry width | Confirmed (four distinct payloads)             |
| Count and blob-length little-endian reading | Probable                                       |
| Entry-field little-endian reading     | Confirmed (`textures.rpf` row 20)              |
| Two 8-byte entry fields               | Confirmed (one table; disjoint key sets)       |
| First-field-to-stored-key direction   | Confirmed (`textures.rpf` row 20); Unknown (two tables) |
| Trailing blob                         | Unknown (decoder and width tests negative)     |
| Independent format                    | Probable                                       |

The magic and the count/length framing are self-contained and fit all five payloads; no documented format is claimed as a match. The key test identifies the second field as a stored texture key in one table. The format is probably independent, but its role as metadata, container or embedded structure is not established. The count-0 and larger payloads share one framing, so they are not treated as separate variants.

## Tools

`tools/edup/edup_inspect.py` reports the layout, the two entry fields as counts only, and an optional membership test against local RDS5/ETPF stores. It never prints key values or payload bytes.

```text
python tools/edup/edup_inspect.py <sample> [<sample> ...] [--store <ttpf> ...] [--store-dir <dir>] [--json]
python -m unittest discover -s tools/edup
```

## Limits

- Five rows and four distinct payloads. The two hidden rows were found through the shared name key; the full 1,735-row type-255 set, about 14 GB logical, was not decoded.
- The key test covers 46 local `.ttpf` stores, not the 57-store sample in the RDS5 document. One table resolves completely; two do not resolve.
- The entry and blob contents are not otherwise interpreted. No executable path was traced and no earlier RAGE format is claimed as a match.
- The trailing blob is not named or decoded. The width and decoder tests are negative, not a proof of encryption.
- The stored-byte census remains three; it is a lower bound for decoded signatures that a zlib chunk can hide.

Evidence: [evidence/edup/INDEX.md](../../../evidence/edup/INDEX.md). The original occurrence and framing findings are UPL-F02 to UPL-F11 in [evidence/unknown-payloads/INDEX.md](../../../evidence/unknown-payloads/INDEX.md).
