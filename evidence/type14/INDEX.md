# Type 14 evidence index

Observations from one decoded payload in the Scarlett build
[e95020b2](../../builds/gta-vi/scarlett-e95020b2/README.md), using `lforge 0.1.0`
from `leonidaforge/leonida-forge` app commit `92af6e2`. No executable code path
was traced. Findings with payload bytes or tool output are **Private-evidence
supported**. Corrected interpretations are recorded in the
[research history](research-history.md).

## Sample and method

| Property | Value |
| --- | --- |
| Row | `<GAME_ROOT>/data.rpf` row 262 |
| Type ID | 14 |
| Layout, mode | F, 0 |
| Chunks | 1, entry encoding 3 |
| Stored size | 240 bytes |
| Logical size | 1,280 bytes |
| Name | unresolved; not published |
| Payload content SHA-256 | `d324c7908f1f8d66877b4ff8d9847662ba83ebbc9aa62e8662a68d270d600a85` |
| Top-level archives | 22 authenticated manifests, 6,534 rows |
| Nested manifests | 250 unique archives, 38,395 rows |

The hash identifies the derived payload. Payload text is not reproduced. String
observations are limited to offsets, counts and lengths.

## Findings

| ID | Claim | Evidence | Confidence | Limits |
| --- | --- | --- | --- | --- |
| T14-F01 | The 22 top-level manifests contain one type 14 row, `data.rpf` row 262. The current CLI decodes it to 1,280 bytes from 240 stored bytes, one chunk with entry encoding 3. Re-extraction matches the recorded header values `+0x00` `u16` `0x0330`, `+0x04` `u32` `0x0500`, `+0x0C` `u16` `0x0043`, `+0x0E` `u16` `0x0330`, `+0x12` `u16` `0x1000`, `+0x18` `u16` `0x0008`, `+0x1C` `u32` `0x03B0`, `+0x20` `0xCD172571` and `+0x24` `0xC0010280`. | Authenticated manifest, native extraction, payload data | Confirmed (bytes) | One decoded row; field meanings unknown |
| T14-F02 | The 250 nested manifests contain a second type 14 row: row 0 of a nested archive reached from `pack/story000/story000_script.rpf` row 2. It is 672,576 bytes logical, 199,424 bytes stored, 11 chunks with entry encoding 3, and `payload_transform` set. Its contents are `unsupported_transform`, so its bytes were not compared. | Authenticated manifest | Confirmed (row record) | The payload transform is unsupported; no payload bytes |
| T14-F03 | A scan of 293 local extracted `.bin` files found only two copies of the row 262 payload. No other payload begins `30 03` at offset 0 and none shares the first 16 bytes. | Payload prefix, hash fingerprint | Confirmed (local sample) | Bounded local set; not a game-wide census |
| T14-F04 | The decoded payload contains a string table at `+0x330`, exactly the value at `+0x00` and `+0x0E`. Its `+0x0C` length is 67 bytes and it holds 8 NUL-terminated ASCII strings. The terminator-inclusive lengths sum to 67, and the count matches the `u16` at `+0x18`. | Payload data, consistency check | Confirmed (one payload) | One payload; string text not published |
| T14-F05 | The decoded payload contains 8 records of stride `0x28` from `+0x3C0` to the payload end at `+0x500`. Each record holds a `u32` at `+0x00`, a `u16` name length at `+0x04`, an ASCII name at `+0x06`, and zero padding to the stride. All 8 names pass an ASCII and length check, with lengths 7, 6, 4, 12, 16, 4, 6 and 10. A scan of strides 8 to `0x80` found no other candidate. | `BINARY` | Confirmed (one payload) | One payload; the record identifier relation is T14-F11 |
| T14-F06 | Several header fields agree with the table extents. `+0x04` `u32` equals the payload size, `+0x0C` equals the string table length, and `+0x18` equals the count of both tables. The values at `+0x10` (`0x0320`) and `+0x1C` (`0x03B0`) are exactly `0x10` less than the string and record table starts; that relation has no established meaning. | Payload data, consistency check | Confirmed (values and relations); Unknown (meaning) | One payload |
| T14-F07 | The repeated `u16` values are not table counts. `0x0330` would imply 816 entries, but 816 two-byte entries exceed the 1,280-byte payload. `0x0500` equals the whole payload size. The repeated `0x0010` at `+0x0A` and `+0x16` does not match either table, which has 8 entries. | Payload data, consistency check | Confirmed (counterexamples) | One payload |
| T14-F08 | A repeated fixed-size structure does not start at offset 0. The first `0x2C` bytes are header fields, followed by zero and `0xCD` fill; the first record starts at `+0x3C0`. The string and record tables have the same count and seven matching name lengths; the fifth entry differs in length. | Payload data, consistency check | Confirmed (one payload) | One payload |
| T14-F09 | The payload is more consistent with a serialized structure than with a typical standalone file. It has no magic, its header stores internal offsets, lengths and a count, and it carries two tables with the same count and overlapping name lengths, separated by fill regions. A standalone, unlabelled file is not excluded: `+0x04` stores the total size and all offsets are internal. | Payload data, consistency check | Probable (serialized structure); Unknown (identity) | One payload; no loader or writer traced |
| T14-F10 | The `u32` values at `+0x20`, `+0x24` and `+0x28` match none of the tested hashes of the 8 string-table entries or the 8 record names. Their meaning remains Unknown. | `BINARY` | Unknown | One payload; no code path |
| T14-F11 | Each of the 8 record `u32` identifiers equals the one-at-a-time ("joaat") hash of the string-table entry at the same index, over the exact entry bytes excluding the terminating `0x00`: 8/8. With the terminator the count is 0/8; with byte-swapped output it is 0/8. The folded lower-case and case-sensitive variants both give 8/8 because the 8 entries are lower-case ASCII. The record name field is not the preimage: six of eight names differ from the same-index string only by case and two have different text; hashing the record names gives 6/8 folded and 0/8 case-sensitive. | `BINARY`, `CROSS_SAMPLE`, `SYNTHETIC` | Confirmed (single payload) | One decoded payload; no second payload or other record type. The relation is not generalised. Record names and record identifiers are not published, and no name preimage or name key is published. The payload content SHA-256 is a content digest, not a name or record identifier. The synthetic test validates the tool, not the native format |

