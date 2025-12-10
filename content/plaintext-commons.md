---
title: Plaintext Commons
date: 2025-11-04
description: "Manifesto for keeping long-form knowledge in durable, human- and agent-friendly files."
featured: true
project:
  year: 2025
  category: /project-humane
  image: /visuals/project-thumbs/proj_plaintext_commons.png
---

Plaintext Commons is the working manifesto for keeping long-form knowledge in durable, human- and agent-friendly files. It doubles as a preview of the future site at [plaintextcommons.org](https://plaintextcommons.org) and a place to gather feedback before launching a dedicated build.

## Overview

Plaintext Commons assumes the folder is the platform, the file is the protocol, and tools— including AI agents—should assist without annexing the corpus. Every component I am building, from [Arrowhead CLI](/arrowhead/) to ongoing capture tooling, lives inside that stance. The manifesto below is the current reference text I share with collaborators and will seed the upcoming repository at [totocaster/plaintext-commons](https://github.com/totocaster/plaintext-commons).

## The draft

<div class="document-draft">
PLAINTEXT COMMONS

Version 0.2 · 2025-11-28


**Premise:** Knowledge should outlast software.

**Problem:** Most modern software is cloud-first and app-centric. Each product keeps your data in its own format and database, only reluctantly offering exports and brittle imports. 

**Claim:** A single folder of plain text files you control can act as the shared, durable substrate for people, tools, and agents—a neutral commons where no app owns the data and any tool may participate.

**Consequence:** Store what matters in _plain text (Markdown or .txt)_ inside a corpus you own. Let tools come and go; the folder remains the source of truth and the bridge between them.


## Why now

For decades, software has demanded rigid, app-specific formats and server-side databases. Each tool became its own silo; connecting them meant exports, imports, and permanent friction.

At the same time, two things changed:
- **Local-first & open formats are resurfacing:** users want data that lives on their machines, in formats they can keep using even if vendors disappear. [^1]
- **Modern models read and write text directly** — and most other media can be transcribed into text. The supposed gap between “human-readable” and “machine-readable” is now mostly artificial. [^2]

Together, this makes a different architecture viable:
- **Data is stable** — plain text files in a folder you control.
- **Tools are interchangeable** — editors, CLIs, and agents operate on those files, not hidden schemas.
- **Intelligence is layered** — search, indexes, and agents understand the corpus without owning it.


## Core principles (non-negotiables)

1. **Files over apps.** Your **corpus** (a folder of open files) is the system of record.  
2. **Plain text by default.** Use Markdown or .txt; keep light metadata in _frontmatter_ (or a tiny sidecar file for .txt when necessary).  
3. **Tools assist, they don’t annex.** No tool owns the data or invents a private schema that captures it.  
4. **Writes are previewed and reversible.** Tools propose changes; you review and apply; changes have a clear _provenance trail_.
5. **Composability beats monoliths.** Many small tools on one shared corpus.  
6. **Minimum ceremony.** Conventions only where they pay for themselves (naming, links, frontmatter).  
7. **Portability and durability.** Ten years from now, the files still open and make sense.  
8. **Privacy first.** Local by default; use cloud only with explicit consent.  
9. **No exports. No migrations.** The folder *is* the platform.



## The three laws of the Commons

1. **The folder is the platform.**  
   One _corpus_—a folder of open files—acts as the system of record.

2. **The file is the protocol.**  
   Stable, human-readable _plain text (Markdown or .txt)_ with optional _frontmatter_. No opaque blobs.

3. **Writes are previewed and reviewable.**  
   Tools propose changes; you preview and accept; a simple log/history preserves *why* changes happened, not just *what* changed.



## Multi-tool by design

Different tools specialize and still cooperate because they share the same substrate:

- **Authoring** in any editor.  
- **Browsing & searching** (exploration and retrieval) via tools—indexers, embeddings, and link graphs.  
- **Scripting and automation** with scripts, CLIs or any automation tool.  
- **Organizing chores** (linking, filing, light refactors) delegated to tools or agents—without taking ownership of the data.  
- **Capture & ingestion** from email, PDFs, and transcripts—converted to text with attachments nearby.

_No exports. No migrations._



## Minimal working conventions

Keep it robust without bureaucracy:

- **Shallow corpus.** Let search, links, tags, and tools handle the heavy lifting—including organizing chores.  
- **Note schema is optional.** Zettelkasten, Fleeting/Project/Evergreen, or none—your choice.  
- **Stable filenames.** Use a simple stamp pattern (e.g., `date + slug`) if it helps.  
- **Metadata:**  
  - _Markdown:_ use frontmatter for light metadata.  
  - _.txt_: use a tiny sidecar only when needed.
- **Sync/history:** Git, cloud sync, or both—your call.


## Norms for tools (agents included)

- **Read-only by default; explicit writes.**  
- **Previewable changes with rationale.** Generate human-auditable previews before any write.  
- **Respect corpus rules.** Honor ignore lists, attachment folders, and local settings.  
- **Pipe-friendly I/O.** Text/JSON in and out; compose with other CLIs and tools.  
- **AI and agent-aware.** Expose capabilities in open, automatable ways (e.g., MCP/stdio/HTTP)—no proprietary lock-ins.  
- **No schema capture.** Indexes are caches; they are purgable and never become the source of truth.



## Adoption path (practical, not sacred)

1. **Start a corpus.** Pick a folder. Make it your system of record.  
2. **Choose light conventions.** Naming, links, and minimal front matter; stop when marginal value drops.  
3. **Add an indexer.** Turn on FTS + embeddings + backlinks; let the index come to the files, not the other way around.  
4. **Introduce a tool/agent.** Examples: [Claude Code](https://docs.anthropic.com/claude/docs/claude-code) (CLI), [Claude.ai](https://claude.ai/) or [ChatGPT](https://chatgpt.com/) (app), or [LM Studio](https://lmstudio.ai/) (local). Use open interfaces (CLI, MCP/stdio/HTTP).  
5. **Require previewable writes.** Propose → preview → apply → log.  
6. **Iterate only where it pays.** Improve naming, linking, tagging, and automation gradually.



## The Plaintext Test

Ask this before adopting a tool or workflow:

1. Can I read/edit the files with a basic text editor?  
2. Can I move the folder and keep working—no exports required?  
3. Can the tool propose a human-auditable preview of changes (with rationale) before writing?  
4. Will this still make sense in ten years?

If not, it’s not Commons-compatible.


## Industry note

This is a **design stance**, not a membership. Build tools that keep data open, changes explainable, and the folder first. Everything else is replaceable.


_The initial version of the manifesto is written by [Toto Tvalavadze](https://ttvl.co)._

[^1]: Martin Kleppmann, Adam Wiggins, Peter van Hardenberg, and Mark McGranaghan. Local-first software: you own your data, in spite of the cloud. 2019 ACM SIGPLAN International Symposium on New Ideas, New Paradigms, and Reflections on Programming and Software (Onward!), October 2019, pages 154–178. [doi:10.1145/3359591.3359737](https://doi.org/10.1145/3359591.3359737)
[^2]: Large language model (n.d.). In Wikipedia. Retrieved November 28, 2025, from [https://en.wikipedia.org/wiki/Large_language_model](https://en.wikipedia.org/wiki/Large_language_model)

</div>

## Next steps

- Collect feedback on this draft before publishing the standalone site.
- Comments, suggestions, reviews are welcome at [totocaster/plaintext-commons](https://github.com/totocaster/plaintext-commons/blob/main/MANIFESTO.md) repository for versioning.
- Publish on [plaintextcommons.org](https://plaintextcommons.org)
