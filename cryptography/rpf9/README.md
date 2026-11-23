# RPF9 metadata cryptography

RPF9 archives pass through a cryptographic step while the engine opens them. The step processes selected spans of the [metadata area](../../formats/containers/rpf9/metadata.md) in place, and a failure rejects the archive. The algorithm is unknown, and so is whether the step decrypts or only verifies.

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

## Relation to earlier RPF versions

Whether RPF9 shares any cryptography with earlier RPF versions is unknown. Nothing in the analyzed code supports that assumption.

## Open questions

- Algorithm, mode and the role of the 16-byte descriptor parameter.
- Decryption versus verification.
- The span set for selector values with bit 0 clear.
- The column descriptors, primary index store and primary value pool lie outside the established spans. Lookups read them only after validation, but whether they are stored transformed is unknown (RPF9-F28).
- The `A` table content is identical across observed archives although it lies inside a processed span. With a per-archive key or nonce that would be unexpected. It is unexplained.
- Whether payloads use the same span runner.
