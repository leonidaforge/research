# RPF9 functions in build e95020b2

RVAs for image base `0x140000000`. Roles are descriptive labels, not recovered symbol names. Finding IDs refer to the [evidence index](../../../evidence/rpf9/INDEX.md).

## Archive open

| RVA | Role | Confidence | Finding |
|---|---|---|---|
| `0xFC21C0` | File object factory: allocates 0x60 bytes, constructs, frees on failure. Optional magic check on a caller-supplied block (compare at `0xFC21D9`) | Confirmed | F01, F07 |
| `0xFC2240` | File object constructor. Resolves the device, opens the handle, reads size and time | Confirmed | F07 |
| `0xFC2490` | Allocates the 0x80-byte archive object | Confirmed | F07 |
| `0xFC2540` | Archive object constructor: header read, view descriptor, validation, view layout | Confirmed | F07 |
| `0x1FB2600` | Header and metadata reader. Magic compares at `0x1FB2619` (preloaded header) and `0x1FB2692` (disk) | Confirmed | F01, F02 |
| `0x28CDFC0` | Mode-0 metadata read helper, archive vtable `+0x398` | Confirmed | F02 |
| `0x1FB2780` | Builds the metadata view descriptor | Confirmed | F07 |
| `0x87AEC0` | Writes region pointers into the metadata view | Confirmed | F07 |
| `0x87AF70`, `0x87AFF0` | Read prefix counts, compute primary region offsets with alignment | Confirmed | F04, F05 |
| `0x87B0B0`, `0x87B0F0` | Compute secondary region offsets | Confirmed | F06 |

Callers of `0xFC21C0`: `0xFC20D0`, `0x1D4C980`, `0x1DEE6C0`, `0x22372C0`, `0x2758210`. A second path at `0xFA87F9`/`0xFA8805` runs the same layout and validation. It was not traced.

## Validation and cryptography

| RVA | Role | Confidence | Finding |
|---|---|---|---|
| `0x8EC200` | Validation chain entry. Every step must succeed | Confirmed | F23 |
| `0xA348A0` | Step 1: reads selector `0x2E`, picks descriptor and span set, processes `A` and `B` spans | Confirmed | F24, F26 |
| `0xA349A0` | Builds the two static cipher descriptors | Confirmed | F24 |
| `0x28CE530` | Conditional step 2. Role unknown | Unknown | |
| `0x1FB2300` | Step 3. Role unknown | Unknown | |
| `0x6BD040` | Step 4. Role unknown | Unknown | |
| `0x8EC360` | Step 5: processes the secondary area | Confirmed | F26 |
| `0x6BD160` | Span runner: init from descriptor, in-place `update` per span, boolean `final` | Confirmed | F27 |
| `0x536A70` | Cipher type to algorithm ID, 19-entry table | Confirmed | F25 |
| `0x613880` | Creates the algorithm object and resolves the key by identifier. Internals not analyzed | Confirmed (role) | F25 |
| `0x193F90` | Key lookup by identifier, called from `0x613880`. Not analyzed | Confirmed (call) | F25 |

## Schema access

| RVA | Role | Confidence | Finding |
|---|---|---|---|
| `0x28CE0A0` | Field value getter thunk: archive object `+0x28`, entry ID truncated to 16 bits | Confirmed | F14 |
| `0x28CE0B0` | Field pointer getter thunk, same adjustments | Confirmed | F14 |
| `0x28CE1B0` | Value accessor: present or absent | Confirmed | F14 |
| `0x38300` | Pointer accessor: returns the value pointer | Confirmed | F14 |
| `0x28CD240` | Field key to column index, `0xFFFF` if absent | Confirmed | F08 |
| `0x4DB65B0` | Selects index store and stride, rebases secondary columns | Confirmed | F10 |
| `0x4DB6600` | Reads one compact index of `F` bytes, sentinel handling | Confirmed | F11 |
| `0x55B2600` | Builds the value pointer from pool, column base offset and element width | Confirmed | F12 |
| `0x5305880` | Row resolver, returns `0xFFFF` when not found | Probable | F15 |
| `0x5305EC0` | Returns the `u16` at file object `+0x0C`, the entry ID high half. Reached only through the vtable | Confirmed | F15 |

