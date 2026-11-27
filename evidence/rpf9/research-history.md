# RPF9 research history

Interpretations that were once used for RPF9 and later corrected. The current model is in the [specification](../../formats/containers/rpf9/README.md).

## Metadata thought to be opaque

**Old assumption.** Everything after the 16-byte header was encrypted. Tools could use only the magic and the metadata size, and had to recover payloads by scanning for zlib streams.

**Correction.** The loader reads bytes `0x10..0x3F` directly as counts and flags and computes region offsets from them. Only selected spans go through the cipher (RPF9-F04, RPF9-F26).

## Entry records were column descriptors

**Old assumption.** The `C` records of 24 bytes were file entries, and `C` was the entry count.

**Correction.** The loader never reads these records at fixed field offsets. A field is fetched by a hashed key, and the key search compares the first 8 bytes of each record. The records are column descriptors and `C` is the column count. The entry count is `E` (RPF9-F08, RPF9-F13).

## Cells hold dictionary indices

**Old assumption.** The cell regions held the field values, and `F` was the value width.

**Correction.** A cell holds an `F`-byte index into the column's value pool, with all-ones as null. The value width comes from descriptor `+0x10`. This is how a one-byte cell can refer to a 16-byte value (RPF9-F09, RPF9-F11, RPF9-F12).

## Row-major addressing

**Old assumption.** Each column's cells were stored contiguously, column-major.

**Correction.** The cell reader computes `row * stride + column` within each store. The stride is `C - D` for the primary store and `D` for the secondary store (RPF9-F10, RPF9-F11).

## Per-column value pools

**Old assumption.** The bytes between the primary cells and `hdr[0x08]` had no known consumer.

**Correction.** They are the primary value pool. The secondary area ends with a second pool. The value pointer adds the descriptor's column base offset to the pool start (RPF9-F12).

## Entry ID tag

**Old assumption.** The high 16 bits of an entry ID were a computed section index.

**Correction.** The getter returns the `u16` stored at file object `+0x0C`. It is the index of the file object's slot in a global registry, assigned when the file object is created (RPF9-F15, RPF9-F64).

## Names

**Old assumption.** Names were rebuilt by the engine, and the hashes could be compared with the name hashes of earlier RPF versions.

**Correction.** A row stores a 64-bit hash of its path. The hash function is RPF9-specific and is described in the specification (RPF9-F18, RPF9-F56).

## Names resolved in reverse

**Old assumption.** The engine turned each row's hash into a name through the runtime dictionary, rebuilt `name.extension` and matched the requested path against it with a substring search. Without the dictionary nothing could be opened.

**Correction.** Opening by path is forward hashing. The resolver strips the mount prefix, hashes the stem and searches the rows by hash and type ID (RPF9-F55). The dictionary is a separate facility that is not filled from archives (RPF9-F60). The substring lookup does exist, but it searches the dictionary string, never reads its rebuilt `name.extension` buffer, and returns the first match in row order (RPF9-F20).

## Fallback name path

**Old assumption.** Key `0xB7076B6245D35FB5` was an unexplained gate for a fallback name lookup.

**Correction.** It is the 32-bit key of rows whose type uses the 32-bit class. Every type uses exactly one of the two classes (RPF9-F57, RPF9-F59).

## Linear row scan only

**Old assumption.** All row lookups scanned the rows linearly. No sorted index existed.

**Correction.** The resolver's row lookups use a binary search when the archive's sorted flag is set. Only the substring lookup is always linear (RPF9-F58).

## Child enumeration

**Old assumption.** `0x28CDA50` enumerated an archive's children from an array of entry IDs.

**Correction.** It resolves an array of caller-supplied path strings. No native enumeration of all rows was found (RPF9-F21).

## Size columns were location records

**Old assumption.** Keys `0xBA18…`, `0x33F7…` and `0x4EAA…` were three size columns: a resource size and two plain sizes masked to 44 and 48 bits. The resource formula was `(w0 & 0xFFFFFFF0) + (w1 & 0x7FFFFFF0)`.

**Correction.** The three keys hold alternative layouts of one location record. Each layout has the payload offset, stored size, logical size, type ID and compression mode. The 44- and 48-bit values are fields at `+0x10` and `+0x08` inside the record, not the whole value. The resource formula has the masks the other way round: `(w1 & 0xFFFFFFF0) + (w0 & 0x7FFFFFF0)` (RPF9-F16, RPF9-F32).

## Stream read was a seek

