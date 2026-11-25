# KB2 header inspector

`kb2_probe.py` inspects an extracted `KB2j` or `KB2n` payload. It reads the
48-byte header, optional audio descriptors and the frame index table. It does
not decode frames and does not read archive files.

## Usage

```sh
python tools/kb2j/kb2_probe.py <PAYLOAD> [<PAYLOAD> ...] [--json] [--strict]
```

| Option | Meaning |
| --- | --- |
| `--json` | Write one JSON object, or an array for several payloads |
| `--strict` | Exit non-zero when a structural validation fails |
| `--max-table-bytes N` | Refuse frame tables larger than `N` bytes (default 8 MiB) |

Inputs are opened read-only. The tool writes nothing except standard output and
errors. It refuses payloads shorter than the header, payloads that declare zero
frames, payloads whose frame table runs past the file, unsupported signatures,
and frame tables above the limit.

## Output

The report includes the signature, declared size, frame count, largest frame
size, dimensions, frame rate, the unexplained header fields, the audio-track
descriptors and the frame index table.

Validation flags:

- size field plus 8 equals the file size,
- the frame count equals its duplicate at `+0x10`,
- table entries are non-decreasing,
- the first entry equals the table end plus one,
- the last entry equals the file size,
- no frame interval exceeds the largest frame size.

A false flag is reported but does not fail the command unless `--strict` is set.
Unrecognized or malformed payloads always fail.

## Dependencies

- Python 3.11 or later, standard library only.

## Tests

```sh
python -m unittest discover -s tools/kb2j
```

The tests build synthetic headers and tables in temporary directories. They do
not read game files.
