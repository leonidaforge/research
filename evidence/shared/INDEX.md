# Shared hashing evidence index

This subject covers the hash functions used by RPF9 identifiers. Name hashes are already established; this note records the field-key falsification tests, explicit normalization vectors and the independent control for the 64-bit path hash.

## Method

| Property             | Value                                                                                                 |
| -------------------- | ----------------------------------------------------------------------------------------------------- |
| Hash implementation  | `lforge-rage9` `rpf::names::hash64` and `joaat` as published at `6b362ad`, ported to the probe        |
| Application build    | `lforge` extractor from `leonidaforge/leonida-forge` at `fc841ea`                                     |
| Independent control  | `mmh3` 5.3.1 for MurmurHash3 x64-128 seed 0, first word, on inputs below 256 bytes                    |
| Control vectors      | Published `names/rpf9-hash64.lut` stems and the published one-at-a-time vectors                       |
| Field keys           | The nine keys listed in `formats/containers/rpf9/schema.md`                                           |
| Documentation inputs | 80 spellings of the 16 documented labels (five spellings each), in lower snake, lower concatenated and lower camel case |
| Executable inputs    | 52,516 distinct printable-string variants from the initialized data sections of one build             |
| Payload inputs       | 368 identifier tokens from one readable `.meta` payload resolved through the published `key32` LUT    |
| Seed inputs          | MurmurHash3 seeds 0 through 15                                                                        |

The control strips the `.rpf` extension from the LUT name before hashing, because RPF9 hashes the stem.

HSH-F01 through HSH-F04 are publicly reproducible from the vectors and the cited controls. HSH-F05 and HSH-F06 use a locally supplied executable and payload; their counts and negative outcome are private-evidence supported. The public text omits paths, bytes and payload strings.

## Findings

