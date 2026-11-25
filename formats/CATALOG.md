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

"Repository category" is where this repository keeps the document. "Role" is what the payload actually is. Only RPF9 has an established role; KB2j/KB2n is Probable, and the rest are **Unknown**, because their documents state that no role is established.

| Identifier | Repository category | Role | Confidence | Signature | Native types | Population | Investigated | Document |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RPF9 | Container | Archive container | Confirmed | `9FPR` (`0x52504639`) | Container; carried by type 0 | 22 top-level archives, 6,534 unique `(archive, row)` pairs | All 22 manifests; 782 nested archives extracted | [rpf9](containers/rpf9/README.md) |
| RBF0 | Metadata | Unknown | Confirmed (sample) | `RBF0` (`52 42 46 30`) at offset 0 | 11 | 156 rows in one nested archive | 18 of 156 rows decoded | [rbf0](metadata/rbf0/README.md) |
| EDUP | Unknown | Unknown | Confirmed (sample) | `EDUP` (`45 44 55 50`) at offset 0 | 255 | 5 rows, 5 archives | 4 distinct payloads | [edup](unknown/edup/README.md) |
| KB2j / KB2n | Unknown | Container family, two signature variants (Probable) | Confirmed (sample) | `KB2j`, `KB2n` at offset 0 | 255 | 515 rows in `movies.rpf` (505 / 10) | Header, frame index and frame region of all 515 | [kb2j](unknown/kb2j/README.md) |
| SGD5 | Unknown | Unknown | Supported | `SGD5` (`53 47 44 35`) at offset 0 | 255 | 2 rows, `shaders.rpf` rows 1 and 2 | 2 of 2 | [sgd5](unknown/sgd5/README.md) |
| PSIN | Unknown | Unknown | Confirmed (sample) | `PSIN` (`50 53 49 4E`) at offset 0 | 11, 93, 94 | 103 unique decoded payloads | 103 of 103 | [psin](unknown/psin/README.md) |
| Type 14 payload | Unknown | Unknown | Confirmed (single sample) | None | 14 | 2 rows, 1 decoded | 1 decoded, 1 behind the payload transform | [type14](unknown/type14/README.md) |
| GFX* | Unknown | Unknown | Supported | `GFX*` (`47 46 58 2A`) at offset 0 of decoded payload | 66 | 49 rows, 6 depth-1 archives under `data.rpf` | Header sample only | [gfx](unknown/gfx/README.md) |
| ADAT | Unknown | Unknown | Supported | `ADAT` (`41 44 41 54`) at offset 0 | 255 | 768 rows, 65 depth-1 archives under 4 top-level archives | Header structure and two sample groups | [adat](unknown/adat/README.md) |
| `PTFX` | Unknown | Unknown | Confirmed (single sample) | `PTFX` (`50 54 46 58`) at offset 0 | 255 | 1 row, `common.rpf` | 1 of 1 | [ptfx](unknown/ptfx/README.md) |

RDS5/ETPF and the resource container are established on `main`: [RDS5](../formats/containers/rds5/README.md) is a container with record and block tables whose codec is Unknown, and [resources](resources/README.md) is the page and pointer serialization used inside resources. Neither has a pixel format, an object grammar or an engine allocation path established.

## Suspected format families

| Identifier | Evidence for a family | Missing | Where |
| --- | --- | --- | --- |
| Resource page serialization | Page map, system and graphics pages, compressed streams and pointer tables reported on an unmerged branch | Object grammar, pointer semantics, engine allocation path | Pending integration; not verified on `main` |

## Unidentified payload structures

| Structure | Population | State |
| --- | --- | --- |
| Type 14 row behind the payload transform | 1 row, in the expanded nested manifests | Not decoded, not compared |
| Unreadable rows inside sampled nested manifests | 823 of 169,523 rows | Counted, not classified |
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
- GFX* and ADAT are only visible after chunk decoding, so their populations depend on RPF9 chunk handling.
- Every family above except RPF9 is reached through an RPF9 row. Extraction capability limits all of them.
- KB2j, KB2n and EDUP populations were reconciled once already; a census over a differently selected manifest is not comparable and MUST be reported with its predicate.

## Recommended next objectives

1. Classify the 823 unreadable nested rows by failure mode, which turns the largest unidentified population into a bounded list.
2. Establish GFX* and ADAT headers beyond the first sample group.
3. Test the PSIN `+0x08` and `+0x0C` integer hypotheses against the full 103-payload sample with counterexamples.
4. Decode one payload-transform row, which unblocks every family whose only remaining sample sits behind it.
5. Transfer the resource and RDS5 findings once re-verified.