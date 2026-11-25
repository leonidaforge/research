# EDUP

`EDUP` (`45 44 55 50`) at offset 0 marks payloads in three rows across three archives, all type ID 255:

| Archive                    | Row | Stored | Logical |
| -------------------------- | --- | ------ | ------- |
| `pack/core_restofworld001` | 1   | 32     | 28      |
| `pack/shared_minigame000`  | 53  | 240    | 236     |
| `pack/story000`            | 532 | 32     | 28      |

All three rows are chunked with entry encoding 3 and none carries the payload transform. After removing the recorded padding, each stored length equals its logical size, which is the condition the engine requires to finish a copy chunk (see [chunk layout](../../containers/rpf9/payloads.md#chunk-layout-and-decoding)). That the chunks use the copy method is **Probable**: the method bits were not read from the chunk table.

## Observed structure

| Offset  | Observation                                                                                            |
| ------- | ------------------------------------------------------------------------------------------------------ |
| `+0x00` | `45 44 55 50`                                                                                          |
| `+0x04` | `u32`: `0` in the two 28-byte payloads, `4` in the 236-byte payload                                    |
| `+0x08` | `u32` 16 in the two 28-byte payloads, followed by 16 bytes. High-entropy value in the 236-byte payload |

The two 28-byte payloads are byte-identical although they come from different archives. Each is 28 bytes: the magic, a `u32` 0, a `u32` 16 and a final 16 bytes. The 236-byte payload does not follow that shape: the `u32` after the magic is 4, and the remaining 228 bytes contain no visible length field.

## Confidence

| Part                 | Status                                                                                      |
| -------------------- | ------------------------------------------------------------------------------------------- |
| Magic and occurrence | Confirmed (3 rows, 3 archives)                                                              |
| Copy-chunk storage   | Confirmed for the stored sizes; Probable for the method, which the manifest does not report |
| Payload identity     | Unknown                                                                                     |
| Any field meaning    | Unknown                                                                                     |

## Limits

- Three rows. One distinct 28-byte payload and one 236-byte payload were compared.
- The high-entropy bytes after the header are not described. Calling them a digest or a checksum would be a guess.
- No executable path was traced and no earlier RAGE format is claimed as a match.
- Whether `EDUP` marks a file, a record inside a larger structure, or a derived copy is not established.

Evidence: [evidence/unknown-payloads/INDEX.md](../../../evidence/unknown-payloads/INDEX.md).
