---
title: Obsidian
date: 2026-05-22
description: "A hub for my Obsidian plugins, vault tools, and plain-text knowledge system experiments."
---

This page gathers the tools and experiments I have built around [Obsidian](https://obsidian.md/). I use it extensively: as a knowledge base, personal journal, life-metrics workspace, and extended context layer for my personal AI assistant.

The center of the system is still [plain text](/plaintext-commons/). Obsidian fits that philosophy well, but I also value it as a programmable workspace: local files underneath, a flexible plugin layer on top, and enough surface area to shape the tool around the way I actually think and work.

That feels especially useful now that software agents can help with small, personal pieces of infrastructure. A plugin does not have to begin as a product idea. It can start as a missing affordance in one vault, become a tool I rely on, and then be published if it seems useful beyond my own setup.

## Obsidian plugins

- [Better Kanban Bases View](/project-humane/bases-kanban-view/) adds a focused Kanban layout to [Obsidian Bases](https://help.obsidian.md/bases), using the existing Bases controls for sorting, grouping, filtering, and property selection instead of inventing a separate board format.
- [Metrics](/project-humane/metrics/) makes plain-text JSON metric files usable inside Obsidian, with friendly editing, validation, search, grouping, and charts while keeping the data readable and editable by AI agents without a proprietary database.
- [Vault Tasks](/project-humane/vault-tasks/) gathers Markdown tasks from across a vault into one organized view with filters, pinned notes, quick actions, and write-back to the original notes.
- [Plaintext Task](https://github.com/totocaster/plaintext-task-obsidian) is an alternative Obsidian implementation for plaintext tasks, with a more centralized model than Vault Tasks.

Published community plugins are collected on my [Obsidian Community profile](https://community.obsidian.md/users/ttvl).

## Vault tools

- [Arrowhead CLI](/arrowhead/) is the search, discovery, graph, metrics, and MCP layer for my vault. It keeps Markdown indexed around the clock and gives local agents a way to work from evidence instead of vague memory.
- [Stamp CLI](/stamp/) generates consistent filenames for daily notes, fleeting notes, project notes, and other predictable objects. It can pick up Obsidian Daily Notes and Unique Note Creator conventions when run inside a vault.
- [Plaintext Commons](/plaintext-commons/) is the underlying argument: the folder is the platform, and the file is the protocol.

## Data that belongs in the vault

Some of the Obsidian work is about making non-prose records feel at home beside notes:

- [Whoopy CLI](/project-humane/whoopy/) pulls WHOOP recovery, sleep, workout, and strain data from the terminal.
- [Withingy CLI](/project-humane/withingy/) pulls Withings activity, sleep, body metric, and workout data.

Those command-line tools are not Obsidian plugins, but they produce the kind of plain, scriptable data that can be summarized, charted, and cross-referenced from the same corpus.

## My current setup

Obsidian, with Sync, is the main human access point to the corpus. Codex, Claude Code, OpenClaw, and other local agents use Arrowhead and shell tools to make the same vault more searchable and discoverable from their side. The goal is to use the Obsidian vault as both my knowledge base and an extended context layer for agents, while keeping Obsidian as the interface I use directly.

The current plugin stack is documented in the [Arrowhead setup notes](/arrowhead/#my-setup). It includes core navigation and linking tools, cleanup utilities, Quick Switcher++, media transcript helpers, and my own Metrics plugin for structured records.

## Development log

- [April 2025](/log/2025/04/) records an early note-search idea that might become either an Obsidian plugin or a native app.
- [June 2025](/log/2025/06/) covers the first useful MCP server version working with Claude and the Obsidian vault.
- [July 2025](/log/2025/07/) notes the note-search work becoming Obsidian-compatible.
- [August 2025](/log/2025/08/) marks the pivot toward an Obsidian companion app.
- [September 2025](/log/2025/09/) describes the combination of Claude Code, Obsidian, and local vault tooling as a file-based note-taking system.
- [October 2025](/log/2025/10/) introduces Arrowhead CLI as an Obsidian-aware search and discovery layer.
- [April 2026](/log/2026/04/) collects the first public Obsidian plugins in this direction: Vault Tasks, Plaintext Task, and Metrics.

## Where this is going

I am interested in Obsidian as a stable, local, human-scale surface for a broader plain-text workspace, but also as a kind of [malleable software](https://www.inkandswitch.com/malleable-software/): an environment that can be reshaped through small plugins and command-line tools. The plugins here begin with my own needs first. The command-line tools do indexing, capture, naming, and data import around the same files; they also give AI agents running through harnesses like Codex or Claude Code a practical way to read and manipulate the corpus. Together they form a system where notes, tasks, metrics, transcripts, and paper scans can stay in one inspectable corpus without depending on a single app to understand everything.
