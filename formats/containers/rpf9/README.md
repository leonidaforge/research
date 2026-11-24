# RPF9

RPF9 is the archive format of GTA VI. RPF9 archives are identified by the magic value `0x52504639` (`9FPR` on disk).

An RPF9 archive starts with a metadata area. Its table of contents is a dictionary-encoded columnar table, not an array of entry records. Each column has a descriptor with a hashed field key. Each row has one compact index per column, and the index selects a value from that column's value pool. Names are stored as hashes. Each row has a location record with the payload's offset, sizes, type and compression mode. Payload data follows the metadata.

All integers are little-endian. Offsets are relative to the start of the archive.

## Documents

| Document | Content |
|---|---|
| [header.md](header.md) | 16-byte header, 0x40-byte prefix, read modes |
| [metadata.md](metadata.md) | Region layout of the metadata area, `A` table |
| [schema.md](schema.md) | Column descriptors, cell addressing, known field keys |
| [entries.md](entries.md) | Entry IDs, location records, batch operations, enumeration and hierarchy limits |
| [names.md](names.md) | Path resolution, name hashes, type classes, extensions, runtime dictionary |
| [payloads.md](payloads.md) | Payload addressing, reads, decoding, chunk tables, observed storage layout |
| [cryptography/rpf9](../../../cryptography/rpf9/README.md) | Validation chain, metadata cipher spans, signature check, payload transform |

Evidence: [evidence/rpf9/INDEX.md](../../../evidence/rpf9/INDEX.md). Corrections to earlier models: [research-history.md](../../../evidence/rpf9/research-history.md).

## Status

| Part | Status |
|---|---|
| Magic, header sizes, read modes | Confirmed |
| Prefix counts `A` to `F`, region layout | Confirmed |
| Column descriptor key, base offset, element width | Confirmed |
| Column descriptor `+0x08`, `+0x12` | Unknown. Not read by the traced accessors |
| Cell addressing and value pointers | Confirmed |
| Entry ID composition | Confirmed |
| Location records R, F, A | Confirmed (layouts and accessor order). Use in real data not checked |
| Payload address | Confirmed |
| Read path, seek, decoder dispatch, chunk tables | Confirmed. Codec identity probable (zlib) |
| Path resolution and name hashes | Confirmed. Folded MurmurHash3 x64-128 variant and joaat. Type tables not published |
| Mount prefix, sorted flag, entry ID tag | Confirmed (origin). Mounting replaces the default prefix. Fingerprint hash identity probable |
| Nested archives | Confirmed (opened through the parent archive as device, positional reads without decoding). Raw storage requirement probable |
| `A` table, `B` sub-blocks | Confirmed (index into `B`). Uses of sub-blocks 1, 2, 3, 6 and 9 known |
| Validation chain order and conditions | Confirmed |
| Metadata cipher spans | Confirmed. CBC decryption without authentication for the observed cipher type. The block transform is encoded AES-256: reproducible with the engine's fixed tables and key state, not with a standard AES API |
| Signature check | Confirmed, conditional. RSASSA-PKCS1-v1_5 with SHA-256 over the double hash of the signed spans and a 2048-bit RSA key. Verifies on all 22 inspected archives once step 1 runs. Metadata only |
| Stored primary area | Transformed in the inspected archives. Step 4 decodes it and the metadata signature verifies |
| Structural checks in validation | None found |
| Payload transform | Routing confirmed. Algorithm and key source unknown |
| Enumeration, directory hierarchy | None on the traced paths. Paths are flat hashed stems |

## Blockers for native TOC extraction

A tool cannot yet list an archive's files with their names and read them from the metadata alone. Missing:

1. Column identities. The bytes are recoverable: steps 4 and 5 decode the primary and secondary areas with the `B` sub-block 1 descriptor, and the decoded metadata authenticates on the tested archives. Most column meanings are still unknown, see [schema.md](schema.md).
2. Name strings. Names are hashes, so they resolve only against an external list of candidate paths. Matching also needs the archive's mount prefix and the extension-to-type table, see [names.md](names.md#offline-consequences).
3. Entries with the payload transform flag. Their stored bytes cannot be read without the unknown transform.
4. A check of the location record layouts against real archives. The layouts come from code only.

Once the metadata is readable, the [location records](entries.md#location-records) give each row's offset, sizes, type and compression mode without scanning.

The engine does not validate the table's structure. A tool that reads RPF9 metadata MUST bounds-check counts, offsets and indices itself.

## Not to be assumed

- RPF9 stores a columnar table, not an array of entry records. No structure has been shown to carry over from earlier RPF versions.
- Name hashes follow the scheme in [names.md](names.md). The hash scheme of an earlier RPF version MUST NOT be assumed for RPF9.
- Native code was not found to enumerate archive contents or to store directories.
- A row is not known to carry exactly one location record in real data. The engine uses the first of R, F, A that is present.
