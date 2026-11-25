# PSIN classifier

`psin_inspect.py` reports the PSIN outer framing, the family grammar, the `LSCH` descriptor count and the `CHKS` integrity result. It reads each input read-only and prints header fields, offsets, tags, lengths, counts and hashes. It is a structural classifier, not a body decoder.

## Usage

```sh
python tools/psin/psin_inspect.py <SAMPLE> [<SAMPLE> ...]
python tools/psin/psin_inspect.py <SAMPLE> [...] --json
```

All paths are required. The tool has no default pointing at a game installation. `--max-bytes` (default 2 GiB) and `--max-sections` (default 10,000) bound the read and the section walk.

## Output

- Input size and SHA-256.
- First-section offset read as a big-endian `u32` at `+0x04`, its high and low 16-bit halves, the big-endian `u16` at `+0x06`, and the eight bytes at `+0x08..+0x0F`.
- Family from the first section tag: `LSCH`, `PMAP`, `OTHER`, or null when the walk is empty. `first_tag` reports the raw tag bytes.
- Every tagged section: tag, offset, byte length, body length and body length modulo 16.
- For `LSCH`: descriptor count, whether the count solution is unique, the descriptor list, the aligned-length sum and the formula result. Four candidate variants are reported under `family_data.variants`.
- For `PMAP`: the pre-section length, the `0x70` marker flag, a pre-section SHA-256 and any embedded magic strings. The family is reported as a separate grammar, not as a failed parse.
- `CHKS`: total-length word, stored and computed checksum, the `zppp` tail, and whether the checksum verifies.

The tool does not decode section bodies or print payload text.

## Tests

```sh
python -m unittest discover -s tools/psin
```

`tools/psin/synthetic.py` writes the synthetic fixtures used by the tests:

```sh
python tools/psin/synthetic.py <output-directory>
```

The fixtures include a valid `LSCH` document, a `PMAP` document, an unaligned `PMAP` document and a corrupted payload that must fail the checksum. They contain no game files.

## Limits

- The descriptor relation is validated only on the `LSCH` family.
- The `PMAP` pre-section grammar is undecoded.
- The checksum seed is unexplained.
- Tag and body meanings are not assigned.
