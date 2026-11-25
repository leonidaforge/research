# RAGE resources

A RAGE resource is serialized into two segments. Each segment is reconstructed from one or more chunks: zlib streams or, for a raw page, an uncompressed range. This section documents the reconstructed layout.

Everything here comes from payload data of the Scarlett build. No engine code path for resource loading, validation or page allocation was traced. Structural facts are sample-verified; segment names follow RAGE convention and are **Probable**, not recovered symbols. Findings are cited as `RES-F01` and listed in [evidence/resources/INDEX.md](../../evidence/resources/INDEX.md).

## Status

| Part                                                                | Status                                                                     |
| ------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| Stored entry: 16 zero bytes, then one chunk per page, except a split page | Confirmed in rechecked rows and the reported survey (RES-F10, RES-F24)     |
| A chunk is a zlib stream or a raw (uncompressed) page               | Confirmed for the type 6 rows; see [pages.md](pages.md#raw-stored-page) (RES-F24) |
| Segment order: system segment first, then graphics segment          | Confirmed in rechecked rows and the reported survey (RES-F01, RES-F11)     |
| Resource header: zero `u64`, system pointer to the page map at `+8` | Confirmed in rechecked rows and the reported survey (RES-F11)              |
| Pointer values: 4-bit segment selector, 28-bit offset               | Confirmed (RES-F16). A 16-bit split is rejected by offsets above `0xFFFF`  |
| Pointer count and bounds                                            | Confirmed in rechecked rows and the reported survey (RES-F02, RES-F17, RES-F18) |
| Page-map location and count bytes                                   | Confirmed (RES-F12)                                                        |
| Page-map length and zero slots                                      | Probable. `16 + 8 * pages` fits; slots are always zero as stored (RES-F12)  |
| Page sizes and the `0x10000` unit                                   | Confirmed for the samples, Probable as a rule (RES-F14, RES-F28)           |
| Split pages at 32 MiB                                               | Confirmed, four instances (RES-F15)                                        |
| A stream is one page except a split page; a raw page is not a stream | Tested scope in [pages.md](pages.md#page-and-stream-relation) (RES-F27)   |
| 0DRP root header at `+0x10..+0x4F`                                 | Confirmed fields for one type 11, 73 and 74 resource (RES-F29, RES-F30)    |
| Block table: 16-byte entries at the `+0x38` pointer                | Confirmed for the same three resources (RES-F31)                           |
| Header field meanings beyond the page-map pointer                   | Unknown                                                                    |
| Types 2, 4, 5 and 11 follow the same layout                         | Confirmed for the reported 1,466 authenticated rows; Probable for the rest (RES-F20) |

## Model

A reconstructed resource has two segments:

- A **system segment**, prefix `0x5000…`. It holds the resource header, pointer-bearing fields and a page map. RAGE convention calls it the system segment. The older name in this repository was "metadata segment".
- A **graphics segment**, prefix `0x6000…`. It holds the payload bytes that pointers address. RAGE convention calls it the graphics segment. The older name was "data segment".

Both are addressed by 32-bit values. A value whose bits 28..31 are `5` selects the system segment and `6` the graphics segment; bits 27..0 are an offset inside the reconstructed segment (RES-F16).

| Segment  | Stored bytes in the primary sample | Reconstructed bytes | Prefix |
| -------- | ---------------------------------- | ------------------- | ------ |
| System   | 395                                | 1,888               | `0x5…` |
| Graphics | 146                                | 49,152              | `0x6…` |

The resource as a whole is the segments reassembled in that order. A reader MUST NOT treat the stored stream bytes as the resource.

Documents:

- [pages.md](pages.md): stored entry, segment split, page map, page sizes, raw pages and reconstruction.
- [pointers.md](pointers.md): pointer encoding, bounds and false positives.
- Evidence: [evidence/resources/INDEX.md](../../evidence/resources/INDEX.md).

## 0DRP root header

Some resources carry the four bytes `0DRP` at system `+0x10` (RES-F21). The candidate layout at `+0x10..+0x4F` was read on one type 11, one type 73 and one type 74 resource (RES-F29). Offsets are from the start of the system segment.

| Offset | Width | Observed content                                   | Status                    |
| ------ | ----- | -------------------------------------------------- | ------------------------- |
| `+0x10` | 4     | `0DRP`                                             | Confirmed (samples)       |
| `+0x14` | 1     | `0x7A`                                             | Confirmed (samples)       |
| `+0x18` | 8     | zero                                               | Confirmed (samples)       |
| `+0x20` | 8     | `1`, `1`, `2` for the type 73, 73 and 74 samples   | Unknown; varies by row    |
| `+0x28` | 8     | system pointer                                     | Confirmed (samples)       |
| `+0x30` | 8     | system pointer, or zero                            | Confirmed (samples)       |
| `+0x38` | 8     | system pointer to the block table                  | Confirmed (samples)       |
| `+0x40` | 8     | system pointer, or zero                            | Confirmed (samples)       |
| `+0x48` | 2 × 4 | four `u16` counts                                  | Confirmed bytes; meanings **Unknown** |
| `+0x50` | 8     | system pointer, or zero                            | Not in the candidate; observed in the type 73 and 74 samples |

- Every nonzero pointer above resolved inside the system segment in the three samples; no out-of-bounds or cross-page pointer was found (RES-F30). The page-map pointer at `+0x08` is also a system pointer.
- Across the three families, the tag, the version byte, the zero at `+0x18`, the pointer positions and the four `u16` positions hold. The `+0x20` word and the values of the four `u16` differ between the samples. The 16-byte block width also holds.
- The four `u16` values were `2/2/2/0` for the type 11 sample, `13/2/5/1` for type 73 and `4/3/5/32` for type 74. The third value equals the number of block entries in each sample. The other three are **Unknown**.
- The field positions are validated on these three resources; the individual values are not a rule.
- The tag, version and `+0x18` zero are not required by the page model. A reader MUST NOT require `0DRP` to reconstruct pages.

## Block tables

The pointer at `+0x38` names a table of 16-byte entries in the system segment (RES-F31):

| Offset | Width | Observed content                                          |
| ------ | ----- | --------------------------------------------------------- |
| `+0`   | 4     | identifier or hash                                        |
| `+4`   | 4     | size in bytes                                             |
| `+8`   | 8     | pointer; the segment selects the addressed segment        |

- The width is 16 bytes for the type 11, 73 and 74 samples. The table length is the third `u16` count times 16.
- The table need not end at the page map. In the type 74 sample the table ends at `0x15A00`, a block fills `0x15A00..0x15A50`, and the page map starts at `0x15A50`.
- Entries address byte ranges, not pages. The pointer selects the system or graphics segment and the size bounds the range. A page can contain several blocks; a block can equal the page when the page contains one block (RES-F33).
- A block range can cross the `0x10000` unit boundary. In the type 74 sample a system block spans `0xBCB0..0x146D0`, across the boundary between its two system pages. The block table therefore cannot be used to derive page boundaries (RES-F34).
- In a type 73 sample, five entries cover three system ranges and two graphics ranges. The graphics ranges `0..0x810` and `0x810..0x860` tile the `0x860`-byte graphics page exactly.
- In 4,426 type 73 resources with a declared graphics page and at least one graphics block, graphics blocks tile the page exactly in 2,864; 606 leave an uncovered remainder; 464 have an internal gap; 492 address outside the reconstructed graphics extent (in the examples the declared page has no stored stream); no overlap was found. The sample is 12 instance-placement nested archives (RES-F32).

## Limits

- The reported survey covers 3,026 reconstructed resources from two archive families and four type IDs, of which 1,466 rows were authenticated. The counts come from the source survey and were not re-counted in this consolidation; representative samples were rechecked with the current CLI and parser.
- Other archives, especially very large resources, were not scanned for this consolidation.
- The page sizes and the 32 MiB split are observations. No engine code that allocates or validates pages was traced. Page allocation and runtime validation remain **Unknown**.
- The page slots are zero in every stored resource. Their runtime content and the exact slot width cannot be checked from data.
- One resource declares one page more than the payload stores. Whether that page is missing or empty is not established.
- A page of exactly 32 MiB cannot be distinguished from a split page by stream length alone.
- A stored page can be raw (not a zlib stream). A reader that only finds zlib streams loses that page; the current CLI reports `partial` for such a row although the bytes are present (RES-F24, RES-F25).
- No packed page, one stream covering two declared pages, was observed. The packing rule is untested (RES-F27).
- The 0DRP root header and block table were read on three resources. The counts, the pointer targets beyond their bounds and the `+0x20` word are not established as general semantics (RES-F29, RES-F30, RES-F31).
- The block-tiling population is type 73 only. Type 11 and type 74 samples are too few to state a tiling rule.
- The primary sample's ASCII names below the page map are resource data, not archive paths. They are payload text and are not reproduced here.
- Payload bytes are not authenticated by the RPF9 metadata signature. A structurally valid resource does not prove untampered content.

## Terms

| Term             | Meaning                                                                | Confidence                              |
| ---------------- | ---------------------------------------------------------------------- | --------------------------------------- |
| system segment   | Segment at prefix `0x5`; holds the header and pointers                 | Probable (RAGE convention)              |
| graphics segment | Segment at prefix `0x6`; holds addressed data                          | Probable (RAGE convention)              |
| page map         | Structure at the system offset named by `+0x08`                        | Confirmed (location), Probable (extent) |
| page             | A unit counted by the page map, reconstructed from one or more zlib streams or from one raw chunk | Confirmed (count), Probable (size rule) |
| stream           | One zlib unit that reconstructs all or part of a page                  | Confirmed                               |
| raw page         | One stored chunk with no zlib header whose stored and reconstructed lengths are equal | Confirmed (bytes), Probable (page identity) |

A reader SHOULD keep the numeric prefixes and not depend on these names.
