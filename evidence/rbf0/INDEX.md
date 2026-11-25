# RBF0 evidence index

Payload observations from the Scarlett build [e95020b2](../../builds/gta-vi/scarlett-e95020b2/README.md). No executable code path was traced. Every finding is **Private-evidence supported**. Corrected interpretations are recorded in [research-history.md](research-history.md).

## Sample

| Property               | Value                                                                                                                                                                                                                                                                |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Nested archive         | row 0 of `<GAME_ROOT>/data.rpf`, a nested RPF9 archive                                                                                                                                                                                                               |
| Nested archive SHA-256 | `91A236BCB4ECF96840BC0B70E22D1619C0FEDFA11976A336DE311A438214A09E`                                                                                                                                                                                                   |
| Nested archive size    | 414544 bytes                                                                                                                                                                                                                                                         |
| Rows                   | 156 rows, type ID 11, in the nested archive                                                                                                                                                                                                                          |
| Verified RBF0 rows     | 0 (12324), 1 (285), 2 (3883), 3 (2223), 4 (291), 5 (601), 6 (1759), 7 (12087), 8 (165145), 9 (218), 10 (1409), 15 (51045), 72 (77902), 78 (57473), 90 (100958), 141 (596616), 154 (652), 155 (30092) bytes |
| Sample SHA-256 (row 1) | `C0A57DF9C6B93DA6A41AF04BC51C1621A369929E02EFD1BD5BAECA2375ACF0AB`                                                                                                                                                                                                   |

The hashes identify derived samples. They contain no asset text.

## Survey of other type ID 11 rows

| Source                                                    | Type ID 11 rows | Decoded samples | First four bytes |
| --------------------------------------------------------- | --------------- | --------------- | ---------------- |
| Nested archive above                                      | 156             | 18              | `RBF0`           |
| Second nested archive, row 15 of `<GAME_ROOT>/data.rpf`    | 155             | 3               | `PSIN`           |
| `story000_restofworld.rpf`                                | 1               | 1               | `PSIN`           |
| `shared_minigame000.rpf`                                  | 2               | 1               | `PSIN`           |
| `story000.rpf`                                            | 25              | 1               | `PSIN`           |
| `core_restofworld.rpf`                                    | 7               | 1               | `PSIN`           |

The second nested archive has SHA-256 `CBAD926F4210CB56FD048EA17FE943BFB6AAD68C3EFEEDDBD2C6D261A78ACD78` and size 755200 bytes. Its three decoded type ID 11 payloads start with `PSIN`. Type ID 11 is not an RBF0 identifier.

## Evidence types

| Type              | Meaning                                                                    |
| ----------------- | -------------------------------------------------------------------------- |
| Payload data      | Bytes read from a decoded RPF9 payload, not traced in executable code      |
| Tool output       | A row record, manifest field or extraction result printed by the local CLI |
| Consistency check | A property compared across all verified rows                               |

## Findings

