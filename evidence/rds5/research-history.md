# RDS5 research history

## 2026-11-25: transfer from `research/textures-rds5`

The RDS5 container material was transferred from `research/textures-rds5` at branch
tip `5a54ae8`. The source branch was read with `git show` and was not rebased,
checked out or integrated. Each item below was classified before transfer.

| Source item | Subject | Classification | Current location |
|---|---|---|---|
| RDS5-F01 | Magic | Already on main as RDS5V-F02 | RDS5-F01 |
| RDS5-F02 | Fixed header | Already on main as RDS5V-F02 | RDS5-F02 |
| RDS5-F03 | Record array start and alignment; the two exact `0x10 + 8*C` samples | Confirmed-unintegrated detail; the aligned relation is already RDS5V-F02 | RDS5-F03 |
| RDS5-F04 | Record decode formula | Confirmed-unintegrated | RDS5-F04 |
| RDS5-F05 | Record roles and contiguity | Already on main as RDS5V-F02 and RDS5V-F03 | RDS5-F05 |
| RDS5-F06 | Version values and split | Already on main as RDS5V-F04 | RDS5-F06 |
| RDS5-F07 | ETPF chunk position and header fields | Positions already on main as RDS5V-F02 and RDS5V-F03; the field table is confirmed-unintegrated | RDS5-F07 |
| RDS5-F08 | ETPF entry table | Already on main as RDS5V-F03 | RDS5-F08 |
| RDS5-F09 | ETPF content end and region length | Already on main as RDS5V-F03; region length stays Probable | RDS5-F09 |
| RDS5-F10 | zlib first bytes and inflation | Already on main as RDS5V-F07 and RDS5V-F09 | RDS5-F10 |
| RDS5-F11 | Storage selector and negative codec results | Supported-with-limitations; the source omitted selector 2 and is superseded by the corrected table | RDS5-F11 |
| RDS5-F12 | Block-record counter and `uncompressed_total` | Supported-with-limitations; the counter is confirmed on two complete samples only | RDS5-F12 |
| RDS5-F13 | Upper 16 bits of the second word | Already on main as RDS5V-F11 | RDS5-F13 |
| RDS5-F14 | ETPF entry page counter | Supported-with-limitations; direct size correspondence on one sample | RDS5-F14 |
| RDS5-F15 | ETPF entry value sets | Already on main as RDS5V-F14 | RDS5-F15 |
| RDS5-F16 | 24-bit offset limit | Confirmed-unintegrated | RDS5-F16 |
| RDS5-F17 | First-block relation | Supported-with-limitations; relation confirmed, flag meaning Unknown | RDS5-F17 |
| RDS5-F18 | 82 selector-0 exceptions | Already on main as RDS5V-F09 | RDS5-F18 |
| RDS5-F19 | ETPF entry `+0x00` low-16 pattern | Already on main as RDS5V-F14 | RDS5-F19 |
| `tools/rds5/rds5.py` | Structural parser | Confirmed-unintegrated | [tools/rds5/rds5.py](../../tools/rds5/rds5.py) |
| `tools/rds5/test_rds5.py` | Synthetic parser tests, 33 cases | Confirmed-unintegrated; the suite passes under Python 3.15.0 | [tools/rds5/test_rds5.py](../../tools/rds5/test_rds5.py) |
| `tools/rds5/README.md` | Tool usage | Confirmed-unintegrated | [tools/rds5/README.md](../../tools/rds5/README.md) |
| `formats/containers/rds5/README.md` | Container overview | Confirmed-unintegrated | [formats/containers/rds5/README.md](../../formats/containers/rds5/README.md) |
| `formats/containers/rds5/specification.md` | Container specification | Confirmed-unintegrated | [formats/containers/rds5/specification.md](../../formats/containers/rds5/specification.md) |
| Per-file sample inventory | 57 paths, sizes and counts | Not transferred: a path list, and the aggregate counts are already on main | RDS5V-F01, RDS5V-F06 |
| LZ4 negative decoding | Non-zlib block test | Unsupported: independent verification could not reproduce it because no LZ4 module was available | Not carried |
| 0x100-byte header model | Small-file header impression | Superseded before transfer by the 0x10-byte header and record array | RDS5-F01, RDS5-F02 |

`RDS5-F01` to `RDS5-F19` keep the source order. The local application checks are
`RDS5-F20` to `RDS5-F22`.

## 2026-11-25: selector 2 added

The source text named selectors 1 and 3 as the unidentified codec and omitted selector
2, although its own low-nibble table listed the `0x8` group. The corrected selector
table now names value 0 as zlib with 82 exceptions, and values 1, 2 and 3 as
unidentified. Selector 2 covers 268 blocks, all with `high_byte` `0x18`. This is a
documentation gap, not a contradiction of the counts.

## 2026-11-25: confidence reduced where the sample is narrow

Three claims were narrowed during transfer:

- the block-record second-word counter is confirmed on two complete samples and
  **Probable** elsewhere;
- the ETPF entry page counter is confirmed on one five-entry sample and **Probable**
  generally;
- the ETPF region length stays **Probable** because a longer region followed by zero
  padding cannot be excluded.

The first-block relation is confirmed as a relation in 57 of 57 samples. The meaning of
its flag term remains **Unknown**, and a reader MUST NOT enforce the relation.

## 2026-11-25: local application check

Two representative claims were checked with the application CLI and the transferred
parser. The CLI reports `lforge 0.1.0`; its RDS5 parser and inspection path are
unchanged from `leonidaforge/leonida-forge` app commit `92af6e2`, and the local binary
was built from a later commit with no diff in that module or path.

- First-block relation with a nonzero flag term: the 238,897,664-byte vfx sample puts
  ETPF at `0x8E00`, content end at `0x23B70`, the 0x1000-aligned end at `0x23E00`,
  the flag term at `0x200` and the first block at `0x24000`. Both implementations
  agree.
- Entry page counter: the 38,656-byte five-entry sample holds pages
  `1, 0x11, 0x21, 0x31, 0x41`, five zlib blocks decode to 327,680 bytes, and
  `uncompressed_total` is 331,776. Both implementations agree.

No counterexample was found. The vfx application report shows 751,046,656 decoded zlib
bytes against the declared 766,107,648; the difference comes from 193 blocks with
unidentified selectors that are not decoded. That limits the `uncompressed_total`
check on that file but does not contradict the layout relation.
