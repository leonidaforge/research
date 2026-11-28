# 0DRP research history

Corrections to the reading of the resource form, with what displaced each one. The findings they belong to are in [INDEX.md](INDEX.md).

## Another resource form, not another format

The form was first treated as an independent serialization: a header, a table of blocks and a reference scheme of its own. Comparing its schema records with a `PSIN` container's showed the same 32-byte structure record, the same 16-byte field record and the same type-word split, with one substitution — a pointer to the field records where the container stores eight `0xAA` bytes. The `0xAA` and `0xEE` markers in the container stand where a resource stores pointers.

So this is the same self-describing metadata in a different container, and the two forms must be read with one vocabulary. The reading of the type codes therefore comes from the container's width table, with the two exceptions a pointer-sized field forces (`0x42` and `0x65` are 8 bytes here).

## The reference shift

The first reading of a reference was `(offset << 16) | block`. Resolving text references against the string pool showed the offset must be a byte offset, which only works with a 20-bit shift: `(offset << 20) | block`, the low 20 bits holding the block number. With the 16-bit shift every target lands in the wrong place, and a payload large enough to expose it fails loudly on block numbers above 16.

## Arrays that look like the container's and arrays that do not

`0x52` arrays store `{u64 reference, u16 length, u16 capacity, u32 zero}`, exactly as the container form does, which suggested all arrays did. They do not: `0x5C` arrays and `0x75` maps store `{u32 length, u32 capacity, u64 reference}` — the words reversed and widened. Reading a `0x5C` array as the container shape yields a length taken from the reference's low half.

## Block type words that are structure names

A first pass treated every block type word as a type code and reported the mass of blocks it could not classify. Most of them are not codes at all: a block whose type word equals one structure's name holds that structure's records, and its length divides by the structure's record size. With that rule the population's block table is almost entirely accounted for, and 194 distinct type words appear instead of a handful of codes and thousands of failures.

A related correction: a block typed by a field code is a legitimate pool of that type's elements, not an unreadable block. Reading such blocks as pools of scalars removed the array-element failures an early model reported.

## The header word at +0x20

The `u32` at `+0x20` was recorded as a count of roots, and later as a word of unknown meaning, because it does not match the number of roots a reference walk derives — most resources derive one root and store 2. It is neither a count nor unknown: it is the block number of the root, counted from one, and the reference walk reaches exactly that block in 15,768 of 15,768 resources. The mismatch that made it look like a count was against the number of roots, not against the root's block number.

## The census count of 1,286

The earlier census reported 1,286 resources of this form and a later recursive walk reported 15,768. Neither is wrong. The census classified rows from their head in the archives on disk and counted type 11 rows only; the walk enters nested archives and counts every row that carries the tag, which adds 14,482 type 111 rows. The number to quote depends on the population being described, and the difference is document type, not a decoding success.
