# Format catalog

Canonical index of every format family this repository has observed. Each entry states what is established, what is not, and where the detail lives. Identifiers are repository labels, not engine names.

Confidence values:

| Value | Meaning |
| --- | --- |
| Confirmed | Structural claims reproduce across the full observed sample with no counterexample |
| Confirmed (sample) | Reproduces across a bounded sample; the remainder of the population is unvisited |
| Confirmed (single sample) | Reproduces within one decoded payload; no second sample was compared |
| Probable | The reading fits every inspected sample, and the source document records it as the most likely one without confirming it |
| Supported | Consistent with all inspected samples but rests on a small population |
| Suspected | One or more signals point at a family; no structure established |
| Unknown | No identification |

## Identified file formats

"Repository category" is where this repository keeps the document. "Role" is what the payload actually is. Only RPF9 has an established role; KB2j/KB2n is Probable over the inspected rows; RDS5/ETPF is a container whose content role is Unknown, and the rest are **Unknown**, because their documents state that no role is established.

| Identifier | Repository category | Role | Confidence | Signature | Native types | Population | Investigated | Document |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RPF9 | Container | Archive container | Confirmed | `9FPR` (`0x52504639`) | Container; carried by type 0 | 22 top-level archives, 6,534 unique `(archive, row)` pairs | All 22 manifests; 782 nested archives extracted | [rpf9](containers/rpf9/README.md) |
| RDS5 / ETPF | Container | Container; content role Unknown | Confirmed (sample) | `RDS5` at offset 0; one `ETPF` chunk per file | Unknown | 57 sampled files, 1,026,833 block records, 357,115 entries | Header, record array, entry table, block catalogue and zlib blocks; no codec, pixel format, object grammar or texture content | [rds5](containers/rds5/README.md) |
| RBF0 | Metadata | Unknown | Confirmed (sample) | `RBF0` (`52 42 46 30`) at offset 0 | 11 | 156 rows in one nested archive | 18 of 156 rows decoded | [rbf0](metadata/rbf0/README.md) |
| EDUP | Unknown | Unknown | Confirmed (sample) | `EDUP` (`45 44 55 50`) at offset 0 | 255 | 5 rows, 5 archives | 4 distinct payloads | [edup](unknown/edup/README.md) |
| KB2j / KB2n | Unknown | Container family, two signature variants (Probable), scoped to the 515 `movies.rpf` rows | Confirmed (sample) | `KB2j`, `KB2n` at offset 0 | 255 (`movies.rpf` rows) | `movies.rpf`: 515 rows (505 `KB2n`, 10 `KB2j`). The `KB2n` stored prefix appears in 787 top-level rows across four archives | Header, frame index and frame region of all 515 `movies.rpf` rows; the other 282 `KB2n` rows are counted by stored prefix only | [kb2j](unknown/kb2j/README.md) |
| SGD5 | Unknown | Unknown | Supported | `SGD5` (`53 47 44 35`) at offset 0 | 255 | 2 rows, `shaders.rpf` rows 1 and 2 | 2 of 2 | [sgd5](unknown/sgd5/README.md) |
| PSIN | Unknown | Unknown | Confirmed (sample) | `PSIN` (`50 53 49 4E`) at offset 0 | 11, 93, 94 | 103 unique decoded payloads | 103 of 103 | [psin](unknown/psin/README.md) |
| Type 14 payload | Unknown | Unknown | Confirmed (single sample) | None | 14 | 2 rows, 1 decoded | 1 decoded, 1 behind the payload transform | [type14](unknown/type14/README.md) |
| GFX* | Unknown | Unknown | Supported | `GFX*` (`47 46 58 2A`) at offset 0 of decoded payload | 66 | 49 rows, 6 depth-1 archives under `data.rpf` | All 49 rows decoded; header, variant bytes and trailer described | [gfx](unknown/gfx/README.md) |
| ADAT | Unknown | Unknown | Supported | `ADAT` (`41 44 41 54`) at offset 0 | 255 | 768 rows, 65 depth-1 archives under 4 top-level archives | Header structure and two sample groups | [adat](unknown/adat/README.md) |

RDS5/ETPF is a container with record, entry and block tables whose codec is Unknown; [resources](resources/README.md) is the page and pointer serialization used inside resources, and it is a shared mechanism rather than a file format. Neither has a pixel format, an object grammar or an engine allocation path established.

