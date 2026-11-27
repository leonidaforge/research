# Fragment research history

Interpretations that were checked against the samples and not adopted. New
observations are recorded in the format document and evidence index, not here.
The current model is in the
[format document](../../formats/resources/fragments/README.md).

## A dictionary member table was reported absent

**Candidate.** No row of the 40 decoded type-3 rows of one nested archive holds
a table of drawable references, so the build was reported as having no drawable
dictionary member table.

**Correction.** The search was bounded to fragments. The table exists in the
type-4 population, where all 8,209 rows hold a hash array and a member-pointer
array (see [drawable dictionaries](../drawable-dictionaries/INDEX.md)). The
fragment finding now claims only what fragments show: a fragment root holds one
member drawable and no member table (FRAG-F06).

## The member-name suffix was used as the recognition test

**Candidate.** A resource was called a fragment when its member drawable's name
ended in `#ft`, because the suffix appears in every decoded sample.

**Correction.** The suffix is an observation about stored text, not a
discriminator. Recognition now uses the root structure: a zero word at `+0x00`,
a page-map pointer at `+0x08`, a member-drawable pointer at `+0x18` whose target
walks as an `rmcDrawable` with a zero page-map word, and no resource-level
drawable at zero. The suffix is reported as a fact (FRAG-F08). A name-based test
would reject a valid fragment whose member carries another suffix and is not
needed to separate fragments from the other containers.

## A second root word was read as a drawable count

**Candidate.** The second `u16` at `+0x30` was read as the number of drawables
because several samples store `1`.

**Correction.** `prop_am_orn_modern_04a.#ft` stores `[1, 2, 2, 2]` and holds one
member drawable, and the whole-population run finds one member drawable in all
5,553 rows while the four values vary from `0` to `266` (FRAG-F05, FRAG-F07).
The four `u16` are exposed as stored and are not counts of drawables.
