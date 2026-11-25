# Resource pages

A resource is stored as a sequence of chunks and reconstructed into two segments, each made of pages. A chunk is a zlib stream or a raw, uncompressed page. This document describes the stored entry, the page map, the page-size observations and the reconstruction rule. Pointer values are in [pointers.md](pointers.md). Findings are cited as `RES-F01` and listed in [evidence/resources/INDEX.md](../../evidence/resources/INDEX.md).

## Primary sample

| Property        | Value                                                                                  |
| --------------- | -------------------------------------------------------------------------------------- |
| Source          | row 0 of a nested archive extracted from `textures.rpf` row 1, Scarlett build e95020b2 |
| Row type ID     | 5                                                                                      |
| Entry           | payload offset `0x1000`, stored size 576 bytes, logical size 51,040 bytes              |
| Chunks          | chunk encoding 2, chunk count 2                                                        |
| System stream   | stored 395 bytes at `0x1010`, reconstructed 1,888                                      |
| Graphics stream | stored 146 bytes at `0x11A0`, reconstructed 49,152                                     |

The row's logical size is the sum of the two reconstructed sizes. Both streams start with the zlib header `78 DA`. Each reconstructs to exactly its logical size (RES-F01).

The current CLI reports the same sizes, page counts and pointer counts for this row. Its page map is at system offset `0x610` and declares one system page and one graphics page.

## Stored entry

| Offset  | Content                                                               | Confidence                                    |
| ------- | --------------------------------------------------------------------- | --------------------------------------------- |
| `+0x00` | 16 zero bytes                                                         | Confirmed in rechecked rows (RES-F10) |
| `+0x10` | One chunk per page, except a split page's several streams; 16-byte aligned, zero fill between chunks | Confirmed (RES-F10, RES-F19, RES-F24) |

- In every rechecked resource row the location record's stored range starts at the 16-byte header, and the first chunk starts 16 bytes later.
- In those rows the number of stored zlib streams equals the RPF9 chunk count, and the inflated lengths sum to the row's logical size. One zlib stream is one chunk (RES-F10).
- Every rechecked resource row used compression mode 0 with chunk encoding 2. A resource stored as raw DEFLATE (mode 1) or with another encoding would lose the chunk sizes that the page layout depends on; whether such a resource exists is **Unknown** (RES-F10).
- The 64 KiB stream rule in [RPF9 payloads](../containers/rpf9/payloads.md) describes the generic encoding-3 path. It does not describe these rows: an encoding-2 chunk can reconstruct a whole page of several megabytes, which is why one zlib stream is one page unless the page is split at 32 MiB.
- A chunk can be a raw page instead of a zlib stream. The chunk starts with no zlib header, its stored length equals its reconstructed length, and its bytes are part of the row's logical size. The type 6 rows in [Raw stored page](#raw-stored-page) are the observed instance (RES-F24).
- The 16 bytes are not part of the decoded payload. Their meaning is **Unknown**.

In the primary sample: 16 prefix bytes + 395 + 5 fill + 146 + 14 fill = 576 bytes.

## Reassembly

The first chunk reconstructs into the first system page. Later chunks continue the system pages, then the graphics pages. The reconstructed system segment is the concatenation of the system pages; the graphics segment follows. Pointer values in the system segment address both segments.

The stored offset of each chunk is not part of this model. A reader obtains it from the RPF9 row's location record or chunk table, or from scan recovery.

## Reconstruction rule

A reader MUST reconstruct every page the page map declares. A readable page map does not end reconstruction, and a zlib stream count does not bound the page count.

