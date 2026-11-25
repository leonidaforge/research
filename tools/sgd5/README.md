# SGD5 structural sampler

`sgd5_inspect.py` reports the fields that two SGD5 payloads share. It reads
each input read-only, refuses to write output inside an input directory, and
prints only header fields, sizes, entry counts, kind counts and record counts.
It is a bounded sampler, not a format validator.

## Usage

```sh
python tools/sgd5/sgd5_inspect.py <SAMPLE> [<SAMPLE> ...]
python tools/sgd5/sgd5_inspect.py <SAMPLE> [...] --json --output <REPORT>
```

All paths are required. The tool has no default pointing at a game installation.
`--max-bytes` (default 2 GiB) and `--max-blocks` (default 100,000) bound the
read and the declared block count.

## Output

- Input size and SHA-256.
- Header words at `+0x04`, `+0x08`, `+0x0C` and `+0x10`.
- Every declared table block: offset, byte length, entry count, descriptor,
  whether the entry index is sequential, the entry-kind histogram, and the
  distinct/minimum/maximum entry values.
- The block after the table list: offset, length, whether that length equals the
  remaining file size, and whether its trailing word is zero.
- The data-region offset, the number of 24-byte records with a duplicated first
  word, the offset where that stride breaks, and the longest printable run near
  the break.

The tool does not print payload text, decode the data region or assign any
field a meaning.

## Dependencies

- Python 3.11 or later, standard library only.

## Tests

```sh
python -m unittest discover -s tools/sgd5
```

The tests build synthetic SGD5 inputs and do not read game files.
