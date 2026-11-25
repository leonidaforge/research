# Public name LUTs

These files map verified RPF9 name hashes to candidate filenames. They are
Leonida Forge LUT v1 files.

## Format

```text
# leonida-forge-lut: 1
# namespace: hash64

0x0123456789ABCDEF<TAB>relative/path/file.ext
```

- UTF-8 text, one record per line.
- Both declarations are required before the first record.
- `HASH<TAB>NAME`; the name keeps its internal spaces.
- Blank lines and lines whose first non-space byte is `#` are ignored.
- `hash64` hashes are exactly 16 hexadecimal digits after `0x`.
- `key32` hashes are exactly 8 hexadecimal digits after `0x`.
- Output is sorted by hash and then name; hashes are uppercase.
- Exact duplicate records are dropped. Different names for one hash are kept.
- Malformed records, control characters, bidi overrides and records outside
  the declared namespace are rejected.
- A reader SHOULD enforce a file-size limit, a line-length limit and an entry
  count limit. Leonida Forge uses 16 MiB, 4096 bytes and 2^20 entries.

`hash64` is the engine's 64-bit name hash: MurmurHash3 x64-128 with seed 0,
first word, over the normalized stem, with only the low byte of the length
mixed in. `key32` is Jenkins one-at-a-time over the normalized string, with the
engine's leading-quote rule. Normalization maps ASCII `A`–`Z` to lower case
and `\` to `/`; nothing else changes. See
[formats/containers/rpf9/names.md](../formats/containers/rpf9/names.md).

## Namespaces

The two files are separate namespaces:

| File              | Namespace | Width     | Field            |
| ----------------- | --------- | --------- | ---------------- |
| `rpf9-hash64.lut` | `hash64`  | 16 digits | 64-bit name hash |
| `rpf9-key32.lut`  | `key32`   | 8 digits  | 32-bit name key  |

A 32-bit value is never reinterpreted as a 64-bit hash or the reverse.

## Validation

Every record was checked by hashing the name, or the stem before its last `.`,
with the declared algorithm and comparing it to the declared hash. A matching
hash proves only that the text is a mathematical preimage. It does not prove
that the game developer chose that text as the original filename.

## Provenance

The current files contain hash-validated candidates from two local sources:

- text extracted from readable, authenticated native RPF9 payloads;
- text extracted from the initialized sections of a user-provided executable.

A candidate was accepted only when the extension and row type were consistent
with the public type/extension knowledge. For `hash64` the only established
extension mapping is `rpf` to type 0, so these records are relative `.rpf`
paths. For `key32` the established types are 255, the engine's no-type class,
and types 11 and 14 from the executable's per-type class tables. Types 11 and
14 have no confirmed extension, so their candidates are path stems without an
invented extension. Payloads behind the unsupported payload transform were
skipped and are not sources. Raw payload text, executable bytes, archive bytes
and local paths are not published.

The records are candidate mappings, not independently established original
developer filenames. A hash match can be coincidental, particularly in the
32-bit namespace. Ambiguous hashes remain ambiguous: the LUT may contain
several names for one hash.

## Current coverage

The published files hold 2250 `hash64` records and 233 `key32` records. Of the
`key32` keys, 106 address type 255 rows and 127 address type 11 rows; 211 keys
over 228 payload-matched rows came from payload text and 22 keys over 31 rows
from the executable, with no key from both sources. Applied to the 22
authenticated local archives, the pair\nresolves 2525 of 6534 rows with no ambiguous row under the strict type matching\ndescribed above: 2266 type-0 rows, 125 type-255 rows and 134 type-11 rows. The\nremaining 4009 rows have no published candidate. A re-hash audit found no\nunverified record, no key with more than one normalized name, no duplicate\nspelling and no path-unsafe name. These counts are observations from one build\nand one local sample, not limits of the format; the harvest run was truncated\nby its explicit byte, string and match limits.

## Contributing

Only mapping data is accepted here, not payload text or executable extracts.
A contribution MUST state:

- the namespace and the exact hash;
- the candidate filename as written;
- how the candidate was obtained, without private paths or secret material;
- whether the hash was recomputed from the name;
- any known collision or ambiguity.

A maintainer MUST validate every record with the published algorithms before
merging it. A mapping whose provenance raises a licensing or publication
concern stays out of this repository and is reported instead.

## License

The files and this document are original Leonida Forge contributions under
GPL-3.0-or-later. They grant no rights to Rockstar Games or Take-Two
Interactive material. See [RESEARCH-POLICY.md](../RESEARCH-POLICY.md) and
[LICENSE.md](../LICENSE.md).
