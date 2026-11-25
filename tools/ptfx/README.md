# PTFX text structure inspector

`inspect_ptfx.py` describes the line structure of a decoded PTFX payload. It
prints offsets, lengths, delimiters and character classes. It does not print key
or value text.

## Usage

```sh
python tools/ptfx/inspect_ptfx.py <payload>
```

The input is opened read-only. Output is JSON.

## Output

- `byte_counts`: CR, LF, CRLF, NUL and non-text byte counts.
- `first_bytes`: the first four bytes as hexadecimal. A PTFX payload begins
  `50 54 46 58`.
- `non_text_offsets`: up to eight offsets of bytes outside printable ASCII,
  CR and LF.
- `document`: record counts, blank-record count, final blank line and the field
  delimiter when every non-empty record has two fields.
- `records`: per-record offset, content length, CRLF termination, field count,
  key length, value length, key segment lengths and character-class checks. Key
  and value bytes are not included.
- `checks`: byte-level and grammar-level observations, including whether the
  first key segment is the PTFX label, whether line endings are CRLF only,
  whether every non-empty record has two fields, and whether keys and values fit
  the observed character classes.

A `records` entry with `empty: true` is a blank line, not a record with an empty
key.

## Dependencies

- Python 3.11 or later, standard library only.

## Tests

```sh
python -m unittest discover -s tools/ptfx
```

The tests build synthetic payloads and do not read game files.
