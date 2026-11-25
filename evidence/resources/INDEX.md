# Resource evidence index

Payload observations from the Scarlett build [e95020b2](../../builds/gta-vi/scarlett-e95020b2/README.md). No executable code path was traced for this subject. Every finding is **Private-evidence supported**: it is checkable against a local installation but not from this repository alone.

This index consolidates findings from `research/shared/resource-serialization` revision `666facc` into `research/resources-v2`. The source branch's merge history was not integrated. Representative samples were rechecked on 2026-11-25 with the application CLI at commit `92af6e2` and with the published parser. The full survey counts are reported from the source branch and were not re-counted.

## Primary sample

| Property                | Value                                                                                     |
| ----------------------- | ----------------------------------------------------------------------------------------- |
| Nested archive          | row 0 of a nested archive extracted from `textures.rpf` row 1, `<GAME_ROOT>/textures.rpf` |
| Nested archive SHA-256  | `FBE052831C9E2734CCF03C3D30083528988D2766F36E9A7E29C7FA7C293056E8`                        |
| Nested archive size     | 4,720 bytes                                                                               |
| Row                     | 0, type ID 5                                                                              |
| Entry                   | payload offset `0x1000`, stored size 576, logical size 51,040                             |
| Chunks                  | encoding 2, count 2                                                                       |
| System stream           | stored 395 bytes at offset 4,112; reconstructed 1,888 bytes                               |
| Graphics stream         | stored 146 bytes at offset 4,512; reconstructed 49,152 bytes                              |
| System stream SHA-256   | `F8D58223326F4528F4AFB5816432984354C8DAFD48CC4A349F0EF4E0E481714D`                        |
| Graphics stream SHA-256 | `EA4E7F8318803D557BB02C9E7F9B55934072584F7EF217F807262B1C0F9C8BA9`                        |

The hashes identify the derived samples. They contain no asset data and no key material.

## Survey samples

Two sets of nested archives were extracted read-only and scanned by the source survey. All values are fingerprints of the extracted archives, not of the original game files.

Nested archives from `<GAME_ROOT>/textures.rpf`, rows 0 to 19. Every authenticated row had type ID 5. The set holds 1,365 resources in 2,736 streams.

| Row | Size       | SHA-256                                                            |
| --- | ---------- | ------------------------------------------------------------------ |
| 0   | 784,176    | `264DC0118E50729EB4348516075FFAFE06B9BF0DDCA1604244153B27231C16EF` |
| 1   | 4,720      | `FBE052831C9E2734CCF03C3D30083528988D2766F36E9A7E29C7FA7C293056E8` |
| 2   | 274,720    | `79E374AB174EC4BF967661F970BCFD698F998F101955993B5FBDB1CE17C07236` |
| 3   | 1,159,648  | `7D2F107656111723F0ABC973E00A4B3B958386D14A2A258D06836C11681A229D` |
| 4   | 412,848    | `CDD5284C255D8919A061CC6B63FC7F14C3DDE1BA3FFD451DED2A5E0A69153B37` |
| 5   | 28,736     | `9FB2811D9D7A3EC090B41A231007F5F7D3CB073BA0AF2AA949EC05BA4B14D24D` |
| 6   | 6,592      | `3B61AE08FE0791FBB930D55A731DDCB067D5E5B8991A0D17646346F4E084904E` |
| 7   | 13,327,488 | `D2DFC515461884BE1E45815DDFDD62E15BD8E688F3649442156DE51959060E58` |
| 8   | 19,154,192 | `033840AFA71424F56BCDE82EBDD13D6E63C916F9B4785A165520A9EDF74F9513` |
| 9   | 84,967,808 | `7F6311F368B2E3AE4C65440C97530B1DA84AA335D7D246B8503A092BF207B3E9` |
| 10  | 57,472     | `7E99A2C5D61BC8037E3F6692664D7B19B668989ED79C3A1A6923F9C5BD4116C1` |
| 11  | 33,753,360 | `0AF933A3B5E5322D3617B9B67F28BFDFB298B0752D575D4C166DBD7E43C007C3` |
| 12  | 2,728,720  | `31CFE051783D8B87687FC832A5214B973F0F438DED46582B9849986D01BAB3E6` |
| 13  | 2,626,064  | `ACD879C622651C0586E439073EBD734F74EA56185546CDBB1F21F9D8D2E02CAA` |
| 14  | 3,280,944  | `EB24B2D2C27BF49429F0F2141080C78D6E0CEEFEA585C37A54AB1B2FEE9ABA6D` |
| 15  | 1,575,952  | `63EEF013AF43A456B44E09761AB59BB496D2BF400E7C2435765E9A3C5E8FC0C3` |
| 16  | 4,159,856  | `05CDE8C940297889AFC9FC12A51BA79F004AE9319D0CBD330A97E162ACEF9969` |
| 17  | 2,249,840  | `D164F9A77C6EE0FB24E807C0D5E350E9363188E4F9D3247C1DD513674E96EAEB` |
| 18  | 20,926,720 | `DA78B9BB7944815BFA3675C9EE57C2FBF02AC6BB15FCE66FFD123983851F930A` |
| 19  | 90,960     | `1C32832BF4227C0735C9BC6CD11F49F95E940B16C0724D6C0F16741179FD2E35` |

