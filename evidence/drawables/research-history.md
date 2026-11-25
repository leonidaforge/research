# Drawable research history

Interpretations that were checked against the samples and not adopted. The
current model is in the [format document](../../formats/resources/drawables/README.md).

## Two header fields were expected in one sample only

**Candidate.** The four `f32` at `+0x70` and the list pointer at `+0xB0` were
expected to appear in one sample and not the other, so a parser would treat them
as optional or version-dependent.

**Correction.** Both fields are present in both samples (DRAW-F07, DRAW-F08).
The `+0x70` block in sample A holds the sentinel `9998` four times; sample B
holds three distances and `9998`. The `+0xB0` pointer targets the same five
record shape in both. The genuine optional field found in this pair is the
shader-group `+0x08` pointer, which is nonzero in A and zero in B. A parser MUST
still treat every pointer slot as nullable, but it MUST NOT drop `+0x70` or
`+0xB0` on the assumption that one sample lacks them.

## The packed vertex count was expected to end in 1

**Candidate.** The layout's packed word was read as `vertex_count << 10 | 1`.

**Correction.** The high bits give the vertex count, but the low ten bits are
`0x51` in A geometry 1 and `0x61` in the other nine geometries (DRAW-F13). The
low bits are uninterpreted flags. A parser MUST mask off the high bits for the
count and MUST NOT require `1` in the low bits.

## The material counts were read as one drawable-wide set

**Candidate.** Sample A was reported as six texture parameters, 55 total
parameters, five bound slots, one declared-but-unbound slot and five distinct
keys.

**Correction.** Those values match A shader 0. A shader 1 separately declares
six texture parameters and 54 total, binds four slots, leaves two unbound and
has four distinct keys (DRAW-F18). The union of the two shaders has six distinct
keys. The counts are per shader; the drawable does not have a single declared
and bound count.

## Sample B has two geometries per model

**Addition.** The reported observation says sample B has four populated LOD
slots, each with one model. The records also give each model two geometry
pointers, so B has eight geometries in total (DRAW-F05). The reported statement
is not contradicted; it stops at the model count.

## The graphics pointer was expected to start with packed descriptors

**Candidate.** The first 16 `u32` words at the graphics pointer were read as
attribute descriptors of the form `format | size << 3 | offset << 7`.

**Correction.** Each vertex-buffer graphics target begins with a 0x80-byte
prefix whose first four bytes are `42 40 00 00`. The attribute offsets, sizes and
format codes are in the layout reached from the vertex buffer's `+0x40` pointer,
as separate 52-entry arrays (DRAW-F12, DRAW-F21). The first 16 words were not
parsed as descriptors and the packed descriptor form was not observed.
