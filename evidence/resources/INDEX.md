# Resource evidence index

Payload observations from the Scarlett build [e95020b2](../../builds/gta-vi/scarlett-e95020b2/README.md). No executable code path was traced for this subject. Every finding is **Private-evidence supported**: it is checkable against a local installation but not from this repository alone.

## Sample locators

Each sample is identified by the top-level archive, the row index, the inner row index for a nested archive, the type ID, the stored size and the SHA-256 of the stored row bytes. The digests contain no asset data and no key material. `<GAME_ROOT>` is a local installation.

### Primary sample

| Property                | Value                                                                                     |
| ----------------------- | ----------------------------------------------------------------------------------------- |
| Top-level archive       | `<GAME_ROOT>/textures.rpf`                                                                |
| Top-level row           | 1                                                                                         |
| Inner row               | 0, type ID 5                                                                              |
| Entry                   | payload offset `0x1000`, stored size 576, logical size 51,040                             |
| Chunks                  | encoding 2, count 2                                                                       |
| System stream           | stored 395 bytes at offset 4,112; reconstructed 1,888 bytes                               |
| Graphics stream         | stored 146 bytes at offset 4,512; reconstructed 49,152 bytes                              |
| Nested archive SHA-256  | `FBE052831C9E2734CCF03C3D30083528988D2766F36E9A7E29C7FA7C293056E8`                        |
| Stored row SHA-256      | `F83B14F1D2B441DE80CFE082DDB94BD19B96983E3D00C14AADDFF1B1088CAD46`                        |
| System stream SHA-256   | `F8D58223326F4528F4AFB5816432984354C8DAFD48CC4A349F0EF4E0E481714D`                        |
| Graphics stream SHA-256 | `EA4E7F8318803D557BB02C9E7F9B55934072584F7EF217F807262B1C0F9C8BA9`                        |

### New samples

| Sample                         | Top-level archive          | Row  | Inner row | Type | Stored size | Stored row SHA-256                                                  |
| ------------------------------ | -------------------------- | ---- | --------- | ---- | ----------- | ------------------------------------------------------------------- |
| type 4 layout                  | `<GAME_ROOT>/levels.rpf`   | 1292 | 0         | 4    | 12,272      | `037FA3771E0FD1E22A8A3D1ADC43FD07984A6CADDC95C0570A071C209CCA1E98` |
| type 11 0DRP                   | `<GAME_ROOT>/data.rpf`     | 34   | 3         | 11   | 880         | `4001FA3F337B43C1C1D8A79E2CB877259A78A476FDF9C13066A9EB5165C61374` |
| type 73 0DRP                   | `<GAME_ROOT>/levels.rpf`   | 116  | 1         | 73   | 5,024       | `A95A31BA11313D8AF1BA19CC30E418E38A68D9F07A81DD2B6D2E3102C2565745` |
| type 74 0DRP                   | `<GAME_ROOT>/levels.rpf`   | 19   | 5         | 74   | 61,776      | `1E10182506FC7C0D4C5DBC0FED79EB0103584EA32A5FE674508AD61F46A1E445` |
| 625,472-byte resource          | `<GAME_ROOT>/data.rpf`     | 14   | 1         | 2    | 257,968     | `058B158AC0BE8A5CEB0D70F848B4DB025A514D065735B415EC4E31E477E7ECFB` |
| raw last system page, row 46   | `<GAME_ROOT>/levels.rpf`   | 2    | 46        | 6    | 47,520      | `5FD804A1D8CF7FCA380F8392239A1E3E0AC4F97D73217C7C424365D350AA1B7D` |
| raw last system page, row 62   | `<GAME_ROOT>/levels.rpf`   | 2    | 62        | 6    | 43,696      | `BBC97D8347E6B77F9884D9445EA2EAA7478340A2A17F48F6548987BA9B932A75` |
| raw last system page, row 89   | `<GAME_ROOT>/levels.rpf`   | 2    | 89        | 6    | 92,400      | `6D250A4D07696BAAFA41C1BFCCAA922BE25A27DD6103645C0C121D09FD0E6498` |
| raw last system page, row 112  | `<GAME_ROOT>/levels.rpf`   | 2    | 112       | 6    | 45,344      | `1A9FF84E625BD92489F1EC19F63EFE792A4CB4687AEC89A28401E98C8D300BB3` |
| raw last system page, row 139  | `<GAME_ROOT>/levels.rpf`   | 2    | 139       | 6    | 90,496      | `A474524399D2C57A1F619FB6CCFCC3B9DE8D7917CA6A3C1E1DAC75FD67C0567A` |
| raw last system page, row 219  | `<GAME_ROOT>/levels.rpf`   | 216  | 219       | 6    | 48,480      | `B96D51110164E3A2C7604E29B5AFE190D0F37FCC6776A63D445A6B33AEA09D5C` |
| raw last system page, row 47   | `<GAME_ROOT>/levels.rpf`   | 1005 | 47        | 6    | 49,120      | `8339000C87688DF19EEC57290383C5B6C92559C9225E79912DBA9D0FD2E6B7B9` |
| raw last system page, row 45   | `<GAME_ROOT>/levels.rpf`   | 1406 | 45        | 6    | 46,848      | `A033A23A85122A7C1D5AFF270B375589F070F92F54F752972B2237239F94ABDE` |
| raw last system page, row 82   | `<GAME_ROOT>/levels.rpf`   | 1361 | 82        | 6    | 46,304      | `F3AEDF5CBBAC8563BD22C9B3935ED871BCE8D8F03F58D0FCBA57882BB04E64EF` |

