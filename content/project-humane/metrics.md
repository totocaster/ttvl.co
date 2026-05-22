---
title: Metrics
date: 2026-04-14
aliases:
  - /metrics/
description: "file-first Obsidian plugin for viewing and editing plaintext metric files"
project:
  year: 2026
  category: /obsidian
  description: "plaintext metrics view for Obsidian with search, validation, and charts"
  image: /visuals/project-thumbs/proj_metrics_obsidian.png
---

[Metrics](https://github.com/totocaster/metrics-obsidian) is an [Obsidian](https://obsidian.md/) plugin for viewing and editing structured metric records stored as plain `*.metrics.ndjson` files. It is designed for measurements, scores, counts, durations, and other discrete data that do not fit naturally into notes.

Obsidian is already excellent at handling prose and documents. Metrics handles the structured side, keeping the files readable and editable outside the UI so humans and AI agents can work with the same records. It follows the [Plaintext Commons](/plaintext-commons/) idea that the folder is the platform and the file is the protocol.

It is for people who want structured records in Obsidian without turning them into spreadsheet-only or app-owned data.

![Metrics charts and timeline in Obsidian](/visuals/project-humane/2026.04.14-metrics-charts.png)

## Example file

Each line is one JSON object:

```json
{"id":"01JV7RK8Q4X60M0E2N0A6QK61V","ts":"2026-04-14T08:30:00+04:00","key":"body.weight","value":105.6,"unit":"kg","source":"withings"}
{"id":"01JV7RM60M9X1Y9G7TWJ3CF8ES","ts":"2026-04-14T09:10:00+04:00","key":"nutrition.energy_intake","value":720,"unit":"kcal","source":"manual","note":"breakfast"}
```

The plugin acts as a lens over those files: view them, validate them, edit them, search them, and chart them without moving the data somewhere else.

## What it does

- Opens `*.metrics.ndjson` files in a dedicated metrics view inside Obsidian.
- Parses and validates each record, surfacing warnings and errors without hiding the raw file.
- Adds and edits records through a form, while writing changes back to the underlying file.
- Creates, renames, and deletes metrics files inside a configurable `Metrics/` root.
- Searches measurements across the vault and jumps straight to the matching row.
- Filters by metric key, source, free text, status, and time range.
- Groups records by day, metric, or source and can compute summaries such as average, median, min, max, sum, or count.
- Renders built-in charts from the currently visible rows using native SVG and no external services.

![Metrics nutrition view with daily summaries and record notes](/visuals/project-humane/2026.04.14-metrics-nutrition.png)

## File format

Each line is one JSON object with required fields for `id`, `ts`, `key`, `value`, and `source`, plus optional metadata such as `date`, `unit`, `origin_id`, `note`, `context`, and `tags`.

That makes the files easy to version, grep, transform, and generate from other tools. The built-in catalog currently covers many of the metrics I personally track, but the format itself is open-ended. Known keys get nicer labels, units, icons, and formatting; unknown keys and units are still allowed and show up as warnings instead of being silently normalized away.

## Why it exists

Notes and documents already have a good home in Obsidian. Discrete data usually gets pushed into vendor dashboards, spreadsheets, or app-specific schemas. Metrics brings that kind of data into alignment with [Plaintext Commons](/plaintext-commons/): inspectable, editable, durable, and still useful outside any single interface. If the UI disappeared tomorrow, the records would still be ordinary text files.

It also gives me a clean destination for data gathered elsewhere, whether that means manual entry or exports from tools like [Whoopy CLI](/project-humane/whoopy/) and [Withingy CLI](/project-humane/withingy/). Other tools and agents can work with the same files directly; Metrics handles the human side inside Obsidian.

## Links

- Community plugin page: [Metrics](https://community.obsidian.md/plugins/metrics-lens)
- Repository and install instructions: [totocaster/metrics-obsidian](https://github.com/totocaster/metrics-obsidian)
- Metric file format and example records: [README: Metric files](https://github.com/totocaster/metrics-obsidian#metric-files)