1. Read the 16-byte zero prefix and every chunk it is followed by. A chunk is a zlib stream if it starts with a valid zlib header and inflates; otherwise it is a raw stored range.
2. Reconstruct the page map from the system bytes. The map may lie in a later system page, so it becomes readable only after enough pages are present.
3. Group zlib streams into pages. A stream of exactly `0x2000000` bytes continues the previous page; every other zlib stream starts a page (RES-F15).
4. Treat a raw stored range after the last zlib stream as the last declared page only when the declared page count and, when known, the declared logical size require it. A zlib-like header that does not inflate is a note, not a classification. An all-zero range is a page when the count and logical size require it. If the declared pages are already present, the same range is trailing data and MUST NOT be counted as a page (RES-F24, RES-F27).
5. If one zlib stream spans several declared pages, split it only when the declared count and the `0x10000` size pattern force the split. Mark the pages packed; no packed page was observed (RES-F27).
6. Report `partial` only when a declared page is genuinely absent from the stored row. A page present as a raw range is not absent.

## Page and stream relation

- In the 625,472-byte sample, 3 streams reconstruct 3 pages: `0x90000`, `0x8B40` and `0x30000` bytes. One stream is one page (RES-F28).
- A split page is the exception: a page larger than 32 MiB uses several streams, each of `0x2000000` bytes except the last (RES-F15).
- A raw page is not a stream. It is one chunk whose stored and reconstructed lengths are equal (RES-F24).
- No packed page was observed. The statement "a stream is one page" is therefore tested for zlib pages up to the split length and for raw pages, but not for a stream that covers two declared pages (RES-F27).

## Raw stored page

The representative type 6 resource has these properties (RES-F24):

| Quantity                     | Value                                              |
| ---------------------------- | -------------------------------------------------- |
| Declared page counts         | 2 system, 0 graphics                               |
| Page map offset              | `0xFD60`, inside the first system page             |
| First chunk                  | zlib, stored 38,734, reconstructed 65,536          |
| Last chunk                   | raw, stored 8,768, reconstructed 8,768             |
| Logical system segment       | 74,304 bytes                                       |
| Reconstructed by the CLI     | 65,536 bytes, status `partial`                     |

The stored row is 47,520 bytes: 16 prefix + 38,734 stored zlib + 2 fill + 8,768 raw. The same terrain-tile archive holds five type 6 rows with a raw last system page; each declares 2 system pages and 0 graphics pages (RES-F24):

| Inner row | First page (zlib) | Raw last page | Logical system | Page map |
| --------- | ----------------- | ------------- | -------------- | -------- |
| 46        | 65,536            | 8,768         | 74,304         | `0xFD60` |
| 62        | 65,536            | 4,464         | 70,000         | `0xFF70` |
| 89        | 131,072           | 16,288        | 147,360        | `0x1FF30` |
| 112       | 65,536            | 8,304         | 73,840         | `0xF5A0` |
| 139       | 131,072           | 14,176        | 145,248        | `0x1E900` |

