# RBF0 evidence index

Payload observations from the Scarlett build [e95020b2](../../builds/gta-vi/scarlett-e95020b2/README.md). No executable code path was traced. Every finding is **Private-evidence supported**. Corrected interpretations are recorded in [research-history.md](research-history.md).

## Sample

| Property | Value |
| -------- | ----- |
| RBF0 files | 447 decoded occurrences; 291 if the repeated row 0 archive extraction is counted once |
| Unique payloads | 238 by SHA-256 of the decoded bytes |
| Original nested archive | row 0 of `<GAME_ROOT>/data.rpf`, SHA-256 `91A236BCB4ECF96840BC0B70E22D1619C0FEDFA11976A336DE311A438214A09E`, 414544 bytes, 156 type 11 rows |
| Original rows | 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 72, 78, 90, 141, 154 and 155 of the nested archive |
| Additional nested archives | 17 more RPF9 archives extracted from `<GAME_ROOT>/data.rpf` type 0 rows 1, 3, 7, 8, 9, 13, 14, 15, 16, 19, 20, 23, 31, 32, 35, 37 and 38, the nested archives at or below 2 MiB |
| Top-level rows | all readable type 11 rows beginning with RBF0 from the 22 top-level archives enumerated in the [format document](../../formats/metadata/rbf0/README.md#population); 9 unique payloads |
| Parse result | 238 of 238 unique payloads and 447 of 447 decoded occurrences consumed |

The original 18 rows remain a subset. Later archives were added to test the grammar, not to estimate a population. The sample is a convenience sample, not a random one.

## Census sample

| Property | Value |
| -------- | ----- |
| Scope | `<GAME_ROOT>/data.rpf`, walked recursively |
| Archives opened | 41 |
| Entries walked | 23,075 |
| Payloads beginning with `RBF0` | 1,462 |
| Payloads decoded to the end of the root element | 1,462 |
| Failures and limit refusals | 0 |
| Unique payloads | 1,395 by SHA-256 of the decoded bytes |
| Document sizes | 98 to 2,372,401 bytes |
| Elements per document | 1 to 68,398 |
| Names per document | 4 to 204 |
| Deepest nesting | 35 levels |
| Headers | 1,459 versioned, 3 versionless |
| Distinct root names | 30 |

This sample is the whole population of one archive, not a selection, and it is what RBF0-F18 to RBF0-F25 rest on. It was produced by the implementation's decoder, which walks the archive the way the CLI does and decodes every payload it reaches. Payloads outside `data.rpf` were walked separately under an entry bound; see RBF0-F26.

## Evidence types

| Type | Meaning |
| ---- | ------- |
| `BINARY` | Bytes read from decoded RPF9 payloads, not traced in executable code |
| `CROSS_SAMPLE` | A property compared across distinct payloads |
| `SYNTHETIC` | Independently built fixtures that test the repository parser, not native semantics |

## Findings

| ID | Claim | Evidence | Confidence | Limits |
| -- | ----- | -------- | ---------- | ------ |
| RBF0-F01 | Payloads start with ASCII `RBF0` (`0x30464252`) at offset 0 | `BINARY` | Confirmed | 238 unique payloads, one build |
| RBF0-F02 | Two header variants exist. The `versioned` form has magic, `u16 0xFFFB` at `+0x04`, a second `u16` at `+0x06` (value 1 in every observed sample), then the token stream at `+0x08`; its numbers are 8 bytes. The `versionless` form starts the token stream at `+0x04`; its numbers are 4 bytes. Counts: 235 `versioned` and 3 `versionless` unique payloads. The labels `version marker` and `version` are **Speculative** interpretations; the header split and the number-width difference are Confirmed. The old fixed 10-byte prefix reading conflated the header with the first token | `BINARY`, `CROSS_SAMPLE` | Confirmed (layout); Speculative (version interpretation) | One build; only the value 1 observed in the second word |
| RBF0-F03 | The first token is `0x0000` in all 238 unique payloads: element type 0, name index 0. The root name is the first name definition. Observed root name lengths are 15, 17, 21, 22, 23, 29, 30 and 35 bytes. Names are not published | `BINARY`, `CROSS_SAMPLE` | Confirmed (sample) | One build; root names are game content |
| RBF0-F04 | Names form one table per document. A token whose low 12-bit index equals the current table length defines a name by `u16` length and bytes; a lower index reuses that name. Observed tables hold 5 to 41 names. The original 18 rows hold 118 definitions and 18 distinct names | `BINARY`, `CROSS_SAMPLE` | Confirmed (sample) | Whether the name set identifies a schema is Unknown |
| RBF0-F05 | An element is a type 0 token, a `u32` reserved word (zero in every observed element), a `u16` attribute count, that many attribute tokens, zero or more body tokens, and `u16 0xFFFF`. The root body uses the same form | `BINARY`, `CROSS_SAMPLE` | Confirmed (sample) | Meaning of the reserved word beyond its zero value is Unknown |
| RBF0-F06 | RPF9 type ID 11 carries at least RBF0 and PSIN. Type ID 11 is not an RBF0 identifier | `BINARY`, `CROSS_SAMPLE` | Confirmed | Surveyed rows, not every type ID 11 row |
| RBF0-F07 | The verified rows decode from mode-1 raw DEFLATE or from stored chunked rows. Storage observations are recorded in RPF9-F118 | `BINARY` | Confirmed | 447 extractions; some rows were not readable |
| RBF0-F08 | Attribute tokens use the same `name index | type code` word as body tokens. Observed attribute type codes are 1, 4 and 6; observed attribute name indices span 1 to 39. Element attribute counts are 0, 1 or 2. Type 6 values are `u16` length followed by bytes. The old closed `0x6003`/`0x6004` attribute set is corrected | `BINARY`, `CROSS_SAMPLE` | Confirmed (sample) | Only counted attributes before the body were observed |
| RBF0-F09 | The former fixed 8-byte field `0x1006` is a type 1 value token with name index 6. Type 1 values are 8 bytes in versioned documents and 4 bytes in versionless documents. It is not a special value class. Observed type 1 counts: 21,671 eight-byte and 201 four-byte values | `BINARY`, `CROSS_SAMPLE` | Confirmed (sample) | Numeric interpretation is structural; signedness and semantics are Unknown |
| RBF0-F10 | Every element ends with `u16 0xFFFF`. Every payload ends with at least one close token, but the eight-byte trailer is not universal: trailing `FF` bytes are 2 to 14 long across the 238 unique payloads, and exactly 8 bytes in 101 of them | `BINARY`, `CROSS_SAMPLE` | Confirmed (sample) | Eight-byte trailers are common but not required |
| RBF0-F11 | A token is `u16` little-endian: low 12 bits are a name index, high 4 bits are a type code. Observed type codes are 0 (element), 1 to 6 (values), and the special tokens `0xFFFD` (text) and `0xFFFF` (close). Codes 7 to 14 were not observed and are rejected | `BINARY`, `CROSS_SAMPLE` | Confirmed (sample) | Semantic meaning of each type code is Unknown |
| RBF0-F12 | A text node is `u16 0xFFFD`, `u32` byte length, then bytes, inside an element. The 238 unique payloads contain 46,701 text nodes, 2 to 2360 bytes long. The original 18-row subset contains 15,305 text nodes | `BINARY`, `CROSS_SAMPLE` | Confirmed (sample) | Text content is game content and is not published |
| RBF0-F13 | The decoded RBF0 sample grew from 18 rows to 447 files and 238 unique payloads. The added payloads come from 17 more nested archives under `<GAME_ROOT>/data.rpf` and from top-level type 11 rows | `BINARY`, `CROSS_SAMPLE` | Confirmed | Convenience sample; nested archives at or below 2 MiB |
| RBF0-F14 | The former claim that the last eight `FF` bytes are always four inferred close words is rejected as a universal statement. Payloads with an eight-byte trailer fit that reading, but the trailer length varies and no per-word role was observed | `BINARY`, `CROSS_SAMPLE` | Rejected (universal) | The role of individual close words in a longer trailer is Unknown |
| RBF0-F15 | An independent token parser consumes 238 of 238 unique payloads and 447 of 447 decoded occurrences with no unsupported token. The original 18 nested rows and the nine unique top-level RBF0 payloads are included in that population | `BINARY`, `CROSS_SAMPLE`, `SYNTHETIC` | Confirmed (sample) | Selection is not the full game population |
| RBF0-F16 | Observed value widths: type 1 is the document number width (8 or 4 bytes); type 2 and type 3 carry no value bytes; type 4 is the document number width (8 or 4 bytes); type 5 is 12 bytes in its single observation; type 6 is `u16` length plus bytes. Counts are in the value table of the format document | `BINARY`, `CROSS_SAMPLE` | Confirmed (widths); Unknown (meaning) | Type 5 has one observation; types 2 and 3 have 21 observations together |
| RBF0-F17 | The versionless header appears in 3 of 238 unique payloads. All three parse with 4-byte numbers and the same token grammar | `BINARY`, `CROSS_SAMPLE` | Confirmed (sample) | Whether it is a stable family or a rare variant is Unknown |
| RBF0-F18 | An element is a node with a name, a counted attribute set and a body of nested elements, value tokens and text nodes in the order the bytes store them. Repeated sibling elements are how the format writes a list; the grammar has no array token. The largest document in `data.rpf` is 68,398 elements, mostly repeated children of one element | `BINARY`, `CROSS_SAMPLE` | Confirmed | Field meaning remains Unknown |
| RBF0-F19 | A text node's declared length includes one trailing `0x00` that is not part of the text. 287,267 of 287,297 text nodes in `data.rpf` end with it; the 30 that do not are also not valid UTF-8, so no UTF-8 text value is observed without a terminator. The earlier reading that the declared bytes are the value verbatim is corrected | `BINARY`, `CROSS_SAMPLE` | Confirmed | One build; a text node is text only when it is UTF-8 |
| RBF0-F20 | A type-6 value is `u16` length plus bytes with **no** terminator: none of 110,051 observations in `data.rpf` ends with a NUL, and 30 contain a NUL before their end or are not UTF-8. Type-6 values appear in body positions as well as counted attribute positions, which the earlier sample did not show | `BINARY`, `CROSS_SAMPLE` | Confirmed | Meaning of a type-6 value is Unknown; it reads as an engine class name in the observed families |
| RBF0-F21 | Type 1 is a 64-bit integer and type 4 is an IEEE-754 binary64, both little-endian. `data.rpf` holds 30,663 class-1 values (30,655 fit in `i32`, 1,079 negative, range -2,125,891,426 to 4,289,044,108) and 39,291 class-4 values (all finite, 27,169 integral, range -431,602,080 to 65,536). The same number is written both ways: `1` is `01 00 00 00 00 00 00 00` as class 1 and `00 00 00 00 00 00 F0 3F` as class 4 | `BINARY`, `CROSS_SAMPLE` | Confirmed (encoding) | What a stored number describes is Unknown |
| RBF0-F22 | Nesting reaches 35 levels and documents reach 2,372,401 bytes in `data.rpf`. A 32-level parse cap refused 4 payloads of the archive, so any decoder limit MUST exceed the observed nesting rather than reject real documents | `BINARY` | Confirmed | One build |
| RBF0-F23 | The recursive walk of `<GAME_ROOT>/data.rpf` reaches 41 archives and 23,075 entries, finds 1,462 RBF0 payloads (1,395 distinct), and decodes all 1,462 to the end of the root element with 0 failures and 0 limit refusals. All end with the close word of the root element; the `FFFF` run before it closes each element still open | `BINARY`, `CROSS_SAMPLE` | Confirmed | One archive; other archives are bounded separately (RBF0-F26) |
| RBF0-F24 | Values of class 2 and class 3 store no bytes: 3,627 and 3,747 observations in `data.rpf`. They carry neither a value nor a length, so their meaning cannot be recovered from the document alone | `BINARY`, `CROSS_SAMPLE` | Confirmed (width) | Meaning Unknown |
| RBF0-F25 | The 1,462 payloads have 30 distinct root names and fall into UI description and tuning families: prefab definitions, animation node graphs, screens, credits pages, movie subtitle containers and views, flow blocks, feedback contexts, panels, grids, progress datasets, safe-area configurations, one general tuning file and one combat tunables table. The vocabulary is the engine's UI one: 518 distinct element names, 11 distinct attribute names, and type-6 values that read as engine class names | `BINARY`, `CROSS_SAMPLE` | Confirmed (family level) | Individual field semantics Unknown; names are game content and are not published |
| RBF0-F26 | Outside `data.rpf` the format is rare. 296,590 entries were walked across 19 other archives under a 60,000-entry bound per archive; 5 payloads beginning with `RBF0` were found, in `textures.rpf` (1), `anim.rpf` (1) and `pack/core_restofworld` (3), and all 5 decoded. `audio.rpf` was not walked | `BINARY`, `CROSS_SAMPLE` | Confirmed (bounded) | Six walks are entry-bounded, so 5 is a floor |
| RBF0-F27 | The element and type-6 vocabularies are the engine's UI vocabulary. Of 1,092 name hashes stored by 13 decoded `PSIN` documents, 16 are reproduced exactly by the 2,539 distinct RBF0 names: 14 field names and 2 enum members, all generic (`Name`, `Type`, `Value`, `Data` and the like), and no structure name. A hash equality is a candidate, not a proof | `BINARY`, `CROSS_SAMPLE`, `SYNTHETIC` (the hash function) | Confirmed (measured) | 13 `PSIN` documents, one build; a 32-bit hash collides |

## Reproduction

Commands ran on 2026-11-25 with the `lforge` CLI built from `leonidaforge/leonida-forge` commit `6b362ad` and the release `0.1.0` binary. `<GAME_ROOT>` is a local installation, `<WORK>` a scratch directory outside it, and `<EXECUTABLE>` the game executable that matches the archive.

```text
lforge archive extract <GAME_ROOT>/data.rpf --row <N> --output <WORK>/nested<N>.rpf --executable <EXECUTABLE>
lforge archive manifest <WORK>/nested<N>.rpf --executable <EXECUTABLE> --format jsonl --output <WORK>/rows.jsonl
lforge archive extract <WORK>/nested<N>.rpf --row <ROW> --output <WORK>/payload.bin --executable <EXECUTABLE>
python tools/rbf0/rbf0_inspect.py <WORK>/payload.bin
```

The parser tests build synthetic documents:

```text
python -m unittest discover -s tools/rbf0 -p "test_*.py"
```

## Limits

- One build and one local archive set were examined. The nested selection is bounded at 2 MiB and is not random.
- No executable code path was traced. The document purpose, field semantics and root names are Unknown.
- Types 2 and 3 are zero-byte values in 21 observations. Type 5 has one 12-byte observation.
- Type 6 appears only in counted attribute positions in this population; whether it may also appear as a field value is Unknown.
- Attribute position is unresolved outside the counted prefix.
- The versionless variant has three samples.
- Text and names are game content and are not copied into this repository.
