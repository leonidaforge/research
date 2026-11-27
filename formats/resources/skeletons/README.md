# Skeletons

A drawable may reference a skeleton. The reference is the header slot at
`+0x18`. The skeleton is a record that holds one bone per joint, the parent of
each bone, a default local transformation, a name, and two per-bone arrays that
repeat the local and model-space rotations. This document describes the record
as read from payload data.

Everything here comes from the Scarlett build and from decoded resources only.
No engine code path was traced for skeleton loading or pose evaluation. Findings
are `SKEL-F01` to `SKEL-F14` and are listed in
[evidence/skeletons/INDEX.md](../../../evidence/skeletons/INDEX.md).

## Where a skeleton is referenced

| Owner                        | Slot                    | Observation                                                   |
| ---------------------------- | ----------------------- | ------------------------------------------------------------- |
| Resource-level drawable      | drawable header `+0x18` | System pointer to the skeleton record, or null                 |
| Fragment member drawable     | member header `+0x18`   | System pointer to the skeleton record, or null                 |
| Drawable dictionary member   | member header `+0x18`   | One skeleton per member drawable; no dictionary-level skeleton |

The slot is null in some resources. A null slot is not an error: such a drawable
is complete as a static model.

## Skeleton header

The header is read from the pointer target in the system segment. Offsets are
from the start of the skeleton record.

| Offset | Size | Observed content                    | Status                                         |
| -----: | ---: | ----------------------------------- | ---------------------------------------------- |
| `+0x00` |  8 | Zero                                | Sample-verified                                |
| `+0x08` |  8 | Zero                                | Sample-verified                                |
| `+0x10` |  8 | The constant `1`                    | Sample-verified; meaning Unknown                |
| `+0x18` |  4 | The constant `0x20`                 | Sample-verified; meaning Unknown                |
| `+0x1C` |  4 | The key map entry count: twice the bone count on 5,604 of 5,628 skeletons, short by 1 or 2 on the rest | Observed; not read as a count |
| `+0x20` |  8 | System pointer to a key map         | Confirmed                                       |
| `+0x28` |  8 | System pointer to the bone records  | Confirmed                                       |
| `+0x30` |  8 | System pointer to inverse-bind data | Confirmed on every sampled skeleton             |
| `+0x38` |  8 | System pointer to local matrices    | Confirmed                                       |
| `+0x40` |  8 | System pointer to a parent array    | Confirmed on every sampled skeleton             |
| `+0x48` |  8 | System pointer to the bone names    | Confirmed                                       |

The key map at `+0x20` is a table of `(u32 key, u32 bone index)` pairs. Every
sampled skeleton stores two keys per bone: the bone record's 32-bit identifier
and its 16-bit identifier. A slot of `0xFFFFFFFF` is empty. The map is not
decoded by the application beyond this observation.

The word at `+0x1C` is close to twice the bone count but not equal to it on 24
of 5,628 surveyed skeletons, where it is short by one or two. It is therefore
recorded and never used to size the bone array; the bone count comes from the
records themselves. Whether the shortfall is a bone without a key is Unknown.

## Bone record

One bone record is 0x50 bytes. The array is contiguous; the records carry their
own index, so a record that does not continue the index sequence ends the array.
The record after the last bone is zero-filled in the samples. Neither the header
word at `+0x1C` nor the per-record value at `+0x4E` is the bone count: reading
either as a limit truncates skeletons that hold helper bones, so the array is
walked to its own end.

| Offset | Size | Content                                                    |
| -----: | ---: | ---------------------------------------------------------- |
| `+0x00` | 16 | Quaternion `x, y, z, w`, standard right-handed rotation     |
| `+0x10` | 12 | Local translation `x, y, z`                                 |
| `+0x1C` |  4 | Per-bone 32-bit identifier; not `joaat` of the name         |
| `+0x20` | 12 | Local scale `x, y, z`                                       |
| `+0x30` |  8 | System pointer to the NUL-terminated name, or null          |
| `+0x38` |  8 | Zero in every sample                                        |
| `+0x40` |  2 | Per-bone flag word; sample values `0xC077`, `0xD007`, `0xD077` |
| `+0x42` |  2 | The constant `7` in every sample                            |
| `+0x44` |  2 | `0xFFFF` in every sample; meaning Unknown                   |
| `+0x46` |  2 | Parent index, `0xFFFF` for a root                           |
| `+0x48` |  2 | The bone's own index                                        |
| `+0x4A` |  2 | Per-bone 16-bit identifier, also a key in the map           |
| `+0x4C` |  2 | The bone's own index again                                  |
| `+0x4E` |  2 | Jump to the end of this bone's subtree; equal to the bone count on a single-root skeleton |

