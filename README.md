# Leonida Forge Research

Technical research into GTA VI file formats, cryptographic architecture and engine internals.

This repository holds the knowledge base behind [Leonida Forge](https://github.com/leonidaforge/leonida-forge), the GTA VI research and modding toolkit. The application implements what is documented here. This repository records what is known, how it is known, and what is still open.

## Scope

- GTA VI only. The behavior of earlier RAGE formats such as RPF7 and RPF8 is not assumed to carry over.
- Format specifications, cryptographic architecture, engine mechanisms and build-specific executable observations each have their own section. See [STRUCTURE.md](STRUCTURE.md).
- Every significant claim carries a confidence level and links to its evidence.

## Research status

| Subject | Status | Entry point |
|---|---|---|
| RPF9 header and metadata layout | Layout and region boundaries established through static analysis | [formats/containers/rpf9](formats/containers/rpf9/README.md) |
| RPF9 columnar schema | Cell addressing confirmed. Most column identities unknown | [schema.md](formats/containers/rpf9/schema.md) |
| RPF9 entries and names | Entry IDs and name lookup confirmed. Directory hierarchy unknown | [entries.md](formats/containers/rpf9/entries.md), [names.md](formats/containers/rpf9/names.md) |
| RPF9 payloads | Engine read path partly traced. Storage layout known only from observed data | [payloads.md](formats/containers/rpf9/payloads.md) |
| RPF9 cryptography | Encoded AES-256 decryption and RSA signature scheme confirmed. Registry and static descriptor recognition verified for e95020b2; key supply embedded; archive binding and cross-build behavior open | [cryptography/rpf9](cryptography/rpf9/README.md) |

Native RPF9 table-of-contents extraction is not possible yet. The blockers are listed in the [RPF9 overview](formats/containers/rpf9/README.md#blockers-for-native-toc-extraction).

## Navigating the repository

- [formats/](formats/README.md): binary structures and parsing rules.
- [cryptography/](cryptography/README.md): cipher selection, processing spans, integrity.
- [engine/](engine/README.md): runtime mechanisms shared by several formats.
- [builds/](builds/README.md): function addresses and object layouts tied to one executable.
- [evidence/](evidence/README.md): sources, finding index and research history.
- [tools/](tools/README.md): requirements for research tools.

## Confirmed and open findings

Specifications use five confidence levels, defined in [RESEARCH-POLICY.md](RESEARCH-POLICY.md#confidence-levels). A **Confirmed** statement is directly supported by code or data. **Probable** and **Speculative** statements are interpretations and say so. Fields nobody has explained are marked **Unknown** in the tables rather than left out. Interpretations that turned out wrong are kept out of the specifications and recorded in the [research history](evidence/rpf9/research-history.md).

## Why there is no game data here

The repository holds original descriptions, formulas and tools only. It contains no game executables, archives, extracted assets, cryptographic key material or decompiled code. Most findings can be checked from the documents and synthetic tests. Findings that depend on restricted private evidence say so and are not independently reproducible from this repository alone. The license below covers the project's own contributions. It grants no rights to Rockstar Games or Take-Two Interactive material. See [RESEARCH-POLICY.md](RESEARCH-POLICY.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## AI Contributions

**AI-enabled, not AI-driven.**

We welcome the use of AI as a development tool, but contributors are expected to understand, review, and take responsibility for their work.

AI-generated code is not inherently a problem. Unreviewed, untested, or poorly understood code is.

- Understand the code you submit and be able to explain your changes.
- Review and test AI-assisted contributions before submitting them.
- Follow existing conventions instead of introducing unnecessary abstractions, boilerplate, or documentation.
- Keep pull requests focused, maintainable, and backed by actual effort.

Low-effort, AI-generated pull requests submitted without meaningful human review or validation will be rejected.

**AI can assist your work. It should not replace your judgment.**

## License

Leonida Forge is licensed under the GNU General Public License v3.0 or later (`GPL-3.0-or-later`). See [LICENSE.md](LICENSE.md).

## Disclaimer

Leonida Forge is an independent, unofficial community project and is not affiliated with or endorsed by Rockstar Games or Take-Two Interactive.

Grand Theft Auto and related trademarks belong to their respective owners.
