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
| [entries.md](entries.md) | Entry IDs, location records, enumeration, path lookup |
| [names.md](names.md) | Name hashes, namespaces and extensions |
| [payloads.md](payloads.md) | Payload addressing, reads, decoding, chunk tables, observed storage layout |
| [cryptography/rpf9](../../../cryptography/rpf9/README.md) | Metadata cipher selection and spans, payload transform |

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
| Name hash column, namespace source | Confirmed. Hash algorithm and namespace table contents unknown |
| `A` table | Confirmed (index into `B`). `B` content unknown |
| Metadata cryptography | Selection and spans confirmed. Operation probable |
| Payload transform | Routing confirmed. Algorithm and key source unknown |
| Directory hierarchy | Unknown |

## Blockers for native TOC extraction

A tool cannot yet list an archive's files with their names and read them from the metadata alone. Missing:

1. Whether the descriptors, cells and pools are stored in plain form. The established cipher spans do not cover them, but the engine only reads them after validation. See [cryptography/rpf9](../../../cryptography/rpf9/README.md#open-questions).
2. Name strings. Names are hashes, so they resolve only against an external list of known strings. That also needs the hash function and the per-type namespace tables, see [names.md](names.md#name-lookup).
3. Entries with the payload transform flag. Their stored bytes cannot be read without the unknown transform.
4. A check of the location record layouts against real archives. The layouts come from code only.

With plain metadata, the [location records](entries.md#location-records) give each row's offset, sizes, type and compression mode without scanning.

## Not to be assumed

- RPF9 stores a columnar table, not an array of entry records. No structure has been shown to carry over from earlier RPF versions.
- Name hashes are not known to use the hash function of any earlier RPF version.
- A row is not known to carry exactly one location record in real data. The engine uses the first of R, F, A that is present.
