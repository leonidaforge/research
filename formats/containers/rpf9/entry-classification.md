# RPF9 entry classification

An RPF9 row does not say what it holds. The table of contents gives a numeric type, a storage shape and a name hash; nothing in it is a file format. Anything that shows, extracts or exports an entry has to decide three separate things:

1. **What the entry type is.** A number stored in the location record, 0 to 255.
2. **What the payload is.** A format, a resource container, a text document, or nothing recognisable.
3. **What the application can do with it.** Open it as an archive, parse it structurally, show it as text, read a resource, or only show its bytes.

Treating these as one property is the mistake this document exists to prevent. Type 255 holds payloads of every kind. Type 0 usually holds a nested archive and, in the sample below, also holds a `PSIN` payload. A type 5 entry is a candidate for the texture viewer only because the type was named that way in observations, not because the bytes are known to be a texture dictionary.

## Where the evidence comes from

A classification reads bounded evidence and records which part of it decided:

| Evidence     | Read                                                     | Cost                                                      |
| ------------ | -------------------------------------------------------- | --------------------------------------------------------- |
| Type         | The location record's type byte                          | Metadata only                                             |
| Storage      | The location record's mode and the chunk table           | Metadata only                                             |
| Payload      | The decoded payload's first 64 bytes                     | One decoded chunk in the worst case                       |
| Document     | A decoded document up to 4 MiB, when the head looks XML  | One document                                              |
| Structure    | Nothing extra: recognisers that walk framing do it on the head | Included in the head read                           |

The classification never reads a payload in full, never guesses an extension it cannot establish, and never lets the type decide the format.

## Confidence

| Level       | Meaning                                                                                  |
| ----------- | ---------------------------------------------------------------------------------------- |
| `verified`  | Repeated tests of real data and structural evidence agree                                 |
| `probable`  | Several observations agree, but the evidence that would settle it is missing              |
| `tentative` | A plausible hypothesis that independent checks do not confirm                             |
| `unknown`   | The available evidence establishes nothing useful                                         |

A recognised format is `verified` when its recogniser walks the payload's own framing from the head, and `probable` when the recogniser matches an identifier only. The RPF9 magic is such an identifier: the head proves the magic, and the archive parser proves the structure when a caller opens it.

A validated XML document is `verified`: the whole document parsed and its root element is known. Bytes that only begin like XML are `tentative`.

A resource header is `probable`. Its shape is established from real rows, but which resource it holds is not.

## Storage

Storage says how the bytes are stored, not what they are. The label is stable and is recorded in every census row:

| Label          | Condition                                  |
| -------------- | ------------------------------------------ |
| `stored`       | No chunk table, mode 0: the bytes lie as they are |
| `raw-deflate`  | No chunk table, mode 1: one raw DEFLATE stream |
| `chunked-2`    | A chunk table with encoding 2               |
| `chunked-3`    | A chunk table with encoding 3               |
| `chunked-4`    | A chunk table with encoding 4               |
| `chunked-other`| A chunk table with any other encoding       |

The payload transform is recorded separately, because it is a property of the stored bytes rather than of the chunks. A chunk table's per-chunk method decides decoding; the location record's mode does not apply to a chunked entry.

One practical consequence, used by the census: when every chunk of an entry copies its bytes, has no padding and is exactly as long as it is stored, the decoded payload is the stored range itself, so a nested archive can be read where it lies. Otherwise the payload has to be decoded before it can be read as an archive.

## Payload state

| State                    | Meaning                                                             |
| ------------------------ | ------------------------------------------------------------------- |
| `decoded`                | The decoded head was read                                            |
| `transform-unavailable`  | The payload is behind the transform and no key state is available     |
| `transform-failed`       | The transform was available but did not verify or run                 |
| `undecodable`            | The storage cannot be decoded                                         |
| `malformed`              | The metadata describing the payload is malformed                      |

Only `decoded` entries are identified. A state that is not `decoded` is a fact about the archive, not a guess about the payload: the entry is reported as unidentified with the reason, never as an unknown format.

## Identification

| Kind           | What it records                                                          |
| -------------- | ------------------------------------------------------------------------ |
| `format`       | A supported format and its recogniser's claim                            |
| `resource`     | Eight zero bytes then a `0x5…` or `0x6…` pointer                          |
| `xml`          | A document, with its root element when it parsed                          |
| `signature`    | A named signature whose format is not established                         |
| `unrecognised` | Nothing in the first 64 bytes identifies the payload                       |

### The resource header

Every resource-shaped payload in the sample starts with the same two 64-bit words:

| Offset | Width | Value                                                                   |
| ------ | ----- | ----------------------------------------------------------------------- |
| `+0x00`| 8     | Zero                                                                     |
| `+0x08`| 8     | A pointer: the segment nibble in bits 28 to 31, the offset in bits 0 to 27 |

The segment nibble is 5 (system) or 6 (graphics). A pointer outside those two segments, a non-zero first word, or a pointer that does not fit in 32 bits is not treated as a resource header, which keeps the match narrow. Observed heads include `0000000000000000 7091e25000000000` (pointer `0x50E29170`, segment 5, offset `0x0E29170`) and `0000000000000000 10fa005000000000` (pointer `0x5000FA10`, segment 5, offset `0x00FA10`).

