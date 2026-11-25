# GFx evidence index

`GFX` (`47 46 58`) with version byte `0x2A` is the decoded-payload signature of
the GFx container. This index records the population, the header, the tag walk
and the corrections. The container family is identified; tag contents are not.

## Earlier claim

| Claim | First recorded in | Sample | Observation level |
| --- | --- | --- | --- |
| `GFX*` under type 66 | Unmerged `research/shared/resource-identification` branch, type inventory commits `1cee8cb` and `ce8629d` | 22,926 rows: five root archives walked, 61 nested archives opened; 49 type-66 rows in six archives | Decoded payload head; every type-66 row is chunked |

The first GFX document described six decoded payloads and called the family
unidentified. The 49-row decode identifies the container from its header and
tag framing. The tag walk replaces the previous reading of an opaque body.

## Sample and predicate

| Property | Value |
| --- | --- |
| Build | [scarlett-e95020b2](../../builds/gta-vi/scarlett-e95020b2/README.md) |
| Population | 849 unique depth-1 manifests in the cached inventory, 183,144 row records (182,321 readable, 823 unreadable) |
| Earlier run frame | 782 unique archives, 169,523 rows; the cache directory holds 67 further unique archives with 13,621 rows |
| GFX rows | 49 type-66 rows in six depth-1 archives reached from `data.rpf` rows 1, 3, 6, 19, 20 and 39 |
| Stored form | chunk encoding 3, mode 0, no payload transform, stored prefix `78 DA` |
| Predicate | exact `47 46 58` at decoded offset 0 and version `0x2A` at `+0x03` |
| Predicate scope | prefix at offset 0; not a whole-file hash and not a substring search |
| Stored-byte result | 0 of all 182,321 readable rows begin `GFX` at the stored payload offset |

All 49 type-66 rows were extracted end to end with `lforge 0.1.0`, including
the 11 multi-chunk rows. The 67 further cached archives contain no type-66 row.
The earlier run summary and the cache manifest count differ because the cache is
a union of runs; the six GFX archives and the 49 rows are present in both.

## Census denominator

The parent is the union of the 782 `unique_archives` in the current run summary
and the 67 further manifests in the same cache. The predicates are applied in
this order:

| Order | Stage | Predicate | Count removed | Count carried |
| ---: | --- | --- | ---: | ---: |
| 1 | Parent | every record with `kind == "row"` in the 849 manifests | - | 183,144 |
| 2 | Readable | `contents.readable == true` | 823 unreadable | 182,321 |
| 3 | Stored-prefix scan | read four bytes at `payload_offset` from the matching cached archive | - | 182,321 scanned; 0 `GFX` |
| 4 | Decoded type 66 | `type_id == 66` | 49 | 182,272 stored-prefix-only |
| 5 | Decoded type 5 | `type_id == 5` in the six GFX archives | 37 | 182,235 stored-prefix-only |

The 49 type-66 and 37 type-5 rows are all readable and all in the same six
archives. The stored-prefix scan covered all 182,321 readable rows, including
those 86; 182,235 is the number of readable rows whose only check was the stored
prefix. The 823 unreadable rows have no stored-prefix check.

To re-run the count, read each `<CACHE>/manifests/*.jsonl`, count its
`kind == "row"` records, test `contents.readable`, seek to `payload_offset` in
`<CACHE>/archives/<manifest-sha>.rpf` and read four bytes. Count `type_id == 66`,
then group the rows by manifest and count `type_id == 5` in the six manifests
that contain type-66 rows.

## Findings

