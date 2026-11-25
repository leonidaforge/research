# GFX* and ADAT evidence index

Two payload signatures recorded in earlier notes: `GFX*` under type ID 66 and
`ADAT` under type ID 255 in `audio.rpf`. This index recovers the observation
level of each claim, the sample that produced it, and why a later top-level
stored-byte census did not repeat it.

Both are nested-payload observations. `GFX*` is a decoded-payload head from
chunked type-66 rows. `ADAT` is a stored-payload head from type-255 rows inside
depth-1 archives reached from `audio.rpf`. Neither signature occurs at offset 0
of a top-level row, so neither belongs to the census that reads only the first
eight stored bytes of the 6,534 top-level rows.

## Earlier claims

| Claim | First recorded in | Sample | Observation level |
| --- | --- | --- | --- |
| `GFX*` under type 66 | Unmerged `research/shared/resource-identification` branch, type inventory commits `1cee8cb` and `ce8629d` | 22,926 rows: five root archives walked, 61 nested archives opened; 49 type-66 rows in six archives | Decoded payload head; every type-66 row is chunked |
| `ADAT` under type 255 in `audio.rpf` | Coordination report "Nested inventory" on branch `research/coordination`, commit `ba24272` | 17 depth-1 archives: one smallest readable type-0 row up to 2 MiB per top-level archive | Decoded type-0 payload opened as a nested archive; stored payload head of its type-255 rows |

The unmerged type inventory also records `GFX*` in its findings table. Its
finding numbering differs from the current RPF9 index and is not reused here.

## Sample frames

| Frame | Scope | Rows | Signature reading |
| --- | --- | ---: | --- |
| Top-level stored-byte census (UPL-F01) | 22 top-level archives | 6,534 | First eight stored bytes of each untransformed top-level row |
| Inventory on `main` (INV-F09 to INV-F17) | 250 depth-1 archives | 38,395 | 130 payload attempts, eight bytes each |
| Newer scratch run | 782 depth-1 archives | 169,523 | 144 payload attempts, eight bytes each; all 782 archives cached |
| Discovery sample behind the earlier notes | 17 depth-1 archives | Not aggregated | Payload heads read after extraction |

The newer scratch run selected all 60 readable type-0 rows of `audio.rpf` and
all 39 of `data.rpf` within its 64 MiB archive cap. Its cache is the source of
the counts below. It is newer than the 250-archive index on `main`; its counts
are not yet in that index.

The parent type-0 rows are stored without a chunk table: `data.rpf` rows 1, 19
and 20 are 1,110,576, 2,082,992 and 5,776 bytes; `audio.rpf` rows 42 and 77 are
3,584,368 and 145,888 bytes.

## Why the top-level census does not show the signatures

### GFX*

- `data.rpf` has 699 top-level rows: 41 type 0, 657 type 11 and one type 14. It
  has no type-66 row.
- Type 66 occurs only in depth-1 archives reached from `data.rpf` rows 1, 3, 6,
  19, 20 and 39. Those six archives hold 49 type-66 rows, all readable and all
  with chunk encoding 3.
- The stored bytes at every type-66 payload offset begin `78 DA`, a zlib
  stream. The decoded payload begins `47 46 58 2A` (`GFX*`).
- The census reads stored bytes, so every type-66 row appears there as a zlib
  stream. The signature exists only after chunk decoding.

### ADAT

- `audio.rpf` has 103 top-level rows, all type 0. It has no type-255 row.
- The 60 depth-1 archives reached from `audio.rpf` hold 747 type-255 rows. 729
  begin `ADAT` at their payload offset; 59 of the 60 archives contain at least
  one. The remaining 18 rows, all in one archive, are chunked and begin a zlib
  stream at the payload offset.
- A top-level `audio.rpf` row begins `39 46 50 52` (`9FPR`); `ADAT` is at the
  start of a nested type-255 payload, not at the start of the type-0 row.
- The 144-payload prefix sample selected no ADAT row. The inventory prefix
  classes cover zero-prefix, `PSIN` and `RBF0`, so `GFX*` and `ADAT` remained in
  its "unrecognized" class.

## GFX* samples

The six distinct decoded payloads below come from three of the six archives.
They are the type-66 rows present in the payload sample.

