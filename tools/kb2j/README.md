# KB2 header inspector

`kb2_probe.py` inspects an extracted `KB2j` or `KB2n` payload. It reads the
48-byte header, optional audio descriptors, the frame index table and, on
request, the leading audio records of every frame. It does not decode frames,
decode audio or read archive files.

## Usage

```sh
python tools/kb2j/kb2_probe.py <PAYLOAD> [<PAYLOAD> ...] [--json] [--strict] [--validate]
python tools/kb2j/kb2_probe.py <PAYLOAD> --validate --output <REPORT>
```

| Option | Meaning |
| --- | --- |
| `--json` | Write one JSON object, or an array for several payloads |
| `--strict` | Exit non-zero when a structural validation fails |
| `--validate` | Walk the leading audio record of each frame without reading packet data |
| `--max-table-bytes N` | Refuse frame tables larger than `N` bytes (default 8 MiB) |
| `--max-frames N` | Stop frame validation after `N` frames (default 1,000,000) |
| `--output PATH` | Write atomically to `PATH` instead of standard output |

Inputs are opened read-only. `--output` refuses a path inside an input
directory. The tool refuses payloads shorter than the header, payloads that
declare zero frames, payloads whose frame table runs past the file, unsupported
signatures, audio track counts above 64 and frame tables above the limit.

## Output

The report includes the signature, declared size, frame count, largest frame
size, dimensions, frame rate, the `u32` flags word at `+0x24`, the audio-track
descriptors and the frame index table.

Validation flags:

- size field plus 8 equals the file size,
- the frame count equals its duplicate at `+0x10`,
- table entries are non-decreasing before and after masking bit 0,
- the first entry equals the table end plus one,
- masking bit 0 of the first entry gives the table end,
- the last entry equals the file size and has bit 0 clear,
- every masked entry lies between the table end and the file size,
- no masked frame interval exceeds the largest frame size,
- every audio track id lies in `0..n-1` and the ids are distinct.

With `--validate`, the tool also reads the record headers at each frame start:

- each track contributes `u32 record_bytes`,
- a nonzero record is followed by `u32 decoded_bytes` and `record_bytes - 4`
  bytes of packet data,
- a zero `record_bytes` is a four-byte empty record,
- the next track record follows immediately after the previous packet.

The audio report states the frame count, nonzero and zero packet counts, the
largest record and decoded byte counts, whether array 1 equals the largest
decoded count, and every record that crosses a frame boundary. Packet bytes are
never read or printed.

A false flag is reported but does not fail the command unless `--strict` is set.
Unrecognized or malformed payloads always fail.

## Dependencies

- Python 3.11 or later, standard library only.

## Tests

```sh
python -m unittest discover -s tools/kb2j -p "test_*.py"
```

The tests build synthetic headers, frame tables and audio records in temporary
directories. They do not read game files.