### Tiling sample

The tiling sample is every type 73 row with a declared graphics page and at least one record whose `+8` pointer selects graphics, in the 12 nested archives below. The archives are type 0 rows of `<GAME_ROOT>/levels.rpf`.

| Row  | Stored size | SHA-256                                                            |
| ---- | ----------- | ------------------------------------------------------------------ |
| 153  | 12,681,024  | `41EB09D66E6DD3348BC5F0533CE64C11BF95B185711B8D34CF4C33B3AE85B7AE` |
| 282  | 8,770,816   | `2D3B0C8327960FE2B4A143802973AD886EE04D2181F82C86D62414A64A023FD4` |
| 298  | 28,548,752  | `05A3B9EA3079A9EF836B2C6B565E72A2CBC34B2C5BC03AE8ED23359883D1F506` |
| 1109 | 11,089,792  | `16E0A47BB37CC4195E92045F8CDC1D598B5D8DEA269F209A79ADA1D841D8CA0E` |
| 1170 | 16,284,432  | `D3A36CE2835DAD5128164C03571F9B7EDD57A88DD9C07B1FDD2CF03E69A5940C` |
| 1479 | 21,519,792  | `6B3659297386AC306DC7F0857F266A357A2341BF332C35AB3B85411E7CF14E72` |
| 1591 | 7,146,320   | `EB2480133577C8E2A900F953ED357C1B8AD97ADF3EDDABEF260693064EE27587` |
| 1617 | 11,524,624  | `10C9E2400330CDC670EF836159A172D1B8B83936A7FABBF7AB76B4F808DB086E` |
| 1622 | 19,690,032  | `70936597A786CA799F08F196154C9EA128F152BC156919169C55966EB6A6F8F9` |
| 1705 | 14,977,280  | `632AB617DC4C38416A8311E6DDB804DC23780F2BF98D93569F4598633A4972B0` |
| 1773 | 15,467,376  | `73F614269948D6AA654137C4B70B82F9293CEB236E2273B7CFAAD182460F3D29` |
| 2045 | 9,790,624   | `272FBE26DAEDC833E94B493A302931775D3A0746D323A7544AAFFB670555BED1` |

### Texture dictionary sample

The texture dictionary sample is every type-5 row of the 25 nested archives below. Each archive is a type-0 row of `<GAME_ROOT>/textures.rpf` or `<GAME_ROOT>/data.rpf`. The digests are of the stored top-level row bytes, which are the nested archive. Inner rows are identified by their row index within the nested archive and by their payload offset, stored size and logical size. The sample holds 1,440 dictionaries and 5,484 records; the selection rule is the local CLI type ID 5, and no other type-5 row was found in the scanned archives.