Nested archives from `<GAME_ROOT>/data.rpf`. Rows 0 to 40 are nested archives; twenty were extracted and scanned, and eight held resources. The set holds 101 resources across type IDs 2, 4, 5 and 11.

| Row | Resource type IDs | Size      | SHA-256                                                            |
| --- | ----------------- | --------- | ------------------------------------------------------------------ |
| 1   | 5                 | 1,110,576 | `DDE85B0D4302E5E7E9E43439289CC1BB0A1AB6CA4EE17284969368AF86B862C9` |
| 3   | 5                 | 757,888   | `60C85DADC14BD6620A3D6F15A8A619B7BAFF77A4EF67A78D73E7ED08DB1611EF` |
| 7   | 4                 | 752,832   | `715B058F720979431A5D1D7F303F2E49980573FFC6A3DE066C15548CB16DA2D1` |
| 8   | 11                | 187,312   | `4F6EB5D35DCAF7CDA2A5E0297058A2F4BAE8DA3412035312311EFDE35BD0C979` |
| 14  | 2                 | 510,336   | `BBDEEDAECE51279746E86F74850E55F13104D6D8111DF0C3EB3E33AD1911BD4F` |
| 19  | 5                 | 2,082,992 | `E22F1C69CE68F4DA32B039D6702DB238ECAC6B8607F90C332020FB5165FD9D2D` |
| 31  | 4                 | 783,504   | `FDE95440F5F0DBC24D8B188D9C2338430EC00F962ADBD130D53A22804E42324B` |
| 39  | 5                 | 3,153,200 | `E6C5A55322BEF1EC013A9E75527C4DA4684305CF0AC5F1AC50D3C3D675B78E0D` |

Rows with type 66 were not resources: no resource header was found at their payload offset.

The `data.rpf` data area itself yielded 18,911 resources in the source CLI's scan (22,767 recovery candidates). 1,560 of them were re-parsed from bytes: all 247 with two system pages, all 673 with two graphics pages, 40 with no graphics page, and a random 600 with one page per segment.

The `data.rpf` nested archive at row 0 holds 156 type 11 rows in mode 1 without a chunk table. Those rows are layout `F`, not resources, and are documented under [RPF9-F118](../rpf9/INDEX.md). They do not contradict the resource survey's mode-0 encoding-2 observation.

Terrain and instance-placement nested archives from `<GAME_ROOT>/levels.rpf` supplied the type 6 raw-page rows, the 0DRP root-header rows and the block-tiling sample. The raw-page representative is inner row 46 of a terrain tile; the tiling sample is 12 instance-placement nested archives. The archive families are named; individual nested archive paths are not retained.

