# RBF0 evidence index

Payload observations from the Scarlett build [e95020b2](../../builds/gta-vi/scarlett-e95020b2/README.md). No executable code path was traced. Every finding is **Private-evidence supported**.

## Sample

| Property               | Value                                                                                              |
| ---------------------- | -------------------------------------------------------------------------------------------------- |
| Nested archive         | row 0 of `<GAME_ROOT>/data.rpf`, a nested RPF9 archive                                             |
| Nested archive SHA-256 | `91A236BCB4ECF96840BC0B70E22D1619C0FEDFA11976A336DE311A438214A09E`                                 |
| Nested archive size    | 414544 bytes                                                                                       |
| Rows                   | 156 rows, type ID 11, in the nested archive                                                        |
| Verified rows          | 1 (285), 5 (601), 15 (51045), 72 (77902), 78 (57473), 90 (100958), 141 (596616), 155 (30092) bytes |
| Sample SHA-256 (row 1) | `C0A57DF9C6B93DA6A41AF04BC51C1621A369929E02EFD1BD5BAECA2375ACF0AB`                                 |

The hashes identify derived samples. They contain no asset text.

## Evidence types

| Type              | Meaning                                                                    |
| ----------------- | -------------------------------------------------------------------------- |
| Payload data      | Bytes read from a decoded RPF9 payload, not traced in executable code      |
| Tool output       | A row record, manifest field or extraction result printed by the local CLI |
| Consistency check | A property compared across all verified rows                               |

## Findings

| ID       | Claim                                                                                                                                                      | Evidence                        | Confidence                           | Limits                                                           |
| -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------- | ------------------------------------ | ---------------------------------------------------------------- |
| RBF0-F01 | Payloads start with ASCII `RBF0` (`0x30464252`) at offset 0                                                                                                | Payload data                    | Confirmed                            | 8 rows, one archive                                              |
| RBF0-F02 | The 12 bytes `52 42 46 30 FB FF 01 00 00 00 11 00` are identical in all verified rows                                                                      | Consistency check               | Confirmed                            | One document type                                                |
| RBF0-F03 | `+0x0A` holds the `u16` length 17 and `+0x0C` begins a fixed 17-byte root name; the root name is identical in all verified rows                            | Payload data                    | Confirmed                            | One document type                                                |
| RBF0-F04 | Several field names repeat across files while text values differ, so names encode structure                                                                | Payload data, consistency check | Probable (names are schema)          | Grammar unknown; one document type; names not published          |
| RBF0-F05 | Some strings are length-prefixed; markers `0x6003` and `0xFFFD` occur before fields and `0xFFFF` after some strings; payloads end with eight `0xFF` bytes  | Payload data                    | Confirmed (bytes); Unknown (meaning) | Tag grammar not decoded                                          |
| RBF0-F06 | In this nested archive, the eight verified type ID 11 rows carry RBF0 payloads                                                                             | Payload data                    | Confirmed                            | Eight of 156 rows; other type 11 archives were not surveyed here |
| RBF0-F07 | The eight verified rows decode from mode-1 raw DEFLATE; the row records report mode 1 and no chunk table. The storage observation is recorded in RPF9-F118 | Payload data, tool output       | Confirmed (eight extractions)        | One nested archive; one row failed with a DEFLATE error          |

## Reproduction

Commands ran on 2026-11-25 with the `lforge` CLI built from `leonidaforge/leonida-forge` commit `6b362ad`. `<GAME_ROOT>` is a local installation, `<WORK>` a scratch directory outside it, and `<EXECUTABLE>` the game executable that matches the archive, used only to authenticate its metadata.

```text
lforge archive extract <GAME_ROOT>/data.rpf --row 0 --output <WORK>/data-row0.rpf --executable <EXECUTABLE>
lforge archive ls <WORK>/data-row0.rpf --executable <EXECUTABLE>
lforge archive manifest <WORK>/data-row0.rpf --executable <EXECUTABLE> --format jsonl --output <WORK>/rows.jsonl
lforge archive extract <WORK>/data-row0.rpf --row 1 --output <WORK>/r1.bin --executable <EXECUTABLE>
```

`archive ls` lists the type 11 rows. `archive manifest` records each row's `mode` and `chunks`. `archive extract` reports `raw DEFLATE` for these rows and writes the decoded payload. The first 12 bytes and the root name are visible in a hex dump. Repeat the last command for each verified row in the sample table.

## Limits

- Eight of 156 rows were decoded. The remaining rows were not verified, so only the eight verified rows are known to carry RBF0.
- One row of the same archive failed to decode with a DEFLATE error, so not every type 11 row is readable through the current tool.
- No counterexample to the fixed header prefix was found, but the sample is one archive.
- Payload text, including the root and field names, is game content and was not copied into this repository.

## Next experiments

- Decode all 156 rows and check the header invariant.
- Find RBF0 in a second archive and compare root names.
- Search the executable for the magic and root-name references to establish the loader and the encoding name, without publishing key material.