The header establishes the container and the segment. It does not establish which resource is inside: the page map and the resource's own descriptor are not read by the classification. That is why a resource entry has no extension.

### Signatures without a format

Four signatures are named without claiming a format, because the bytes are distinctive and nothing more is known: `MoVE`, `SGD5`, `MHIU` and `SPS1`. `DDS ` and the PNG signature are named as images. Naming them separates "we know these bytes start a known container" from "we do not know what this is", which matters for the backlog: the first group has a target, the second does not.

## Extension

An extension is applied only when the classification establishes it. The order is:

1. The archive's own name, if the entry resolved to one. It is kept exactly as found, including case and a leading dot.
2. `rpf` when the payload is an RPF9 archive.
3. `xml` when the payload is a validated XML document.
4. Nothing, with a reason.

A recognised format without an established extension stays unresolved with the reason "the format is recognised but no extension is established" rather than borrowing the extension from a type table or a neighbouring file. The same applies to a resource container ("the asset class is not identified"), to a named signature, to a payload that is transformed and was not decoded ("the payload is transformed and was not decoded"), and to an entry typed as an archive whose payload is not one.

Two consequences follow. A listing cannot show an extension for most rows, because most payloads are resource containers. And no caller needs to invent a fallback: `extension` is present or absent, and `extension_verified` says whether it may be applied without a fallback.

## Capability

| Capability    | Meaning                                                    |
| ------------- | ---------------------------------------------------------- |
| `archive`     | The archive commands open its table of contents             |
| `structural`  | A structural inspection, without field meaning              |
| `text`        | A document shown as text                                    |
| `resource`    | A resource container whose asset class is not identified    |
| `bytes`       | Bytes only, through the binary viewer                       |
| `unavailable` | Nothing can be decoded; the reason says why                 |

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

Twelve root archives, 69 archives opened, 8,138 entries classified. Eight roots stopped at their entry budget; `appdata0.rpf` (2), `common.rpf` (418), `movies.rpf` (515) and `shaders.rpf` (3) ended because the archive and its nested archives were exhausted. No archive failed to open. Nothing was copied to temporary storage: every nested archive in the sample had all-copy chunks and was read where it lies.

### What the sample holds

| Identification | Entries | Share |
| -------------- | ------: | ----: |
| resource container | 5,140 | 63.2% |
| supported format | 2,575 | 31.6% |
| validated XML document | 399 | 4.9% |
| nothing | 19 | 0.2% |
| named signature | 5 | 0.1% |

| Format | Entries |
| ------ | ------: |
| `PSIN` | 955 |
| `ADAT` | 887 |
| `KB2` | 515 |
| `RBF0` | 156 |
| RPF9 | 57 |
| GFx | 5 |

Every resource container is segment 5. Of the 399 XML payloads, 397 parse, under 164 distinct root elements; the other two begin like XML and are reported as tentative.

| Capability | Entries | Share |
| ---------- | ------: | ----: |
| resource | 5,140 | 63.2% |
| structural | 2,518 | 30.9% |
| text | 399 | 4.9% |
| archive | 57 | 0.7% |
| bytes | 23 | 0.3% |
| unavailable | 1 | 0.0% |

| Extension | Entries |
| --------- | ------: |
| none | 7,684 |
| `xml` | 397 |
| `rpf` | 57 |

| Confidence | Entries |
| ---------- | ------: |
| probable | 5,197 |
| verified | 2,920 |
| unknown | 19 |
| tentative | 2 |

152 entries (1.9%) carry the payload transform. The executable's key state was available for them, and 151 decoded; one type-89 entry did not verify and is reported as `transform-failed` rather than identified.

### What the type does and does not say

Twenty types appear in the sample. Thirteen of them hold only resource containers: 2, 3, 5, 6, 67, 70, 74, 79, 87, 95, 102, 111 and 114. Five hold only a supported format: 0 (RPF9), 11 (`PSIN` and `RBF0`), 66 (GFx), 93 and 94. Two hold nothing identifiable: 89 and 96, one entry each.

Type 255 holds all of it: `ADAT` (887), `KB2` (515), 399 XML documents under 164 roots, 17 payloads that match nothing, the five named signatures, and two `PSIN` payloads. Type 11 holds two formats, `PSIN` (897) and `RBF0` (156). Type 0 holds RPF9 archives throughout the sample; a synthetic fixture in the test suite also shows a type-0 row holding `PSIN`, which is why the type never decides the format in the code either.

That is why the type cannot decide the format. A type that holds one identification in the sample is a type whose rows happened to share one; it is not a promise about the next row.

## What this does not establish

- Which resource a resource container holds. The classification records the segment and the page-map offset and stops there.
- The format of a payload that decoded but matched no signature.
- The format of a payload behind the transform when no key state is available.
- Any meaning for the entry type. Every type seen in the sample is reported with the identifications observed under it, and no type is treated as a format.
- That the sample is complete. Types and combinations outside the budgets are not counted.
