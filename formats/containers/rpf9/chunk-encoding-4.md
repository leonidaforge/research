# RPF9 chunk encoding 4

Encoding 4 is a chunk-table descriptor layout, not a compression algorithm. Its
entry fields give each chunk a logical size, a stored size, padding and a
two-bit method. The method selects zlib or a copy. The framing differs from
encoding 2 in one respect only: the 16-byte stored prefix is present on some
rows and absent on others.

Status: **Confirmed** on all 14,488 encoding-4 entries of the installation.
Every one decoded to its declared logical size (RPF9-F151).

## Chunk table

The value of key `0xE0C12D7A5D4884C5` has the same header as encodings 2 and 3:

| Offset  | Type  | Meaning                                                     |
| ------- | ----- | ----------------------------------------------------------- |
| `+0x00` | `u32` | Offset of the entry array, relative to the start of the value |
| `+0x04` | `u16` | Chunk count                                                 |
| `+0x06` | `u8`  | `0x08` in every observed table; no reader uses it           |
| `+0x07` | `u8`  | Entry encoding: 4                                           |

Each entry is a `u64`:

| Field      | Bits    | Meaning                                  |
| ---------- | ------- | ---------------------------------------- |
| Logical    | 0..27   | Logical chunk size, in bytes             |
| Stored     | 28..51  | Stored chunk size in 16-byte units       |
| Padding    | 52..55  | Bytes after the compressed data, 0 to 15 |
| Method     | 56..57  | 3: zlib; 0, 1, 2: copy                   |

The compressed size is `stored - padding`. Stored sizes are therefore multiples
of 16. A method-3 chunk holds one zlib stream (RFC 1950) with its Adler-32
trailer. A copy chunk's compressed size MUST equal its logical size.

Bits 58..63 are zero in every observed entry and no reader uses them.

## Stored framing

Chunks are stored back to back. Chunk `i` starts at

```text
payload offset + stored prefix + sum(stored size of chunks 0..i-1)
```

`stored prefix` is the entry's stored size minus the sum of its chunk stored
sizes. Across the installation it is 0 on 56 rows and 16 on 14,432 rows; no
other value occurs (RPF9-F150). On every 16-byte prefix the bytes are zero.
Within a chunk, the compressed bytes come first, then the padding.

The prefix's meaning is not established. It is not part of the decoded payload;
the chunk logical sizes already sum to the entry's logical size. It is also not
a zlib header. The same 16-byte zero prefix occurs before encoding-2 chunks
(RPF9-F119, RPF9-F124), and the resource layout explains neither the presence
nor the absence: every row with the prefix uses location record R and every row
without it uses F, but the decoder derives the length from the sizes instead of
reading the layout.

A reader MUST NOT assume the prefix from the encoding number. It MUST compute it
from the entry's stored size and the chunk stored sizes, accept only the
observed lengths, and reject any other gap.

### Samples

| Chain | Type | Bytes | Chunks | Methods | Prefix | Meaning |
| --- | ---: | ---: | ---: | --- | ---: | --- |
| `pack/core_bvh4/core_bvh4.rpf!772!0` | 15 | 131,280 | 2 | 3, 3 | 16 | two zlib chunks |
| `levels.rpf!1719!1429` | 4 | 20,050,112 | 6 | 3, 3, 3, 3, 3, 3 | 16 | largest entry |
| `levels.rpf!1029!4065` | 11 | 2,504 | 1 | 3 | 0 | `PSIN` payload |
| `levels.rpf!1029!2750` | 73 | 102,272 | 3 | 3, 0, 3 | 16 | copy chunk in the middle |
| `levels.rpf!1806!0` | 2 | 13,552 | 2 | 3, 3 | 16 | type-2 drawable |
| `levels.rpf!1091!0` | 255 | 15 | 1 | 0 | 0 | `FORCE_EMPTY_RPF` |

All paths are installation-relative. `levels.rpf!N` names row `N` of
`levels.rpf`; `!M` after it names row `M` of that nested archive.

## Observed variants

