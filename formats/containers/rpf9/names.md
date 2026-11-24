# RPF9 names

RPF9 stores no file name text. A row holds a hash of its path. The engine opens an entry by hashing the requested path and searching the rows for that hash (RPF9-F55). It does not need to turn a stored hash back into a string to open a file.

A separate runtime dictionary can map hashes back to strings. It is optional, it is not filled from archives, and [path matching by substring](#substring-lookup) depends on it (RPF9-F60).

## Path to row

The resolver takes a path string and returns a row index or `0xFFFF` (RPF9-F55):

1. Mount prefix. The archive object holds a prefix length `P` and a 64-bit hash of the prefix. If the path is shorter than `P`, the result is `0xFFFF`. Otherwise the first `P` bytes are hashed with the [folded 64-bit hash](#64-bit-hash) and compared with the stored hash. A mismatch gives `0xFFFF`.
2. The rest of the path after the prefix is split at its last `.` into a stem and an extension.
3. The extension selects a type ID ([extensions](#extensions)).
4. The type decides the key ([type classes](#type-classes)):
   - 64-bit class: `key = hash64(stem)`. The resolver looks for a row with name hash `key` and type ID `type`.
   - 32-bit class: `key = joaat(stem)`. The resolver looks for a row whose `u32` value of key `0xB7076B6245D35FB5` is `key` and whose type ID is `type`.
5. No `.` in the rest, or an extension that maps to no type: `key = joaat(rest)` over the whole rest including any extension, with type `0xFF`.

The row lookup is described [below](#row-lookup).

## Mount prefix

The archive stores a prefix length and the [folded 64-bit hash](#64-bit-hash) of the prefix. Two operations set them (RPF9-F61):

| Operation | Prefix | Confidence |
|---|---|---|
| Construction | Default derived from the archive's own path, see below | Confirmed |
| Mounting through the archive's mount method | The caller's mount prefix. It replaces the default | Confirmed |

The effective prefix is the mount prefix for a mounted archive. It is the default only for an archive that was never mounted that way, for example a nested archive that is opened but not mounted.

Default prefix at construction:
1. Take the file object's stored path. That is the archive's resolved device path ([engine](../../../engine/README.md#file-objects-and-devices)).
2. If the path starts with `memory:`, the prefix ends just after the next `:` following `memory:`.
3. Otherwise the prefix ends just after the last `/` or `\`. Without either, the prefix is empty.
4. The prefix is cut to at most 255 bytes.

The empty prefix has length 0 and hash 0.

Mount prefix: the mount table accepts a prefix only if it is non-empty, ends in `/` or `\` and is at most 253 bytes long ([engine](../../../engine/README.md#mount-table)). The same string becomes the archive's prefix.

Consequences:
- Both prefixes include the trailing separator.
- With the default prefix, entries are addressed as `<directory of the archive><stem>.<ext>`. With a mount prefix, they are addressed as `<mount prefix><stem>.<ext>`. The archive's own file name is part of neither.
- The resolver compares only the first `P` bytes of a request by folded hash, so case and separator style do not matter in the prefix.
- The mount prefixes used by the game are runtime state set by engine code. They are not stored in the archive.

How the path normalizers that produce the stored path format it is not established. Because matching folds case and separators, only the directory structure matters for the default prefix.

## Nested archives

A nested archive is a row of type 0 (`rpf`) in a parent archive. It is opened by path like any file. The parent archive object is itself the device that serves the path ([engine](../../../engine/README.md#archives-as-devices), RPF9-F65, RPF9-F67, RPF9-F70):

1. Device selection finds the parent, because the path lies under a prefix the parent is mounted at.
2. The parent resolves the path to a row with the same resolver. An unresolved path fails the open.
3. The row's payload offset, relative to the parent's base, becomes the child's base offset.
4. The row's logical size becomes the child's size.
5. The child reads with the parent's handle that the row's [read-source index](payloads.md#read-source) selects in the parent: the parent's main handle or one of its alternates.
6. The child gets its own file object, tag and archive object. Its prefix is the default derived from its own path, unless it is mounted itself. Its own alternate handle array starts empty. It does not inherit the parent's alternates, so read-source indices of entries inside the child refer to the child's own handles (RPF9-F73).

All child reads then go through the parent as [positional reads with added bases](payloads.md#nested-reads).

Matching a nested archive therefore works in two steps. Find `<parent prefix><stem>.rpf` in the parent. Then match the nested archive's entries under its own effective prefix.

Raw storage: the nested read path does not decompress, decrypt or apply the payload transform, and the open checks neither the compression mode nor the transform flag. A nested archive is readable through this path only if its row stores the archive bytes as they are, starting at the payload offset. All reads are clamped to the row's logical size, not its stored size. That every nested archive in valid game data is stored this way is Probable. It follows from the code, not from a check found in it.

### Preloaded construction

The engine has a second way to build an RPF9 archive object. It uses the same class and interface as the regular one (RPF9-F75):

1. The file object is constructed from a caller-supplied 0x20-byte block instead of querying the device. The block MUST start with the RPF9 magic. Its `+0x10` gives the size and `+0x18` the time.
2. The archive takes its metadata from one of two sources:
   - **Parent copy.** If the file's device is a version-9 archive with loaded metadata and column `0xC26722D233648AE7`, the parent resolves the file's path to a row. The archive copies `u32@+4` bytes, the total metadata size, from that row's value.
   - **Device read.** Otherwise it reads the block's `u32@+4` bytes from the file's base.
3. The constructor reads no header and runs no layout or validation. A separate archive method lays out the metadata and runs the validation chain on the copied or read buffer.

The batch path resolution record has exactly the block's layout. It carries the 16 header bytes from the same column, the stored size and the time. That the engine uses batch resolution in a parent to build the blocks for nested archives, and validates them afterwards, is Probable. The layouts match, but no direct call chain was observed.

Differences to the regular open:
- The size is the block's size, which batch resolution fills with the stored size, not the logical size.
- With the parent copy, the nested archive's metadata comes from the parent's value pool, not from the nested archive's payload. Entry payloads are still read through the parent as raw positional reads.

## Normalization

Both hashes map every input byte through the same table before mixing: ASCII `A` to `Z` become `a` to `z`, and `\` becomes `/`. All other bytes are unchanged (RPF9-F56, RPF9-F57).

- Matching is case-insensitive for ASCII only. Bytes above `0x7F` must match exactly.
- `\` and `/` are interchangeable.
- Nothing else is normalized. Repeated separators, `.` and `..` components and surrounding spaces are hashed as they are.
- The extension test is a case-sensitive string comparison. `ITEM.YDR` and `item.ydr` give the same stem hash but may select different types.

## 64-bit hash

The hash is MurmurHash3 x64-128 with seed 0, returning the first 64-bit word of the result, with one deviation: only the low 8 bits of the input length are mixed into the final state (RPF9-F56). For inputs shorter than 256 bytes the result equals the standard algorithm on the normalized input. From 256 bytes on, it differs.

```text
hash64(s) = MurmurHash3_x64_128_h1(fold(s), seed = 0, length_mixed = len(s) & 0xFF)
```

A null pointer and the empty string both give 0. The engine also has a variant without folding. It is not used for RPF9 paths.

## 32-bit key

The 32-bit key is Jenkins one-at-a-time ("joaat") over the folded bytes with seed 0 (RPF9-F57):

```text
for each byte b: h += fold(b); h += h << 10; h ^= h >> 6
h += h << 3; h ^= h >> 11; h += h << 15
```

If the string starts with `"`, the quote is skipped and hashing stops at the next `"` or at the end. `"a/b"x`, `"a/b` and `a/b` therefore have the same key.

That the archive stores `joaat(stem)` in key `0xB707…` follows from the lookup. It has not been checked against archive data.

## Type classes

Each type ID belongs to exactly one class: 64-bit name hash or 32-bit key. The engine keeps two complementary per-type tables. One gives a namespace for the 64-bit class, the other a namespace for the 32-bit class, and `0xFF` marks the class a type does not use (RPF9-F31, RPF9-F59). Both tables are filled at runtime by a one-time initializer. Their contents are executable data and are not reproduced here.

The namespace numbers only matter for the [runtime dictionary](#runtime-dictionary). The resolver hashes every 64-bit-class stem with the same function.

## Extensions

The extension and the type ID map to each other through executable tables (RPF9-F19, RPF9-F59).

- Type to extension: `0xFF` means no extension. An ID without a table entry gives a default string.
- Extension to type: a case-sensitive comparison against fixed strings, then against registered handlers. No match gives `0xFF`.
- `rpf` maps to type 0, which belongs to the 64-bit class. Nested archives are rows of type 0.

The tables are not reproduced here.

## Row lookup

Two row lookups exist, one per class. Both use the same method, chosen by a per-archive sorted flag (RPF9-F58):

| Sorted flag | Method |
|---|---|
| Clear | Scan rows `0 .. E-1`. Return the first row whose key and type ID match |
| Set | Binary search for the first row not below the key, then scan forward over rows with an equal key until the type ID matches |

In sorted archives the comparator puts every row with `0xB707… == 0` first, in ascending unsigned order of the 64-bit name hash. Rows with a nonzero 32-bit key come after them. The forward scan of the 64-bit lookup stops at the first row with a nonzero 32-bit key.

### Sorted flag

The sorted flag is bit 0 of the byte at file object `+0x09` (RPF9-F63). It is computed once, after the first successful open of the file object:

```text
sorted = (u32@0x28 == fingerprint)
```

The header byte `u8@0x2D` selects the fingerprint:

| `u8@0x2D` bit 3 | Fingerprint |
|---|---|
| Clear | A value the engine computes once at startup over all 256 type IDs |
| Set | Computed over the type IDs listed in `B` sub-block 9 ([metadata.md](metadata.md#a-table-and-b-block)) |

Both fingerprints hash a bit mask. Bit `i` is set when the `i`-th type ID uses the 32-bit class. For the startup value the `i`-th type ID is `i`; for sub-block 9 it is the `i`-th listed ID. The mask has `ceil(n / 8)` bytes for `n` type IDs.

The 32-bit hash over the mask has the constants and length branches of CityHash32. Equivalence with CityHash32 has not been checked (Probable).

Interpretation: the sort order depends on which rows carry a 64-bit hash and which a 32-bit key. The header records the type classification the archive was sorted under. If the engine classifies the types differently, the fingerprints differ and the engine scans linearly. This reading is Probable.

The concrete startup fingerprint is not established, because it depends on whether the type tables are filled before the static initializer that computes it runs.

A reader that does not reproduce the fingerprint SHOULD scan linearly, as the engine does when the fingerprints differ.

Collisions and duplicates:
- The first row in scan order that matches both key and type wins.
- Nothing detects a collision. A second row with the same key and type is unreachable through the resolver.
- The same stem with different types, i.e. different extensions, is fine.

## Runtime dictionary

The engine keeps hash-to-string dictionaries per namespace, one set for 64-bit keys and one for 32-bit keys (RPF9-F18, RPF9-F60). The mechanism is described in [engine](../../../engine/README.md#hashed-string-dictionary).

What matters for RPF9:
- Strings enter the dictionaries when structured data files that spell them out are loaded. Archives do not fill them.
- A dictionary string for a row is the string whose hash equals the row's key. Given the resolver, that is the stem: the path relative to the mount prefix, without the last extension. Probable, by hash equality.
- At initialization, insertion is disabled for all 64-bit namespaces. No direct code that enables it was found. Indirect writers were not excluded, so the dictionaries MUST NOT be assumed to stay empty.

Reverse lookup for one row: the 64-bit dictionary under the row's 64-bit-class namespace and name hash; if that misses, the 32-bit dictionary under the 32-bit-class namespace and the `u32` key. The extension for the row's type is appended for display.

## Substring lookup

The archive interface also has a path lookup that works through the dictionary (RPF9-F20):

1. Take the part of the request after the first `/`. The code does not check that a `/` exists. Without one it reads an invalid pointer.
2. For every row `0 .. E-1`, get the row's dictionary string by the reverse lookup above. Rows without a string are skipped.
3. Search for the requested part inside the dictionary string with a case-sensitive, unanchored substring search. The code also builds `name.extension` in a buffer but never reads it.
4. Collect the matches in row order and return the first.

An empty requested part matches every row that has a string. This lookup depends on the dictionary, so it finds nothing for rows whose strings were never registered.

## Offline consequences

A tool can match entries by hashing candidate paths. It needs:
- the plain metadata, i.e. descriptors, cells and pools;
- candidate paths from outside the archive;
- the archive's effective [mount prefix](#mount-prefix): the runtime mount prefix, or the default derived from the archive's resolved path;
- the extension-to-type table, to choose the class and the type ID.

With those, a candidate matches a row when its stem hash or 32-bit key and its type ID agree. Rows that match no candidate can only be shown by type ID, hash and size.

## Synthetic example

Mount prefix `dev:/synthetic/Packs/`, request `dev:/synthetic/Packs/Sub\Dir/Item.Name.rpf`:

| Step | Value |
|---|---|
| Rest | `Sub\Dir/Item.Name.rpf` |
| Stem, extension | `Sub\Dir/Item.Name`, `rpf` |
| Type | 0 |
| Normalized stem | `sub/dir/item.name` |
| `hash64(stem)` | `0x3FC602FCF22D7472` |
| `hash64("alpha/beta/gamma")` | `0x7489FBD94F2A4C86`, the same for `ALPHA\BETA\GAMMA` |
| `joaat("alpha/beta")` | `0x75438640` |