| ID      | Claim                                                                                                                                                                                                                                                                                                                        | Evidence                                                                       | Confidence                                                                                      | Limits                                                                                                                                                                                            |
| ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| HSH-F01 | The published 64-bit hash reproduces the first two `rpf9-hash64.lut` records exactly when the extension is stripped                                                                                                                                                                                                          | Re-hash control                                                                | Confirmed                                                                                       | Two records; the LUT itself was validated separately in RPF9-F108                                                                                                                                 |
| HSH-F02 | None of the nine observed field keys equals the 64-bit hash or joaat of any of the 80 candidate spellings                                                                                                                                                                                                                       | Exhaustive comparison over the candidate set                                   | Confirmed (negative for the tested set)                                                         | The true field names, if any, are unknown; a miss does not show the field keys are not hashes                                                                                                     |
| HSH-F03 | The field-key hash must be tested with candidate inputs derived from executable or schema evidence; descriptive labels from the research documents are not the preimages                                                                                                                                                     | Consequence of HSH-F02                                                         | Probable                                                                                        | Negative evidence only                                                                                                                                                                            |
| HSH-F04 | Both hashes fold only ASCII `A`-`Z` and `\`; bytes above `0x7F` are hashed unchanged. `hash64` treats NUL as an ordinary byte; `joaat` stops at the first NUL. The vectors reproduce the LUT and published one-at-a-time controls                                                                                            | Explicit vectors; independent Murmur control; published vectors (public)       | Confirmed (fold and `hash64` NUL); Confirmed against the published implementation (`joaat` NUL) | The 64-bit hash is independently checked only below 256 bytes. The `joaat` absolute values follow the published implementation, not a second independent implementation. No game data was checked |
| HSH-F05 | No field key matched any of 52,516 distinct printable-string variants from the initialized data sections of the Scarlet build game_scarlett_master.exe (SHA-256 95020b2...), or any of 368 identifier tokens from one readable `.meta` payload, under `hash64` words 1 and 2 (folded and unfolded), `joaat` (folded and unfolded), UTF-8 and UTF-16LE, and `joaat` half-words | Executable data and payload data (private-evidence supported); HSH-F01 control | Confirmed (negative for the tested set)                                                         | One build and one payload. A field name may be absent from the scanned strings, so this is not a disproof. No seed sweep in this finding                                                          |
| HSH-F06 | No field key matched under MurmurHash3 x64-128 seeds 0 through 15, words 1 and 2, folded and unfolded, over the 80 documentation labels and 19,547 identifier-like executable variants. Seed 0 passes the HSH-F01 control                                                                                                    | Executable data (private-evidence supported); HSH-F01 control                  | Confirmed (negative for the tested set)                                                         | The seed space is 16 values. A match at one key would be a lead only, and no match does not show the keys are not hashes                                                                          |

## Normalization vectors

The bytes are shown escaped. `hash64` values are 64-bit; `joaat` values are 32-bit.

| Hash     | Input bytes                | Result               | Note                                          |
| -------- | -------------------------- | -------------------- | --------------------------------------------- |
| `hash64` | `alpha/beta/gamma`         | `0x7489FBD94F2A4C86` | LUT stem control                              |
| `hash64` | `ALPHA/BETA/GAMMA`         | `0x7489FBD94F2A4C86` | ASCII case folded                             |
| `hash64` | `Alpha\x5CBeta/Gamma`      | `0x7489FBD94F2A4C86` | Backslash folded                              |
| `hash64` | `caf\xC3\xA9/item`         | `0xC5803A918B18D3ED` | Non-ASCII bytes unchanged                     |
| `hash64` | `caf\xC3\xA9/ITEM`         | `0xC5803A918B18D3ED` | Non-ASCII prefix unchanged, suffix folded     |
| `hash64` | `caf\xC3\xA8/item`         | `0x00E0B4E3BC830FD9` | `0xA8` is not folded from `0xA9`              |
| `hash64` | `caf\xC3\x89/item`         | `0xBC073E08A6C3D838` | `0x89` is not folded from `0xA9`              |
| `hash64` | `a\x00b`                   | `0x2DEF92D2C1E6B5DB` | NUL is an ordinary byte                       |
| `hash64` | `ab`                       | `0x938B11EA16ED1B2E` | NUL changes the result                        |
| `joaat`  | `alpha/beta`               | `0x75438640`         | Published one-at-a-time control               |
| `joaat`  | `ALPHA\x5CBETA`            | `0x75438640`         | ASCII case and backslash folded               |
| `joaat`  | `caf\xC3\xA9/item`         | `0xB53D3A5D`         | Non-ASCII bytes unchanged                     |
| `joaat`  | `caf\xC3\xA8/item`         | `0x28AAE738`         | `0xA8` is not folded from `0xA9`              |
| `joaat`  | `caf\xC3\x89/item`         | `0x6B633C5F`         | `0x89` is not folded from `0xA9`              |
| `joaat`  | `alpha/beta\x00ignored`    | `0x75438640`         | NUL stops hashing                             |
| `joaat`  | `a\x00b`                   | `0xCA2E9442`         | NUL stops hashing                             |
| `joaat`  | `\x00`                     | `0x00000000`         | A leading NUL gives 0                         |

## Candidate vocabulary

The documentation labels were derived from the field meanings in `schema.md`: name, name hash, location records R/F/A, chunk table, payload transform, metadata start, read source, 32-bit key, type, size, offset, entry, row, path. Each base label was tested with space, underscore, concatenated and camel-case spellings, plus the bare word. The list is intentionally small and derived from documentation; it is not a symbol list.

The executable candidates are printable ASCII and ASCII-only UTF-16LE runs of 4 to 512 bytes from the readable, initialized, non-executable sections of one build. Exact strings, trimmed strings, stems, last path components and text after a scheme prefix were tested as UTF-8 and UTF-16LE. The payload candidates are XML identifier tokens from one readable `.meta` payload. No payload text is published.

## Reproduction

The LUT control is:

```text
hash64("levels/americas/interiors/instanced/int_tst_interiors_metadata") == 0x000542ABDCA39C4C
```

A probe that omits the stem step and hashes the full `.rpf` name fails the control. The 64-bit implementation must also agree with `mmh3` 5.3.1 for the lowercase control inputs below 256 bytes, and `joaat("a")` must equal `0xCA2E9442`, before either negative result is trusted.

The executable and payload probes read user-supplied files only. They print one line per key, plus aggregate string counts. They do not write to the inputs and publish no bytes or payload text.

## Search spaces

| Source            | Search space                                                                                                                                                       |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Documentation     | 80 spellings of the 16 labels, tested with both hashes and both Murmur words                                                                                            |
| Executable        | 71,925 printable strings from initialized data sections, reduced to 52,516 distinct variants and 19,547 identifier-like variants                                   |
| Payload           | One `.meta` payload of 121,460 bytes, reduced to 368 XML identifier tokens                                                                                         |
| Seeds             | MurmurHash3 x64-128 seeds 0 through 15                                                                                                                             |
| Encodings         | UTF-8 bytes and UTF-16LE code units for every candidate                                                                                                            |
| Hash variants     | `hash64` words 1 and 2, folded and unfolded; `joaat` folded and unfolded; `joaat` compared with either 32-bit half of each key                                     |

## Interpretation limits

- A hash of a known algorithm over unknown inputs cannot be inverted. A miss is expected and proves nothing about the algorithm.
- The executable scan covers string literals present in one build. A field name computed at build time, stored outside those sections, or never present as text is outside the search space.
- The `.meta` sample is one file. Its XML field names are game-data names and need not be the internal names of RPF9 columns.
- Seed coverage is 0 through 15 only. Other seeds, initial states and algorithms were not tested.
- If a field name is ever recovered from the executable or from a schema dump, the same probes can confirm or reject the hash function.
- Do not describe the field keys as MurmurHash3 or joaat on the strength of this evidence alone.

## Next experiments

- Recover a field name from the structured-data loader's field setters or from a schema dump, then test it against the nine keys with the normalization vectors.
- Require a second key before treating a single match as a lead.
- Test a second executable build or an independently sourced schema to separate build-specific from format-wide behavior.
- Do not brute-force the key space.
