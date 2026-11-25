# PSIN structural sampler

`psin_inspect.py` reports the PSIN magic, the header words at `+0x04` and
`+0x08..+0x0F`, and the tagged-section walk that starts at the big-endian
offset stored at `+0x04`. It reads each input read-only and prints only header
fields, offsets, tags, lengths and counts. It is a bounded sampler, not a
format validator.

## Usage

```sh
python tools/psin/psin_inspect.py <SAMPLE> [<SAMPLE> ...]
python tools/psin/psin_inspect.py <SAMPLE> [...] --json
```

All paths are required. The tool has no default pointing at a game
installation. `--max-bytes` (default 2 GiB) and `--max-sections` (default
10,000) bound the read and the section walk.

## Output

- Input size and SHA-256.
- The first-section offset read as a big-endian `u32` at `+0x04`, its high and
  low 16-bit halves, the big-endian `u16` at `+0x06`, and the eight bytes at
  `+0x08..+0x0F` as raw hex plus big-endian and little-endian integer readings.
- Every tagged section from the first offset: tag, offset, byte length,
  body length and body length modulo 16. The length includes the 8-byte tag and
  length header.
- Checks for an unaligned first offset, `+0x06` equal to the payload size,
  `+0x06` equal to the low 16 bits of the first offset, and a section walk that
  ends at the file size.

The tool prints the tag bytes because they are part of the observed structure.
It does not decode section bodies, print payload text or assign any field or tag
a meaning.

## Dependencies

- Python 3.11 or later, standard library only.

## Tests

```sh
python -m unittest discover -s tools/psin
```

The tests build synthetic PSIN inputs and do not read game files.
