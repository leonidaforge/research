# ADAT evidence index

The current ADAT findings are in [evidence/adat/INDEX.md](../adat/INDEX.md). The
ADAT sections below are the earlier 21-row record; their findings `ADAT-F01` to
`ADAT-F05` are superseded and the identifiers are retired.

Two payload signatures were recorded in earlier notes: `GFX*` under type ID 66,
whose observations are now in [GFX*](../gfx/INDEX.md), and `ADAT` under type ID
255 in `audio.rpf`. This index recovers the observation level of each claim, the
sample that produced it, and why a later top-level stored-byte census did not
repeat it.

`ADAT` does not occur at offset 0 of a top-level row, so it does not belong to
the census that reads only the first eight stored bytes of the 6,534 top-level
rows.

## Earlier claim

| Claim | First recorded in | Sample | Observation level |
| --- | --- | --- | --- |
| `ADAT` under type 255 in `audio.rpf` | Coordination report "Nested inventory" on branch `research/coordination`, commit `ba24272` | 17 depth-1 archives: one smallest readable type-0 row up to 2 MiB per top-level archive | Decoded type-0 payload opened as a nested archive; stored payload head of its type-255 rows |

## Sample frames

| Frame | Scope | Rows | Signature reading |
| --- | --- | ---: | --- |
| Top-level stored-byte census (UPL-F01) | 22 top-level archives | 6,534 | First eight stored bytes of each untransformed top-level row |
| Inventory on `main` (INV-F09 to INV-F17) | 250 depth-1 archives | 38,395 | 130 payload attempts, eight bytes each |
| Newer scratch run | 782 depth-1 archives | 169,523 | 144 payload attempts, eight bytes each; all 782 archives cached |
| Discovery sample behind the earlier notes | 17 depth-1 archives | Not aggregated | Payload heads read after extraction |

The newer scratch run selected all 60 readable type-0 rows of `audio.rpf` within
its 64 MiB archive cap. Its cache is the source of the counts below. It is newer
than the 250-archive index on `main`; its counts are not yet in that index.

The parent type-0 rows are stored without a chunk table: `audio.rpf` rows 42 and
77 are 3,584,368 and 145,888 bytes.

## Why the top-level census does not show ADAT

- `audio.rpf` has 103 top-level rows, all type 0. It has no type-255 row.
- The 60 depth-1 archives reached from `audio.rpf` hold 747 type-255 rows. 729
  begin `ADAT` at their payload offset; 59 of the 60 archives contain at least
  one. The remaining 18 rows, all in one archive, are chunked and begin a zlib
  stream at the payload offset.
- A top-level `audio.rpf` row begins `39 46 50 52` (`9FPR`); `ADAT` is at the
  start of a nested type-255 payload, not at the start of the type-0 row.
- The 144-payload prefix sample selected no ADAT row. The inventory prefix
  classes cover zero-prefix, `PSIN` and `RBF0`, so `ADAT` remained in its
  "unrecognized" class.

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
169,523 rows. It finds 729 type-255 rows that begin `ADAT` at the payload
offset. The run did not extract 3,188 eligible top-level type-0 rows or 381
above its 64 MiB cap, so the counts are sample counts.

## Missing link

The discovery sample that first reported the signature was scratch-only. Its
payload heads were read after nested archive extraction, but the repository
inventory retains prefix classes for zero-prefix, `PSIN` and `RBF0`. `ADAT`
therefore fell into "unrecognized". The top-level stored-byte census could not
see it for a different reason: it occurs one level below it.

## Reproduction

`<GAME_ROOT>` is a local installation, `<EXECUTABLE>` the matching executable
used only to authenticate metadata, and `<WORK>` a scratch directory outside
the repository.

```text
lforge archive extract <GAME_ROOT>/audio.rpf --row 77 --executable <EXECUTABLE> --output <WORK>/audio-row77.rpf
lforge archive manifest <WORK>/audio-row77.rpf --executable <EXECUTABLE> --format jsonl --output <WORK>/audio-row77.jsonl
```

The `audio.rpf` type-255 rows are stored, so their payload bytes can be read at
the manifest offsets directly. Payload files are not part of this repository.

## Limits

- One build ([scarlett-e95020b2](../../builds/gta-vi/scarlett-e95020b2/README.md))
  and one local archive set.
- The ADAT structure comes from 21 rows in two archives; the other 708 ADAT
  rows were checked only for their first eight bytes and manifest fields.
- No executable path was traced. The archive name is provenance, not evidence
  of purpose, and no field meaning is established.
- The 782-archive run is scratch output. Its counts are not yet part of the
  inventory index on `main`.

## Open questions

- What do the `ADAT` values at `+0x06`, `+0x08` and `+0x0C` represent?
- Why does one archive hold 18 type-255 rows with zlib at the payload offset
  while 59 archives hold stored ADAT rows?
- Are there type-255 rows below depth 1? The current sample reaches depth 1 only.
