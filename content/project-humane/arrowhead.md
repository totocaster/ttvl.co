---
title: Arrowhead CLI
date: 2025-10-31
url: /arrowhead/
aliases:
  - /project-humane/arrowhead/
---

**Arrowhead** ([on GitHub](https://github.com/totocaster/arrowhead)) is the plain-text search engine and agent bridge for my [Obsidian](https://obsidian.md/) vault. It keeps everything indexed for humans and AI alike, combining fast full-text search, semantic vectors, and graph analytics under one [CLI](https://en.wikipedia.org/wiki/Command-line_interface). Arrowhead is part of **[Plaintext Commons](/plaintext-commons/)**—my broader effort to build file-native thinking systems—with a public site forthcoming at [plaintextcommons.org](https://plaintextcommons.org).

I built Arrowhead after years of bouncing between note-taking apps that locked away structure, links, and history. Plain text stayed the only constant, so the tool had to respect the folder as the source of truth. Arrowhead rewrites my earlier [Synapse/Soma](/project-humane/soma/) tools in Rust, trading a single-purpose search utility for a platform that feels at home on the command line, runs an always-on daemon, and speaks to AI agents like Claude and other that can help manage the corpus. 

## How Arrowhead works

The CLI is the control surface, but the daemon does the real work. Indexing, search, and graph features depend on the daemon staying alive, so the typical flow is to initialize once and let the service run in the background.

- `arrowhead` (CLI) bootstraps the vault, manages the daemon (`arrowhead index start/status/autostart`), and provides search, graph, and CRUD commands.
- `arrowheadd` (daemon) watches the vault, streams changes into the SQLite + FTS5 + vector indexes, and exposes health/status endpoints.
- MCP transports (stdio + optional HTTP) read from the same live index so assistants can perform everything the CLI can.
- Hybrid ranking combines boolean operators, field filters, semantic similarity, and per-result explanations to show why a note surfaced.

The stack is intentionally pragmatic: Rust for speed and safety, SQLite for portability, `fastembed` embeddings stored with the index. `arrowhead init` seeds configuration, starts the daemon, and can register launchd/systemd autostart so indexing stays on even after reboot. CLI searches and MCP calls read directly from the hot index maintained by the daemon.

## Why it exists

**Plaintext Commons** treats files—not apps—as the durable layer for long-term knowledge work. Arrowhead is the search, discovery, and automation engine for that vision. It gives me confidence that vaults stay queryable, linkable, and agent-friendly without handing control to a silo. Whether I am debugging code, revisiting research threads, or asking Claude to draft a change, Arrowhead keeps the raw materials close while letting assistants do meaningful work.

Arrowhead also absorbs the ingest and transcription ambitions that started with Soma. Analog note capture will migrate here—paired with a dedicated helper tool once the ergonomics are nailed—so a single system handles vault search and the bridges back to paper.

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
  - [Natural Language Dates](https://github.com/argenos/nldates-obsidian)
  - [Paste URL into selection](https://github.com/denolehov/obsidian-url-into-selection)
  - [Quick Switcher++](https://github.com/darlal/obsidian-switcher-plus) as my human-accessible FTS

I prefer Claude Code over Codex when working with my notes (although the reverse is true for programming). I sometimes use Claude.app with Arrowhead MCP as well, but I find it a bit slower for tool calls (MCP tool calls vs. direct CLI usage). CLI agents are also better at picking up conventions since they don't need to call the `vault_conventions` MCP tool every time; everything is laid out in `AGENTS.md` or `CLAUDE.md` at startup. You can see my `CLAUDE.md` [here](https://gist.github.com/totocaster/cc197014af915ec06cb746bab34dbe26).