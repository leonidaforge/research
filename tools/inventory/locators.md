# Recorded sample locators

These are the locators behind the iteration 11 report for Workers B and E. They
are a recorded set, not a new measurement. `<GAME_ROOT>` is a local
installation, `<WORK>` a scratch directory outside it, and `<EXE>` the
recognized executable.

Identity: `lforge 0.1.0`, CLI SHA-256
`9b8f06d0022a6823a882e89e78fe469a77258e253768a6582ac60d6b8e624ecf`,
application revision `b0fcebb5c5b7720ef236752544df6da94a7e18c2`, recognized
executable SHA-256
`e95020b2fa4a721db3df59fdecf75621730ac559d8835252f6c3b658d5a08993`.

## Reproduction

```text
lforge archive extract <GAME_ROOT>/<TOP>.rpf --row <TOP_ROW> --output <WORK>/<NAME>.rpf --executable <EXE>
lforge archive manifest <WORK>/<NAME>.rpf --format jsonl --output <WORK>/<NAME>.jsonl --executable <EXE>
python tools/resources/page_reconstruct.py --file <WORK>/<NAME>.rpf --offset <PAYLOAD_OFFSET> --length <STORED_SIZE> --logical-size <LOGICAL_SIZE> --json
```

`page_reconstruct.py` reports `system_size`; the decoded bytes are the report's
chunks in order, with the first `system_size` bytes as the system segment.
`drawable_inspect.py` takes the decoded bytes and `--system-length`.

Each SHA-256 below is over the extracted archive bytes for an archive row, or
over the stored row bytes at the manifest's payload offset and stored size for
an inner row. A reader can verify a locator before interpreting it.

## Drawable parent archives

All four are type-0 rows of `<GAME_ROOT>/levels.rpf`.

| Top row | Stored bytes | Rows | Type 2 | Type 3 | SHA-256 |
| ---: | ---: | ---: | ---: | ---: | --- |
| 5 | 22,172,864 | 316 | 92 | 224 | `450B6A5A95578A31133F686AE5D1D8151B4C7A38197F039895311D44742DBC96` |
| 563 | 16,825,792 | 638 | 320 | 317 | `B86B4A68F6DE553A617D2740B71EDA916D623C80BFD287DA6BE59B79371CA78D` |
| 1,120 | 28,285,648 | 720 | 312 | 407 | `F93D66A304B9D1D6662567360C4F7D75D4CCADEB2C3A7ADCAC44D90E79E50391` |
| 1,845 | 18,676,720 | 592 | 304 | 288 | `1773D4905823A7896057475320E649D94C5955347BF554911A45CC81A9F0EAA8` |

All 316 rows of `levels.rpf` row 5 reconstruct `complete` with
`page_reconstruct.py`: 92 type 2 and 224 type 3. The 92 type-2 rows also report
`complete` with no issues from `drawable_inspect.py`.

Selected type-2 inner rows of `levels.rpf` row 5:

| Inner row | Type | Stored | System | Graphics | LOD slots | Geometries | Shaders | Stored row SHA-256 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 158 | 2 | 31,968 | 20,480 | 64,288 | 4 | 16 | 4 | `6245318CDDBC3326B854C937ED2A85D1228421B36CB9E22B429E12F305FE12AE` |
| 64 | 2 | 10,480 | 20,160 | 17,808 | 3 | 11 | 6 | `FDB315E973A89131BAA3EFAB4741E162A68563AA36F34F2809A399C7637DE59C` |
| 90 | 2 | 9,696 | 17,552 | 17,504 | 3 | 12 | 4 | `DFDBF5A8832337E501D9D01F5FD3977E90ADFB4E876FA846EBEDA7E51F91DE96` |
| 193 | 2 | 95,568 | 21,104 | 156,928 | 3 | 12 | 4 | `7D99E1386AF6D9D0F696CE867C19BCD83B48ECE91F6CA0408210D17A8ED13ED2` |
| 303 | 2 | 7,472 | 16,576 | 15,168 | 3 | 12 | 4 | `5F83A8C872BA9C2F00B7B2597E13F21C81A6C5D8C38CA6E4F11A9D162C5999EC` |
| 25 | 2 | 10,784 | 15,584 | 17,392 | 3 | 9 | 4 | `A148912BB8EE9E92DD5A2F1AE40D93684C1EAA8B6CD699961D9FD0A16244C3DC` |
| 289 | 2 | 1,402,000 | 24,048 | 2,378,768 | 2 | 8 | 6 | `BAF7EBBD84E7AB6A01AC48581805B11AA3EEEB7533E38B55C6C873F026DA3D56` |
| 6 | 2 | 60,032 | 15,728 | 205,568 | 4 | 8 | 4 | `B2FEB35EFE186D418EF7FD02C320B52DBBD7712C232D6029AB4B57D7D8EF6AD7` |