| ID | Claim | Evidence | Confidence | Limits |
| --- | --- | --- | --- | --- |
| GFX-F01 | `GFX` begins the decoded payload of 49 type-66 rows in six depth-1 archives under `data.rpf`. All 49 rows use chunk encoding 3, mode 0 and no payload transform; all 49 stored payloads begin `78 DA`. A stored-prefix scan covers all 182,321 readable rows and finds 0 stored `GFX` prefixes; the 49 type-66 and 37 type-5 rows in the six GFX archives were also decoded, leaving 182,235 rows checked only at the stored prefix. | `BINARY`, `CROSS_SAMPLE` | Confirmed (49/49) | One build and one local archive set; the count is the type-66 count of the sampled population, not a decoded census of every row. The 823 unreadable rows have no stored-prefix check |
| GFX-F02 | The 49 decoded lengths are distinct and range from 2,251 to 6,605,786 bytes. In every row the decoded length equals the manifest logical size and the little-endian `u32` at `+0x04`. The 11 multi-chunk rows were reconstructed end to end. | `BINARY`, `CROSS_SAMPLE` | Confirmed (49/49) | No second archive set |
| GFX-F03 | The container header is `GFX` at `+0x00`, version `0x2A` at `+0x03`, a little-endian `u32` length at `+0x04`, then a SWF header. All 49 rows have version 42 and a length field equal to the payload length; no payload has another version or a length mismatch. | `BINARY`, `CROSS_SAMPLE` | Confirmed (49/49) | The GFx name rests on the documented header shape; no executable path was traced |
| GFX-F04 | The SWF header begins with a bit-packed RECT. Its first byte gives `nbits = byte >> 3` and its size is `ceil((5 + 4 * nbits) / 8)` bytes. Observed `nbits` values are 14 (2 rows), 15 (2), 16 (28) and 17 (17); first tag offsets are `+0x14` (2), `+0x15` (30) and `+0x16` (17). The previous revision read `+0x08`/`+0x0A` as variant pairs; those bytes are RECT bytes, not payload variants. | `BINARY`, `CROSS_SAMPLE` | Confirmed (bytes and sizes); Unknown (RECT coordinates) | Coordinate values were not decoded |
| GFX-F05 | The frame rate is a little-endian `u16` in 8.8 fixed point after the RECT. It is 30.0 in 48 rows and 24.0 in one. The frame count is a little-endian `u16` and is 1 in all 49 rows. | `BINARY`, `CROSS_SAMPLE` | Confirmed (49/49) | The frame rate is not uniform across the sample |
| GFX-F06 | After the frame header the payload is a tag stream. A record has a little-endian `u16` header with `code = header >> 6` and `length = header & 0x3F`; a length of 63 is followed by a little-endian `u32`. The walk reaches the payload end in 49/49 rows and has 0 failures. Top-level tag counts range from 8 to 2,839 and sum to 12,167. The first tag code is 1000 in 49/49 and its length is 15 to 42. The last two top-level codes are 1 and 0 in 49/49. | `BINARY`, `CROSS_SAMPLE`, `SYNTHETIC` | Confirmed (49/49) | Tag bodies are not interpreted; the synthetic tests validate the tool, not the native format |
| GFX-F07 | Tag code 39 is the only code whose body the sample walker also reads. Its body begins with two `u16` values (four bytes) followed by a record stream; the values are not interpreted. 41 payloads contain at least one tag 39; the sample has 1,025 tag 39 records and 102,306 nested records. The maximum nesting depth is 1. Including nested records raises the total from 12,167 to 114,473 records. A tag count MUST state whether it includes nested records. | `BINARY`, `CROSS_SAMPLE`, `SYNTHETIC` | Confirmed (49/49) | Nesting is measured only through tag 39; other tag bodies are skipped. The tag is not named and its prefix is not interpreted |
| GFX-F08 | The final four bytes are two adjacent zero-length tag headers, `40 00 00 00`: ShowFrame (code 1) and End (code 0). The previous revision recorded a little-endian `u32` 64; that reading is corrected. The printable run immediately before the headers ends at `length - 6`, followed by a zero byte and the two headers. | `BINARY`, `CROSS_SAMPLE` | Confirmed (49/49) | The five-byte printable suffix is not reproduced |
| GFX-F09 | In this 49-payload sample, three payloads have 11, 28 and 261 top-level tags. Including records nested in tag 39, the same three have 13, 5,616 and 4,227 records. A tag count MUST state whether it includes nested records. | `BINARY`, `CROSS_SAMPLE` | Confirmed (sample) | Three selected payloads; the counts are not identifiers |
| GFX-F10 | The first tag body is a ten-byte prefix, a printable run of 3 to 30 bytes and two further bytes. The run is preceded by a big-endian `u16` length equal to its length in 49/49 rows. The 15-byte group after the run spans a tag boundary: its first two bytes end the first tag, then the next tag's two-byte header and eleven body bytes follow. A second printable run starts 13 bytes after the first tag ends, contains the first run, ends in a constant five-byte suffix and is followed by a zero byte. The rest of the payload is further tags. | `BINARY`, `CROSS_SAMPLE` | Confirmed (bytes and positions); Unknown (meaning) | The printable text and class names are not reproduced; the previous opaque-body and single-tag readings are withdrawn |
| GFX-F11 | All observed GFX rows are type 66. In the six GFX archives, 0 of 37 type-5 rows begin `GFX` after decoding. A bounded sample across eight non-type-66 encoding-3 types decoded 37 rows and found 0 `GFX`; one type-14 row was behind the payload transform. | `BINARY`, `CROSS_SAMPLE` | Confirmed (sample); no exclusivity claim | The cross-type scan is a bounded sample, not a decoded census of all rows |
| GFX-F12 | No two payloads are byte-identical: 49 distinct SHA-256 values and 49 distinct lengths. The only prefix shared by all 49 is the four-byte signature; no pair shares the first eight bytes. | `BINARY`, `CROSS_SAMPLE` | Confirmed (49/49) | Pairwise suffix figures are not reported |

