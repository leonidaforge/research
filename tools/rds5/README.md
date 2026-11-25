# rds5

Read-only structural parser for [RDS5 containers](../../formats/containers/rds5/README.md)
and their ETPF chunk. It validates the layout, bounds-checks every record, and can
inflate a single zlib block with an output cap. It prints offsets, sizes, counts and
flag bytes only; block payload bytes are never printed. It does not identify the
non-zlib codec and does not decode texture content.

## Requirements

- Python 3.8 or later. Standard library only (`argparse`, `struct`, `zlib`, `os`,
  `json`).

## Usage

```sh
python tools/rds5/rds5.py inspect PATH [--json] [--records] [--block N] [--inflate]
python tools/rds5/rds5.py scan ROOT [--json] [--codecs]
```

`inspect` parses one file. `--records` adds every decoded record (index, offset, high
byte, second word). `--block N` reports block `N` (0-based among block records);
`--inflate` also decompresses it and prints the uncompressed size.

`scan` walks `ROOT` for `*.ttpf` and parses each file. `--codecs` additionally reads
the first byte of every block to count storage forms; this costs one read per block.

Limits, all overridable on the command line:

| Option | Default | Effect |
|---|---|---|
| `--max-file-size` | 8 GiB | Refuse larger inputs |
| `--max-records` | 2,000,000 | Refuse a larger `record_count` |
| `--max-etpf-entries` | 2,000,000 | Refuse a larger ETPF entry count |
| `--max-block-bytes` | 256 MiB | Refuse a block whose stored span is larger |
| `--max-uncompressed` | 64 MiB | Decompression output cap for `--inflate` |

The padding between the ETPF content and the first block is scanned in 1 MiB pieces, and
`--inflate` decompresses straight from the file without loading the stored block. A
malformed input cannot force an allocation proportional to the file size.

Exit codes: 0 on success, 1 on the first structural violation (and, for `scan`, if any
file fails).

## Output

`inspect` prints `key: value` lines, or a JSON object with `--json`. Fields:

| Key | Meaning |
|---|---|
| `path` | Input path as passed on the command line |
| `size` | File size in bytes |
| `version` | RDS5 version word, `0x16000000` or `0x16000001` |
| `record_count` | Number of 8-byte records |
| `block_count` | `record_count - 2` |
| `uncompressed_total` | Header field at `0x08` |
| `etpf_offset`, `etpf_type`, `entry_count`, `field_m` | ETPF chunk fields |
| `etpf_data_end` | End of the nonzero ETPF content |
| `etpf_align_end` | `etpf_offset` plus the content length rounded up to 0x1000 |
| `flag_extra` | `0x100 * (record 0 second word >> 28)`, the observed extra before the first block |
| `layout_matches_observed` | Whether `first_block` equals `etpf_align_end + flag_extra` (reported, not enforced) |
| `padding_bytes` | Zero bytes between the content end and the first block |
| `first_block` | Offset of the first data block |
| `offsets_in_bounds` | Whether every record offset lies inside the file |
| `codecs` | Count of `zlib` and `unknown` blocks |
| `records` | Present with `--records`: index, offset, high byte, second word per record |
| `block` | Present with `--block`: index, block span, codec, and uncompressed size with `--inflate` |

`scan` prints one tab-separated line per file, including `layout=ok` or `layout=MISMATCH`
for the observed first-block relation, and a summary line. The summary reports
`files`, `failures`, `blocks`, `entries` and `layout_mismatches`; with `--codecs` it
also reports `zlib` and `other` block totals. A layout mismatch is reported, not
counted as a failure.

## Tests

```sh
python -m unittest discover -s tools/rds5 -p "test_*.py"
```

The tests build synthetic containers in a temporary directory. They cover a valid
round trip, both version values, every rejection path (magic, truncation, version,
count limits, misplaced ETPF, bad type, non-multiple `field_m`, disordering, wrong end
record, non-zero padding), the decompression cap and block-span limit, truncated
streams, non-zlib blocks, an 8 MiB gap that must be scanned without allocating it, and
`scan` output for a layout mismatch with and without `--codecs`. No game files are
needed.
