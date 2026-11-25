# RPF9 cryptography

While the engine opens an RPF9 archive, it runs a validation chain over the [metadata area](../../formats/containers/rpf9/metadata.md). The chain processes selected spans in place with a cipher. On the first open of a file it also checks a signature. Any failure rejects the archive.

The cipher used by the observed archives is CBC-mode decryption with a 16-byte block, and it does not authenticate (see [Algorithm 0x10](#algorithm-0x10)). The only integrity check in the chain is the conditional [signature check](#signature-check). It is RSASSA-PKCS1-v1_5 with SHA-256 and a 2048-bit RSA key embedded in the executable (RPF9-F92, RPF9-F93). The engine signs the SHA-256 hash of the SHA-256 hash of the message (RPF9-F101). With the recognized key supply and the archive-dependent fixed-table selection, step 1 decrypts the metadata of all 22 tested local archives and their signatures verify (RPF9-F100, RPF9-F102).

The authenticated layer is metadata. Parsed entry semantics and payload contents are outside the signature. See [What is authenticated](#what-is-authenticated).

Payloads of some entries go through the same 16-byte CBC engine when they are read, through a separate per-stream cipher object whose key state is unresolved. See [Payload transform](#payload-transform).

Three kinds of statement appear below and must not be mixed:

- Code behavior: which bytes the engine passes to which routine, and in which order. Mostly Confirmed.
- Cryptographic interpretation: which algorithm family a routine belongs to. Probable or Unknown unless stated otherwise.
- On-disk representation: whether stored bytes differ from what the engine later reads. Settled only where archive data was checked.

## Validation chain

The archive constructor reads the header and metadata into buffers ([header.md](../../formats/containers/rpf9/header.md#read-modes)). It lays out a temporary view of the regions over those buffers and runs the chain. After the chain succeeds, it lays out the archive's metadata view over the same buffers (RPF9-F07). Lookups therefore read the bytes as the chain left them.

The chain runs in this order (RPF9-F42):

| Step   | Operation                                                | Runs when                                                                                                              | On failure                                                                 |
| ------ | -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| 1      | Static pass over the `A` table and `B` block             | `hdr[0x2E] != 0`. Otherwise the step succeeds without processing                                                       | Archive rejected                                                           |
| 2      | [Signature check](#signature-check)                      | File object `+0x08` bit 0 is clear                                                                                     | Archive rejected                                                           |
| lookup | Fetch `B` sub-block 1, the per-archive cipher descriptor | Always                                                                                                                 | If it is missing, the chain ends with success and steps 4 and 5 do not run |
| 4      | Primary pass with the sub-block 1 descriptor             | Sub-block 1 present                                                                                                    | Archive rejected                                                           |
| 5      | Secondary pass with the sub-block 1 descriptor           | Sub-block 1 present, header read mode 0 or 1, non-empty secondary area. Otherwise the step succeeds without processing | Archive rejected                                                           |

The lookup between steps 2 and 4 is not a validation step. Earlier notes called it step 3.

The prefix counts are read before the chain runs, so they are stored in plain form (RPF9-F04).

## Selection

The byte at prefix `0x2E` controls step 1 (RPF9-F24):

| Value        | Effect                                                                                                                                                             |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 0            | Step 1 does nothing                                                                                                                                                |
| bit 0        | Selects one of two span sets, see [Processed spans](#processed-spans)                                                                                              |
| `value >> 1` | Selects a static cipher descriptor: index 4 has cipher type 16, index 1 has cipher type 3, any other index gets a default descriptor with cipher type 0 (RPF9-F51) |

All inspected archives use 9: bit 0 set, descriptor index 4, cipher type 16, which selects [algorithm 0x10](#algorithm-0x10).

## Descriptors and keys

A cipher descriptor has this layout (RPF9-F25):

| Offset  | Type     | Meaning                                                  |
| ------- | -------- | -------------------------------------------------------- |
| `+0x00` | `u32`    | Key identifier                                           |
| `+0x04` | `u16`    | Cipher type                                              |
| `+0x06` | 16 bytes | Parameter. For algorithm `0x10` it is the initial CBC IV |

Two descriptor sources use this layout and the same initializer:

| Source                          | Used by                  |
| ------------------------------- | ------------------------ |
| Static, built in the executable | Step 1                   |
| `B` sub-block 1 in the archive  | Steps 4 and 5 (RPF9-F45) |

The cipher type in sub-block 1 is not known for real archives, because sub-block 1 lies inside the step 1 span.

### Initialization and context

Initialization (RPF9-F50):

1. Maps the cipher type to an algorithm ID through the [type table](#cipher-types).
2. Takes the per-thread context. It holds the mode, the algorithm ID, an algorithm object and the key identifier. The object is kept between runs and replaced only when the algorithm ID changes.
3. Looks up key material by key identifier, algorithm ID and mode. If the lookup fails, initialization fails and the archive is rejected.
4. Initializes the algorithm object with the key material and the 16-byte parameter.

The metadata path always uses mode 1. The key is not stored in the descriptor or in the archive.

### Key supply

Key resolution uses a static registry inside the executable, not a platform key store (RPF9-F94). The key identifier and the cipher mode form a 64-bit selector:

```text
algorithm in 0x10..0x15:  provider = 3 if mode == 0 else 2
otherwise:                provider = 0
selector = (key_id << 32) | (provider << 24)
```

The registry is a lazily built map populated from a static entry list plus runtime registrations. A hit returns a pointer and a length. The observed archives use `hdr[0x2E] = 9` with cipher type `0x10` and mode 1, so provider 2. The registry's location, exact size, identifiers and entry-to-location mappings are kept in private evidence.

Algorithm `0x10` consumes a `0x10F4`-byte encoded key state (RPF9-F95):

| Blob offset | Content                                        |
| ----------- | ---------------------------------------------- |
| `+0x000`    | `u32` magic `0x4E3B9B8E`                       |
| `+0x004`    | 240-byte schedule, 60 little-endian dwords     |
| `+0x0F4`    | 16 × 256-byte key-dependent final-round tables |

The setup copies these bytes into a `0x1100`-byte state and copies the 16-byte descriptor parameter into state `+0x10F0`. The engine checks the magic and does not expand a raw key. It does not receive the blob length, so a provider MUST enforce `0x10F4`.

In private validation, the registered algorithm-`0x10` states matched the recovered encodings on all 16 final-round tables, so they are encoded AES-256 states. Their contents, fingerprints and registry locations are not published.

A standard 32-byte AES key is not accepted by algorithm `0x10`. Separate provider-0 32-byte entries serve other algorithms and are not a conversion path. No conversion from a raw AES key to the encoded state is provided by the engine.

The key material is embedded and build-specific. The binding to the local archives is demonstrated for this build: the resolved state decrypts the step-1 `A` span of all 22 tested archives into structurally valid tables, and the metadata signature then verifies under the static public key (RPF9-F100, RPF9-F102). An earlier read-only probe recovered no structured `A` table; it used one assumed fixed-table block (RPF9-F96). The difference is candidate selection, not the key. Whether a second executable build binds to the same archives is untested; a build mismatch for those archives is neither shown nor excluded.

### Recognition

The static registry can be located without a fixed storage address by a bounded scan of read-only sections (RPF9-F97). A candidate run of `0x18`-byte records is accepted only if:

- every state pointer lies inside the image,
- every algorithm-`0x10` state has length `0x10F4`; the provider-0 default entry may be `0x20`,
- the schedule is nonzero,
- each of the 16 final tables is a permutation,
- at least one state carries the algorithm-`0x10` magic.

On build e95020b2 this yields one candidate run with 24 records and 10 algorithm-`0x10` states. Selectors, pointers and state contents are not published.

The method is public; the concrete result is verified only for this build. A missing, malformed or ambiguous candidate fails closed. No cross-build compatibility is established.

The static descriptor is recognized separately (RPF9-F98). The recognizer finds the descriptor writer, bounds its caller with the PE exception table and derives the index-guarded key/type/parameter path. On build e95020b2 selector 9 resolves to index 4, kind `0x10`, and exactly one compatible registry state; selector 7 has no descriptor and fails closed. Key identifiers, IVs and addresses are not published.

### Fixed tables and the archive gate

The fixed transformation tables are recognized structurally (RPF9-F99). A candidate is a contiguous 20 KiB block: sixteen 256-byte stage tables that are affine bijections of rank 8, followed without padding by sixteen 1 KiB round tables that are injective with four byte-lane permutations and an affine 8-dimensional image. On build e95020b2 this finds nine structurally valid blocks. The recognition method and the validation rule are public; the concrete count and the selected index are private-evidence supported.

Structural validity does not identify which block the engine uses. All nine satisfy the same public invariants, the archive names no block, and the table bytes are not published. The discriminator is archive data (RPF9-F100): the engine's step-1 `A` span is decrypted with the recognized descriptor state under each candidate, and the decoded records are validated. A candidate qualifies only if the records are 8 bytes long, their `u16` identifiers are nonzero and unique, every offset lies inside `B`, and at least one identifier is a known sub-block ID. Exactly one candidate MUST qualify; zero or several fail closed.

All 22 tested local archives select the same candidate and pass. A qualifying `A` table is structural evidence that one ciphertext span decoded under the recognized key. It is not authenticity: the signature check decides that, in [Verified archive result](#verified-archive-result).

### Cipher types

The cipher type indexes a 19-entry table of algorithm IDs (RPF9-F51):

| Cipher types                     | Algorithm ID     | Implementation                                                  |
| -------------------------------- | ---------------- | --------------------------------------------------------------- |
| 0, 9, and any type of 19 or more | 0                | [No-op](#algorithm-0)                                           |
| 3, 4, 5, 10, 11, 12, 16          | `0x10`           | [CBC decryption](#algorithm-0x10)                               |
| 1                                | 1                | Not analyzed                                                    |
| 2                                | 2                | Not analyzed                                                    |
| 17                               | `0x11`           | Not analyzed                                                    |
| 6, 7, 8, 18                      | `0x12`           | Not analyzed                                                    |
| 13, 14, 15                       | `0x0D` to `0x0F` | None. The object factory traps, so these types crash the engine |

An algorithm ID outside the factory's cases gets an object whose operations all fail.

A descriptor stores a _cipher kind_, a `u16`. The kind is the archive's or the static writer's selection and indexes the type table; it is not the algorithm identity. Several kinds share one algorithm family: 3, 4, 5, 10, 11, 12 and 16 all map to algorithm `0x10`, and 3, 4 and 5 differ from the others in when `final` runs. The algorithm family selects the provider namespace and the block implementation. Cipher kinds and algorithm families MUST NOT be used interchangeably: "type 16" names the archive-side kind, "algorithm `0x10`" names the implementation family.

## Processed spans

`A`, `B` and `u32@0x30` are the [prefix fields](../../formats/containers/rpf9/header.md#schema-prefix).

| Step                     | Span                                                      | Covers                                                                   |
| ------------------------ | --------------------------------------------------------- | ------------------------------------------------------------------------ |
| 1, `hdr[0x2E]` bit 0 set | `(A table, align16(A * 8))` and `(B block, B - u32@0x30)` | `A` with padding, `B` without its trailer                                |
| 1, bit 0 clear, nonzero  | One span `(A table, align16(A * 8) + B)`                  | `A`, padding and all of `B`                                              |
| 4                        | `[end of B - u32@0x30, hdr[0x08])`                        | `B` trailer, column descriptors, primary index store, primary value pool |
| 5                        | `[hdr[0x08], hdr[0x04])`                                  | The whole secondary area                                                 |

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

| Part           | Behavior                                                                                                                                                                                                                                        | Confidence |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- |
| Engine         | Only the mode 1 engine exists. Mode 0 has none and cannot initialize                                                                                                                                                                            | Confirmed  |
| Initialization | Sets up the engine state from the key material and sets the IV to the 16-byte descriptor parameter                                                                                                                                              | Confirmed  |
| `update`       | CBC decryption: decrypts each 16-byte block and XORs it with the previous stored block, the first with the IV. Writes the result to the output, which is the input buffer. The output is written only after decryption, so in-place use is safe | Confirmed  |
| Chaining       | After each `update` the IV is the last stored block of that span, so the next span continues the CBC chain                                                                                                                                      | Confirmed  |
| Length         | A length that is not a multiple of 16 fails                                                                                                                                                                                                     | Confirmed  |
| `final`        | Resets the IV to the descriptor parameter and returns success. It checks nothing                                                                                                                                                                | Confirmed  |
| Authentication | None in this algorithm. `final` cannot reject the data                                                                                                                                                                                          | Confirmed  |

(RPF9-F53)

Span handling follows from `final`:

- Cipher types 3, 4 and 5 call `final` after every span. Each span is decrypted on its own, starting from the descriptor IV.
- Cipher types 10, 11, 12 and 16 call `final` only at the end. Consecutive spans form one CBC chain. For the observed type 16 this means the step 1 `A` and `B` spans are decrypted as one chain.
- The extra `final` after the last span only resets the IV and changes no output.

The block decryption is AES-256 decryption under a fixed affine encoding: a 128-bit block, 14 rounds (13 table rounds plus a substitution-only final round) and a 240-byte round-key schedule (RPF9-F54, RPF9-F88, RPF9-F90).

The fixed tables decompose exactly (RPF9-F85, RPF9-F86, RPF9-F87, RPF9-F89):

- The 16 static byte tables applied before the first round are affine bijections over GF(2), not substitution boxes. That stage is a fixed invertible affine transform of the block followed by a four-word key XOR.
- Each of the 16 static 1 KiB round tables is injective 8→32 bit with an 8-dimensional affine image: `T(x) = c xor L(s(x))` with `c = T(0)` nonzero and `s` an 8-bit permutation. Every core permutation is differentially 4-uniform, of algebraic degree 7 and with maximum absolute Walsh coefficient 32, and its difference-distribution and absolute Walsh multisets equal the AES inverse S-box's. The checked core also has the AES inverse S-box's boomerang uniformity of 6.
- Each of the 16 core permutations is constructively affinely equivalent to the AES inverse S-box. Invertible linear maps and translations were recovered from the tables and verified on all 256 inputs (RPF9-F89).
- The 16 round tables are pairwise unrelated by a linear map or by a byte rotation, and all are distinct. They are therefore not a textbook AES T-table set; each position carries its own affine encoding.

The linear layer is identified as well. Each 8→32 table map factors exactly as `E_i P_j`, where `E_i` is a byte-diagonal 32-bit encoding and `P_j` is the `InvMixColumns` coefficient column, and the per-position encodings compose across rounds: each output byte encoding is the inverse of the input decoding of the table that reads that byte next, with the affine constants absorbed into the encoded round key. The fixed tables therefore implement the AES-256 equivalent-inverse-cipher round function on a fixed byte-wise affine state encoding, with the round key supplied in the encoded domain (RPF9-F90). With the thirteen rounds, the substitution-only final round and the initial key addition, the block function is an encoded AES-256 decryption.

The round model is verified against the instructions, not only against its own algebra. Symbolic execution of the 272-instruction listing derives the stage-0 packing and key-byte order, both half-round table and lane formulas, the 13-round control flow and the final permutation; Ghidra and objdump agree on all instruction boundaries. A synthetic encoded AES-256 instance, built from the recovered encodings and a synthetic key blob and executed with the real fixed tables read from a user-provided executable, reproduces the FIPS-197 AES-256 decryption vector and further blocks (RPF9-F91). Driven with the engine's chaining rule, the same model reproduces the NIST SP 800-38A AES-256-CBC vector over four blocks, so the block transform and the CBC order are checked against published vectors. The layout is fixed: a code word is an AES column and its lane `r` is AES row `3-r`, with the caller block in column-major order.

The round-key material supplies the rest of the structure. Whitening uses schedule words 0 to 3, 13 rounds use words 4 to 55, and the last 16 schedule bytes are never read. That fits the AES-256 equivalent-inverse-cipher layout, whose 15th round key is folded into the 16 key-dependent final-round byte tables instead of being XORed (RPF9-F88).

These properties were measured read-only from the two fixed table regions at RVAs `0x6036F30` (4 KiB) and `0x6037F30` (16 KiB) in build e95020b2, from the Ghidra 12.2 listing of `0x5642C50` and local scripts that recompute the difference distribution, the Walsh spectrum, the table relations and the affine-equivalence witnesses. The fixed table bytes and witness files are not in this repository. The mathematical statements and synthetic model are public; the table-specific verification is private-evidence supported. A reader with a compatible executable can re-run the scripts.

Differing table bytes do not by themselves decide AES equivalence, because a table-encoded cipher with per-position affine encodings necessarily differs from the textbook constants. The constructive result settles both layers from the fixed tables: the S-box layer is the AES inverse S-box and the linear layer is InvMixColumns, each up to the recovered affine encodings, and the encodings compose across rounds. Algorithm `0x10` is therefore an encoded AES-256 decryption. What remains outside the fixed data is the key-dependent state: the 240-byte schedule and the 16 key-dependent final-round tables. That state is embedded in a static registry (RPF9-F94, RPF9-F95). Private validation found that the registered algorithm-`0x10` states match the recovered final-table encodings on all 16 tables, so they are encoded AES-256 states. Their bytes, fingerprints and registry locations are not published. Whether the schedule is the standard AES-256 expansion of a raw key in encoded form was not determined from public data.

The identity of the algorithm does not by itself enable interoperability. A standard AES-256 implementation cannot be dropped in, because the engine consumes a pre-expanded, per-position-encoded schedule and key-dependent final tables, not a raw key. The state encodings are recovered by the constructive analysis. The provider boundary is therefore a `0x10F4` blob, not a raw key. The archive-specific key binding is demonstrated for the tested build and archive sample (RPF9-F100, RPF9-F102); the key does not come from an external platform key store.

### Interpretation summary

| Interpretation                                                  | Status                                                                                                                                                             |
| --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| In-place call for each span                                     | Confirmed: input and output pointers are identical                                                                                                                 |
| Result checked by a boolean `final` that can reject the archive | Confirmed for the runner. Algorithms 0 and `0x10` never fail in `final`                                                                                            |
| Decryption that changes the bytes                               | Confirmed for algorithm `0x10`. Algorithm 0 leaves them unchanged                                                                                                  |
| Authenticated decryption                                        | Rejected for algorithm `0x10`. Unknown for the algorithms that were not analyzed                                                                                   |
| Algorithm `0x10` identity                                       | Encoded AES-256 decryption: the AES inverse S-box and InvMixColumns, established constructively and verified on all 256 inputs per S-box core (RPF9-F89, RPF9-F90) |

### On-disk state of the primary area

Code places the column descriptors, primary index store and primary value pool inside the step 4 span. Archive data adds this (RPF9-F48):

- A read-only scan of a sample of archives found none of the known field keys anywhere in the stored primary area `[0x40, hdr[0x08])`. The scan looked for each key as a little-endian `u64` at every byte offset.
- The engine needs one of the location record keys in the descriptors of every archive it reads (RPF9-F32).

So in those archives the stored primary area differs from what the engine reads. The area is stored transformed and step 4 transforms it, which also means those archives contain `B` sub-block 1 with a cipher type that is not a no-op. Confirmed for the inspected archives by the successful step 4 pass and the signature; whether every byte changes is not established.

Steps 4 and 5 now run to completion with the sub-block 1 descriptor on all 22 tested archives, and the metadata signature over the decoded spans verifies (RPF9-F102). That confirms the stored primary area is transformed in those archives and that a non-no-op descriptor is present. It does not show that every byte changes, and it does not decode the secondary area's storage state beyond running the step 5 span.

## Signature check

Step 2 checks a 256-byte value against a message built from metadata bytes (RPF9-F43). It writes only to new allocations, never to metadata.

The signature record comes from the `B` block:

| Sub-block | Layout                                                                      | Used                      |
| --------- | --------------------------------------------------------------------------- | ------------------------- |
| 6         | `u8` message type, `u16` key identifier at `+2`, 256-byte signature at `+4` | First choice              |
| 2         | `u32` key identifier, 256-byte signature at `+4`. Message type 0            | If sub-block 6 is missing |

Neither present, a message type other than 0 or 1, a signature outside the `B` block, a key identifier without key material, or a failed check all reject the archive.

The message is the concatenation of these spans:

| Message type | Spans, in order                                                                                                                                |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| 0            | `hdr[0x00..0x10)`, from the end of the signature to `hdr[0x08]`, then the secondary area if it is non-empty                                    |
| 1            | `hdr[0x00..0x10)`, from `hdr[0x18]` to the signature, from the end of the signature to `hdr[0x08]`, then the secondary area if it is non-empty |

Coverage:

- Step 2 runs after step 1 and before steps 4 and 5. It covers the `A` and `B` bytes as step 1 left them, and the primary and secondary areas as stored.
- Message type 0 leaves out `hdr[0x10..0x40)`, the `A` table and the part of `B` before the signature.
- No message type covers `hdr[0x10..0x18)` or any payload data.
- The check runs only while file object `+0x08` bit 0 is clear. After the first successful open the engine sets that bit, so later archives opened on the same file object skip the check (RPF9-F44).

The scheme is RSASSA-PKCS1-v1_5 with SHA-256 (RPF9-F92). The engine hashes the assembled message once and passes that 32-byte digest to the verifier, which applies SHA-256 again. The signed value is therefore the double hash (RPF9-F101):

```
digest     = SHA-256(message)
signed     = SHA-256(digest)
digestInfo = 30 31 30 0d 06 09 60 86 48 01 65 03 04 02 01 05 00 04 20 || signed
EM         = 00 01 FF...FF 00 || digestInfo
accept     = RSA public operation on the signature yields exactly EM
```

The verifier builds the DigestInfo itself. It requires the recovered payload to be 51 bytes and compares it with the computed DigestInfo; a raw 32-byte digest is rejected. The signature length is fixed at 256 bytes, so the key is 2048-bit. The RSA type is fixed in the verifier call and does not come from the archive. The synthetic rule is publicly reproducible with a synthetic key and synthetic messages. The concrete verification-key record and the archive signatures stay private-evidence supported.

The key record carries a 16-bit or 32-bit identifier, resolved through a static key registry that MUST yield exactly one match. This build supplies a DER `rsaEncryption` SubjectPublicKeyInfo with exponent 65537 (RPF9-F93). The registry location, identifier mapping and fingerprint are not published; the modulus bytes are not reproduced.

### Verified archive result

Step 2 runs after step 1, so the signed message is metadata after decryption. For the observed archives selector 9 keeps step 1 active, so the stored `A` and `B` bytes are ciphertext and a stored archive contains neither the signed message nor a readable signature. The recognized provider of [Key supply](#key-supply) supplies the missing step, and the whole chain runs end to end (RPF9-F102). All 22 tested local archives, 12 root archives and 10 under `pack/`, authenticate: step 1 decrypts, the type 1 record in `B` sub-block 6 supplies the signature, the message spans are hashed and double-hashed, and the static key verifies. None of them uses sub-block 2. The rules and the pipeline are public; the archive set, the signatures and the key identifier are private-evidence supported.

The archive is only partly authenticated even when the signature passes: coverage depends on the message type, and the check is skipped on later opens of the same file object. For archives using algorithm `0x10`, nothing else in the chain detects altered metadata.

### What is authenticated

| Layer                             | Authenticated | Basis                                                                                                                            |
| --------------------------------- | ------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| Signed metadata spans             | Yes           | RSA signature over the post-step-1 spans (RPF9-F102)                                                                             |
| Other metadata bytes              | No            | `hdr[0x10..0x18)` is outside every message type; for type 0 so are `hdr[0x18..0x40)` and the `B` prefix                          |
| Structurally valid native entries | No            | A plausible `A` table and column view follow from decryption; the signature covers bytes, not parsed entry semantics (RPF9-F100) |
| Payload contents                  | No            | No message type covers payload data                                                                                              |

A plausible `A` table is structural evidence that one ciphertext span decoded under the recognized key. It is not authenticity. Only a successful signature check authenticates the metadata, and it says nothing about later opens that skip step 2 or about payload bytes.

## Payload transform

Payload reads have their own transform path. The read routines call RVAs `0x19C380` (position the context), `0x1616150` (whole blocks) and `0x28CF9C0` (partial blocks), not the metadata span runner directly (RPF9-F38). The whole-block consumer calls slot `+0x30` of a per-stream algorithm object of the same class as the metadata cipher's object. That slot is shared, but the engine behind the object is selected by the descriptor's cipher type, and real transform descriptors select algorithm `0x11` (RPF9-F114, RPF9-F115).

| Part                            | Status                                                                                                                                                                                                        | Evidence             |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------- |
| Selection                       | Per entry, by the presence of key `0x286030A358A789FB` in the [schema](../../formats/containers/rpf9/schema.md#known-columns). Confirmed                                                                      | RPF9-F38             |
| Granularity                     | The engine stores `position & ~0xF` in a per-stream context, reads whole 16-byte blocks and processes them in place. A partial block reads the whole block, transforms it and copies the sub-range. Confirmed | RPF9-F110            |
| Seeks                           | Reposition the context to the stored cursor; the per-block position then selects the counter in mode 3. Confirmed                                                                                            | RPF9-F110, RPF9-F112 |
| Interaction                     | Entries with the flag never use the chunk fast path, and stored bytes are transformed before inflation. Confirmed                                                                                             | RPF9-F111            |
| Algorithm                       | Selected by the descriptor's cipher type. Sampled transform descriptors use type `0x11`, which selects algorithm `0x11`, a counter-mode keystream over the encoded block generator (RPF9-F115). Confirmed (call chain)                                                         | RPF9-F114, RPF9-F115 |
| IV repositioning                | Object mode 1 continues the CBC chain; mode 3 sets the IV to the 16-byte parameter plus the block index. The algorithm-`0x11` factory sets mode 3, the algorithm-`0x10` factory sets mode 2, which this slot refuses. Confirmed                                                   | RPF9-F112, RPF9-F115 |
| Key source                      | The descriptor is the value of the entry's transform field (RPF9-F114) and the key identifier resolves through the static registry (RPF9-F97) to one provider-2 state carrying the algorithm-`0x11` magic (RPF9-F116). Confirmed (sample)                                       | RPF9-F114, RPF9-F116 |
| Block program                   | Not reproduced. A transcription of the generator does not decode sampled chunks, so transformed payloads stay unsupported. Unknown                                                                                                                            | RPF9-F117            |
| Relation to the metadata cipher | Same object class, initializer, update and reset path, and a separate per-stream instance; the algorithm and engine differ. Confirmed                                                                                                                        | RPF9-F109, RPF9-F114 |

The read path is described in [payloads.md](../../formats/containers/rpf9/payloads.md#payload-transform). Routines are listed in the [function catalog](../../builds/gta-vi/scarlett-e95020b2/functions.md#entries-names-payloads).

### Cipher descriptor of a transform entry

The descriptor is the value of the entry field `0x286030A358A789FB`, not an archive descriptor (RPF9-F114):

| Offset  | Type     | Meaning        |
| ------- | -------- | -------------- |
| `+0x00` | `u32`    | Key identifier |
| `+0x04` | `u16`    | Cipher type    |
| `+0x06` | 16 bytes | Parameter      |

A stream attaches it with `0x1415DBE40` -> `0x141641EF0` -> `0x1428CEBC0` -> `0x140536A70`, the initializer the metadata descriptors also use, with mode 1, so the parameter reaches the algorithm object's `+0x20` and the type reaches the engine's 19-entry type table. The descriptor is therefore per entry, and different entries can carry different key identifiers and parameters.

### Algorithm `0x11`

Type `0x11` selects algorithm `0x11` (RPF9-F115). Its object carries mode 3, so slot `+0x30` repositions before every run: the counter becomes the 128-bit big-endian parameter plus the block index of the run.

The engine is a counter-mode keystream:

| Step   | Behavior                                                                                                                       |
| ------ | ------------------------------------------------------------------------------------------------------------------------------ |
| Init   | Validates a four-byte state magic, expands a 60-word schedule and sixteen key-dependent 256-byte tables, loads the counter       |
| Process | Generates one 16-byte block per counter value, XORs it into the data in place, and advances the counter once per block           |
| Reset  | Reloads the counter from the parameter plus block index and drops the unused tail of a partial block                             |

The block generator runs fourteen rounds over two fixed table regions read from the image: sixteen 256-byte stage tables, then sixteen 256-entry round tables. Its exact round program is not reproduced, so no payload can be transformed (RPF9-F117). The earlier negative probe mixed the archive descriptor with the metadata cipher and therefore says nothing about this engine (RPF9-F113).

## Synthetic and public checks

A reader without game data can check the cryptographic claims at the level they are published:

| Check           | Input                                                                                                                         | Expected                                                                                                                                             |
| --------------- | ----------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Block transform | The engine's fixed tables read from a user-provided executable, a synthetic encoded key state and the FIPS-197 AES-256 vector | The recovered block operation decrypts to the FIPS plaintext, and further synthetic blocks agree (RPF9-F91)                                          |
| CBC order       | The same block operation with the engine's chaining rule and the NIST SP 800-38A AES-256-CBC vector                           | Four blocks decrypt to the published plaintext                                                                                                       |
| Signature rule  | A synthetic RSA-2048 key and synthetic messages                                                                               | The double-hash signature is accepted; single-hash, mutated-message, mutated-signature, short-signature and wrong-key cases are rejected (RPF9-F101) |
| A-table gate    | Synthetic 8-byte records and a synthetic `B` length                                                                           | Well-formed tables pass; zero or duplicate IDs, out-of-range offsets and tables without a known sub-block ID fail (RPF9-F100)                        |

The checks use author-created keys, states, tables and records. They validate the published rules, not any real archive. Engine-fixed tables and real key states are never redistributed.

## Implementation

Leonida Forge implements the chain in `crates/rage9/src/rpf/metadata/`:

| Module         | Role                                                                                       |
| -------------- | ------------------------------------------------------------------------------------------ |
| `transform/`   | Span runner, descriptor parsing, `Cipher` and `CipherSource`                               |
| `recognize/`   | Structural recognition of the static key registry and the static cipher descriptor         |
| `provider/`    | Fixed-table recognition, encoded block operation and archive-dependent candidate selection |
| `probe.rs`     | Bounded step-1 compatibility probe and `A`-table validation                                |
| `signature.rs` | Signature record, message spans, key resolution and double-hash verification               |
| `verify.rs`    | Steps 1, 2, 4 and 5, the trust classification and authenticated metadata opening           |

`verify::open_authenticated` returns parsed metadata only when the signature verifies and the decoded table parses. The type boundary keeps unverified bytes out of the trusted reader. `lforge archive probe <archive> --executable <exe>` reports the recognition, signature, archive-pass and trust stages. `lforge archive metadata <archive> --executable <exe> --entries` lists native rows, and `lforge archive extract <archive> --executable <exe> --row <n> --output <file>` extracts a supported payload. Native listing requires authentication for processed metadata; unprocessed metadata remains readable without an executable. Decoded but unsigned metadata is reported separately and never unlocks the trusted path.

## Relation to earlier RPF versions

Whether RPF9 shares any cryptography with earlier RPF versions is unknown. Nothing in the analyzed code supports that assumption.

## Open questions

- Algorithms 1, 2 and `0x12`.
- Whether the 240-byte schedule is the standard AES-256 expansion of a raw key in encoded form. The block transform is established (RPF9-F89, RPF9-F90, RPF9-F91); the key blob was not read.
- Whether a second executable build registers the same keys or binds to the same archives. Every verified result covers build e95020b2 and its local archive set.
- The cipher type of `B` sub-block 1 in real archives. It is readable only after step 1, which the provider now performs.
- The per-archive key identifier and IV used by steps 4 and 5, which are inside sub-block 1 and are not published.
- Whether the key lookup succeeds for the default descriptor, which decides whether algorithm 0 archives open at all.
- Which message types real archives use beyond the observed type 1, and whether every build registers the same key.
- The role of the `B` trailer.
- The `A` table content is identical across observed archives although it lies inside a processed span. The static descriptor uses a fixed key identifier and a fixed IV, which would explain identical stored bytes for identical plaintext. Not verified.
- The block program of the payload transform's algorithm `0x11`: its round structure, table roles and key use. The descriptor, the algorithm selection and the key state are established (RPF9-F114 to RPF9-F116), but no transformed payload decodes yet (RPF9-F117). Payload bytes are not authenticated by the metadata signature.
