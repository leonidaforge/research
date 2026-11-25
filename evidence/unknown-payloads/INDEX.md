# Unknown payload evidence index

This subject records payload signatures that are identified by bytes only. Sample provenance, extraction availability and the observations cited below are listed here.

## Sample and method

| Property | Value                                                                                                                                                |
| -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Archives | 22 authenticated top-level archives, 6,534 unique rows                                                                                               |
| Tool     | `lforge 0.1.0` from `leonidaforge/leonida-forge`, app commit `92af6e2`, manifest and extract commands                                                 |
| Method   | Manifest row records for mode, chunk encoding and sizes; first eight stored bytes read at each row's payload offset; extraction for the sampled rows |
| Decoded scan | All 290 unique readable type-255 rows with logical size at or below 64 KiB, extracted with the same CLI; first four logical bytes read |

`<GAME_ROOT>`, `<EXECUTABLE>` and `<WORK>` are local inputs. No payload text beyond a four-byte signature is reproduced.

The census covers top-level stored bytes only. Depth-1 nested payloads add `GFX*` under type 66, recorded in [GFX*](../gfx/INDEX.md), and `ADAT` under type 255, recorded in [ADAT](../gfx-adat/INDEX.md).

## Findings

| ID      | Claim                                                                                                                                                                                                                                                                                    | Evidence                  | Confidence                           | Limits                                              |
| ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------- | ------------------------------------ | --------------------------------------------------- |
| UPL-F01 | The signature census over the 6,534 unique rows of the current manifest, reading every untransformed row with at least eight stored bytes, found `9FPR` in 4,351 rows, `KB2n` in 505, `KB2j` in 10, `EDUP` in 3, `SGD5` in 2 and one printable `PTFX` payload. An earlier census over a different `movies.rpf` population reported 787 `KB2n` rows (KB2-F01, KB2-F12). Every other row in that set begins with a zlib stream, except the single encoding-2 row, whose first 16 stored bytes are the prefix recorded in RPF9-F119 | Archive data              | Confirmed (census)                   | Stored bytes only; decoded content can hide a signature inside a zlib chunk (UPL-F10). The earlier 787 count is not reproducible from the current manifest |
| UPL-F02 | The stored-byte census sees `EDUP` at offset 0 in three rows in three archives. All are chunked with entry encoding 3, and stored length minus padding equals logical size in each                                                                                                        | Archive data, tool output | Confirmed (stored bytes)             | Three stored rows; UPL-F10 adds two decoded rows    |
| UPL-F03 | The two 28-byte `EDUP` payloads are byte-identical across two archives. The other distinct payloads are 236, 1,548 and 965,964 bytes                                                                                                                                                      | Archive data              | Confirmed                            | Four distinct payloads                              |
| UPL-F04 | In the `EDUP` payloads the little-endian `u32` at `+0x04` is 0 (two 28-byte rows), 4 (236-byte), 33 (1,548-byte) and 17,431 (965,964-byte)                                                                                                                                               | Archive data              | Confirmed (bytes); Unknown (meaning) | Four distinct payloads; UPL-F11 gives the framing   |
| UPL-F05 | `KB2j` occurs in 10 rows of `movies.rpf`. In four extracted payloads the `u32` at `+0x04` equals the extracted (logical) size minus 8, and the `u32` values at `+0x08` and `+0x10` are 15. The field is not the stored size minus 8 when row padding exists                                                                                                             | Archive data, tool output | Confirmed (4 of 10); corrected by KB2-F02 | One archive; six rows read from stored bytes only   |
| UPL-F06 | `KB2n` occurs in `movies.rpf` and is not observed elsewhere. The current 515-row manifest reads 505 rows; an earlier census reported 787 rows over a different `movies.rpf` population whose manifest is not preserved (KB2-F01, KB2-F12). `KB2j` and `KB2n` share one container layout                                                                                                             | Archive data              | Confirmed (occurrence); Probable (one family) | One archive; the two counts cover different manifest populations |
| UPL-F07 | `SGD5` occurs in two rows of `shaders.rpf` with stored sizes 3,086,896 and 271,048,480 bytes. Both payloads were extracted, fingerprinted and structurally sampled; see [SGD5](../sgd5/INDEX.md)                                                                                                                                                             | Archive data              | Confirmed (occurrence)               | Two rows                                            |
| UPL-F08 | Type ID 14 has one row, `data.rpf` row 262, extracting to 1,280 bytes with no printable magic. The `u16` at `+0x00` and `+0x0E` is `0x0330` in that payload                                                                                                                              | Archive data, tool output | Confirmed (bytes)                    | One row; no field meaning established               |
| UPL-F09 | Type ID 255 carries at least four unrelated signatures in this sample (`EDUP`, `KB2j`, `KB2n` and `SGD5`), so a type ID does not identify a payload format                                                                                                                               | Archive data              | Confirmed (sample)                   | 22 archives; the decoded scan also found XML/text, `SPS1`, `PTFX` and other prefixes |
| UPL-F10 | Decoding found `EDUP` in five rows across five archives. The two rows missed by the stored-byte census are `core_restofworld.rpf` row 15 (1,548 bytes) and `textures.rpf` row 20 (965,964 bytes); both store zlib chunks. All five rows share `name_hash` `0x21E7013DF19FB4FA` and `name_key` `0x3BE189DE`; no other row in the 22-archive inventory has that key | Archive data, tool output | Confirmed                            | The two hidden rows were found through the shared key; the full type-255 set was not decoded |
| UPL-F11 | The four distinct `EDUP` payloads (28, 236, 1,548 and 965,964 bytes) fit `size = 8 + 16 × count + 4 + length`: a little-endian `u32` count at `+0x04`, `count` 16-byte entries, a little-endian `u32` blob length at `+0x08 + 16 × count`, and that many trailing bytes. Testing entry widths 1–64 leaves only 16. Each payload has exactly one 4-byte-aligned `u32` equal to the bytes after it, at the predicted offset. Big-endian counts and lengths are implausible | Archive data, tool output | Confirmed (bytes); Probable (endianness, field meaning) | Four distinct payloads; no executable trace        |
| UPL-F12 | The 16-byte entries are not sorted by 128-bit value. Every entry is distinct within its payload. In the 4-, 33- and 17,431-entry payloads the first 8 bytes are all distinct and the last 8 bytes take 4, 21 and 6,845 values. In the 17,431-entry payload every byte position takes all 256 values. No entry contains the shared name hash or key. The trailing blob has no zlib, gzip, bzip2 or LZMA header, contains no entry, and the 687,056-byte blob has entropy about 8.0 bits/byte | Archive data, tool output | Confirmed (bytes)                    | Entry and blob meanings Unknown                     |
| UPL-F13 | The 16-byte blob of the count-0 payload is constant across the two byte-identical rows. It does not match the first or last 16 bytes of MD5, SHA-1, SHA-256, SHA-512 or BLAKE2 digests of the five payloads; the byte at `+0x06` does not take a standard UUID version nibble. No digest identity is established | Archive data, tool output | Confirmed (negative tests); Unknown (identity) | Limited hash set; not proof that no digest exists   |
| UPL-F14 | Extracting all 290 unique readable type-255 rows at or below 64 KiB found four `EDUP` rows and no fifth. The fifth known `EDUP` payload is 965,964 bytes, above the cap. The same scan saw XML/text, `SPS1`, `PTFX`, `alph`, `<CTu`, `Anim`, `PAMH`, `<Spr`, `KB2j` and `KB2n` prefixes, so type 255 is not a format identity | Archive data, tool output | Confirmed (sample)                   | 290 of 1,735 type-255 rows; rows above 64 KiB were not decoded |

