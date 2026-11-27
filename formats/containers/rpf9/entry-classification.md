# RPF9 entry classification

An RPF9 row does not say what it holds. The table of contents gives a numeric type, a storage shape and a name hash; nothing in it is a file format. Anything that shows, extracts or exports an entry has to decide three separate things:

1. **What the entry type is.** A number stored in the location record, 0 to 255.
2. **What the payload is.** A format, a resource container, a text document, or nothing recognisable.
3. **What the application can do with it.** Open it as an archive, parse it structurally, show it as text, read a resource, or only show its bytes.

Treating these as one property is the mistake this document exists to prevent. Type 255 holds payloads of every kind. Type 0 is registered as `rpf` and holds archives, but a type-0 row is an archive only when its payload is one: a synthetic fixture whose type-0 row holds a `PSIN` payload is classified as structural, and the census keeps such a row apart from the archives it also counts. A type 5 row is a candidate for the texture viewer because the recovered [type registry](type-registry.md) calls the type `ztd`; that is a declaration about the loader's naming, not evidence about the bytes.

## Where the evidence comes from

A classification reads bounded evidence and records which part of it decided:

| Evidence  | Read                                                           | Cost                                |
| --------- | -------------------------------------------------------------- | ----------------------------------- |
| Type      | The location record's type byte                                | Metadata only                       |
| Storage   | The location record's mode and the chunk table                 | Metadata only                       |
| Payload   | The decoded payload's first 64 bytes                           | One decoded chunk in the worst case |
| Document  | A decoded document up to 4 MiB, when the head looks XML        | One document                        |
| Structure | Nothing extra: recognisers that walk framing do it on the head | Included in the head read           |
| Extension | The engine's [type registry](type-registry.md)                 | Metadata only                       |

The classification reads at most 64 decoded bytes. The matrix publishes the first 32 of them with every combination, which is a sample of the head, not the whole head.

The classification never reads a payload in full, never guesses an extension it cannot establish, and never lets the type decide the format.

## Confidence

A classification makes separate claims, each with its own level. A verified signature is not a verified format, and a verified container shape is not a verified asset class.

| Claim       | Established by                                                                               |
| ----------- | -------------------------------------------------------------------------------------------- |
| `signature` | The bytes matched a signature, or the first bytes look like XML. Nothing about structure.    |
| `structure` | The recogniser walked the payload's own framing from the head, or the whole document parsed. |
| `asset`     | The payload itself was read closely enough to say what asset class it belongs to.            |

| Level       | Meaning                                                                      |
| ----------- | ---------------------------------------------------------------------------- |
| `verified`  | Repeated tests of real data and structural evidence agree                    |
| `probable`  | Several observations agree, but the evidence that would settle it is missing |
| `tentative` | A plausible hypothesis that independent checks do not confirm                |
| `unknown`   | The available evidence establishes nothing useful                            |

A recogniser that walks framing from the head claims `verified` structure. The RPF9 recogniser matches the magic only, so its structure is `probable` until a caller opens the archive. A resource header is a verified signature with `unknown` structure: the page map it points at is not read. A named signature such as `MHIU` is a verified signature with unknown structure, format and asset class.

The asset claim stays `unknown` for every entry today. The one thing that could settle it is a registry entry, and a registry entry is a property of the type, not of the payload: it says which class the loader assigns to the type id, not what these bytes are. The census therefore reports the registry value as a **declared** asset class (`declared_asset_classes`) and keeps it out of the claims. A type whose registry entry says `zsm` holding a `PSIN` payload is a declared `zsm` with a verified `PSIN` signature, and the disagreement is visible instead of being averaged away.

Reading the first 64 decoded bytes never establishes the whole entry. Every claim is about the head, except a validated document, which is about the whole document.

## Storage

Storage says how the bytes are stored, not what they are. The label is stable and is recorded in every census row:

| Label           | Condition                                         |
| --------------- | ------------------------------------------------- |
| `stored`        | No chunk table, mode 0: the bytes lie as they are |
| `raw-deflate`   | No chunk table, mode 1: one raw DEFLATE stream    |
| `chunked-2`     | A chunk table with encoding 2                     |
| `chunked-3`     | A chunk table with encoding 3                     |
| `chunked-4`     | A chunk table with encoding 4                     |
| `chunked-other` | A chunk table with any other encoding             |