**Old assumption.** `0x28CD3B0` was the stream reader and read payloads in 4 KiB blocks through a low-level block read at `0x314330`.

**Correction.** `0x28CD3B0` is a seek. It decodes and discards up to 4 KiB at a time only when a compressed stream seeks forward. `0x314330` is the read dispatcher (RPF9-F34, RPF9-F37).

## Enumeration base offset

**Old assumption.** The descriptor written by `0x28CDA50` held the device base offset at `+0x18`.

**Correction.** It holds the `u64` at file object `+0x30`. Payload reads add file object `+0x20` (RPF9-F21, RPF9-F33).

## Namespace column

**Old assumption.** Each row stored its name namespace in a column.

**Correction.** The namespace comes from a table in the executable, indexed by the row's type ID (RPF9-F31).

## Validation step 3 was a lookup

**Old assumption.** The validation chain had five steps. Steps 2 to 4 had unknown roles, and step 3 looked up `B` sub-block 1.

**Correction.** Step 2 is a conditional signature check. The third operation is a lookup of the per-archive cipher descriptor in sub-block 1. If that sub-block is missing, the chain ends with success and steps 4 and 5 do not run. Step 4 processes the primary area (RPF9-F42, RPF9-F43, RPF9-F45).

## Primary regions outside the cipher spans

**Old assumption.** The column descriptors, primary index store and primary value pool lay outside every processed span, so their stored state was open with no code-level lead.

**Correction.** They lie in the step 4 span. In the inspected archives none of the known field keys occurs in the stored primary area, so those archives probably store it transformed (RPF9-F45, RPF9-F48).

## B trailer as authentication tag

**Old assumption.** The `B` trailer, left out of step 1, was a plausible authentication tag.

**Correction.** The trailer starts the step 4 span and is part of the signed message. Nothing in the code supports the tag reading any more. Its role is unknown (RPF9-F45).

## Authenticated decryption was CBC decryption

**Old assumption.** The span runner calls `update` in place and checks a boolean `final`, so the metadata cipher was probably authenticated decryption with a 16-byte tag.

**Correction.** Algorithm `0x10`, which the observed static descriptor selects, is CBC decryption. Its `final` resets the IV and always succeeds. The cipher therefore authenticates nothing. The separate signature check remains the chain's only integrity check, and it is conditional (RPF9-F43, RPF9-F44, RPF9-F53).

## Initializer label

**Old assumption.** `0x536A70` was the table that maps cipher types to algorithm IDs.

**Correction.** `0x536A70` is the initializer. It calls the table lookup `0x536AC0` and then the factory and key setup `0x613880` (RPF9-F25).

## Mount prefix from the archive path

**Old assumption.** An archive's resolver prefix always came from the directory of its own resolved path, so it was a property of the archive and never a mount point supplied by a caller.

**Correction.** The directory-derived prefix is only the default set during construction. Mounting the archive through its mount method replaces it with the caller's mount prefix. Mounted archives therefore resolve entries under the mount prefix (RPF9-F61, RPF9-F69).

## Preloaded blocks from batch resolution

**Old assumption.** A parent's batch path resolution built the preload blocks for nested archives, which were then mounted in bulk from the parent's metadata copies. This rested on matching record layouts.

**Correction.** The traced caller of the preloaded path is a batch loader that takes its blocks from a global index. What fills that index is unknown. Whether the parent copy is used on this path was not established (RPF9-F76).

## Descriptor `+0x08` unread

**Old assumption.** No code read column descriptor `+0x08` or `+0x12` (RPF9-F40).

**Correction.** One archive method returns the `u32` at `+0x08` together with a column's first value address (RPF9-F82). `+0x12` is still unread on the traced paths.

## Header field letters

Some earlier notes used "A" and "B" for `hdr[0x04]` and `hdr[0x08]`. Those letters name the prefix fields at `0x1A` and `0x1C`. Header fields are now referred to by offset.

## Algorithm 0x10 input stage

**Old assumption.** The block function substitutes each input byte through 16 static 256-byte tables.

**Correction.** Those tables are affine bijections over GF(2): for every table and every nonzero input difference, the output difference is constant. The stage contains no substitution box and is an invertible affine transform of the block followed by a four-word key XOR (RPF9-F85). The nonlinearity is entirely in the 16 static round tables, whose cores are 4-uniform permutations of degree 7, and in the key-dependent final-round tables (RPF9-F86, RPF9-F87).

## Algorithm 0x10 identity

