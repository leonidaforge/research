# Drawable dictionary research history

Interpretations that were checked against the samples and not adopted. New
observations are recorded in the format document and evidence index, not here.
The current model is in the
[format document](../../formats/resources/drawable-dictionaries/README.md).

## No drawable dictionary was believed to exist in this build

**Candidate.** An earlier iteration reported that no drawable dictionary member
table could be found, and concluded that member enumeration and member selection
had no representation in the build (the finding then labelled FRAG-F06).

**Correction.** That search decoded 40 type-3 rows of one nested archive and
looked for a member table inside fragment roots. It never looked at the type-4
population. A drawable dictionary root does exist: every one of 8,209 type-4
rows of 53 nested archives holds a sorted `u32` name-hash array and a parallel
`u64` member-pointer array, with 12,480 members in total (DDICT-F01 to DDICT-F07).
The fragment finding now states only what fragments show (FRAG-F06), and the
dictionary grammar is documented separately.

## The member hash was expected to cover the stored name

**Candidate.** The `u32` hash array was cross-checked against `joaat` of the
member drawable's stored name, and later members did not match.

**Correction.** The hash covers the member name with its final extension
removed. Every stored member name ends in `.#dr`; hashing the full name matches
0 of 12,480 members and hashing the name without that suffix matches 12,480 of
12,480 (DDICT-F06). The suffix is part of the stored name text and not part of
the hashed string.

## The two counts were expected to differ from their capacities

**Candidate.** A texture-dictionary-shaped root in the same build stores a
count and a capacity that can differ, so the drawable dictionary root was read
the same way.

**Correction.** In all 8,209 populated rows the count equals its capacity. The
observed pairs are `(1,1)` through `(108,108)`. A reader SHOULD require equal
counts and MUST require `count <= capacity`; requiring a strict inequality would
reject every observed row (DDICT-F05).

## The inferred boundary was reported as unable to produce a usable dictionary

**Candidate.** Measured on the 53-archive corpus, the standalone inference
disagreed with native page metadata on 1,513 rows and produced no usable
dictionary on any of them, so a standalone open was described as always failing
loudly (DDICT-F09).

**Correction.** Two things changed the number and the reach of the claim. The
inference now refuses a tie between equally supported boundaries instead of
breaking it by offset order, so the same corpus reports 1,521 disagreements and
every one of them has no candidate rather than a candidate without a root form.
The installation-wide survey also shows the corpus limit: of 45,200 type-4 rows
read through their original chains, 6,304 boundaries disagree and 25 of those
disagreements still yield a root form whose members all resolve. The inference
can therefore land on a non-native boundary that parses completely. Native page
metadata stays authoritative, an inferred boundary is marked as inferred, and a
failed inference is still never read as evidence that the resource is not a
dictionary.

## The overlap between the inferred and native boundary was read, not assumed

**Candidate.** The 53-archive corpus produced no usable dictionary from an
inferred boundary on any disagreeing row, which was read as the general
behaviour.

**Correction.** The installation-wide read locates 25 rows where the inferred
boundary does enumerate the dictionary with every member resolved. Reading one,
`levels.rpf!1355!3`, shows what that means: at the native `0x1080` the single
member decodes to 2,449 vertices and 4,534 triangles, while at the inferred
`0x553e` the dictionary enumerates identically and the member then fails with
`the drawable yielded no renderable mesh`. The system segment had been cut past
the member's own records. A standalone open therefore still fails loudly on those
rows, one step later than elsewhere, which is why native page metadata remains
authoritative and an inferred boundary is marked as inferred.
