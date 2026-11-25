# Inventory evidence index

Read-only sample of nested RPF9 archives reached from the authenticated top-level tables of contents. Archives, extracted payloads and scratch manifests stay outside this repository. The sample covers one build and one local archive set; the counts are observations, not format limits.

All findings below are **Private-evidence supported**: the sampler and its selection rule are public, but the counts cannot be re-derived without the same restricted inputs. Metadata authentication and decoding used the native path of build [scarlett-e95020b2](../../builds/gta-vi/scarlett-e95020b2/README.md) through the Leonida Forge CLI at commit `fc841ea`. RPF9 finding IDs refer to the [RPF9 evidence index](../rpf9/INDEX.md).

## Evidence types

| Type                   | Meaning                                                                                                                                                             |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Authenticated manifest | Read-only parse of an RPF9 table of contents whose metadata signature the CLI accepted. Supplies row count, type ID, sizes, layout, chunk encoding and readability  |
| Native extraction      | `archive extract` exited 0 and the output size equals the row's logical size                                                                                        |
| Payload prefix         | First 8 bytes of an extracted payload, reduced to a signature class. Exact prefixes remain in scratch                                                              |
| Hash fingerprint       | SHA-256 of an extracted nested archive. Only uniqueness and duplicate counts are published                                                                          |
| Sample audit           | Deterministic recomputation of the selection from the stored manifests                                                                                              |

## Sample frame

- Input: 22 unique top-level archives from 23 manifest files. Each manifest header reports a verified metadata signature; the sampler does not re-check it, so authentication here is inherited from the manifest record. One duplicate manifest path was ignored. 17 archives contain type-0 rows; 5 contain none.
- Rule: per archive, order readable type-0 rows with logical size at most 8 MiB by `(logical size, row)` and take indices `0`, `n // 2` and `n - 1`; remove duplicate rows. The tool is [tools/inventory](../../tools/inventory/README.md).
- Result: 44 nested archives. 12 top-level archives contributed 3 samples, 3 contributed 2 and 2 contributed 1.
- Caps: depth 2, 60 nested archives, 512 MiB extracted, 8 MiB per archive, 2 payloads per type at or below 1 MiB. Used: 44 archives, 101,949,270 bytes in total, 8,384,080 bytes for the largest archive and 39 payload samples.
- Depth 2: no candidate. None of the 44 depth-1 manifests contains a type-0 row at any size (INV-F08).
- Run date: 2026-11-25. All inputs were opened read-only.

## Findings