Three more type 6 rows in other terrain tiles store an 8,768-byte raw last page, with page maps at `0xF7D0`, `0xFA80` and `0xF2A0`. The raw page sizes measured in the representative tile are 8,768, 4,464, 16,288, 8,304 and 14,176 bytes. These rows are listed with stored-row digests in [Sample locators](../../evidence/resources/INDEX.md#sample-locators).

The last chunk is a page, not padding, for these reasons:

- its bytes are not a valid zlib stream; in these rows they are non-zero;
- its stored length equals the difference between the row's logical size and the reconstructed first page;
- the declared system page count is one higher than the zlib page count;
- the page-size pattern places it as the last page of the system segment.

Alternatives eliminated by these observations:

| Alternative                     | Discriminating observation                                                                 |
| ------------------------------- | ------------------------------------------------------------------------------------------ |
| continuation of a split stream  | the first zlib stream ends at 65,536 bytes, not at the 32 MiB split length; the raw bytes are a new chunk |
| residual or padding tail        | in these rows the raw length is non-zero and equals the logical remainder; it is not zero fill |
| a separate stored range         | the row's chunk count is 2 and its stored size includes the raw bytes; no second entry exists |
| an artefact of chunk grouping   | the metadata chunk count and the stored-size arithmetic both account for the raw chunk      |
| a page-size interpretation error | the raw length 8,768 is at most `0x10000`, as the model requires for a last page            |

The remaining interpretation is a raw stored page. Whether the engine copies a raw range directly into the page or treats it as a page with a different transport is **Unknown**; no engine code was traced.

The current CLI reports `system_size` 65,536, status `partial` and "1 of 2 system pages found" for the representative. It finds only zlib streams, so it never sees the raw page (RES-F25).

### Rule check

The rule was run over 4,647 resources from 12 instance-placement nested archives. It reconstructs all 4,647 as complete: 9,041 zlib pages and 496 raw pages, with no packed page and no missing page. The packed split was not needed. The CLI reports `partial` for many of the same rows. This is the largest sample checked; it is not a census of every archive (RES-F35).

The raw page sizes measured in the representative tile are 8,768, 4,464, 16,288, 8,304 and 14,176 bytes. A packed page was not observed in the sample; the synthetic fixture is its only test (RES-F27).

## System segment

The first 0x60 bytes of the reconstructed system segment of the primary sample, as 64-bit little-endian slots:

| Offset  | Value                | Interpretation                                                   |
| ------- | -------------------- | ---------------------------------------------------------------- |
| `+0x00` | `0x0000000000000000` | Unknown                                                          |
| `+0x08` | `0x0000000050000610` | Pointer to the page map                                          |
| `+0x10` | `0x0000000000000000` | Unknown                                                          |
| `+0x18` | `0x0000000000000001` | Unknown                                                          |
| `+0x20` | `0x00000000500005E0` | Pointer; the target was not interpreted                          |
| `+0x28` | `0x00000000000C000C` | Two `u16` values, both 12                                        |
| `+0x30` | `0x0000000050000580` | Pointer to a 12-entry array of `0x5000` pointers                 |
| `+0x38` | `0x00000000000C000C` | Two `u16` values, both 12                                        |
| `+0x40` | `0x0000000000000000` | Unknown                                                          |
| `+0x48` | `0x0008000800000200` | Unknown; `u16` fields are `0x0200`, `0x0000`, `0x0008`, `0x0008` |
| `+0x50` | `0x0000000000000980` | Unknown                                                          |
| `+0x58` | `0x0000000060000000` | Pointer to the start of the graphics segment                     |

Only the page-map pointer and the graphics-segment pointer are interpreted. The repeated `0x0C` counts pair with the 12-entry pointer array, which fits a `{pointer, count}` descriptor. That reading is **Probable**; the field meanings are **Unknown** (RES-F05).

Values in 64-bit slots have a zero upper half in this sample and in the rechecked rows. Whether the upper half carries flags for other resources is **Unknown** (RES-F09).

The header is not uniform across all resources:

- The rechecked 0DRP samples carry the four bytes `0DRP` at `+0x10..+0x13` and the byte `0x7a` at `+0x14`, with zero at `+0x18` (RES-F21).
- Other rows carry `0` or `1` at `+0x18`, depending on the type ID.

All offsets in this list are from the start of the system segment. A reader MUST NOT require the bytes at `+0x10` through `+0x17` to be zero.

## Page map

The pointer at system `+0x08` is `0x50000610`, inside the system segment. The bytes at that offset are:

| Offset from map | Bytes        | Interpretation                                         |
| --------------- | ------------ | ------------------------------------------------------ |
| `+0x00`         | 8 zero bytes | Unknown                                                |
| `+0x08`         | `01 01`      | System page count 1, graphics page count 1 (RES-F12)   |
| `+0x0A`         | 6 zero bytes | Unknown                                                |
| `+0x10`         | 8 zero bytes | Page slot 0                                            |
| `+0x18`         | 8 zero bytes | Page slot 1                                            |
| `+0x20`         | 8 zero bytes | Not part of the map under the `16 + 8 * pages` reading |
| `+0x28`         | ASCII        | First name starts here                                 |

The map length is `16 + 8 * (system pages + graphics pages)`; for this sample 32 bytes, ending at `0x630`. The first name starts at `0x638`, eight bytes later. The map is inside the system segment and its offset is a multiple of 8 and at least `0x40` (RES-F12).

The length and the 8-byte slot width are **Probable**. The slots are zero in every stored map, so their width cannot be observed directly; `16 + 8 * pages` is the reading that fits the observed maps and the six maps that end exactly at the system segment end.

The two count bytes are **page** counts, not stream counts. The one-sample reading could not separate the two because this resource has one page and one stream per segment. Other resources have two pages of one stream each, and split pages store one page as several streams (RES-F12, RES-F15). Six names follow the map; they are resource data and are unrelated to the counts.

Slots are zero in every stored map. Six maps end exactly at the end of the system segment, which pins the extent for those rows. The split between the 16-byte header and the 8-byte slots is not directly observable while the slots are zero (RES-F12).

## Graphics segment

The graphics stream reconstructs to 49,152 bytes. The 12 pointers in the system segment are `0x60000000`, `0x60001000`, …, `0x6000B000`: twelve 4 KiB-aligned targets that span the segment. They are addresses inside one 48 KiB graphics page, not page boundaries.

Each 4 KiB block begins with small header-like values whose meaning is **Unknown**, followed by data whose pixel format is **Unknown**.

The byte `0xAA` occurs in short runs: 24 bytes in six 4-byte runs in this segment. It is not a segment-wide fill (RES-F06).

## Page counts

The declared counts match the reconstructed page groups in every rechecked complete resource. A raw page counts as one page group. The rechecked samples cover 1/0 (type 11), 1/1 (primary and type 73), 2/0 (raw-page and type 74) and 2/1 (625,472-byte) page-count pairs. Counts are one byte each, so a segment can declare up to 255 pages.

## Page sizes

Page sizes are not stored as lengths. They follow from the reconstructed chunk sizes.

- **Unit, not page size.** In a segment with more than one page, every page except the last is a multiple of `0x10000` and the last is at most `0x10000`. The reconstruction tool reports no page-size violation in 4,647 rechecked resources (RES-F14). A single-page segment is not constrained: the primary sample has 1,888 and 49,152 bytes.
- **Pages larger than 64 KiB.** In the 625,472-byte sample the system pages are 589,824 (`0x90000`) and 35,648 (`0x8B40`) bytes; the graphics page is 196,608 (`0x30000`) bytes. The sample has 3 streams and 3 pages. A fixed 64 KiB page size is therefore refuted: the arithmetic is consistent with `0x10000` as the allocation multiple for every page but the last, not as the page size (RES-F28).
- **Split pages.** A page larger than 32 MiB is stored as consecutive chunks. Every chunk but the last of a split page reconstructs to exactly `0x2000000` (32 MiB). Four split-page rows are identified by payload offset and size in the rechecked samples table below; their tails are `0x200000` (2 MiB), `0x170000` (1.4375 MiB) and `0x600000` (6 MiB, twice). Their archive row locators are not retained (RES-F15).

  `0x200000` (2 MiB) is not a split length. The 2 MiB stream in the rechecked split-page sample is the tail of a 35,651,584-byte page whose first stream is `0x2000000`.

- **Grouping.** A reader with the chunk lengths and the page count:
  1. reconstructs every zlib stream and every raw chunk;
  2. merges a zlib stream of exactly `0x2000000` into the next one;
  3. treats a raw chunk as the last page only when the declared count requires it;
  4. uses the grouping if it yields the declared page count;
  5. otherwise, if the number of zlib streams equals the page count, treats every zlib stream as one page;
  6. otherwise reports an ambiguous layout.

  Step 5 handles a page of exactly 32 MiB, which stream length alone cannot distinguish from a split page. No such page was observed. A packed page is handled only by the arithmetic in step 5 of the reconstruction rule; no packed page was observed.

## Rechecked samples

The rechecked samples below come from the primary nested archive and from nested archives in `levels.rpf` and `data.rpf`. Each located row is identified in [Sample locators](../../evidence/resources/INDEX.md#sample-locators). The split-page and system-only rows are identified by payload offset and size; their archive row locators are not retained.

| Sample                        | Payload   | Map       | System pages | Graphics pages | System bytes | Graphics bytes | Split pages |
| ----------------------------- | --------- | --------- | ------------ | -------------- | ------------ | -------------- | ----------- |
| primary sample                | `0x1000`  | `0x610`   | 1            | 1              | 1,888        | 49,152         | 0           |
| map in the second system page | `0x7000`  | `0x988E0` | 2            | 1              | 625,472      | 196,608        | 0           |
| raw last system page          | `0x2EEB000` | `0xFD60` | 2           | 0              | 74,304       | 0              | 0           |
| split graphics page           | `0x9A0000` | `0x2E20`  | 1            | 1              | 11,840       | 35,651,584     | 1           |
| split graphics page           | `0x1000`   | `0x41C0`  | 1            | 2              | 20,960       | 35,090,432     | 1           |
| split graphics page           | `0x87C000` | `0xD10`   | 1            | 2              | 4,288        | 39,862,272     | 1           |
| split graphics page           | `0xC26000` | `0xCF0`   | 1            | 1              | 3,344        | 39,845,888     | 1           |
| system only                   | `0x8000`  | `0x10A0`  | 1            | 0              | 4,688        | 0              | 0           |

The raw last system page is inner row 46 of the nested archive at `<GAME_ROOT>/levels.rpf` row 2; its stored-row digest is in [Sample locators](../../evidence/resources/INDEX.md#sample-locators). The 625,472-byte sample is inner row 1 of the nested archive at `<GAME_ROOT>/data.rpf` row 14; its 3 streams reconstruct to 589,824 + 35,648 + 196,608 bytes. The map in the second system page and system pointers above `0x20000` in that resource show that offsets address the concatenated segment (RES-F17).

## Reader requirements

A reader that decodes a resource from its stored entry SHOULD:

- require the 16-byte header to be zero, one chunk per page, and zero fill between chunks;
- accept a chunk that is a zlib stream or a raw page; a raw chunk has no zlib header and its stored length equals its reconstructed length;
- reconstruct every page the page map declares; a readable page map MUST NOT end reconstruction;
- require the first system page to start with the resource header of the table above;
- bound the page map by the reconstructed system data, reject nonzero bytes outside the counts, reject a zero system-page count and reject a map outside the declared system pages;
- use a raw last chunk as the last page only when the declared page count and logical size require it; otherwise report it as trailing data, not as a page. An all-zero chunk is valid when the count and logical size require it;
- require the declared page count to match the reconstructed pages, and report missing pages instead of inventing sizes;
- require the page-size pattern for multi-page segments, and report an ambiguous split instead of choosing silently;
- split a packed stream only when the declared count and the size pattern force it, and mark the result as untested;
- treat pointer-like values outside a segment as warnings ([pointers.md](pointers.md#false-positives));
- report every failure instead of returning partial data as complete.

The published [parser](../../tools/resources/README.md) implements the zlib page rules. [page_reconstruct.py](../../tools/resources/page_reconstruct.py) implements the corrected rule, including raw pages and packed-page detection, and does not invoke the CLI.

## Open questions

- The meaning of the 16-byte entry header, the `0DRP` marker and the `u64` at `+0x18`.
- The runtime content of the page slots. No stored resource has a nonzero slot, so the slot width and its per-page value cannot be checked from data.
- Whether a resource can be stored as raw DEFLATE without a chunk table. No such resource was observed.
- Whether a page of exactly 32 MiB exists, and how it is distinguished from a split page.
- Whether a packed page, one zlib stream covering two declared pages, exists outside the synthetic fixture. None was observed.
- Whether a raw stored page is copied directly or passes through another transport. No engine code was traced.
- The meanings of the four `u16` fields at `+0x48` and the `+0x20` word in the 0DRP root header.
- Whether the tiling result for the records behind `+0x38` extends beyond the sampled type 73 rows.
- The page-size rule is an observation. No engine code that allocates or validates pages was traced; page allocation remains **Unknown**.
