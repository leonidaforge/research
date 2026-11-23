# RPF9 names

RPF9 stores no file name text. A row holds a 64-bit name hash and a namespace in its columns. The engine turns them into a string at runtime (RPF9-F18).

## Name lookup

The engine looks up `(namespace, hash)` in a runtime string dictionary (see [engine](../../../engine/README.md#hashed-string-dictionary)). The result is the stored string or null.

| Part | Status |
|---|---|
| Hash width | 64 bits. Confirmed |
| Hash function | Unknown |
| Namespace values | Unknown |
| Columns holding hash and namespace | Unknown keys. Path lookup reads them |
| Behavior when the hash is unknown | The lookup returns null |

What a caller does with a null name during path lookup is not documented.

RPF9 name hashes are 64-bit. Hash functions of earlier RPF versions must not be assumed. A hash function for RPF9 names must be verified in engine code before matches against known strings count as evidence.

## Extensions

The extension comes from a numeric type ID, not from the name (RPF9-F19).

- The engine maps the type ID to an extension string.
- `0xFF` means no extension.
- An ID without a table entry gives a default string.

The type ID table is not decoded. The column holding the type ID is not identified.

## Path matching

Path lookup rebuilds `name + extension` for each row and matches it with a substring search, as described in [entries.md](entries.md#path-lookup).

## Offline consequences

A tool without the engine's dictionary can only show names whose strings it already knows and can hash. That needs the hash function, which is unknown. Until then, offline tools can show row numbers and raw hashes, but no names.