| ID       | Claim                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | Evidence                                | Confidence                                        | Limits                                                                                                                                                                                                                       |
| -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------- | ------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| INV-F01  | The deterministic rule selected 44 readable type-0 rows from 17 of 22 top-level archives. All 44 native extractions exited 0 with output size equal to the logical size. The nested archives total 100,904,448 bytes; the smallest is 720 bytes and the largest 8,384,080 bytes. With 39 payloads of 1,044,822 bytes, the run extracted 101,949,270 bytes, below the 512 MiB cap, and used 44 of the 60-archive cap.                                                                                                     | Sample audit, native extraction         | Confirmed (sample)                                | Readable type-0 rows at or below 8 MiB only. Five top-level archives have no type-0 row. The total number of nested archives is unknown.                                                                                    |
| INV-F02  | All 44 extracted type-0 rows produced files that begin with the RPF9 magic and whose metadata authenticated under the same build. Their 44 SHA-256 fingerprints are distinct; no duplicate nested archive content was found.                                                                                                                                                                                                                                                                                          | Authenticated manifest, hash fingerprint, native extraction | Confirmed (sample)                                | Metadata only; payload bytes remain unauthenticated (RPF9-F102). The sample is bounded by INV-F01. Magic alone is not treated as identification.                                                                            |
| INV-F03  | The 44 nested manifests hold 3,553 rows and 25 distinct type IDs. 3,535 rows are readable and 18 are unreadable. Every row uses read source `main`. Compression mode 0 covers 3,552 rows and mode 1 covers one row. Layout R covers 2,326 rows and layout F covers 1,227. The type histogram is below.                                                                                                                                                                                                                 | Authenticated manifest                  | Confirmed (sample)                                | One build and sample. Type IDs are row labels; this index assigns no payload format to them. Names remain unresolved hashes.                                                                                               |
| INV-F04  | Chunk encoding and location layout correlate exactly in the sample. All 2,326 layout-R rows use chunk encoding 2. All 1,203 layout-F rows with a chunk table use encoding 3. The 24 layout-F rows without a chunk table are stored. No row uses encoding 4. Readable counts are 2,325 of 2,326 encoding-2 rows, 1,187 of 1,203 encoding-3 rows and 23 of 24 unchunked rows.                                                                         | Authenticated manifest                  | Confirmed (sample correlation)                    | A sample correlation, not a format rule. No encoding-4 row was available to test.                                                                                                                                           |
| INV-F05  | All 44 archive extractions and all 39 payload extractions exited 0 with exact logical size. No extraction failed. The payload sample contains 34 encoding-2 rows and 5 encoding-3 rows. The 18 unreadable rows were not extraction attempts: 16 type-11 rows (15 encoding 3, one unchunked mode-1 row), one type-14 encoding-3 row and one type-89 encoding-2 row. All 18 are `unsupported_transform`. Types 96 and 109 are readable but exceed the 1 MiB payload cap; no sample exists for types 14, 89, 96 or 109. | Native extraction, authenticated manifest | Confirmed (sample)                                | At most two payloads per type. Most readable rows were not extracted. The payload transform remains unsupported (RPF9-F113, RPF9-F116, RPF9-F117). The single mode-1 row in this sample is transformed, so non-chunked raw DEFLATE mode 1 is not present in the top-level archives; RPF9-F118 records it in a nested archive. |
| INV-F06  | The 39 payload samples fall into two prefix classes: 34 zero-prefix and 5 non-zero. The zero-prefix class spans 18 type IDs and every encoding-2 sample. The five non-zero samples are all encoding 3: type 11 (2 samples with different prefixes), type 66 (1) and type 255 (2 samples sharing one prefix). No sample has an RPF9-magic or zlib-container-header prefix. Exact first-8-byte values stay in scratch.                                     | Payload prefix                          | Confirmed (classes and counts); Unknown (format identity) | First 8 bytes only. Payloads above 1 MiB and unreadable transform rows were not sampled. No payload bytes or text are published.                                                                                            |
| INV-F07  | Type ID does not determine the sampled prefix class. Eighteen type IDs share the zero-prefix class, and type 11 produced two different non-zero prefixes. Conversely, every sampled type-0 row extracted as an RPF9 archive with authenticated metadata. The sample therefore separates the row type ID from a payload format identity; no type is mapped to a format here.                                                                              | Payload prefix, authenticated manifest  | Confirmed (sample independence); Unknown (format identity) | Only 21 of 25 type IDs were sampled. An 8-byte prefix is weak evidence of format. The type-0 observation is an extraction result, not a type-to-format rule.                                                                  |
| INV-F08  | No depth-1 archive contains a type-0 row, so the depth-2 selection has 0 candidates and no depth-2 archive was extracted. The recursive sample stops at depth 1.                                                                                                                                                                                                                                                                                                                                                      | Authenticated manifest, sample audit    | Confirmed (sample); Unknown (general)             | Covers the 44 sampled depth-1 archives. Larger or unselected nested archives were not examined.                                                                                                                              |

## Type histogram

Counts are rows in the 44 nested manifests. "Encoding" is the chunk-table encoding; `none` means no chunk table.

