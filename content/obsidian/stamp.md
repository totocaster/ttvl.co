---
title: Stamp CLI
date: 2025-09-18
aliases:
  - /stamp/
  - /project-humane/stamp/
description: "A CLI tool for generating consistent filenames for notes"
project:
  year: 2025
  category: /obsidian
  image: /visuals/project-thumbs/proj_stamp.png
resources:
  - title: 'GitHub'
    url: 'https://github.com/totocaster/stamp'
---

[Stamp CLI](https://github.com/totocaster/stamp) is my note-naming assistant for [Plaintext Commons](/project-humane/plaintext-commons/) vaults and folders. It generates consistent IDs and filenames so humans, agents, and automations can keep a shared corpus tidy without manual bookkeeping. The same binary is available as both `stamp` and `nid`.

## What it does

Stamp prints filename suggestions to stdout, making it useful in shell scripts, AI-agent workflows, and quick terminal sessions. Common tasks include:

- `stamp daily` produces a YYYY-MM-DD daily note name.
- `stamp fleeting` outputs a timestamped fleeting note ID.
- `stamp project "Arrowhead CLI"` produces the next project ID, such as `P0461 Arrowhead CLI`.
- `stamp seq --prefix jin --width 3 "Jinny Research"` produces a custom sequential ID, such as `jin005 Jinny Research`.

It also supports default timestamps, voice transcripts, analog or slipbox notes, and monthly and yearly reviews. The `--ext` flag adds a Markdown extension, while `--copy` copies the result to the clipboard on macOS.

The `project` and `seq` commands find the next number by scanning the current directory for matching filenames and folders. `stamp project` is shorthand for `stamp seq --prefix P --width 4`. Analog notes continue to use a persistent counter that resets daily.

Each format follows the conventions used across my Project Humane tools, so new notes land in predictable places and link cleanly inside the Plaintext Commons corpus.

## Obsidian-aware

When run inside an Obsidian vault, Stamp automatically picks up formats from the enabled [Daily Notes](https://help.obsidian.md/plugins/daily-notes) core plugin and the community [Unique Note Creator](https://github.com/adriano-tirloni/unique-note-creator) plugin. If their settings are missing or use unsupported format tokens, Stamp falls back to its built-in formats and reports a warning without interrupting the command.

## Why it exists

I wanted [Arrowhead](/obsidian/arrowhead/) and my AI assistants to agree on the same naming rules without hand-coded prompts. Stamp gives them one shared source of truth, making cross-linking, lookup, and note creation consistent across my automation tools.

## Installation

Install via my Homebrew tap:

```sh
brew tap totocaster/tap
brew install stamp
```

This installs both the `stamp` and `nid` commands. You can also download binaries directly from [GitHub releases](https://github.com/totocaster/stamp/releases) if you prefer a manual installation.

## Current version

### 0.3.0 — 2026-02-21

- Added the general-purpose `stamp seq` command, with configurable prefix, width, and starting number.
- Changed project and custom sequences to derive the next number by scanning the current directory instead of reading and writing stored counters.
- Kept `stamp project` as shorthand for a sequence using the `P` prefix and four digits. Analog notes still use their persistent daily counter.
