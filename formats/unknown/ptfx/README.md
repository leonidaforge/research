# PTFX

`PTFX` (`50 54 46 58`) at offset 0 marks one payload in `common.rpf` row 151.
The four bytes are followed by `_` (`0x5F`) and continue to the first space,
which supports reading them as the first segment of a text key rather than a
standalone magic. The payload is 47 bytes of printable ASCII text.

The label is neutral. Nothing about the payload purpose, field meanings, writer,
loader or format identity is established.

## Samples

| Archive | Row | Type ID | Layout, mode | Stored | Logical | Chunks | Payload SHA-256 |
| --- | --: | ---: | --- | ---: | ---: | --- | --- |
| `common.rpf` | 151 | 255 | F, 0 | 48 | 47 | 1, encoding 3 | `FFC51809F9D5E749F47DEB9A37CCFF193ADEFB2A097B6B1DB31998E571FA06D5` |

The row has no payload transform. Its `key32` name key is `0x62CE875E` and its
name hash is `0x368EBDE7CCAA9E19`; a user mapping supplies one verified
candidate. A hash match proves only a name preimage, not the original filename.

## Storage

The row's payload offset is `0x1B1110`. The 48 stored bytes are the 47 payload
bytes followed by one `0x00` byte. Stored size minus that padding equals the
logical size, which is the completion condition for a copy chunk in encoding 3.
The chunk method bits were not read, so the copy method is **Probable**. See
[chunk layout](../../containers/rpf9/payloads.md#chunk-layout-and-decoding).

The native CLI extracts exactly the logical size. Two extractions produced the
same 47 bytes and SHA-256.

## Header and records

There is no binary header. Record 1 starts at offset 0. All offsets are from the
start of the decoded payload.

| Item | Start | Content bytes | Terminator | Fields | Key bytes | Value bytes | Key segment lengths |
| --- | ---: | ---: | --- | ---: | ---: | ---: | --- |
| Record 1 | `0x0000` | 23 | CRLF | 2 | 19 | 3 | 4, 3, 10 |
| Record 2 | `0x0019` | 18 | CRLF | 2 | 14 | 3 | 3, 10 |
| Blank line | `0x002D` | 0 | CRLF | 0 | — | — | — |

The payload ends at `0x002F` (47 bytes). The final CRLF terminates the blank
line. The first record's first underscore-separated segment is `PTFX`; the
second record's key does not begin with that segment.

## Delimiters and grammar

- CRLF (`0D 0A`) terminates each non-empty record and the final blank line.
- One `0x20` byte separates the key and the value in each non-empty record.
- No other delimiter occurs: no tab, comma, colon, equals, semicolon or quote.
- Keys use uppercase ASCII letters and underscore. The observed keys contain
  three and two underscore-separated segments.
- Values use ASCII digits and one `.`. Both observed values are 3 bytes.
- No record has a leading or trailing space, an empty key or an empty value.

The flat key-value shape is **Probable** from two records in one payload. The
key and value meanings are **Unknown**. The labels `key` and `value` describe
position in a record, not recovered field names.

## Constant and variable bytes

Only one `PTFX` payload was found, so a byte-level constant and variable split
across payloads cannot be established. Across samples it is **Unknown**.

Within this payload:

| Kind | Observation |
| --- | --- |
| Constant record shape | CRLF termination, one `0x20` delimiter, key and value character classes, final blank line |
| Variable between records | Key text, key length (19 and 14 bytes), segment pattern, value text |

Both values have the same length, but that is one observation and not a rule.

## Text, tagged structure or serialized document

| Option | Support | Status |
| --- | --- | --- |
| Plain text | All 47 bytes are printable ASCII or CRLF; no NUL, BOM, high-entropy region or other control byte | Confirmed (byte level) |
| Tagged key-value text | Both non-empty records have the same two-field grammar and character classes | Probable |
| Binary serialized document | No length, offset, count, checksum or binary header; all bytes are text and delimiters | Rejected for the observed bytes |
| Text serialization | A text writer or schema is not observed; the bytes cannot be distinguished from plain text without one | Unknown |

The payload is plain ASCII text. A flat key-value structure fits the observed
records, but the file does not establish a schema. No loader or writer was
traced.

## Identification

Identification MUST use the payload bytes. Type ID 255 also carries unrelated
payloads (UPL-F09), so the type ID is not an identifier. The `PTFX` first token
segment and the line grammar identify this observed payload class; neither
establishes its purpose.

## Confidence

| Part | Status |
| --- | --- |
| Occurrence and sizes | Confirmed (one row) |
| Text bytes and line structure | Confirmed (one payload) |
| `PTFX` as a key segment | Probable |
| Stored copy chunk | Confirmed (sizes and bytes); Probable (method) |
| Flat key-value grammar | Probable (two records) |
| Binary serialization framing | Rejected (observed bytes) |
| Format identity, purpose and field meanings | Unknown |
| Constants across payloads | Unknown (one sample) |

## Limits

- One decoded payload. The 782-archive nested inventory contains no `PTFX`
  prefix in any untransformed stored row.
- The decoded scan covers 2,366 top-level rows at or below 1,048,576 logical
  bytes. The 3,713 larger untransformed top-level rows and 1,278 transformed
  rows were not decoded for this comparison.
- The chunk method bits were not read.
- No executable code path was traced, and no earlier RAGE format is claimed as a
  match.
- Key and value text are game data and are not reproduced here.

Evidence: [evidence/ptfx/INDEX.md](../../../evidence/ptfx/INDEX.md).
