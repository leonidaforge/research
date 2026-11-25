# GFX* structural sampler

`gfx_inspect.py` reports the decoded-payload fields that 49 `GFX*` payloads
share. It encodes the observed grammar: a little-endian size field, one of five
variant byte pairs, a constant pre-name run, a `u16` big-endian first-run length,
a 15-byte interstitial, a second run, an opaque body, and a fixed trailer.

It is an experimental sampler, not a format validator. It reads each input
read-only, refuses to write output inside an input directory, and prints only
offsets, lengths, variant bytes and counts. It does not print the ASCII runs.

An unknown variant, a mismatched size field, a missing constant run or a marker
that does not occur exactly once is an error. The tool therefore accepts only
the five variant pairs observed in the 49-row sample.

## Usage

```sh
python tools/gfx/gfx_inspect.py <SAMPLE> [<SAMPLE> ...]
python tools/gfx/gfx_inspect.py <SAMPLE> [...] --json --output <REPORT>
```

All paths are required. The tool has no default pointing at a game installation.
`--max-bytes` (default 64 MiB) bounds each read.

## Output

- Input size and SHA-256.
- Variant bytes at `+0x08` and `+0x0A`, and the first-run offset.
- The little-endian `u32` at `+0x04` and whether it equals the input size.
- Offsets and lengths of the pre-name run, first run, interstitial, second run,
  body, final run and trailer.
- The first three bytes of the interstitial's variable group.
- Whether the second run contains the first run and ends in `_Main`.
- Occurrence counts of the three constant markers.

The body is reported as an offset and a length only. Its contents are not
parsed, and no field is assigned a meaning.

## Dependencies

- Python 3.11 or later, standard library only.

## Tests

```sh
python -m unittest discover -s tools/gfx
```

The tests build synthetic payloads for the `0x88`, `0x80` and `0x70` variants
and do not read game files.