| Type ID | Rows | Readable | Unreadable | Encoding            |
| ------: | ---: | -------: | ---------: | ------------------- |
|       2 |  366 |      366 |          0 | 2                   |
|       3 |   45 |       45 |          0 | 2                   |
|       4 |   67 |       67 |          0 | 2                   |
|       5 |    5 |        5 |          0 | 2                   |
|      11 | 1191 |     1175 |         16 | 3: 1190, none: 1    |
|      14 |    1 |        0 |          1 | 3                   |
|      15 |  401 |      401 |          0 | 2                   |
|      16 |   31 |       31 |          0 | 2                   |
|      66 |    1 |        1 |          0 | 3                   |
|      67 |   50 |       50 |          0 | 2                   |
|      70 |    1 |        1 |          0 | 2                   |
|      72 |  147 |      147 |          0 | 2                   |
|      73 |    1 |        1 |          0 | 2                   |
|      74 |    2 |        2 |          0 | 2                   |
|      78 |  175 |      175 |          0 | 2                   |
|      79 |  162 |      162 |          0 | 2                   |
|      87 |  650 |      650 |          0 | 2                   |
|      88 |   36 |       36 |          0 | 2                   |
|      89 |    1 |        0 |          1 | 2                   |
|      96 |    1 |        1 |          0 | 3                   |
|     103 |   41 |       41 |          0 | 2                   |
|     109 |    1 |        1 |          0 | 2                   |
|     111 |    6 |        6 |          0 | 2                   |
|     115 |  138 |      138 |          0 | 2                   |
|     255 |   33 |       33 |          0 | 3: 10, none: 23     |

The top-level set reported in RPF9-F103 is `{0, 11, 14, 255}`. The nested sample adds 22 type IDs: `{2, 3, 4, 5, 15, 16, 66, 67, 70, 72, 73, 74, 78, 79, 87, 88, 89, 96, 103, 109, 111, 115}`. Type 0 appears only in the top-level rows used as archive containers; no sampled nested archive contains one.

## Extraction outcomes

| Measure                     | Result        |
| --------------------------- | ------------- |
| Nested archives extracted   | 44 of 44      |
| Nested bytes                | 100,904,448   |
| Payload samples extracted   | 39 of 39      |
| Payload bytes               | 1,044,822     |
| Extraction failures         | 0             |
| Encoding-2 payload samples  | 34 of 34      |
| Encoding-3 payload samples  | 5 of 5        |
| Encoding-4 rows             | 0             |
| Duplicate nested archives   | 0 of 44       |

Unreadable rows, which were excluded from payload sampling:

| Type ID | Rows | Encoding | State                 |
| ------: | ---: | -------- | --------------------- |
|      11 |   15 | 3        | `unsupported_transform` |
|      11 |    1 | none     | `unsupported_transform` |
|      14 |    1 | 3        | `unsupported_transform` |
|      89 |    1 | 2        | `unsupported_transform` |

## Payload prefix classes

| Class                 | Samples | Type IDs                                                                  | Encoding | Distinct 8-byte prefixes |
| --------------------- | ------: | ------------------------------------------------------------------------- | -------- | -----------------------: |
| zero-prefix           |      34 | 2, 3, 4, 5, 15, 16, 67, 70, 72, 73, 74, 78, 79, 87, 88, 103, 111, 115   | 2        |                        1 |
| non-zero prefix       |       5 | 11, 66, 255                                                               | 3        |                        4 |
| rpf9-magic            |       0 | none                                                                      | none     |                        0 |
| zlib-container-header |       0 | none                                                                      | none     |                        0 |

## Not concluded

- No payload format is identified. A type ID, a magic or an 8-byte prefix alone does not establish a format.
- No extension or original filename is assigned to any nested type ID.
- The 8-byte prefix sample is too short to distinguish resource headers, container headers or compressed streams.
- Encoding 4 is absent from this sample. Non-chunked raw DEFLATE mode 1 is absent from the 22 top-level archives; it is recorded for a nested archive in RPF9-F118.
- Depth-2 absence is a property of this sample, not evidence that nested archives never contain archives.
