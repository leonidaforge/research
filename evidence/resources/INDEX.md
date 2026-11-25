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

## Evidence types

Types follow [RESEARCH-POLICY.md](../../RESEARCH-POLICY.md#evidence-types). Each finding records its method and the type that method maps to.

| Type           | Use in this index                                                                                                         |
| -------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `BINARY`       | Archive and payload bytes: offsets, widths, counts and structural relations                                               |
| `CROSS_SAMPLE` | The same property checked across the sample sets above. Each finding states its scope; the counts are in the tables above |
| `SYNTHETIC`    | The parser's fixtures. They validate the tool, not native behavior, and support no finding in this index                  |

"Payload data" and "Archive data" are `BINARY`. A claim checked across several archives or resources is also `CROSS_SAMPLE`. The parser's 26 tests are `SYNTHETIC` and are recorded under [tools/resources](../../tools/resources/README.md), not as evidence for the findings.

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
python tools/resources/rage_resource.py payload --file <WORK>/tex-row1.rpf --offset 0x1000 --length 576 --json
python tools/resources/rage_resource.py decoded --file <DECODED> --system-length 1888 --json
python -m unittest discover -s tools/resources/tests
```

The byte-level results come from the published parser, which does not use application code. The local CLI supplied the authenticated metadata and was used as a cross-check: the rechecked rows matched on page-map offset, page counts, segment sizes, page sizes, stream counts and pointer counts. That agreement is consistency, not independent evidence for the format.

## Limits

- One resource of one type was analysed in detail; the survey extends the checks but relies on scan recovery for the stored offsets. Authenticated chunk counts and logical sizes back the entry model (RES-F10).
- No engine code path was traced. Pointer validation, relocation, page-map semantics and page allocation are unknown.
- Payload bytes are outside the RPF9 metadata signature.
- The ASCII names below the page map are payload text. They are not reproduced in this repository; only their count and record stride are recorded.
- Only 1,560 of the 18,911 `data.rpf` resources were re-parsed from bytes in the source survey; the rest are counts from the local CLI.
- Archives other than `textures.rpf` and `data.rpf` were not scanned for resources. `common.rpf` and `script.rpf` reported none; `shaders.rpf` was not scanned for resources.

## Next experiments

- Trace the resource loader in the executable for pointer validation and page allocation.
- Find a resource with a nonzero page slot, or a decrypted runtime page map, to establish the slot width.
- Find a resource stored as raw DEFLATE without a chunk table, to see whether the page layout survives without chunk sizes.
- Find or build a resource with a page of exactly 32 MiB to confirm the grouping rule.
- Check whether the absent page in the incomplete resource is empty or missing.
