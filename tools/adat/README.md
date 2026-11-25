# ADAT inspector

`adat_inspect.py` checks the ADAT header, locates the 8-byte chunk-record run
and, with `--framing`, walks the `0x55` stream records in 2,048-byte blocks. It
reads each input read-only, refuses to write output inside an input directory,
and assigns no codec or stream identity.

## Usage

```sh
python tools/adat/adat_inspect.py <SAMPLE> [<SAMPLE> ...]
python tools/adat/adat_inspect.py <SAMPLE> [...] --framing --json --output <REPORT>
```

All paths are required. `--max-bytes` (default 64 MiB) bounds each read.
`--output` writes atomically outside the input directory.

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

## Stream descriptors

The framing walk reads two descriptor records. Neither field is given a codec
name.

| Record | Offset | Field |
| --- | --- | --- |
| `0x76` | `+0x00` | `u32` declared count |
| `0x76` | `+0x08` | low `u16` rate, high `u16` flags |
| `0x76` | `+0x1C` | codec byte in the first byte of the last `u32` |
| `0x48` | `+0x00` | `u32` page count |
| `0x48` | `+0x04` | `u32` page stride in bytes, a multiple of 2,048 |
| `0x48` | `+0x08` | `u32` sub-stream count |
| `0x48` | `+0x0C` | `sub-stream count` entries of 16 bytes |

A `0x48` entry is `[u32 unknown][u32 decoded][u32 rate_flags][u16 codec_word][u16 flags]`.
The record size must equal `12 + 16 * count`. `FF25` uses one `0x55` record for
all entries; the other variants pair one `0x76` with one `0x55` in record order.

## Framing

For a `0x55` record whose descriptor codec byte is not `0x02`:

- the record size must be a multiple of 2,048 bytes;
- each data block is a sequence of `u16 length` and `length` bytes;
- a zero length terminates the block and the rest of the block must be zero;
- a block that ends exactly at 2,048 bytes has no terminator;
- a length that would cross the block end is a violation.

For `FF25`, the stream is divided into pages of the `0x48` stride. A page starts
with a sentinel block (`u32` `0xFFFFFFFF`), may carry one or more metadata
blocks, then data blocks, then zero blocks to the page end. The page count must
equal the `0x48` field. The block classes are counted per page.

For a descriptor codec byte `0x02`, the tool reports
`size == 4 * declared` and does not walk packet lengths. Codec bytes other than
`0x0B` and `0x02` are reported but not framed.

## Record layout

Each record is a little-endian 64-bit word:

| Bits | Field |
| --- | --- |
| 63 to 56 | type byte |
| 55 to 28 | size |
| 27 to 0 | payload-relative offset |

The byte immediately before the data offset is the last record's type byte.

## Output

- Input size and content SHA-256. Input paths are shown by basename only.
- Flags, version, variant, stream count and data offset.
- Record start, record count, remainder, type-byte counts, first and last type,
  and the size range.
- The `FF02` chunk sum and formula result, or the `FF61` second offset.
- Boolean checks for flags packing, record-run end, nonzero sizes, extents and
  the last record type.
- With `--framing`: per-stream codec byte, rate, declared count, block counts,
  packet count, length range and histogram, TOC-shaped first-byte histogram,
  padding bytes, and every block-boundary violation with its block and offset.

No packet bytes or decoded audio are printed.

## Dependencies

- Python 3.11 or later, standard library only.

## Tests

```sh
python -m unittest discover -s tools/adat -p "test_*.py"
```

The tests build synthetic payloads for all four variants, a misaligned record
run, an overrunning record, a zero-size record, an unknown variant, a version
other than 1, a two-block `0x76` stream, a block-length overrun, nonzero
padding, a non-multiple `0x55` size, a `0x02` size relation, an `FF25` page
layout and a page-count mismatch. They do not read game files.
