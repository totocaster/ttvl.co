---
title: Things CLI
date: 2026-04-28
aliases:
  - /things-cli/
description: "macOS CLI for managing Things 3 tasks from the terminal"
project:
  year: 2026
  category: /project-humane
  image: /visuals/project-thumbs/proj_things_cli.png
resources:
  - title: 'GitHub'
    url: 'https://github.com/totocaster/things-cli-go'
---

[Things CLI](https://github.com/totocaster/things-cli-go) is a short macOS command-line tool for managing [Things 3](https://culturedcode.com/things/) tasks from the terminal. The binary is called `th`, because task capture and task checks should be quick enough to type without thinking.

It talks to Things through the app's supported AppleScript automation, so creates, updates, scheduling, completion, and trash operations go through Things itself. It does not write directly to the Things database.

## What it does

`th` gives the terminal a practical control surface for Things. Common tasks:

- `th add "Send invoice" --today --tag Work` creates a to-do for today with a tag.
- `th add "Draft launch notes" --project JLMPPROJECT123 --deadline 2026-05-01` creates a task directly inside a project.
- `th today` and `th inbox` show common Things lists quickly.
- `th list projects` and `th list areas` print Things IDs for move and create commands.
- `th get <id>` shows one to-do with status, tags, dates, and notes.
- `th search <query>` searches Things to-dos.
- `th schedule <id> 2026-04-29` and `th schedule <id> none` set or clear the scheduled date.
- `th due <id> 2026-05-01` sets a deadline.
- `th move <id> --list someday` moves a to-do to a built-in list.
- `th complete <id> --quiet` marks a task completed without printing success text.
- `th show <id>` reveals a to-do in Things.
- `th delete <id> --yes` moves a to-do to Things Trash.

Text output is the default for ordinary terminal use. `--json` switches to structured output for scripts and AI agents, while `--quiet` suppresses successful mutating output when only the exit code matters.

## Agent-friendly by design

Things already has a polished human interface, but agents and shell scripts need a stable command contract. `th` is designed to be used by AI agents like OpenClaw, Claude Code, Codex, and similar local assistants, following the same Project Humane conventions as my other tools: predictable flags, concise text, structured JSON, non-zero exit codes on errors, shell completions, and explicit confirmation for destructive commands.

That makes it useful as a bridge between Things and local automation. An agent can inspect today's list, capture a task, move work into a project, complete a finished task, or open a specific item in Things without scraping the UI or touching private app storage.

## Local requirements

`th` is macOS-only. It requires Things 3, `osascript`, and macOS Automation permission for terminal access to Things.

The built-in doctor command checks the local setup:

```sh
th doctor
th doctor --check-automation
```

The explicit automation check is read-only, but it may trigger the macOS permission prompt the first time it runs.

## Get Things CLI

Install it via my Homebrew tap:

```sh
brew install --cask totocaster/tap/th
```

Or install it with Go:

```sh
go install github.com/totocaster/things-cli-go/cmd/th@latest
```

The source and release notes live on GitHub: [totocaster/things-cli-go](https://github.com/totocaster/things-cli-go).
