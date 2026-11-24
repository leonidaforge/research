# Engine

Runtime mechanisms that more than one format uses. Everything here was observed in one executable, [scarlett-e95020b2](../builds/gta-vi/scarlett-e95020b2/README.md), and has so far only been followed through the RPF9 code paths. Other RAGE versions or other parts of GTA VI may behave differently.

## Hashed-string dictionary

The engine maps a hash back to a string through runtime dictionaries (RPF9-F18, RPF9-F60).

Structure:
- There are two sets of dictionaries: 16 namespaces keyed by `u64` hashes and 31 namespaces keyed by `u32` hashes.
- Each namespace has a control block with a lock, a hash function, an allocator and a flags byte. Bit 1 of the flags enables insertion.
- Lookups probe a per-thread cache first, then the global map under a shared lock. A hit is copied into the cache.
- The maps are SwissTable-style. Groups of 0x110 bytes hold 16 control bytes and 16 `{key, string}` slots.
- A lookup compares only the key. A zero key and a miss both return null.

Hash functions per namespace:
- Most 64-bit namespaces use the folded MurmurHash3 variant described in [names.md](../formats/containers/rpf9/names.md#64-bit-hash). A few use the same hash without folding. None of those few is used for RPF9 types.
- The 32-bit namespaces use joaat.

Insertion:
- When the namespace's insertion flag is clear, nothing is stored.
- If the key is already present, the existing string stays. The new string is not compared with it, so a collision keeps the first string.
- The string must be valid UTF-8 with no control bytes other than tab, line feed and carriage return. Otherwise the engine traps.
- The string is copied unless it lies in a shared string pool.

Sources of strings:
- Field setters of the structured-data loader. Some field kinds hash a string and also insert it, other kinds only hash it.
- A loader that inserts a list of strings into one 32-bit namespace.
- No path from RPF9 archives into the dictionaries was found.

State at initialization: insertion is disabled for all 64-bit namespaces and enabled for two 32-bit namespaces. No direct code that enables insertion for a 64-bit namespace was found. Indirect writers were not excluded. Whether the 64-bit dictionaries receive strings at runtime is therefore open.

RPF9 uses the dictionaries only for reverse lookup and for its substring path lookup, see [names.md](../formats/containers/rpf9/names.md#runtime-dictionary).

## File objects and devices

An RPF9 archive is opened through two objects (RPF9-F07):

- A 0x60-byte file object. It finds a device for the path and opens a handle through it, then queries size and modification time through two device methods. It can also take these values from a caller-supplied block in memory.
- A 0x80-byte archive object that holds the file object, the metadata buffers and the metadata view.

All archive reads go through a device read method with an explicit offset. The physical device implementations behind that method were not traced, so whether such a device transforms data is unknown.

Path resolution (RPF9-F62):
- Without a caller-supplied block, the file object tries each configured search root in turn. A path starting with `$` skips its first two characters. Each candidate is normalized. The first candidate whose device reports that the file exists wins.
- With a caller-supplied block, the path is copied unchanged, up to 255 bytes.
- The result is stored in the file object. The archive derives its default [mount prefix](../formats/containers/rpf9/names.md#mount-prefix) from it.

The normalizers were not analyzed. The exact form of the stored path is therefore not established.

Open through the device (RPF9-F65, RPF9-F70):
- The device's open method returns a handle and writes the base offset of the file inside the device into file object `+0x20`.
- Size and time normally come from two device methods.
- If the device is an archive, the size instead comes from that archive: it resolves the path to a row and returns the row's logical size. This is how [nested archives](../formats/containers/rpf9/names.md#nested-archives) are opened.

Registration: after a successful device open, the file object is registered in a global table of file objects. Its slot index becomes the 16-bit tag that forms the high half of RPF9 entry IDs ([entries.md](../formats/containers/rpf9/entries.md#tag-allocation), RPF9-F64).

Destruction (RPF9-F72): the file object releases its registry slot, which makes the tag available again, and asks its device to release its handles. It holds no reference on its device.

The file object also holds the flag that enables sorted row lookup ([names.md](../formats/containers/rpf9/names.md#sorted-flag)).

## Device selection

A path is mapped to a device in this order (RPF9-F68):

1. A scheme before `:` that is one of three hashed names selects a fixed device.
2. `tcpip:`, paths containing `globalroot`, and the drive prefixes `t:`, `g:` and `R:` (including the `\??\T:`-style variants) select fixed devices.
3. Every other path goes to the [mount table](#mount-table).

The fixed devices were not analyzed.

## Mount table

A global table maps path prefixes to devices (RPF9-F68).

Mounting:
- A prefix MUST be non-empty, end in `/` or `\` and be at most 253 bytes long. Otherwise the mount fails.
- The prefix `default` instead sets the fallback device, if none is set yet.
- Mounting a prefix that is already present, compared without regard to ASCII case and with `\` equal to `/`, appends the device to that prefix. Several devices can therefore share a prefix.
- Each prefix carries a flag. The archive mount method sets it. Lookups that pass mode 0 skip prefixes with the flag set. That the flag marks read-only mounts is Probable.

Lookup:
1. Choose the longest mounted prefix that matches the start of the path, with the same case and separator folding.
2. With one device, return it.
3. With several, ask them from the most recently mounted to the oldest whether the path exists, and return the first that has it. If none has it, return none.
4. With no matching prefix, use the fallback device.

The mount table does not own devices. Unmounting and clearing the table release only the table's own storage. Whoever mounts an archive keeps the file object and the archive object alive.

## Archives as devices

An RPF9 archive object implements the device interface itself (RPF9-F67):
- It reports that it is an archive-backed device, and its "parent archive" method returns the archive object.
- Its existence test resolves the path with the [row resolver](../formats/containers/rpf9/names.md#path-to-row).
- Its open method resolves the path to a row, returns its own file object's physical handle, and reports the row's payload offset as the opened file's base (RPF9-F70).
- Its read method is a positional read that adds its own base offset, clamps to its own size and calls its own device (RPF9-F71, see [payloads.md](../formats/containers/rpf9/payloads.md#nested-reads)).
- Its handle release does nothing.

The archive's mount method adds it to the mount table under a caller-supplied prefix and replaces the archive's [resolver prefix](../formats/containers/rpf9/names.md#mount-prefix) with that prefix (RPF9-F61, RPF9-F69).

Lifetime (RPF9-F72):
- A nested archive's file object stores the parent archive as its device and the parent's physical handle as its own handle. It takes no reference on either.
- Destroying the nested archive calls the parent's handle release, which does nothing, so the shared physical handle stays open.
- The parent MUST outlive every archive and stream opened through it. No mechanism that invalidates children when a parent goes away was found.

Object layouts and vtable slots are in the [build catalog](../builds/gta-vi/scarlett-e95020b2/functions.md).
