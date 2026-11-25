# rds5

Read-only structural parser and bounded decoder for [RDS5 containers](../../formats/containers/rds5/README.md)
and their ETPF descriptor chunk. It validates the layout, bounds-checks every
record, decodes a block only when its storage class is known, and can map a
descriptor to its virtual block range. It prints offsets, sizes, counts and class
ids only; block payload bytes are never printed unless an explicit output path is
given.

## Requirements

- Python 3.8 or later. Standard library only (`argparse`, `struct`, `zlib`, `os`,
  `json`).

## Usage

```sh
python tools/rds5/rds5.py inspect PATH [--json] [--records] [--descriptors] [--headers] [--block N] [--decode]
python tools/rds5/rds5.py scan ROOT [--json] [--headers]
python tools/rds5/rds5.py descriptors PATH [--json]
python tools/rds5/rds5.py decode PATH --block N [--out FILE]
python tools/rds5/rds5.py reconstruct PATH --descriptor N [--bytes-per-texel B --levels L] [--max-total-bytes B] [--json]
python tools/rds5/textures.py probe PATH --descriptor N [--unit B8|B16|L4|L2|L1] [--levels N] [--decoder none|bc1|bc4|channels] [--json]
python tools/rds5/textures.py units
```

`inspect` parses one file. `--records` adds every decoded record. `--descriptors`
adds every descriptor. `--headers` reads the first byte of every block and counts
zlib headers. `--block N` reports block `N` (0-based among block records);
`--decode` decodes it by class and prints the consumed length.

`scan` walks `ROOT` for `*.ttpf`, parses each file and prints the class totals.
`--headers` additionally counts first-byte zlib headers; this costs one read per
block.

`descriptors` prints the descriptor field distributions and whether the key table
is strictly increasing. It never prints key values.

`decode` dispatches by storage-class id. Class `0x20` must be one complete zlib
stream; class `0x00` returns stored bytes and checks the declared virtual length.
Every other observed class fails with an explicit message. `--out` writes the
decoded bytes through a temporary file in the target directory and renames it
after a successful decode. It refuses a path that resolves to the input file.

`reconstruct` decodes every block whose virtual position falls in a descriptor's
range. With `--bytes-per-texel` and `--levels` it compares the decoded total with
the expected mip sizes and reports whether each level boundary falls on a block
boundary. It does not infer a block codec or a pixel format from a format id.
`--max-total-bytes` caps the cumulative decoded size; the cap is applied to each
block and to the running total.

Block and descriptor indices are checked against the parsed array before any
record or offset arithmetic. An out-of-range index raises a typed error that
names the index and the array length.

## Texture candidate analysis

`textures.py` reads one descriptor's decoded stream and reports candidate
structure, not a codec identity.

`probe` decodes every block in the descriptor's virtual range through `rds5`
and prints:

- descriptor fields, range, block indices, classes, decoded block sizes;
- the observed format-id storage unit from `units`;
- level counts whose reverse-order slot total equals the decoded extent;
- the levels that can be peeled from the end while each level start is an
  observed block boundary;
- optionally, the slot layout for a stated level count;
- optionally, a box-downsample error between consecutive block-aligned levels
  under the `bc1`, `bc4` or linear `channels` candidate decoder;
- first-byte statistics of 8-byte or 16-byte candidate blocks: distinct count,
  zero count, the fraction of block-first bytes that are multiples of 16, the
  same fraction over all bytes, and the lowest-set-bit histogram.

The last two items are structural discriminators. They never print pixel bytes
or write an image.

`mip_check.pass` is true only when at least two block-aligned levels were
decoded and every pair is below `--threshold` (default 25.0). Levels whose
start is not a block boundary are excluded and the stop reason is reported.
The tool does not infer a level count from the descriptor fields.

`units` prints the observed format-id storage units. They are size fits, not
codec names. Formats not in the table need `--unit`.

Limits, all overridable on the command line:

| Option | Default | Effect |
|---|---|---|
| `--max-file-size` | 8 GiB | Refuse larger inputs |
| `--max-records` | 2,000,000 | Refuse a larger `record_count` |
| `--max-etpf-entries` | 2,000,000 | Refuse a larger descriptor count |
| `--max-block-bytes` | 256 MiB | Refuse a block whose stored span is larger |
| `--max-uncompressed` | 64 MiB | Per-block decompression output cap |
| `--max-total-bytes` | 512 MiB | Cumulative decoded cap for `reconstruct` |

The padding between the ETPF content and the first block is scanned in 1 MiB
pieces, and zlib decoding reads straight from the file without loading the stored
block. A malformed input cannot force an allocation proportional to the file size.

Exit codes: 0 on success, 1 on the first structural violation (and, for `scan`, if
any file fails).

## Output

`inspect` prints `key: value` lines, or a JSON object with `--json`. Fields:

| Key | Meaning |
|---|---|
| `path` | Input path as passed on the command line |
| `size` | File size in bytes |
| `size_word`, `header_word` | Raw words at `+0x08` and `+0x0C` |
| `size_high_bit` | Bit 0 of `header_word`, the payload-size bit 32 |
| `payload_size` | `size_word | (size_high_bit << 32)` |
| `record_count`, `block_count`, `descriptor_count` | Counts |
| `etpf_offset`, `etpf_type`, `field_m` | ETPF chunk fields |
| `etpf_data_end` | End of the nonzero ETPF content |
| `etpf_align_end` | `etpf_offset` plus the content length rounded up to 0x1000 |
| `flag_extra` | `0x100 * (record 0 second word >> 28)` |
| `layout_matches_observed` | Whether `first_block` equals `etpf_align_end + flag_extra` (reported, not enforced) |
| `padding_bytes` | Zero bytes between the content end and the first block |
| `first_block` | Offset of the first data block |
| `extent_matches_payload_size` | Whether the end record's virtual position equals `payload_size` |
| `keys_strictly_increasing` | `true`, `false`, or `null` when the table has fewer than two keys |
| `ambiguous_class_records` | Number of records with bit 24 or 25 set |
| `class_counts` | Block count per storage-class id |
| `headers` | With `--headers`: `zlib` and `other` first-byte counts |
| `records` | With `--records`: index, 24-bit offset, 26-bit offset, class, class-ambiguity flag, raw six-bit value, page term, virtual position, padding, second word |
| `descriptors` | With `--descriptors`: index, dimensions, mip, flags, format id, array size, kind, tile mode, first page |
| `block` | With `--block`: class, span, padding, stream length, and with `--decode` the decoded size, consumed length and virtual length |

`reconstruct` reports the descriptor fields, range, block list, block boundaries
and decoded total. With `--bytes-per-texel` and `--levels` it adds the expected
level sizes, whether they match the total, and whether each level boundary falls
on a block boundary. It also reports `max_total_bytes`.

`scan` prints one tab-separated line per file and a summary. The summary reports
`files`, `failures`, `blocks`, `descriptors`, `layout_mismatches` and the class
totals; with `--headers` it also reports `zlib_headers` and `other_headers`. A
layout mismatch is reported, not counted as a failure.

## Tests

```sh
python -m unittest discover -s tools/rds5 -p "test_*.py"
```

The tests build synthetic containers in a temporary directory. They cover a valid
round trip, all eight class ids, explicit failure for the six undecoded classes, a
bit-24/25 record that must decode and be reported as ambiguous, both class-field
readings, a stored block whose payload is returned verbatim, a stored block whose
length mismatches the declared virtual length, virtual offsets including a
sub-page term, a nonzero padding count, a size word with bit 32 set, descriptor
fields, sorted and unsorted key tables, a small mip chain, block and descriptor
index bounds, refusal to overwrite the input, the cumulative reconstruction cap,
every rejection path, the decompression cap, an 8 MiB gap scanned without
allocating it, and the CLI commands. No game files are needed.

`test_textures.py` adds synthetic checks for the reverse-order slot layout, the
minimum slot, level peeling, the BC1 and BC4 block decoders, first-byte
statistics, a passing mip check, a deliberately broken level that must fail, and
the `probe` CLI.