| Top-level archive | Row | Stored size | Type-5 rows | SHA-256                                                            |
| ----------------- | --: | ----------: | ----------: | ------------------------------------------------------------------ |
| `textures.rpf`    | 0   |     784,176 |           1 | `264DC0118E50729EB4348516075FFAFE06B9BF0DDCA1604244153B27231C16EF` |
| `textures.rpf`    | 1   |       4,720 |           1 | `FBE052831C9E2734CCF03C3D30083528988D2766F36E9A7E29C7FA7C293056E8` |
| `textures.rpf`    | 2   |     274,720 |           1 | `79E374AB174EC4BF967661F970BCFD698F998F101955993B5FBDB1CE17C07236` |
| `textures.rpf`    | 3   |   1,159,648 |           5 | `7D2F107656111723F0ABC973E00A4B3B958386D14A2A258D06836C11681A229D` |
| `textures.rpf`    | 4   |     412,848 |           1 | `CDD5284C255D8919A061CC6B63FC7F14C3DDE1BA3FFD451DED2A5E0A69153B37` |
| `textures.rpf`    | 5   |      28,736 |           1 | `9FB2811D9D7A3EC090B41A231007F5F7D3CB073BA0AF2AA949EC05BA4B14D24D` |
| `textures.rpf`    | 6   |       6,592 |           1 | `3B61AE08FE0791FBB930D55A731DDCB067D5E5B8991A0D17646346F4E084904E` |
| `textures.rpf`    | 7   |  13,327,488 |           6 | `D2DFC515461884BE1E45815DDFDD62E15BD8E688F3649442156DE51959060E58` |
| `textures.rpf`    | 8   |  19,154,192 |           1 | `033840AFA71424F56BCDE82EBDD13D6E63C916F9B4785A165520A9EDF74F9513` |
| `textures.rpf`    | 9   |  84,967,808 |           9 | `7F6311F368B2E3AE4C65440C97530B1DA84AA335D7D246B8503A092BF207B3E9` |
| `textures.rpf`    | 10  |      57,472 |           3 | `7E99A2C5D61BC8037E3F6692664D7B19B668989ED79C3A1A6923F9C5BD4116C1` |
| `textures.rpf`    | 11  |  33,753,360 |           9 | `0AF933A3B5E5322D3617B9B67F28BFDFB298B0752D575D4C166DBD7E43C007C3` |
| `textures.rpf`    | 12  |   2,728,720 |           1 | `31CFE051783D8B87687FC832A5214B973F0F438DED46582B9849986D01BAB3E6` |
| `textures.rpf`    | 13  |   2,626,064 |           1 | `ACD879C622651C0586E439073EBD734F74EA56185546CDBB1F21F9D8D2E02CAA` |
| `textures.rpf`    | 14  |   3,280,944 |           1 | `EB24B2D2C27BF49429F0F2141080C78D6E0CEEFEA585C37A54AB1B2FEE9ABA6D` |
| `textures.rpf`    | 15  |   1,575,952 |           1 | `63EEF013AF43A456B44E09761AB59BB496D2BF400E7C2435765E9A3C5E8FC0C3` |
| `textures.rpf`    | 16  |   4,159,856 |           3 | `05CDE8C940297889AFC9FC12A51BA79F004AE9319D0CBD330A97E162ACEF9969` |
| `textures.rpf`    | 17  |   2,249,840 |           1 | `D164F9A77C6EE0FB24E807C0D5E350E9363188E4F9D3247C1DD513674E96EAEB` |
| `textures.rpf`    | 18  |  20,926,720 |       1,315 | `DA78B9BB7944815BFA3675C9EE57C2FBF02AC6BB15FCE66FFD123983851F930A` |
| `textures.rpf`    | 19  |      90,960 |           3 | `1C32832BF4227C0735C9BC6CD11F49F95E940B16C0724D6C0F16741179FD2E35` |
| `data.rpf`        | 1   |   1,110,576 |           3 | `DDE85B0D4302E5E7E9E43439289CC1BB0A1AB6CA4EE17284969368AF86B862C9` |
| `data.rpf`        | 3   |     757,888 |           3 | `60C85DADC14BD6620A3D6F15A8A619B7BAFF77A4EF67A78D73E7ED08DB1611EF` |
| `data.rpf`        | 19  |   2,082,992 |          29 | `E22F1C69CE68F4DA32B039D6702DB238ECAC6B8607F90C332020FB5165FD9D2D` |
| `data.rpf`        | 33  |  98,215,344 |          38 | `F60C836DB9EA4596C0BB7D843E744A81DD38AF53BC4AA43CAD168C26DB99E3A9` |
| `data.rpf`        | 39  |   3,153,200 |           2 | `E6C5A55322BEF1EC013A9E75527C4DA4684305CF0AC5F1AC50D3C3D675B78E0D` |

## Evidence types

