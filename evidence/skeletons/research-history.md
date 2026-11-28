# Skeleton research history

## 2026-11-27: the member's skeleton reference is parsed

The fragment document recorded the member drawable's `+0x18` reference and
deliberately did not interpret it. FRAG-F10 and FRAG-F21 keep that wording: it
was true of the runs that produced them, and the reference is still the only
evidence those runs had.

A later run read the record behind the pointer. The layout, the parent semantics
and the transform conventions are SKEL-F01 to SKEL-F14. Three statements in the
fragment document are now superseded in scope but not in claim:

- "The skeleton reference is recorded and not parsed" describes that document's
  work. The reference is parsed in [skeletons](../../formats/resources/skeletons/README.md).
- "Whether it changes the rendered pose is not established" remains true for
  animation. For the four verified fragments the stored vertex positions are the
  bind pose, so no static pose transform is needed.
- "A fragment whose parts are posed through a skeleton could render in its bind
  pose" remains the open case. No sampled fragment required a bone-local
  placement, so no placement rule was invented.

No earlier finding was wrong; the record behind the reference was simply not
read yet.

## 2026-11-27: the wider census corrects two statements

The four samples established the layout. A census of 27 containers (7,309 rows,
5,628 skeletons) then disproved two statements that the samples alone could not
separate, and added one.

- **SKEL-F05 was wrong as written.** The fourth `u16` of a record's trailing
  group is not the bone count. On a skeleton with helper bones it points past the
  end of that bone's chain: a 98-bone skeleton stores `81` in the first record
  and `98` in the last two. Limiting the walk by it truncated 550 of 5,628
  skeletons, and the records it dropped carry real names such as
  `XH_SecondarySurface` and `OH_TorsoDirection_01`.
- **SKEL-F02 needed a limit.** The header word at `+0x1C` is twice the bone count
  on 5,604 skeletons and one or two short on 24. It is recorded, not used.
- **SKEL-F06 needed a limit.** Multi-root is normal: 548 skeletons have more than
  one root, up to 16, because helper bones head their own short chains. Recorded
  as SKEL-F15.

Both wrong statements survived the four samples because those four have a single
root, where the subtree jump equals the count and the header word equals twice
the count. The samples were consistent with three readings; the census separated
them.

The census also bounded the influence findings. 8,304 of 10,106 LOD-0 geometries
decode an influence set at slots 6 and 8 and all of them validate. The other
1,802 are counted and left unassociated: 968 declare the weight form at slot 1,
753 have one bone and no weight form, 69 have several bones and no index form at
slot 8, and 12 have no weight form anywhere. Searching the declaration for the
weight format was tried as a fix and measured: it claimed the 968 slot-1
geometries, and every one of them then failed the weight totals and the index
bounds. `0x26` is a four-`u8` component format, not the name of the weight
attribute, so the reader keeps the slot the samples verified and reports the
rest as unread.

State: 5,627 of 5,628 skeletons are `complete`. The one `partial` is a skeleton
whose `+0x40` parent array holds a value outside the skeleton while its bone
records are consistent; it is reported, not reconciled. The four documented
fragments still decode as `complete` with the corrected walk.

## 2026-11-27: boundary check, storage conventions and the placement claim

Three things the earlier runs stated too broadly, and one they did not state at
all.

The bone walk trusted the index sequence alone. Measured against the arrays that
follow the bones, 2,303 of 5,628 skeletons have the next array starting exactly
where the bone records end, so the count is stated twice. Two skeletons broke the
walk in the other direction: data past the bone allocation carried the next index
by chance, and the walk added a record that the matrix arrays contradict. Both
were trimmed to the layout's limit and are reported as `BoneArrayOverrun`. Their
dropped records had no name, a zero 16-bit identifier and a denormal scale, so
they were not bones.

The two stored matrix arrays were described as confirming the pose, without
separating the raw elements from their mathematical reading. Measured over
133,110 bones: the `+0x38` elements read row-major equal `transpose(R_local)` for
every bone, worst delta `1.2e-7`; the `+0x30` elements equal `R_model` for every
bone, worst rotation delta `5.4e-7` and worst translation delta `4.8e-6` against
`-R_model^T * t_model`. Read the other way round, none match. Scale is `(1, 1, 1)`
in all 133,110 bones, so the composition ignoring scale is consistent with the
corpus but says nothing about a non-identity scale.

`PlacementCompleteness::NotRequired` was derived from the influence decoding
alone. It now requires the decoded vertices to match the per-geometry box the
record declares: the peacock matches 4 of 4 (`2.0e-5`) and the candlestick 2 of 2
(`2.0e-6`), while the tarot and bolt records declare no box and report
`unverified`. A valid influence set says which bones a primitive uses; it does
not say where its vertices are stored, and the two are now reported apart. The
verdict was then renamed `AuthoredGeometryMatchesBounds`, because agreement
between a geometry and the box in the same record does not prove that no later
stage places it.

The 753 one-bone geometries without a weight form were also inspected. All of
them belong to one-bone skeletons, but their geometry records carry no bone
index, bone-array pointer or palette pointer, so the association is left
undecoded rather than inferred from the count.

The bone rows in both viewers are now virtualized: the 600-row and 400-row caps
are gone, so every decoded bone is reachable.

## 2026-11-28: the declaration truncation, five index encodings and deformation

Two claims were wrong, both traced to one reader defect, and the influence work
then went further than recording bones.

