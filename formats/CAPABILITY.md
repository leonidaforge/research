# Capability matrix

What research establishes and what the application implements are separate questions. The first table is research capability, the second is application capability. A positive claim in either table cites supporting findings.

## States

| State | Meaning |
| --- | --- |
| Not investigated | No work attempted |
| Unknown | Work attempted; the answer is not established, or the implementation state could not be determined |
| Unsupported | Attempted and shown not to work, or no evidence that it can |
| Experimental | A research tool does the work on samples; not production quality |
| Partially established by research | Some structure or some variants are established; coverage is bounded |
| Established by research | Structure reproduces across the whole observed population |
| Implemented and validated in the application | The application performs the capability and its output was checked against real samples |
| Implemented, not validated here | Code exists; the check performed for this document did not confirm it |
| Not applicable | The capability has no meaning for this format |

## Research capability

| Format | Recognition | Inspection | Parsing | Decoding | Reconstruction | Export | Rendering | Writing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RPF9 | Established (F01) | Established (F01–F123) | Established (F10–F60) | Partially established: chunk encodings 2, 3 and 4 (F119–F122); rows behind the payload transform undecoded | Partially established: metadata region and payload placement; no writer | Experimental: native row extraction verified on 782 archives and 144 payloads (INV-F18, INV-F23) | Not applicable | Unsupported: no writer researched |
| RBF0 | Established (RBF0-F01) | Established (RBF0-F01–F12) | Established (RBF0-F02–F11) | Partially established: 15,305 strings and 14,127 attributes decoded (RBF0-F12); field semantics Unknown | Unsupported | Experimental: `tools/rbf0` | Not applicable | Not investigated |
| EDUP | Established (5 rows) | Established | Established: `size = 8 + 16 × count + 4 + length` on 4 distinct payloads | Partially established: entry fields read; meanings Unknown | Unsupported | Experimental: `tools/edup` if present, otherwise sample scripts | Not applicable | Not investigated |
| KB2j / KB2n | Established (515 rows) | Established | Established: header, frame index table, frame-data region | Partially established: frame index decoded; frame payload encoding Unknown | Unsupported | Experimental: `tools/kb2j` | Unsupported: no codec; external demuxers stop at `Bink 2 video is not implemented` | Not investigated |
| SGD5 | Established (2 rows) | Established | Established: block table, 36 blocks across 2 payloads | Partially established: data-region record prefix observed | Unsupported | Experimental: `tools/sgd5` | Unsupported: purpose Unknown | Not investigated |
| PSIN | Established (103 payloads) | Established | Established: tagged section walk on 103/103 (PSIN-F04) | Partially established: section bodies Unknown (PSIN-F05) | Unsupported | Experimental: `tools/psin` | Not applicable | Not investigated |
| Type 14 | Established (1 decoded row) | Established | Established: header, string table, 8 records of `0x28` (T14-F01–F10) | Established for the single decoded row | Unsupported | Experimental: `tools/type14` | Not applicable | Not investigated |
| GFX* | Established (49 rows) | Partially established: header sample only | Not investigated | Partially established: chunk decoding only | Unsupported | Experimental: extraction via the CLI | Unsupported | Not investigated |
| ADAT | Established (729 rows) | Partially established: two sample groups | Not investigated | Partially established: chunk decoding only | Unsupported | Experimental: extraction via the CLI | Unsupported | Not investigated |
| RDS5 / ETPF | Established on `research/textures-rds5`; independently verified in `evidence/rds5-verification` | Established: 57 files, 1,026,833 blocks, 357,115 entries verified | Established: header, record array, block catalogue | Partially established: delta bounds and zlib blocks; codec identity Unknown | Partially established: ETPF chunk extent; no object reconstruction | Experimental: `tools/rds5` | Unsupported: no pixel format established | Not investigated |
| Resource page serialization | Established: page map, segments, pointer tables observed | Partially established | Partially established: page map and stream containers | Established: every stream inflated with a valid checksum on the inspected resource | Partially established: pages and pointers; object graph Unknown | Experimental: `archive resource` | Not applicable | Unsupported |

Recognition means the signature is identified. It does not mean the format is understood. RPF9 recognition in this table is the research result, not the application's.

## Application capability

Assessed against `lforge` 0.1.0 by running the CLI read-only and by reading `crates/core/src/inspect.rs`. Application revision `92af6e2`.

| Format | Recognition | Inspection | Parsing | Decoding | Reconstruction | Export | Rendering | Writing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RPF9 | Implemented and validated: header recognition, 22 archives authenticated | Implemented and validated | Implemented and validated: columnar table of contents after metadata authentication | Implemented and validated: chunked rows, encodings 2, 3 and 4 | Not applicable | Implemented and validated: `archive extract`, `manifest`, `ls`, `search`, `recover` | Not applicable | Unsupported |
| RDS5 | Implemented (`RDS5`, support `structural`); not validated here: one extracted type-5 row returned `unrecognised` | Implemented, not validated here | Implemented, not validated here | Implemented, not validated here | Not applicable | Not applicable | Unsupported | Unsupported |
| RBF0 | Implemented (`RBF0`, support `structural`) | Implemented, not validated here | Implemented, not validated here | Implemented, not validated here | Not applicable | Not applicable | Not applicable | Unsupported |
| PSIN | Implemented (`PSIN`, support `recognition`, magic only) | Implemented: magic reported, no field shown | Unsupported | Unsupported | Not applicable | Not applicable | Not applicable | Unsupported |
| Resource page serialization | Implemented and validated: `archive resource 0x1010` reported a complete resource, 1 system page of 1,888 bytes and 1 graphics page of 49,152 bytes, 39 system and 12 graphics pointers, 0 outside | Implemented and validated | Implemented and validated: page map declares 1 system and 1 graphics page | Implemented and validated: every stream inflated with a valid checksum | Implemented, not validated here: page reconstruction only, no object graph | Implemented: page listing | Not applicable | Unsupported |
| EDUP, KB2j, KB2n, SGD5, type 14, GFX*, ADAT | Unsupported: unrecognised by `binary inspect` and `archive inspect` | Unsupported | Unsupported | Unsupported | Not applicable | Unsupported | Unsupported | Unsupported |

Support levels are read from `FormatInfo` in `crates/core/src/inspect.rs`: `structural`, `header` or `recognition`. `structural` means header and the record structures the documentation establishes are parsed. It does not mean the payload semantics are known.

## Distinctions this matrix relies on

- Metadata decoding is not payload decoding. RPF9 metadata decodes fully while several payload families hold decoded bytes with no established field meanings.
- Container parsing is not object reconstruction. RDS5 records and blocks parse; the objects they describe are not rebuilt.
- Synthetic tests are not real-sample compatibility. Every `tools/` inspector is validated on authored fixtures only.
- Research tools are not application features. `tools/rds5` and the application's RDS5 inspector are separate implementations.
- Recognition is not support. PSIN is recognised from its magic and nothing else.

## Evidence gaps

- No application capability was validated for RBF0 or RDS5 with a real sample; the one RDS5 check performed returned `unrecognised`, which may be a build difference, a sample selection error or a defect. Unknown which.
- Application rendering, writing and reconstruction beyond pages were not investigated; the CLI exposes no command for them.
- Worker-run analysis of GFX*, ADAT and PSIN was in progress when this document was written; their rows reflect committed findings only.