## Reproduction

Commands ran on 2026-11-25. `<GAME_ROOT>` is a local installation, `<WORK>` a
scratch directory outside it, and `<EXECUTABLE>` the matching game executable,
used only to authenticate archive metadata.

```text
lforge archive manifest <GAME_ROOT>/data.rpf --format jsonl --output <WORK>/rows.jsonl --overwrite --executable <EXECUTABLE>
lforge archive extract <GAME_ROOT>/data.rpf --row 262 --output <WORK>/row262.bin --overwrite --executable <EXECUTABLE>
python tools/type14/inspect_type14.py <WORK>/row262.bin
python tools/type14/inspect_type14.py <WORK>/row262.bin --verify-ids
```

The inspector reports header fields, the string table offset and length, the
string lengths, and every record stride that forms a table of the header count.
It does not print payload text or record identifiers. Default output includes a
payload content digest only, not a name or record identifier. `--verify-ids`
prints only match counts. The nested type 14 row is read from a manifest only;
its transform is unsupported.

## Limits

- One decoded payload. The second type 14 row is behind the payload transform and
  was not compared.
- The local prefix scan covers 293 extracted files, not every row or every
  archive. The 22 top-level archives contain no other type 14 row.
- The record identifiers are interpreted only as hashes of the same-index
  string-table entries. The high-entropy header values and the purpose of the
  structure remain unknown.
- No executable code was traced, so the observations do not establish a loader,
  writer, field name or format identity.
- String contents are game data and were not copied into this repository.

## Open questions

- Whether the second type 14 row uses the same table layout and identifier
  relation after its transform.
- Whether the identifier relation holds for other payloads or record types.
- What the values at `+0x20`, `+0x24` and `+0x28` mean.
- Why the values at `+0x10` and `+0x1C` are `0x10` below the two table starts.
- Whether the payload is written by a serializer or is an unlabelled standalone
  file.
