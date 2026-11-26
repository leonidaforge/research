# RPF9 entry identification backlog

Work that the classification in [entry-classification.md](entry-classification.md) leaves open, ordered by what it unlocks in the sample matrix ([entry-matrix.md](entry-matrix.md)).

Each item states what is known, what is missing, and what would count as done. Counts are the sample's, not the install's.

## 1. Resource containers

**Known.** A resource payload starts with eight zero bytes and a `0x5…` pointer at `+0x08`. Every resource in the sample is segment 5, and the pointer's low 28 bits are a page-map offset.

**Missing.** The page map at that offset, the resource headers it reaches, and the resource types those headers name. Until the map is read, a resource entry can be described as a container and nothing more, which is why it carries no extension.

**Done when** a resource container can list its resources, each with its own type identifier and count, and the classification can report an asset class per resource instead of per entry.

**Blocks.** The largest share of the sample. It is also the precondition for any resource viewer.

## 2. A bounded head read

**Known.** Classifying one entry currently costs one decoded chunk, because the payload decoder decodes a chunk before handing out its first bytes. On large entries the first chunk is large.

**Missing.** A read that stops after the requested bytes and does not decode past them, while keeping the exact-size and checksum checks that the decoder performs today.

**Done when** a census of a full install is affordable: the current run is bounded to a small entry budget per root archive, and a complete count would take hours at the present cost per entry.

**Blocks.** Completeness of every measurement in this repository that samples entries.

## 3. Named signatures without a format

**Known.** `MoVE`, `SGD5`, `MHIU` and `SPS1` start payloads and nothing else about them is established. `DDS ` and the PNG signature also appear.

**Missing.** Structure: version fields, section tables, sizes, and the relationship to the entry types they appear under.

**Done when** each has a field layout with at least one verified size or offset, and either an extension or a documented reason why it has none.

## 4. Payloads that match nothing

**Known.** A small number of decoded payloads match no signature. Their first 64 bytes are recorded in the matrix samples, so the bytes are available without a new run.

**Missing.** Enough structure to say whether these are one family or several.

**Done when** each recorded head is either grouped with a known format or recorded as a negative result with the heads that were rejected.

## 5. Transform behind the transform

**Known.** A payload transform is required for a share of entries. Where the executable's key state is available the census decodes them; where it is not, the entry is reported as `transform-unavailable` with no format guess.

**Missing.** Nothing for the classification itself. The open work is the transform's own coverage across builds, which belongs to the cryptography documents.

**Done when** no entry in a census is `transform-unavailable`.

## Rejected

**A type table that maps entry types to formats or extensions.** The sample shows types that hold several formats and formats that hold several types, so any such table would be wrong for real entries. The only established mapping stays type 0 to `rpf`, and even that is applied only when the payload's own bytes are an RPF9 archive.

**An extension inferred from a type when the payload is not read.** This is what made misidentified entries look resolved. The classification reports `extension: null` with a reason instead.

**Guessing a format from a partial match.** A short signature that is not unique to one format stays a named signature, not a format.
