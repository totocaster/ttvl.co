---
title: Stamp CLI
date: 2025-09-18
url: /stamp/
aliases:
  - /project-humane/stamp/
description: "tool for generating consistent filenames for notes"
project:
  year: 2025
  category: /obsidian
  image: /visuals/project-thumbs/proj_stamp.png
---

[Stamp CLI](https://github.com/totocaster/stamp) is my note-naming assistant for [Plaintext Commons](/plaintext-commons) vaults and folders. It generates consistent IDs and filenames so humans, agents, and automations can keep a shared corpus tidy without manual bookkeeping.

## What it does

Stamp is a single binary that prints filename suggestions to stdout. It is friendly to shell scripts, AI agents, and quick terminal workflows. Common tasks:

- `stamp daily` produces a YYYY-MM-DD daily note name.
- `stamp fleeting` outputs a timestamped fleeting note ID.
- `stamp project` increments project IDs such as `P0461-arrowhead-cli`.

Each format follows the conventions used across my Project Humane tools, so new notes land in predictable places and link cleanly inside the Plaintext Commons corpus.

## Obsidian-aware

Stamp is Obsidian-aware and automatically picks up [Daily Notes](https://help.obsidian.md/plugins/daily-notes) and [Unique Note Creator](https://help.obsidian.md/plugins/unique-note) formats when run inside an Obsidian vault.


## Why it exists

I wanted [Arrowhead](/arrowhead/) and my AI assistants to agree on the same naming rules without hand-coded prompts. Stamp serves that role:

The side effect is that all automation tools follow same instructions for naming using stamp and thus cross-linking, lookup and note creation is standartized.

## Installation

Install via my Homebrew tap:

```
brew tap totocaster/tap
brew install totocaster/tap/stamp
```

You can also download release binaries directly from [GitHub releases](https://github.com/totocaster/stamp/releases) if you prefer manual installs.

## Changelog

### 0.3.0 — 2026-02-21

- Added `stamp seq` for general-purpose sequential counters, so you can mint predictable IDs for any object (projects, folios, bindery fixtures, etc.) without relying on a single hard-coded format.
- Removed the legacy project-specific counters in favor of `stamp seq <key>`, keeping number generation consistent across every workspace.
