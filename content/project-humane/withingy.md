---
title: Withingy CLI
date: 2026-03-06
aliases:
  - /withingy/
description: "Withings data CLI for humans, automation, and AI agents"
project:
  year: 2026
  category: /project-humane
  image: /visuals/project-thumbs/proj_withingy.png
resources:
  - title: 'GitHub'
    url: 'https://github.com/totocaster/withingy'
---

[Withingy CLI](https://github.com/totocaster/withingy) is a Go CLI for pulling [Withings](https://www.withings.com/) data from the terminal. It started as a transplant from [Whoopy CLI](/project-humane/whoopy/), keeping the same JSON-first operator experience while swapping in Withings-specific auth, activity, body metrics, sleep, and workouts.

## What it does

Withingy keeps health data accessible through a single binary with predictable output for humans, shell scripts, dashboards, and AI agents. Common tasks:

- `withingy stats daily --text` aggregates activity, sleep, and workouts for your local calendar day.
- `withingy activity today --text` renders a human-readable activity summary.
- `withingy weight today --text` shows the current day's weigh-ins without needing a manual date range.
- `withingy weight latest --text` shows the most recent body-weight entry.
- `withingy sleep today --text` renders the latest sleep summary in a readable table.
- `withingy workouts export --format csv` exports workouts as CSV or JSON Lines.

JSON is the default for scripts and agents; `--text` switches to readable terminal output where available. `weight` and `measures` JSON timestamps are emitted as RFC3339 UTC values, while `--text` output renders times in your local timezone. `weight list` defaults to the last 30 days when you do not provide a range, and `today` shortcuts plus `stats daily` without `--date` follow your local calendar day.

## Agent-friendly by design

Withingy follows the same conventions as my other [Project Humane](/project-humane/) tools: quiet success, non-zero exit codes on errors, deterministic JSON, XDG-friendly config, and shell completions for `zsh`, `bash`, and `fish`. That makes it straightforward for AI agents and local automations to inspect body metrics, sleep sessions, workouts, and daily aggregates without relying on a browser-first workflow.

## Authentication

Withingy stores config and tokens under `~/.config/withingy/`. The current auth flow supports browser login plus a manual fallback when localhost callback auth is inconvenient. Credentials and endpoint overrides can also be provided through `WITHINGY_*` environment variables.

## Get Withingy

Install it via my Homebrew tap:

```sh
brew tap totocaster/tap
brew install withingy
```

The source and release notes live on GitHub: [totocaster/withingy](https://github.com/totocaster/withingy).
