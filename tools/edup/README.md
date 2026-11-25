# EDUP inspector

`edup_inspect.py` reports the EDUP layout, the two entry fields as counts and an optional membership test against local RDS5/ETPF texture stores. It reads each input read-only, never prints key values or payload bytes, and does not decode the trailing blob.

## Usage

```sh
python tools/edup/edup_inspect.py <SAMPLE> [<SAMPLE> ...]
python tools/edup/edup_inspect.py <SAMPLE> [...] --store <TTPF> [--store <TTPF> ...]
python tools/edup/edup_inspect.py <SAMPLE> [...] --store-dir <DIRECTORY>
python tools/edup/edup_inspect.py <SAMPLE> [...] --json
```

All paths are required. The tool has no default pointing at a game installation. `--max-bytes` bounds an EDUP sample; store files are never loaded whole. The store reader bounds the descriptor count and the key-table size before reading.

## Output

- Input size and SHA-256.
- Count, table end, blob length and the `size = 8 + 16 × count + 4 + length` result.
- Distinct first-field keys, distinct second-field keys, repeat counts and the largest repeat group.
- Whether any entry has equal fields, whether the two key sets are disjoint, and the set differences.
- With `--store` or `--store-dir`: store count, key count, union size, first-field hits, second-field hits and the direction classification.

The tool never prints a key value, a store key value or payload text.

## Tests

```sh
python -m unittest discover -s tools/edup
```

`tools/edup/synthetic.py` writes the synthetic fixtures:

```sh
python tools/edup/synthetic.py <output-directory>
```

The fixtures include an EDUP table with repeated second-field keys, an empty table and a minimal RDS5/ETPF store. They contain no game content.

## Limits

- The store test covers the key tables of the supplied stores only.
- An unresolved direction is reported as unresolved; the tool does not guess.
- The trailing blob is not decoded.
- Key values are not published.