The payload transform is recorded separately, because it is a property of the stored bytes rather than of the chunks. A chunk table's per-chunk method decides decoding; the location record's mode does not apply to a chunked entry.

One practical consequence, used by the census: when every chunk of an entry copies its bytes, has no padding and is exactly as long as it is stored, the decoded payload is the stored range itself, so a nested archive can be read where it lies. Otherwise the payload has to be decoded before it can be read as an archive.

## Payload state

| State                   | Meaning                                                           |
| ----------------------- | ----------------------------------------------------------------- |
| `decoded`               | The decoded head was read                                         |
| `not-read`              | No payload was read, as in a metadata pass                        |
| `transform-unavailable` | The payload is behind the transform and no key state is available |
| `transform-failed`      | The transform was available but did not verify or run             |
| `undecodable`           | The storage cannot be decoded                                     |
| `malformed`             | The metadata describing the payload is malformed                  |

Only `decoded` entries are identified. A state that is not `decoded` is a fact about the archive, not a guess about the payload: the entry is reported as unidentified with the reason, never as an unknown format.

### Listing state

`archive ls` reports `contents.state` without decoding a payload:

| State                    | Established                                                        |
| ------------------------ | ------------------------------------------------------------------ |
| `stored`                 | The stored bytes are the contents                                  |
| `validated`              | The chunk table and its sizes fit the entry; no chunk was decoded  |
| `transform_key_missing`  | The payload is transformed and no key state is available           |
| `transform_available`    | The payload is transformed and a key state is available            |
| `unsupported_transform`  | The transform's algorithm or descriptor is not supported           |
| `unsupported_compression`| The storage cannot be decoded                                      |
| `alternate_source`       | The entry reads through a companion that was not opened            |
| `malformed`              | The metadata describing the payload is malformed                   |

`validated` replaced the earlier `decoded`, which promised a decode the listing
never performed: a row with a corrupt zlib stream was reported as `decoded`
while extraction failed. `decoded` now means a read returned the payload, which
`archive verify` and extraction establish (RPF9-F153).

## Terminal outcome

Every entry ends an investigation with exactly one outcome, and the census counts them so the counts add up to the entry count. This is what makes an inventory exhaustive rather than a pile of categories: a row cannot be counted twice and cannot be left out.

| Outcome                 | Established                                                       |
| ----------------------- | ----------------------------------------------------------------- |
| `identified`            | The payload's own framing was walked and the container named      |
| `partially-identified`  | Something about the payload, but not the container                |
| `unresolved`            | The payload was read and nothing in it was recognised             |
| `undecodable`           | The storage cannot be decoded                                     |
| `transform-unavailable` | The payload is behind the transform and no key state is available |
| `malformed`             | The metadata describing the payload is malformed                  |
| `not-probed`            | No payload was read, so nothing about the bytes is established    |
| `blocked`               | The payload was reached and could not be read                     |

`partially-identified` covers the three shapes that stop short of a container: a magic-only match such as `RPF9`, a resource header whose page map was not read, and a payload that looks like XML without parsing as XML. A metadata pass reports every entry as `not-probed`: it never claims that a payload was blocked. `blocked` is reserved for a payload that was reached and could not be read, which in this installation means a transform that did not verify.

## Identification

| Kind           | What it records                                      |
| -------------- | ---------------------------------------------------- |
| `format`       | A supported format and its recogniser's claim        |
| `resource`     | Eight zero bytes then a `0x5…` or `0x6…` pointer     |
| `xml`          | A document, with its root element when it parsed     |
| `signature`    | A named signature whose format is not established    |
| `unrecognised` | Nothing in the first 64 bytes identifies the payload |

### The resource header

Every resource-shaped payload read so far starts with the same two 64-bit words:

| Offset  | Width | Value                                                                      |
| ------- | ----- | -------------------------------------------------------------------------- |
| `+0x00` | 8     | Zero                                                                       |
| `+0x08` | 8     | A pointer: the segment nibble in bits 28 to 31, the offset in bits 0 to 27 |

