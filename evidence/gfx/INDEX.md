# GFX* evidence index

`GFX*` is a four-byte decoded-payload observation. This index records the
sample, the predicate, the structural findings and the corrections. The
identifier remains the observed signature; no format name is claimed.

## Earlier claim

| Claim | First recorded in | Sample | Observation level |
| --- | --- | --- | --- |
| `GFX*` under type 66 | Unmerged `research/shared/resource-identification` branch, type inventory commits `1cee8cb` and `ce8629d` | 22,926 rows: five root archives walked, 61 nested archives opened; 49 type-66 rows in six archives | Decoded payload head; every type-66 row is chunked |

The first GFX document described six decoded payloads. The 49-row recount
confirms the type-66 association and the six archives, and adds the full
structure recorded below.

## Sample and predicate

| Property | Value |
| --- | --- |
| Build | [scarlett-e95020b2](../../builds/gta-vi/scarlett-e95020b2/README.md) |
| Population | 849 unique depth-1 manifests in the cached inventory, 183,144 row records (182,321 readable, 823 unreadable) |
| Earlier run frame | 782 unique archives, 169,523 rows; the cache directory holds 67 further unique archives with 13,621 rows |
| GFX rows | 49 type-66 rows in six depth-1 archives reached from `data.rpf` rows 1, 3, 6, 19, 20 and 39 |
| Stored form | chunk encoding 3, mode 0, no payload transform, stored prefix `78 DA` |
| Predicate | exact four bytes `47 46 58 2A` at decoded offset 0 |
| Predicate scope | prefix at offset 0; not a whole-file hash and not a substring search |
| Stored-byte result | 0 of all 182,321 readable rows begin `GFX*` at the stored payload offset |

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
| 3 | Stored-prefix scan | read four bytes at `payload_offset` from the matching cached archive | - | 182,321 scanned; 0 `GFX*` |
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
| GFX-F01 | `GFX*` begins the decoded payload of 49 type-66 rows in six depth-1 archives under `data.rpf`. All 49 rows use chunk encoding 3, mode 0 and no payload transform; all 49 stored payloads begin `78 DA`. A stored-prefix scan covers all 182,321 readable rows and finds 0 stored `GFX*` prefixes; the 49 type-66 and 37 type-5 rows in the six GFX archives were also decoded, leaving 182,235 rows checked only at the stored prefix. | `BINARY`, `CROSS_SAMPLE` | Confirmed (49/49) | One build and one local archive set; the count is the type-66 count of the sampled population, not a decoded census of every row. The 823 unreadable rows have no stored-prefix check |
| GFX-F02 | The 49 decoded lengths are distinct and range from 2,251 to 6,605,786 bytes. In every row the decoded length equals the manifest logical size and the little-endian `u32` at `+0x04`. The 11 multi-chunk rows were reconstructed end to end. | `BINARY`, `CROSS_SAMPLE` | Confirmed (49/49) | No second archive set |
| GFX-F03 | The bytes at `+0x08` and `+0x0A` form five observed pairs: `88/01` (17 rows, first run at `+0x22`), `80/02` (28, `+0x21`), `78/05` (2, `+0x21`), `70/0B` (1, `+0x20`) and `70/0A` (1, `+0x20`). The pairs co-occur within one archive. | `BINARY`, `CROSS_SAMPLE` | Confirmed (49/49) | The pairs are observable variants; version, purpose and field meaning are Unknown |
| GFX-F04 | The pre-name header is not fixed-size, but its tail is fixed relative to the first run. In all 49 rows the nine bytes immediately before the run length are `FA 01 04 00 00 00 00 0E 00`; the next two bytes are a big-endian `u16` first-run length (3 to 30); the run is printable ASCII. The four bytes before that run are `30 01 00 v` in 48 rows and `18 01 00 v` in 1, with `v` from 15 to 42. | `BINARY`, `CROSS_SAMPLE` | Confirmed (49/49) | Bytes between `+0x0B` and that run vary; their meaning is Unknown |
| GFX-F05 | The first run is followed by a 15-byte interstitial. Its first ten bytes are constant `00 00 44 11 09 00 00 00 43 02` in 49/49; the next three bytes are `00 00 00` (46), `FF 00 00` (2) or `FF FF FF` (1); the fifteenth byte is `0x0A` in 49/49. The second printable run starts 15 bytes after the first run and ends `_Main` and contains the first run in 49/49. | `BINARY`, `CROSS_SAMPLE` | Confirmed (bytes and positions); Unknown (meaning) | Four values in the variable group; their roles are not established |
| GFX-F06 | Every payload ends with a ten-byte trailer: the five-byte printable run `.Main`, a zero byte and the little-endian `u32` 64. The trailer is the common suffix of all 49 payloads. The 17 to 54 byte range belongs to the second run, not to the trailer. | `BINARY`, `CROSS_SAMPLE` | Confirmed (49/49) | The trailer's `.Main` is not shown to be a name or a path |
| GFX-F07 | The established grammar stops at the first byte after the second run. That offset is 69 to 132. The body's first two bytes take 21 distinct pairs; the most common pair occurs in 15 of 49. The three constant markers occur exactly once per payload and never in the body. | `BINARY`, `CROSS_SAMPLE` | Confirmed (positions and counts); Unknown (body content) | The body was not parsed |
| GFX-F08 | No two payloads are byte-identical: 49 distinct SHA-256 values and 49 distinct lengths. The only prefix shared by all 49 is the four-byte signature; no pair shares the first eight bytes. 109 of 1,176 pairs share more than the ten-byte common suffix, up to 29 bytes. | `BINARY`, `CROSS_SAMPLE` | Confirmed (49/49) | Pairwise suffix figures are sample counts |
| GFX-F09 | A search over every one-, two- and four-byte field in the first 64 bytes, in both byte orders, found no field equal to the body start, body length, first run length or second run length. The only matching field is the `u32` at `+0x04`, equal to the total decoded length. | `BINARY`, `CROSS_SAMPLE` | Confirmed (49/49) | Equality only; other arithmetic relations were not tested |
| GFX-F10 | All observed GFX rows are type 66. In the six GFX archives, 0 of 37 type-5 rows begin `GFX*` after decoding. A bounded sample across eight non-type-66 encoding-3 types decoded 37 rows and found 0 `GFX*`; one type-14 row was behind the payload transform. | `BINARY`, `CROSS_SAMPLE` | Confirmed (sample); no exclusivity claim | The cross-type scan is a bounded sample, not a decoded census of all rows |

