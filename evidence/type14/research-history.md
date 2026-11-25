# Type 14 research history

## 2026-11-25: structural layout replaces "no structural boundary"

The first type 14 document recorded one 1,280-byte payload with repeated `u16` values and stated that no structural boundary was established. Decoding the payload resolved a header, a string table starting at `0x330`, and eight records of `0x28` bytes from `0x3C0` to `0x500`, which is the end of the payload. T14-F04 to T14-F08 record the layout. The format identity and every field meaning remain **Unknown**, and the observations still come from a single decoded payload.