The segment nibble is 5 (system) or 6 (graphics). A pointer outside those two segments, a non-zero first word, or a pointer that does not fit in 32 bits is not treated as a resource header, which keeps the match narrow. Observed heads include `0000000000000000 7091e25000000000` (pointer `0x50E29170`, segment 5, offset `0x0E29170`) and `0000000000000000 10fa005000000000` (pointer `0x5000FA10`, segment 5, offset `0x00FA10`).

The header establishes the container and the segment. It does not establish which resource is inside: the page map and the resource's own descriptor are not read by the classification. A resource entry therefore gets whatever extension its type declares, and no extension of its own: the container is identified, the resource is not.

### Signatures without a format

Four signatures are named without claiming a format, because the bytes are distinctive and nothing more is known: `MoVE`, `SGD5`, `MHIU` and `SPS1`. `DDS ` and the PNG signature are named as images. Naming them separates "we know these bytes start a known container" from "we do not know what this is", which matters for the backlog: the first group has a target, the second does not.

## Extension

An extension is applied only when something establishes it. The precedence is fixed, and the provenance is kept:

1. The archive's own resolved name, kept exactly as found, including case and a leading dot.
2. The engine's native extension for the type id, from the [type registry](type-registry.md).
3. A payload-derived extension: `xml` when the whole document parsed.
4. Nothing, with a reason.

A native extension and a payload-derived extension are different properties. The engine's extension names the asset class the loader assigns to the type; the payload-derived extension names the container the bytes actually are. When the two disagree — a type whose registry extension is `zmt` holding a validated XML document — the native extension is applied, because that is the name the game would use, and the disagreement is reported in `conflict` instead of being silently dropped.

The only payload-derived extension this model applies is `xml`. A recognised format such as `PSIN` has no established extension and stays unresolved with that reason; the type's native extension is what a caller sees.

Where a resource header appears under a type the registry does not cover, the reason is "a resource container with no registered engine type".

Because the registry covers every type the census reached except 255, almost every entry now has an extension without reading any payload, and no caller needs a fallback: `extension` is present or absent, `extension_provenance` says where it came from (`original`, `native`, `payload`, `unresolved`), and `extension_verified` says whether it may be applied automatically. A `native` extension is applied without being verified against the payload; the provenance is what keeps that visible.

Two surfaces name an entry, and one function decides the name for both. `lforge_core::registry::file_name` keeps a name that already carries an extension, appends the declared one when it does not, and appends nothing when the type declares none; the Explorer shows that name and marks a synthesized extension as synthesized, and the command line resolves a name the same way. The command line publishes one extra fact the Explorer does not need: `extension_source` is `archive` when the archive's own type table declares the extension and `declared` when only the engine registry does. On every archive of this installation the two agree; an archive built by another build could disagree, and then the command line keeps the archive's spelling while the Explorer keeps the build's, which is why the provenance is published instead of assumed.

The Explorer names an entry from the table of contents alone, so it shows no payload-derived extension. The census reads payloads, so the 489 validated documents carry `xml` with provenance `payload`. That difference is the point of keeping the four provenances apart: a name on screen is not a claim about the bytes, and no Explorer row is decoded to give it one.

## Capability

| Capability    | Meaning                                                  |
| ------------- | -------------------------------------------------------- |
| `archive`     | The archive commands open its table of contents          |
| `structural`  | A structural inspection, without field meaning           |
| `text`        | A document shown as text                                 |
| `resource`    | A resource container whose asset class is not identified |
| `bytes`       | Bytes only, through the binary viewer                    |
| `unavailable` | Nothing can be decoded; the reason says why              |

The capability is what the application dispatches on. The type is not: an entry typed 0 whose payload is `PSIN` is `structural`, not `archive`.

## The inventory

The classification is used twice. A **metadata pass** enumerates every entry without reading a payload; a **payload pass** reads the first decoded bytes of every entry. They are separate investigations with separate journals, because a metadata checkpoint must never stand in for a payload one.

