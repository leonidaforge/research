# Research policy

This document sets the method and the publication limits for this repository. It is not legal advice. Contributors are responsible for complying with the law and the license terms that apply to them.

## Inputs

- Analyze only material you can lawfully access.
- All analysis of game files and executables is read-only. Nothing is written to, renamed or deleted in a game installation.
- Proprietary inputs stay outside this repository: executables, archives, extracted assets, decompiler databases, analysis caches.
- What gets published is original work about those inputs: structural descriptions, formulas, field tables, addresses, confidence assessments and original tools.

## Confidence levels

Every significant claim carries one of these labels.

| Level | Meaning |
|---|---|
| **Confirmed** | Directly supported by verified observations, such as decompiled control flow, disassembly or data checked against samples |
| **Probable** | Strong evidence, but not fully demonstrated |
| **Speculative** | A plausible hypothesis that needs further investigation |
| **Rejected** | Contradicted by reliable evidence |
| **Unknown** | Not sufficiently investigated |

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

Cryptographic research describes architecture: where processing happens, how a cipher is selected, which spans it covers, and how failure affects loading. The repository does not publish:

- key material, key fingerprints or values derived from keys,
- descriptor values, parameters or key identifiers read from the executable,
- listings of cipher or key-lookup implementations,
- tools that search for, extract or apply keys.

## Publication-safe artifacts

Published material MUST NOT contain:

- game files, executable bytes or extracted assets,
- decompiled function bodies or long disassembly listings (short formulas and a few instructions that support a claim are acceptable),
- per-archive data dumps (aggregate observations such as value ranges are acceptable),
- private absolute paths, user names or machine-specific configuration,
- code from external projects whose license does not allow reuse.

If it is unclear whether something is safe to publish, leave it out and raise it in the pull request.

## Tools and fixtures

Tools in `tools/` are original work under the repository license. They read inputs read-only, take paths as arguments and write outputs outside the input directories. Tests use synthetic data built by the tests or committed as small authored fixtures.

## External references

Third-party projects, such as tools for earlier RAGE formats, are read-only references unless their license permits reuse. Comparing architecture with them is fine. Their source, embedded keys and data are not copied. When a comparison relies on a third-party source, attribute it and treat it as a comparison, not as evidence about GTA VI.