## Corrections

The previous revision of this index and format document described five
`+0x08`/`+0x0A` variant pairs, an opaque body after the second printable run, and
a ten-byte trailer containing a little-endian `u32` 64. The 49-row tag walk
changes those readings:

- The `+0x08` and `+0x0A` bytes are inside the RECT. They are byte patterns of
  the RECT, not payload variants.
- The region after the second run is a tag stream, not an opaque body.
- The last four bytes are the two zero-length tag headers for ShowFrame and End,
  not a `u32` field.
- The family is identified as the GFx container, not an unidentified signature.

The current tree contains no statement that compared only the three-byte
prefix; the previous predicate already used four bytes. The signature is now
recorded as three magic bytes plus the version byte, so a three-byte comparison
is insufficient.

See [research-history.md](research-history.md).

## Reproduction

`<GAME_ROOT>`, `<EXECUTABLE>` and `<WORK>` are local inputs. Payloads are not
part of this repository.

```text
lforge archive extract <GAME_ROOT>/data.rpf --row <ROW> --executable <EXECUTABLE> --output <WORK>/archive.rpf
lforge archive manifest <WORK>/archive.rpf --executable <EXECUTABLE> --format jsonl --output <WORK>/archive.jsonl
lforge archive extract <WORK>/archive.rpf --row <NESTED_ROW> --executable <EXECUTABLE> --output <WORK>/payload.bin
```

The manifest predicate is `type_id == 66`; the decoded predicate is
`payload[0:3] == 47 46 58` and `payload[3] == 0x2A`. The sampler is
[tools/gfx](../../tools/gfx/README.md).

## Limits

- One build and one local archive set.
- The GFX population is the type-66 row set of the cached depth-1 inventories.
  The bounded cross-type sample does not establish that no other type carries
  `GFX` outside the sampled archives.
- The RECT coordinates, tag bodies, ActionScript and rendering remain Unknown.
- The inventory reached depth 1. Type-66 rows below that depth were not searched.
- No executable path was traced. The archive name, type ID and GFx name are
  identifiers for this sample only.
- Movie strings and class names are not reproduced in repository text.

## Open questions

- What do the non-zero tag codes and their bodies mean?
- Do the RECT coordinate values describe bounds, stage size or another layout?
- Why does one payload use frame rate 24.0 while 48 use 30.0?
- What structural role, if any, do the constant first-tag body bytes and the
  five-byte printable suffix have?

## Six sample rows carried over

The six rows below were recorded before this index existed. They are kept because they are the only per-row stored and logical sizes in the record; every claim they support is restated with the full 49-row population in GFX-F01 to GFX-F12.

| Source | Nested row | Stored bytes | Logical bytes | First eight decoded bytes |
| --- | ---: | ---: | ---: | --- |
| `data.rpf` row 20 | 0 | 1,632 | 2,688 | `47 46 58 2A 80 0A 00 00` |
| `data.rpf` row 1 | 4 | 6,288 | 12,107 | `47 46 58 2A 4B 2F 00 00` |
| `data.rpf` row 1 | 6 | 1,408 | 2,251 | `47 46 58 2A CB 08 00 00` |
| `data.rpf` row 1 | 7 | 3,072 | 6,250 | `47 46 58 2A 6A 18 00 00` |
| `data.rpf` row 19 | 45 | 2,432 | 5,345 | `47 46 58 2A E1 14 00 00` |
| `data.rpf` row 19 | 48 | 2,816 | 5,463 | `47 46 58 2A 57 15 00 00` |
