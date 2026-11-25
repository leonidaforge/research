# Contributing

Contributions are welcome if they can be checked. Read [RESEARCH-POLICY.md](RESEARCH-POLICY.md) first. It defines the confidence levels and what may be published.

## Technical claims

- Back every significant claim with evidence and add it to the subject's evidence index, for example [evidence/rpf9/INDEX.md](evidence/rpf9/INDEX.md).
- Identify the build. Give the executable SHA-256, image base and RVAs for anything that depends on an executable location. A `RUNTIME` finding records the executable SHA-256 only and does not invent an RVA. Key-material locators stay private; cite an opaque evidence ID and mark the dependency instead.
- Describe the method well enough to repeat it: tool and version, function RVA, the samples checked and what the check covered.
- Label confidence. Never promote a probable interpretation to confirmed without new evidence.
- Keep unknown fields in tables as **Unknown**. Do not fill gaps with guesses.
- Cite external sources, including other research projects, by name and with a link when one exists.

A plausible-looking format description without evidence will not be merged.

## Corrections

To correct an existing specification:

1. Show the evidence that contradicts it.
2. Update the specification and the affected evidence index entries.
3. Add one entry to the subject's research history: what was believed, what replaced it, and why.

## Tools and fixtures

Tools follow the requirements in [tools/README.md](tools/README.md). Tests and fixtures use synthetic data only.

## AI assistance

The [AI Contributions](README.md#ai-contributions) policy covers research and documentation as well as code. You are accountable for every claim you submit, including claims an assistant drafted. Check AI-produced interpretations of decompiler output against the code before submitting them.

## Changes

- Keep pull requests focused on one subject.
- Validate relative Markdown links and any JSON before submitting.
- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/), for example `docs(rpf9): document descriptor field at +0x08`.
