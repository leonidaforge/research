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
| Mount prefix, sorted flag, entry ID tag | Confirmed (origin). Fingerprint hash identity probable |
| Nested archives | Confirmed (opened by path, sized from the parent row). Device selection not traced |
| `A` table, `B` sub-blocks | Confirmed (index into `B`). Uses of sub-blocks 1, 2, 6 and 9 known, sub-block 3 unknown |
| Validation chain order and conditions | Confirmed |
| Metadata cipher spans | Confirmed. CBC decryption without authentication for the observed cipher type. Block transform not reproducible with standard AES |
| Signature check | Data flow confirmed, conditional. Signature algorithm unknown |
| Stored primary area | Probably transformed in the inspected archives |
| Structural checks in validation | None found |
| Payload transform | Routing confirmed. Algorithm and key source unknown |
| Enumeration, directory hierarchy | None on the traced paths. Paths are flat hashed stems |

## Blockers for native TOC extraction

A tool cannot yet list an archive's files with their names and read them from the metadata alone. Missing:

1. The stored descriptors, cells and pools. They lie in the step 4 cipher span, and in the inspected archives they are probably stored transformed. Reading them needs the transform, which is unknown. See [cryptography/rpf9](../../../cryptography/rpf9/README.md#on-disk-state-of-the-primary-area).
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
