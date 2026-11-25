# rage_resource

Reads a RAGE resource from an RPF9 payload, or from an already decoded resource, and reports its segments, pages and page map.

Each stored chunk is one RPF9 chunk in the observed encoding-2 resource rows. A chunk is a zlib stream or a raw page. A zlib page is one stream, except that a page larger than 32 MiB is stored as several streams; the declared page count resolves the grouping. The companion [page_reconstruct](#page_reconstruct) implements the corrected rule, including raw pages, without invoking the CLI.

The tool is a research instrument. It reads only, bounds every stream and the total inflated size, and reports what it cannot establish instead of guessing. The documented layout is in [formats/resources](../../formats/resources/README.md).

## Requirements

- Python 3.10 or later. Tested with CPython 3.15 on Windows.
- Standard library only: `argparse`, `dataclasses`, `json`, `struct`, `sys`, `zlib`.
- No network access and no game files for the tests.

## Usage

Stored entry:

```text
python rage_resource.py payload --file <ARCHIVE> --offset <ENTRY> --length <STORED_SIZE> [--json]
```

- `--offset` is the entry's payload offset from the RPF9 location record, not the first stream.
- `--length` is the entry's stored size. Both values come from the table of contents or from a recovery candidate range.
- `--max-stream` and `--max-total` bound inflation, defaulting to 256 MiB per stream and 512 MiB total.

Decoded resource:

```text
python rage_resource.py decoded --file <DECODED> --system-length <BYTES> [--json]
```

The decoded form has no stored page boundaries, so the system segment length must be supplied.

Exit code is 0 when the status is `complete`, 1 when it is `partial` or `unverified`, and 2 for invalid usage.

## Output

The text report lists the page map, the segment sizes, every page with its size and stream count, every stream with its archive offset and sizes, pointer counts and every issue.

The JSON report has the same values under:

| Field                          | Content                                                                          |
| ------------------------------ | -------------------------------------------------------------------------------- |
| `status`                       | `complete`, `partial` or `unverified`                                            |
| `page_map`                     | Offset, system and graphics page counts, byte length                             |
| `page_map_error`               | Code and detail when no valid map was found                                      |
| `system_size`, `graphics_size` | Decoded segment lengths                                                          |
| `pages`                        | Per page: index, segment, `size`, `streams`; `null` sizes in decoded mode        |
| `streams`                      | Per stored stream: offset, stored size, inflated size                            |
| `pointers`                     | Counts of decoded system and graphics values and of values outside their segment |
| `issues`                       | Codes and details                                                                |

Status vocabulary:

- `complete`: the map is valid, the declared page count matches the stored pages, and the page-size pattern holds.
- `partial`: the map is valid but pages are missing.
- `unverified`: the map is invalid, the counts or the page sizes do not fit, or the input is truncated.

`pointers_outside` never changes the status. Text, hashes and fill patterns match the pointer encoding.

Issue codes: `payload_error`, `not_a_resource`, `map_in_header`, `map_outside`, `map_nonzero`, `no_system_page`, `missing_pages`, `page_count`, `page_size`, `ambiguous_split`, `pointers_outside`.

## What it refuses

- A payload whose first 16 bytes are not zero, whose padding between streams is not zero, or whose first stream does not start with the resource header.
- A page map outside the system pages, a map with nonzero bytes outside the counts, or a map declaring no system page.
- A stream that does not reach end of stream, exceeds the per-stream cap, or pushes the total over the cap.
- A page count that does not match the derived pages is reported as an issue instead of being chosen silently.

## Tests

```text
python -m unittest discover -s tools/resources -p "test_*.py"
```

The 26 `rage_resource` tests build every input with `zlib` and `struct`. They cover a valid one-page-per-segment resource, a map in a later system page, a split 32 MiB page, a page of exactly 32 MiB, missing and extra pages, a page-size violation, an outside pointer, and the negative cases: truncated stream, zero system-page count, map outside the system data, nonzero slot, nonzero prefix, nonzero padding, stream and total caps, and data without a resource header.

The suite also holds 18 `page_reconstruct` tests, 8 `root_tables` tests, 22 `texture_dictionary` tests, 16 `pool_reference` tests and 1 `dictionary_census` test. All 91 tests pass with the standard library only.

## Limits

- Page sizes in decoded mode are unknown; the tool reports `null`.
- A page of exactly 32 MiB is ambiguous without the declared page count; the tool reports `ambiguous_split` when neither reading fits.
- Pointer values are counted, not interpreted. The tool does not resolve targets.
- The tool does not authenticate the RPF9 metadata and does not decode the payload transform. It expects the bytes it is given to be the stored chunks.
- The tool does not trace or model engine page allocation, which remains **Unknown**.

## page_reconstruct

Reconstructs a stored resource row independently of the CLI, including a raw last page.

```text
python page_reconstruct.py --file <ARCHIVE> --offset <PAYLOAD_OFFSET> --length <STORED_SIZE> [--logical-size BYTES] [--max-total BYTES] [--json]
```

- `--offset` is the entry's payload offset; the tool reads the 16-byte prefix itself.
- `--length` is the stored length of the entry.
- `--logical-size` is the RPF9 row's logical size when known. It decides whether a raw tail is part of the resource; without it, the declared page count decides.
- `--max-total` caps the reconstructed bytes across all chunks (default 512 MiB). A chain that exceeds it fails with a `payload_error` that names the cap and the observed total.
- Exit code is 0 when the status is `complete`, 1 for `partial` or `unverified`, and 2 for invalid usage.

The reconstruction:

1. reads every chunk after the 16-byte zero prefix;
2. reconstructs the page map from all system bytes, so a map in a later system page is readable;
3. groups zlib streams into pages, merging a stream of exactly `0x2000000` bytes into the page it continues;
4. classifies a raw last chunk from the declared page count and, when supplied, the declared logical size. A zlib header that does not inflate is a note, not a classifier. A raw chunk that the count and logical size require is a page even when its bytes are all zero;
5. splits a packed zlib stream only when the declared count and the `0x10000` size pattern force it, and records that the split is untested;
6. reports `partial` only when a declared page is absent.

The JSON report adds `chunks` with the stored offset, stored size, reconstructed size and kind, and pages carry `storage`: `zlib`, `split`, `raw` or `packed`.

The synthetic tests cover a two-page row with the map near the end of page 0, a single-page row, a missing declared page, a packed page, a raw tail that is not a page, an all-zero raw page required by the count, a zlib-like raw tail that does not inflate, a raw tail that breaks the logical size, a map in a second system page, a first page larger than 64 KiB, a split page, a page-size violation, the total cap across chunks, and malformed prefixes. A row without the raw second page reconstructs as `partial`; the same row with it reconstructs as `complete`.

## root_tables

A bounded reader for the 0DRP root header and the 16-byte records behind `+0x38`.

```text
import root_tables
root, issues = root_tables.parse_root(system_bytes, graphics_len)
```

- `parse_root` requires the zero first qword and the `0DRP` tag, resolves every nonzero root pointer inside the system segment, and returns the four `u16` fields.
- `walk_records` reads 16-byte records: a 4-byte value at `+0`, a 4-byte value at `+4` and a pointer at `+8`. The `+4` value is used as a length in the boundary check; its meaning is not established. The walk stops at the first record that does not fit. A target outside its selected segment is reported as `record_outside`, not resized.
- The module has no CLI and does not invoke the application. The tests cover a valid header, an out-of-bounds record table, a target outside its segment, a huge count, an out-of-bounds root pointer, a missing tag and a short buffer.

## texture_dictionary

Reads a texture dictionary: the hash and value arrays, the 0x70-byte records
and the allocation extents.

```text
python texture_dictionary.py --file <FILE> --offset <ENTRY> --length <STORED> [--logical-size BYTES] [--check-names] [--json]
python texture_dictionary.py --file <DECODED> --system-length <BYTES> [--check-names] [--json]
```

- The first form reconstructs a stored row with `page_reconstruct`, then parses
  the two segments.
- The second form reads an already decoded resource whose system length is
  known.
- `parse_dictionary(system, graphics_length)` is the library entry point. It
  raises `TextureDictionaryError` for a short root, a nonzero first qword, a
  missing page-map pointer, a count above the `max_records` argument, or an array
  that leaves the buffer. The default `max_records` is 65,536, above the `u16`
  maximum, so the default never triggers on a real count; a caller can pass a
  lower cap. Per-record problems are issues.
- The report gives the hash count, value count, record count and each
  capacity, every record's name hash, width, height, format id, mip count,
  allocation offset, raw unit count, allocation size and allocation extent, plus
  the in-bounds and partition tests.
- `allocation_size` is the extent to the next distinct allocation start, an
  upper bound. The `+0x08` value is a unit count whose byte scale is
  **Unknown**; the tool does not multiply it.
- `--check-names` reports only how many records' hashes equal the one-at-a-time
  hash of their ASCII name; the text is never printed. The hash folds `A`–`Z`
  and `\`, reads at most 64 bytes and skips a text without a terminator in that
  window.
- The tool does not decode pixels and does not map the format id to an enum.

The tests cover a valid two-record dictionary, the empty form, count mismatch,
capacities below the counts, unsorted and duplicate hashes, record pointers and
records outside the segment, allocation outside and duplicate starts, a raw
unknown format id, zero dimensions and mip bounds, the refusal cases, the folded
hash and the 64-byte window, a stored row through `page_reconstruct`, and the
JSON CLI.

## pool_reference

Reads the drawable shader texture-slot chain and reports slot references
separately from 0x5/0x6 pointers.

```text
python pool_reference.py --file <FILE> --offset <ENTRY> --length <STORED> [--logical-size BYTES] [--json]
python pool_reference.py --file <DECODED> --system-length <BYTES> [--json]
```

- `parse_shader_pool(system, graphics_length=None)` is the library entry point.
  It walks the shader group, each shader's parameter table and slot table,
  reads the first `texture count` parameter words, and reports each slot as
  `bound`, `null` or `bad`.
- `decode_slot_reference(value, slot_count)` splits a parameter word into the
  low-two-bit class and the slot index. `control_acceptance(values, slot_count)`
  applies the same rule to a control block.
- The report gives the shader count, texture-entry count, index-in-range count,
  bound/null/bad slot counts, the number of entries whose low class bits are
  nonzero, the 0x5/0x6 pointer counts with their system and graphics outside
  counts, and every reference.
- The shader array extent and each parameter and slot table extent are checked
  before the loops. A texture count above the declared parameter count is
  clamped to the parameter count and reported as `parameter_count`.
- A bound reference also reports the name record's 64-bit key and, when the
  name record's `+0x10` is `6`, its 32-bit dictionary namespace value. The tool
  does not resolve hashes to names or decode pixels.

The tests cover a bound slot and a null slot, a class mismatch, an index out of
range, a bad slot target, a parameter count below the texture count, a shader
array at the end of the segment, a clamped texture count with no table slack,
the shader cap, short and non-system buffers, an out-of-bounds parameter table,
the scalar control, and a stored row and the JSON CLI.

## dictionary_census

Reproduces the aggregates in [formats/resources/textures.md](../../formats/resources/textures.md).

```text
python dictionary_census.py --dictionary ARCHIVE LISTING [--dictionary ...] \
    --drawable ARCHIVE LISTING [--drawable ...] \
    --negative ARCHIVE LISTING TYPE [TYPE ...] [--json]
```

- A `LISTING` is the JSON object printed by `lforge archive ls <ARCHIVE> --json`.
  Rows are selected by the listing's `type_id`: 5 for dictionaries, 2 for
  drawables, and the type IDs given to `--negative`.
- The script reconstructs each selected stored row with `page_reconstruct`,
  parses dictionaries with `texture_dictionary` and walks drawables with
  `pool_reference`. It invokes no application code and reads the inputs only.
- The report holds the dictionary counts, format and mip distributions, the
  distinct-hash count and the hash multiplicity; the drawable slot counts, the
  distinct name values, the namespace matches, the per-drawable match counts,
  the matched-hash multiplicity, the DRAW-F18 overlap and the 64-bit key
  comparison; the negative accepted/rejected counts; and the seeded 10,000-value
  controls.
- The test builds a synthetic dictionary and a synthetic non-dictionary, runs the
  CLI and checks the dictionary, negative and control sections.
