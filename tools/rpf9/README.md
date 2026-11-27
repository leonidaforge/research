# RPF9 framing and header probes

Three bounded, read-only probes and one verification harness for RPF9 research. They read the archive they are given
and refuse every range outside that file. They refuse an `--output` that names an input
file, write through a temporary file in the target directory, and replace the
destination only after the write succeeds. They do not print payload or trailer bytes.

| Tool                        | Input                                                                       | Reports                                                                                                    |
| --------------------------- | --------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `framing_survey.py`         | one archive and a native row manifest                                       | encoding-2 prefix classes, chunk methods, decoded header classes, chunk count against declared page counts |
| `trailer_probe.py`          | one or more archives, optionally with manifests                             | `hdr[0x0C]` as a trailing length, the payload boundary, four bound checks, and trailer equality classes    |
| `secondary_probe.py`        | one or more archives                                                        | `C`, `D`, `E`, `F`, the secondary-area size, and two size-model checks                                     |
| `random_transform_tests.py` | a compatible Leonida Forge CLI, a game directory and an executable          | random transformed rows per archive, each decoded and compared with its declared logical size              |
| `census_all.py`             | a compatible Leonida Forge CLI, an installation directory and an executable | one bounded entry census per root archive, and the merged summary                                          |
| `entry_matrix.py`           | the merged census from `census_all.py`                                      | the published [entry matrix](../../formats/containers/rpf9/entry-matrix.md) and its JSON                   |

Python 3 standard library only.

## Entry census

```text
LFORGE=/path/to/lforge python tools/rpf9/census_all.py INSTALL_DIR EXECUTABLE OUTPUT_DIR [ENTRIES_PER_ROOT]
python tools/rpf9/entry_matrix.py OUTPUT_DIR/census-merged.jsonl OUTPUT_DIR
```

Every root archive gets the same entry budget, so the sample covers all roots rather
than the first archive. `census_all.py` reports how many archives and entries each run
covered and whether it stopped at a budget. `entry_matrix.py` writes `entry-matrix.md`
and `entry-matrix.json`: one row per combination of entry type, identification, storage,
transform, payload state, confidence, extension and capability, with the number of
entries, the archives it was seen in and samples that name the row and show the first
bytes of its decoded head.

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
- `raw` when the last chunk is not zlib and its stored length minus its padding equals
  the remaining logical length; padding from 0 to 15 is accepted and reported;
- `unknown` when neither condition holds or a bound stops the read.

`raw` therefore means the copy condition. The chunk method and padding bits were not
read.

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

The store starts at `align_F(hdr[0x08])`. The index-store model then needs `D * E * F`
bytes followed by an 8-aligned pool. The direct model stores values of one fixed width
in every secondary column, so the area from the store start must divide by `D * E`.
Both checks are necessary conditions only. They do not choose between the models; a
direct layout with a different width per column remains possible. The summary reports
the archives where the two size predictions differ and the archives where an observation
selects a model; without decoded secondary bytes the second count is zero. Neither
check assigns a meaning to the flag at `u8@0x2D`.

## Payload-transform verification

```text
python tools/rpf9/random_transform_tests.py LFORGE GAME_DIR EXECUTABLE [SEED]
```

The harness lists the transformed rows of every top-level `.rpf` with the
application's `archive search --transformed true`, samples them at random with a
fixed seed, extracts each with `archive extract`, and requires the output size to
equal the row's declared logical size. It reports only archive names, row
numbers, sizes and a pass count. It needs a compatible Leonida Forge CLI and the
matching executable; it does not read key material itself. `PER_ARCHIVE` sets
the sample size (default 5). This harness is separate from the synthetic unit
tests below because it needs the application and a local installation.

## Tests

```text
python -m unittest discover -s tools/rpf9 -p "test_*.py" -v
```

The tests build synthetic archives from code. They cover a 16-byte prefix with a zlib
stream, a raw chunk, a padded copy chunk, a two-part resource with a page map, a
truncated row, an output collision against each tool's input, trailer bounds, trailer
equality, the documented secondary store start, and both necessary size conditions.
