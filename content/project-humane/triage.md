---
title: Triage
date: 2026-06-12
aliases:
  - /triage/
description: "Obsidian plugin for resurfacing unprocessed notes in an Anki-style triage queue"
project:
  year: 2026
  category: /obsidian
  description: "resurfaces unprocessed notes in an Anki-style triage queue"
  image: /visuals/project-thumbs/proj_triage_obsidian.png
---

[Triage](https://github.com/totocaster/triage-obsidian) is an [Obsidian](https://obsidian.md/) plugin for resurfacing unprocessed notes in an Anki-style triage queue before they disappear into the vault.

Every vault accumulates loose material: fleeting notes, literature notes, clippings, and pages that never got a tag or a category. Triage gathers eligible notes into a scrolling queue of cards so I can make a quick, low-stakes decision about each one: keep it, snooze it, delete it, or open it and actually process the note.

## What it does

- Builds an Anki-style triage queue from notes that match configurable include and exclude filters.
- Shows content-rich note cards with actual previews, not just titles.
- Expands cards in place to a rendered note body when more context is needed.
- Supports keyboard-first review with shortcuts for focus, expand, snooze, keep, and clear snooze.
- Snoozes notes for configurable intervals and brings them back on concrete due dates.
- Marks kept notes through configurable frontmatter fields, tags, or frontmatter values.
- Hands delete actions to Obsidian's built-in delete prompt instead of deleting silently.
- Keeps all state in note frontmatter, with configurable field names.

## How it fits

Triage is for notes that are not quite tasks. A task manager is the wrong place for a clipped paragraph, a half-formed idea, or a literature note that needs a category. Leaving those notes alone is not much better; they fade into search results and backlinks until I forget why I saved them.

The plugin borrows some ergonomics from Anki: focused cards, numbered decisions, and intervals that feel quick enough to use. It is not a spaced-repetition tool, though. There is no memory model or ease factor. Snooze writes a plain due date to frontmatter, and the note returns when that date arrives.

That keeps the system compatible with [Plaintext Commons](/plaintext-commons/): the plugin adds a useful review surface, but the notes remain ordinary Markdown files with inspectable metadata.

## Links

- Community plugin page: [Triage](https://community.obsidian.md/plugins/triage)
- Source, releases, and development notes: [totocaster/triage-obsidian](https://github.com/totocaster/triage-obsidian)
