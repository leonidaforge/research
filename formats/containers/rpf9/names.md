# RPF9 names

RPF9 stores no file name text. A row holds a 64-bit name hash. The engine turns it into a string at runtime with a namespace that depends on the row's type ID (RPF9-F18, RPF9-F30, RPF9-F31).

## Name lookup

Path lookup resolves a row's name in these steps:

1. Read the type ID from the row's [location record](entries.md#location-records).
2. Look up the namespace: `ns = table1[typeId]`, a `u8` table in the executable's `.data` section at RVA `0x7A0B100`. Before the read, the lookup runs a guarded one-time initializer at RVA `0x56C9290`. That this initializer fills the table is Probable. It was not analyzed.
3. Read the name hash, the `u64` value of key `0x73BCB72DCE74F11F`.
4. If `ns != 0xFF` and the hash is nonzero, look up `(ns, hash)` in the runtime string dictionary (see [engine](../../../engine/README.md#hashed-string-dictionary)). The result is the stored string or null.
5. If step 4 did not run or returned null, try a fallback. Take `ns2 = table2[typeId]` from the `u8` table at RVA `0x7A0B000`. If `ns2 != 0xFF` and the `u32` value of key `0xB7076B6245D35FB5` is nonzero, call a second lookup at RVA `0x4DA8040`.
6. If neither path returns a string, the row cannot match.

The namespace is a property of the type, not of the archive. An offline tool needs the contents of both tables. They are probably filled at runtime, so the executable's static bytes may not hold them.

| Part | Status |
|---|---|
| Hash width | 64 bits. Confirmed |
| Hash column | `0x73BCB72DCE74F11F`. Confirmed |
| Namespace source | Per-type table in the executable. Confirmed |
| Namespace table contents | Unknown |
| Hash function | Unknown |
| Behavior when the hash is unknown | The lookup returns null |
| Fallback path | Arguments and meaning of `0x4DA8040` and key `0xB707…` unknown |

RPF9 name hashes are 64-bit. Hash functions of earlier RPF versions must not be assumed. A hash function for RPF9 names must be verified in engine code before matches against known strings count as evidence.

## Extensions

The extension comes from the numeric type ID, not from the name (RPF9-F19).

- The engine maps the type ID to an extension string.
- `0xFF` means no extension.
- An ID without a table entry gives a default string.

The type ID table is not decoded.

## Path matching

Path lookup rebuilds `name + "." + extension` for each row and matches it with a substring search, as described in [entries.md](entries.md#path-lookup).

## Offline consequences

A tool without the engine's dictionary can only show names whose strings it already knows and can hash. That needs the hash function and the namespace tables, and both are unknown. Until then, offline tools can show row numbers, type IDs and raw hashes, but no names.