## Reproduction

```text
lforge archive manifest <ARCHIVE> --executable <EXECUTABLE> --format jsonl --output <WORK>/rows.jsonl
lforge archive extract <ARCHIVE> --row <ROW> --executable <EXECUTABLE> --output <WORK>/row.bin
```

The census reads the first eight bytes at each row's `payload_offset` using the stored size from the manifest. Rows with `payload_transform` set were skipped.

The decoded scan extracts each selected row, reads the first four logical bytes, and discards non-`EDUP` extractions. It covers 290 unique readable type-255 rows at or below 64 KiB; the 965,964-byte `EDUP` row is above the cap and was found through the shared name key instead.

## Corrections

UPL-F02 to UPL-F04 originally described only the three stored-byte hits. Decoding the two other rows with the same name key found two more `EDUP` payloads, and UPL-F11 supersedes the earlier ad hoc header description. UPL-F01 and UPL-F02 remain valid as stored-byte observations; UPL-F10 to UPL-F14 record the decoded occurrence and framing.

## Open questions

- What the 16-byte entries and the trailing blob represent, and whether `EDUP` is metadata or content.
- What the fourth byte of `KB2j` and `KB2n` selects; the layouts are shared
  ([KB2 evidence](../kb2j/INDEX.md)).
- What `SGD5` stores, beyond its occurrence in `shaders.rpf`.
- Whether type ID 14 payloads share a structure with any documented format.
