# EDUP evidence index

EDUP observations from the Scarlett build [e95020b2](../../builds/gta-vi/scarlett-e95020b2/README.md). No executable code path was traced. Every finding is **Private-evidence supported**: the selection and the tools are public, but the payloads and store keys remain outside this repository. The original occurrence and framing findings are UPL-F02 to UPL-F11 in [evidence/unknown-payloads/INDEX.md](../unknown-payloads/INDEX.md); this index records the key relationship and the blob tests.

## Sample

| Property | Value |
| -------- | ----- |
| EDUP rows | 5 rows in 5 archives, type ID 255 |
| Distinct payloads | 4 by size and content: 28, 236, 1,548 and 965,964 bytes |
| Layout | `size = 8 + 16 × count + 4 + length` in 4 of 4 |
| Store population for the key test | 46 local `.ttpf` RDS5/ETPF stores |
| Store keys | 352,461 keys, 352,417 distinct |

The two 28-byte rows are byte-identical. The local store set is 46 files, not the 57-store sample used by the RDS5 document.

## Evidence types

| Type | Meaning |
| ---- | ------- |
| `BINARY` | Bytes read from decoded EDUP payloads and from store headers and key tables |
| `CROSS_SAMPLE` | A property compared across distinct payloads or stores |
| `SYNTHETIC` | Authored fixtures that test the repository parser and membership test |

## Findings

| ID | Claim | Evidence | Confidence | Limits |
| -- | ----- | -------- | ---------- | ------ |
| EDUP-F01 | The five rows and four distinct payloads and the count/length framing are as recorded in UPL-F02 to UPL-F11. The framing was rechecked by the committed parser: `layout_ok` is true in 4 of 4 | `BINARY` | Confirmed | See UPL-F11 for the endianness argument; no executable trace |
| EDUP-F02 | An entry is two 8-byte little-endian fields, not one 128-bit value. The first field is distinct within each nonempty table: 4, 33 and 17,431 distinct values. The second field repeats: 4, 21 and 6,845 distinct values. The two key sets are disjoint in all three tables: 0 first-field values occur as second-field values and 0 second-field values occur as first-field values | `BINARY`, `CROSS_SAMPLE` | Confirmed (sample) | Three nonempty tables; the 28-byte payloads have no entries |
| EDUP-F03 | In the 17,431-entry `textures.rpf` table every first-field key is absent from every one of the 46 store key tables, and every second-field key is present: 0 of 17,431 and 17,431 of 17,431. The second field is the stored texture key; the mapping direction is alias to stored key. The table has 6,845 distinct stored keys; 1,176 stored keys have more than one alias and the largest alias group is 723 | `BINARY`, `CROSS_SAMPLE` | Confirmed (one table) | 46 local stores; this is the only table that resolves completely |
| EDUP-F04 | The direction does not resolve for the other two nonempty tables against the 46 local stores. The 33-entry table has 33 distinct first and 21 distinct second keys; the 4-entry table has 4 and 4. In both, 0 first-field and 0 second-field keys occur in the store key set. The hypothesis stays open for these tables | `BINARY` | Unknown (membership test negative) | The local set is smaller than the 57-store sample; a missing store is the first explanation to test |
| EDUP-F05 | The trailing blob is not decoded. Blob lengths are 16, 160, 1,008 and 687,056 bytes, all multiples of 16. Widths 1 to 64 do not produce a record table with a count equal to the entry count or the distinct stored-key count, and no fixed-offset 4-byte field is strictly increasing. No 8-byte word matches a store key. Complete zlib, raw deflate, gzip, bzip2, xz and LZMA-alone decodes fail; raw deflate and LZMA produce no complete stream with zero unused input. No zstd or LZ4 frame signature occurs. Entropy is 3.9, 6.8, 7.8 and 8.0 bits/byte | `BINARY`, `CROSS_SAMPLE` | Confirmed (negative tests); Unknown (content) | Negative tests do not prove encryption; the count-0 blob is not named |
| EDUP-F06 | `tools/edup/edup_inspect.py` reproduces the layout, field counts, disjointness and optional store membership. It never prints key values or payload bytes. Synthetic tests cover a valid table, an empty table, a minimal ETPF store, wrong magic, an entry-table overrun, trailing bytes after the blob and the entry cap | `SYNTHETIC` | Confirmed (tool behavior) | Synthetic data does not establish native semantics |

## Counterexamples

| Reading | Counterexample |
| ------- | -------------- |
| Entry as one 128-bit value | The second 8 bytes repeat and the first do not; the two sets are disjoint |
| First field as the stored texture key | 0 of 17,431 first-field keys occur in the 46 store key tables |
| Second field as an offset into the blob | Every second-field value is larger than every blob length by many orders of magnitude |
| Blob as a compressed stream | No complete stream with zero unused input across the tested decoders |
| Universal direction | The 33-entry and 4-entry tables do not resolve against the local store set |

## Reproduction

```text
python tools/edup/edup_inspect.py <EDUP> --store-dir <TTDB_DIRECTORY>
python -m unittest discover -s tools/edup
```

`<TTDB_DIRECTORY>` is a local directory of `.ttpf` stores. The tool reads each store header and key table only; it does not inflate blocks or write to the inputs.

## Limits

- Five rows and four distinct payloads. The two hidden rows were found through the shared name key; the full type-255 set was not decoded.
- The key test covers 46 local stores and does not establish why two tables do not resolve.
- The entry and blob contents are not otherwise interpreted.
- No executable path was traced and no earlier RAGE format is claimed as a match.
- Key values are not published. Only counts and membership results are recorded.
