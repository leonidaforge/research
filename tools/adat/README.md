# ADAT inspector

`adat_inspect.py` checks the ADAT header, locates the 8-byte chunk-record run and
reports its type bytes, sizes and offsets. It reads each input read-only,
refuses to write output inside an input directory, and assigns no codec or
stream semantics.

## Usage

```sh
python tools/adat/adat_inspect.py <SAMPLE> [<SAMPLE> ...]
python tools/adat/adat_inspect.py <SAMPLE> [...] --json --output <REPORT>
```

All paths are required. `--max-bytes` (default 64 MiB) bounds each read.

## Checks

- `ADAT` at offset 0.
- A little-endian `u32` at `+0x04` with version 1 in the low 16 bits and one of
  the observed variants in the high 16 bits.
- A stream count at `+0x08` and a data offset at `+0x0C`.
- The per-stream table at `+0x10` (`FF21`, `FF25`, `FF02`) or a second offset at
  `+0x10` and the table at `+0x14` (`FF61`). For `FF21`, `FF25` and `FF61`, an
  `8 * streams + 4`-byte region follows the `u16` table and is skipped.
- The 8-byte record run that ends exactly at the data offset. The start is
  `+0x10 + 4 * streams` for `FF02`, `+0x14 + 10 * streams` for `FF21` and
  `FF25`, and `+0x18 + 10 * streams` for `FF61`.
- Every record has a nonzero size and an extent inside the payload.
- For `FF02`, the chunk counts in the high three bits of each `u32` at `+0x10`
  must satisfy `data_offset = 0x10 + 4 * streams + 8 * sum(chunks)`.

A record run that leaves a remainder, a zero-size record, an out-of-range
extent, an unknown variant or a failed `FF02` formula is an error.

## Record layout

Each record is a little-endian 64-bit word:

| Bits | Field |
| --- | --- |
| 63 to 56 | type byte |
| 55 to 28 | size |
| 27 to 0 | payload-relative offset |

The byte immediately before the data offset is the last record's type byte.

## Output

- Input size and SHA-256.
- Flags, version, variant, stream count and data offset.
- Record start, record count, remainder, type-byte counts, first and last type,
  and the size range.
- The `FF02` chunk sum and formula result, or the `FF61` second offset.
- Boolean checks for flags packing, record-run end, nonzero sizes, extents and
  the last record type.

## Dependencies

- Python 3.11 or later, standard library only.

## Tests

```sh
python -m unittest discover -s tools/adat
```

The tests build synthetic payloads for all four variants, a misaligned record
run, an overrunning record, a zero-size record, an unknown variant and a version
other than 1. They do not read game files.
