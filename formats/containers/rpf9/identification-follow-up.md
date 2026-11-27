# RPF9 identification follow-up tasks

Five pieces of work the full census leaves measurable but unsolved. They are
separate investigations — none of them has to be finished before another
starts — but they are not independent. A and B both ask how a chunk stream is
framed and meet in the same decoder, so a finding in one changes what the other
is testing. C and E both describe resource containers: three of E's five types
are containers, so their layouts cannot be described before C's shared structure
is. D's filename work overlaps the name discovery and stringtable work this
repository already carries. None of the five is started by the classification
itself.

Every count here comes from the payload census of the installation — 22 root
archives, 4,373 archives, 1,255,039 entries — and can be reproduced with
`tools/rpf9/census_breakdown.py` on the merged census. Sample chains name the
row as `<root archive>!<row>` or `<root archive>!<outer row>!<inner row>`, with
the root given by its installation-relative path, so a chain can be opened from
the installation directory without searching for it.

## A. Chunk-encoding 4

**Solved.** The framing is established and every entry decodes. Encoding 4 is a
chunk-descriptor layout, not a compression algorithm: each chunk selects zlib or
copy. The 16-byte stored prefix that the decoder applied only to encoding 2 is
also present on encoding 4 when the entry's stored size exceeds the chunk stored
sizes by 16. The decoder now derives that length from the sizes. All 14,488
entries decoded to their declared logical size, and the 56 that decoded before
the change produce the same bytes. See
[chunk-encoding-4.md](chunk-encoding-4.md) and RPF9-F150 to RPF9-F153.

**Established before the fix.** 14,488 entries are stored with chunk encoding 4.
14,432 of them could not be decoded at all, and every entry the census could not
decode used this encoding: no undecodable entry had any other storage. The 56
that did decode were 55 `PSIN` rows of type 11 and one 15-byte row of type 255
whose payload is the text `FORCE_EMPTY_RPF`.

| Type        | Entries | Outcome before the fix        |
| ----------- | ------: | ----------------------------- |
| 15 (`zbdr`) |   4,768 | undecodable                   |
| 73 (`zmap`) |   4,087 | undecodable                   |
| 2 (`zdr`)   |   3,196 | undecodable                   |
| 6 (`zbn`)   |   1,654 | undecodable                   |
| 16 (`zbdd`) |     256 | undecodable                   |
| 4 (`zdd`)   |     256 | undecodable                   |
| 74 (`ztyp`) |     173 | undecodable                   |
| 11 (`zmt`)  |      88 | 55 identified, 33 undecodable |
| 67 (`zcd`)  |       9 | undecodable                   |
| 255         |       1 | unresolved                    |

Representative undecodable rows, with the archive each lives in:

- 4,768 rows of type 15: `pack/core_bvh4/core_bvh4.rpf!772!0` (131,280 bytes) and `pack/core_bvh4/core_bvh4.rpf!772!1` (196,816 bytes)
- 4,087 rows of type 73: `levels.rpf!772!0` (1,263,616 bytes) and `levels.rpf!927!0` (6,384 bytes)
- 3,196 rows of type 2: `levels.rpf!1719!4` (54,928 bytes) and `levels.rpf!1719!5` (5,376 bytes)

Representative rows that did decode:

- 55 rows of type 11: `levels.rpf!1029!4065` (2,504 bytes), head `5053494e…`
- 1 row of type 255: `levels.rpf!1091!0` (15 bytes), head `FORCE_EMPTY_RPF`

**Was missing.** What encoding 4 meant. The handoff described the decoder error
as "unrecognised chunk encoding". The build does not contain that string: it
accepted the encoding-4 table and then failed to inflate chunk 0 because it
started the chunk 16 bytes too early. Nothing was known about how those bytes
were framed, compressed or padded.

**Done when** the encoding's framing is described from the bytes, at least one
row decodes to a size that matches its location record, and the census reports
those rows with a real payload state. **Met:** the framing is described in
[chunk-encoding-4.md](chunk-encoding-4.md), all 14,488 rows decode to their
declared sizes, and the census reports them as decoded.

