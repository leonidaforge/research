# SGD5

`SGD5` (`53 47 44 35`) at offset 0 marks two payloads in `shaders.rpf`, rows 1 and 2. Both rows are type ID 255 and stored without a chunk table.

The archive name is provenance, not evidence of purpose. Nothing about the payload purpose, field meanings, data encoding, rendering stage or graphics API is established.

## Status

| Part                                       | Status                              |
| ------------------------------------------ | ----------------------------------- |
| Magic and occurrence                       | Confirmed (2 rows, one archive)     |
| Block count and first-block length        | Confirmed (2 samples)               |
| Block and entry layout                     | Confirmed (36 table blocks)         |
| Data-region record prefix                  | Confirmed (observation, 2 samples)  |
| Field meanings, purpose, data encoding     | Unknown                             |
| Additional samples                         | None found in the bounded search    |

## Samples

| Archive        | Row | Type ID | Stored bytes | Decoded bytes | SHA-256                                                            |
| -------------- | --: | ------: | -----------: | ------------: | ------------------------------------------------------------------ |
| `shaders.rpf`  |   1 |     255 |    3,086,896 |     3,086,891 | `D86AF8CD24312A51C1FC7E7888A43B04338C37CEF1568B6473A88AD469A03925` |
| `shaders.rpf`  |   2 |     255 |  271,048,480 |   271,048,467 | `331DB1162E6440D1629CF87B4802505FA41DA534034AF1147BCE5A9B402C4E16` |

The stored size exceeds the decoded size by 5 and 13 bytes. The difference is not explained. `shaders.rpf` has one other row; it decodes to 275,540,780 bytes, does not begin with `SGD5` and is outside this subject.

## Header and first-block fields (SGD5-F03)

| Offset  | Size | Observation                                                            | Status                              |
| ------- | ---: | ---------------------------------------------------------------------- | ----------------------------------- |
| `+0x00` |    4 | `53 47 44 35`                                                          | Confirmed                           |
| `+0x04` |    4 | `u32`: `0x3EFB3ED6`, `0xA08B72B3`                                      | Unknown                             |
| `+0x08` |    4 | `u32`: `0x095DF2DC`, `0x60555DC2`                                      | Unknown                             |
| `+0x0C` |    4 | `u32`: 3 and 33; equal to the number of table blocks                   | Confirmed (2 samples)               |
| `+0x10` |    4 | `u32`: 248 and 2112; equal to the length of the first table block      | Confirmed (2 samples)               |
| `+0x14` |   20 | Descriptor of the first table block                                    | Unknown contents                    |
| `+0x28` |    4 | Zero in both samples                                                   | Confirmed (2 samples)               |
| `+0x2C` |    — | Start of the first table payload                                       | See below         |

No checked header field equals the decoded size, the stored size or the data-region offset. The `u32` at `+0x0C` is not an entry count: the first sample declares 3 table blocks holding 486 entries, the second declares 33 blocks holding 2,423 entries.

## Table blocks (SGD5-F04)

The `u32` at `+0x10` is the length of the first table block. Each block has this shape, and the next block's length field follows the payload:

```text
u32  length
u8   descriptor[20]
u32  zero
u8   payload[length - 24]
```

For a table block, the payload is `n` entries of 8 bytes:

```text
u32  value
u16  kind
u16  index
```

The block length equals `24 + 8n` in all 36 table blocks. The `index` runs from 0 to `n - 1` in every block.

| Sample | Declared blocks | Entry counts per block |
| ------ | --------------: | ---------------------- |
| Row 1  |               3 | 28, 197, 261 |
| Row 2  |              33 | 261, 2, 104, 28, 197, 126, 185, 42, 71, 74, 72, 11, 17, 138, 183, 17, 2, 17, 117, 4, 37, 126, 97, 27, 6, 26, 12, 13, 19, 136, 153, 80, 23 |

### Entry census (SGD5-F05)

Fifteen distinct `u16` kind values occur. The most frequent are `0x0102` and `0x0405`. No kind was assigned a meaning.

The `u32` value is not a file offset or a size. The largest value in the sample is `0xFF18999D`, which exceeds both payload sizes. 299 of the 486 values in row 1 and 488 of the 2,423 values in row 2 are distinct.

Three row-1 table payloads appear byte-identical in row 2: the 28-entry block, the 197-entry block and the 261-entry block. Their 20-byte descriptors are also identical. The table order differs. This shows shared table content, not what the content represents.

## Block after the tables (SGD5-F06)

One more block header of the same shape follows the last table block:

| Sample | Offset  | Length | Length equals remaining file bytes | Trailing word |
| ------ | ------- | -----: | ---------------------------------- | ------------- |
| Row 1  | `0xF94` |  7,401 | No                                 | Zero          |
| Row 2  | `0x4F64`| 11,985 | No                                 | Zero          |

The length at this position does not describe the remaining file. It equals `24 × (number of records whose headers begin at a 24-byte stride) + 9` in both samples, but that relation is an observation from two samples and the field meaning is Unknown.

## Data region (SGD5-F07)

The data region begins after that block header, at `0x0FB0` and `0x4F80`.

The first 308 and 499 records, respectively, begin at a 24-byte stride:

```text
u32  value
u32  value copy
u16  kind
u16  index
u8   payload[12]
```

The first two words are identical in every counted record. The `u16` at `+0x0A` is not sequential, unlike the table entry index. Most 12-byte payloads are zero; some carry values.

At the next record the 24-byte stride no longer holds. A NUL-terminated printable ASCII run appears within the following bytes. The run is not reproduced. The rest of the data region contains high-entropy bytes and further printable runs. No internal section boundary was established, and no record meaning was assigned.

Neither payload contains a second `SGD5` sequence or an `RPF9`, `RBF0`, `PSIN`, `EDUP`, `KB2j` or `KB2n` signature (SGD5-F08). The two-byte sequences `0x78 0x9C` and `0x78 0xDA` occur; they are not evidence of a compressed stream without a valid stream parse.

## Identification

Identification MUST use the payload bytes. Type ID 255 also carries unrelated payloads (UPL-F09), so the type ID is not an identifier.

## Limits

- Two payloads from one archive. No second archive or row carries `SGD5` in the bounded sample.
- The nested-archive sample was limited to 44 archives selected by an earlier inventory. Rows behind the payload transform were not read, and chunked rows were classified by stored bytes, not decoded bytes.
- No executable path was traced. No earlier RAGE format is claimed as a match.
- The archive name and the field values above do not establish a shader, material or graphics API representation.

Evidence: [evidence/sgd5/INDEX.md](../../../evidence/sgd5/INDEX.md).