| Source | Nested row | Stored bytes | Logical bytes | First eight stored bytes | First eight decoded bytes |
| --- | ---: | ---: | ---: | --- | --- |
| `data.rpf` row 20 | 0 | 1,632 | 2,688 | `78 DA 85 56 CD 72 1A D9` | `47 46 58 2A 80 0A 00 00` |
| `data.rpf` row 1 | 4 | 6,288 | 12,107 | `78 DA DC 97 09 54 53 57` | `47 46 58 2A 4B 2F 00 00` |
| `data.rpf` row 1 | 6 | 1,408 | 2,251 | `78 DA 75 56 4B 53 1B 47` | `47 46 58 2A CB 08 00 00` |
| `data.rpf` row 1 | 7 | 3,072 | 6,250 | `78 DA 8D 97 7B 6C 5B F5` | `47 46 58 2A 6A 18 00 00` |
| `data.rpf` row 19 | 45 | 2,432 | 5,345 | `78 DA 9D 96 7D 6C 5B 57` | `47 46 58 2A E1 14 00 00` |
| `data.rpf` row 19 | 48 | 2,816 | 5,463 | `78 DA 9D 56 7B 6C 5B D5` | `47 46 58 2A 57 15 00 00` |

All 49 type-66 rows follow the same pattern after chunk decoding: the first
decoded chunk begins `GFX*`, and the `u32` at `+0x04` equals the row's logical
size. 38 rows are one chunk. The other 11 are multi-chunk; only their first
chunk was decoded here.

## ADAT samples

| Source | Nested rows | Type | Chunk table | Stored bytes | First eight bytes |
| --- | ---: | ---: | --- | --- | --- |
| `audio.rpf` row 42 | 11 | 255 | none | 69,728 to 741,488 | `41 44 41 54 01 00 25 FF` |
| `audio.rpf` row 77 | 10 | 255 | none | 4,224 to 33,984 | `41 44 41 54 01 00 21 FF` |

The two archives supply 21 rows. Their payload SHA-256 values are all distinct,
so the repeated stored sizes are not repeated content. The full 59-archive
census covers 729 rows from 4,224 to 51,693,440 bytes. All have no chunk table,
mode 0, and no payload transform. 630 store exactly their logical size; 99 add
up to fourteen bytes of padding.

## Findings

| ID | Claim | Evidence | Confidence | Limits |
| --- | --- | --- | --- | --- |
| GFX-F01 | `GFX*` (`47 46 58 2A`) begins the decoded payload of 49 type-66 rows in six depth-1 archives under `data.rpf`. Every type-66 row uses chunk encoding 3, and its stored bytes begin `78 DA`; the signature is visible only after chunk decoding. | Archive data, authenticated manifests, chunk decoding | Confirmed (sample) | Six archives and 49 rows from one build and one local archive set |
| GFX-F02 | The `u32` at `+0x04` of the decoded payload equals the row's logical size in all 49 rows. The six distinct sampled payloads are 2,251, 2,688, 5,345, 5,463, 6,250 and 12,107 bytes. | Payload data | Confirmed (sample) | 49 decoded first chunks; multi-chunk rows were not reconstructed end to end |
| GFX-F03 | The decoded payloads have two header forms: `88 00 01 xx` at `+0x08` in three samples and `80 00 02 xx` in three. A length field at `+0x20` precedes a printable ASCII run; the field is a `u16` in the first form and a `u8` in the second. A second printable run begins at `+0x37` in the two payloads inspected for it. | Payload data | Confirmed (bytes and positions); Unknown (meaning) | Six payloads; field meanings and the two forms are unexplained |
| GFX-F04 | The earlier 22,926-row claim is reproduced at its stated scope: 49 type-66 rows in six archives, all leading with `GFX*`. The type does not occur at top level, so the top-level stored-byte census cannot see it. | Authenticated manifests, archive data | Confirmed (sample) | Type 66 only; other types were not compared |
| ADAT-F01 | `ADAT` (`41 44 41 54`) begins 729 stored type-255 payloads in 59 depth-1 archives reached from `audio.rpf`. One further archive holds 18 type-255 rows that begin a zlib stream instead. | Archive data, authenticated manifests | Confirmed (sample) | 60 of 103 type-0 rows of `audio.rpf` were extracted; 43 larger rows were not |
| ADAT-F02 | In the 729 ADAT rows, `+0x04` is `u16` 1; `+0x06` is one of four values (`0xFF02`, `0xFF21`, `0xFF25`, `0xFF41`); `+0x08` is a small count from 1 to 231; and `+0x0C` is a value from 46 to 27,484 that is always below the payload size. | Payload data | Confirmed (values); Unknown (meaning) | Field roles are not established; the values are observations only |
| ADAT-F03 | All 729 ADAT rows have no chunk table, mode 0 and no payload transform. 630 have equal stored and logical sizes; 99 have up to fourteen bytes of trailing padding. Sizes range from 4,224 to 51,693,440 bytes. | Authenticated manifests | Confirmed (sample) | One build and one local archive set |
| ADAT-F04 | The 21 ADAT rows in the archives from `audio.rpf` rows 42 and 77 have 21 distinct SHA-256 payload fingerprints. | Hash fingerprint | Confirmed (sample) | Two archives; the other 57 archives were not hashed row by row |
| ADAT-F05 | The ADAT observation is a nested stored-payload observation. The type-0 rows that contain it begin `9FPR`, and `audio.rpf` has no top-level type-255 row. The top-level census and the 144-payload sample therefore did not reproduce it. | Authenticated manifests, archive data | Confirmed (scope) | The 144-payload sample is a selection, not a census |

