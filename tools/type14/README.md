# Type 14 inspector

`inspect_type14.py` reports the header fields and internal tables of a decoded
type 14 payload. It prints offsets, sizes, counts and name lengths. It does not
print payload text or record identifiers.

## Usage

```sh
python tools/type14/inspect_type14.py <payload>
python tools/type14/inspect_type14.py <payload> --verify-ids
```

The input is opened read-only. Output is JSON.

## Output

- `header_u16` and `header_u32`: the first `0x2C` bytes, read at each aligned
  offset.
- `string_table`: the offset at `+0x00`, the length at `+0x0C`, the count at
  `+0x18`, and the observed string lengths.
- `record_table_candidates`: every stride from 8 to `0x80` that forms a table of
  the header count that ends at the payload end. A candidate requires a `u32` ID,
  a `u16` name length, an ASCII name and zero padding to the stride. The report
  gives record offsets and name lengths, not IDs or names.
- `checks`: comparisons between header fields and the observed tables.

## Identifier verification

`--verify-ids` prints only counts. It compares each record's `u32` identifier
with the one-at-a-time hash of the string-table entry at the same index. The
reported variants are:

- folded lower-case or case-sensitive input;
- with or without the terminating `0x00`;
- little-endian or byte-swapped output.

It also reports how many identifiers match the folded or case-sensitive hash of
the record name field. No name, hash or identifier is printed.

## Dependencies

- Python 3.11 or later, standard library only.

## Tests

```sh
python -m unittest discover -s tools/type14
```

The tests build synthetic payloads with invented strings and correctly computed
identifiers. They do not read game files.