**Old assumption.** Algorithm `0x10` was AES-256-shaped, and equivalence with AES was unknown. Its table invariants matched, but no constructive result existed, and differing table bytes were read as consistent with, not evidence for, AES.

**Correction.** The fixed tables are an encoded AES-256 decryption, established constructively. Every round-table core is affinely equivalent to the AES inverse S-box with explicit invertible maps verified on all 256 inputs. The 16 table maps factor as InvMixColumns columns under byte-diagonal output encodings, and the per-position encodings compose across rounds (RPF9-F89, RPF9-F90). The round formula was then re-derived by symbolic execution of the instruction stream, and a synthetic encoded AES-256 instance reproduced standard AES-256 on known vectors (RPF9-F91). The key schedule and the key-dependent final-round tables remain protected, so the equivalence is established for the block transform, not for any particular key.

## Archive metadata could not be decrypted

**Old assumption.** No local archive produced verified native metadata. Read-only probes decrypted the step-1 `A` span with one assumed fixed-table block, found no structured `A` table, and reported the key-to-archive binding as unconfirmed (RPF9-F96).

**Correction.** Structural recognition finds nine fixed-table blocks that satisfy every public invariant, so structure alone cannot pick one (RPF9-F99). The archive decides: each candidate is tried with the recognized descriptor state, and the block whose decryption yields a plausible `A` table is selected (RPF9-F100). All 22 tested archives select the same candidate and then pass the metadata signature check (RPF9-F102). A plausible `A` table is a compatibility gate, not authentication.

## Signature covered a single hash

**Old assumption.** The signed value was `SHA-256(message)`, so a verifier hashed the assembled metadata spans once and compared that digest. Every tested archive failed that check.

**Correction.** The archive path hashes the message once and the verifier hashes the resulting 32-byte digest again, so the signed value is `SHA-256(SHA-256(message))` (RPF9-F101). A single-hash check rejects valid signatures; the archive signatures were never invalid. All 22 tested archives authenticate (RPF9-F102).

## Native table of contents unreadable

**Old assumption.** The native table of contents could not be listed or extracted. Metadata was encrypted, the location layouts came from code only, and the available tools could scan for zlib streams but had no authoritative entries.

**Correction.** Once step 1 runs with the recognized provider and steps 4 and 5 decode the primary area, the columnar table of contents parses directly. All 22 tested archives authenticate and yield 6534 native rows (RPF9-F102, RPF9-F103). The location record layouts are confirmed in real data: F on 6533 rows and R on one row; all listed rows use read source `main` and mode 0. Stored and chunked rows extract to exactly their logical sizes, while rows behind the payload transform are refused (RPF9-F104). Names remain hashes, type meanings remain mostly unknown, and payload bytes remain outside the signature. Native listing therefore needs metadata authentication but does not make payload content authenticated.

## Key-state setup addresses withdrawn

**Old assumption.** The function catalog and the evidence index listed RVAs for the key-registry lookup, its lazy initialization, and the integrity gate and thunks around key-state setup, next to the algorithm-`0x10` setup routine.

**Correction.** Those addresses are withdrawn. Together they lead from a descriptor's key identifier to the executable's embedded key-material storage, which the research policy keeps out of this repository. The behavior stays documented: selector construction (RPF9-F94), the `0x10F4`-byte state and its `0x1100`-byte copy (RPF9-F95), and the structural recognition method (RPF9-F97). Ordinary cryptographic processing functions keep their RVAs, including the selector construction and the setup routine. Some rows had also been written as full virtual addresses. Those are withdrawn with the rows above, or corrected to RVAs against the image base recorded in the build document where they remain.

## Payload transform reuses the metadata cipher

**Old assumption.** The payload-transform routines `0x19C380`, `0x1616150` and `0x28CF9C0` were only known to be called; their algorithm, key source and relation to the metadata cipher were unknown (RPF9-F38).

**Correction.** The three routines run the same encoded AES-256 CBC engine as the metadata cipher, through a separate per-stream algorithm object (RPF9-F109). The read stores the block-aligned position, reads whole 16-byte blocks and transforms them in place; a partial block reads the whole block, transforms it and copies the requested sub-range (RPF9-F110). The flag disables the chunk fast path and transforms stored bytes before inflation (RPF9-F111). The object's mode selects CBC continuation or an IV equal to the 16-byte parameter plus the block index, and the mode also selects the key-provider state (RPF9-F112).

