# RBF0 inspector

`rbf0_inspect.py` reports the structure of one RBF0 payload. It implements the grammar documented in [formats/metadata/rbf0](../../formats/metadata/rbf0/README.md).

The tool prints offsets, tags, widths, counts and name hashes. It does not print field names or text values.

## Usage

```text
python tools/rbf0/rbf0_inspect.py <payload> [--json]
```

The input path is required. The tool opens it read-only and writes nothing.

## Output

Text output reports:

- payload size and header fields,
- object, field, attribute, string and fixed 8-byte counts,
- each unsupported header marker, value tag or field identifier with its file offset.

`--json` emits the same report as a JSON object. The `definitions` list records each field identifier when its name is first defined: the offset of the name-length word, the identifier, the high-nibble group, the low 12-bit slot, the name length and the name SHA-256.

## Exit codes

| Code | Meaning                                                         |
| ---- | --------------------------------------------------------------- |
| 0    | Parsed with no unsupported tag and no structural error          |
| 1    | Input could not be read                                         |
| 2    | Unsupported tag or structural error; details are in the report  |

## Supported forms

- Header marker `0xFFFB` and header value `1`.
- Object body with `u32` reserved word, `u16` attribute count and `u16 0xFFFF` terminator.
- Object fields `0x0001` and `0x0002`.
- String fields `0x0004` to `0x000A` with value tag `0xFFFD`, NUL-terminated bytes and `u16 0xFFFF` value terminator.
- Attribute fields `0x6003` and `0x6004` in the counted attribute position.
- Fixed 8-byte field `0x1006`.

Any other identifier, value tag or header marker is reported as unsupported, including field identifiers `0x000B` to `0x5FFF` that have the string value shape. An attribute identifier in the field stream is also reported as unsupported because attribute position is unresolved. A nonzero reserved word or value header is reported without stopping the parse.

## Dependencies

Python 3.11 or later, standard library only.

## Tests

```text
python -m unittest discover -s tools/rbf0 -p "test_*.py"
```

The tests build synthetic RBF0 payloads. They do not use game files.

## Limits

The tool encodes only the forms observed in 18 rows from one nested archive. It does not establish field semantics, the meaning of the header words or the meaning of the high-nibble groups beyond the observed encodings.
