# Resource pointers

A reconstructed resource carries 32-bit pointer values. In the primary sample the system segment holds 51 such values: 39 starting with `0x5` and 12 starting with `0x6`. The stored bytes are `0x5000…` and `0x6000…`.

Findings are cited as `RES-F02` and listed in [evidence/resources/INDEX.md](../../evidence/resources/INDEX.md).

## Encoding

Observed values:

```text
0x50000040  0x50000610  0x50000740
0x60000000  0x60001000  0x6000B000
```

The high bits select a segment; the remaining bits are an offset inside that segment.

| Reading         | Rule                                                                  | Status                                                                |
| --------------- | --------------------------------------------------------------------- | --------------------------------------------------------------------- |
| 4-bit selector  | bits 28..31 select the segment, bits 27..0 are the offset             | Confirmed (RES-F16)                                                   |
| 16-bit selector | high 16 bits select the segment, low 16 bits are the offset           | Rejected (RES-F16)                                                    |
| Virtual address | value is `segment_base + offset`, bases `0x50000000` and `0x60000000` | Arithmetically identical to the 4-bit selector for the observed bases |

The primary sample alone cannot separate these readings: both segments are small. A second sample separates them. One resource places its page map at system offset `0x988E0` and holds an in-bounds system pointer at `0x98B34`; a 16-bit offset cannot express either value. The 4-bit selector with a 28-bit offset fits. The same resource also contains one pointer-like value outside the segment, at offset `0xC74C225`, which is reported as a warning rather than used as structure (RES-F18).

The offset is at most `0x0FFFFFFF`. A larger offset would set bit 28 and change the decoded segment, so the encoding cannot express more. This is a property of the scheme, not an observed upper bound. The largest observed in-bounds offsets are `0x740` (system) and `0xB000` (graphics) in the primary sample, and `0x2600000` (graphics, about 39.8 MB) in a split-page sample.

## Counts and bounds

Primary sample:

| Property                     | Value                   |
| ---------------------------- | ----------------------- |
| System segment size          | 1,888 bytes (`0x760`)   |
| Graphics segment size        | 49,152 bytes (`0xC000`) |
| Values starting `0x5`        | 39                      |
| Values starting `0x6`        | 12                      |
| Highest system offset        | `0x740`                 |
| Highest graphics offset      | `0xB000`                |
| Values outside their segment | 0                       |

The reported survey of 1,466 authenticated rows counted 34,022 system-shaped values and 6,609 graphics-shaped values in system data, with 1,353 and 591 outside their segment. A further 1,560 resources from the `data.rpf` data area were re-parsed by the source survey: 2,112,806 system-shaped values (44,463 outside) and 94,564 graphics-shaped values (52,873 outside). Those totals come from the source survey and were not re-counted in this consolidation.

Scan predicate: every 8-byte aligned `u64` whose upper half is zero and whose low 32 bits have top nibble `0x5` or `0x6`. Mutual consistency supports the model but does not prove it. Values outside a segment are expected in arbitrary data (RES-F18).

## Segment-wide offsets

Pointer offsets address the concatenated pages of a segment, not a page. In one rechecked resource the page map is at system offset `0x988E0`, beyond the 65,536-byte first system page, and in-bounds system pointers reach `0x98B34` (RES-F17). A page-relative offset could not express either value.

## Pointer table

The system slot at `+0x30` points to `0x50000580`. From that offset, 12 consecutive 8-byte slots hold `0x5000` values. The `u16` fields at `+0x28` and `+0x38` both hold `0x000C`, matching the 12 entries. This fits a `{pointer, count}` descriptor, but the pairing is **Probable** and the field meanings are **Unknown** (RES-F05).

The table entries:

```text
0x50000350 0x50000040 0x50000270 0x50000200 0x50000190 0x50000120
0x500000B0 0x50000510 0x500004A0 0x50000430 0x500003C0 0x500002E0
```

All 12 are inside the system segment. Their targets were not interpreted.

## Stored width

The observed pointer fields are 8-byte slots whose upper 32 bits are zero: the header slot at `+0x08`, the array at `0x580`, and the 12 graphics values. Whether a field may be 4 bytes wide elsewhere, or whether the upper half carries flags or a wider address, is **Unknown** (RES-F09). A reader MUST check the upper half rather than discard it silently.

The source survey found 12,441 `u64` values with a pointer-shaped low half and a nonzero upper half. They were not counted as pointers; whether any is one is not established.

## False positives

Matching the two high nibbles alone is a heuristic. Values that look like pointers but cannot be:

- fill patterns, such as the repeating `0x55555555`;
- text read as a little-endian `u64`, for example `0x0C617274` from the bytes `74 72 61 0C` (`tra`);
- 32-bit hashes whose bits 28..31 happen to be `0101` or `0110`, followed by four zero bytes.

In a rechecked split-page resource, 8 graphics-shaped values point outside the graphics segment. In the `data.rpf` sample of the source survey more than half of the graphics-shaped values point outside the graphics segment. Their number, not their position, is what makes them visible.

### Consequences

- A pointer-like value outside a segment is a warning. It is not proof that a page is missing.
- No case was found where an outside value corresponded to a page that the page map declared and the payload did not store.
- Pointer-derived structure, such as string tables, can be checked against its target bytes. A pointer count alone cannot.

## Validation rules for a reader

- Apply the 4-bit selector and keep the two segment prefixes as observed values.
- Require the upper 32 bits to be zero.
- Reject an offset at or above the reconstructed size of its segment, and report it as unresolved rather than resizing the segment.
- Do not write through a pointer. A parser only reads.
- Report unresolved values as counts with their byte positions.

These are reader rules. No engine-side validation was traced; whether or how the engine validates pointers remains **Unknown**.

The published [parser](../../tools/resources/README.md) counts decoded pointers and values outside a segment but does not interpret targets.