| ID       | Claim                                                                                                                                                                                                 | Evidence                        | Confidence                           | Limits                                                           |
| -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------- | ------------------------------------ | ---------------------------------------------------------------- |
| RBF0-F01 | Payloads start with ASCII `RBF0` (`0x30464252`) at offset 0                                                                                                                                            | Payload data                    | Confirmed                            | 18 rows, one RBF0-bearing archive                                |
| RBF0-F02 | The first 10 bytes `52 42 46 30 FB FF 01 00 00 00` are identical in all verified rows. `+0x0A` holds the root name length: 17 in 17 rows and 15 in one row. The old fixed 12-byte claim is corrected | Consistency check               | Confirmed                            | One document family                                              |
| RBF0-F03 | The root name follows the length at `+0x0C`, has no terminator, and is identical in the 17 rows that use the 17-byte name. One row uses a different 15-byte name                                | Payload data                    | Confirmed                            | One document family; names not published                         |
| RBF0-F04 | Field names repeat across payloads but are defined once per payload on first use; later uses omit the length and name bytes. Across 18 rows there are 118 definitions and 18 distinct ASCII names, 4 to 17 bytes, with no NUL | Payload data, consistency check | Confirmed                            | Field meaning and whether the name set identifies a schema are Unknown |
| RBF0-F05 | An object value is `u32 0`, `u16 attribute_count`, that many attributes, zero or more fields, then `u16 0xFFFF`. The root body uses the same form after the header                                  | Payload data, tool output       | Confirmed                            | 18 rows                                                          |
| RBF0-F06 | RPF9 type ID 11 carries at least RBF0 and PSIN. A second nested archive and four top-level pack archives yield PSIN payloads for type ID 11, so the type ID does not identify RBF0                 | Payload data, tool output       | Confirmed                            | Surveyed rows, not every type ID 11 row                          |
| RBF0-F07 | The verified rows decode from mode-1 raw DEFLATE; the row records report mode 1 and no chunk table. The storage observation is recorded in RPF9-F118                                  | Payload data, tool output       | Confirmed                            | 18 extractions; one nested archive; one row failed in an earlier pass |
| RBF0-F08 | An attribute is `u16 value_len` followed by bytes, with no terminator and no NUL. All 14,127 observed values are ASCII, 8 to 26 bytes long                                               | Payload data, consistency check | Confirmed                            | One document family                                              |
| RBF0-F09 | One row carries field `0x1006` with an 8-byte value and no length prefix or terminator. Every observed value is `FF` x 8                                              | Payload data                    | Confirmed                            | One row; value meaning is Unknown                                |
| RBF0-F10 | Every string value ends with `u16 0xFFFF`, every object ends with `u16 0xFFFF`, and all 18 payloads end with exactly eight `FF` bytes                                                                  | Consistency check               | Confirmed                            | 18 rows                                                          |
| RBF0-F11 | Field identifiers allocate low 12-bit slots in first-definition order starting at 1. Observed groups: `0x0001`/`0x0002` object, `0x0004`-`0x000A` string, `0x1006` fixed 8 bytes, `0x6003`/`0x6004` attribute | Payload data, consistency check | Confirmed                            | Observed groups only; high-nibble meaning beyond them is Unknown |
| RBF0-F12 | A string field is `u32 0`, `u16 0`, `u16 0xFFFD`, `u32 byte_len`, bytes, `u16 0xFFFF`. All 15,305 observed values end in one NUL, are valid UTF-8, and are 2 to 1,990 bytes long. 334 contain non-ASCII bytes | Payload data, consistency check | Confirmed                            | Observed values only; no empty value observed                    |
| RBF0-F13 | Ten additional RBF0 rows decode from the same nested archive: rows 0, 2, 3, 4, 6, 7, 8, 9, 10 and 154. The sample grows from 8 to 18 rows                                                       | Payload data, tool output       | Confirmed                            | Same archive; selection not random                                |
| RBF0-F14 | The eight trailing `FF` bytes are four consecutive `0xFFFF` words inferred to close the last string value, its object, the container object and the root object                                      | Consistency check               | Speculative                          | Inference from the grammar; no per-word level markers             |

## Reproduction

Commands ran on 2026-11-25 with the `lforge` CLI built from `leonidaforge/leonida-forge` commit `6b362ad`, and with the release binary reporting `lforge 0.1.0` for the added rows. `<GAME_ROOT>` is a local installation, `<WORK>` a scratch directory outside it, and `<EXECUTABLE>` the game executable that matches the archive, used only to authenticate its metadata.

```text
lforge archive extract <GAME_ROOT>/data.rpf --row 0 --output <WORK>/data-row0.rpf --executable <EXECUTABLE>
lforge archive ls <WORK>/data-row0.rpf --executable <EXECUTABLE>
lforge archive manifest <WORK>/data-row0.rpf --executable <EXECUTABLE> --format jsonl --output <WORK>/rows.jsonl
lforge archive extract <WORK>/data-row0.rpf --row <N> --output <WORK>/r<N>.bin --executable <EXECUTABLE>
python tools/rbf0/rbf0_inspect.py <WORK>/r<N>.bin
```

`archive ls` lists the type 11 rows. `archive manifest` records each row's `mode` and `chunks`. `archive extract` reports `raw DEFLATE` for these rows and writes the decoded payload. The inspector reports the header, object and field counts, field definitions and unsupported tags. It does not print names or text values.

The survey rows came from the inventory manifests and were decoded the same way. The second nested archive was row 15 of `<GAME_ROOT>/data.rpf`; the top-level samples came from `story000_restofworld.rpf`, `shared_minigame000.rpf`, `story000.rpf` and `core_restofworld.rpf`.

## Limits

- Eighteen of 156 rows were decoded. The remaining rows were not verified, so only these 18 rows are known to carry RBF0.
- One row of the same archive failed to decode with a DEFLATE error in an earlier pass, so not every type ID 11 row is readable through the tool version used for the first sample.
- No counterexample to the 10-byte header prefix was found, but the sample is one RBF0-bearing archive.
- Payload names and text, including the root and field names, are game content and were not copied into this repository.
- The survey does not cover every type ID 11 row in every archive.

## Next experiments

- Decode all 156 rows and check the header, grammar and terminator counts against the full set.
- Find a second RBF0-bearing archive and compare root names and name sets.
- Search the executable for the magic and root-name references to establish the loader and the encoding name, without publishing key material.
- Test other high-nibble field groups against documents that carry numeric or binary values.
