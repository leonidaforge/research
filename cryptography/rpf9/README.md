# RPF9 cryptography

RPF9 archives pass through a cryptographic step while the engine opens them. The step processes selected spans of the [metadata area](../../formats/containers/rpf9/metadata.md) in place, and a failure rejects the archive. The algorithm is unknown, and so is whether the step decrypts or only verifies.

Payloads of some entries go through a separate 16-byte block transform when they are read. See [Payload transform](#payload-transform).

## Position in archive initialization

1. Read the header and metadata ([header.md](../../formats/containers/rpf9/header.md#read-modes)).
2. Compute the region layout from the plain prefix.
3. Run the validation chain. The cryptographic passes run here, and failure abandons the archive (RPF9-F23).
4. Store the region pointers in the metadata view that all lookups use (RPF9-F07).

The prefix counts are read before step 3, so they are stored in plain form.

## Selection

The byte at prefix `0x2E` controls the step (RPF9-F24):

| Value | Effect |
|---|---|
| 0 | No cryptographic pass |
| bit 0 | Selects one of two span sets |
| `value >> 1` | Selects a cipher descriptor. Two indices map to static descriptors. Any other index falls back to a default descriptor |

The observed value is 9: bit 0 set, descriptor index 4, which is one of the two static descriptors.

## Descriptors and keys

A descriptor holds (RPF9-F25):

| Field | Meaning |
|---|---|
| 32-bit key identifier | Names a key that the engine looks up at runtime |
| `u16` cipher type | Mapped to an algorithm ID through a 19-entry table |
| 16-byte parameter | Purpose unknown |

Both static descriptors map to the same algorithm ID. The engine creates the algorithm object from a factory and resolves the key by its identifier. The key is not stored inline in the descriptor or in the archive. The cipher context lives in a per-thread slot.

Descriptor values, key identifiers and algorithm IDs are not published.

## Processed spans

With bit 0 set (RPF9-F26):

| Span | Range |
|---|---|
| `A` table | All `A * 8` bytes |
| `B` block | All `B` bytes except the last `u32@0x30` bytes (observed: 16) |
| Secondary area | `hdr[0x08]` to `hdr[0x04]`, in a separate pass |

The span set selected when bit 0 is clear is not described. The bytes excluded from the `B` block are a plausible authentication tag (see below).

## Operation

The span runner initializes the cipher from the descriptor. It calls `update` once per span, with the same buffer as input and output, then calls `final`, which returns a boolean (RPF9-F27).

| Interpretation | Status |
|---|---|
| In-place transformation of each span | Confirmed: input and output pointers are identical |
| Result checked by a boolean `final` that can reject the archive | Confirmed |
| Authenticated decryption with a 16-byte tag | Probable |
| Verification only, data unchanged | Not excluded |

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

- Algorithm, mode and the role of the 16-byte descriptor parameter.
- Decryption versus verification.
- The span set for selector values with bit 0 clear.
- The column descriptors, primary index store and primary value pool lie outside the established spans. Lookups read them only after validation, but whether they are stored transformed is unknown (RPF9-F28).
- The `A` table content is identical across observed archives although it lies inside a processed span. With a per-archive key or nonce that would be unexpected. It is unexplained.
- The payload transform's algorithm, key source and relation to the metadata cipher. Payload reads do not call the span runner directly (RPF9-F38).