Names are stored per bone and are not generated. Two bones may share a name; the
index stays the identity. The 32-bit and 16-bit identifiers are keys, not names:
`joaat` of a sampled bone name does not equal the stored 32-bit value, so no hash
function is claimed for it.

## Hierarchy

The parent index at `+0x46` is sufficient to rebuild the tree. The array at
`+0x40` repeats the same parents as `u16` values for every bone, which gives a
second, independent statement of the hierarchy. A mismatch between the two is a
diagnostic, not a repair; one row of the 5,628 surveyed skeletons disagrees, and
it is reported rather than reconciled.

A skeleton may hold several root bones. 5,080 of the 5,628 surveyed skeletons
have one root, 58 have two, and the rest hold up to 16. The extra roots are
helper bones: records named `XH_SecondarySurface`, `OH_EyelineDirection_01`,
`OH_FocusDirection_01` or `OH_TorsoDirection_01` sit at the head of their own
short chains and are not parented to the body. Multi-root is therefore not a
defect and is not reported as one.

The reader does not require parent-first order: a parent outside the array, a
self-parent and a cycle are reported, and a multi-root or non-parent-first
skeleton is supported where the bounds allow it.

Traversal is bounded by the bone count. A cycle is detected before any pose is
composed, and its members are reported.

## Transform semantics

Local values compose into model space as

```text
R_model = R_parent * R_local
t_model = t_parent + R_parent * t_local
```

The quaternion is used as `x, y, z, w` with column-vector rotation. Two stored
arrays confirm this without assuming it:

| Array      | 3x3 content                    | Translation content                  |
| ---------- | ------------------------------ | ------------------------------------ |
| `+0x38`    | transpose of the local rotation | local translation                    |
| `+0x30`    | model-space rotation            | `-R_model^T * t_model`               |

The `+0x30` translation is the translation half of the inverse bind matrix
`[R_model^T | -R_model^T * t_model]`, stored with the rotation transposed back.
On the peacock skeleton, whose tail has six rotated levels, both arrays match the
composed pose to the stored precision: the largest rotation delta is `0.0000`
and the largest translation delta is `0.0000` against a `2e-3` tolerance. The
same check passes on the other sampled skeletons.

A matrix record is 0x40 bytes: a 3x3 rotation in row-major order, an unused
fourth column of zeros, a translation and one further value whose meaning is
Unknown. The reader keeps the last value for a later investigation.

### Bind-pose terminology

The stored local transforms are the pose the resource ships with. The application
calls the composed result the **static pose** or **stored bind pose**, because
the inverse-bind array validates against exactly that composition. No separately
authored pose was found, so an authored pose is not claimed. A record whose
inverse-bind entry does not validate is reported and not used.

Invalid values are reported, never repaired. A non-finite translation, a
quaternion whose length is not one, and an inverse-bind record that disagrees
with the composed pose each make the result `partial`.

## Geometry associations

The geometry record carries its bone count at `+0x2C`. It equals the skeleton's
bone count on every highest-LOD geometry of a skeleton-bearing drawable and is
zero on lower LODs. The vertex buffer carries the influences:

| Stream slot | Format | Content                                                     |
| ----------: | -----: | ----------------------------------------------------------- |
|           6 | `0x26` | Four `u8` blend weights, one per influence                  |
|           8 | `0x25` | Four `u8` blend indices, one per influence                  |

The slot number alone is not enough: slot 8 carries another quantised attribute
(format `0x8C`) on some rigid drawables, so the reader checks the format. A set
is accepted only when every vertex has at least one non-zero weight, every
weighted lane names a bone inside the skeleton, and the weights are used as
stored. The weight totals observed are 255, 127 (a 7-bit scale), and rare
unnormalised totals such as 169; an unnormalised total is reported once and the
association still uses the non-zero lanes. A missing index stream is accepted
only for a one-bone skeleton, where lane 0 selects the only bone.

