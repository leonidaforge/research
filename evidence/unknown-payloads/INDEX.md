# Unknown payload evidence index

This subject records payload signatures that are identified by bytes only. Sample provenance, extraction availability and the observations cited below are listed here.

## Sample and method

| Property | Value                                                                                                                                                |
| -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Archives | 22 authenticated top-level archives, 6,534 unique rows                                                                                               |
| Tool     | `lforge 0.1.0` from `leonidaforge/leonida-forge`, manifest and extract commands                                                                      |
| Method   | Manifest row records for mode, chunk encoding and sizes; first eight stored bytes read at each row's payload offset; extraction for the sampled rows |

`<GAME_ROOT>`, `<EXECUTABLE>` and `<WORK>` are local inputs. No payload text beyond a four-byte signature is reproduced.

## Findings

| ID      | Claim                                                                                                                                                                                                                                                                                    | Evidence                  | Confidence                           | Limits                                              |
| ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------- | ------------------------------------ | --------------------------------------------------- |
| UPL-F01 | The signature census over 6,534 unique rows, reading every untransformed row with at least eight stored bytes, found `9FPR` in 4,351 rows, `KB2n` in 787, `KB2j` in 10, `EDUP` in 3, `SGD5` in 2 and one printable `PTFX` payload. Every other row in that set begins with a zlib stream, except the single encoding-2 row, whose first 16 stored bytes are the prefix recorded in RPF9-F119 | Archive data              | Confirmed (census)                   | Rows behind the payload transform were not censused |
| UPL-F02 | Three rows in three archives carry `EDUP` at offset 0. All are chunked with entry encoding 3, and stored length minus padding equals logical size in each                                                                                                                                | Archive data, tool output | Confirmed                            | Three rows                                          |
| UPL-F03 | The two 28-byte `EDUP` payloads are byte-identical across two archives. The third payload is 236 bytes and does not share their shape                                                                                                                                                    | Archive data              | Confirmed                            | Two distinct payloads                               |
| UPL-F04 | In the 28-byte `EDUP` payloads the `u32` at `+0x04` is 0 and the next `u32` is 16; in the 236-byte payload `+0x04` is 4                                                                                                                                                                  | Archive data              | Confirmed (bytes); Unknown (meaning) | Three payloads                                      |
| UPL-F05 | `KB2j` occurs in 10 rows of `movies.rpf`. In four extracted payloads the `u32` at `+0x04` equals the stored size minus 8, and the `u32` values at `+0x08` and `+0x10` are 15                                                                                                             | Archive data, tool output | Confirmed (4 of 10)                  | One archive; six rows read from stored bytes only   |
| UPL-F06 | `KB2n` occurs in 787 rows of `movies.rpf` and is not observed elsewhere. Its relation to `KB2j` is Unknown                                                                                                                                                                               | Archive data              | Confirmed (occurrence)               | One archive                                         |
| UPL-F07 | `SGD5` occurs in two rows of `shaders.rpf` with stored sizes 3,086,896 and 271,048,480 bytes. The payloads were not analysed                                                                                                                                                             | Archive data              | Confirmed (occurrence)               | Two rows                                            |
| UPL-F08 | Type ID 14 has one row, `data.rpf` row 262, extracting to 1,280 bytes with no printable magic. The `u16` at `+0x00` and `+0x0E` is `0x0330` in that payload                                                                                                                              | Archive data, tool output | Confirmed (bytes)                    | One row; no field meaning established               |
| UPL-F09 | Type ID 255 carries at least four unrelated signatures in this sample (`EDUP`, `KB2j`, `KB2n` and `SGD5`), so a type ID does not identify a payload format                                                                                                                               | Archive data              | Confirmed (sample)                   | 22 archives                                         |

## Reproduction

```text
lforge archive manifest <ARCHIVE> --executable <EXECUTABLE> --format jsonl --output <WORK>/rows.jsonl
lforge archive extract <ARCHIVE> --row <ROW> --executable <EXECUTABLE> --output <WORK>/row.bin
```

The census reads the first eight bytes at each row's `payload_offset` using the stored size from the manifest. Rows with `payload_transform` set were skipped.

## Open questions

- Whether `EDUP` is a record inside a larger structure or a standalone payload.
- Whether `KB2j` and `KB2n` are one format with two variants.
- What `SGD5` stores, beyond its occurrence in `shaders.rpf`.
- Whether type ID 14 payloads share a structure with any documented format.
