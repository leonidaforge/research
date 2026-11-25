# Unresolved payload signatures

Entries here are identified by observable payload bytes only. A signature is not a format identity, and a type ID is not either. Each entry records what the bytes show and what remains unknown.

| Signature | Rows                 | Archives      | Document                   |
| --------- | -------------------- | ------------- | -------------------------- |
| `EDUP`    | 3 stored / 5 decoded | 5             | [edup](edup/README.md)     |
| `KB2j`    | 10                   | `movies.rpf`  | [kb2j](kb2j/README.md)     |
| `KB2n`    | 505                  | `movies.rpf`  | [kb2j](kb2j/README.md)     |
| `PTFX`    | 1                    | `common.rpf`  | [ptfx](ptfx/README.md)     |
| `SGD5`    | 2                    | `shaders.rpf` | [sgd5](sgd5/README.md)     |
| none      | 1                    | `data.rpf`    | [type14](type14/README.md) |
| `PSIN`    | 18 sampled           | 5 archives    | [psin](psin/README.md)     |
| `GFX*`    | 49                   | 6 depth-1 under `data.rpf`   | [gfx](gfx/README.md)       |
| `ADAT`    | 768                  | 65 depth-1 under 4 top-level archives | [adat](adat/README.md)     |

These counts come from a signature census over the 6,534 unique rows of the 22 top-level archives, reading the first eight stored bytes of every untransformed row with at least eight stored bytes. Chunked rows are included; rows behind the payload transform are not, so the counts are lower bounds for those archives. The `GFX*` figure is not a top-level census result: all 49 rows are type-66 rows in depth-1 archives, and their stored payloads are zlib streams, so the signature appears only after chunk decoding. See [gfx](gfx/README.md). Every other row in that set begins with a zlib stream, except the single encoding-2 row, whose first 16 stored bytes are the prefix recorded in RPF9-F119. PSIN is recorded from decoded payloads, not from stored bytes: its rows are chunked, so the census sees a zlib stream where the decoded payload begins with `PSIN`. `EDUP` shows the same effect: the stored-byte census sees three rows, but decoding the two other rows with the same name key adds two, so the decoded occurrence is five. The table records both counts for `EDUP`. The `KB2n` figure is 505 from the current 515-row `movies.rpf` manifest. An earlier census reported 787 over a 797-row `movies.rpf` population whose manifest is not preserved; that figure is not interchangeable with the current one. The two populations and their selection rules are listed in [KB2-F12](../../evidence/kb2j/INDEX.md#census-reconciliation). The `ADAT` count is a depth-1 nested-payload count from the newer inventory, not a top-level census row.
