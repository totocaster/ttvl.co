---
title: Whoopy CLI
date: 2026-03-04
aliases:
  - /whoopy/
description: "unofficial WHOOP data CLI for humans, automations, and AI agents"
project:
  year: 2026
  category: /project-humane
  image: /visuals/project-thumbs/proj_whoopy.png
---

[Whoopy CLI](https://github.com/totocaster/whoopy) is an unofficial [WHOOP](https://www.whoop.com/) data CLI written in Go. It wraps WHOOP's OAuth flow and developer v2 APIs so humans, automations, dashboards, and AI agents can pull workouts, sleep, recovery, and stats securely from the terminal.

## What it does

Whoopy v0.4 provides access to the profile, workouts, sleep, recovery, cycles, and day-level stats exposed by the WHOOP developer API through a single binary with consistent, scriptable output. Common tasks:

- `whoopy stats daily --date 2026-03-03 --text` aggregates workouts, recovery, sleep, and strain for a single day.
- `whoopy workouts list --sport running --min-strain 8` filters workouts client-side.
- `whoopy workouts export --format csv --output workouts.csv` auto-paginates and streams data as CSV or JSON Lines.
- `whoopy sleep today --text` shows a human-readable sleep summary.

JSON output is the default for scripts and agents; `--text` switches to aligned tables for human reading.

![Whoopy CLI daily stats in the terminal](/visuals/project-humane/2026.03.04-whoopy-screenshot.png)

Here is an example of `whoopy recovery today` returning JSON, ready for piping into `jq` or consumption by an AI agent:

```json
{
  "recoveries": [
    {
      "cycle_id": 1345285100,
      "score_state": "SCORED",
      "score": {
        "recovery_score": 81,
        "resting_heart_rate": 66,
        "hrv_rmssd_milli": 39.19,
        "spo2_percentage": 94.85,
        "skin_temp_celsius": 32.93
      }
    }
  ]
}
```

And the same day's sleep as a human-readable table with `whoopy sleep today --text`:

```
Start                          Duration  Perf%  Resp  Nap  ID
Tue, 03 Mar 2026 23:40:19 JST  8h27m     90.0   14.8  no   eab936b2-…
```

## Agent-friendly by design

Whoopy follows the same conventions as my other [Project Humane](/project-humane/) tools: consistent flags, quiet success, non-zero exit codes on errors, and deterministic JSON output. This makes it straightforward for AI agents like Claude to query WHOOP data, build daily dashboards, or integrate health metrics into broader workflows.

## Authentication

Whoopy v0.4 uses first-party OAuth with PKCE. Running `whoopy auth login` creates a configuration template at `${XDG_CONFIG_HOME:-~/.config}/whoopy/config.toml` when one does not exist. After the WHOOP client ID and secret have been added, running the command again opens the browser for authorization and stores tokens at `${XDG_STATE_HOME:-~/.local/state}/whoopy/tokens.json`. Existing tokens in the old configuration-directory location are migrated automatically. Tokens refresh automatically; `whoopy auth status` shows remaining lifetime and scopes. Headless workflows are supported via `--no-browser` and `--manual` flags.

## Get Whoopy

Install via my Homebrew tap:

```
brew tap totocaster/tap
brew install whoopy
```

The source and release notes live on GitHub: [totocaster/whoopy](https://github.com/totocaster/whoopy).
