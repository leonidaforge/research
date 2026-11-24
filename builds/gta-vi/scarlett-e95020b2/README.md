# GTA VI, Xbox Series executable e95020b2

The main game executable of the GTA VI Xbox Series ("Scarlett") build. All RVAs in this repository refer to this build unless stated otherwise.

## Identity

| Property | Value |
|---|---|
| SHA-256 | `e95020b2fa4a721db3df59fdecf75621730ac559d8835252f6c3b658d5a08993` |
| Size | 120,181,760 bytes |
| Format | PE32+ |
| Machine | x86-64 (`0x8664`) |
| Image base | `0x140000000` |
| Entry point RVA | `0x56A1EC8` |
| COFF timestamp | `1794606036` (2026-11-13 21:40:36 UTC) |

## Sections

| Name | RVA | Virtual size | Raw size |
|---|---|---|---|
| `.text` | `0x1000` | `0x5F3F966` | `0x5F3FA00` |
| `.rdata` | `0x5F41000` | `0x8A0C0C` | `0x8A0E00` |
| `.data` | `0x67E2000` | `0x43EC398` | `0x622E00` |
| `.pdata` | `0xABCF000` | `0x36CBAC` | `0x36CC00` |
| `.retplne` | `0xAF3C000` | `0xE4` | `0x200` |
| `.tls` | `0xAF3D000` | `0x1481` | `0x1600` |
| `.voltbl` | `0xAF3F000` | `0x724` | `0x800` |
| `.xbld` | `0xAF40000` | `0x6B9` | `0x800` |
| `.reloc` | `0xAF41000` | `0x12A350` | `0x12A400` |
| `.xbld` | `0xB06C000` | `0xDC` | `0x200` |

The executable carries no meaningful symbol names. Function names in this repository are descriptive labels.

## Content

- [functions.md](functions.md): function roles, vtable slots and object layouts for RPF9.
- Evidence and confidence per finding: [evidence/rpf9/INDEX.md](../../../evidence/rpf9/INDEX.md).

## Limitations

- Indirect calls are resolved only where a vtable slot was read directly.
- Device read and open implementations are not traced.
- The key lookup is analyzed at the architecture level. The local archive sample binds to this build's registry: step 1 decrypts all 22 tested archives and their metadata signatures verify (RPF9-F100, RPF9-F102). A second build is untested. The payload transform and metadata cipher algorithms 1, 2, `0x11` and `0x12` are not analyzed. Algorithms 0 and `0x10` are.
- The codec's inner decode call and the chunk decompression service are not analyzed.
