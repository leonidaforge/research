# Tools

No tools are published yet.

A tool added here MUST:

- be original work under the repository license,
- open game files and executables read-only and never run them,
- take every input and output path as an argument, with no default pointing at a local installation or another project,
- refuse to write output inside an input directory,
- may implement generic recognition, structural validation and local application of compatible cryptographic state from a user-provided executable,
- never print, export or persist cryptographic key material or encoded secret state,
- never embed key material, key-material locators for a specific build, or private extraction reports,
- not require an external key service or transmit key material over a network,
- fail explicitly when compatible state is missing or the build is unsupported,
- not print game data beyond what a finding needs, such as a header field or a size,
- list its dependencies with versions,
- ship tests that build synthetic inputs, so they run without game files.

Put each tool in its own directory with a short README covering usage and output format.
