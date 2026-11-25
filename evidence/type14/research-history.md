# Type 14 research history

## 2026-11-25: structural layout replaces "no structural boundary"

The first type 14 document recorded one 1,280-byte payload with repeated `u16` values and stated that no structural boundary was established. Decoding the payload resolved a header, a string table starting at `0x330`, and eight records of `0x28` bytes from `0x3C0` to `0x500`, which is the end of the payload. T14-F04 to T14-F08 record the layout. The format identity and every field meaning remain **Unknown**, and the observations still come from a single decoded payload.

## 2026-11-25: record identifiers match the string table, not the record name

The layout findings left the eight `u32` record identifiers uninterpreted
(T14-F10). Re-reading the decoded payload shows that each identifier equals the
one-at-a-time ("joaat") hash of the string-table entry at the same index, over
the exact entry bytes excluding the terminating `0x00`: 8/8.

The exact boundary matters. Including the terminator gives 0/8, and byte-swapped
output gives 0/8. The folded lower-case and case-sensitive forms both give 8/8
because the eight string-table entries are lower-case ASCII. That coincidence is
a property of this payload.

The record name field is not the preimage. Six of eight record names differ from
the same-index string only by case; two have different text, and one of those is
16 bytes against a 10-byte string. Hashing the record names gives 6/8 for the
folded form and 0/8 for the case-sensitive form.

The relation is established on one decoded payload. The second type 14 row is
behind the payload transform and was not compared, so the relation is not
generalised to that row or to other record types. The header values at `+0x20`,
`+0x24` and `+0x28` still match none of the tested hashes and remain **Unknown**.
