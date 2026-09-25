---
title: Copy Editor
date: 2026-09-25
description: "AI writing tool for people who love to write."
project:
  year: 2026
  category: /project-humane
  description: "AI writing tool for people who love to write."
  image: /visuals/project-thumbs/proj_copy_editor.png
resources:
  - title: 'GitHub'
    url: 'https://github.com/totocaster/copy-editor'
---

[Copy Editor](https://github.com/totocaster/copy-editor) is a local editor for writing and revising prose. Write a draft, ask for an editing pass, and work through the findings beside your text. Suggestions, questions, and notes stay attached to the passages they concern, and you decide which changes to make.

## Why I Made It

I enjoy writing, and I don't like AI-generated text. But I can't deny that AI is a phenomenal tool in many ways. It can help me spot a mistake, question a claim, or notice where a sentence gets in the way of what I mean. I made Copy Editor to make that kind of help part of my writing process.

This follows the idea in [The Human Border](/notes/the-human-border/): I am happy to use AI as a private tool, while taking responsibility for the words I share with other people. I want to do the writing, make the decisions, and stand behind the result.

## What It Does

- Provides a block editor with Markdown shortcuts, smart typography, autosave, and notes attached to selected text.
- Offers separate passes for copy editing, proofreading, line editing, tightening, reading as a reader, and fact checking. Each preset can be edited or duplicated.
- Keeps a personal rulebook of one-line instructions, with tags and switches for enabling individual rules. Copy editing passes receive every enabled rule, and findings can identify the rule behind them.
- Presents findings beside the draft, with controls for accepting corrections, resolving questions, and dismissing suggestions. Keyboard shortcuts let you work through them in sequence.
- Remembers why a finding was dismissed on a document and supplies that history to later passes. Sharing dismissal examples across documents is optional.
- Saves revisions automatically and lets you create named snapshots, compare changes word by word, and restore an earlier version.
- Exports drafts as Markdown or plain text.

## A Local Writing Workspace

Copy Editor runs in a browser with a server on your own computer. Writing, notes, revisions, and export work without a model account.

AI editing passes use an installed, signed-in Codex CLI or Claude Code. You can choose the provider and model for each run. These passes need an internet connection and send prompt context to the selected provider; the local workspace does not make AI processing offline.

## Get Copy Editor

Copy Editor is open source under the MIT license. It runs on macOS and Linux and requires Git, Python 3.12 or newer, uv, Node.js 20 or newer with npm, and Make.

Clone the repository, install its dependencies, build the browser assets, and start the server:

```sh
git clone https://github.com/totocaster/copy-editor.git
cd copy-editor
make setup
make build
make run
```

Open `http://127.0.0.1:8000` in your browser. Keep the terminal open while using the app; press Ctrl+C to stop the server. On macOS, an optional `ce` launcher makes subsequent starts easier.

The source, full installation instructions, provider setup, and backup guidance live on GitHub: [totocaster/copy-editor](https://github.com/totocaster/copy-editor).
