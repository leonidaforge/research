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
not say where its vertices are stored, and the two are now reported apart.

The 753 one-bone geometries without a weight form were also inspected. All of
them belong to one-bone skeletons, but their geometry records carry no bone
index, bone-array pointer or palette pointer, so the association is left
undecoded rather than inferred from the count.

The bone rows in both viewers are now virtualized: the 600-row and 400-row caps
are gone, so every decoded bone is reachable.