## Unidentified payload structures

| Structure | Population | State |
| --- | --- | --- |
| `PTFX` text payload | 1 row, `common.rpf` row 151 | Structurally characterised: two CRLF-terminated key/value records and one final blank line, 47 bytes of printable ASCII and CRLF, no binary header (PTFX-F05, PTFX-F07). The flat key/value grammar is Probable (PTFX-F06), and reading the signature as the first segment of a text key is Probable (PTFX-F04). Format identity, purpose and loader are Unknown |
| Type 14 row behind the payload transform | 1 row, in the expanded nested manifests | Not decoded, not compared |
| Unreadable rows inside sampled nested manifests | 823 of 169,523 rows | All `unsupported_transform` (INV-F21, INV-F30), split by row state into 746 type-89 encoding-2, 76 type-11 encoding-3 and 1 type-14 encoding-3 row. 8 of the 823 were extraction-sampled and all failed at the payload transform; 815 were not sampled |
| Nested archives outside the sample | 3,188 eligible type-0 rows plus 381 above the 64 MiB cap | Not extracted |
| Rows whose decoded payload begins with zlib-looking data but is not one of the families above | Unknown | Not investigated |

Type IDs are row labels. The catalog assigns no format to a type ID except where a finding does so. No type ID observed so far is known to carry a single payload family, and type 11 and type 255 are each known to carry several.

## Shared serialization mechanisms

These are not game file formats and MUST NOT be listed as formats.

| Mechanism | Role | Document |
| --- | --- | --- |
| RPF9 name hashing | `hash64` and `key32` values derived from paths; resolves names and selects key classes | [names.md](containers/rpf9/names.md), [evidence/shared](../evidence/shared/INDEX.md) |
| Chunked storage | Chunk table plus per-chunk encoding, shared by every chunked row across families | [payloads.md](containers/rpf9/payloads.md) |
| Payload transform | A stored payload transform the reader rejects; rows behind it are unreadable and their decoded contents unobserved. The algorithm is unknown, so the transform is a storage mechanism of unknown effect, not a format | [payloads.md](containers/rpf9/payloads.md) |
| Resource page serialization | Page map, segment pages and compressed stream containers used inside resources | [resources](resources/README.md) |

## Research utilities

Not formats, not evidence of format support.

| Tool | Purpose |
| --- | --- |
| `tools/inventory/recursive_inventory.py` | Bounded recursive archive and payload selection with resumable state |
| `tools/rbf0`, `tools/sgd5`, `tools/type14`, `tools/kb2j`, `tools/psin` | Structural inspectors with synthetic tests |
| `lforge` CLI | Application-side inspection, extraction and resource reconstruction |

## Transferred from research branches

Two workstreams were transferred from unmerged branches. Their unique findings are recorded, and the claims that could not be re-derived are stated as Unknown rather than carried.

| Workstream | Source branch | State on `main` |
| --- | --- | --- |
| Resource serialization | `research/shared/resource-serialization` at `666facc`, transferred by `research/resources-v2` | Page, pointer and split-page rules established; engine allocation Unknown |
| RDS5 and ETPF container | `research/textures-rds5` at `5a54ae8`, verified in [evidence/rds5-verification](../evidence/rds5-verification/INDEX.md), transferred by `research/rds5-v2` | Container and record layout established; codec and pixel format Unknown |

## Dependencies between entries

- PSIN samples come from type 11, 93 and 94 rows; type 11 also carries RBF0. No type ID identifies PSIN.
- GFX* is only visible after chunk decoding, so its population depends on RPF9 chunk handling. ADAT rows are stored, not chunked.
- Every family above except RPF9 is reached through an RPF9 row. Extraction capability limits all of them.
- KB2j, KB2n and EDUP populations were reconciled before; a census over a differently selected manifest is not comparable and MUST be reported with its predicate.

## Recommended next objectives

1. Decode or otherwise bound one payload-transform row; all 823 unreadable nested rows fail at that transform (INV-F21, INV-F30).
2. Establish the GFX and ADAT headers beyond the first sample group.
3. Test the PSIN `+0x08` and `+0x0C` integer hypotheses against the full 103-payload sample with counterexamples.