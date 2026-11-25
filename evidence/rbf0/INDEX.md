# RBF0 evidence index

Payload observations from the Scarlett build [e95020b2](../../builds/gta-vi/scarlett-e95020b2/README.md). No executable code path was traced. Every finding is **Private-evidence supported**. Corrected interpretations are recorded in [research-history.md](research-history.md).

## Sample

| Property | Value |
| -------- | ----- |
| RBF0 files | 447 decoded payloads |
| Unique payloads | 238 by SHA-256 of the decoded bytes |
| Original nested archive | row 0 of `<GAME_ROOT>/data.rpf`, SHA-256 `91A236BCB4ECF96840BC0B70E22D1619C0FEDFA11976A336DE311A438214A09E`, 414544 bytes, 156 type 11 rows |
| Original rows | 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 72, 78, 90, 141, 154, 155 |
| Additional nested archives | 17 more RPF9 archives extracted from rows of `<GAME_ROOT>/data.rpf`, selected at or below 2 MiB stored size |
| Top-level rows | 9 type 11 rows from the top-level archives begin with RBF0 |
| Parse result | 238 of 238 unique payloads and 447 of 447 decoded occurrences consumed |

The original 18 rows remain a subset. Later archives were added to test the grammar, not to estimate a population. The sample is a convenience sample, not a random one.

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
| RBF0-F02 | Two header variants exist. The versioned form is magic, `u16 0xFFFB` at `+0x04`, `u16` version at `+0x06` (value 1 in every observed sample), then the token stream at `+0x08`; its numbers are 8 bytes. The versionless form starts the token stream at `+0x04`; its numbers are 4 bytes. Counts: 235 versioned and 3 versionless unique payloads. The old fixed 10-byte prefix reading conflated the header with the first token | `BINARY`, `CROSS_SAMPLE` | Confirmed (sample) | One build; only version 1 observed |
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
| RBF0-F15 | An independent token parser consumes 238 of 238 unique payloads and 447 of 447 decoded occurrences with no unsupported token. The previous private 31-payload selection is not published; the 18 nested rows are reproducible and all reachable top-level RBF0 rows add nine unique payloads | `BINARY`, `CROSS_SAMPLE`, `SYNTHETIC` | Confirmed (sample) | Selection is not the full game population |
| RBF0-F16 | Observed value widths: type 1 is the document number width (8 or 4 bytes); type 2 and type 3 carry no value bytes; type 4 is the document number width (8 or 4 bytes); type 5 is 12 bytes in its single observation; type 6 is `u16` length plus bytes. Counts are in the value table of the format document | `BINARY`, `CROSS_SAMPLE` | Confirmed (widths); Unknown (meaning) | Type 5 has one observation; types 2 and 3 have 21 observations together |
| RBF0-F17 | The versionless header appears in 3 of 238 unique payloads. All three parse with 4-byte numbers and the same token grammar | `BINARY`, `CROSS_SAMPLE` | Confirmed (sample) | Whether it is a stable family or a rare variant is Unknown |

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
