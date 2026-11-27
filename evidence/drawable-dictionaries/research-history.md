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