## Corrections

The first GFX document described two header forms from six payloads and split
the first-run length into a `u16` form and a `u8` form. The 49-row decode shows
five `+0x08`/`+0x0A` pairs and one big-endian `u16` length in every form; the
apparent `u8` was the low byte of that field. The earlier absolute offset for
the second run was a property of the two payloads inspected. See
[research-history.md](research-history.md).

## Reproduction

`<GAME_ROOT>`, `<EXECUTABLE>` and `<WORK>` are local inputs. Payloads are not
part of this repository.

```text
lforge archive extract <GAME_ROOT>/data.rpf --row <ROW> --executable <EXECUTABLE> --output <WORK>/archive.rpf
lforge archive manifest <WORK>/archive.rpf --executable <EXECUTABLE> --format jsonl --output <WORK>/archive.jsonl
lforge archive extract <WORK>/archive.rpf --row <NESTED_ROW> --executable <EXECUTABLE> --output <WORK>/payload.bin
```

The manifest predicate is `type_id == 66`; the decoded predicate is
`payload[0:4] == 47 46 58 2A`. The structural sampler is
[tools/gfx](../../tools/gfx/README.md).

## Limits

- One build and one local archive set.
- The GFX population is the type-66 row set of the cached depth-1 inventories.
  The bounded cross-type sample does not establish that no other type carries
  `GFX*` outside the sampled archives.
- The body and every pre-name byte between `+0x0B` and the fixed run remain
  Unknown.
- The inventory reached depth 1. Type-66 rows below that depth were not searched.
- No executable path was traced. The archive name, type ID and signature are
  identifiers for this sample only.
- The ASCII runs are not reproduced in repository text.

## Open questions

- What distinguishes the five variant pairs, and do they mark versions, payload
  kinds or stored properties?
- Does the `u32` 64 in the trailer have a structural role, or is it a constant?
- What marks the end of the body, and does the body have a record grammar?
