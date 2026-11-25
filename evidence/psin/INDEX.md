# PSIN evidence index

Payload observations from the Scarlett build [e95020b2](../../builds/gta-vi/scarlett-e95020b2/README.md). No executable code path was traced. Every finding is **Private-evidence supported**.

## Sample

| Property          | Value                                                                                                                                                                        |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Rows              | 18 type ID 11 rows                                                                                                                                                           |
| Archives and rows | `<GAME_ROOT>/anim.rpf` 235, 238, 241, 244; `data.rpf` 42, 48, 49, 52; `levels.rpf` 2053, 2055, 2056, 2057; `packs.rpf` 61, 67, 70, 71; `pack/story000/story000.rpf` 444, 457 |
| Selection         | first successfully extracted type 11 rows per archive, up to four per archive; readable rows that extraction refused were skipped                                                                                                              |
| Sizes             | 248 to 169316 bytes                                                                                                                                                          |
| Signature         | `50 53 49 4E` at offset 0 in all 18                                                                                                                                          |

The sample is a convenience sample. It does not establish the type's population or size range.

## Evidence types

| Type              | Meaning                                                               |
| ----------------- | --------------------------------------------------------------------- |
| Payload data      | Bytes read from a decoded RPF9 payload, not traced in executable code |
| Consistency check | A property compared across the 18 rows                                |

## Findings

| ID       | Claim                                                                                                | Evidence          | Confidence                                 | Limits                                                     |
| -------- | ---------------------------------------------------------------------------------------------------- | ----------------- | ------------------------------------------ | ---------------------------------------------------------- |
| PSIN-F01 | Payloads start with ASCII `PSIN` (`0x4E495350`) at offset 0                                          | Payload data      | Confirmed                                  | 18 rows, 5 archives                                        |
| PSIN-F02 | Bytes `+0x04` are `00 00` in 17 rows and `00 02` in one, which is `u16` 0 and `0x0200` little-endian | Consistency check | Confirmed (observation); Unknown (meaning) | Meaning not established                                    |
| PSIN-F03 | In these 18 samples, no `u16` or `u32` in the first 32 bytes equals the payload size                 | Consistency check | Confirmed (bounded observation)            | Only the first 32 bytes and the sample were checked        |
| PSIN-F04 | Many payloads contain runs of `0xAA` and `0x70`, which fits padding or uninitialised bytes           | Payload data      | Speculative                                | Could be meaningful data                                   |
| PSIN-F05 | The 18 sampled type 11 rows all carry PSIN | Payload data | Confirmed | Sample only; does not establish the type's full population |

## Reproduction

The following commands ran on 2026-11-25 with the `lforge` CLI built from `leonidaforge/leonida-forge` commit `fce79a34ab622b1eeb0370c9dceee4700f0b897f`. `<GAME_ROOT>` is a local installation, `<WORK>` a scratch directory outside it, and `<EXECUTABLE>` the game executable that matches the archive, used only to authenticate its metadata. Repeat for each archive in the sample table:

```text
lforge archive manifest <ARCHIVE> --executable <EXECUTABLE> --format jsonl --output <WORK>/rows.jsonl
lforge archive extract <ARCHIVE> --row <ROW> --output <WORK>/row.bin --executable <EXECUTABLE>
```

`archive manifest` lists each row's type ID and stored form. `archive extract` writes the decoded payload. A hex dump of the first bytes shows the `PSIN` signature.

## Limits

- Some rows listed as decoded fail extraction with a DEFLATE error. Those rows were skipped; the exact count is not recorded here.
- Fields were not assigned names. `+0x04` is the only field with a recorded observation; other offsets are unexamined.

## Next experiments

- Count the population of type 11 rows and their signatures across the top-level archives.
- Cluster the samples on the varying header words to test for subtypes.
- Search the executable for the magic constant, without publishing key material or secret state.