**Still open.** The key state is not the archive `B` sub-block 1 descriptor or the executable static descriptor in the tested combinations, under either provider mode, so real transformed rows do not decrypt (RPF9-F113). No speculative decoding was implemented; transformed rows stay refused.

**Later corrected.** The relation to the metadata cipher held only for the object class, not for the algorithm. See [Payload transform descriptor](#payload-transform-descriptor) below.

## Payload transform descriptor

**Old assumption.** The payload transform initialized its per-stream cipher from the archive `B` sub-block 1 descriptor or the executable static descriptor, and its algorithm was the metadata cipher's algorithm `0x10` with CBC chaining (RPF9-F109, RPF9-F112, RPF9-F113).

**Correction.** The descriptor is the value of the entry's own transform field `0x286030A358A789FB` (RPF9-F114): key identifier, cipher type and parameter, handed to the same initializer the metadata descriptors use. The type selects the algorithm, and the sampled rows carry type `0x11`, which selects algorithm `0x11` (RPF9-F115). That object carries mode 3, so the slot repositions a counter instead of continuing CBC, and the engine is a counter-mode keystream rather than the CBC engine. The key identifier resolves through the static registry to a provider-2 state carrying the magic algorithm `0x11` accepts (RPF9-F116). The earlier negatives are therefore evidence about the archive and static descriptors only.

**Still open.** The block generator's round program is not reproduced, so no chunk decodes and the reader keeps refusing transformed rows (RPF9-F117).

## Encoding-2 chunk prefix

**Old assumption.** Chunks are stored back to back from the entry's payload offset for every encoding (RPF9-F78).

**Correction.** Encoding-2 entries keep 16 bytes before the first chunk. The chunk stored sizes sum to 16 less than the entry's stored size, and the first zlib stream starts at offset 16. One row with two chunks and one with a single chunk show it, and 27 encoding-2 rows from a random sample of nested archives extract to their logical sizes once the prefix is skipped (RPF9-F119). Encodings 3 and 4 still start at offset 0.

**Still open.** What the prefix contains or means, and whether another encoding-2 layout exists.

## Raw DEFLATE rows were unobserved

**Old assumption.** Native extraction covered stored rows and chunked rows. Raw DEFLATE rows with mode 1 and no chunk table had been seen only in code, never in real data (RPF9-F104).

**Correction.** A nested archive contains 156 type 11 rows, all mode 1 without a chunk table. Eight sampled rows extracted as raw DEFLATE to exact logical sizes (RPF9-F118). The archive is nested, outside the 22 top-level archives of RPF9-F103, so that sample's counts do not change. One row failed with a DEFLATE error; the failure is not explained.

## Header field `0x0C` was unknown

**Old assumption.** `hdr[0x0C]` was not read on any traced path and its value was unknown. The header table marked it Unknown and the reader bound stopped at the file size.

**Correction.** In 1,440 archives (22 top-level and 1,418 nested), `file_size - hdr[0x0C]` is a 16-byte-aligned boundary above the metadata end, below the file size, and at or above every row's stored end. `hdr[0x0C]` is the byte length of a trailing region, and stored payload data ends at `file_size - hdr[0x0C]` (RPF9-F129). No traced path was found that reads the field, so the correction is from archive data. The trailing content remains undecoded. The equality groups are in RPF9-F130.

## Archive name text scoped to the metadata table

**Old assumption.** An archive stores no file name text.

**Correction.** The metadata table stores hashes rather than names. The trailing region was measured only by length, offset and equality; it has not been examined for text. The statement in [names.md](../../formats/containers/rpf9/names.md) is scoped to the metadata table, and the trailing region is recorded as unexamined (RPF9-F129, RPF9-F130).

## Secondary column count was one

**Old assumption.** The header field `D` was 1 in every observed archive, so the secondary area held one column and its size observations were written for that case.

**Correction.** `D` takes values 1 to 8 in the 1,440-archive sample; 1,066 archives use 1 and 374 use more than one (RPF9-F131). With the documented store start `align_F(hdr[0x08])`, the index-store layout is a necessary size fit in all 374 archives with `D > 1`; a direct layout with one fixed width in every secondary column is a necessary size fit in 140 and fails 234. The models therefore make different size predictions in 234 archives, but no observation selects one: the direct model can fit every archive with per-column widths, and no decoded secondary store was available (RPF9-F132). The index-store model stays documented because the accessors implement it, not because the sizes select it. The flag at `u8@0x2D` is still an open hypothesis.

## Bytes at `0x18` were constant

**Old assumption.** The 8 bytes at `0x18` held the same value in every observed archive, consistent with constant `A` and `B` fields inside them.

**Correction.** The `u16` at `0x18` is `0x7A00` in the 1,440-archive sample, but the same 8 bytes contain `A` at `0x1A` and `B` at `0x1C`. `A` takes 4 to 6 and `B` takes several sizes, so the combined value changes between archives (RPF9-F131). A set in which `A` and `B` do not vary makes the 8 bytes look constant. The meaning of `0x18` itself remains Unknown.

## Copy chunk test used the stored length

**Old assumption.** An encoding-2 last chunk was a copy chunk when its stored length equalled the remaining logical length. Padded copy chunks were classified as unknown.

**Correction.** The copy condition uses the compressed length, stored length minus padding, not the stored length. The classifier now accepts padding from 0 to 15 and records it. All 178 copy chunks in the sample had zero padding, so the observed counts do not change; a synthetic fixture covers a padded copy chunk (RPF9-F125).

## Trailer equality figures covered different sets

**Old assumption.** One trailer comparison reported thirty 720-byte archives with an identical 64-byte trailer alongside four shape groups with an identical 544-byte trailer, without saying that the figures covered different sets.

**Correction.** The thirty 720-byte archives are a size subset of one header-shape group; that full group also contains other sizes with different trailers, so it is not single-class. The four single-class groups are other header shapes and all have a 544-byte trailer. The figures are not two readings of the same group (RPF9-F130).

## The entry type was treated as the file's kind

**Old assumption.** An entry's numeric type said what the file was: a type-0 row was an archive, a type-5 row a texture dictionary, and a listing that showed a name and a type had nothing else to establish.

**Correction.** The type is one property, not the format. In a bounded census of every root archive, type 255 holds `ADAT`, `KB2`, validated XML documents, named signatures and payloads that match nothing; type 11 holds `PSIN` and `RBF0`; type 0 holds archives and `PSIN`. The classification now records the type, the format identified from a bounded decoded head, and what the application can do with the bytes as three separate properties, and the texture viewer no longer opens a row because of its type (RPF9-F140).

## An extension was shown where none was established

**Old assumption.** A recognisable payload, or a known type, was enough to show a file extension.

**Correction.** An extension is applied only when the classification establishes it: the archive's own name, `rpf` for an RPF9 payload, `xml` for a validated document. Everything else is reported as unresolved with a reason, including a recognised format with no established extension and a resource container whose asset class is not identified. The sample's largest group is unresolved for exactly that reason (RPF9-F140, RPF9-F141). The rule was widened later, when the engine's own table was recovered: a type's declared extension is applied and labelled as such, which is not the same as establishing it (see below).

## A head read was assumed to be cheap

**Old assumption.** Reading the first bytes of an entry costs a few bytes.

**Correction.** The payload decoder decodes a chunk before handing out its first byte, so classifying one entry can cost a whole chunk — that part stands. What did not stand is the conclusion drawn from it: that a complete census was unaffordable. Two full passes, one over metadata and one over every payload head, each covered all 1,255,039 entries of the installation and finished in 19 and 31 minutes with a release build. The 91-entries-per-second figure that made a complete run look out of reach came from a debug build; the same archive runs four times faster in release. No count in this repository is a budgeted sample any more (RPF9-F145, RPF9-F146). A bounded head read would still cut the cost, so it stays in the backlog, but as an optimisation rather than a precondition.

## A declared extension was treated as an inference

**Old assumption.** Any type-to-extension mapping could only come from observation, so applying one without reading the payload meant guessing.

**Correction.** The engine carries its own table, recovered from the build (RPF9-F144), and the classification quotes it rather than inventing one. Each entry records where its extension came from (`original`, `native`, `payload`, `unresolved`), the asset claim stays `unknown`, and a payload that contradicts the declared family is reported as a conflict. The earlier statement that a resource container "carries no extension" was wrong for every type the build registers: 1,181,971 of the installation's 1,255,039 entries carry a declared extension, and the only entries without one are the 73,068 rows of type 255 (RPF9-F145).

## The Explorer applied its own extension rule

**Old assumption.** The listing completed a name the archive did not spell with an extension by appending `.rpf`, but only for type 0; every other type was shown as the archive spells it.

**Correction.** One rule now serves the Explorer and the command line, from `lforge_core::registry::file_name`: a name that already carries an extension keeps it, a name without one takes the extension the type declares — type 5 rows show `.ztd`, type 11 rows `.zmt` — and a type that declares nothing gets none. The Explorer names the synthesized extension as such and keeps the archive's own spelling beside it, so a completed name is never mistaken for a stored one. 1,181,971 entries carry a declared extension and 72,579 carry none.

## A metadata pass was reported as a decoding blocker

**Old assumption.** An entry whose payload was not read was `blocked`, the same outcome a payload transform failure produced.

**Correction.** `blocked` now means a payload that was reached and could not be read. An entry nothing was read for is `not-probed`: a metadata pass reports that for every row, and it claims nothing about the bytes. The five outcomes the payload pass reports add up to the entry count, and the two that occur nowhere are named rather than left to be inferred.

## A census summary was trusted because it existed

**Old assumption.** The driver accepted a summary file the CLI had written, whatever the CLI's exit status and however the run had ended.

**Correction.** A census now publishes its summary atomically — written beside the target and renamed into place — and exits non-zero when it stopped at a limit or could not read an archive. The driver requires a zero exit status, a `completion.complete` record, a matching header schema and scan mode, and binds a reused summary to a SHA-256 of its own bytes, its size and the root fingerprint the journal recorded. A journal record alone no longer authorizes a summary, and the merged result names the reasons it is not a census of the installation instead of only saying that it is not.

## Chunk encoding 4 was a prefix, not a compression algorithm

**Old assumption.** Encoding 4 was treated as unsupported storage. The census
reported 14,432 entries as `undecodable`, and the handoff described the error as
"unrecognised chunk encoding", which suggested the chunk method or the
compression algorithm was unknown.

**Correction.** The decoder already parsed the encoding-4 chunk table. It
applied the 16-byte stored prefix only to encoding 2, so chunk 0 began 16 bytes
early on 14,432 rows and zlib read zero bytes as a header. The error was
therefore a framing error with a DEFLATE message, not a missing codec. The
prefix length is the entry's stored size minus the sum of the chunk stored
sizes; it is 0 on 56 rows and 16 on 14,432, and every prefixed row stores zero
bytes there. The decoder now derives it from the sizes (RPF9-F150). All 14,488
entries decode to their declared logical size, and the 56 that decoded before
the change produce identical bytes (RPF9-F151, RPF9-F152).

**Correction.** `archive ls` reported `contents.state = "decoded"` for a chunked
row whose chunk table validated but whose chunk was never decoded. The state is
now `validated`, and `decoded` is reserved for a read that returned the payload.
A full-decode command reports the digest, size match and failure category
(RPF9-F153).

**Provenance.** The accepted payload pass used scanner `ef1cde45…`. An
integrated rerun with the final build (`6560e67c…`) reproduced the same 22
roots, 4,373 archives and 1,255,039 entries and the same outcome counts; its
wall clock is not quoted because an unrelated scan shared the disk. The
integrated build's only census-path change is a shared helper for the stored
prefix, which returns the same prefix for every valid row.

## Open

- Meaning of descriptor `+0x08`, and any use of `+0x12`.
- What selects location layout F over A, and whether real rows carry more than one layout.
- The content of the `B` sub-blocks.
- The stored state of the secondary area and of archives other than the inspected ones, and how many bytes of the primary area change. One earlier note called the primary regions "post-transform" from the order of initialization alone. The step 4 pass, the archive scan and the verified signature now confirm the primary area is stored transformed in the inspected archives (RPF9-F28, RPF9-F48, RPF9-F102).
- Whether a second executable build registers the same keys or binds to the same archives. Cipher algorithms 1, 2 and `0x12`, whether the embedded schedule is the standard AES-256 expansion, and the role of the `B` trailer remain open.
- The block program of the payload transform's algorithm `0x11`: its round structure, table roles and key use, without which no transformed payload can be decoded (RPF9-F117). The descriptor, the algorithm selection and the key state are established (RPF9-F114 to RPF9-F116). Payload bytes are not covered by the metadata signature.
- The meaning of the 16-byte stored prefix before encoding-2 and some
  encoding-4 chunks (RPF9-F119, RPF9-F124, RPF9-F150). Its length is known; its
  content is only observed to be zero.
- Directory structure outside the traced paths, and enumeration in the device layer or above.
- CityHash32 identity of the fingerprint hash, the concrete startup fingerprint and the contents of `B` sub-block 9 in real archives.
- Path normalization, the physical device implementation, and the mount prefixes the game uses.
- Whether any nested archive is stored compressed or transformed, which the native nested read path cannot read.
