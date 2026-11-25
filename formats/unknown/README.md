# Unresolved payload signatures

Entries here are identified by observable payload bytes only. A signature is not a format identity, and a type ID is not either. Each entry records what the bytes show and what remains unknown.

| Signature | Rows | Archives      | Document                   |
| --------- | ---- | ------------- | -------------------------- |
| `EDUP`    | 3    | 3             | [edup](edup/README.md)     |
| `KB2j`    | 10   | `movies.rpf`  | [kb2j](kb2j/README.md)     |
| `KB2n`    | 787  | `movies.rpf`  | [kb2j](kb2j/README.md)     |
| `SGD5`    | 2    | `shaders.rpf` | not yet documented         |
| none      | 1    | `data.rpf`    | [type14](type14/README.md) |

These counts come from a signature census over the 6,534 unique rows of the 22 top-level archives, reading the first eight stored bytes of every untransformed row with at least eight stored bytes. Chunked rows are included; rows behind the payload transform are not, so the counts are lower bounds for those archives. Every other row in that set begins with a zlib stream, except the single encoding-2 row, whose first 16 stored bytes are the prefix recorded in RPF9-F119.

Evidence: [evidence/unknown-payloads/INDEX.md](../../evidence/unknown-payloads/INDEX.md).