## Bounded search procedure

1. Open the newer scratch inventory cache and select every manifest whose parent
   is a depth-1 archive reached from the target top-level archive.
2. For each row, read eight bytes at the manifest's `payload_offset` from the
   stored archive bytes. Require a signature match at offset 0.
3. For chunked rows, decode the first chunk before classifying the payload.
   Stored bytes of a chunked row are not the decoded head.
4. Treat `ADAT` inside printable XML text as a false positive. The substring
   also occurs inside `METADATA`; only offset 0 counts.
5. Record the archive, row, type ID, chunk table, stored and logical sizes, and
   the first eight bytes. Keep extracted payloads outside Git.

Applied to the newer scratch cache, the procedure covers 782 archives and
169,523 rows. It finds 49 type-66 rows whose first decoded chunk begins `GFX*`
and 729 type-255 rows that begin `ADAT` at the payload offset. The run did not
extract 3,188 eligible top-level type-0 rows or 381 above its 64 MiB cap, so the
counts are sample counts.

## Missing link

The discovery sample that first reported both signatures was scratch-only. Its
payload heads were read after nested archive extraction, but the repository
inventory retains prefix classes for zero-prefix, `PSIN` and `RBF0`.
`GFX*` and `ADAT` therefore fell into "unrecognized". The top-level stored-byte
census could not see them for a different reason: both occur one level below it,
and `GFX*` additionally requires chunk decoding. No finding on `main` named
either signature before this index.

## Reproduction

`<GAME_ROOT>` is a local installation, `<EXECUTABLE>` the matching executable
used only to authenticate metadata, and `<WORK>` a scratch directory outside
the repository.

```text
lforge archive extract <GAME_ROOT>/data.rpf --row 20 --executable <EXECUTABLE> --output <WORK>/data-row20.rpf
lforge archive manifest <WORK>/data-row20.rpf --executable <EXECUTABLE> --format jsonl --output <WORK>/data-row20.jsonl
lforge archive extract <WORK>/data-row20.rpf --row 0 --executable <EXECUTABLE> --output <WORK>/type66-row0.bin

lforge archive extract <GAME_ROOT>/audio.rpf --row 77 --executable <EXECUTABLE> --output <WORK>/audio-row77.rpf
lforge archive manifest <WORK>/audio-row77.rpf --executable <EXECUTABLE> --format jsonl --output <WORK>/audio-row77.jsonl
```

The type-66 payload must be extracted because its stored bytes are a zlib
stream. The `audio.rpf` type-255 rows are stored, so their payload bytes can be
read at the manifest offsets directly. Payload files are not part of this
repository.

## Limits

- One build ([scarlett-e95020b2](../../builds/gta-vi/scarlett-e95020b2/README.md))
  and one local archive set.
- The GFX* structure comes from six distinct payloads; the 43 other type-66 rows
  were checked only for the first decoded chunk and the size field.
- The ADAT structure comes from 21 rows in two archives; the other 708 ADAT
  rows were checked only for their first eight bytes and manifest fields.
- No executable path was traced. The archive names are provenance, not
  evidence of purpose, and no field meaning is established.
- The 782-archive run is scratch output. Its counts are not yet part of the
  inventory index on `main`.

## Open questions

- Do the two `GFX*` header forms at `+0x08` mark versions, or two payload
  kinds?
- What do the `ADAT` values at `+0x06`, `+0x08` and `+0x0C` represent?
- Why does one archive hold 18 type-255 rows with zlib at the payload offset
  while 59 archives hold stored ADAT rows?
- Are there type-66 or type-255 rows below depth 1? The current sample reaches
  depth 1 only.
