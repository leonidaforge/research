# GFX* research history

## 2026-11-25: five variants and one big-endian length replace the two-form reading

The first GFX document was based on six decoded payloads. It recorded two
header forms at `+0x08` (`88 00 01 xx` and `80 00 02 xx`) and described the
first-run length as a `u16` in the `88` form and a `u8` in the `80` form. The
second printable run was placed at `+0x37` from two payloads, and 11 multi-chunk
rows were left unreconstructed.

Decoding all 49 type-66 rows in the population changes those readings:

- Five `+0x08`/`+0x0A` pairs occur, not two: `88/01`, `80/02`, `78/05`, `70/0A`
  and `70/0B`. They co-occur within one archive.
- The first-run length is a big-endian `u16` in every variant. The apparent
  `u8` was the low byte of that field; the high byte is the zero at the byte
  before it.
- The second run begins 15 bytes after the first run, not at a fixed `+0x37`.
  Its absolute offset depends on the first-run length.
- All 11 multi-chunk rows were reconstructed end to end. The decoded length
  equals the manifest logical size and the `u32` at `+0x04` in all 49 rows.
- The payload has a fixed ten-byte trailer shared by all 49 rows. The first
  document recorded only the prefix and did not inspect the end.

The corrections supersede the two-form reading in GFX-F03 of the earlier index.
The stored zlib observation, the type-66 association and the six parent archives
remain valid. Field meanings and format identity remain **Unknown**.

The findings in [INDEX.md](INDEX.md) use a new GFX-F01 to GFX-F10 numbering. The
earlier combined index used GFX-F01 to GFX-F04 for different claim boundaries,
so its IDs are not reused.

The population recount also differs from the earlier frame: the cache contains
849 unique depth-1 manifests and 183,144 row records, while the run summary
records 782 archives and 169,523 rows. The extra cached archives contain no
additional type-66 row, so the 49-row count is unchanged.