**Scope.** Do not add an encoding-4 path by guessing from the encoding number.
Do not treat the 56 decodable rows as evidence about the 14,432 that are not.
The 56 were used only as a regression set: their bytes must not change.

## B. Payload transform failures

**Solved.** Every transformed entry decodes. The failures were storage
integration, not the block program or key state.

The descriptor's stream fields at `+0x18`, `+0x20`, `+0x28` and `+0x30` define
the covered range, including a trailing region the decoder ignored. The
keystream counter starts at the first chunk byte, so an encoding-2 stored
prefix does not advance it. The 746 chunked-2 type-89 rows use a shape
(`0x1000/0x1000/0x31000/0x1000`) the decoder had hard-coded away. The four
raw-DEFLATE rows were refused before any byte was read because the selection
path required a chunk table; they are one DEFLATE stream whose selection now
inflates the whole stream and accepts only zero trailing bytes.

All 1,398 entries were read to their end and hashed: 746 chunked-2, 648
chunked-3 and 4 raw DEFLATE, with no failures. The 648 rows that decoded
before the change are byte-identical. See
[payload-transform.md](payload-transform.md).

**Established before the fix.** 1,398 entries carry the payload transform.
648 were read successfully and 750 were not.

| Storage       | Entries | Outcome                       |
| ------------- | ------: | ----------------------------- |
| `chunked-2`   |     746 | blocked                       |
| `chunked-3`   |     648 | 638 identified, 10 unresolved |
| `raw-deflate` |       4 | blocked                       |

| Type           | Entries |
| -------------- | ------: |
| 89 (`zscript`) |     746 |
| 11 (`zmt`)     |     500 |
| 255            |     151 |
| 14 (`zdatb`)   |       1 |

Every type-89 entry (746 of 746) is transformed, chunked-2, and blocked. The
four type-11 failures are stored with raw DEFLATE:

- 746 rows of type 89: `pack/story000/story000_script.rpf!1!0` and `pack/story000/story000_script.rpf!1!1`
- 4 rows of type 11: `pack/story000/story000.rpf!90!0` and `pack/story000/story000.rpf!407!0`

**Was missing.** Why these 750 did not verify. The key state that decodes the
chunked-3 rows is available, so the difference is in the rows, not in the
installation: the storage shape, the descriptor, or the transform's parameters.
Nothing was asserted about which. **Established:** the descriptor shape, the
counter origin and the stage relative to decompression; not a different key or
block program.

**Done when** each failing combination is explained by a property of the row —
not by a change to the transform implementation — and the census reports it as a
decoded payload or as a documented format. **Met for the observed installation
and build:** each combination is explained by its descriptor's stream fields and
its storage framing, the decoder derives both from the row, and the new census
reports all 1,398 as decoded. Another build's field values remain open.

**Scope.** Do not change the transform decoder in this task. 1,398 entries and
the 648 that already decode are the regression set: they must decode to the same
bytes afterwards.

## C. Shared resource structures

**Established.** 1,153,560 entries — 91.9% of the installation — are reported
as resource containers. What that rests on is narrow: the first 16 bytes are
eight zero bytes and a segment-5 pointer whose low 28 bits are a page-map
offset. Recognition stops there. No page map was walked, no segment was
resolved, and nothing behind the pointer was read, so the group is a set of
payloads that agree on 16 bytes, not a verified structure.

The census normalises the next two 32-bit fields so unrelated payloads are not
merged and pointer values are not split into thousands of buckets. The
normalised shapes are:

| Normalised header      | Entries |
| ---------------------- | ------: |
| `s5:small+ptr:seg5`    | 300,879 |
| `s5:ptr:seg5+zero`     | 297,579 |
| `s5:ptr:seg5+ptr:seg5` | 223,385 |
| `s5:small+zero`        | 119,843 |
| `s5:zero+zero`         |  96,582 |
| `s5:zero+small`        |  73,592 |
| `s5:zero+other`        |  40,019 |
| `s5:other+small`       |     844 |
| `s5:other+other`       |     611 |
| `s5:other+zero`        |     226 |

