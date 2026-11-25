# RAGE resources

A RAGE resource is serialized into two segments. Each segment is reconstructed from one or more compressed streams. This section documents the reconstructed layout.

Everything here comes from payload data of the Scarlett build. No engine code path for resource loading, validation or page allocation was traced. Structural facts are sample-verified; segment names follow RAGE convention and are **Probable**, not recovered symbols. Findings are cited as `RES-F01` and listed in [evidence/resources/INDEX.md](../../evidence/resources/INDEX.md).

## Status

| Part                                                                | Status                                                                     |
| ------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| Stored entry: 16 zero bytes, then one zlib stream per chunk         | Confirmed in rechecked rows and the reported survey (RES-F10)              |
| Segment order: system segment first, then graphics segment          | Confirmed in rechecked rows and the reported survey (RES-F01, RES-F11)     |
| Resource header: zero `u64`, system pointer to the page map at `+8` | Confirmed in rechecked rows and the reported survey (RES-F11)              |
| Pointer values: 4-bit segment selector, 28-bit offset               | Confirmed (RES-F16). A 16-bit split is rejected by offsets above `0xFFFF`  |
| Pointer count and bounds                                            | Confirmed in rechecked rows and the reported survey (RES-F02, RES-F17, RES-F18) |
| Page-map location and count bytes                                   | Confirmed (RES-F12)                                                        |
| Page-map length and zero slots                                      | Probable. `16 + 8 * pages` fits; slots are always zero as stored (RES-F12)  |
| Page sizes and the `0x10000` unit                                   | Confirmed for the samples, Probable as a rule (RES-F14)                    |
| Split pages at 32 MiB                                               | Confirmed, four instances (RES-F15)                                        |
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

- [pages.md](pages.md): stored entry, segment split, page map, page sizes.
- [pointers.md](pointers.md): pointer encoding, bounds and false positives.
- Evidence: [evidence/resources/INDEX.md](../../evidence/resources/INDEX.md).

## Limits

- The reported survey covers 3,026 reconstructed resources from two archive families and four type IDs, of which 1,466 rows were authenticated. The counts come from the source survey and were not re-counted in this consolidation; representative samples were rechecked with the current CLI and parser.
- Other archives, especially very large resources, were not scanned for this consolidation.
- The page sizes and the 32 MiB split are observations. No engine code that allocates or validates pages was traced. Page allocation and runtime validation remain **Unknown**.
- The page slots are zero in every stored resource. Their runtime content and the exact slot width cannot be checked from data.
- One resource declares one page more than the payload stores. Whether that page is missing or empty is not established.
- A page of exactly 32 MiB cannot be distinguished from a split page by stream length alone.
- The primary sample's ASCII names below the page map are resource data, not archive paths. They are payload text and are not reproduced here.
- Payload bytes are not authenticated by the RPF9 metadata signature. A structurally valid resource does not prove untampered content.

## Terms

| Term             | Meaning                                                                | Confidence                              |
| ---------------- | ---------------------------------------------------------------------- | --------------------------------------- |
| system segment   | Segment at prefix `0x5`; holds the header and pointers                 | Probable (RAGE convention)              |
| graphics segment | Segment at prefix `0x6`; holds addressed data                          | Probable (RAGE convention)              |
| page map         | Structure at the system offset named by `+0x08`                        | Confirmed (location), Probable (extent) |
| page             | A unit counted by the page map, reconstructed from one or more streams | Confirmed (count), Probable (size rule) |
| stream           | One compressed unit that reconstructs all or part of a page            | Confirmed                               |

A reader SHOULD keep the numeric prefixes and not depend on these names.
