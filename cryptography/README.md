# Cryptography

Research into how GTA VI selects and applies ciphers, verifies integrity and references keys. Format documents link here and do not repeat it.

The section documents architecture only. [RESEARCH-POLICY.md](../RESEARCH-POLICY.md#cryptographic-research) defines the boundary: algorithms, formats and provider contracts are publishable; key material, encoded secret states, direct key-material locators and private extraction reports are not.

## Organization

- One directory per format whose processing has been researched, such as `rpf9/`.
- Mechanisms used by more than one format, such as a shared algorithm factory or key lookup, get their own document at this level once two formats are shown to use them.

| Subject | Content |
|---|---|
| [rpf9](rpf9/README.md) | Archive metadata processing during validation |
