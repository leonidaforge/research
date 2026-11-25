# PSIN evidence index

Payload observations from the Scarlett build [e95020b2](../../builds/gta-vi/scarlett-e95020b2/README.md). No executable code path was traced. Every finding is **Private-evidence supported**: the selection and the inspector are public, but the payloads remain outside this repository.

## Sample

| Property              | Value                                                                                                                                                    |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Payloads              | 103 unique PSIN payloads: the earlier 18 plus 85 additional                                                                                              |
| Earlier sample        | 18 type 11 payloads from five top-level archives                                                                                                         |
| Expanded extraction   | 86 decoded type 11 rows attempted from nine top-level archives; 82 began with `PSIN`, four with `RBF0`                                                    |
| Selection             | decoded type 11 rows at or below 1 MiB from the top-level inventory manifests; per archive, sorted by `(logical size, row)` and quantile-spaced up to 16 |
| Depth-1 payloads      | 13 unique payloads from the expanded inventory and earlier probes                                                                                         |
| Sizes                 | 216 to 1,032,656 bytes                                                                                                                                   |
| First section offsets | 48 to 972,552                                                                                                                                            |
| Signature             | `50 53 49 4E` at offset 0 in all 103                                                                                                                     |

The earlier 18 rows were `anim.rpf` 235, 238, 241, 244; `data.rpf` 42, 48, 49, 52; `levels.rpf` 2053, 2055, 2056, 2057; `packs.rpf` 61, 67, 70, 71; and `pack/story000/story000.rpf` 444, 457.

The sample is a convenience sample. It does not establish the type's population, size range or type-ID range. The expanded extraction shows that type ID 11 carries both PSIN and RBF0.

## Evidence types

| Type           | Meaning                                                                                   |
| -------------- | ----------------------------------------------------------------------------------------- |
| `BINARY`       | Bytes read from decoded RPF9 payloads, not traced in executable code                      |
| `CROSS_SAMPLE` | A property compared across distinct payloads. The sample count and selection rule are above |

## Findings

| ID       | Claim                                                                                                                                                                                                                                                                               | Evidence                 | Confidence                                 | Limits                                                                 |
| -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------ | ------------------------------------------ | ---------------------------------------------------------------------- |
| PSIN-F01 | Payloads start with ASCII `PSIN` (`0x4E495350`) at offset 0                                                                                                                                                                                                                          | `BINARY`, `CROSS_SAMPLE` | Confirmed                                  | 103 unique payloads, one build                                         |
| PSIN-F02 | The big-endian `u32` at `+0x04` is the offset of the first tagged section. In 103 of 103 payloads a printable four-byte tag starts at that offset, and walking `tag + big-endian length` from there ends exactly at the payload size. The length includes the eight-byte tag and length header | `BINARY`, `CROSS_SAMPLE` | Confirmed (sample)                         | The meaning of each tag and section body is unknown                    |
| PSIN-F03 | `+0x04` is not the payload size or a section count. 0 of 103 big-endian `u32` values at `+0x04` equal the payload size; the value ranges from 48 to 972,552 while sizes range from 216 to 1,032,656. `+0x06` is not the size either; it equals the low 16 bits of the `+0x04` offset in 103 of 103, and 28 offsets are above `0xFFFF` | `CROSS_SAMPLE`           | Confirmed (rejected readings)              | Only the tested integer readings were rejected                         |
| PSIN-F04 | The tagged-section walk has three observed sequences: 94 payloads use `LSCH` -> `LENM` -> `LSNS` -> `LGID` -> `LRSC` -> `CHKS`; seven use `PMAP` -> `PSCH` -> `PSIG` -> `STNS` -> `CHKS`; two insert `STDN` before `STNS`. The walk ends at the payload size in 103 of 103 payloads | `BINARY`, `CROSS_SAMPLE` | Confirmed (sequences and boundary rule)    | Tag strings are raw bytes, not semantic names                          |
| PSIN-F05 | Several section bodies have repeated length properties: `LSCH` body is a multiple of 16 in 94 of 94; `LRSC` body is 80 in 94 of 94; `CHKS` body is 12 in 103 of 103; `PMAP` and `STNS` bodies are multiples of 16 in nine of nine; `STDN` body is a multiple of 16 in two of two. `PSCH`, `PSIG`, `LENM`, `LSNS` and `LGID` have no single body modulus | `CROSS_SAMPLE`           | Confirmed (lengths); Unknown (meaning)     | Body contents were not decoded into records                            |
| PSIN-F06 | Bytes `+0x08..+0x0F` take 84 distinct values in 103 payloads; nine payloads store eight `0x70` bytes there. The candidate readings are a big-endian `u32` at `+0x08` and a little-endian `u32` at `+0x0C`. Neither equals the payload size or a section length in the sample | `CROSS_SAMPLE`           | Unknown (probable integer readings only)   | No hash or identifier interpretation was tested to a conclusion        |
| PSIN-F07 | Type ID does not identify PSIN. The expanded type 11 extraction produced 82 PSIN payloads and four `RBF0` payloads. The expanded inventory also has PSIN in type 93 and type 94 rows. PSIN therefore occurs in at least types 11, 93 and 94 | `BINARY`, `CROSS_SAMPLE` | Confirmed (sample)                         | Sample only; the full type-ID population was not surveyed              |
| PSIN-F08 | The first section offset is not always 16-byte aligned. It is aligned in 100 of 103 payloads and unaligned in `anim.rpf` rows 260 (offset 260), 247 (offset 307,048) and 248 (offset 972,552)                                                                                          | `CROSS_SAMPLE`           | Confirmed (counterexamples)                | Three counterexamples found in 103 payloads                            |
| PSIN-F09 | Many payloads contain runs of `0xAA` and `0x70` inside the region before the first section or inside section bodies                                                                                                                                | `BINARY`                 | Speculative                                | Could be padding, uninitialised bytes or meaningful data               |

