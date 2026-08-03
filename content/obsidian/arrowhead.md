---
title: Arrowhead CLI
date: 2025-10-31
aliases:
  - /arrowhead/
  - /project-humane/arrowhead/
description: "helps AI agents and command-line tools make sense of your Obsidian vault"
featured: true
project:
  year: 2025
  category: /obsidian
  description: "helps AI agents and command-line tools make sense of your Obsidian vault"
  image: /visuals/project-thumbs/proj_arrowhead.png
---

**Arrowhead** ([on GitHub](https://github.com/totocaster/arrowhead)) helps AI agents and command-line tools make sense of my [Obsidian](https://obsidian.md/) vault. It keeps Markdown notes indexed around the clock, combining fast full-text search, semantic vectors, graph analytics, time-based context, and metric queries under one [CLI](https://en.wikipedia.org/wiki/Command-line_interface) and MCP surface. Arrowhead is part of **[Plaintext Commons](/project-humane/plaintext-commons/)**—my broader effort to build file-native thinking systems—whose manifesto lives at [plaintextcommons.org](https://plaintextcommons.org/).

I built Arrowhead after years of bouncing between note-taking apps that locked away structure, links, and history. Plain text stayed the only constant, so the tool had to respect the folder as the source of truth. Arrowhead rewrites my earlier search tools in Rust, trading a single-purpose search utility for a platform that feels at home on the command line, runs an always-on daemon, and speaks to AI agents like Claude, Codex, and OpenClaw.

## How Arrowhead works

The CLI is the control surface, but the daemon does the real work. Indexing, search, and graph features depend on the daemon staying alive, so the typical flow is to initialize once and let the service run in the background.

- `arrowhead` (CLI) bootstraps Obsidian vaults or generic Markdown workspaces, manages the daemon (`arrowhead index start/status/autostart`), and provides search, workspace, context, metric, graph, and CRUD commands.
- `arrowheadd` (daemon) watches the vault, streams changes into the SQLite + FTS5 + vector indexes, and writes status/log files agents can inspect while it starts.
- MCP transports (stdio + authenticated HTTP) read from the same live index, with bearer or link-token auth, CIDR allowlists, and `/health` readiness checks for remote clients.
- Context commands surface day, week, month, changed-note, note, metric, and source views with evidence tiers and suggested pivots instead of only raw search hits.
- Hybrid ranking combines boolean operators, field filters, date filters, semantic similarity, and per-result explanations to show why a note surfaced.

The stack is intentionally pragmatic: Rust for speed and safety, SQLite for portability, `fastembed` embeddings stored with the index. `arrowhead init` seeds configuration, starts the daemon, and can register launchd/systemd autostart so indexing stays on even after reboot. Obsidian settings remain the preferred source of vault conventions, but non-Obsidian Markdown folders can use `.arrowhead/workspace.toml` for attachments, ignored folders, daily-note formats, and link style. Embeddings can also be disabled with `--fts-only` when a lighter full-text-only setup makes more sense.

## Why it exists

**Plaintext Commons** treats files—not apps—as the durable layer for long-term knowledge work. Arrowhead is the search, discovery, and automation engine for that vision. It gives me confidence that vaults stay queryable, linkable, and agent-friendly without handing control to a silo. Whether I am debugging code, revisiting research threads, checking metric trends, or asking an agent to draft a change, Arrowhead keeps the raw materials close while letting assistants do meaningful work.

Arrowhead also extends into ingest and transcription. Analog note capture will migrate here—paired with a dedicated helper tool once the ergonomics are nailed—so a single system handles vault search and the bridges back to paper.

## Get Arrowhead

Install it via my Homebrew tap:

```
brew tap totocaster/tap
brew install totocaster/tap/arrowhead
```

The source and release notes live on GitHub: [totocaster/arrowhead](https://github.com/totocaster/arrowhead).

---

## My setup

As of November 2025, below is the setup I use for my digital note-taking.

* **[Claude Code](https://www.claude.com/product/claude-code)** (with Pro Plan) serves as my AI assistant and primary access point to the corpus. It uses the following tools:
  * [Arrowhead CLI](https://github.com/totocaster/arrowhead) for search and discovery
  * [Stamp CLI](https://github.com/totocaster/stamp) for standardized file names, following the Obsidian plugin conventions listed below
  * [MarkEdit](https://github.com/MarkEdit-app/MarkEdit) for editing and viewing text, since copying from Terminal apps can mess with formatting
  * [Things URL Schema](https://culturedcode.com/things/support/articles/2803573/) for creating (no read available) todos in my todo app
  * [things-cli](https://github.com/thingsapi/things-cli) for traversing my todos
  * [iMCP](https://github.com/mattt/iMCP) for access to my location and calendar (I seldom use this)
* **[Obsidian](https://obsidian.md)** (with Sync) is my main human access point to the corpus. I use the following plugins:
  - [Backlinks](https://help.obsidian.md/plugins/backlinks)
  - [Unique note creator](https://help.obsidian.md/plugins/unique-note) for fleeting notes
  - [File Cleaner](https://github.com/Johnson0907/obsidian-file-cleaner)
  - [Linter](https://github.com/platers/obsidian-linter)
  - [Local images](https://github.com/aleksey-rezvov/obsidian-local-images)
  - [Media Extended](https://github.com/aidenlx/media-extended) for lectures and video transcripts
  - [Metrics](/obsidian/metrics/) for nutrition, WHOOP data, medications, and other structured records
  - [Natural Language Dates](https://github.com/argenos/nldates-obsidian)
  - [Paste URL into selection](https://github.com/denolehov/obsidian-url-into-selection)
  - [Quick Switcher++](https://github.com/darlal/obsidian-switcher-plus) as my human-accessible FTS

I prefer Claude Code over Codex when working with my notes (although the reverse is true for programming). I sometimes use Claude.app with Arrowhead MCP as well, but I find it a bit slower for tool calls (MCP tool calls vs. direct CLI usage). CLI agents are also better at picking up conventions since they don't need to call the `vault_conventions` MCP tool every time; everything is laid out in `AGENTS.md` or `CLAUDE.md` at startup. You can see my `CLAUDE.md` [here](https://gist.github.com/totocaster/cc197014af915ec06cb746bab34dbe26).
