# RBF0 token parser

`rbf0_inspect.py` parses one RBF0 payload with the grammar documented in [formats/metadata/rbf0](../../formats/metadata/rbf0/README.md). It reports the header variant, token counts, value widths and name-definition hashes. It does not print names or text values.

## Usage

```text
python tools/rbf0/rbf0_inspect.py <payload> [--json] [--max-depth 256]
```

The input path is required. The tool opens it read-only and writes nothing. `--max-depth` bounds element nesting.

## Output

Text output reports:

- payload size, header variant, version, number width and token start;
- element, attribute, text-node, name-definition and maximum-depth counts;
- value counts per type code;
- every name definition with its offset, name index, name length and SHA-256.

`--json` emits the same report as a JSON object. A failed parse reports the first failing offset and the token class, such as `truncated_token`, `name`, `text`, `value_6`, `unterminated`, `unsupported_type_7`, `trailing` or `magic`.

## Exit codes

| Code | Meaning |
| ---- | ------- |
| 0 | Parsed to the end with no unsupported token |
| 1 | Input could not be read |
| 2 | Structural or token error; details are in the report |

## Grammar support

- Versioned header `RBF0` + `0xFFFB` + `u16` version, token stream at `+0x08`, 8-byte numbers.
- Versionless header `RBF0`, token stream at `+0x04`, 4-byte numbers.
- Global per-document name table with definition on first use.
- Type 0 elements with `u32` reserved word and `u16` attribute count.
- Attribute tokens with type codes 1 to 6.
- Value widths: type 1 and 4 use the document number width; types 2 and 3 are zero bytes; type 5 is 12 bytes; type 6 is `u16` length plus bytes.
- Text token `0xFFFD` with `u32` length.
- Close token `0xFFFF`.

Token types 7 to 14 are reported as unsupported errors. The parser does not skip them.

## Tests

```text
python -m unittest discover -s tools/rbf0 -p "test_*.py"
```

`tools/rbf0/synthetic.py` writes the synthetic fixtures used by the tests:

```text
python tools/rbf0/synthetic.py <output-directory>
```

The fixtures cover versioned and versionless documents, every value type, a text node, nested elements and each malformed case. They contain no game files.

## Limits

The width table is observed data, not a semantic model. Type 5 has one observation, types 2 and 3 have 21, and field-position type 6 is unobserved. The tool does not establish field meanings, the purpose of the document or whether the name set identifies a schema.
