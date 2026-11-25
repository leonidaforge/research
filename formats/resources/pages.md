# Resource pages

A resource is stored as a sequence of compressed streams and reconstructed into two segments, each made of pages. This document describes the stored entry, the page map and the page-size observations. Pointer values are in [pointers.md](pointers.md). Findings are cited as `RES-F01` and listed in [evidence/resources/INDEX.md](../../evidence/resources/INDEX.md).

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
| `+0x00` | 16 zero bytes                                                         | Confirmed in rechecked rows and the survey (RES-F10) |
| `+0x10` | One zlib stream per chunk, 16-byte aligned, zero fill between streams | Confirmed (RES-F10, RES-F19)                  |

- In the reported 1,466 authenticated rows the location record's stored range starts at the 16-byte header, and the first stream starts 16 bytes later.
- The number of stored zlib streams equals the RPF9 chunk count, and the inflated lengths sum to the row's logical size in those rows. One stream is one chunk (RES-F10).
- Every resource row in the reported survey used compression mode 0 with chunk encoding 2. A resource stored as raw DEFLATE (mode 1) or with another encoding would lose the chunk sizes that the page layout depends on; whether such a resource exists is **Unknown** (RES-F10).
- The 64 KiB stream rule in [RPF9 payloads](../containers/rpf9/payloads.md) describes the generic encoding-3 path. It does not describe these rows: an encoding-2 chunk can reconstruct a whole page of several megabytes, which is why one stream is one page unless the page is split at 32 MiB.
- The 16 bytes are not part of the decoded payload. Their meaning is **Unknown**.

In the primary sample: 16 prefix bytes + 395 + 5 fill + 146 + 14 fill = 576 bytes.

## Reassembly

The system stream reconstructs first. Its bytes `0x00` to `0x75F` are the system segment. The graphics stream follows and forms the graphics segment `0x00` to `0xBFFF`. Pointer values in the system segment address both segments.

The stored offset of each stream is not part of this model. A reader obtains it from the RPF9 row's location record or chunk table, or from scan recovery.

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

Values in 64-bit slots have a zero upper half in this sample and in the survey. Whether the upper half carries flags for other resources is **Unknown** (RES-F09).

The header is not uniform across all resources:

- 38 rows carry the four bytes `0DRP` at `+0x10..+0x13` and the byte `0x7a` at `+0x14`, with zero at `+0x18` (RES-F21).
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

The declared counts match the page groups derived from the chunk sizes in every complete resource of the reported survey. Across the reported 1,466 authenticated rows:

| System pages | Graphics pages | Resources |
| ------------ | -------------- | --------- |
| 1            | 0              | 47        |
| 1            | 1              | 1,378     |
| 1            | 2              | 34        |
| 2            | 0              | 0         |
| 2            | 1              | 2         |
| 2            | 2              | 5         |

These counts are from the source survey and were not re-counted in this consolidation. Counts are one byte each, so a segment can declare up to 255 pages. The largest observed counts are 2 and 2 (RES-F12).

### Counterexample: a declared page with no stored chunk

One resource declares one system page and two graphics pages but stores two streams. The current CLI reports status `partial` and `1 of 2 graphics pages found`. The graphics page present is `0x420000` bytes, a multiple of `0x10000`, consistent with a missing last page. Whether the absent page is missing or empty is not established (RES-F13).

## Page sizes

Page sizes are not stored as lengths. They follow from the chunk sizes.

- **Unit.** In a segment with more than one page, every page except the last is a multiple of `0x10000` and the last is at most `0x10000`. The reported survey counted 965 multi-page segments without exception (RES-F14). A single-page segment is not constrained: the primary sample has 1,888 and 49,152 bytes.
- **Split pages.** A page larger than 32 MiB is stored as consecutive chunks. Every chunk but the last of a split page inflates to exactly `0x2000000` (32 MiB). Four split pages were rechecked with the current CLI, with tails of `0x200000` (2 MiB), `0x170000` (1.5 MiB) and `0x600000` (6 MiB, twice) (RES-F15).

  `0x200000` (2 MiB) is not a split length. The 2 MiB stream in the survey is the tail of a 35,651,584-byte page whose first stream is `0x2000000`.

- **Grouping.** A reader with the stream lengths and the page count:
  1. merges a stream of exactly `0x2000000` into the next one;
  2. uses that grouping if it yields the declared page count;
  3. otherwise, if the number of streams equals the page count, treats every stream as one page;
  4. otherwise reports an ambiguous layout.

  Rule 3 handles a page of exactly 32 MiB, which stream length alone cannot distinguish from a split page. No such page was observed.

## Survey observations

The rechecked samples below come from nested archives of the `textures.rpf` and `data.rpf` families. They are structural checks, not a re-run of the full survey.

| Sample                        | Payload   | Map       | System pages | Graphics pages | System bytes | Graphics bytes | Split pages |
| ----------------------------- | --------- | --------- | ------------ | -------------- | ------------ | -------------- | ----------- |
| primary sample                | `0x1000`  | `0x610`   | 1            | 1              | 1,888        | 49,152         | 0           |
| map in the second system page | `0x7000`  | `0x988E0` | 2            | 1              | 625,472      | 196,608        | 0           |
| split graphics page           | `0x9A0000` | `0x2E20`  | 1            | 1              | 11,840       | 35,651,584     | 1           |
| split graphics page           | `0x1000`   | `0x41C0`  | 1            | 2              | 20,960       | 35,090,432     | 1           |
| split graphics page           | `0x87C000` | `0xD10`   | 1            | 2              | 4,288        | 39,862,272     | 1           |
| split graphics page           | `0xC26000` | `0xCF0`   | 1            | 1              | 3,344        | 39,845,888     | 1           |
| system only                   | `0x8000`  | `0x10A0`  | 1            | 0              | 4,688        | 0              | 0           |

The map in the second system page and system pointers above `0x20000` in that resource show that offsets address the concatenated segment (RES-F17).

## Reader requirements

A reader that decodes a resource from its stored entry SHOULD:

- require the 16-byte header to be zero, one zlib stream per chunk, and zero fill between streams;
- require the first system page to start with the resource header of the table above;
- bound the page map by the system data, reject nonzero bytes outside the counts, reject a zero system-page count and reject a map outside the declared system pages;
- require the declared page count to match the derived page groups, and report missing pages instead of inventing sizes;
- require the page-size pattern for multi-page segments, and report an ambiguous split instead of choosing silently;
- treat pointer-like values outside a segment as warnings ([pointers.md](pointers.md#false-positives));
- report every failure instead of returning partial data as complete.

The published [parser](../../tools/resources/README.md) implements these rules and builds synthetic negative cases for each of them.

## Open questions

- The meaning of the 16-byte entry header, the `0DRP` marker and the `u64` at `+0x18`.
- The runtime content of the page slots. No stored resource has a nonzero slot, so the slot width and its per-page value cannot be checked from data.
- Whether a resource can be stored as raw DEFLATE without a chunk table. No such resource was observed.
- Whether a page of exactly 32 MiB exists, and how it is distinguished from a split page.
- Whether the absent page in the incomplete resource is missing data or an empty page.
- The page-size rule is an observation. No engine code that allocates or validates pages was traced; page allocation remains **Unknown**.
