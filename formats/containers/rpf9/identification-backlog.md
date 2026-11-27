# RPF9 entry identification backlog

Work that the classification in [entry-classification.md](entry-classification.md) leaves open, ordered by what it unlocks in the [entry matrix](entry-matrix.md).

Each item states what is known, what is missing, and what would count as done. Counts are the inventory's: 1,255,039 entries in 4,373 archives, every one of them classified and given an outcome.

The five findings that the census measured now have their own tasks in
[identification-follow-up.md](identification-follow-up.md). Chunk encoding 4 is
solved: all 14,488 entries decode ([chunk-encoding-4.md](chunk-encoding-4.md)).
The payload transform is solved: all 1,398 transformed entries decode
([payload-transform.md](payload-transform.md)). Resource structures, type 255
and the newly observed types remain open.

## 1. Resource containers

**Known.** A resource payload starts with eight zero bytes and a `0x5…` pointer at `+0x08`. Every resource in the installation is segment 5, and the pointer's low 28 bits are a page-map offset.

**Missing.** The page map at that offset, the resource headers it reaches, and the resource types those headers name. Until the map is read, a resource entry can be described as a container and nothing more: it carries the extension its type declares, which is a fact about the loader's naming, and no extension of its own.

**Done when** a resource container can list its resources, each with its own type identifier and count, and the classification can report an asset class per resource instead of per entry.

**Blocks.** 1,153,560 entries, 91.9% of the installation. It is also the precondition for any resource viewer.

## 2. A bounded head read

**Known.** Classifying one entry costs one decoded chunk, because the payload decoder decodes a chunk before handing out its first bytes. On large entries the first chunk is large.

**Missing.** A read that stops after the requested bytes and does not decode past them, while keeping the exact-size and checksum checks that the decoder performs today.

**Done when** the census gets cheaper per entry. Completeness is no longer what this unlocks: with a release build the payload pass covered all 1,255,039 entries in about half an hour. What it would buy now is a lower cost per run and a head read that does not depend on how a chunk was stored.

**Blocks.** Nothing outstanding. Every count in this repository is now a count of the installation, not of a budget.

## 3. Named signatures without a format

**Known.** `MoVE`, `SGD5`, `MHIU` and `SPS1` start payloads and nothing else about them is established: 443 `MoVE` payloads (all of them under type 64), two `MHIU`, two `SGD5` and one `SPS1`. `DDS ` and the PNG signature do not appear in this installation at all.

**Missing.** Structure: version fields, section tables, sizes, and the relationship to the entry types they appear under.

**Done when** each has a field layout with at least one verified size or offset, and either an extension or a documented reason why it has none.

## 4. Payloads that match nothing

**Known.** 3,047 entries were read and matched no signature. Their first 64 bytes are recorded in the matrix samples, so the bytes are available without a new run.

**Missing.** Enough structure to say whether these are one family or several.

**Done when** each recorded head is either grouped with a known format or recorded as a negative result with the heads that were rejected.

## 5. Transform behind the transform

**Solved.** All 1,398 transformed entries decode; the remaining 750 failed on
storage integration, not on the transform. The descriptor's stream fields at
`+0x18`, `+0x20`, `+0x28` and `+0x30` select the covered range, the counter
starts at the first chunk byte, and raw DEFLATE has its own selection path.
The range formula, the four observed shapes and the integrity limits are in
[payload-transform.md](payload-transform.md).

**Open outside this repository.** Whether another build uses other field
values. A reader MUST derive the range from the fields and reject a descriptor
that describes no usable range.

## Rejected

**A table from observed types to formats.** Types hold several formats and formats appear under several types, so any such table would be wrong for the next entry. What the census publishes instead is what it observed under each type, in [entry-matrix.md](entry-matrix.md).

**Reporting a declared extension as a verified asset class.** The engine's [type registry](type-registry.md) is a real table, recovered from the build, and the classification applies it. It is labelled `native` and the asset claim stays `unknown`, because the table says what the loader calls the type, not what these bytes are. Folding the two together is what made misidentified entries look resolved.

**Inventing an extension for a type the build does not register.** Type 255 has none, and the classification says so with a reason instead of guessing.

**Guessing a format from a partial match.** A short signature that is not unique to one format stays a named signature, not a format.
