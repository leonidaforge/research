# PTFX evidence index

Observations from one decoded payload in the Scarlett build
[e95020b2](../../builds/gta-vi/scarlett-e95020b2/README.md), using `lforge 0.1.0`
from `leonidaforge/leonida-forge` app commit `29758a2`. No executable code path
was traced. Findings with payload bytes or tool output are **Private-evidence
supported**.

## Sample and method

| Property | Value |
| --- | --- |
| Archive | `<GAME_ROOT>/common.rpf`, row 151 |
| Type ID | 255 |
| Layout, mode | F, 0 |
| Chunks | 1, entry encoding 3 |
| Payload offset | `0x1B1110` |
| Stored size | 48 bytes |
| Logical size | 47 bytes |
| Stored SHA-256 | `90CBB3B09B930FF8C724C6202DD7A1A89030731D9807856889BC2F29EB36E1D0` |
| Payload SHA-256 | `FFC51809F9D5E749F47DEB9A37CCFF193ADEFB2A097B6B1DB31998E571FA06D5` |
| Name | `key32` key `0x62CE875E`, hash `0x368EBDE7CCAA9E19`, resolved candidate from a user mapping |
| Authentication | Archive metadata signature verified |
| Top-level archives | 22 unique archives from 23 manifest files, 6,534 unique rows |
| Nested inventory | 782 unique archives, 169,523 rows |
| Extracted payloads | 144 attempts, 137 unique payloads |

The hashes identify the stored and derived bytes. Payload text is not
reproduced. String observations are limited to offsets, counts and lengths.

## Search scope

| Item | Value |
| --- | --- |
| Top-level stored-prefix scan | 6,079 untransformed rows with at least four stored bytes; 455 transformed rows skipped |
| Nested stored-prefix scan | 168,700 untransformed rows in 782 archives; 823 transformed rows skipped |
| Combined stored-prefix scan | 174,779 row records scanned |
| Stored-prefix result | `PTFX` at offset 0 in one row, `common.rpf` row 151 |
| Decoded top-level scan, 1 MiB cap | 2,366 untransformed rows extracted; one transient output write error retried successfully; one `PTFX` prefix |
| Inventory payload sample | 144 attempts, 137 unique; no `PTFX` prefix |
| Method | Read the first four stored bytes at each row's `payload_offset`; for the decoded scan, extract with the current CLI and read the first four decoded bytes |

The stored-prefix scan covers rows whose first stored bytes are not transformed.
Chunked rows contribute their stored stream, so a compressed row whose decoded
payload begins `PTFX` is not found by that scan. The decoded scan covers
top-level rows below the stated size limit, including compressed rows. Neither
scan covers every nested archive or rows above the size limit.

## Evidence types

| Type | Meaning |
| --- | --- |
| Authenticated manifest | Read-only parse of an RPF9 table of contents whose metadata signature the CLI accepted |
| Native extraction | `archive extract` exited 0 and the output size equals the row's logical size |
| Payload data | Bytes read from a decoded RPF9 payload |
| Stored-prefix scan | First four stored bytes at each row's payload offset |
| Decoded-prefix scan | First four bytes of an extracted payload |
| Hash fingerprint | SHA-256 of stored or decoded bytes |
| Consistency check | A property compared within the payload or across the scans |

## Findings

