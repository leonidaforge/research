# RDS5 verification evidence

Independent verification of the RDS5/ETPF research on `research/textures-rds5` at
branch tip `5a54ae8`. The source branch was read with `git show` and was not modified
or checked out.

The subject is the container layer only. No executable analysis was performed, no RAGE
resource relationship is claimed, and no pixel format or texture content is described.
Samples were opened read-only; no block payload was printed or stored.

## Sources

- `research/textures-rds5:formats/containers/rds5/README.md`
- `research/textures-rds5:formats/containers/rds5/specification.md` (finding IDs `RDS5-F01`..`RDS5-F19`)
- `research/textures-rds5:evidence/rds5/INDEX.md`
- `research/textures-rds5:tools/rds5/rds5.py` (SHA-256 `5e188058cf555a2964c77f8ae9186f6ebb5b5f6e9073f88bdec1dda3f2beff30`)
- `research/textures-rds5:tools/rds5/test_rds5.py` (SHA-256 `24dc12f149671ca91d8c6a3c60a98d45162217f01e05eaf127843c00ec046edb`)

## Evidence types

| Method | Type | Meaning |
|---|---|---|
| Header and record scan | `BINARY`, `CROSS_SAMPLE` | Fields read from all 57 samples and checked against file size and layout rules |
| Block read | `BINARY` | Stored span and codec selector of a named block; no payload output |
| Bounded inflate | `BINARY` | zlib inflation with a fixed output cap; sizes, end-of-stream and padding only |
| Negative decode | `BINARY` | A whole stored span offered to zlib and gzip at offset 0 and to raw DEFLATE at offsets 0 to 8 |
| Parser tests | `SYNTHETIC` | Branch tests on authored fixtures plus independent mutation cases |
| Arithmetic | `CROSS_SAMPLE` | A layout formula checked against every sample |

`BINARY` and `CROSS_SAMPLE` findings depend on a local `<GAME_ROOT>`. They are
private-evidence supported in the sense of `RESEARCH-POLICY.md` and reproducible from
any lawful copy of the same sample.

## Verification status

| Task | Result | Finding |
|---|---|---|
| 1. Sample count and total size | Reproduced: 57 files, 62,217,061,888 bytes | RDS5V-F01 |
| 2. Core invariants | Reproduced in 57 of 57 | RDS5V-F02, RDS5V-F03 |
| 3. Parser and tests | Reproduced: 33 tests pass | RDS5V-F05 |
| 4. Block codecs | zlib and non-zlib reproduced. LZ4 negative blocked: module unavailable | RDS5V-F07, RDS5V-F08 |
| 5. Entry fields and page counter | Reproduced on the reported file; no counterexample to the global bound | RDS5V-F12, RDS5V-F14 |
| 6. First-block flag | Reproduced in 57 of 57 | RDS5V-F13 |
| 7. Version differences | Reproduced: 39 and 18 samples, same structural rules | RDS5V-F04 |
| 8. Boundary conditions | Reproduced on synthetic files | RDS5V-F15 |

## Findings