| Pass     | Reads                      | Establishes                                                                     |
| -------- | -------------------------- | ------------------------------------------------------------------------------- |
| metadata | the table of contents      | every archive and entry, the type id, the storage shape, the declared extension |
| payload  | the first 64 decoded bytes | what the entry holds, and one terminal outcome per entry                        |

### How the inventory was taken

Every `.rpf` under the installation, found recursively, one census run per root archive:

```sh
lforge archive census <root>.rpf --executable <game executable> --recursive \
    --samples 3 --max-depth 8 --max-archives 4096 --max-entries 2000000 \
    --max-nested-bytes 268435456 --max-spool-bytes 4294967296 --metadata-only
```

The payload pass is the same command without `--metadata-only` and with room for what a payload read costs: `--max-archives 8192`, `--max-nested-bytes 2147483648`, `--max-spool-bytes 68719476736`. Reading payloads opens more nested archives, and larger ones, than reading tables of contents does.

Each root gets a journal of its own: one line per completed archive, written and synced before the run moves on. A line is keyed by a SHA-256 over the schema, the rule set, the registry build, the scan mode, every limit including the entry budget, the scanner's own digest, and the root's size, modification time and 1 MiB head and tail digests. That last part is a fingerprint, not a whole-file hash: a change in the middle of a root that alters neither end is not detected, which is why a reused line is also bound to the size and digest of the summary it came from. A line also names the summary it came from and that file's digest, so a journal is only reused for the scan that wrote it: a different build, a different budget or a different mode re-runs the root instead of crediting rows it never enumerated. A line cut short by an interruption is repaired at the next append, and a root interrupted at archive N resumes at archive N.

A summary is written to a temporary name and only replaces its target once its own write has finished, so a reader never sees a half-written file. A stopped or failed census still publishes what it counted and exits non-zero, and the driver deletes that summary instead of merging it; only a run whose completion checks pass is merged and quoted. Measured: a scan of `audio.rpf` killed after 25 s had journalled four archives, and the rerun with the same identity reproduced the uninterrupted totals exactly.

Both passes use the same root discovery, root naming and limits, and the machine-written documents are produced by `tools/rpf9/entry_matrix.py` from the merged census, so no figure below is copied by hand.

The counts below were produced by one binary and one executable, and both are recorded in every journal line. The scanner that produced this payload pass is SHA-256 `6774edb32f406f92b7afdc4681ec6b928b00c116584f3591b225170004e929cd`. The executable was build `e95020b2`, SHA-256 `e95020b2fa4a721db3df59fdecf75621730ac559d8835252f6c3b658d5a08993`. Earlier payload passes used scanner `d9620f6c…` and then `6560e67c…`; the first reported 14,432 `undecodable` rows, the second 750 `blocked` rows. This pass adds the descriptor-derived transform range, the counter origin at the first chunk byte and a raw-DEFLATE selection path, so every entry decodes. A census with the rebased scanner `5ee002c3…` and another with the final build `63bc772f…` each reproduced every count, outcome and combination. The timing table is from the uncontended pass that preceded this one, because the roots this fix affects were re-run while other work shared the machine. Because the journal is keyed to the whole binary, a rebuilt scanner rejects older journals and re-runs the roots rather than mixing counts.

### What the metadata pass establishes

22 roots discovered and opened, 4,373 archives opened (4,351 of them nested), 1,255,039 entries enumerated, no archive failed to open, no root stopped at a limit: `complete: true`. It finished in 20 minutes 28 seconds, about 1,022 entries and 3.6 archives per second.

| Count                  |     Value |
| ---------------------- | --------: |
| entries enumerated     | 1,255,039 |
| entries probed         |         0 |
| archives opened        |     4,373 |
| nested archives opened |     4,351 |
| failed archives        |         0 |
| declared asset classes | 1,181,971 |
| unresolved formats     | 1,255,039 |

Nothing is read, so the pass claims nothing about any payload: every entry is `unprobed` and its outcome is `not-probed`. What it does establish is exhaustive: which types exist, in which archives, in what storage shape, and with which declared extension. The full per-root, per-type and per-combination record is [type-inventory.md](type-inventory.md) with the same data in [type-inventory.json](type-inventory.json).

