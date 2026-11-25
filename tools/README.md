# Tools

- [inventory](inventory/README.md): recursive, content-addressed RPF9
  inventory sampler.
- [SGD5 structural sampler](sgd5/README.md): reports the observed SGD5 header,
  table blocks and data-region prefix.
- [rbf0](rbf0/README.md): structural inspector for RBF0 payloads.
- [PSIN structural sampler](psin/README.md): reports the observed PSIN header
  and tagged-section walk.
- [ptfx](ptfx/README.md): line-structure inspector for a decoded PTFX payload.
- [type14](type14/README.md): header and table inspector for a decoded type 14
  payload.
- [kb2j](kb2j/README.md): bounded `KB2j`/`KB2n` header and frame-table
  inspector.
- [resources](resources/README.md): RAGE resource page and pointer inspector.
- [drawables](drawables/README.md): bounded drawable, LOD, geometry and material inspector.
- [adat](adat/README.md): ADAT header and chunk-table inspector.
- [GFx container inspector](gfx/README.md): identifies the `GFX` container, checks the internal length and walks the tag stream with a depth bound.
- [RDS5 structural parser](rds5/README.md): bounds-checked RDS5/ETPF reader for storage classes, descriptor fields and capped block reconstruction.

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