The two slot numbers hold for most geometry records but not for all. Of 10,106
surveyed highest-LOD geometries that declare bones, 8,304 decode an association
this way and none of them fails validation. The remaining 1,802 are counted and
not associated:

| Observation                                                    | Geometries |
| -------------------------------------------------------------- | ---------: |
| Weight form at slot 1 instead of slot 6                          |        968 |
| One bone and no weight form                                     |        753 |
| Several bones and no index form at slot 8                       |         69 |
| No weight form in any declared slot                             |         12 |

Searching the declaration for the weight format instead of reading slot 6 was
tried and measured: it moved the 968 geometries out of the unread group, and
every one of them failed the weight totals and the index bounds. The format code
`0x26` says four `u8` components, not "blend weights", so the reader keeps the
slot the samples verified and reports the rest as unread. A 753-geometry group
of one-bone records needs no weights: the bone count states the association.

Accepted associations record which bones a primitive uses and whether any vertex
blends more than one. The sampled geometry falls into three cases:

- **Already positioned geometry.** The stored vertex positions are the bind
  pose, so drawing them unchanged is correct. All four verified fragments are of
  this kind.
- **Rigid single-bone geometry.** One bone with weight 1, as on the tarot,
  candlestick and weapon bolt. No placement is applied; the weights already agree
  with drawing the vertices as stored.
- **Weighted geometry.** Up to four influences, as on the peacock's tail. The
  reader records the bones and does not deform; the bind pose is what the stored
  positions already are.

No resource in the sample required a bone-local vertex space to be placed by a
bone transform. The application therefore applies no placement and reports
`not required`. A geometry whose influences do not validate makes the association
`partial` and the placement `unverified`; it is never reported as placed.

## Coverage

Two corpora were read through the native archive path. The narrow one holds the
four verified samples; the wide one is the census that corrected two of the
findings. Both are selected samples, not the installation.

| Quantity                                | Narrow corpus           | Wide corpus            |
| --------------------------------------- | ----------------------- | ---------------------- |
| Archives                                | `data.rpf!26`, `levels.rpf!5` | 27 archived containers |
| Rows read                               | 3,211                   | 7,309                  |
| Skeletons present                       | 3,138                   | 5,628                  |
| Null skeleton slots                     | 73                      | 1,681                  |
| Bone counts observed                    | 1 to 42                 | 1 to 596               |
| Roots per skeleton                      | 1                       | 1 to 16 (5,080 have 1) |
| Hierarchy depths observed               | 1 to 21                 | 1 to 35                |
| Inverse-bind records present            | every bone              | every skeleton         |
| Skeletons with a structural issue       | 0                       | 1                      |
| Decoded-LOD geometries declaring bones  | 3,425                   | 10,106                 |
| Influence sets validated                | 3,425                   | 8,304                  |
| Weighted geometries                     | 100                     | 425                    |

The single structural issue in the wide corpus is one skeleton whose `+0x40`
parent array holds a value outside the skeleton while its bone records are
consistent. It is reported as partial and its hierarchy is still read from the
bone records.

## Limits

- The meanings of `+0x10`, `+0x18`, `+0x44`, the flag word at `+0x40` and the
  matrix record's last value are Unknown.
- The 32-bit and 16-bit bone identifiers have no established hash function.
- The key map is observed, not decoded beyond its entry shape.
- The value at `+0x4E` is described as a jump to the end of the bone's subtree
  because that reading fits every surveyed record; no engine code confirms it,
  and nothing depends on it.
- Skeletons whose geometry declares its weight stream somewhere other than slot
  6 are read as skeletons without an association. 968 of 10,106 geometries are
  in that state; an association is never invented for them.
- The sample is 29 archives of the Scarlett build. A skeleton variant outside it
  may store a different parent encoding or a different influence layout; the
  reader reports what it cannot read instead of assuming this layout holds
  everywhere. Earlier RAGE skeleton layouts are not assumed to match.
- No animation pose, blending or skinning is decoded. A pose evaluated over time
  is out of scope.

## Tools

[skeleton_inspect.py](../../../tools/drawables/skeleton_inspect.py) walks a
decoded resource to a skeleton and reports the header, bones, hierarchy,
composed pose, inverse-bind validation and geometry associations. The
synthetic tests are in `tools/drawables/tests/test_skeleton_inspect.py`.
