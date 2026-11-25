# PSIN classifier

`psin_inspect.py` reports the PSIN outer framing, the family grammar, the `LSCH` descriptor count, the `PMAP` block table, the `PSCH` table, the `LSCH`/`LENM` body structure and the `CHKS` integrity result. It reads each input read-only and prints header fields, offsets, tags, lengths, counts and hashes. It is a structural classifier, not a value decoder. It does not print payload text or block names.

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
- For `LSCH`: descriptor count, whether the count solution is unique, the descriptor list, the aligned-length sum and the formula result. Four candidate variants are reported under `family_data.variants`. The `LSCH` body marker run, tail length and `LENM` header summary are reported under `family_data.section_bodies`.
- For `PMAP`: the pre-section length, the `0x70` marker, the block table (mode, count, block ids, offsets, lengths), the per-block offset relation, the padding result, a name-block summary (count only, no strings), and the `PSCH` count, tiling and id-containment results. The family is reported as a separate grammar, not as a failed parse.
- `CHKS`: total-length word, stored and computed checksum, the `zppp` tail, and whether the checksum verifies.

The tool does not decode block or value internals and does not print payload text.

## Prediction record

`pmap_heldout.py` re-runs the padding comparison and writes the split record:

```sh
python tools/psin/pmap_heldout.py --samples <EXTRACTED_PAYLOAD_DIRECTORY> --json
python tools/psin/pmap_heldout.py --samples <DIRECTORY> --output heldout-record.json
```

It applies the no-trailing-pad and pad-after-last rules, records the 52 aligned labels, the ten unaligned labels and a seeded random reproduction split. The 52/10 split is a designed contrast, not a blind hold-out. `heldout-record.json` is the committed record for the 62-payload population. The tool needs the extracted payloads; it has no default path.

## Value and block probe

`value_probe.py` re-runs the `PSCH` value and block width, signature and decoder tests:

```sh
python tools/psin/value_probe.py --samples <DIRECTORY> --json
python tools/psin/value_probe.py --samples <DIRECTORY> --summary-only --output value-record.json
```

`value-record.json` is the committed record for the 62 `PMAP` payloads: 1,170 values and 521 blocks. The probe rejects an output path equal to the sample directory and writes atomically.

## Tests

```sh
python -m unittest discover -s tools/psin -p "test_*.py"
```

`tools/psin/synthetic.py` writes the synthetic fixtures used by the tests:

```sh
python tools/psin/synthetic.py <output-directory>
```

The fixtures include a valid `LSCH` document, a `PMAP` document, an unaligned `PMAP` document and a corrupted payload that must fail the checksum. They contain no game files.

## Limits

- The descriptor relation is validated only on the `LSCH` family.
- The `PMAP` block table and padding are decoded; the `PSCH` values and the block contents are bounded but not decoded.
- The `LSCH` body tail and the `LENM` chain and extra region are not decoded.
- The checksum seed is unexplained.
- Tag and value meanings are not assigned.
