# Format catalog

Canonical index of every format family this repository has observed. Each entry states what is established, what is not, and where the detail lives. Identifiers are repository labels, not engine names.

Confidence values:

| Value | Meaning |
| --- | --- |
| Confirmed | Structural claims reproduce across the full observed sample with no counterexample |
| Confirmed (sample) | Reproduces across a bounded sample; the remainder of the population is unvisited |
| Supported | Consistent with all inspected samples but rests on a small population |
| Suspected | One or more signals point at a family; no structure established |
| Unknown | No identification |

## Identified file formats

| Identifier | Class | Confidence | Signature | Native types | Population | Investigated | Document |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RPF9 | Container | Confirmed | `9FPR` (`0x52504639`) | Container; carried by type 0 | 22 top-level archives, 6,534 unique rows | All 22 manifests; 782 nested archives extracted | [rpf9](containers/rpf9/README.md) |
| RBF0 | Metadata encoding | Confirmed (sample) | `RBF0` (`52 42 46 30`) at offset 0 | 11 | 18 payloads, 1 nested archive | 18 of 18 | [rbf0](metadata/rbf0/README.md) |
| EDUP | Record container | Confirmed (sample) | `EDUP` (`45 44 55 50`) at offset 0 | 255 | 5 rows, 5 archives | 4 distinct payloads | [edup](unknown/edup/README.md) |
| KB2j / KB2n | Media container family | Confirmed (sample) | `KB2j`, `KB2n` at offset 0 | 255 | 515 rows in `movies.rpf` (505 / 10) | Header, frame index and frame region of all 515 | [kb2j](unknown/kb2j/README.md) |
| SGD5 | Block table | Supported | `SGD5` (`53 47 44 35`) at offset 0 | 255 | 2 rows, `shaders.rpf` rows 1 and 2 | 2 of 2 | [sgd5](unknown/sgd5/README.md) |
| PSIN | Tagged section encoding | Confirmed (sample) | `PSIN` (`50 53 49 4E`) at offset 0 | 11, 93, 94 | 103 unique decoded payloads | 103 of 103 | [psin](unknown/psin/README.md) |
| Type 14 payload | Unnamed document | Confirmed (single sample) | None | 14 | 2 rows, 1 decoded | 1 decoded, 1 behind the payload transform | [type14](unknown/type14/README.md) |
| GFX* | Unknown | Supported | `GFX*` (`47 46 58 2A`) at offset 0 of decoded payload | 66 | 49 rows, 6 depth-1 archives under `data.rpf` | Header sample only | [gfx](unknown/gfx/README.md) |
| ADAT | Unknown | Supported | `ADAT` (`41 44 41 54`) at offset 0 | 255 | 729 rows, 59 of 60 depth-1 `audio.rpf` archives | Two sample groups | [adat](unknown/adat/README.md) |

RDS5 and the resource container are not in the table because their detail is not yet on `main`; see [Pending integration](#pending-integration).

## Suspected format families

| Identifier | Evidence for a family | Missing | Where |
| --- | --- | --- | --- |
| PTFX | One plaintext row whose decoded payload carries `PTFX`; a decoded-payload scan of 356 small rows found exactly one occurrence | Structure, variant spread, second sample | No evidence index is committed; the family is under active research |
| Row payload transform | A stored payload transform that the reader rejects; rows behind it are unreadable and their contents unobserved | Algorithm, key schedule, whether the output is a known family | [payloads.md](containers/rpf9/payloads.md) |
| Resource page serialization | Page map, system and graphics pages, compressed streams and pointer tables observed in extracted resources | Object grammar, pointer semantics, engine allocation path | [Pending integration](#pending-integration) |

## Unidentified payload structures

| Structure | Population | State |
| --- | --- | --- |
| Type 14 row behind the payload transform | 1 row, in the expanded nested manifests | Not decoded, not compared |
| Unreadable rows inside sampled nested manifests | 823 of 169,523 rows | Counted, not classified |
| Nested archives outside the sample | 3,188 eligible type-0 rows plus 381 above the 64 MiB cap | Not extracted |
| Rows whose decoded payload begins with zlib-looking data but is not one of the families above | Unknown | Not investigated |

Type IDs are row labels. The catalog assigns no format to a type ID except where a finding does so, and no type ID in the 40 observed values carries a single payload family.

## Shared serialization mechanisms

These are not game file formats and MUST NOT be listed as formats.

| Mechanism | Role | Document |
| --- | --- | --- |
| RPF9 name hashing | `hash64` and `key32` values derived from paths; resolves names and selects key classes | [names.md](containers/rpf9/names.md), [evidence/shared](../../evidence/shared/INDEX.md) |
| Chunked storage | Chunk table plus per-chunk encoding, shared by every chunked row across families | [payloads.md](containers/rpf9/payloads.md) |
| Resource page serialization | Page map, segment pages and stream containers used inside resources | Pending integration |

## Research utilities

Not formats, not evidence of format support.

| Tool | Purpose |
| --- | --- |
| `tools/inventory/recursive_inventory.py` | Bounded recursive archive and payload selection with resumable state |
| `tools/rbf0`, `tools/sgd5`, `tools/type14`, `tools/kb2j`, `tools/psin` | Structural inspectors with synthetic tests |
| `lforge` CLI | Application-side inspection, extraction and resource reconstruction |

## Pending integration

Two research workstreams are Research-owned and in progress. Their findings are not yet on `main`, so this catalog does not cite them as established.

| Workstream | Source | State |
| --- | --- | --- |
| Resource serialization | `research/shared/resource-serialization` at `666facc`, successor `research/resources-v2` | Unique findings being re-verified before transfer |
| RDS5 and ETPF container | `research/textures-rds5` at `5a54ae8`, independent verification in `evidence/rds5-verification`, successor `research/rds5-v2` | 57 files and 1,026,833 blocks verified; transfer in progress |

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