| Property | Observation | Entries |
| --- | --- | ---: |
| Stored prefix | 16 zero bytes | 14,432 |
| Stored prefix | none | 56 |
| Chunk count | 1 to 6 | 14,488 |
| Chunk methods | zlib only | 14,098 |
| Chunk methods | at least one copy | 390 |
| Copy chunk position | last | 386 |
| Copy chunk position | middle, followed by zlib | 4 |
| Payload transform | absent | 14,488 |
| Read source | main | 14,488 |
| Location record | R | 14,432 |
| Location record | F | 56 |

The 390 rows with a copy chunk are 384 of type 73, three of type 6, two of type
74 and the one type-255 row. Four type-73 rows store `3, 0, 3`: a copy chunk
between two zlib chunks. The decoder therefore MUST decide each chunk from its
own method; it MUST NOT assume that a copy chunk ends the stream.

| Type | Extension | Entries | Decoded bytes | Stored bytes |
| ---: | --- | ---: | ---: | ---: |
| 15 | `zbdr` | 4,768 | 2,816,930,960 | 160,447,744 |
| 73 | `zmap` | 4,087 | 93,067,184 | 36,621,200 |
| 2 | `zdr` | 3,196 | 1,807,840,496 | 697,823,360 |
| 6 | `zbn` | 1,654 | 274,704,768 | 171,736,000 |
| 16 | `zbdd` | 256 | 138,896 | 57,984 |
| 4 | `zdd` | 256 | 402,763,808 | 142,896,816 |
| 74 | `ztyp` | 173 | 74,100,080 | 20,058,032 |
| 11 | `zmt` | 88 | 990,240 | 482,736 |
| 67 | `zcd` | 9 | 36,752 | 10,832 |
| 255 | none | 1 | 15 | 16 |
| **Total** | | **14,488** | **5,470,573,199** | **1,230,134,720** |

Decoded payloads classify as follows: 14,432 resource headers on system segment
5, 55 `PSIN` documents of type 11, and the one 15-byte type-255 payload, which
matches no signature. Header recognition is not decoding; the table above is the
result of reading every payload to its end.

## Comparison with encodings 2 and 3

| Property | Encoding 2 | Encoding 3 | Encoding 4 |
| --- | --- | --- | --- |
| Stored prefix | 16 bytes, always | none | 0 or 16 bytes |
| Logical size field | bits 0..23, in 16-byte units | `0x10000 - bits 0..15` | bits 0..27, bytes |
| Stored size field | bits 32..55, in 16-byte units | `padding + (0x10000 - bits 16..31)` | bits 28..51, in 16-byte units |
| Padding | bits 58..61 | bits 16..19 | bits 52..55 |
| Method | bits 62..63 | bits 60..61 | bits 56..57 |
| Method 3 | zlib | zlib | zlib |
| Other methods | copy | copy | copy |
| Entry mode | unused with a chunk table | unused | unused |

All three encodings share one decode loop: validate the table and its spans,
then for each chunk either inflate exactly the compressed bytes and require the
declared output, or copy and require equal sizes, then skip the padding
(RPF9-F78).

## Why the previous decoder failed

The decoder accepted encoding 4 and decoded its chunk table. It then started
chunk 0 at the payload offset, as it does for encoding 3, because the
16-byte prefix was implemented only for encoding 2. On the 14,432 rows with a
prefix, byte 0 is zero, not `0x78`, so zlib reported a bad header or an unknown
compression method. The failure was a framing error, not evidence of another
compression algorithm (RPF9-F152).

This explains the three observations in the previous handoff:

| Surface | Observed | Cause |
| --- | --- | --- |
| Census | `undecodable`, reason `the compressed data is invalid: deflate decompression error` | It read a 64-byte head, so it decoded chunk 0 and hit the framing error |
| Extraction | `the compressed data is invalid: deflate decompression error` | Same decoder, same prefix error |
| `archive ls` | `contents.state = "decoded"` | It built the `Payload` and validated the table's sizes, but decoded no chunk |

The string `unrecognised chunk encoding` does not occur in the current or
baseline build (commit `750db9e`). The census records the terminal state, not
that string. `archive ls` now reports `validated` for this case, and `decoded`
is reserved for a read that returned the payload (RPF9-F153).

## Decoder rules

A reader of encoding 4 MUST:

- validate the chunk table and its entries against the value pool;
- compute the stored prefix as `stored size - sum(chunk stored sizes)` and
  accept only 0 or 16;
- require the prefix and the chunk stored sizes to fit in the entry's stored
  size, and the chunk logical sizes to sum to the entry's logical size;
- for method 3, inflate exactly `stored - padding` bytes from the chunk's start,
  require end of stream, a valid checksum and output equal to the chunk's
  logical size;
- for any other method, require `stored - padding` to equal the logical size
  and copy the bytes;
- decode every chunk, including a copy chunk that is not the last one;
- skip the padding and report every failure.

Encoding 4 provides no integrity check beyond the Adler-32 of each zlib chunk.
A copy chunk has none. The 16-byte prefix is outside the decoded stream and no
checksum covers it. The metadata signature covers no payload bytes.

## Verification

Every encoding-4 entry was decoded in full through a bounded stream and hashed.
The run covered the eight nested archives that hold the entire population:
`pack/core_bvh4/core_bvh4.rpf!772`, `levels.rpf!1719`, `levels.rpf!1029`,
`levels.rpf!1806`, `levels.rpf!927`, `levels.rpf!1549`, `levels.rpf!772` and
`levels.rpf!1091`.

| Check | Result |
| --- | --- |
| Entries verified | 14,488 of 14,488 |
| Chunk table parsed | 14,488 |
| Every chunk decoded | 14,488 |
| Logical size matched | 14,488 |
| zlib checksums passed | every method-3 chunk |
| Failures | none |
| Digest of all payload digests, in chain order | `80c4ec5b0c49fd17235b93ac2568f62e467515abab70d891ac071a8bf7a76cb9` |

The 56 entries that decoded before the fix were extracted again with both
builds. All 56 produced identical bytes, and each digest matched the
verification record. The 55 `PSIN` rows and the `FORCE_EMPTY_RPF` row use no
prefix, so the change leaves their framing untouched.

The full per-entry inventory is `affected-inventory.jsonl`, beside the
verification streams in the analysis directory. It records the chain, row, type,
extension, hashes, sizes, layout, encoding, chunk count and methods, stored
prefix and bytes, digest, decoded classification and outcome for every entry.

## Census after the fix

The payload census was run again over the whole installation with the fixed
scanner, into a new checkpoint namespace. The enumeration is unchanged: 22
roots, 4,373 archives (4,351 nested), 1,255,039 entries, 46 observed type ids.
Every total reconciles and the run reports `complete: true`.

| Count | Before | After |
| --- | ---: | ---: |
| entries decoded | 1,239,857 | 1,254,289 |
| entries undecoded | 15,182 | 750 |
| `undecodable` | 14,432 | 0 |
| `blocked` | 750 | 750 |
| resource containers | 1,138,382 | 1,152,814 |
| nothing recognised | 18,229 | 3,797 |
| unresolved formats | 18,229 | 3,797 |

The 14,432 rows move from `undecodable` to `partially-identified` resource
containers. The 750 that remain undecoded are the payload-transform failures of
the separate task; no encoding-4 row is among them. The storage distribution is
unchanged (`chunked-4` is still 14,488).

No newly readable payload is an RPF9 archive: the 14,432 resource headers, the
55 `PSIN` documents and the one unrecognised payload are not archives, and the
nested archive count remains 4,351. No additional archive was opened, so the
enumeration is complete without a second descent.

The pre-fix pass's scanner was `d9620f6c…`; the post-fix pass used `ef1cde45…`.
An integrated rerun with the final build (`6560e67c…`) reproduced the same
counts; its wall clock is not quoted because an unrelated scan shared the disk.
Every journal records the scanner digest, so no run can reuse another's
checkpoints.

## External research

The awesome-gta6-reverse-engineering index was inspected for leads. The format
was established from the local archives and executable; no third-party code,
text or implementation was used.

## Open questions

- What the 16-byte prefix holds, and why 56 rows omit it. The length correlates
  with location layout R, but no field names it.
- Whether another build stores a prefix of another length, or a non-zero prefix.
- Whether an encoding-4 entry can carry the payload transform or an alternate
  read source. Neither occurs in this installation, so neither path is verified
  for this encoding.