The declaration table is a fixed array of 23 words and the slot number is the
attribute's semantic. The reader stopped at the first zero word, which is
correct only for the attributes before the gap: a geometry without a second UV
set leaves slot 7 empty, so slots 6 and 8 were never read for those geometries.
That is where the earlier census's "968 geometries declare the weight form at
slot 1" came from; it named a layout attribute of the vertex buffer, not a
declaration slot. Reading all 23 words moves those geometries into the ordinary
weighted group, and the slot-1 claim is withdrawn. Searching the declaration for
the format instead of reading the slot stays rejected, for the measured reason
already recorded: a format code says how many components an attribute has, not
what it means.

The index encoding is the pair of declaration format and layout size, and five
pairs occur over 10,106 geometries: `0x25`/4 four `u8` (8,254), `0x8C`/16 four
`u32` (104), `0x4A`/8 two `u32` (15), `0x00`/1 one `u8` (446) and `0x00`/2 one
`u16` (55). The wide forms pair lane `i` with weight lane `i`, so a lane never
crosses attributes.

Two attachment kinds are now decoded that were previously left unassociated:

- 501 geometries store one index per vertex and no weight stream, 446 as one
  `u8` and 55 as one `u16`. All of them declare more than one bone, every index
  is inside the declared count, the largest is 319 and no geometry repeats a
  single index. A single influence has weight 1 as a structural consequence, so
  the reading needs no invented value.
- 753 geometries store neither attribute and their record declares one bone.
  That reading rests on the declared count matching a one-bone skeleton and is
  accepted only there; 479 multi-bone geometries in the same state stay
  unassociated.

No palette was found, and the search was repeated rather than assumed: the
geometry record's fields at `+0x28`, `+0x2A`, `+0x2E`, `+0x30`, `+0x34`, `+0x38`
and `+0x3C` hold no bone index and no palette pointer, and the model's `+0x28`
slot does not read as a `u8` or `u16` bone list. Indices name the skeleton's own
array positions. A palette remains a possible future decode; nothing in the
corpus needs one.

The last step evaluates a pose instead of recording one. The skinning matrix is
`S[i] = G_pose[i] * inverse-bind[i]`, the inverse-bind array being the inverse of
the bind pose the stored transforms define, and a vertex sums `w_k * S[i_k] *
p_authored`. Scale stays identity, so a pose that would introduce one is
refused rather than approximated. Two independent evaluators were compared on
real data: a CPU reference and a GPU compute probe agree on the peacock's 25,456
tail vertices within `3.6e-7` m at a 40 degree pose and on the candlestick's 788
vertices within `3.7e-9` m. The peacock frame moves 24,496 of those vertices, so
the agreement is measured on real displacement.

Scope: the pose is entered by hand. No animation clip, blending or authored pose
is decoded, and linear blend skinning is the only method implemented. The
authored vertices are the deformed result at the reference pose, which is why
the reference pose reproduces the stored geometry and a delta is what changes
it.

## 2026-11-28: single-influence skinning, weight totals and the raster check

An acceptance review of the previous entry corrected four statements in it and
found one renderer defect.

**"501 rigid attachments" was the wrong name.** The measurement stands: 501
geometries store one index per vertex and no weight stream, every index is inside
the declared count, the largest is 319, and none of them repeats a single index.
That last fact is the opposite of a rigid piece. A primitive whose vertices name
different bones skins across those bones; whole-primitive rigid attachment is the
narrower case where every vertex names one bone, and it occurs on weighted
geometry as well. Measured per chain: the peacock has 2 single-influence
primitives, 1 of them whole-primitive rigid; the candlestick 2 and 2; the
dominator 25 of 29 and 2. The code now names the two cases apart
(`single_influence`, `rigid_attachment`) and no primitive is collapsed into one
mesh transform.

**The candlestick sample was misread.** Rotating `Candle` (bone 3) by 60 degrees
moved 139 vertices of the 927, not 788. The 788-vertex primitive belongs to bone
2 and does not move at all. The earlier count named the primitive size, not the
affected vertices.

**The rotation axis was misnamed.** A pose delta is a bone-local rotation, applied
after the stored local rotation, and a parent-space translation. The peacock's
"40 degrees about model Z" was 40 degrees about `Tail_01`'s own Z axis.

**The weight-total rule needed its population.** 8,373 rows carry a weight
stream; 10 of them hold a vertex whose four lanes do not sum to 255 or 127. Those
totals cluster between 197 and 254, which reads as independent rounding of four
lanes rather than a third scale, and the bowtie dictionary member is one of them
at 254. The decoder keeps rejecting them: a denominator that is not stated cannot
be inferred from the total alone, and rescaling would silently change every
weight on the primitive.

The inferred association is now named. 753 geometries declare no influence
attribute and their record declares one bone; that reading is an inference, so
`VertexInfluences::inferred` marks it and the status line says so. It is not
presented as a decoded stream.

The renderer defect: the skinned vertex shader normalised the skinned tangent, and
a geometry without a tangent attribute supplies a zero vector, so
`normalize(vec3(0))` produced NaN and the whole primitive lost its normal-mapped
shading. A pixel comparison of CPU-deformed geometry against skinned geometry
found it on the peacock: 24,141 of 630,000 pixels differed before the correction
and 28 differ now. The numerical probe could not see it, because it compared
positions, normals and tangents of the same vertices and not the shading they
produce. The fallback now matches the CPU reference: a direction the blend
cancels falls back to the authored direction.

The declaration truncation measured: every one of the 10,106 rows has a zero slot
before a populated one, so the old reader lost 29,438 slot entries in total,
including 660 normal streams, 683 first-UV streams and 1,996 tangent streams.
