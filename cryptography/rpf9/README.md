# RPF9 cryptography

While the engine opens an RPF9 archive, it runs a validation chain over the [metadata area](../../formats/containers/rpf9/metadata.md). The chain processes selected spans in place with a cipher. On the first open of a file it also checks a signature. Any failure rejects the archive.

The cipher used by the observed archives is CBC-mode decryption with a 16-byte block, and it does not authenticate (see [Algorithm 0x10](#algorithm-0x10)). The only integrity check in the chain is the conditional [signature check](#signature-check). The signature algorithm is unknown.

Payloads of some entries go through a separate 16-byte block transform when they are read. See [Payload transform](#payload-transform).

Three kinds of statement appear below and must not be mixed:

- Code behavior: which bytes the engine passes to which routine, and in which order. Mostly Confirmed.
- Cryptographic interpretation: which algorithm family a routine belongs to. Probable or Unknown unless stated otherwise.
- On-disk representation: whether stored bytes differ from what the engine later reads. Settled only where archive data was checked.

## Validation chain

The archive constructor reads the header and metadata into buffers ([header.md](../../formats/containers/rpf9/header.md#read-modes)). It lays out a temporary view of the regions over those buffers and runs the chain. After the chain succeeds, it lays out the archive's metadata view over the same buffers (RPF9-F07). Lookups therefore read the bytes as the chain left them.

The chain runs in this order (RPF9-F42):

| Step | Operation | Runs when | On failure |
|---|---|---|---|
| 1 | Static pass over the `A` table and `B` block | `hdr[0x2E] != 0`. Otherwise the step succeeds without processing | Archive rejected |
| 2 | [Signature check](#signature-check) | File object `+0x08` bit 0 is clear | Archive rejected |
| lookup | Fetch `B` sub-block 1, the per-archive cipher descriptor | Always | If it is missing, the chain ends with success and steps 4 and 5 do not run |
| 4 | Primary pass with the sub-block 1 descriptor | Sub-block 1 present | Archive rejected |
| 5 | Secondary pass with the sub-block 1 descriptor | Sub-block 1 present, header read mode 0 or 1, non-empty secondary area. Otherwise the step succeeds without processing | Archive rejected |

The lookup between steps 2 and 4 is not a validation step. Earlier notes called it step 3.

The prefix counts are read before the chain runs, so they are stored in plain form (RPF9-F04).

## Selection

The byte at prefix `0x2E` controls step 1 (RPF9-F24):

| Value | Effect |
|---|---|
| 0 | Step 1 does nothing |
| bit 0 | Selects one of two span sets, see [Processed spans](#processed-spans) |
| `value >> 1` | Selects a static cipher descriptor: index 4 has cipher type 16, index 1 has cipher type 3, any other index gets a default descriptor with cipher type 0 (RPF9-F51) |

All inspected archives use 9: bit 0 set, descriptor index 4, cipher type 16, which selects [algorithm 0x10](#algorithm-0x10).

## Descriptors and keys

A cipher descriptor has this layout (RPF9-F25):

| Offset | Type | Meaning |
|---|---|---|
| `+0x00` | `u32` | Key identifier |
| `+0x04` | `u16` | Cipher type |
| `+0x06` | 16 bytes | Parameter. For algorithm `0x10` it is the initial CBC IV |

Two descriptor sources use this layout and the same initializer:

| Source | Used by |
|---|---|
| Static, built in the executable | Step 1 |
| `B` sub-block 1 in the archive | Steps 4 and 5 (RPF9-F45) |

The cipher type in sub-block 1 is not known for real archives, because sub-block 1 lies inside the step 1 span.

### Initialization and context

Initialization (RPF9-F50):

1. Maps the cipher type to an algorithm ID through the [type table](#cipher-types).
2. Takes the per-thread context. It holds the mode, the algorithm ID, an algorithm object and the key identifier. The object is kept between runs and replaced only when the algorithm ID changes.
3. Looks up key material by key identifier, algorithm ID and mode. If the lookup fails, initialization fails and the archive is rejected.
4. Initializes the algorithm object with the key material and the 16-byte parameter.

The metadata path always uses mode 1. The key is not stored in the descriptor or in the archive. Key identifiers, descriptor parameters, key material and executable lookup tables are not published, and the key lookup was not analyzed.

### Cipher types

The cipher type indexes a 19-entry table of algorithm IDs (RPF9-F51):

| Cipher types | Algorithm ID | Implementation |
|---|---|---|
| 0, 9, and any type of 19 or more | 0 | [No-op](#algorithm-0) |
| 3, 4, 5, 10, 11, 12, 16 | `0x10` | [CBC decryption](#algorithm-0x10) |
| 1 | 1 | Not analyzed |
| 2 | 2 | Not analyzed |
| 17 | `0x11` | Not analyzed |
| 6, 7, 8, 18 | `0x12` | Not analyzed |
| 13, 14, 15 | `0x0D` to `0x0F` | None. The object factory traps, so these types crash the engine |

An algorithm ID outside the factory's cases gets an object whose operations all fail.

## Processed spans

`A`, `B` and `u32@0x30` are the [prefix fields](../../formats/containers/rpf9/header.md#schema-prefix).

| Step | Span | Covers |
|---|---|---|
| 1, `hdr[0x2E]` bit 0 set | `(A table, align16(A * 8))` and `(B block, B - u32@0x30)` | `A` with padding, `B` without its trailer |
| 1, bit 0 clear, nonzero | One span `(A table, align16(A * 8) + B)` | `A`, padding and all of `B` |
| 4 | `[end of B - u32@0x30, hdr[0x08])` | `B` trailer, column descriptors, primary index store, primary value pool |
| 5 | `[hdr[0x08], hdr[0x04])` | The whole secondary area |

(RPF9-F26, RPF9-F45)

- Step 4 computes the start of the column descriptors as `0x40 + align16(A * 8) + B`. The [layout builder](../../formats/containers/rpf9/metadata.md#primary-area) aligns differently when `G` bit 0 is clear. The two agree when `G` bit 0 is set and `B` is a multiple of 16, or when `G` bit 0 is clear, `A` is even and `B` is a multiple of 8. No traced code checks these conditions. All inspected archives meet them (RPF9-F49).
- Header bytes `0x10` to `0x17` are never processed or signed.
- The `B` trailer of `u32@0x30` bytes is left out of step 1 when bit 0 is set. It is the first part of the step 4 span and is covered by the signature. Its own role is unknown.
- With algorithm `0x10`, every span length must be a multiple of 16, or `update` fails and the archive is rejected. This is why the step 1 `A` span is padded to `align16(A * 8)` (RPF9-F53).

## Operation

The span runner (RPF9-F27, RPF9-F46):

1. Initializes the cipher from the descriptor. Failure rejects the archive.
2. Calls `update` once per span, with the same buffer as input and output.
3. Calls `final`, which returns a boolean:
   - cipher types 3, 4 and 5: after every span, and once more after the last span;
   - other types: once, after all spans;
   - zero spans: once, after the initialization.
4. Returns the last `final` result. A false result from any `update` or `final` rejects the archive.

What `update` and `final` do depends on the algorithm.

### Algorithm 0

Initialization, `update` and `final` all return success without touching the data (RPF9-F52). Bytes stay unchanged. Initialization still needs a successful key lookup, and whether that succeeds for the default descriptor's key identifier is unknown.

### Algorithm 0x10

| Part | Behavior | Confidence |
|---|---|---|
| Engine | Only the mode 1 engine exists. Mode 0 has none and cannot initialize | Confirmed |
| Initialization | Sets up the engine state from the key material and sets the IV to the 16-byte descriptor parameter | Confirmed |
| `update` | CBC decryption: decrypts each 16-byte block and XORs it with the previous stored block, the first with the IV. Writes the result to the output, which is the input buffer. The output is written only after decryption, so in-place use is safe | Confirmed |
| Chaining | After each `update` the IV is the last stored block of that span, so the next span continues the CBC chain | Confirmed |
| Length | A length that is not a multiple of 16 fails | Confirmed |
| `final` | Resets the IV to the descriptor parameter and returns success. It checks nothing | Confirmed |
| Authentication | None in this algorithm. `final` cannot reject the data | Confirmed |

(RPF9-F53)

Span handling follows from `final`:

- Cipher types 3, 4 and 5 call `final` after every span. Each span is decrypted on its own, starting from the descriptor IV.
- Cipher types 10, 11, 12 and 16 call `final` only at the end. Consecutive spans form one CBC chain. For the observed type 16 this means the step 1 `A` and `B` spans are decrypted as one chain.
- The extra `final` after the last span only resets the IV and changes no output.

The block decryption has the structure of AES-256 decryption: a 128-bit block, 14 rounds and a 240-byte round-key schedule, computed with lookup tables (RPF9-F54). Its static tables differ from the standard AES reference constants, so a standard AES implementation cannot replace this one. Whether the underlying transform equals AES under some encoding is unknown.

### Interpretation summary

| Interpretation | Status |
|---|---|
| In-place call for each span | Confirmed: input and output pointers are identical |
| Result checked by a boolean `final` that can reject the archive | Confirmed for the runner. Algorithms 0 and `0x10` never fail in `final` |
| Decryption that changes the bytes | Confirmed for algorithm `0x10`. Algorithm 0 leaves them unchanged |
| Authenticated decryption | Rejected for algorithm `0x10`. Unknown for the algorithms that were not analyzed |

### On-disk state of the primary area

Code places the column descriptors, primary index store and primary value pool inside the step 4 span. Archive data adds this (RPF9-F48):

- A read-only scan of a sample of archives found none of the known field keys anywhere in the stored primary area `[0x40, hdr[0x08])`. The scan looked for each key as a little-endian `u64` at every byte offset.
- The engine needs one of the location record keys in the descriptors of every archive it reads (RPF9-F32).

So in those archives the stored primary area differs from what the engine reads. Probable: it is stored transformed and step 4 transforms it, which also means those archives contain `B` sub-block 1 with a cipher type that is not a no-op.

Not established: other archives, the secondary area, and whether every byte changes.

## Signature check

Step 2 checks a 256-byte value against a message built from metadata bytes (RPF9-F43). It writes only to new allocations, never to metadata.

The signature record comes from the `B` block:

| Sub-block | Layout | Used |
|---|---|---|
| 6 | `u8` message type, `u16` key identifier at `+2`, 256-byte signature at `+4` | First choice |
| 2 | `u32` key identifier, 256-byte signature at `+4`. Message type 0 | If sub-block 6 is missing |

Neither present, a message type other than 0 or 1, a signature outside the `B` block, a key identifier without key material, or a failed check all reject the archive.

The message is the concatenation of these spans:

| Message type | Spans, in order |
|---|---|
| 0 | `hdr[0x00..0x10)`, from the end of the signature to `hdr[0x08]`, then the secondary area if it is non-empty |
| 1 | `hdr[0x00..0x10)`, from `hdr[0x18]` to the signature, from the end of the signature to `hdr[0x08]`, then the secondary area if it is non-empty |

Coverage:

- Step 2 runs after step 1 and before steps 4 and 5. It covers the `A` and `B` bytes as step 1 left them, and the primary and secondary areas as stored.
- Message type 0 leaves out `hdr[0x10..0x40)`, the `A` table and the part of `B` before the signature.
- No message type covers `hdr[0x10..0x18)` or any payload data.
- The check runs only while file object `+0x08` bit 0 is clear. After the first successful open the engine sets that bit, so later archives opened on the same file object skip the check (RPF9-F44).

The structure, key lookup by identifier and a 256-byte value checked against a message, is Probable for a digital signature. The algorithm is unknown. The archive is therefore not fully signature-verified: coverage depends on the message type, and the check is skipped on later opens. For archives using algorithm `0x10`, nothing else in the chain detects altered metadata.

## Payload transform

Payload reads have their own transform path. The read routines call RVAs `0x19C380` (position the context), `0x1616150` (whole blocks) and `0x28CF9C0` (partial blocks), not the metadata span runner directly. Those routines were not analyzed, so shared code with the span runner is not excluded (RPF9-F38).

| Part | Status |
|---|---|
| Selection | Per entry, by the presence of key `0x286030A358A789FB` in the [schema](../../formats/containers/rpf9/schema.md#known-columns). Confirmed |
| Granularity | The engine positions a per-stream context at `position & ~0xF`, reads whole 16-byte blocks and processes them in place. Partial blocks at the ends use a separate routine. Confirmed |
| Seeks | Reposition the context to the new position. Confirmed |
| Interaction | Entries with the flag never use the chunk fast path. Confirmed |
| Algorithm | Unknown |
| Key source | Unknown. Not examined |
| Relation to the metadata cipher | Unknown |

The read path is described in [payloads.md](../../formats/containers/rpf9/payloads.md#payload-transform). Routines are listed in the [function catalog](../../builds/gta-vi/scarlett-e95020b2/functions.md#entries-names-payloads).

## Relation to earlier RPF versions

Whether RPF9 shares any cryptography with earlier RPF versions is unknown. Nothing in the analyzed code supports that assumption.

## Open questions

- Algorithms 1, 2, `0x11` and `0x12`.
- Whether the algorithm `0x10` block transform equals AES under some encoding.
- The cipher type of `B` sub-block 1 in real archives.
- Whether the key lookup succeeds for the default descriptor, which decides whether algorithm 0 archives open at all.
- The signature algorithm.
- The role of the `B` trailer.
- The `A` table content is identical across observed archives although it lies inside a processed span. The static descriptor uses a fixed key identifier and a fixed IV, which would explain identical stored bytes for identical plaintext. Not verified.
- The payload transform's algorithm, key source and relation to the metadata cipher. Payload reads do not call the span runner directly (RPF9-F38).
