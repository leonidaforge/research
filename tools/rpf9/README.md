# RPF9 framing and header probes

Three bounded, read-only tools for RPF9 research. They read the archive they are given
and refuse every range outside that file. They do not print payload or trailer bytes.

| Tool | Input | Reports |
| --- | --- | --- |
| `framing_survey.py` | one archive and a native row manifest | encoding-2 prefix classes, chunk methods, decoded header classes, chunk count against declared page counts |
| `trailer_probe.py` | one or more archives, optionally with manifests | `hdr[0x0C]` as a trailing length, the payload boundary, four bound checks, and trailer equality classes |
| `secondary_probe.py` | one or more archives | `C`, `D`, `E`, `F`, the secondary-area size, and two size-model checks |

Python 3 standard library only.

## Framing survey

```text
python tools/rpf9/framing_survey.py --archive ARCHIVE --manifest MANIFEST.json
```

The manifest is the JSON written by the application's native manifest command. A row
is surveyed only when its chunk table has encoding 2. Every stored range is checked
against the archive size. Chunk reads are bounded by the row's stored range and
`--max-row-bytes`; decoded output is bounded by `--max-output`. Rows carrying the
payload transform are counted but not decoded. The summary contains counts only, not
row bytes or archive paths.

Chunk methods are classified structurally:

- `zlib` when the chunk starts with a valid zlib header and inflates;
- `raw` when the last chunk is not zlib and its stored length equals the remaining
  logical length;
- `unknown` when neither condition holds or a bound stops the read.

`raw` therefore means the copy condition. The chunk method bits were not read.

## Trailer probe

```text
python tools/rpf9/trailer_probe.py ARCHIVE [ARCHIVE ...]
```

The declared trailing length is `u32@0x0C`; the payload boundary is
`file_size - length`. The probe checks that the boundary is 16-byte aligned, lies above
the metadata end, lies below the file size, and, when a manifest is supplied, is at or
above every row's stored end. Equality classes compare trailer bytes in memory and
report only `equal_first_16`, `equal_first_32` and `equal_full`. Trailer bytes and
digests are not printed.

## Secondary probe

```text
python tools/rpf9/secondary_probe.py ARCHIVE [ARCHIVE ...]
```

The index-store model needs `D * E * F` bytes rounded up to 8 before the pool. The
direct model stores values of one fixed width in every secondary column, so the
secondary area must divide by `D * E`. Both are reported as fits or non-fits; neither
assigns a meaning to the flag at `u8@0x2D`.

## Tests

```text
python -m unittest discover -s tools/rpf9 -p "test_*.py" -v
```

The tests build synthetic archives from code. They cover a 16-byte prefix with a zlib
stream, a raw chunk, a two-part resource with a page map, a truncated row, trailer
bounds, trailer equality, and both secondary size models.
