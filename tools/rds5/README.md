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
python tools/rds5/rds5.py reconstruct PATH --descriptor N [--bytes-per-texel B --levels L] [--json]
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
stream; class `0x00` returns stored bytes. Every other observed class fails with
an explicit message. `--out` writes the decoded bytes to the given path.

`reconstruct` decodes every block whose virtual position falls in a descriptor's
range. With `--bytes-per-texel` and `--levels` it compares the decoded total with
the expected mip sizes and reports whether each level boundary falls on a block
boundary. It does not infer a block codec or a pixel format from a format id.

Limits, all overridable on the command line:

| Option | Default | Effect |
|---|---|---|
| `--max-file-size` | 8 GiB | Refuse larger inputs |
| `--max-records` | 2,000,000 | Refuse a larger `record_count` |
| `--max-etpf-entries` | 2,000,000 | Refuse a larger descriptor count |
| `--max-block-bytes` | 256 MiB | Refuse a block whose stored span is larger |
| `--max-uncompressed` | 64 MiB | Decompression output cap |

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
| `class_counts` | Block count per storage-class id |
| `headers` | With `--headers`: `zlib` and `other` first-byte counts |
| `records` | With `--records`: index, offset, class, page term, virtual position, padding, second word |
| `descriptors` | With `--descriptors`: index, dimensions, mip, flags, format id, array size, kind, tile mode, first page |
| `block` | With `--block`: class, span, padding, stream length, and with `--decode` the decoded size, consumed length and virtual length |

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
bit-24/25 record that must be rejected as out of model, both class-field readings,
virtual offsets including a sub-page term, a nonzero padding count, a size word
with bit 32 set, descriptor fields, sorted and unsorted key tables, a small mip
chain, every rejection path, the decompression cap, an 8 MiB gap scanned without
allocating it, and the CLI commands. No game files are needed.
