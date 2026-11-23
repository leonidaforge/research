# Tools

No tools are published yet.

A tool added here MUST:

- be original work under the repository license,
- open game files and executables read-only and never run them,
- take every input and output path as an argument, with no default pointing at a local installation or another project,
- refuse to write output inside an input directory,
- never search for, read, print or apply cryptographic keys,
- not print game data beyond what a finding needs, such as a header field or a size,
- list its dependencies with versions,
- ship tests that build synthetic inputs, so they run without game files.

Put each tool in its own directory with a short README covering usage and output format.
