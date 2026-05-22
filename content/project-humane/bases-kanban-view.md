---
title: Better Kanban Bases View
date: 2026-05-22
aliases:
  - /bases-kanban-view/
  - /kanban-base-view/
description: "focused Kanban view for Obsidian Bases"
project:
  year: 2026
  category: /project-humane
  description: "focused Kanban view for Obsidian Bases with draggable cards and saved layouts"
  image: /visuals/project-thumbs/proj_kanban_view_obsdian.png
---

[Better Kanban Bases View](https://github.com/totocaster/kanban-base-view-obsidian) is an [Obsidian](https://obsidian.md/) plugin that adds a focused Kanban layout to Bases. It keeps the existing Bases controls for sorting, grouping, filtering, and property selection, then renders the same results as columns and cards.

This is a Bases view: it extends the presentation capabilities of Obsidian Bases without creating a separate Kanban file format or a second set of project-management settings.

I also really like how [Things 3 for Mac](https://culturedcode.com/things/) handles shortcuts, so I tried to emulate that behavior inside the view. The goal is for keyboard navigation and card movement to feel fluid and pleasant, not like an afterthought bolted onto a mouse-first board.

![Better Kanban Bases View thumbnail](/visuals/project-thumbs/proj_kanban_view_obsdian.png)

## What it does

- Adds a custom **Kanban** view to Obsidian Bases.
- Builds columns from the active Bases grouping.
- Shows each note's title plus the properties already selected in Bases.
- Renders formula properties through the same evaluated Bases values as the table view.
- Adds optional small or large plain-text previews from the note body.
- Reorders columns and cards with drag-and-drop, keyboard shortcuts, and context menus.
- Moves cards across columns when the board is grouped by a writable `note.*` property.
- Saves column order and manual card order per grouping.
- Creates notes in writable columns and supports rename or delete actions from the card menu.
- Makes no network requests and includes no telemetry.

## How it fits

Sorting, grouping, filters, and selected properties still live in the built-in Bases UI. The Kanban view adds another way to look at the same notes, then writes changes back to note frontmatter only when a move can be represented by the grouped property.

Manual card ordering behaves like a deliberate snapshot of the current grouped board. When the Base sort changes again, the board returns to following that sort, which keeps the plugin from fighting the underlying query.

## Install

Install it from Obsidian's community plugin directory: [Better Kanban Bases View](https://community.obsidian.md/plugins/bases-kanban-view-ttvl).

The source, releases, and development notes live on GitHub: [totocaster/kanban-base-view-obsidian](https://github.com/totocaster/kanban-base-view-obsidian).