`levels.rpf` row 563, inner row 400, reconstructs to 75,744 system and 682,784
graphics bytes with four populated LOD slots (16 + 16 + 16 + 12 geometries) and
16 shaders. Inner row 488 has four populated LOD slots, 10 geometries and 3
shaders. Type-3 rows reconstruct but were not validated as drawables.

## Texture-dictionary candidates

The parent rows are type-0 rows of `<GAME_ROOT>/textures.rpf`. Every listed
archive row holds only type-5 rows; all 1,365 type-5 rows in the set reconstruct
`complete`.

| Top row | SHA-256 | Stored bytes | Rows | Type 5 |
| ---: | --- | ---: | ---: | ---: |
| 0 | `264DC0118E50729EB4348516075FFAFE06B9BF0DDCA1604244153B27231C16EF` | 784,176 | 1 | 1 |
| 1 | `FBE052831C9E2734CCF03C3D30083528988D2766F36E9A7E29C7FA7C293056E8` | 4,720 | 1 | 1 |
| 2 | `79E374AB174EC4BF967661F970BCFD698F998F101955993B5FBDB1CE17C07236` | 274,720 | 1 | 1 |
| 3 | `7D2F107656111723F0ABC973E00A4B3B958386D14A2A258D06836C11681A229D` | 1,159,648 | 5 | 5 |
| 4 | `CDD5284C255D8919A061CC6B63FC7F14C3DDE1BA3FFD451DED2A5E0A69153B37` | 412,848 | 1 | 1 |
| 5 | `9FB2811D9D7A3EC090B41A231007F5F7D3CB073BA0AF2AA949EC05BA4B14D24D` | 28,736 | 1 | 1 |
| 6 | `3B61AE08FE0791FBB930D55A731DDCB067D5E5B8991A0D17646346F4E084904E` | 6,592 | 1 | 1 |
| 7 | `D2DFC515461884BE1E45815DDFDD62E15BD8E688F3649442156DE51959060E58` | 13,327,488 | 6 | 6 |
| 8 | `033840AFA71424F56BCDE82EBDD13D6E63C916F9B4785A165520A9EDF74F9513` | 19,154,192 | 1 | 1 |
| 9 | `7F6311F368B2E3AE4C65440C97530B1DA84AA335D7D246B8503A092BF207B3E9` | 84,967,808 | 9 | 9 |
| 10 | `7E99A2C5D61BC8037E3F6692664D7B19B668989ED79C3A1A6923F9C5BD4116C1` | 57,472 | 3 | 3 |
| 11 | `0AF933A3B5E5322D3617B9B67F28BFDFB298B0752D575D4C166DBD7E43C007C3` | 33,753,360 | 9 | 9 |
| 12 | `31CFE051783D8B87687FC832A5214B973F0F438DED46582B9849986D01BAB3E6` | 2,728,720 | 1 | 1 |
| 13 | `ACD879C622651C0586E439073EBD734F74EA56185546CDBB1F21F9D8D2E02CAA` | 2,626,064 | 1 | 1 |
| 14 | `EB24B2D2C27BF49429F0F2141080C78D6E0CEEFEA585C37A54AB1B2FEE9ABA6D` | 3,280,944 | 1 | 1 |
| 15 | `63EEF013AF43A456B44E09761AB59BB496D2BF400E7C2435765E9A3C5E8FC0C3` | 1,575,952 | 1 | 1 |
| 16 | `05CDE8C940297889AFC9FC12A51BA79F004AE9319D0CBD330A97E162ACEF9969` | 4,159,856 | 3 | 3 |
| 17 | `D164F9A77C6EE0FB24E807C0D5E350E9363188E4F9D3247C1DD513674E96EAEB` | 2,249,840 | 1 | 1 |
| 18 | `DA78B9BB7944815BFA3675C9EE57C2FBF02AC6BB15FCE66FFD123983851F930A` | 20,926,720 | 1,315 | 1,315 |
| 19 | `1C32832BF4227C0735C9BC6CD11F49F95E940B16C0724D6C0F16741179FD2E35` | 90,960 | 3 | 3 |

