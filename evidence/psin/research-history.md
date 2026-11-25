# PSIN research history

Interpretations that were once used for PSIN and later corrected. The current model is in the [specification](../../formats/unknown/psin/README.md).

## Bytes at `+0x04` read as a `u16`

**Old assumption.** Bytes `+0x04..+0x05` were an independent `u16`, `00 00` in 17 samples and `00 02` in one. A little-endian reading gave 0 and `0x0200`.

**Correction.** Bytes `+0x04..+0x07` are a big-endian `u32` offset to the first tagged section (PSIN-F02). The old `00 00` and `00 02` values are its high half. The low half is the big-endian `u16` at `+0x06` (PSIN-F03). The sample grew from 18 to 103 payloads, and the offset reaches `0x000ED708`, so the high half can be nonzero in more than one sample.

## One header model for every PSIN payload

**Old assumption.** The header at `+0x04` and `+0x08..+0x0F` had one meaning for every payload, and the first-section offset was 16-byte aligned in all samples.

**Correction.** The outer framing is shared, but the pre-section area has two grammars. `LSCH` payloads hold a 16-byte descriptor table at `+0x08`; `PMAP` payloads begin the area with eight `0x70` bytes and have no descriptor solution. All 695 unique `LSCH` payloads are aligned; 10 of 62 `PMAP` payloads are unaligned. The two families are not separate file formats.

## 103 payloads as the PSIN population

**Old assumption.** The recorded sample of 103 unique payloads was treated as the reachable PSIN population.

**Correction.** The 103 figure is the earlier 18 payloads plus 85 additional payloads. The 85 additions combine the deterministic top-level sample and the depth-1 payloads; duplicates are removed by SHA-256 before the total is taken. The 82 expanded-extraction payloads and the 13 depth-1 payloads are the two source sets, not additional components. The full recount in the current scope is 757 unique payloads: 695 `LSCH` and 62 `PMAP`.

## The pre-section area was undecoded

**Old assumption.** The bytes before the first section were not decoded beyond repeated `0xAA` and `0x70` runs.

**Correction.** The `LSCH` area contains a descriptor table whose count satisfies `0x10 + 16 * C + sum(align16(length_i)) == first_section_offset` with a unique solution in 695 of 695 payloads. The `PMAP` area has a stable eight-byte `0x70` marker but no descriptor solution. The `PMAP` record grammar remains undecoded.

## The `CHKS` section was a length-only observation

**Old assumption.** `CHKS` was recorded as a 20-byte section with a 12-byte body.

**Correction.** The body holds a big-endian total-length word, a big-endian checksum and ASCII `zppp`. The total-length word equals the payload size in 757 of 757 payloads. The checksum is a one-at-a-time hash over signed bytes seeded with `0x3FAC7125`, over the payload with the length and checksum words zeroed; it verifies in 757 of 757 payloads. The seed is unexplained.

## `LSCH` body header-word counts

**Old reading.** The `u32` at body `+0x08` was recorded as 512 in 441 payloads, 768 in 35 payloads, and 1024 in 7 payloads.

**Correction.** The pairing was wrong. The correct counts over the same 483 unique top-level `LSCH` payloads are 768 in 441, 512 in 35, and 1024 in 7. The value set and total are unchanged; only the counts assigned to 512 and 768 were swapped. The correction came from `tools/psin/body_probe.py` and `tools/psin/body-record.json`.
