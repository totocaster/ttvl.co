---
title: Vault Tasks
date: 2026-04-08
aliases:
  - /vault-tasks/
description: "Obsidian plugin that gathers tasks across a vault into one organized view"
project:
  year: 2026
  category: /project-humane
  description: "organized vault-wide task view for Obsidian with filters, pinning, and quick actions"
  image: /visuals/project-thumbs/proj_vault_tasks_obsidian.png
---

[Vault Tasks](https://github.com/totocaster/vault-tasks-obsidian) is an [Obsidian](https://obsidian.md/) plugin that gathers Markdown tasks from across the vault into one organized view.

I built it because I wanted a global task list that stays lightweight and native to Obsidian instead of turning the vault into a separate task system. Vault Tasks pulls everything into one place, keeps it organized, and lets me act on tasks without losing the context of the notes they came from.

## What it does

- Collects tasks from across the entire vault into one place
- Groups tasks by note and optionally by section
- Filters by pending, completed, or all tasks
- Filters by section name across notes
- Keeps pinned notes at the top of the list
- Adds quick note and task actions through inline controls and context menus
- Supports note-level defer and hide behavior
- Writes task changes back to the original notes

The settings pane covers vault-wide defaults such as open location, filters, related notes, folder scope, sorting, and task-status actions, so the view can match how a particular vault is organized.

There is also a read-only companion CLI, [vault-tasks](https://github.com/totocaster/vault-tasks-obsidian-cli), which renders the same organized task view in the terminal. It respects the plugin's saved settings and relevant Obsidian settings, and can emit human-readable output, summaries, or JSON for scripts and AI agents.

## Source

The source, releases, and development notes live on GitHub:

- Plugin: [totocaster/vault-tasks-obsidian](https://github.com/totocaster/vault-tasks-obsidian)
- Companion CLI: [totocaster/vault-tasks-obsidian-cli](https://github.com/totocaster/vault-tasks-obsidian-cli)