| ID | Claim | Evidence | Confidence | Limits |
|---|---|---|---|---|
| RDS5V-F01 | Enumeration by `.ttpf` extension under `<GAME_ROOT>` returns exactly 57 files and 62,217,061,888 bytes. Sizes range from 38,656 to 2,828,296,704 bytes | Header scan (`BINARY`, `CROSS_SAMPLE`) | Confirmed | One installation. No exclusions. Extension selection, not content validation. Sizes match `RDS5-F01` inventory |
| RDS5V-F02 | In 57 of 57 files the magic is `RDS5`, the fixed header is 0x10 bytes, and `align_up(0x10 + 8*record_count, 0x100)` equals both the ETPF position and record 0's offset. Record offsets are 0x100-aligned and strictly increasing, and the last record equals the file size | Header and record scan, arithmetic (`BINARY`, `CROSS_SAMPLE`) | Confirmed | Value meanings outside the documented fields remain unknown. All 57 containers |
| RDS5V-F03 | In 57 of 57 files the ETPF magic is `ETPF`, the type word is `0x27A`, `field_m` is a multiple of 16, the entry table is inside the file, and the content end `pos + 0x10 + 0x20*N + M` does not pass the first block. The byte before the content end is nonzero and the byte at it is zero in 57 of 57 | Header scan, arithmetic (`BINARY`, `CROSS_SAMPLE`) | Confirmed (nonzero end), Probable (region length `16N + M`) | A longer region followed by zero padding cannot be excluded, so the length stays Probable. All 57 containers |
| RDS5V-F04 | `version` is `0x16000000` in 39 files and `0x16000001` in 18. The 18 are exactly the eight `maps_*_7`, eight `terrain_*_7` and two `vehicles_loose_*_1` files. Every structural rule in RDS5V-F02 and RDS5V-F03 holds within both groups (39 of 39 and 18 of 18). No structural field or formula differs | Header scan, arithmetic (`BINARY`, `CROSS_SAMPLE`) | Confirmed (values and invariants), Unknown (meaning of bit 0) | Observed value sets such as `field_m` differ between the groups, but they are content-dependent sizes, not layout rules. The sample does not prove that both versions are semantically equivalent |
| RDS5V-F05 | The branch parser passes its full suite: 33 tests, 0 failures, under Python 3.15.0. Tests cover parsing, rejection, limits, streaming and CLI output | Parser tests (`SYNTHETIC`) | Confirmed | The suite exercises the parser contract, not the actual format. A green suite does not confirm any field meaning |
| RDS5V-F06 | The branch tool reproduces the published sample summary: `files=57 failures=0 blocks=1026833 entries=357115 layout_mismatches=0`, and `zlib=918223 other=108610` with `--codecs`. `inspect` of `data/ttdb/ui/platform.ttpf` block 0 reports one zlib block and 524,288 uncompressed bytes | Header, record and block scan (`BINARY`, `CROSS_SAMPLE`) | Confirmed | Structural parse and one inflation. No content is interpreted |
| RDS5V-F07 | A zlib block reproduces on `data/ttdb/ui/platform.ttpf` block 0: `high_byte` `0x60`, selector 0, first byte `0x78`, 218,624 stored bytes, clean end-of-stream, 524,288 output bytes (128 * 0x1000), 213 trailing bytes all zero | Block read, bounded inflate (`BINARY`) | Confirmed | One named block. The branch's 2,173-block inflation census was not re-run |
| RDS5V-F08 | Non-zlib blocks reproduce on named files. `data/ttdb/ui/ttdb_ui.ttpf` block 139 carries `high_byte` `0x50` (selector 0) and starts with `0x34`; `data/ttdb/graphics/ttdb_graphics.ttpf` block 114 carries `high_byte` `0x54` (selector 1) and starts with `0x36`. Both spans fail zlib and gzip at offset 0 and raw DEFLATE at offsets 0 to 8 with a whole-range criterion | Block read, negative decode (`BINARY`) | Confirmed (negative results), Unknown (codec) | Two blocks. LZ4 was not tested because no LZ4 module is installed, so the branch's LZ4 negative is not independently reproduced. Negative results do not identify the codec |
| RDS5V-F09 | The first-byte census matches: 918,223 blocks start `0x78` and all have second byte `0xDA`; 108,610 do not start `0x78`. Low nibble totals are `0x0`: 918,305, `0x4`: 103,058, `0x8`: 268, `0xC`: 5,202. Exactly 82 selector-0 blocks lack a zlib header: 79 in `ttdb_ui`, 2 in `weapon_liveries`, 1 in `ttdb_vehicles`. Their high bytes are `0x10`, `0x40`, `0x50`, `0x80`, `0x90`, `0xD0`; 77 start `0x30`-`0x36` then `0xDE`, 5 start otherwise | Block read (`BINARY`, `CROSS_SAMPLE`) | Confirmed (observation), Unknown (storage form) | First two bytes only. All 1,026,833 blocks. The 82 remain an unexplained form or flag exception |
| RDS5V-F10 | Selector 2 `((high_byte >> 2) & 3) == 2` covers 268 non-zlib blocks, all with `high_byte` `0x18`. The branch text names selectors 1 and 3 as the unidentified codec but omits selector 2, although its nibble table lists the `0x8` group | Block read (`BINARY`, `CROSS_SAMPLE`) | Confirmed (observation) | Documentation gap, not a contradiction of the counts. The 268 blocks are not decoded |
| RDS5V-F11 | Block-record second word `hi[16:32]` takes 19,174 distinct values with maximum `0xFFF3` across 1,026,833 block records | Record scan (`BINARY`, `CROSS_SAMPLE`) | Unknown | Distribution reproduced. No checksum or hash identification. All 57 containers |
| RDS5V-F12 | On `pack/core_restofworld001/data/ttdb/ui/ttdb_ui.ttpf` the low 16 bits of entry `+0x08` are `1, 0x11, 0x21, 0x31, 0x41`; the five blocks inflate to 0x10000 bytes each; each step is 16 pages, so one page is 0x1000 bytes. `uncompressed_total = 0x1000 + sum(block sizes)` holds exactly. Across all files the largest consecutive page delta modulo 65536 is `0x1560`, with no value above it | Header scan, bounded inflate, arithmetic (`BINARY`, `CROSS_SAMPLE`) | Confirmed on the named file; Probable generally | Direct size correspondence is shown on one file only. The global check supports a wrapping counter but does not map entries to blocks. No counterexample to the `0x1560` bound was found |
| RDS5V-F13 | The first block equals `pos + align_up(0x10 + 0x20*N + M, 0x1000) + 0x100 * (record0.second_word >> 28)` in 57 of 57 files. The term is 0 in 55 files, `0x100` in `data/ttdb/maps/ttdb_maps_0_7.ttpf` (`0x10000000`) and `0x200` in `data/ttdb/vfx/ttdb_vfx.ttpf` (`0x20000000`) | Header scan, arithmetic (`BINARY`, `CROSS_SAMPLE`) | Confirmed (relation), Unknown (flag meaning) | Reading the term as a count of 0x100-byte units is unproven. The relation must not be enforced by a reader |
| RDS5V-F14 | Entry fields reproduce the published value sets: `w0` 202 distinct values, `w1` 133, `w2` 349,703, `w3` 24. `w0` low 16 bits equal `0xC000 \| ((1 << k) - 1)` in 357,114 of 357,115 entries; the exception is entry 832 of `data/ttdb/graphics/ttdb_graphics.ttpf` with `w0 = 0x100040FF`. `w1` high 16 bits range `0x0020`..`0x1320`; `w3` splits 16/12 | Header scan (`BINARY`, `CROSS_SAMPLE`) | Confirmed (observation), Unknown (meaning) | Value sets only. No field is shown to be a texture descriptor or a block reference |
| RDS5V-F15 | The branch parser rejects a truncated header, a record array larger than the file, a wrong ETPF type, a `field_m` that is not a multiple of 16, a wrong magic and an unsupported version, each with the expected error text | Parser tests (`SYNTHETIC`) | Confirmed | Authored fixtures and mutations, not adversarial fuzzing. This is parser behavior, not format evidence |