Selected type-5 inner rows. `Records` is the `u16` at system `+0x28`;
`Identifiers` counts printable runs of at least three bytes after the page map;
`Graphics pointers` counts values with selector 6 in the system segment.

| Archive key | Inner row | Stored | System | Graphics | Pages | Records | Identifiers | Graphics ptrs | Stored row SHA-256 |
| --- | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | --- |
| row 1 | 0 | 576 | 1,888 | 49,152 | 1/1 | 12 | 12 | 12 | `F83B14F1D2B441DE80CFE082DDB94BD19B96983E3D00C14AADDFF1B1088CAD46` |
| row 3 | 3 | 1,108,480 | 192,240 | 5,353,472 | 2/2 | 1,198 | 1,152 | 1,272 | `ABDE52518258DB8F8B5B197C59FF031DFEC73BD505EE3D300546E8F81453E3A5` |
| row 8 | 0 | 19,150,048 | 20,960 | 35,090,432 | 1/2 | 134 | 131 | 144 | `9B71CE5B82B6D213E953F6B48E55F8827F7C5838E09AACEF06BC978CDCEF66AD` |
| row 10 | 2 | 24,208 | 7,136 | 266,240 | 1/2 | 46 | 46 | 50 | `5CE1F0D5EF233EE2D0C231CD9B32F3317B7A35E226431C40680F31037996EB9B` |
| row 11 | 6 | 3,838,640 | 4,288 | 39,862,272 | 1/2 | 26 | 25 | 31 | `7EFB8BA248D19C47E3BD694C46D6951B0D170A61707E0D65A3D806B32B801AC8` |
| row 7 | 3 | 3,270,720 | 6,720 | 20,316,160 | 1/1 | 43 | 38 | 49 | `471C6EDFD653DC5B0FFCA26387E3C2D68A8EBE994C27DE3F82DC0D198C658EC5` |
| row 3 | 0 | 8,528 | 2,656 | 90,112 | 1/2 | 16 | 15 | 19 | `FC5A5C3A031A7B9B95943E15F8AE69969082FC7D171C8C28D849EBBEAADB1E31` |

The `row 3` inner row 3 system segment has a pointer array at `+0x30` that ends
at `+0x20`, with equal `u16` record counts at `+0x28` and `+0x38`. A sorted array
of 1,198 distinct `u32` values follows the pointer array. Each record target has
a system pointer at `+0x18` selecting graphics and a system pointer at `+0x30`
to an identifier record (eight zero bytes, then the string). The graphics
pointers are 4 KiB aligned. No valid zlib stream was found in five checked
graphics segments; the `78 9C`/`78 DA` byte pairs there do not inflate.

## Drawable texture-slot statistics

| Parent | Type-2 rows | Slots | Bound | Keys | Distinct keys |
| --- | ---: | ---: | ---: | ---: | ---: |
| `levels.rpf` row 5 | 92 | 969 | 770 | 770 | 285 |
| `levels.rpf` row 563 | 320 | 3,447 | 3,019 | 3,019 | 200 |

All keys have between 56 and 64 significant bits; none is below 2^32, and the
top nibble is spread over all 16 values. This rules out an internal pointer
reading (selector 5 or 6 with a zero upper half) for the observed set.

Bounded negative: none of the 3,789 bound keys from these two parents has its
low 32 bits or its high 32 bits in the 1,198-value sorted array of
`textures.rpf` row 3 inner row 3. Other dictionaries were not tested.