| Declared extension | Entries |
| ------------------ | ------: |
| `zbdr`             | 250,434 |
| `zdr`              | 167,897 |
| `zmap`             | 166,072 |
| `zbn`              |  92,199 |
| none               |  73,068 |
| `zcd`              |  62,384 |
| `zft`              |  55,488 |
| `zmt`              |  48,612 |
| `zdd`              |  48,584 |
| `zsm`              |  40,019 |
| `zascd`            |  32,878 |
| `zldbmt`           |  30,511 |

The remaining thirty-three extensions are in the type inventory. The `none` row is type 255 alone: 73,068 entries under the one type the build does not register.

### What the payload pass establishes

The same roots and the same archives, read one entry at a time: the first 64 decoded bytes, never the whole payload. Every figure of this pass is in [entry-matrix.md](entry-matrix.md) with the same data in [entry-matrix.json](entry-matrix.json); the tables below quote it.

It enumerated 1,255,039 entries in 4,373 archives, root by root the same numbers as the metadata pass: two enumerations that never consulted each other agree exactly. No archive failed to open in either pass, and no type-0 row was rejected: all 4,351 rows of that type opened as archives, which is what the type claims and what the payload proves. A row whose declared type says archive and whose payload does not open is counted as a rejected candidate with its reason rather than as a failed archive, so a declared type can never make a run look broken. This installation has none.

| Outcome                |   Entries | Share |
| ---------------------- | --------: | ----: |
| `partially-identified` | 1,158,361 | 92.3% |
| `identified`           |    93,631 |  7.5% |
| `unresolved`           |     3,047 |  0.2% |

Every entry has exactly one outcome, and the three that occur add up to the entry count. Four outcomes of the vocabulary occur nowhere: no entry is `blocked`, none is `undecodable`, none is `malformed`, and none is `transform-unavailable`. The payload transform now decodes every row that carries it, so `blocked` no longer occurs; the encoding-4 rows that the earlier pass reported as `undecodable` are `partially-identified` resource containers (RPF9-F151), and the type-89 rows behind the transform are too (RPF9-F160).

| Identification         |   Entries |
| ---------------------- | --------: |
| resource container     | 1,153,560 |
| supported format       |    97,493 |
| nothing recognised     |     3,047 |
| validated XML document |       491 |
| named signature        |       448 |

`nothing recognised` is 3,047 entries, every one of them read and found unrecognisable.

| Format | Entries |
| ------ | ------: |
| `ADAT` |  71,676 |
| `PSIN` |  19,084 |
| RPF9   |   4,351 |
| `RBF0` |   1,493 |
| `KB2`  |     797 |
| GFx    |      87 |
| `EDUP` |       5 |

The 4,351 RPF9 rows are the whole of the nesting in this installation: the passes opened exactly 4,351 nested archives, every one of them through a type-0 row. Opening an archive is a separate fact from recognising its magic. The 4,351 RPF9 rows are `partially-identified` on the strength of a four-byte match; that all 4,351 then authenticated and were walked is what `archives_opened` records, and it is the stronger claim. No other entry that was _read_ holds an archive.

| Capability  |   Entries |
| ----------- | --------: |
| resource    | 1,153,560 |
| structural  |    93,142 |
| archive     |     4,351 |
| bytes       |     3,495 |
| text        |       491 |

| Extension provenance |   Entries |
| -------------------- | --------: |
| `native`             | 1,181,971 |
| `unresolved`         |    72,579 |
| `payload`            |       489 |

1,181,971 entries carry the extension their type declares and 489 carry one the bytes themselves established: the 491 validated documents, two of which only look like XML and therefore keep no payload extension. 72,579 entries have no extension at all: the 73,068 rows of the unregistered type 255, minus the 489 documents that established `xml` for themselves.

| Structure claim |   Entries |
| --------------- | --------: |
| unknown         | 1,157,055 |
| verified        |    93,631 |
| probable        |     4,351 |
| tentative       |         2 |