## Counterexamples

| Reading                          | Counterexample                                                                                                                                       |
| -------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| `+0x04` as payload size          | `packs.rpf` row 67 is 248 bytes with `+0x04` = 48; `data.rpf` row 42 is 25,476 bytes with `+0x04` = 23,888; `anim.rpf` row 248 is 976,116 bytes with `+0x04` = 972,552 |
| `+0x06` as payload size          | 0 of 103 `u16` values at `+0x06` equal the payload size                                                                                              |
| `+0x06` as an independent offset | `levels.rpf` row 2056 is 169,316 bytes with first offset 152,352 (`0x00025320`); `+0x06` is `0x5320`, or 21,280                                      |
| 16-byte alignment of `+0x04`     | `anim.rpf` rows 260, 247 and 248 have offsets 260, 307,048 and 972,552                                                                               |
| Type ID 11 implies PSIN          | `core_restofworld.rpf` row 22, `data.rpf` row 698, `packs.rpf` row 121 and `story000.rpf` row 645 begin with `RBF0`                                  |

## Reproduction

The following commands ran on 2026-11-25 with the `lforge` CLI built from `leonidaforge/leonida-forge` commit `92af6e2ef26f1f2819a757457a97003fd52029b4`. `<GAME_ROOT>` is a local installation, `<WORK>` a scratch directory outside it, and `<EXECUTABLE>` the game executable that matches the archive, used only to authenticate its metadata. `--executable` is required by this build for encrypted metadata.

```text
lforge archive manifest <ARCHIVE> --executable <EXECUTABLE> --format jsonl --output <WORK>/rows.jsonl
lforge archive extract <ARCHIVE> --row <ROW> --output <WORK>/row.bin --executable <EXECUTABLE> --overwrite
python tools/psin/psin_inspect.py <WORK>/row.bin --json
```

`archive manifest` lists each row's type ID, logical size and stored form. `archive extract` writes the decoded payload. The inspector reports the big-endian first-section offset, the eight bytes at `+0x08..+0x0F`, every tagged section, and whether the walk ends at the payload size.

The tool tests build synthetic PSIN inputs:

```text
python -m unittest discover -s tools/psin
```

## Limits

- The sample is not random. The expanded extraction only covers decoded type 11 rows at or below 1 MiB in the selected top-level archives.
- One build and one local archive set were examined.
- Some depth-1 payloads repeat earlier content; the corpus is deduplicated by SHA-256.
- No executable path was traced and no historical RAGE format is claimed as a match.
- Fields and tags were not assigned meanings. Section bodies were not decoded.
- Exact payload bytes stay outside this repository.

## Next experiments

- Survey type 11 rows above 1 MiB and count PSIN against RBF0 over the full readable population.
- Decode the repeated `LSCH`, `LRSC`, `CHKS`, `PMAP` and `STNS` bodies into candidate records and test their field alignment without assigning semantics.
- Search the executable for the `PSIN` magic and section tags, without publishing key material or secret state.
