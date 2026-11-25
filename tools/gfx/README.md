# GFx container inspector

`gfx_inspect.py` checks the decoded header of a GFx container and walks its SWF
tag stream. It reports the container header, the bit-packed RECT size, the frame
rate and frame count, the first tag offset, the top-level tag count, bounded
nesting inside tag 39 and the final tag codes.

It is an experimental structural sampler, not a player, validator or
ActionScript decoder. It reads each input read-only, refuses to write output
inside an input directory, and prints only offsets, lengths, codes and counts.
It does not print payload bytes or movie strings.

## Usage

```sh
python tools/gfx/gfx_inspect.py <SAMPLE> [<SAMPLE> ...]
python tools/gfx/gfx_inspect.py <SAMPLE> [...] --json --output <REPORT>
```

All paths are required. The tool has no default pointing at a game installation.
`--max-bytes` (default 64 MiB) bounds each read.

## Checks

- `GFX` at offset 0, version `0x2A` at `+0x03`, and a little-endian `u32` length
  at `+0x04` equal to the input size.
- RECT size from `nbits = first_byte >> 3` and
  `ceil((5 + 4 * nbits) / 8)` bytes.
- A little-endian `u16` frame rate in 8.8 format and a `u16` frame count after
  the RECT.
- A tag walk from the first tag to the input end. A `u16` record header holds
  `code << 6 | length`, and a length of 63 reads a `u32` extended length.
- Tag 39 is the only body the walker reads further. In this sample its body
  begins with two `u16` values (four bytes) followed by a record stream; the
  values are not interpreted. The walk is bounded by `MAX_NESTING_DEPTH` and
  reports `unsupported nesting depth` with the tag offset when the bound is
  exceeded.
- The final four bytes must be the two zero-length tag headers for ShowFrame
  (code 1) and End (code 0).

An unknown version, a bad RECT, a mismatched length, a tag that overruns its
region, an unsupported nesting depth, trailing bytes after End, or a final four
bytes that are not those two headers is an error. The tool does not accept a
partial parse.

## Output

- Input size and content SHA-256. Input paths are shown by basename only.
- Container magic, version and length field.
- RECT `nbits` and byte size, frame rate, frame count and first tag offset.
- Top-level tag count, maximum nesting depth, tag 39 count, nested record count,
  first tag code and length, and the last two tag codes.
- The final four bytes and the two tag codes they encode.

Tag codes are reported as numbers. Only codes 0 and 1 are named, because the
walk needs them to stop and to check the final headers. Tag 39 is read only as a
bounded record stream; it is not named or assigned a meaning.

## Dependencies

- Python 3.11 or later, standard library only.

## Tests

```sh
python -m unittest discover -s tools/gfx
```

The tests build synthetic GFx payloads with short and long tag forms, bounded
tag 39 nesting, an unsupported nesting depth, a hostile extended length, a
truncated tag, a bad RECT, a version other than 42 and trailing bytes. They do
not read game files.