`unknown` is what a resource container and an unrecognised payload share: the head was read, and neither said what lies behind it. `probable` is the 4,351 RPF9 rows, whose recogniser matches the magic and leaves authentication to whoever opens them. `tentative` is the two payloads that begin like XML and do not parse.

| Storage       |   Entries |
| ------------- | --------: |
| `chunked-2`   | 1,139,128 |
| `stored`      |    76,826 |
| `chunked-3`   |    24,436 |
| `chunked-4`   |    14,488 |
| `raw-deflate` |       161 |

1,398 entries carry the payload transform and every one decodes, including the 746 type-89 rows in chunked-2 storage and the four raw-DEFLATE rows ([payload-transform.md](payload-transform.md)).

### What the encoding-4 pass cost

Both passes that produced these coverage counts ran against the same release
build, one root archive at a time, on one machine reading a 150 GiB
installation.

| Pass     | Wall clock  |   Entries | Entries per second | Archives per second |
| -------- | ----------- | --------: | -----------------: | ------------------: |
| metadata | 20 min 28 s | 1,255,039 |              1,022 |                 3.6 |
| payload  | 29 min 31 s | 1,255,039 |                709 |                 2.5 |

Each pass ran on its own, from an empty output directory, so neither figure shares the machine with the other. The payload timing belongs to the pass that decoded the 14,432 encoding-4 rows. The later transform pass re-ran the roots whose rows it had refused, while other work shared the machine, so its wall clock is not comparable and is not quoted. The cost is per entry, not per byte: classifying an entry decodes one chunk before it can read the first 64 bytes, and that chunk's size is what the archive chose, not what the census asked for. An earlier note in this repository measured 91 entries per second; that figure came from a debug build. The same archive taken with a release build is four times faster, which is why a complete count is now affordable and why no figure here is a budgeted sample.

### What the types say

The 22 roots together reach 46 type ids: the 45 registered ids that rows use, and 255, the one id the build does not register. Twenty-six registered ids appear in no entry of the installation: 1, 7, 8, 9, 10, 12, 13, 65, 68, 71, 75, 76, 80, 81, 82, 83, 84, 85, 90, 91, 92, 97, 98, 106, 107 and 112. Seven of them are in the low range and nineteen in the high one. Since every `.rpf` under the installation was scanned, these are unobserved, not merely unsampled: this installation has no entry that uses them. What they would hold is not established by their absence.

Type 0 holds exactly 4,351 entries, and the passes opened exactly 4,351 nested archives. Every nested archive in this installation is a type-0 row. The type is still not a format: a type-0 row is an archive only because its payload is one, which is what the payload pass checks.

Some types hold one format throughout the installation, and others do not. Every type-0 row is an RPF9 archive (4,351), every type-64 row is a `MoVE` payload (443) and every type-66 row is a GFx payload (87). Against that, `PSIN` appears under four types — 11 (18,791), 93 (211), 94 (80) and 255 (2) — and type 11 holds `PSIN` and `RBF0` (1,493) side by side.

Type 255 is the catch-all the build does not name, 73,068 entries strong, and it holds everything: `ADAT` (71,676), `KB2` (797), `EDUP` (5), `PSIN` (2), 491 XML documents, five named signatures and 92 payloads that match nothing. No extension is declared for any of them, and 72,579 of those rows have none — the 489 that parsed as XML are the only ones that established one for themselves.

That is why the type cannot decide the format. A type whose rows share one identification is a type whose rows happened to; the matrix records every identification seen under every type, and it is the payload, not the type, that decides.

## What this does not establish

- Which resource a resource container holds. The classification records the segment and the page-map offset and stops there.
- The format of a payload that decoded but matched no signature.
- The format of a payload behind the transform when no key state is available.
- Any meaning for an entry type beyond the extension the loader registers for it.
- That a declared extension matches the bytes. The provenance says `native`, and a payload that says otherwise is reported in `conflict` rather than resolved.
- That these counts describe another installation or another build. Every count is of this installed copy and this executable; the journals are keyed to both, so a changed build or archive invalidates them instead of mixing them.
- That a payload's full content is known. Every claim except a validated document is about the first 64 decoded bytes.