## Block codec detail

| File | Block | `high_byte` | Selector | First bytes | Stored | zlib result |
|---|---:|---:|---:|---|---:|---|
| `data/ttdb/ui/platform.ttpf` | 0 | `0x60` | 0 | `78 DA` | 218,624 | 524,288 bytes, end-of-stream, 213 zero tail |
| `data/ttdb/ui/ttdb_ui.ttpf` | 139 | `0x50` | 0 | `34 DE` | 7,424 | not zlib or gzip at 0; not raw DEFLATE at 0..8 |
| `data/ttdb/graphics/ttdb_graphics.ttpf` | 114 | `0x54` | 1 | `36 DE` | 19,712 | not zlib or gzip at 0; not raw DEFLATE at 0..8 |

The two non-zlib attempts used the whole-range rule: the decoder must reach
end-of-stream with no unused tail. Leaving an unused tail does not count as a match.
The LZ4 attempt is not reported because the module is unavailable.

## Version comparison

| Property | `0x16000000` | `0x16000001` |
|---|---:|---:|
| Files | 39 | 18 |
| ETPF type | `0x27A` | `0x27A` |
| `field_m % 16 == 0` | 39 of 39 | 18 of 18 |
| Record 0 equals ETPF position | 39 of 39 | 18 of 18 |
| Last record equals file size | 39 of 39 | 18 of 18 |
| Offsets aligned and increasing | 39 of 39 | 18 of 18 |
| First-block relation holds | 39 of 39 | 18 of 18 |
| `uncompressed_total` multiple of 0x1000 | 39 of 39 | 18 of 18 |
| `high_byte` distinct values | 30 | 19 |
| Selector 2 count | 268 | 0 |
| Page delta maximum | `0xC00` | `0x1560` |

