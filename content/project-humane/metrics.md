---
title: Metrics
date: 2026-04-14
aliases:
  - /metrics/
description: "file-first Obsidian plugin for viewing and editing plaintext metric files"
project:
  year: 2026
  category: /project-humane
  description: "plaintext metrics view for Obsidian with search, validation, and charts"
  image: /visuals/project-thumbs/proj_metrics_obsidian.png
---

[Metrics](https://github.com/totocaster/metrics-obsidian) is a file-first [Obsidian](https://obsidian.md/) plugin for viewing and editing canonical `*.metrics.ndjson` files. It follows the [Plaintext Commons](/plaintext-commons/) stance that the folder is the platform, the file is the protocol, and tools should assist without annexing the corpus.

Obsidian is already excellent at handling notes and documents. Metrics is for the other kind of information: discrete data. I built it so measurements, counts, scores, durations, and similar records can live in the same plaintext world, readable and editable by humans and AI agents alike. This plugin is the human-facing part.

## What it does

- Opens `*.metrics.ndjson` files in a dedicated metrics view inside Obsidian.
- Parses and validates each record, surfacing warnings and errors without hiding the raw file.
- Adds and edits records through a form, while writing changes back to the underlying file.
- Creates, renames, and deletes metrics files inside a configurable `Metrics/` root.
- Searches measurements across the vault and jumps straight to the matching row.
- Filters by metric key, source, free text, status, and time range.
- Groups records by day, metric, or source and can compute summaries such as average, median, min, max, sum, or count.
- Renders built-in charts from the currently visible rows using native SVG and no external services.

## File format

Each line is one JSON object with required fields for `id`, `ts`, `key`, `value`, and `source`, plus optional metadata such as `date`, `unit`, `origin_id`, `note`, `context`, and `tags`.

That makes the files easy to version, grep, transform, and generate from other tools. The built-in catalog currently covers many of the metrics I personally care about, including body measurements, nutrition, sleep, recovery, and WHOOP-derived values, but the format itself is not limited to health data. Unknown keys and units are still allowed and simply show up as warnings rather than being silently normalized away.

## Why it exists

Notes and documents already have a good home in Obsidian. Discrete data usually gets pushed into vendor dashboards, spreadsheets, or app-specific schemas. Metrics brings that kind of data into alignment with [Plaintext Commons](/plaintext-commons/): inspectable, editable, durable, and still useful outside any single interface. If the UI disappeared tomorrow, the records would still be ordinary text files.

It also gives me a clean destination for data gathered elsewhere, whether that means manual entry or exports from tools like [Whoopy CLI](/project-humane/whoopy/) and [Withingy CLI](/project-humane/withingy/). Other tools and agents can work with the same files directly; Metrics handles the human side inside Obsidian.

## Source

The source and release notes live on GitHub: [totocaster/metrics-obsidian](https://github.com/totocaster/metrics-obsidian).
