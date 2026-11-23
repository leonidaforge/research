# RPF9

RPF9 is the archive format of GTA VI. RPF9 archives are identified by the magic value `0x52504639` (`9FPR` on disk).

An RPF9 archive starts with a metadata area. Its table of contents is a dictionary-encoded columnar table, not an array of entry records. Each column has a descriptor with a hashed field key. Each row has one compact index per column, and the index selects a value from that column's value pool. Names are stored as hashes. Payload data follows the metadata.

All integers are little-endian. Offsets are relative to the start of the archive.

## Documents

| Document | Content |
|---|---|
| [header.md](header.md) | 16-byte header, 0x40-byte prefix, read modes |
| [metadata.md](metadata.md) | Region layout of the metadata area |
| [schema.md](schema.md) | Column descriptors and cell addressing |
| [entries.md](entries.md) | Entry IDs, enumeration, path lookup, sizes |
| [names.md](names.md) | Name hashes and extensions |
| [payloads.md](payloads.md) | Payload reads and observed storage layout |
| [cryptography/rpf9](../../../cryptography/rpf9/README.md) | Cipher selection and processed spans |

Evidence: [evidence/rpf9/INDEX.md](../../../evidence/rpf9/INDEX.md). Corrections to earlier models: [research-history.md](../../../evidence/rpf9/research-history.md).

## Status

| Part | Status |
|---|---|
| Magic, header sizes, read modes | Confirmed |
| Prefix counts `A` to `F`, region layout | Confirmed |
| Column descriptor key, base offset, element width | Confirmed |
| Cell addressing and value pointers | Confirmed |
| Entry ID composition | Confirmed |
| Name and extension lookup | Confirmed. Hash algorithm unknown |
| Column identities | Size columns probable. The rest unknown |
| Cryptographic processing | Selection and spans confirmed. Operation probable |
| Directory hierarchy | Unknown |
| Payload offsets, compression path | Unknown in code. Storage layout observed in data |

## Blockers for native TOC extraction

A tool cannot yet list an archive's files with their names from the metadata alone. Missing:

1. The meaning of descriptor bytes `+0x08` and `+0x12`, which probably carry type or bounds information.
2. Which field key is the name hash, the payload offset, the compression mode or the flags. Only the size columns are probable.
3. Whether the descriptors, cells and pools are stored in plain form. The established cipher spans do not cover them, but the engine only reads them after validation. See [cryptography/rpf9](../../../cryptography/rpf9/README.md#open-questions).
4. Name strings. Names are hashes, so they resolve only against an external list of known strings.
5. The roles of the `A` table and the `B` block.

## Not to be assumed

- RPF9 stores a columnar table, not an array of entry records. No structure has been shown to carry over from earlier RPF versions.
- Name hashes are not known to use the hash function of any earlier RPF version.
