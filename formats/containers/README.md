# Containers

Formats that group or index several assets or records. Each format has its own directory here, see [STRUCTURE.md](../../STRUCTURE.md#flat-container-directories).

| Format | Used for | Status |
|---|---|---|
| [RPF9](rpf9/README.md) | GTA VI archives | Metadata layout and schema addressing known. Native TOC extraction works for stored and chunked rows; rows behind the payload transform remain unsupported. |
| [RDS5](rds5/README.md) | RDS5 containers observed with the `.ttpf` extension | Header, records and ETPF extent known. zlib blocks extract; other selectors and entry meanings are unidentified. No texture decode. |