`ptr:seg5` means a 16-byte-aligned pointer into the system segment, `small` a
value below 0x10000, `tag:` four printable bytes, and the two fields are
`u32@0x10` and `u32@0x18`. The whole distribution is in the matrix. The shapes
are normalisations chosen to keep unlike payloads apart: two different shapes
are not evidence of two structures, and one shape is not evidence of one field
layout.

**Missing.** What those two fields mean, whether all of these are one structure
with optional fields or several structures, and the page map behind the pointer.
Nothing here establishes that any two entries in the group are the same asset
class.

**Done when** the resource header is described field by field, with the page map
walked for at least one segment, and the variants are either explained or shown
to be the same structure.

**Scope.** Similar extensions or similar headers are not equivalence. The
existing research, texture and model implementations are the reusable parts;
none of them should be copied into a new parser before this task establishes
what is shared.

## D. Type-255 identification and naming

**Established.** 73,068 entries carry type 255, the one id the build does not
register. 72,579 of them have no extension and none is invented.

| Identification     |                      Entries |
| ------------------ | ---------------------------: |
| `ADAT`             |                       71,676 |
| `KB2`              |                          797 |
| XML document       | 491 (489 parsed, 2 unparsed) |
| nothing recognised |                           92 |
| `EDUP`             |                            5 |
| `PSIN`             |                            2 |
| named signature    |                            5 |

**Missing.** An extension for any of them, an owner for the 92 rows that match
nothing, and a name for the rows whose path hash the local tables do not resolve.

**Done when**, for each family separately:

- `ADAT`: a documented container with a verified field layout.
- `KB2`: the two variants (`KB2j`, `KB2n`) distinguished by their framing.
- `EDUP`: the five rows described, or recorded as too rare to identify yet.
- `PSIN`: the two type-255 rows placed against the type-11 rows of the same
  format.
- Named signatures: `MHIU` (2 rows), `SGD5` (2) and `SPS1` (1) described or
  rejected. `MoVE` is not one of them: the census places `MoVE` under type 64,
  which the registry already names `mrf` (443 rows).
- Unknown text and binary payloads: the 92 heads grouped or rejected one by one.
- Original filenames: which rows can be named from the archive's own evidence,
  and which cannot be named at all. This must account for the name discovery and
  stringtable work the repository already carries — the path hashes, the LUT
  files, the runtime dictionaries and the candidate-naming tooling in
  [names.md](names.md) and `lforge names` — by verifying or extending it, not by
  starting a second naming path beside it.
- Payload-derived extensions: which of these families establishes an extension
  from the bytes, and which only from a decision a person makes.

**Scope.** An extension chosen for convenience is not a native naming fact. Only
the engine's registry declares those, and it declares nothing for type 255.

## E. Newly observed and unresolved types

**Established.** The full inventory reached every type id that earlier, bounded
runs had missed. Five of them are worth their own investigation:

| Type | Extension | Entries | Identification     |
| ---- | --------- | ------: | ------------------ |
| 18   | `zvert`   |     611 | resource container |
| 100  | `zsp`     |  27,482 | resource container |
| 104  | `zmsk`    |   1,476 | nothing recognised |
| 105  | `zhdat`   |   1,476 | nothing recognised |
| 113  | `zkit`    |   2,715 | resource container |

Types 104 and 105 carry the same number of entries. Every type-105 head begins
with `PAMH` (`50414d48`), and type-105 rows are 8,748 bytes in the samples. Type
104 rows are 32 bytes:

- type 104: `levels.rpf!69!0`, head `01000102800080000000000080008000…`
- type 105: `levels.rpf!1237!0`, head `50414d480132375f31350074400040000000…`

**Missing.** A layout for `PAMH`; anything at all about the 32-byte type-104
rows; and the meaning of the `zvert`, `zsp` and `zkit` extensions beyond the
registry's naming.

**A hypothesis, not a finding.** Types 104 and 105 have equal counts, appear in
the same archives, and read like a header and its payload. That is a reason to
investigate them together, and nothing more: no ordering, pairing or containment
has been observed.

**Done when** `PAMH` has a verified layout, the type-104 rows are either placed
in it or described as a separate structure, and the equal counts are explained
or left as a coincidence with the evidence that would settle it named.
