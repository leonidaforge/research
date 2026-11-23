# Repository structure

Each mechanism is documented once, in the section that owns it. Other sections link to it.

## Sections

| Directory | Holds | Does not hold |
|---|---|---|
| `formats/` | On-disk structures, field tables, encoding rules, parsing behavior | Function addresses, cipher internals, research narrative |
| `cryptography/` | Cipher selection, processing spans, integrity and authentication, key-management architecture | Key material, cipher implementation listings |
| `engine/` | Runtime mechanisms that more than one format uses, such as name dictionaries or device abstractions | Behavior used by a single format, which stays with that format |
| `builds/` | RVAs, vtables, object layouts and function roles for one identified executable | Format rules that do not depend on the build |
| `evidence/` | Source list, finding index and research history per subject | Raw reports, decompiler output, game data |
| `tools/` | Original, publishable research tools and their synthetic fixtures | Private scripts, anything that reads or exports keys |

A format document says *what* the structure is. The build catalog says *where* in one executable the evidence was found. The evidence index connects the two. Format documents cite findings by ID, such as `RPF9-F07`, and do not repeat addresses.

## Formats

`formats/` is split by category. Create a category only when the first format in it has researched content.

| Category | Content |
|---|---|
| `containers/` | Formats that group or index several assets or records: archives, dictionaries, banks |
| `resources/` | RAGE resource serialization: segments, pages, pointers |
| `textures/` | Texture pixel formats and compression |
| `models/` | Geometry and model encodings |
| `animations/` | Clip and animation encodings |
| `audio/` | Audio sample and stream encodings |
| `scripts/` | Script bytecode and script containers |
| `metadata/` | Structured data formats such as PSO or XML schemas |

Only `containers/` exists so far.

### Flat container directories

Each container format gets one directory directly under `formats/containers/`, named after the format:

```text
formats/containers/rpf9/
```

Archive versions are separate formats with no shared parent directory such as `rpf/`. Concepts that several containers share go into a Markdown file in `formats/containers/`.

### Containers and encodings

A container groups or indexes data. An encoding describes how one asset or value is represented. One file can involve several layers. A texture dictionary is a container, it is serialized as a RAGE resource, and its pixels use a texture encoding. Document each layer in its own category and link between them. For example, an RPF9 archive stores RAGE resources. The archive storage belongs in `containers/rpf9/`. The resource page layout belongs in `resources/` once there is code-level evidence for it.

## Adding research

1. Find the section that owns the mechanism. Extend the existing document before creating a new one.
2. Add the findings to the subject's `evidence/<subject>/INDEX.md` and cite their IDs.
3. Put addresses into the build catalog, not into format documents.
4. If a finding corrects an earlier one, fix the specification and add one entry to the research history.

Do not create directories or files for formats that have not been researched.