## Entries, names, payloads

| RVA | Role | Confidence | Finding |
|---|---|---|---|
| `0x1331670` | Entry size helper: resource and non-resource size columns | Confirmed | F16 |
| `0x28CD5B0` | Open by path: linear row scan with name rebuild and substring match | Confirmed | F20 |
| `0x4DAC8F0` | Builds the 0x118-byte entry descriptor after a path match | Confirmed (call) | F20 |
| `0x553D070` | Hashed-string dictionary lookup by namespace and hash | Confirmed | F18 |
| `0x4EBBC30` | Extension string from type ID. Default string at `0x678832B` | Confirmed | F19 |
| `0x28CDA50` | Child enumeration into 0x20-byte descriptors | Confirmed | F21 |
| `0x28C6B20` | Batch open, read and collect over an ID array | Confirmed | F21 |
| `0x28CD3B0` | Stream read with seek modes, size clamp, 4 KiB blocks | Confirmed | F22 |
| `0x314330` | Low-level block read used by the stream reader | Confirmed (call) | F22 |

## Archive vtable

Archive object vtable at RVA `0x62FD480`.

| Slot | RVA | Role | Confidence |
|---|---|---|---|
| `+0x28` | `0x28CD2E0` | Open entry by key, returns a handle or -1 | Probable |
| `+0x30` | `0x2758940` | Open entry, variant with an extra argument | Probable |
| `+0x60` | `0x28CD360` | Read or seek on a handle | Probable |
| `+0x80` | `0x28CD3B0` | Stream read | Confirmed |
| `+0x90` | `0x503F490` | Release handle | Probable |
| `+0x108` | `0x28CD580` | Fetch an entry field or size by ID | Probable |
| `+0x120` | `0x28CD5B0` | Open by path | Confirmed |
| `+0x1A0` | `0x28CDA50` | Child enumeration | Confirmed |
| `+0x1B0` | `0x28C6B20` | Batch open | Confirmed |
| `+0x398` | `0x28CDFC0` | Mode-0 metadata read | Confirmed |
| `+0x3D0` | `0x5305EC0` | Entry ID high half | Confirmed |
| `+0x3F0` | `0x28CE0A0` | Field value getter | Confirmed |
| `+0x3F8` | `0x28CE0B0` | Field pointer getter | Confirmed |

File object vtable at RVA `0x62FD890`.

## Object layouts

Archive object, 0x80 bytes:

| Offset | Content | Confidence |
|---|---|---|
| `+0x00` | Vtable | Confirmed |
| `+0x08` | File object pointer. Cleared when the open fails | Confirmed |
| `+0x18` | Primary metadata buffer | Confirmed |
| `+0x20` | Secondary metadata buffer | Confirmed |
| `+0x28` | Metadata view, see below | Confirmed |
| `+0x7C` | Flags byte | Confirmed (presence) |

Metadata view at archive object `+0x28`:

| Offset | Content |
|---|---|
| `+0x00` | State word, set to 2 by the constructor |
| `+0x08` | Header and prefix |
| `+0x10` | `A` table |
| `+0x18` | `B` block |
| `+0x20` | Column descriptors |
| `+0x28` | Primary index store |
| `+0x30` | Primary value pool |
| `+0x38` | Secondary index store |
| `+0x40` | Secondary value pool |

File object, 0x60 bytes:

| Offset | Content | Confidence |
|---|---|---|
| `+0x0C` | `u16` tag, high half of entry IDs | Confirmed |
| `+0x10` | Device | Probable |
| `+0x18` | Handle, -1 when the open failed. The decompiler shows it passed as the device argument | Probable |
| `+0x20` | Archive base offset | Probable |

The device interface reads through vtable slot `+0x60` and reports size and time through `+0xF8` and `+0x108`.