## Evidence types

Types follow [RESEARCH-POLICY.md](../../RESEARCH-POLICY.md#evidence-types). Each finding records its method and the type that method maps to.

| Type           | Use in this index                                                                                                         |
| -------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `BINARY`       | Archive and payload bytes: offsets, widths, counts and structural relations                                               |
| `CROSS_SAMPLE` | The same property checked across the sample sets above. Each finding states its scope; the counts are in the tables above |
| `SYNTHETIC`    | The parser's fixtures. They validate the tool, not native behavior, and support no finding in this index                  |

"Payload data" and "Archive data" are `BINARY`. A claim checked across several archives or resources is also `CROSS_SAMPLE`. The parser's 26 tests, `page_reconstruct`'s 14 tests and `root_tables`' 8 tests are `SYNTHETIC` and are recorded under [tools/resources](../../tools/resources/README.md), not as evidence for the findings.

## Findings

| ID      | Claim                                                                                                                                                                                                                                 | Evidence                            | Confidence                                                                           | Limits                                                                                                                                                                                               |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- | ------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| RES-F01 | The type 5 payload of the primary sample is two separately stored zlib streams that reconstruct to 1,888 and 49,152 bytes, whose sum is the row's logical size                                                                         | Payload data (BINARY); CLI and parser recheck | Confirmed (sample)                                                                   | One row, one archive                                                                                                                                                                                 |
| RES-F02 | The reconstructed system segment holds 32-bit values starting `0x5` (39 values) and `0x6` (12 values); every offset is inside its segment                                                                                             | Payload data (BINARY)               | Confirmed (sample)                                                                   | One resource                                                                                                                                                                                         |
| RES-F03 | The 12 values starting `0x6` are `0x60000000 + n * 0x1000` for `n = 0..11`, spanning the 49,152-byte graphics segment                                                                                                                  | Payload data (BINARY)               | Confirmed (sample)                                                                   | One resource                                                                                                                                                                                         |
| RES-F04 | System slot `+0x08` points to `0x50000610`; the bytes there are eight zeros, `01 01`, six zeros, 16 zero bytes, then ASCII names                                                                                                      | Payload data (BINARY)               | Confirmed (bytes)                                                                    | The counts are page counts (RES-F12), not stream counts                                                                                                                                              |
| RES-F05 | System slot `+0x30` points to a 12-entry array of `0x5000` pointers; `u16` fields at `+0x28` and `+0x38` hold `0x0C`                                                                                                                  | Payload data (BINARY)               | Confirmed (bytes); Probable (descriptor reading)                                     | Field meanings unknown                                                                                                                                                                               |
| RES-F06 | The byte `0xAA` occurs in 24 bytes in six 4-byte runs inside the graphics segment                                                                                                                                                     | Payload data (BINARY)               | Confirmed (sample)                                                                   | Not a segment-wide fill. Corrected interpretation in the research history                                                                                                                            |
| RES-F09 | Observed pointer fields are 8-byte slots whose upper half is zero in the primary sample and the survey                                                                                                                                | Payload data (BINARY, CROSS_SAMPLE) | Confirmed (sample, survey)                                                           | 1,466 authenticated rows and 1,560 re-parsed resources in the source survey. 12,441 values with a pointer-shaped low half and a nonzero upper half were not counted; whether any is a pointer is unknown                  |
| RES-F10 | A stored resource entry is 16 zero bytes followed by one zlib stream per RPF9 chunk. The chunk count equals the stream count and the inflated lengths sum to the logical size                                                         | Archive data (BINARY, CROSS_SAMPLE) | Confirmed                                                                            | 1,466 resource rows in the 28 scanned nested archives of the source survey. Only compression mode 0 with chunk encoding 2 observed. Whether a resource can use mode 1 is unknown                        |
| RES-F11 | The decoded payload is the system segment followed by the graphics segment. System data starts with a zero `u64` and, at `+8`, a system pointer to the page map                                                                       | Payload data (BINARY, CROSS_SAMPLE) | Confirmed                                                                            | 1,466 authenticated rows and 1,560 re-parsed resources in the source survey. Recognition depends on that header                                                                                                           |
| RES-F12 | The page map holds the system page count at `+8` and the graphics page count at `+9`. Every other byte is zero. The map lies inside the system pages, its offset is 8-aligned and at least `0x40`; its length is consistent with `16 + 8 * pages` (Probable) | Payload data (BINARY, CROSS_SAMPLE) | Confirmed (counts, zeroing, bounds); Probable (length, 16-byte header, 8-byte slots) | 3,026 resources in the source survey. Slots are always zero, so slot width and runtime content cannot be observed. Six maps end exactly at the system segment end                                               |
| RES-F13 | Declared page counts match the page groups derived from the chunk sizes in every complete resource. One resource declares one page more than the payload stores                                                                       | Payload data (BINARY, CROSS_SAMPLE) | Confirmed                                                                            | 3,026 resources in the source survey. Whether the absent page is missing or empty is not established. Rechecked counterexample in `pages.md`                                                          |
| RES-F14 | In a segment with more than one page, every page except the last is a multiple of `0x10000` and the last is at most `0x10000`                                                                                                         | Payload data (BINARY, CROSS_SAMPLE) | Confirmed for the samples; Probable as a rule                                        | 965 multi-page segments in the source survey, with no exception. Single-page segments are unconstrained. Rechecked in the split-page and second-system-page samples                                |
| RES-F15 | A page larger than 32 MiB is stored as several streams; every stream but the last inflates to exactly `0x2000000`. Rejected: a split length of `0x200000`                                                                            | Payload data (BINARY, CROSS_SAMPLE) | Confirmed (split length)                                                             | Four split pages rechecked among the source survey. A page of exactly 32 MiB cannot be told apart by stream length alone                                                                            |
| RES-F16 | The pointer split is a 4-bit segment selector and a 28-bit offset. A 16-bit selector is rejected by offsets above `0xFFFF`                                                                                                            | Payload data (BINARY, CROSS_SAMPLE) | Confirmed                                                                            | The rechecked second sample has a map at `0x988E0` and an in-bounds system pointer at `0x98B34`. 28 bits is the maximum the scheme can express; observed offsets use at most 26 bits                  |
| RES-F17 | Pointer offsets address the concatenated pages of a segment, not a page                                                                                                                                                               | Payload data (BINARY)               | Confirmed                                                                            | One rechecked resource with the map in the second system page and in-bounds system pointers reaching `0x98B34`                                                                                       |
| RES-F18 | Values that match the pointer encoding can lie outside their segment. They occur in real data and MUST be warnings, not proof of missing pages                                                                                        | Payload data (BINARY, CROSS_SAMPLE) | Confirmed (values occur); Probable (causes)                                          | Rechecked split-page and second-system-page resources. Causes identified by inspection as fill patterns, text and 32-bit hashes. No per-value proof                                                |
| RES-F19 | Every stored stream starts on a 16-byte boundary with zero fill after it. Both segment lengths are multiples of 16                                                                                                                    | Payload data (BINARY, CROSS_SAMPLE) | Confirmed                                                                            | 3,026 resources in the source survey. Alignment may come from the packer or the chunk layer                                                                                                          |
| RES-F20 | The same layout occurs across type IDs 2, 4, 5 and 11 and across the `textures.rpf` and `data.rpf` archive families                                                                                                                  | Archive data (BINARY, CROSS_SAMPLE) | Confirmed for 1,466 rows; Probable for the rest of `data.rpf`                        | Type IDs are the local CLI's assignment. The identity of the payload formats is not established. Only 1,560 of 18,911 `data.rpf` resources were re-parsed from bytes                                    |
| RES-F21 | 38 rows carry the four bytes `0DRP` at system `+0x10..+0x13` and the byte `0x7a` at `+0x14`, with zero at `+0x18`. Other rows carry 0 or 1 at `+0x18`                                                                                 | Archive data (BINARY, CROSS_SAMPLE) | Confirmed (bytes); Unknown (meaning)                                                 | The correlation is with the local CLI's type ID 11. Rechecked on one type 11 resource; the CLI reports the same `0DRP` tag                                                                                                          |
| RES-F22 | The source survey's pointer totals are 34,022 system-shaped and 6,609 graphics-shaped values in system data for the 1,466 authenticated rows, with 1,353 and 591 outside their segment. The 1,560 re-parsed `data.rpf` resources give 2,112,806 system-shaped values (44,463 outside) and 94,564 graphics-shaped values (52,873 outside) | Byte counts made by the originating survey (`BINARY`) | Probable; Not demonstrated as a whole | The originating survey's output is not preserved in this repository, so none of these totals can be re-derived here. They are recorded because the pointers document quotes them, and they carry the status of quoted figures rather than verified results |
| RES-F23 | Seven resources define the structural sample: page map in the primary sample, in a second system page, in four split-page resources and in a system-only resource. Their map offsets, page counts, segment sizes and split-page counts are the rows listed in the pages document | Payload bytes read with the current CLI (`BINARY`) | Confirmed for the seven rows as stated | Each row identifies its subject only by stored payload offset, so a row can be re-read from a matching resource but not from a named archive and row index. Two rows share payload `0x1000`, so an offset alone does not identify a resource. The values replace an earlier set whose subjects are not recorded; the earlier set is not retained |
| RES-F24 | A stored resource chunk can be a raw page: no zlib header, stored length equal to reconstructed length, and its bytes complete the row's logical size. The representative terrain tile holds five type 6 rows with a raw last system page of 8,768, 4,464, 16,288, 8,304 and 14,176 bytes; each declares 2 system pages and 0 graphics pages, with page maps at `0xFD60`, `0xFF70`, `0x1FF30`, `0xF5A0` and `0x1E900`. The representative is inner row 46: a 65,536-byte zlib page plus an 8,768-byte raw page (74,304 system bytes). Three more rows in other terrain tiles store an 8,768-byte raw page | Payload bytes and stored-size arithmetic (`BINARY`) | Confirmed (bytes, arithmetic) | Five rows in one tile and three in other tiles. A 16,384-byte raw page was not located; the largest in the tile is 16,288. Whether the engine treats the raw range as a page or copies it through another transport is **Unknown** |
| RES-F25 | The current CLI reconstructs only zlib streams. For the representative raw-page row it reports `system_size` 65,536, status `partial` and `1 of 2 system pages found`, although the second page is stored | CLI output and payload bytes (`BINARY`) | Confirmed (reproduced row) | One row. The command is in [Reproduction](#reproduction) |
| RES-F26 | Corrected reconstruction rule: reconstruct every declared page, including a raw last page; a readable page map MUST NOT end reconstruction; report `partial` only when a declared page is genuinely absent | Payload bytes, CLI output, synthetic tests (`BINARY`, `SYNTHETIC`) | Confirmed (reader rule) | A reader requirement; no engine-side reconstruction was traced |
| RES-F27 | A zlib stream is one page except a split page. A raw chunk is a page only when the declared page count requires it. No packed page, one stream covering two declared pages, was observed | Payload bytes (`BINARY`); synthetic packed-page fixture (`SYNTHETIC`) | Confirmed for zlib and raw pages in the sample; **Unknown** for packed pages | The 625,472-byte sample, the raw-page rows and the type 6 sample. The packed rule is untested outside the fixture |
| RES-F28 | The 625,472-byte sample has system pages of 589,824 and 35,648 bytes and a graphics page of 196,608 bytes, reconstructed from 3 streams. A fixed 64 KiB page size is refuted; `0x10000` is the allocation multiple for every page but the last | Payload bytes and CLI page sizes (`BINARY`) | Confirmed (sample) | One resource. The sample does not establish a maximum page size |
| RES-F29 | The 0DRP root header at `+0x10..+0x4F` reads as: `0DRP` at `+0x10`, `0x7A` at `+0x14`, zero at `+0x18`, a varying word at `+0x20`, pointers at `+0x28`, `+0x30`, `+0x38` and `+0x40`, and four `u16` at `+0x48`. A pointer at `+0x50` also appears in the type 73 and 74 samples | Payload bytes (`BINARY`) | Confirmed (bytes, three rows); **Unknown** (meanings) | One type 11, one type 73 and one type 74 resource. The private counts `3/0/3/0`, `13/2/7/1` and `32/4/27/41` were not all reproduced |
| RES-F30 | Every nonzero root pointer in the three samples resolved inside the system segment. No out-of-bounds or cross-page root pointer was found | Payload bytes (`BINARY`) | Confirmed (three rows) | Three resources, not a population |
| RES-F31 | The block table behind `+0x38` holds 16-byte entries: `u32` identifier, `u32` size, `u64` pointer. The third `u16` at `+0x48` is the entry count. The table need not end at the page map | Payload bytes (`BINARY`) | Confirmed (three rows) | One resource per family. The fourth `u16` and the `+0x20` word remain unknown |
| RES-F32 | In 4,426 type 73 resources with a declared graphics page and at least one graphics block, graphics blocks tile the page exactly in 2,864; 606 leave a remainder; 464 have an internal gap; 492 address outside the reconstructed graphics extent; no overlap was found | Payload bytes (`BINARY`, `CROSS_SAMPLE`) | Confirmed (sample counts) | 12 instance-placement nested archives, type 73 only. The private rows with 7,840 and 23,360-byte graphics pages were not located |
| RES-F33 | A block entry addresses a byte range inside the system or graphics segment. A page is not a block and not a stream; one page can contain several blocks, and a block can equal the page when the page contains one block | Payload bytes (`BINARY`) | Confirmed (samples) | Type 73 mainly; the type 11 and type 74 samples are too few to generalise |
| RES-F34 | Block ranges are not page-aligned. In the type 74 sample a system block spans `0xBCB0..0x146D0`, across the boundary between its two system pages. The block table cannot be used to derive page boundaries | Payload bytes (`BINARY`) | Confirmed (sample) | One type 74 resource |
| RES-F35 | Across 4,647 resources from 12 instance-placement nested archives, the corrected rule reconstructs all 4,647 as complete: 9,041 zlib pages and 496 raw pages, no packed page and no missing page. The CLI reports `partial` for many of the same rows | Payload bytes (`BINARY`, `CROSS_SAMPLE`); reconstruction tool (`SYNTHETIC` for its tests) | Confirmed (sample) | The completion test is the tool's page-count arithmetic, not an independent engine check. The 16,384-byte raw page variant was not located |

### Not carried

- **RES-F07** read the primary sample as a probable texture dictionary. The name meaning and pixel format were not established, so the reading is speculative and was dropped.
- **RES-F08** stated that one type 5 row carries a RAGE resource payload with two streams. It is folded into RES-F01 and is not kept as a separate claim.

## Counters and negative results

- **No stored page slot is nonzero.** 3,026 resources in the source survey, zero nonzero slot bytes. Rechecked samples agree.
- **One declared page has no stored chunk.** A `textures.rpf` nested row, entry `0x1000`, declares 1 system and 2 graphics pages but stores 2 streams. The graphics page present is `0x420000` bytes. The current CLI reports `partial`.
- **No map has a nonzero byte outside its counts.** Rechecked samples agree.
- **No map lies outside the system pages.** Rechecked samples agree.
- **No multi-page segment breaks the `0x10000` pattern.** 965 segments in the source survey; rechecked split-page samples agree.
- **No resource entry lacks the 16-byte zero header.** 1,466 authenticated rows and 1,560 re-parsed resources in the source survey.
- **No resource in the 1,466 authenticated rows was stored with compression mode 1 or without a chunk table.** The mode-1 type 11 rows of the `data.rpf` row 0 nested archive are layout `F`, not resources.
- **False positives are common.** In 1,560 `data.rpf` resources of the source survey, 52,873 of 94,564 graphics-shaped values in system data point past the graphics segment.
- **A wider pointer base was not established.** 12,441 `u64` values have a pointer-shaped low half and a nonzero upper half.
- **No engine allocation or validation path was traced.** Page allocation, runtime page slots and engine-side pointer validation remain **Unknown**.

## Reproduction

The commands below reproduce the checks. On 2026-11-25 the listing, resource and parser checks were run with the `lforge` CLI at application commit `92af6e2`. `<GAME_ROOT>` is a local installation, `<WORK>` a scratch directory outside it, and `<EXECUTABLE>` the game executable that matches the archive, used only to authenticate its metadata.

```text
lforge archive extract <GAME_ROOT>/textures.rpf --row 1 --output <WORK>/tex-row1.rpf --executable <EXECUTABLE>
lforge archive ls <WORK>/tex-row1.rpf --executable <EXECUTABLE> --json
lforge archive resource <WORK>/tex-row1.rpf 0x1010 --json
lforge archive resource <WORK>/tile.rpf 0x2EEB010 --json --no-cache
python tools/resources/rage_resource.py payload --file <WORK>/tex-row1.rpf --offset 0x1000 --length 576 --json
python tools/resources/rage_resource.py decoded --file <DECODED> --system-length 1888 --json
python tools/resources/page_reconstruct.py --file <WORK>/tile.rpf --offset 0x2EEB000 --length 47520 --json
python -m unittest discover -s tools/resources/tests
```

The byte-level results come from the published parser and `page_reconstruct`, which do not use application code. The local CLI supplied the authenticated metadata and was used as a cross-check: the rechecked rows matched on page-map offset, page counts, segment sizes, page sizes, stream counts and pointer counts. That agreement is consistency, not independent evidence for the format.

`<WORK>/tile.rpf` is a terrain-tile nested archive. The payload offsets `0x2EEB000` and `0x2EEB010` are the entry and the first stream; they identify the representative raw-page row, not a path.

## Limits

- One resource of one type was analysed in detail; the survey extends the checks but relies on scan recovery for the stored offsets. Authenticated chunk counts and logical sizes back the entry model (RES-F10).
- No engine code path was traced. Pointer validation, relocation, page-map semantics and page allocation are unknown.
- Payload bytes are outside the RPF9 metadata signature.
- The ASCII names below the page map are payload text. They are not reproduced in this repository; only their count and record stride are recorded.
- Only 1,560 of the 18,911 `data.rpf` resources were re-parsed from bytes in the source survey; the rest are counts from the local CLI.
- A raw stored page was observed only in type 6 rows. Its identity as a page is supported by the page count, the logical size and the size pattern, not by engine code.
- The 0DRP root header and block table were read on three resources. The block-tiling population is type 73 only.
- Archives other than `textures.rpf`, `data.rpf` and `levels.rpf` were not scanned for resources. `common.rpf` and `script.rpf` reported none; `shaders.rpf` was not scanned for resources.

## Next experiments

- Trace the resource loader in the executable for pointer validation and page allocation.
- Find a resource with a nonzero page slot, or a decrypted runtime page map, to establish the slot width.
- Find a resource stored as raw DEFLATE without a chunk table, to see whether the page layout survives without chunk sizes.
- Find or build a resource with a page of exactly 32 MiB to confirm the grouping rule.
- Check whether the absent page in the incomplete resource is empty or missing.
