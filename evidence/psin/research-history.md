# PSIN research history

Interpretations that were once used for PSIN and later corrected. The current model is in the [specification](../../formats/unknown/psin/README.md).

## Bytes at `+0x04` read as a `u16`

**Old assumption.** Bytes `+0x04..+0x05` were an independent `u16`, `00 00` in 17 samples and `00 02` in one. A little-endian reading gave 0 and `0x0200`.

**Correction.** Bytes `+0x04..+0x07` are a big-endian `u32` offset to the first tagged section (PSIN-F02). The old `00 00` and `00 02` values are its high half. The low half is the big-endian `u16` at `+0x06` (PSIN-F03). The sample grew from 18 to 103 payloads, and the offset reaches `0x000ED708`, so the high half can be nonzero in more than one sample.
