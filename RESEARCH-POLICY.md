# Research policy

This document sets the method and the publication limits for this repository. It is not legal advice. Contributors are responsible for complying with the law and the license terms that apply to them.

## Inputs

- Analyze only material you can lawfully access.
- All analysis of game files and executables is read-only. Nothing is written to, renamed or deleted in a game installation.
- Proprietary inputs stay outside this repository: executables, archives, extracted assets, decompiler databases, analysis caches.
- What gets published is original work about those inputs: structural descriptions, formulas, field tables, addresses, confidence assessments and original tools.

## Confidence levels

Every significant claim carries one of these labels.

| Level           | Meaning                                                                                                                   |
| --------------- | ------------------------------------------------------------------------------------------------------------------------- |
| **Confirmed**   | Directly supported by verified observations, such as decompiled control flow, disassembly or data checked against samples |
| **Probable**    | Strong evidence, but not fully demonstrated                                                                               |
| **Speculative** | A plausible hypothesis that needs further investigation                                                                   |
| **Rejected**    | Contradicted by reliable evidence                                                                                         |
| **Unknown**     | Not sufficiently investigated                                                                                             |

A confirmed mechanism can still have field meanings that are only probable. State the level for each part separately.

Names such as "value pool" or "file-object tag" are descriptive labels chosen by researchers. They are not recovered symbol names unless a document says so with evidence.

## Evidence quality

- Decompiler output is an interpretation. Check it against disassembly, data access patterns and independent observations where possible.
- Byte-pattern scans and string hits are leads, not proof of a call graph or an algorithm.
- Observations from real data, such as layout arithmetic checked against archives, have to state what was checked and what was not.
- Similarity to RPF7 or RPF8 is a comparison, not evidence that GTA VI behaves the same way.

## Build-specific findings

Addresses only apply to the executable they came from. Every build-specific finding records the executable SHA-256, the image base and the RVA. Format documents describe behavior. They cite build catalog entries and do not embed addresses.

## Uncertain and corrected interpretations

- Unknown fields stay in the tables and are marked **Unknown**.
- When sources conflict, document the better-supported interpretation, and record the conflict if it remains open.
- Corrected interpretations leave the specification. The research history keeps one entry per meaningful correction.

## Cryptographic research

Cryptographic research may describe algorithms, format structures, initialization and validation contracts, and the general key-provider architecture. This supports open-source interoperability and generic recognition of compatible data in a user-provided executable.

### Permitted public research

- Algorithms and mathematical descriptions, including synthetic test vectors and original tests.
- File-format structures, metadata semantics, descriptor layouts and selection behavior.
- Cryptographic initialization, validation and failure contracts.
- General key-provider architecture, record layouts and provider-selection behavior.
- Generic structural recognition methods, validators and format constants.
- Build-specific addresses for ordinary format-processing functions, including cipher block operations, signature verification and parser code.
- Publicly reproducible, nonsecret analysis.

### Kept out of this repository

- Actual cryptographic key material or encoded secret states, and dumps derived from them.
- Proprietary executable bytes and extracted secret tables.
- Direct addresses or RVAs that point to embedded key-material storage.
- Direct maps from executable-specific cryptographic key identifiers to key-material locations.
- Key-material fingerprints or hashes used primarily to identify stored secrets.
- Private extraction reports and executable-derived secret-state dumps.
- Machine-specific paths, configurations and local analysis artifacts.
- Long decompiler listings or copied proprietary code.

### Distinctions

- The word `key` is not by itself a secret. RPF9 schema field keys, name hashes, archive identifiers and metadata keys are ordinary format data and may be documented.
- A generic recognition algorithm is publishable even if it can locate compatible state in a user-provided executable. What stays private is a ready-made address map or extraction report for one build's secret storage.
- Build-specific addresses of ordinary processing functions are publishable. Addresses of key-material storage are not.
- Concrete executable-specific cryptographic key identifiers may be described only as part of general selection behavior. They MUST NOT be published together with a key-material location or a direct identifier-to-location mapping.
- A public recognizer cannot promise to conceal how it works. Secrecy through code obfuscation is not a goal. The goal is to avoid distributing proprietary material and unnecessarily convenient build-specific key-location references.

Public research MUST remain compatible with automatic local recognition. It MUST NOT require a mandatory private build profile or a manually entered key-storage address. A recognizer may use generic structural checks against a user-provided executable, MUST verify build compatibility, and MUST fail explicitly when no compatible state is found. Published tools MUST NOT bundle key material, require an external key service or transmit key material over a network.

### Evidence and reproducibility

Every public finding states one of these:

| Label                          | Meaning                                                                                                                                  |
| ------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------- |
| **Publicly reproducible**      | Checkable from this repository and synthetic inputs alone                                                                                |
| **Private-evidence supported** | Verified against restricted local evidence; the public text states the conclusion and the dependency without the locator or secret bytes |
| **Not demonstrated**           | A hypothesis or an incomplete result                                                                                                     |

Private-evidence findings may cite stable opaque evidence IDs. They MUST NOT be described as independently reproducible from this repository alone. The repository does not include the private locators or secret state needed to repeat them.

This section supersedes older blanket exclusions of descriptor values and key identifiers. Descriptor structure and selection behavior are publishable. Direct key-material locators and concrete key-identifier-to-location maps are not.

## Publication-safe artifacts

Published material MUST NOT contain:

- game files, executable bytes or extracted assets,
- decompiled function bodies or long disassembly listings (short formulas and a few instructions that support a claim are acceptable),
- per-archive data dumps (aggregate observations such as value ranges are acceptable),
- private absolute paths, user names or machine-specific configuration,
- code from external projects whose license does not allow reuse.

If it is unclear whether something is safe to publish, leave it out and raise it in the pull request.

## Name and hash mappings

A factual mapping between a format's documented name hash and a candidate
filename is not a payload copy. Publishing such mappings supports
interoperability and is permitted when each record is:

- hash-validated with the published algorithm and namespace;
- accompanied by its provenance at the level required for the finding;
- marked as a candidate unless the original name is independently established;
- free of private paths, user names, credentials and cryptographic material.

The public LUT files under `names/` are mapping data only. They MUST NOT be used
to publish bulk extracted strings, readable payload text, executable byte
ranges or unrelated embedded data. A 32-bit match is weaker than a 64-bit one
and MUST NOT be presented as proof of original identity. Different names for
one hash stay separate and ambiguous; the format does not pick a winner.

When a discovered mapping's provenance raises a licensing or publication
concern, keep it in local analysis and report the concern instead of publishing
it. A mapping that is safe to publish does not make the payload it came from
safe to publish.

## Tools and fixtures

Tools in `tools/` are original work under the repository license. They read inputs read-only, take paths as arguments and write outputs outside the input directories. Tests use synthetic data built by the tests or committed as small authored fixtures.

## External references

Third-party projects, such as tools for earlier RAGE formats, are read-only references unless their license permits reuse. Comparing architecture with them is fine. Their source, embedded keys and data are not copied. When a comparison relies on a third-party source, attribute it and treat it as a comparison, not as evidence about GTA VI.