| ID | Claim | Evidence | Confidence | Limits |
| --- | --- | --- | --- | --- |
| PTFX-F01 | `common.rpf` row 151 is the only untransformed row in the 22 top-level archives whose stored bytes begin `PTFX`. It is type 255, layout F, mode 0, one chunk with entry encoding 3, no payload transform, stored size 48 and logical size 47. Two native extractions produced 47 bytes with the same SHA-256. | Authenticated manifest, native extraction, hash fingerprint | Confirmed (row, sizes, bytes) | One row |
| PTFX-F02 | The 48 stored bytes contain the 47 payload bytes followed by one `0x00` padding byte. Stored size minus padding equals logical size, which is the completion condition for a copy chunk. The chunk method bits were not read, so the copy method is probable, not confirmed. | Payload data, consistency check | Confirmed (bytes and sizes); Probable (copy method) | One row; method bits unread |
| PTFX-F03 | The bounded stored-prefix census scanned 174,779 untransformed row records: 6,079 top-level and 168,700 in 782 nested archives. Exactly one begins `PTFX`, the row above. A decoded scan of all 2,366 untransformed top-level rows at or below 1,048,576 logical bytes found the same single prefix. One attempt failed with a transient output write error and succeeded on retry; it is not a `PTFX` row. The 144-attempt nested-payload inventory sample contains no `PTFX` prefix. | Stored-prefix scan, decoded-prefix scan, authenticated manifest | Confirmed (bounded census) | 1,278 transformed rows skipped; nested archives are a 782-archive sample; top-level decoded scan is limited to 1,048,576 logical bytes |
| PTFX-F04 | The first four bytes are ASCII `PTFX` and byte 4 is `_` (`0x5F`); the token continues to the first `0x20`. The payload has no binary header before the first record, which starts at offset 0. Reading `PTFX` as the first segment of a text key, rather than a standalone magic followed by a binary header, is probable. | Payload data | Confirmed (bytes); Probable (key-segment reading) | One payload |
| PTFX-F05 | The payload contains two non-empty records terminated by CRLF, then one empty line terminated by CRLF. Record 1 starts at `0x0000` with 23 content bytes; record 2 starts at `0x0019` with 18 content bytes; the blank line starts at `0x002D`; the payload ends at `0x002F`. No other delimiter occurs: no tab, comma, colon, equals, semicolon or quote. | Payload data, consistency check | Confirmed (one payload) | One payload |
| PTFX-F06 | Each non-empty record is one key token, one `0x20` byte and one value token, with no leading or trailing space. Keys use uppercase ASCII letters and underscore; their lengths are 19 and 14 bytes and their underscore-separated segment lengths are 4/3/10 and 3/10. Both value tokens are 3 bytes, use digits and one `.` and match a decimal form. The flat key-value shape is probable; the field meanings remain unknown. | Payload data, consistency check | Confirmed (Grammar and lengths); Probable (key-value structure); Unknown (meaning) | Two records, one payload |
| PTFX-F07 | All 47 payload bytes are printable ASCII (`0x20`–`0x7E`) or CRLF; there is no NUL, BOM, high-entropy region or other control byte. The bytes support plain text (confirmed at the byte level) and a flat tagged key-value document (probable). Binary serialization framing is rejected for the observed bytes: no length, offset, count or checksum field and no binary header. A text serialization cannot be distinguished from plain text without a writer or loader. | Payload data, consistency check | Confirmed (text bytes); Probable (tagged text); Rejected (binary framing in these bytes); Unknown (identity and purpose) | One payload; no code path |
| PTFX-F08 | Only one `PTFX` payload was found, so a byte-level constant and variable split across payloads cannot be established. Within the single payload, the record shape is constant (CRLF termination, one space delimiter, key and value character classes, final blank line) and the key text, key length, segment pattern and value text vary between the two records. | Payload data, consistency check | Confirmed (within one payload); Unknown (across payloads) | One payload |

## Reproduction

Commands ran on 2026-11-25. `<GAME_ROOT>` is a local installation, `<WORK>` a
scratch directory outside it, and `<EXECUTABLE>` the matching game executable,
used only to authenticate archive metadata.

```text
lforge archive manifest <GAME_ROOT>/common.rpf --format jsonl --output <WORK>/common.jsonl --overwrite --executable <EXECUTABLE>
lforge archive extract <GAME_ROOT>/common.rpf --row 151 --output <WORK>/row151.bin --overwrite --executable <EXECUTABLE>
python tools/ptfx/inspect_ptfx.py <WORK>/row151.bin
```

The inspector reports offsets, lengths, terminator counts and character-class
checks. It does not print payload text.

The stored-prefix scan reads the first four bytes at each manifest row's
`payload_offset` and skips rows whose `payload_transform` is true. The
decoded-prefix scan extracts each selected row with the current CLI and reads the
first four bytes of the output.

## Limits

- One decoded `PTFX` payload.
- The stored-prefix scan skips 1,278 transformed rows and does not decode
  compressed rows.
- The nested-archive frame is the 782-archive inventory sample, not every nested
  archive. The decoded top-level scan is limited to 2,366 rows at or below
  1,048,576 logical bytes; 3,713 larger untransformed top-level rows were not
  decoded.
- The chunk method bits were not read; the copy method is inferred from the
  size relation.
- No executable code was traced, so no loader, writer, field name or format
  identity is established.
- Key and value text are game data and were not copied into this repository.

## Open questions

- Whether any payload above 1,048,576 logical bytes, or any transformed row, begins
  `PTFX`.
- Whether the two key patterns and decimal values are a schema with defined
  fields or free-form text.
- What writes the payload and what consumes it.
