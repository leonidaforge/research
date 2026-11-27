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

The classification reads at most 64 decoded bytes. The matrix publishes the first 32 of them with every sample, which is a sample of the head, not the whole head.

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
| `transform-unavailable` | The payload is behind the transform and no key state is available |
| `transform-failed`      | The transform was available but did not verify or run             |
| `undecodable`           | The storage cannot be decoded                                     |
| `malformed`             | The metadata describing the payload is malformed                  |

Only `decoded` entries are identified. A state that is not `decoded` is a fact about the archive, not a guess about the payload: the entry is reported as unidentified with the reason, never as an unknown format.

## Terminal outcome

Every entry ends an investigation with exactly one outcome, and the census counts them so the counts add up to the entry count. This is what makes an inventory exhaustive rather than a pile of categories: a row cannot be counted twice and cannot be left out.

| Outcome                 | Established                                                        |
| ----------------------- | ------------------------------------------------------------------ |
| `identified`            | The payload's own framing was walked and the container named        |
| `partially-identified`  | Something about the payload, but not the container                  |
| `unresolved`            | The payload was read and nothing in it was recognised               |
| `undecodable`           | The storage cannot be decoded                                       |
| `transform-unavailable` | The payload is behind the transform and no key state is available   |
| `malformed`             | The metadata describing the payload is malformed                    |
| `blocked`               | The payload was not read, or the transform did not verify or run    |

`partially-identified` covers the three shapes that stop short of a container: a magic-only match such as `RPF9`, a resource header whose page map was not read, and a payload that looks like XML without parsing as XML. `blocked` is the honest label for a metadata pass and for a transform that failed to verify: nothing was established about the bytes, and the reason field says why.

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

## Sample

The census below is bounded: every root archive of the install gets the same entry budget, and nested archives are entered where they lie or through temporary storage. It is a sample, not a complete count. The machine-written matrix is [entry-matrix.md](entry-matrix.md) with the same data in [entry-matrix.json](entry-matrix.json).

### How the sample was taken

One run per root archive, each with the same budget:

```sh
lforge archive census <root>.rpf --executable <game executable> --recursive \
    --samples 3 --max-depth 4 --max-archives 64 --max-entries 900 \
    --max-nested-bytes 268435456 --max-spool-bytes 4294967296
```

Every root archive under the installation, found recursively: 22 discovered, 22 opened, 126 archives opened (104 of them nested), 11,283 entries classified, no archive failed to open. Seventeen roots stopped at their per-root entry budget, so the run is a sample and the matrix records `complete: false`. Nothing was copied to temporary storage: every nested archive in the sample had all-copy chunks and was read where it lies.

### What the sample holds

| Identification                | Entries | Share |
| ----------------------------- | ------: | ----: |
| resource container            |   7,189 | 63.7% |
| supported format              |   3,634 | 32.2% |
| validated XML document        |     421 |  3.7% |
| nothing, or a named signature |      39 |  0.3% |

| Format | Entries |
| ------ | ------: |
| `PSIN` |   1,442 |
| `ADAT` |   1,410 |
| `KB2`  |     522 |
| `RBF0` |     156 |
| RPF9   |     104 |
| GFx    |       5 |

Every resource container is segment 5. The matrix records the documents' distinct roots and the two payloads that begin like XML without parsing as `xml:unvalidated`.

| Capability  | Entries | Share |
| ----------- | ------: | ----: |
| resource    |   7,189 | 63.7% |
| structural  |   3,536 | 31.3% |
| text        |     423 |  3.7% |
| archive     |     104 |  0.9% |
| bytes       |      30 |  0.3% |
| unavailable |       1 |  0.0% |

| Extension | Entries |
| --------- | ------: |
| native    |   9,317 |
| `xml`     |     421 |
| none      |   1,545 |

| Structure claim | Entries |
| --------------- | ------: |
| verified        |   3,957 |
| probable        |     104 |
| tentative       |       2 |
| unknown         |   7,220 |

154 entries carry the payload transform. The executable's key state was available for them, and 153 decoded; one entry did not verify and is reported as `transform-failed` rather than identified.

### What the type does and does not say

Twenty-eight types appear in the sample, against twenty-one in the earlier twelve-root run. Nine of them were never reached before, because ten root archives under `pack/` were missed by a non-recursive glob: 4, 15, 16, 17, 72, 73, 78, 88 and 108. Types 93 and 94, which the tighter budget had reached before, are not in this sample.

The thirteen resource-only types of the earlier sample (2, 3, 5, 6, 67, 70, 74, 79, 87, 95, 102, 111, 114) still hold only resource containers, and every type except 255 has a registered native extension. Type 255 is the unregistered catch-all and holds `ADAT`, `KB2`, documents, named signatures and payloads that match nothing.

Eleven types the earlier investigation recorded remain unobserved in both runs: 14, 64, 69, 77, 86, 99, 101, 103, 109, 110 and 115. They are unobserved, not disproved; the per-root entry budgets are the first thing to raise, and no scan has yet reached the archives that hold them.

That is why the type cannot decide the format. A type that holds one identification in the sample is a type whose rows happened to share one; it is not a promise about the next row.

## What this does not establish

- Which resource a resource container holds. The classification records the segment and the page-map offset and stops there.
- The format of a payload that decoded but matched no signature.
- The format of a payload behind the transform when no key state is available.
- Any meaning for the entry type. Every type seen in the sample is reported with the identifications observed under it, and no type is treated as a format.
- That the sample is complete. Types and combinations outside the budgets are not counted.
