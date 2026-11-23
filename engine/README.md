# Engine

Runtime mechanisms that more than one format uses. Everything here was observed in one executable, [scarlett-e95020b2](../builds/gta-vi/scarlett-e95020b2/README.md), and has so far only been followed through the RPF9 code paths. Other RAGE versions or other parts of GTA VI may behave differently.

## Hashed-string dictionary

The engine maps `(namespace, u64 hash)` to a string through a runtime dictionary (RPF9-F18).

- There is a per-thread dictionary and a global one. The namespace selects which table is probed.
- The probe compares 16 control bytes at once in groups of 0x110 bytes, which is the layout of SwissTable-style hash maps.
- A miss returns null.

Strings enter the dictionary at runtime. The executable alone therefore does not give the string for a hash. How strings are registered and which hash function produces the keys are unknown.

RPF9 file names use this dictionary, see [names.md](../formats/containers/rpf9/names.md).

## File objects and devices

An RPF9 archive is opened through two objects (RPF9-F07):

- A 0x60-byte file object. It finds a device for the path and opens a handle through it, then queries size and modification time through two device methods. It can also take these values from a caller-supplied block in memory.
- A 0x80-byte archive object that holds the file object, the metadata buffers and the metadata view.

All archive reads go through a device read method with an explicit offset. The device implementations behind that method were not traced, so whether a device transforms data is unknown.

The file object also stores the 16-bit tag that forms the high half of RPF9 entry IDs ([entries.md](../formats/containers/rpf9/entries.md#entry-ids)).

Object layouts and vtable slots are in the [build catalog](../builds/gta-vi/scarlett-e95020b2/functions.md).
