# Metadata

Structured data encodings, such as schema-driven documents or serialized records. Each format has its own directory.

| Format                 | Identification    | Status                                                                 |
| ---------------------- | ----------------- | ---------------------------------------------------------------------- |
| [RBF0](rbf0/README.md) | ASCII `RBF0` at 0 | Header, object body, field dictionary and observed value forms known |
| [PSIN `LSCH`](psin/README.md) | ASCII `PSIN` at 0, first section `LSCH` | Schema, instance blocks, references, arrays, maps and enums decoded; field meanings unknown |

The `PSIN` framing for both of its families is documented under [unknown/psin](../unknown/psin/README.md).
