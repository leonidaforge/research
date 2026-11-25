# SGD5 evidence index

Payload observations from the Scarlett build [e95020b2](../../builds/gta-vi/scarlett-e95020b2/README.md). No executable code path was traced. Every finding is **Private-evidence supported**.

## Sample

| Property | Value |
| -------- | ----- |
| Archive | `<GAME_ROOT>/shaders.rpf`, 3 rows, all type ID 255 |
| SGD5 rows | row 1, stored 3,086,896 bytes, decoded 3,086,891 bytes; row 2, stored 271,048,480 bytes, decoded 271,048,467 bytes |
| Signature | `53 47 44 35` at offset 0 in both decoded payloads |
| Row 1 SHA-256 | `D86AF8CD24312A51C1FC7E7888A43B04338C37CEF1568B6473A88AD469A03925` |
| Row 2 SHA-256 | `331DB1162E6440D1629CF87B4802505FA41DA534034AF1147BCE5A9B402C4E16` |
| Third row | decodes to 275,540,780 bytes; no `SGD5` at offset 0 |

The hashes identify derived samples and carry no asset text.

## Search scope

| Item | Value |
| ---- | ----- |
| Manifests | 23 top-level manifest files covering 22 unique archives, and 44 nested-archive manifests |
| Row records scanned | 10,505: 6,534 unique top-level rows, 3,553 nested rows, and one duplicated top-level manifest |
| Method | read the first four stored bytes at each row's `payload_offset`; skip rows with `payload_transform` |
| Skipped | 622 row records with `payload_transform`; chunked rows contribute their stored compressed bytes, not decoded bytes |
| Result | `SGD5` at offset 0 in the two rows above and in no other row record |

The nested set is a 44-archive sample reached from type-0 rows of the top-level archives. It is not every nested archive.

## Evidence types

| Type              | Meaning                                                              |
| ----------------- | -------------------------------------------------------------------- |
| Payload data      | Bytes read from a decoded RPF9 payload, not traced in executable code |
| Tool output       | A manifest field or extraction result printed by the local CLI        |
| Consistency check | A property compared across the two payloads                          |
| Manifest scan     | First stored bytes at each row's payload offset                      |

## Findings

| ID       | Claim | Evidence | Confidence | Limits |
| -------- | ----- | -------- | ---------- | ------ |
| SGD5-F01 | `shaders.rpf` rows 1 and 2 decode to payloads that start with ASCII `SGD5` (`53 47 44 35`) at offset 0. Sizes and SHA-256 are in the sample table. The third row does not start with `SGD5` | Payload data, tool output | Confirmed | Two rows, one archive |
| SGD5-F02 | A scan of 10,505 row records across the 22 top-level archives and the 44 nested archives in the inventory sample found `SGD5` at offset 0 only in the two rows above | Manifest scan | Confirmed (sample) | Stored-byte prefixes; 622 transformed rows skipped; chunked rows not decoded; nested sample not exhaustive |
| SGD5-F03 | The header has `u32` values at `+0x04`, `+0x08`, `+0x0C` and `+0x10`, a 20-byte descriptor at `+0x14` and a zero `u32` at `+0x28`. `+0x0C` equals the number of table blocks (3, 33) and `+0x10` equals the first block length (248, 2112). No tested header field equals a payload size or the data-region offset | Payload data, consistency check | Confirmed (observation); Unknown (meaning) | Two samples |
| SGD5-F04 | The first table block starts at `+0x10`, where its length field sits; the header fields end at `+0x0C`. It and each later block are shaped `u32 length`, 20-byte descriptor, `u32 zero`, payload. A table payload holds 8-byte entries `{u32 value, u16 kind, u16 index}`. `length = 24 + 8n` in all 36 table blocks and `index` runs 0 to `n - 1` in all 36 | Payload data, consistency check | Confirmed | Two samples; 36 blocks |
| SGD5-F05 | The entry `u32` value is not a file offset or a size: the maximum `0xFF18999D` exceeds both payloads and no value equals a payload size. 299 of 486 values in row 1 and 488 of 2,423 in row 2 are distinct. Fifteen `u16` kinds occur. The 28-, 197- and 261-entry table payloads and their descriptors are byte-identical across the two samples | Payload data, consistency check | Confirmed (bytes); Unknown (meaning) | Two samples |
| SGD5-F06 | After the last table block, one more block header carries length 7,401 (row 1) and 11,985 (row 2). Neither equals the remaining file bytes, 3,082,875 and 271,028,115. Both equal `24 × (records whose headers begin at a 24-byte stride) + 9` | Payload data, consistency check | Confirmed (values and relation); Unknown (meaning) | Two samples |
| SGD5-F07 | The data region starts after that block header at `0x0FB0` and `0x4F80`. Its first 308 and 499 record headers are spaced 24 bytes apart. Each begins with two identical `u32` values, a `u16` kind, a non-sequential `u16`, and 12 bytes. The spacing then breaks and a NUL-terminated printable ASCII run appears within the following bytes | Payload data | Confirmed (observation); Unknown (meaning) | Two samples; payload text not reproduced |
| SGD5-F08 | Neither payload contains a second `SGD5` sequence or an `RPF9`, `RBF0`, `PSIN`, `EDUP`, `KB2j` or `KB2n` signature | Payload data | Confirmed | Two payloads; byte search only |

## Reproduction

Commands ran on 2026-11-25 with the `lforge` CLI built from `leonidaforge/leonida-forge` commit `fc841ea`. `<GAME_ROOT>` is a local installation, `<WORK>` a scratch directory outside it, and `<EXECUTABLE>` the game executable that matches the archive, used only to authenticate its metadata.

```text
lforge archive manifest <GAME_ROOT>/shaders.rpf --executable <EXECUTABLE> --format jsonl --output <WORK>/shaders.jsonl
lforge archive extract <GAME_ROOT>/shaders.rpf --row 1 --output <WORK>/row1.bin --executable <EXECUTABLE>
lforge archive extract <GAME_ROOT>/shaders.rpf --row 2 --output <WORK>/row2.bin --executable <EXECUTABLE>
python tools/sgd5/sgd5_inspect.py <WORK>/row1.bin <WORK>/row2.bin
```

The first four decoded bytes show the signature. The search read the first four stored bytes at each manifest row's `payload_offset` and skipped rows whose `payload_transform` was true.

## Limits

- Two payloads from one archive. The 20-byte descriptor, the `u16` kinds, the `u32` values and the data-region records have no established meaning.
- The search cannot classify transformed rows and does not decode chunked rows for this comparison.
- The nested-archive sample is bounded by the inventory selection. Larger or unselected nested archives were not examined.
- No executable path was traced and no earlier RAGE format is claimed as a match.
