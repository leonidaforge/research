# RPF9 native type registry

The engine maps a table-of-contents type id to a file extension. The mapping is not derived from the payload: it is a static table in the executable, and it is the same table the loader uses to build a file name when it looks an entry up by path.

Recovered from build `e95020b2` of the retail executable, SHA-256 `e95020b2fa4a721db3df59fdecf75621730ac559d8835252f6c3b658d5a08993`, image base `0x140000000`.

## The accessor

`0x4EBBC30(type_id, variant)` returns a `const char *` or nothing:

| Condition              | Result                                                       |
| ---------------------- | ------------------------------------------------------------ |
| `type_id == 0xFF`      | nothing                                                      |
| `variant == 0xFFFF`    | nothing                                                      |
| `type_id < 19`         | `*(u64 *)(0x62FCD30 + variant * 0x98 + type_id * 8)`         |
| `type_id` in 64 to 115 | `*(u64 *)(0x618D9E0 + variant * 0x1A0 + (type_id - 64) * 8)` |
| anything else          | nothing                                                      |

`0x98` is 19 pointers and `0x1A0` is 52 pointers, so each variant row is a contiguous array of string pointers indexed by the type id. The second range is reached through a provider registered at `0x4EBBCF0`; it is the only provider in the engine's provider array, whose count and base are at `0x78F68C4` and `0x78F68C8`.

When the accessor returns nothing, the callers substitute the string `???`, which is at RVA `0x678832B`.

## The reverse lookup

`0x56EE50(extension)` compares the input, case-sensitively and in id order, against the **path** variant of the first table: `rpf`, `zmf`, `zdr`, … `zvert`. A match answers the id; no match answers `0xFFFF`. The second table is not searched, so a `64..115` extension has no reverse mapping.

The name resolver at `0x28CD5B0` calls the accessor with variant 0 while it builds the `name.extension` candidate for an entry, which is why the path variant is the one that names real files.

## The three variants

Every id in both ranges has three extensions. They differ only in a prefix; `rpf`, `mrf`, `cut`, `gfx`, `rdb` and `iasf` are stored once and are the same in every variant.

Type ids 0 to 18, path variant:

| Id  | Extension | Id  | Extension |
| --- | --------- | --- | --------- |
| 0   | `rpf`     | 10  | `zsd`     |
| 1   | `zmf`     | 11  | `zmt`     |
| 2   | `zdr`     | 12  | `zsc`     |
| 3   | `zft`     | 13  | `zcs`     |
| 4   | `zdd`     | 14  | `zdatb`   |
| 5   | `ztd`     | 15  | `zbdr`    |
| 6   | `zbn`     | 16  | `zbdd`    |
| 7   | `zbd`     | 17  | `zbft`    |
| 8   | `zpd`     | 18  | `zvert`   |
| 9   | `zbs`     |     |           |

Type ids 64 to 115, path variant:

| Id  | Extension | Id  | Extension | Id  | Extension  | Id  | Extension |
| --- | --------- | --- | --------- | --- | ---------- | --- | --------- |
| 64  | `mrf`     | 77  | `zjd`     | 90  | `zascript` | 103 | `zfid`    |
| 65  | `cut`     | 78  | `zad`     | 91  | `zsma`     | 104 | `zmsk`    |
| 66  | `gfx`     | 79  | `znv`     | 92  | `iasf`     | 105 | `zhdat`   |
| 67  | `zcd`     | 80  | `znvs`    | 93  | `zfc`      | 106 | `znmd`    |
| 68  | `zld`     | 81  | `zpl`     | 94  | `zlfc`     | 107 | `zsmm`    |
| 69  | `zpmd`    | 82  | `znd`     | 95  | `zcg`      | 108 | `zascd`   |
| 70  | `zpm`     | 83  | `zvr`     | 96  | `zasd`     | 109 | `zrd`     |
| 71  | `zed`     | 84  | `zwr`     | 97  | `rdb`      | 110 | `zsmam`   |
| 72  | `zpt`     | 85  | `znh`     | 98  | `zfbs`     | 111 | `zldbmt`  |
| 73  | `zmap`    | 86  | `zfd`     | 99  | `zcps`     | 112 | `znmd`    |
| 74  | `ztyp`    | 87  | `zas`     | 100 | `zsp`      | 113 | `zkit`    |
| 75  | `zch`     | 88  | `zsm`     | 101 | `ztsl`     | 114 | `zcgc`    |
| 76  | `zldb`    | 89  | `zscript` | 102 | `zmmd`     | 115 | `zcov`    |

The alternate variant is the same list with the `z` replaced by `i` (`imf`, `idr`, … `icov`); the hash variant replaces it with `#` (`#mf`, `#dr`, … `#cov`). Ids 92 and 97 and the five unprefixed entries keep their single spelling in every variant.

## What the registry does and does not say

A registered extension names the **asset class the engine assigns to the type**. It says nothing about the payload's format, and a payload of a different format does not invalidate it:

- type 0 is `rpf` and holds archives;
- type 11 is `zmt` and its rows hold `PSIN` and `RBF0` payloads, which is what a meta container and a meta document are;
- type 66 is `gfx` and its rows are GFx payloads;
- types 2, 3, 5, 6 and 79 are `zdr`, `zft`, `ztd`, `zbn` and `znv`, and their rows are resource containers.

The last two are independent confirmations: the registry and the payload evidence agree on ids 66 and 11 without either being derived from the other.

Every id outside the two ranges is unregistered. `0xFF` is unregistered by construction. Unregistered ids are not "unknown types": the engine has no extension for them and prints `???`.

## Limits

- The three variants are recorded as facts about the build. What selects a variant at a call site other than the name resolver was not traced; one caller passes it as a stack argument.
- The registry is a table of extensions, not of formats. It cannot tell a `zsm` asset's layout.
- Types 19 to 63 and 116 to 255 have no extension in this build. Whether another build registers them is untested.
- The provider array holds one entry in this build. A build that registers more providers would need the same reading again.
