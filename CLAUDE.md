# Leonida Forge Research

This repository documents verified technical research into GTA VI, RAGE file formats, cryptographic architecture, and related engine internals.

It is a public research repository, not the Leonida Forge application.

## Documentation and research quality

- Prefer verified technical findings over documentation about the research process.
- Keep documentation minimal, factual, useful, and evidence-driven.
- Create documentation files only when explicitly requested or required to explain a researched format, mechanism, or finding.
- Do not create ADRs, implementation summaries, phase reports, progress logs, or planning documents by default.
- Do not document obvious details or repeat information already explained elsewhere.
- Use the root README for essential project information and navigation.
- Document complex behavior in the relevant format, cryptography, engine, or build-specific document.
- Update existing documentation instead of creating new files when the subject already has an appropriate home.
- Do not repeat the same information across multiple files.
- Treat Git history, issues, and pull requests as the record of repository development.
- Keep code comments minimal. Explain non-obvious behavior, constraints, and workarounds.
- Avoid speculative abstractions, placeholder implementations, empty directories, and unnecessary boilerplate.
- Before finishing, remove redundant comments, unused abstractions, and documentation that adds no practical value.
- Report task results in the final response, not in committed progress or implementation reports.

Write documentation for developers and researchers who need to understand, verify, or implement the documented mechanisms, not to demonstrate that work was completed.

## Project rules

- Leonida Forge Research targets GTA VI. Historical RAGE formats may be referenced for comparison, but their behavior must not be assumed to apply to GTA VI.
- Treat GTA VI file formats, cryptography, resource structures, natives, scripts, and engine internals as unknown until supported by evidence.
- Never invent format details, archive entries, field meanings, function relationships, decoded names, or research results.
- Distinguish confirmed observations, probable interpretations, speculative hypotheses, rejected assumptions, and unknowns.
- Significant technical claims must be traceable to supporting evidence.
- Separate general format knowledge from build-specific executable observations.
- Document build fingerprints and RVAs when a finding depends on a specific executable.
- Do not treat decompiler output as infallible. Validate interpretations against control flow, data access, and independent observations when possible.
- Keep corrected or superseded interpretations out of current specifications. Preserve meaningful corrections in research history.
- Keep cryptographic research in the cryptography section, with links from the affected format documents.
- Never copy proprietary game files, executables, resource dumps, extracted keys, or license-restricted third-party implementation code into this repository.
- Treat external source repositories as read-only references unless their licensing explicitly permits reuse.
- Use synthetic data for tests and fixtures. Never commit game files or data extracted from them.
- Research tools must accept configurable paths. Do not hardcode private local game installations or executable locations.
- All research operations on original game files must be read-only. Never write to, rename, or delete source game files.
- Do not include private absolute filesystem paths in public documentation.
- Keep the repository independently usable without access to the original proprietary research inputs.
- Do not create empty directories or placeholder documents for formats that have not been researched.
- Keep documentation in English.
- Preserve the mandatory AI Contributions, License, and Disclaimer sections in the root README.
- The repository uses GPL-3.0-or-later, with the complete license text in LICENSE.md.
- Before committing, validate Markdown links, structured data, evidence references, and applicable tests.
- Commit messages follow Conventional Commits.
- Do not commit or push automatically unless explicitly instructed.