Types follow [RESEARCH-POLICY.md](../../RESEARCH-POLICY.md#evidence-types). Each finding records its method and the type that method maps to.

| Type           | Use in this index                                                                                                         |
| -------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `BINARY`       | Archive and payload bytes: offsets, widths, counts and structural relations                                               |
| `CROSS_SAMPLE` | The same property checked across the sample locators. Each finding states its scope                                      |
| `SYNTHETIC`    | The tools' fixtures. They validate the tools, not native behavior, and support no finding in this index                  |

"Payload data" and "Archive data" are `BINARY`. A claim checked across several archives or resources is also `CROSS_SAMPLE`. The parser's 26 tests, `page_reconstruct`'s 18 tests, `root_tables`' 8 tests, `texture_dictionary`'s 21 tests and `pool_reference`'s 14 tests are `SYNTHETIC` and are recorded under [tools/resources](../../tools/resources/README.md), not as evidence for the findings.

## Findings

| ID      | Claim                                                                                                                                                                                                                                 | Evidence                            | Confidence                                                                           | Limits                                                                                                                                                                                               |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- | ------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| RES-F01 | The type 5 payload of the primary sample is two separately stored zlib streams that reconstruct to 1,888 and 49,152 bytes, whose sum is the row's logical size                                                                         | Payload data (BINARY); CLI and parser recheck | Confirmed (sample)                                                                   | One row, one archive                                                                                                                                                                                 |
| RES-F02 | The reconstructed system segment holds 32-bit values starting `0x5` (39 values) and `0x6` (12 values); every offset is inside its segment                                                                                             | Payload data (BINARY)               | Confirmed (sample)                                                                   | One resource                                                                                                                                                                                         |
| RES-F03 | The 12 values starting `0x6` are `0x60000000 + n * 0x1000` for `n = 0..11`, spanning the 49,152-byte graphics segment                                                                                                                  | Payload data (BINARY)               | Confirmed (sample)                                                                   | One resource                                                                                                                                                                                         |
| RES-F04 | System slot `+0x08` points to `0x50000610`; the bytes there are eight zeros, `01 01`, six zeros, 16 zero bytes, then ASCII names                                                                                                      | Payload data (BINARY)               | Confirmed (bytes)                                                                    | The counts are page counts (RES-F12), not stream counts                                                                                                                                              |
| RES-F05 | System slot `+0x30` points to a 12-entry array of `0x5000` pointers; `u16` fields at `+0x28` and `+0x38` hold `0x0C`                                                                                                                  | Payload data (BINARY)               | Confirmed (bytes); Probable (descriptor reading)                                     | Field meanings unknown                                                                                                                                                                               |
| RES-F06 | The byte `0xAA` occurs in 24 bytes in six 4-byte runs inside the graphics segment                                                                                                                                                     | Payload data (BINARY)               | Confirmed (sample)                                                                   | Not a segment-wide fill. Corrected interpretation in the research history                                                                                                                            |
| RES-F09 | Observed pointer fields are 8-byte slots whose upper half is zero in the primary sample and the rechecked rows                                                                                                                        | Payload data (BINARY, CROSS_SAMPLE) | Confirmed (sample)                                                                   | Values with a pointer-shaped low half and a nonzero upper half were not counted; whether any is a pointer is unknown                                                                                  |
| RES-F10 | A stored resource entry is 16 zero bytes followed by one chunk per page. In the rechecked rows every chunk is a zlib stream or a raw page, the chunk count equals the RPF9 chunk count, and the reconstructed lengths sum to the logical size | Archive data (BINARY, CROSS_SAMPLE) | Confirmed                                                                            | Rechecked rows. Only compression mode 0 with chunk encoding 2 observed. Whether a resource can use mode 1 is unknown                                                                                  |
| RES-F11 | The decoded payload is the system segment followed by the graphics segment. System data starts with a zero `u64` and, at `+8`, a system pointer to the page map                                                                       | Payload data (BINARY, CROSS_SAMPLE) | Confirmed                                                                            | Primary sample, 625,472-byte sample and raw-page rows. Recognition depends on that header                                                                                                            |
| RES-F12 | The page map holds the system page count at `+8` and the graphics page count at `+9`. Every other byte is zero. The map lies inside the system pages, its offset is 8-aligned and at least `0x40`; its length is consistent with `16 + 8 * pages` (Probable) | Payload data (BINARY, CROSS_SAMPLE) | Confirmed (counts, zeroing, bounds); Probable (length, 16-byte header, 8-byte slots) | Rechecked maps. Slots are always zero, so slot width and runtime content cannot be observed                                                                                                          |
| RES-F13 | Declared page counts match the reconstructed page groups in every rechecked complete resource. One resource declares one page more than the payload stores | Payload data (BINARY, CROSS_SAMPLE) | Confirmed | Rechecked complete resources. The counterexample is in `pages.md`; its archive row locator is not retained (Probable). Whether the absent page is missing or empty is not established |
| RES-F14 | In a segment with more than one page, every page except the last is a multiple of `0x10000` and the last is at most `0x10000`                                                                                                         | Payload data (BINARY, CROSS_SAMPLE) | Confirmed for the samples; Probable as a rule                                        | 4,647 rechecked resources with no page-size violation. Single-page segments are unconstrained                                                                                                        |
| RES-F15 | A page larger than 32 MiB is stored as several streams; every stream but the last inflates to exactly `0x2000000`. Rejected: a split length of `0x200000`                                                                            | Payload data (BINARY, CROSS_SAMPLE) | Confirmed (split length)                                                             | Four split-page rows are identified by payload offset and size in `pages.md`; their archive row locators are not retained. A page of exactly 32 MiB cannot be told apart by stream length alone |
| RES-F16 | The pointer split is a 4-bit segment selector and a 28-bit offset. A 16-bit selector is rejected by offsets above `0xFFFF`                                                                                                            | Payload data (BINARY, CROSS_SAMPLE) | Confirmed                                                                            | The 625,472-byte sample has a map at `0x988E0` and an in-bounds system pointer at `0x98B34`. 28 bits is the maximum the scheme can express; observed offsets use at most 26 bits                  |
| RES-F17 | Pointer offsets address the concatenated pages of a segment, not a page                                                                                                                                                               | Payload data (BINARY)               | Confirmed                                                                            | The 625,472-byte sample has its map in the second system page and in-bounds system pointers reaching `0x98B34`                                                                                       |
| RES-F18 | Values that match the pointer encoding can lie outside their segment. They occur in real data and MUST be warnings, not proof of missing pages                                                                                        | Payload data (BINARY, CROSS_SAMPLE) | Confirmed (values occur); Probable (causes)                                          | Rechecked rows. Causes identified by inspection as fill patterns, text and 32-bit hashes. No per-value proof                                                                                          |
| RES-F19 | Every stored stream starts on a 16-byte boundary with zero fill after it. Both segment lengths are multiples of 16                                                                                                                    | Payload data (BINARY, CROSS_SAMPLE) | Confirmed                                                                            | Rechecked rows. Alignment may come from the packer or the chunk layer                                                                                                                                |
| RES-F20 | The same layout occurs in the rechecked type 2, 4, 5, 11, 73 and 74 rows                                                                                                                                                              | Archive data (BINARY, CROSS_SAMPLE) | Confirmed (sample)                                                                   | Type IDs are the local CLI's assignment. The identity of the payload formats is not established. Sample locators above                                                                                |
| RES-F21 | The four bytes `0DRP` occur at system `+0x10..+0x13` with the byte `0x7A` at `+0x14` and zero at `+0x18` in the rechecked samples. Other rows carry 0 or 1 at `+0x18`                                                                  | Archive data (BINARY, CROSS_SAMPLE) | Confirmed (bytes); Unknown (meaning)                                                 | Rechecked 0DRP samples of types 11, 73 and 74. The meaning is unknown                                                                                                                                |
| RES-F23 | Eight resources define the structural sample: the rows in the Rechecked samples table in [pages.md](../../formats/resources/pages.md) (primary sample, 625,472-byte sample, raw-page representative, four split-page rows and system-only row). The selection rule is that each row exercises a page-map or page-size condition. Four split-page rows are identified by payload offset and size; their archive row locators are not retained | Payload bytes read with the current CLI (`BINARY`) | Confirmed for the located rows; Probable for the split-page rows | The structural sample has eight rows. The split-page rows cannot be re-read from an archive row index in this repository                                                                                                                   |
| RES-F24 | A stored resource chunk can be a raw page: no zlib header, stored length equal to reconstructed length, and its bytes complete the row's logical size. Nine raw-page rows are located: five in the representative terrain tile (`levels.rpf` row 2, inner rows 46, 62, 89, 112 and 139) with tails of 8,768, 4,464, 16,288, 8,304 and 14,176 bytes; three in other terrain tiles (`levels.rpf` rows 216, 1005 and 1406, inner rows 219, 47 and 45) with 8,768-byte tails; and one in `levels.rpf` row 1361, inner row 82, with an 8,000-byte tail. The representative is inner row 46: a 65,536-byte zlib page plus an 8,768-byte raw page (74,304 system bytes) | Payload bytes and stored-size arithmetic (`BINARY`) | Confirmed (bytes, arithmetic) | Nine rows: five in one tile, three in three other terrain tiles and one in a different nested archive. Whether the engine treats the raw range as a page or copies it through another transport is **Unknown** |
| RES-F25 | The current CLI reconstructs only zlib streams. For the representative raw-page row it reports `system_size` 65,536, status `partial` and `1 of 2 system pages found`, although the second page is stored | CLI output and payload bytes (`BINARY`) | Confirmed (reproduced row) | One row. The command is in [Reproduction](#reproduction) |
| RES-F26 | Corrected reconstruction rule: reconstruct every declared page, including a raw last page; a readable page map MUST NOT end reconstruction; report `partial` only when a declared page is genuinely absent | Payload bytes, CLI output, synthetic tests (`BINARY`, `SYNTHETIC`) | Confirmed (reader rule) | A reader requirement; no engine-side reconstruction was traced |
| RES-F27 | A zlib stream is one page except a split page. A raw chunk is a page only when the declared page count and logical size require it. No packed page, one stream covering two declared pages, was observed | Payload bytes (`BINARY`); synthetic packed-page fixture (`SYNTHETIC`) | Confirmed for zlib and raw pages in the sample; **Unknown** for packed pages | The 625,472-byte sample, the raw-page rows and the type 6 rows. The packed rule is untested outside the fixture |
| RES-F28 | The 625,472-byte sample has system pages of 589,824 and 35,648 bytes and a graphics page of 196,608 bytes, reconstructed from 3 streams. A fixed 64 KiB page size is refuted; `0x10000` is the allocation multiple for every page but the last | Payload bytes and CLI page sizes (`BINARY`) | Confirmed (sample) | One resource. The sample does not establish a maximum page size |
| RES-F29 | The 0DRP root header at `+0x10..+0x4F` reads as: `0DRP` at `+0x10`, `0x7A` at `+0x14`, zero at `+0x18`, a word at `+0x20`, pointers at `+0x28`, `+0x30`, `+0x38` and `+0x40`, and four `u16` at `+0x48`. A pointer at `+0x50` also appears in the type 73 and 74 samples | Payload bytes (`BINARY`) | Confirmed (bytes, three rows); **Unknown** (meanings) | One type 11, one type 73 and one type 74 resource. The four `u16` were `2/2/2/0`, `13/2/5/1` and `4/3/5/32`; the `+0x20` word was `1`, `1` and `2`. The field positions are validated; the individual values are not a rule |
| RES-F30 | Every nonzero root pointer in the three samples resolved inside the system segment. No out-of-bounds or cross-page root pointer was found | Payload bytes (`BINARY`) | Confirmed (three rows) | Three resources, not a population |
| RES-F31 | The `+0x38` pointer leads to 16-byte records. Each record has a 4-byte value at `+0`, a 4-byte value at `+4` and a pointer at `+8`. The walk reads the third `u16` field at `+0x48` times 16 bytes; that field's meaning is unconfirmed. The record table need not end at the page map | Payload bytes (`BINARY`) | Confirmed (bytes, three rows); **Unknown** (meanings) | One resource per family. The `+0` and `+4` meanings are not established; the `+4` value is used only as a length in the boundary check |
| RES-F32 | In 4,426 type 73 resources with a declared graphics page and at least one record whose `+8` pointer selects graphics, records whose pointer selects graphics tile the page exactly in 2,864; 606 leave a remainder; 464 have an internal gap; 492 address outside the reconstructed graphics extent; no overlap was found | Payload bytes (`BINARY`, `CROSS_SAMPLE`) | Confirmed (sample counts) | 12 instance-placement nested archives, type 73 only; 4,426 resources. The counts describe that sample; no tiling rule is stated for type 11 or type 74 |
| RES-F33 | A 16-byte record whose `+8` pointer selects a segment delimits a byte range inside that segment. A page is not a record and not a stream; one page can contain several such ranges, and a range can equal the page when the page contains one range | Payload bytes (`BINARY`) | Confirmed (samples) | Type 73 mainly; the type 11 and type 74 samples are too few to generalise |
| RES-F34 | Record ranges are not page-aligned. In the type 74 sample a system range spans `0xBCB0..0x146D0`, across the boundary between its two system pages. The record table cannot be used to derive page boundaries | Payload bytes (`BINARY`) | Confirmed (sample) | One type 74 resource |
| RES-F35 | Across 4,647 resources from 12 instance-placement nested archives, the corrected rule reconstructs all 4,647 as complete: 9,041 zlib pages and 496 raw pages, no packed page and no missing page. The CLI reports `partial` for many of the same rows | Payload bytes (`BINARY`, `CROSS_SAMPLE`); reconstruction tool (`SYNTHETIC` for its tests) | Confirmed (sample) | The completion test is the tool's page-count arithmetic, not an independent engine check. The raw-page rows are listed above |
| RES-F36 | A texture dictionary is recognised by arithmetic in the decoded system segment: a zero first qword, a system page-map pointer at `+0x08`, a system hash-array pointer at `+0x20` with `u16` count and capacity at `+0x28`, a system value-array pointer at `+0x30` with `u16` count and capacity at `+0x38`, equal counts, an ascending duplicate-free `u32` hash array, and a value array whose entries are system pointers to 0x70-byte records. All 1,431 non-empty dictionaries pass; the 9 empty dictionaries have zero pointers and zero counts | Payload bytes (`BINARY`, `CROSS_SAMPLE`) | Confirmed (positions and counts, sample); Probable (recognition as a general rule) | 1,440 type-5 resources from 25 nested archives of two top-level archives. No engine code that builds or validates a dictionary was traced |
| RES-F37 | A texture record is 0x70 bytes: a `u32` allocation unit count at `+0x08`, a graphics allocation pointer at `+0x18`, a system name pointer at `+0x30` with ASCII text at pointer `+8`, `u16` width at `+0x38`, `u16` height at `+0x3A`, a format id at `+0x3F`, and a mip word at `+0x42` whose low 15 bits are the mip count. Width, height, format id and mip count are supported by allocation arithmetic, not by pixel decoding | Payload bytes (`BINARY`, `CROSS_SAMPLE`); arithmetic (`CROSS_SAMPLE`) | Confirmed (positions, 5,484 records); Probable (width, height, format id, mips) | One build. The meanings of the other record fields are **Unknown**. The format id is not decoded to pixels |
| RES-F38 | For every record, `allocation_units × unit_bytes(format id)` equals the stored allocation size, stays inside the graphics segment, and is at most the gap to the next allocation. The 22 observed format ids each give one consistent unit; the units take the values 1, 2, 4, 8 and 16 bytes. The sizes sum to at most the graphics size in all 1,431 non-empty resources (equality in 1,375, strict inequality in 56); the 9 empty dictionaries have no graphics segment. The 4 KiB-aligned mip-chain size computed from width, height, format unit and mip count is at most the stored size in 5,484 of 5,484 records and equal in 4,901; the other 583 are larger | Payload bytes (`BINARY`, `CROSS_SAMPLE`); allocation arithmetic (`CROSS_SAMPLE`) | Confirmed (bounds, inequality, sample counts); Probable (format id selects the unit) | No allocation overrun or duplicate start was observed. The 583 larger allocations are not explained; padding or additional surfaces are candidates. The unit table is not a pixel decoder |
| RES-F39 | Each stored 32-bit name hash equals the one-at-a-time (`joaat`) hash of the ASCII text reached from the record's `+0x30` pointer with the text at pointer `+8`; 5,484 of 5,484 records match. The text and the hashes are payload data and are not published | Payload bytes (`BINARY`, `CROSS_SAMPLE`); hash comparison (`CROSS_SAMPLE`) | Confirmed (sample) | One build. The relation is a key namespace, not a recovered filename. A 32-bit match is weaker than a 64-bit one |
| RES-F40 | The sample holds 1,440 type-5 dictionaries and 5,484 records: 1 to 1,198 records per dictionary, 94 distinct dimension pairs from 4×4 to 4,096×1,024, 22 format ids and 1 to 12 mip levels. Nine dictionaries are empty (96-byte system segment, one system page, no graphics page). One 1,198-record dictionary has a 0x20-byte record-table gap at a `0x10000` boundary, so the table is not required to be contiguous; the 0x70 record width holds | Payload bytes (`BINARY`, `CROSS_SAMPLE`) | Confirmed (sample counts) | A census of the type-5 rows in the 25 nested archives, not of the game. Other archives and builds were not scanned |
| RES-F41 | In the 92 type-2 drawables of the nested archive at `levels.rpf` row 5 (164 shaders, 969 texture parameters), each texture parameter's `u32` at entry `+0x04` selects a slot: low two bits are the class, class 0 means a texture entry and bits 2..31 are the slot index. All 969 texture entries resolve to an index below the texture count; 0 of 7,920 non-texture entries pass. 770 slots hold a system texture record, 199 are null and 0 are invalid. Of the 678 name records with the `u64` at `+0x10` equal to `6`, the `u32` at `+0x18` matches a name hash in the 1,440 sampled dictionaries for 264 references (4 distinct hashes, 86 of 92 drawables, 404 candidate records, every candidate allocation in bounds) and not for 414. The other 92 name records have a system pointer at `+0x10` and no dictionary hash. Neither 32-bit half of the 64-bit key at name record `+0x08` matches a dictionary hash (0 of 770). A control of 10,000 random `u32` values yields no accepted slot reference and no dictionary-hash match | Payload bytes (`BINARY`, `CROSS_SAMPLE`); arithmetic and random control (`CROSS_SAMPLE`) | Confirmed (sample counts, namespace overlap, controls); Probable (slot bit split and the `+0x18` reading) | One drawable archive and one build; 1,440 dictionaries from two archives. The 414 unresolved references are not shown to be absent from every dictionary. The slot index equals the parameter position in all 969 cases, so an independent cross-reference is not demonstrated. No engine code was traced; names and hashes are not published |

### Not carried

- **RES-F07** read the primary sample as a probable texture dictionary. The name meaning and pixel format were not established, so the reading is speculative and was dropped. The dictionary grammar and its allocation arithmetic are now established as RES-F36–RES-F40; the pixel format remains undecoded.
- **RES-F08** stated that one type 5 row carries a RAGE resource payload with two streams. It is folded into RES-F01 and is not kept as a separate claim.
- **RES-F22** is withdrawn; the sample set behind the earlier pointer totals is not retained.

## Counters and negative results

- **No stored page slot is nonzero.** Rechecked maps agree.
- **No map has a nonzero byte outside its counts.** Rechecked samples agree.
- **No map lies outside the system pages.** Rechecked samples agree.
- **One declared page has no stored chunk.** A `textures.rpf` nested row at entry `0x1000` declares one system page and two graphics pages but stores two streams. The graphics page present is `0x420000` bytes. The current CLI reports `partial`. The archive row locator is not retained; the row is **Probable** (RES-F13).
- **No multi-page segment breaks the `0x10000` pattern.** 4,647 rechecked resources show no page-size violation.
- **No resource entry lacks the 16-byte zero header.** Rechecked rows agree.
- **No rechecked resource was stored with compression mode 1 or without a chunk table.**
- **Pointer-like values outside a segment occur.** Their number, not their position, is what makes them visible.
- **No texture dictionary had unequal hash and value counts.** 1,431 non-empty dictionaries agree; 9 empty dictionaries have both counts zero.
- **No texture-dictionary hash array was unsorted or repeated a value.** 1,431 of 1,431 agree.
- **No texture allocation left the graphics segment, overlapped another start or exceeded its gap.** 5,484 of 5,484 records agree.
- **No texture record had a zero dimension, a zero mip count or a mip count above the dimension limit.** 5,484 of 5,484 agree.
- **No drawable texture-parameter word failed the slot rule.** 969 of 969 texture entries resolve to an in-range slot; 7,920 non-texture entries do not match the texture class.
- **No reachable dictionary allocation was out of bounds.** 404 candidate records from 264 resolved drawable references are in bounds.
- **No 64-bit drawable texture key half matched a dictionary hash.** 0 of 770 lower halves and 0 of 770 upper halves; the key is a separate namespace.
- **A wider pointer base was not established.** Values with a pointer-shaped low half and a nonzero upper half were not counted as pointers; whether any is one is unknown.
- **No engine allocation or validation path was traced.** Page allocation, runtime page slots and engine-side pointer validation remain **Unknown**.

## Reproduction

The commands below reproduce the checks. `<GAME_ROOT>` is a local installation, `<WORK>` a scratch directory outside it, and `<EXECUTABLE>` the game executable that matches the archive, used only to authenticate its metadata.

```text
lforge archive extract <GAME_ROOT>/textures.rpf --row 1 --output <WORK>/tex-row1.rpf --executable <EXECUTABLE>
lforge archive extract <GAME_ROOT>/levels.rpf --row 2 --output <WORK>/tile.rpf --executable <EXECUTABLE>
lforge archive ls <WORK>/tile.rpf --executable <EXECUTABLE> --json
lforge archive resource <WORK>/tile.rpf 0x2EEB010 --json --no-cache
python tools/resources/rage_resource.py payload --file <WORK>/tex-row1.rpf --offset 0x1000 --length 576 --json
python tools/resources/rage_resource.py decoded --file <DECODED> --system-length 1888 --json
python tools/resources/page_reconstruct.py --file <WORK>/tile.rpf --offset 0x2EEB000 --length 47520 --logical-size 74304 --json
lforge archive extract <GAME_ROOT>/textures.rpf --row 18 --output <WORK>/txd18.rpf --executable <EXECUTABLE>
python tools/resources/texture_dictionary.py --file <WORK>/txd18.rpf --offset 0xE5C000 --length 26096 --logical-size 33168 --json
lforge archive extract <GAME_ROOT>/levels.rpf --row 5 --output <WORK>/draw5.rpf --executable <EXECUTABLE>
python tools/resources/pool_reference.py --file <WORK>/draw5.rpf --offset 0x330000 --length 2352 --logical-size 7840 --json
python -m unittest discover -s tools/resources -p "test_*.py"
```

The byte-level results come from the published parser and `page_reconstruct`, which do not use application code. The local CLI supplied the authenticated metadata and was used as a cross-check: the rechecked rows matched on page-map offset, page counts, segment sizes, page sizes, stream counts and pointer counts. That agreement is consistency, not independent evidence for the format.

`<WORK>/tile.rpf` is the nested archive at `<GAME_ROOT>/levels.rpf` row 2. The payload offsets `0x2EEB000` and `0x2EEB010` are the entry and the first stream for inner row 46; the stored-row digest is in [Sample locators](#sample-locators).

## Limits

- The samples rechecked for this index are the primary sample and the sample locators above. Other archives were not scanned.
- Four split-page rows are identified by payload offset and size in [pages.md](../../formats/resources/pages.md); their archive row locators are not retained.
- No engine code path was traced. Pointer validation, relocation, page-map semantics and page allocation are unknown.
- Payload bytes are outside the RPF9 metadata signature.
- The ASCII names below the page map are payload text. They are not included in this repository; only their count and record stride are recorded.
- A raw stored page was observed only in type 6 rows. Its identity as a page is supported by the page count, the logical size and the size pattern, not by engine code.
- The 0DRP root header and the records behind `+0x38` were read on three resources. The tiling population is type 73 only.
- The texture dictionary sample is a census of the type-5 rows in 25 nested archives of two top-level archives. The name text and hashes are payload data and are not published. Width, height, format id and mip count are supported by allocation arithmetic, not by pixel decoding.
- The drawable reference sample is one nested archive (`levels.rpf` row 5) and one build. The 264 resolved references cover 4 distinct name hashes; the 414 unresolved references are not shown to be absent from every dictionary.
- Archives other than `textures.rpf`, `data.rpf` and `levels.rpf` were not scanned for resources. `common.rpf` and `script.rpf` reported none; `shaders.rpf` was not scanned for resources.

## Next experiments

- Trace the resource loader in the executable for pointer validation and page allocation.
- Find a resource with a nonzero page slot, or a decrypted runtime page map, to establish the slot width.
- Find a resource stored as raw DEFLATE without a chunk table, to see whether the page layout survives without chunk sizes.
- Find or build a resource with a page of exactly 32 MiB to confirm the grouping rule.
- Check whether the absent page in an incomplete resource is empty or missing.
- Find the dictionaries that cover the 414 unresolved drawable texture hashes, and check whether the slot index can differ from the parameter position in another drawable.
- Check whether the 64-bit drawable texture key resolves in a different namespace or a resource other than a type-5 dictionary.
