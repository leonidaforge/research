# drawable_inspect

Inspects a decoded drawable resource. It walks the header, LOD slots, model and
geometry records, vertex-buffer and index records, and the shader/material
chain. It reports offsets, counts, pointer resolutions, attribute descriptors
and key counts; it does not interpret vertex semantics, format codes, parameter
names or texture keys.

The input is a reconstructed RAGE resource: the system segment followed by the
graphics segment. The system length is required because the page map records
page counts, not byte lengths. Use the
[resource parser](../resources/README.md) to reconstruct a stored row, then pass
the decoded bytes and the system length here. The layout is documented in
[formats/resources/drawables](../../formats/resources/drawables/README.md).

## Requirements

- Python 3.10 or later. Tested with CPython 3.15 on Windows.
- Standard library only: `argparse`, `dataclasses`, `json`, `struct`, `sys`.
- No network access and no game files for the tests.

## Usage

```text
python drawable_inspect.py inspect --file <DECODED> --system-length <BYTES> [--json]
```

- `--file` is the decoded resource, not the stored archive row and not one
  segment on its own.
- `--system-length` is the byte length of the system segment. It must end where
  the graphics segment starts. A reader obtains it structurally, as described
  in the format document; the page map alone does not give it.
- `--json` prints the full report.

Exit code is 0 when the report status is `complete`, 1 when it is `partial` or
`unverified`, and 2 for invalid usage.

## Output

The text report lists the segment sizes, the page-map counts, the header bounds,
the LOD distances, every populated LOD slot with its models and geometries,
each vertex buffer with its declared size, vertex count, attribute count and
graphics offset, the graphics base, and the material counts.

The JSON report has the same values. The main fields are:

| Field            | Content                                                                    |
| ---------------- | -------------------------------------------------------------------------- |
| `status`         | `complete`, `partial` or `unverified`                                      |
| `page_map`       | Offset and the two page counts, when the header page-map pointer resolves  |
| `header`         | Header fields, bounds, LOD slots, distances, flags and unresolved values   |
| `lod_slots`      | One entry per populated LOD slot: model array, counts, shader indices, models |
| `materials`      | Shader group, shader records, parameter counts, bound slots and key counts |
| `graphics_base`  | Base derived from at least two vertex-buffer graphics pointers             |
| `issues`         | Codes and details                                                          |

Per geometry, `vertex_buffer_record` holds the element count, element unit,
declared bytes, graphics pointer, layout pointer, the parsed layout and the
declaration table. The declaration table is read from the graphics prefix: each
`u32` is a `u8` format byte and an `offset / 2`, and a zero word ends the table.
The layout holds `vertex_count`, `flags`, `attribute_stride`, `attribute_end` and
an `attributes` list of `{semantic, offset, size, format}`. `semantic` is the
zero-based index in the 52-entry table; it is not a recovered name.

Each model reports `aabb_record_count`, `aabb_aggregate`, `aabb_records` and
`aabb_union_matches`. The records are eight `f32` values each: `minimum.xyz`,
`minimum.x`, `maximum.xyz`, `maximum.x`. Record 0 is the aggregate, and a
one-geometry model stores only that record. The tool checks the union within
`2e-3`.

Each index buffer reports its first three `u32` as `header`, whether they match
the descriptor as `header_matches_descriptor`, and the longest ascending `u16`
run starting at zero as `sequential_run_length`. The run is cluster-local; it
is not a triangle list. The tool measures and bounds the index bytes; it does
not reconstruct triangles.

Each shader reports `shader_hash` (the `u32` at `+0x00`). Each parameter table
reports `key_join` with `direct_store`, `edup_indirection`, `null_key` and
`unresolved` counts. Every unbound slot is reported with key
`0x0000000000000000` and status `unbound`.

Issue codes include `input_cap`, `size`, `truncated_header`, `header_zero`,
`missing_pointer`, `pointer_outside`, `pointer_segment`, `pointer_undecodable`,
`pointer_read`, `array_outside`, `lod_group`, `lod_count`, `model`,
`model_count`, `aabb`, `aabb_union`, `geometry`, `vertex_buffer`, `buffer_size`,
`buffer_outside_graphics`, `declaration`, `layout`, `index_descriptor`,
`index_buffer`, `index_outside_graphics`, `index_header`, `shader_group`,
`shader`, `shader_constant`, `shader_count`, `parameter_table`,
`parameter_count` and `page_map`.

Status vocabulary:

- `complete`: every walked record resolved and the attribute ranges fit the
  declared buffer sizes.
- `partial`: a pointer or array could not be resolved, but the header and at
  least one chain element were read.
- `unverified`: the header is truncated or its zero word is nonzero.

## Graphics base

The graphics base is not stored. The tool derives it from at least two distinct
vertex-buffer graphics offsets whose targets land on the four-byte marker
`42 40 00 00`. Two geometries that share one graphics offset count once. For each
marker occurrence the tool subtracts a pointer offset; a base supported by both
distinct offsets is a candidate. If the candidate set contains the supplied
system length, that base is reported; a single other candidate is also reported;
several unrelated candidates are reported as ambiguous. The marker is an
observation, not a format signature.

## What it refuses

- A system length that is zero, negative or larger than the input.
- A record that would cross its segment boundary.
- A nonzero pointer that is not a decodable system or graphics value.
- A pointer whose upper 32 bits are nonzero, whose selector is not `5` or `6`,
  or whose offset is outside its segment.
- A model, geometry, shader or parameter count above the built-in cap.
- A pointer array that overruns the system segment; the report is partial.
- A shader whose `+0x04` word is not `0x6D657461`.
- A vertex-buffer attribute range that does not match the declared buffer
  bytes.

## Tests

```text
python -m unittest discover -s tools/drawables -p "test_*.py"
```

The tests build the system and graphics segments with `struct` and `bytearray`.
They cover a one-LOD drawable with two geometries, a four-LOD drawable, a null
LOD slot, overrunning model, geometry, shader and texture-slot arrays,
undecodable and segment-mismatched pointers, a page-map read across the system
boundary, a shared graphics pointer, a single shifted base and an ambiguous
base. They also cover the AABB record array and its union, the declaration
table and its layout offsets, the index header and ascending run, and the key
join counts. Negative cases include a truncated header, a nonzero header zero
word, an out-of-range geometry pointer, an out-of-range graphics pointer, a
declared buffer-size mismatch, a truncated index buffer and a declaration entry
that names no layout attribute. They do not use game files.

## Limits

- The tool does not verify the RPF9 metadata, inflate the stored chunks or
  reconstruct the segments. It expects the decoded bytes and the system length.
  The input is capped at 512 MiB.
- Vertex attribute semantics and format codes are reported as indices, codes and
  declaration bytes, not names. No position is decoded: the four 16-bit lanes
  are reported raw because the dequantization scale and origin are not
  established. The `0x80`-byte prefix is read only as the declaration table and
  as raw bytes.
- Material parameter hashes and 64-bit keys are opaque values. The tool does not
  read the name string a key record points to and does not resolve a key to a
  texture. The key join is exact for the decoded slots; a direct-store or EDUP
  match requires a texture store the tool does not read.
- The index buffer is measured, bounded and scanned for an ascending run; the
  cluster grammar is not resolved and no triangles are reconstructed.
- No engine code path was traced. Pointer validation, record allocation and
  runtime meanings remain unknown.
