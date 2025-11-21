---
title: Plaintext Commons
date: 2025-11-04
description: "Manifesto for keeping long-form knowledge in durable, human- and agent-friendly files."
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

Version 0.1 · November 2025


**Premise:** Knowledge should outlast software.  

**Claim:** Today's models read the same media we do — _predominantly text_ — and other media (images, audio, video) are readily transcribable into text. The old "human-readable vs machine-readable" trade-off collapses.  

**Consequence:** Store what matters in _plain text (Markdown or .txt)_. Let tools come and go.


## Why now

For decades, computers demanded rigid, app-specific formats. Modern tools (including AI) read and reason over text directly. That enables a different architecture:

- **Data is stable** — files you own and control.  
- **Tools are interchangeable** — text editors, CLIs, and agents operate on those files.  
- **Intelligence is layered** — tools like search indexers and agents understand without owning the data.



## Core principles (non-negotiables)

1. **Files over apps.** Your _corpus_ (a folder of open files) is the system of record.  
2. **Plain text by default.** Use Markdown or .txt; keep light metadata in _front matter_ (or a tiny adjacent metadata file for .txt when necessary).  
3. **Tools assist, they don't annex.** No tool owns the data or invents a private schema that captures it.  
4. **Writes are previewed and reversible.** Tools propose changes; you review and apply; changes have a clear _provenance trail_.
5. **Composability beats monoliths.** Many small and non-exclusive tools on one shared corpus.  
6. **Minimum ceremony.** Conventions only where they pay for themselves (naming, links, front matter).  
7. **Portability and durability.** Ten years from now, the files still open and make sense.  
8. **Privacy first.** Local by default; use cloud only when needed.  
9. **No exports. No migrations.** The folder *is* the platform.



## The three laws of the Commons

1. **The folder is the platform.**  
   One **corpus**—a folder of open files—acts as the system of record.

2. **The file is the protocol.**  
   Stable, human-readable **plain text (Markdown or .txt)** with optional front matter. No opaque blobs.

3. **No tool owns the corpus.**  
   Tools are non-exclusive and interchangeable, none of them enforce format or schema of the corpus. 



## Multi-tool by design

Different tools specialize and still cooperate because they share the same substrate:

- **Authoring** in any editor.  
- **Browsing & searching** (exploration and retrieval) via tools—indexers, embeddings, link graphs, etc.  
- **Scripting and automation** with CLIs operated by humans/agents.  
- **Organizing chores** (linking, filing, light refactors) delegated to tools/agents—without taking ownership of the data.  
- **Capture & ingestion** from email, PDFs, and transcripts—converted to text with attachments nearby.

No exports. No migrations.



## Minimal working conventions

Keep it robust without bureaucracy:

- **Shallow corpus.** Let search, links, tags, and tools handle the heavy lifting, including organizing chores.  
- **Note schema is optional.** Zettelkasten, Fleeting/Project/Evergreen, or none—your choice.  
- **Stable filenames.** Use a simple stamp pattern if it helps.  
- **Metadata:**  
  - **Markdown:** use _front matter_ for light metadata.  
  - **.txt:** use a tiny _adjacent metadata file_ only when needed.  
- **Sync/history:** Git, cloud sync, both or none — your call.



## Norms for tools (agents included)

- **Read-only by default; explicit writes.**  
- **Previewable changes with rationale.** Generate human-auditable previews before any write.  
- **Explain results.** For ranking and retrieval, indicate why (keywords, similarity, links).  
- **Respect corpus rules.** Honor ignore lists, attachment folders, and local settings.  
- **Pipe-friendly I/O.** Text/JSON in and out; compose with other CLIs.  
- **AI/agent-aware.** Expose capabilities in open, automatable ways (e.g., MCP/stdio/HTTP)—no proprietary lock-ins.  
- **No schema capture.** Indexes are caches; they never become the source of truth.



## Adoption path (practical, not sacred)

1. **Start a corpus.** Pick a folder. Make it your system of record.  
2. **Choose light conventions.** Naming, links, and minimal front matter; stop when marginal value drops.  
3. **Add an indexer.** Turn on FTS + embeddings + backlinks; let the index come to the files, not the other way around.  
4. **Introduce a tool/agent.** Examples: **Claude Code** or **Codex** (CLI), **Claude.ai** (app), or **LM Studio** (local). Use open interfaces (CLI, MCP/stdio/HTTP).  
5. **Require previewable writes.** Propose → preview → apply → log.  
6. **Iterate only where it pays.** Improve naming, linking, tagging, and automation gradually.



## The Plaintext Test

Ask this before adopting a tool or workflow:

1. **Can I read/edit the files with a basic text editor?**  
2. **Can I move the folder and keep working—no exports required?**  
3. **Can the tool propose a human-auditable preview of changes (with rationale) before writing?**  
4. **Will this still make sense in ten years?**

If not, it's not Commons-compatible.



## Industry note

This is a **design stance**, not a membership. Build and use tools that keep data open, changes explainable, and the plaintext first. Everything else is replaceable.

</div>

## Next steps

- Collect feedback on this draft before publishing the standalone site.
- Comments, suggestions, reviews are welcome at [totocaster/plaintext-commons](https://github.com/totocaster/plaintext-commons/blob/main/MANIFESTO.md) repository for versioning.
- Publish on [plaintextcommons.org](https://plaintextcommons.org)