No layout rule differs between the groups. Observed value sets differ because the
`0x16000001` group has no small containers and no selector-2 blocks. Whether the
version bit changes any runtime behavior is **Unknown** and cannot be answered from
container bytes alone.

## Readiness for texture work

Implementation-ready from this research:

- enumerating `.ttpf` samples and reading sizes without touching payloads;
- parsing the 0x10-byte header and the record array with bounds checks;
- locating the ETPF chunk, entry table and first block;
- extracting zlib blocks whose first byte is `0x78`, with an output cap and a required
  end-of-stream;
- rejecting the malformed cases in RDS5V-F15.

Not implementation-ready:

- any mapping from ETPF entries to blocks or textures. Entry meanings are unknown, and
  entry count equals block count in only 3 of 57 files;
- any non-zlib block. Selectors 1, 2 and 3 plus the 82 selector-0 exceptions have no
  identified codec;
- the `16N + M` region after the entry table;
- the meaning of the version bit, the first-block flag and the second word's high
  16 bits.

The verified layer supports a container reader and raw block extractor. It does not
support texture export, pixel-format selection or asset naming. The branch makes no
RAGE resource claim, and this verification found no evidence for one.

## Not reproduced or blocked

- LZ4 negative decoding: no LZ4 module is installed, so the branch's LZ4 result was not
  re-run.
- The 2,173-block zlib inflation census: not re-run. This verification inflated one
  named zlib block and the five blocks of the page-counter file.
- Entry-to-block association: not attempted, because the format does not expose it and
  the branch states it is unknown.

## Reproduction

The branch tools were extracted to a scratch directory outside the repository, so the
texture worktree stayed untouched.

```sh
mkdir -p "$TMP/rds5"
git show research/textures-rds5:tools/rds5/rds5.py > "$TMP/rds5/rds5.py"
git show research/textures-rds5:tools/rds5/test_rds5.py > "$TMP/rds5/test_rds5.py"
cd "$TMP/rds5"
python -m unittest discover -s . -p "test_*.py" -v
```

Expected: `Ran 33 tests ... OK`.

```sh
python "$TMP/rds5/rds5.py" scan "<GAME_ROOT>"
python "$TMP/rds5/rds5.py" scan "<GAME_ROOT>" --codecs
python "$TMP/rds5/rds5.py" inspect "<GAME_ROOT>/data/ttdb/ui/platform.ttpf" --block 0 --inflate
```

Expected summaries:

```text
files=57 failures=0 blocks=1026833 entries=357115 layout_mismatches=0
files=57 failures=0 blocks=1026833 entries=357115 layout_mismatches=0 zlib=918223 other=108610
```

Expected `inspect` block result: `codec: zlib`, `uncompressed_bytes: 524288`.

The remaining findings come from an independent read-only parser that read the header,
record array, ETPF header and table, one byte at each side of the content end, and the
first two bytes of every block. It wrote no input and printed no payload. Python
3.15.0, standard library only.
