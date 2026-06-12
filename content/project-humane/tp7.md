---
title: TP-7 CLI
date: 2026-05-07
aliases:
  - /tp7/
description: "CLI tool for humans and agents to manage files on Teenage Engineering TP-7 field recorders"
project:
  year: 2026
  category: /project-humane
  description: "CLI tool for humans and agents to manage files on Teenage Engineering TP-7 field recorders"
  image: /visuals/project-thumbs/proj_tp7_cli.png
---

[TP-7 CLI](https://github.com/totocaster/tp7) is a Rust command-line tool for humans and agents to manage files on a [Teenage Engineering TP-7](https://teenage.engineering/products/tp-7) field recorder from macOS. It can browse the recorder, download recordings from the device, and upload files back to it without relying on FieldKit or Android File Transfer.

The TP-7 normally appears as a USB audio/MIDI device. `tp7` switches the recorder into MTP mode when needed, opens a direct session, performs the requested file operation, and closes cleanly.

It is an unofficial project and is not affiliated with Teenage Engineering.

## What it does

`tp7` gives the terminal a practical file-access surface for the recorder. Common tasks:

- `tp7 devices` lists connected TP-7 recorders.
- `tp7 doctor` checks macOS USB and MTP setup.
- `tp7 -a ls -lah /memo` lists memo files with readable sizes.
- `tp7 -a stat /memo/2026-02-23_112713_000.wav` shows metadata for one recording.
- `tp7 -a pull /memo/2026-02-23_112713_000.wav ./recordings/` downloads one file.
- `tp7 -a pull /recordings ./recordings --recursive --skip-existing` copies a folder without replacing existing local files.
- `tp7 -a push ./clip.wav /memo/clip.wav --dry-run` previews an upload.
- `tp7 -a push ./clip.wav /memo/clip.wav --overwrite` uploads and replaces an existing remote file.
- `tp7 -a rm /memo/clip.wav --dry-run` previews a delete.

For normal use, `-a` / `--auto-connect` is the important flag. Each command then handles the full TP-7 lifecycle: detect the recorder, switch it to MTP if needed, open the session, perform the operation, and close the session.

A Finder-style `mount` / `unmount` workflow is also in progress. The goal is to let the same CLI expose the TP-7 as a mounted device, backed by macFUSE, without requiring FieldKit, Android File Transfer, or a separate TP-7 app.

## Agent-friendly by design

TP-7 CLI follows the same [Project Humane](/project-humane/) conventions as my other local tools: concise text output for people, deterministic `--json` for scripts and agents, non-zero exit codes on errors, explicit destructive commands, and dry-run support where a command can change files.

The CLI is independent of companion apps. FieldKit was useful as research for understanding the TP-7 handshake, but it is not a runtime dependency.

## Transfer safety

TP-7 recordings can be large, so the tool is cautious around transfers. I usually inspect before pulling unknown files:

```sh
tp7 -a ls -lah /recordings
tp7 -a stat /recordings/take.wav
tp7 -a pull /recordings/take.wav ./recordings --dry-run
```

Human output shows readable sizes plus exact byte counts for `stat`, `pull`, and `push`. JSON output keeps numeric byte fields for scripts. Downloads use temporary files and verify the final local size. Upload overwrite uses a staged remote replacement, uploading the new file under a temporary name before the existing object is moved out of the way.

## Current TP-7 limitations

The TP-7 firmware I tested (`1.1.9`) accepts file upload, rename, delete, and download operations over MTP, but rejects MTP folder creation. Because of that:

- `mkdir` exists, but currently reports the TP-7 firmware rejection.
- `push --recursive` uploads into an existing remote folder tree only.
- Missing remote folders are detected before any recursive upload starts.

## Local requirements

- macOS
- A Teenage Engineering TP-7 connected over USB
- Rust 1.88 or newer for source builds and development

No Android File Transfer, FieldKit, libmtp, or kernel extension is required for the direct CLI workflow.

## Get TP-7 CLI

Install it via my Homebrew tap:

```sh
brew tap totocaster/tap
brew install totocaster/tap/tp7
```

Or build it from source:

```sh
cargo install --git https://github.com/totocaster/tp7 --locked
```

The source and release notes live on GitHub: [totocaster/tp7](https://github.com/totocaster/tp7).
