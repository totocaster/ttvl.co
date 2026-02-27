---
title: Universal Content Bundle
date: 2026-02-21
url: /universal-content-bundle/
aliases:
  - /project-humane/universal-content-bundle/
  - /ucb/
description: "a self-describing file bundle format for any type of content"
project:
  year: 2026
  category: /project-humane
  image: /visuals/project-thumbs/proj_ucb.png
---

**Universal Content Bundle** is a file format for packaging any type of content—text, images, data, code, media—into a single self-describing bundle that humans, software, and AI agents can all read and work with. No external dependencies, no proprietary schema registries, no opinions about how the content should look on screen.

## The problem

Content today is trapped in app-shaped containers. A literature review lives in one tool, its source PDF in another, the highlights in a third. A photo essay scatters images across a folder while its captions and sequencing live in an app's database. The content can't describe itself. It depends on the app that created it to make sense.

Universal Content Bundle inverts this: the bundle carries everything needed to understand what's inside. A reader—any reader—can open it and decide how to present it.

## Core principles

1. **Self-contained** — the bundle carries everything needed to understand its content. No external dependencies.
2. **Self-describing** — a manifest describes what's inside, the types, and the relationships. No external schema registry.
3. **Purely declarative** — the bundle says _"I am these things, in these relationships."_ It has zero opinion about rendering.
4. **Renderer-agnostic** — CLI, desktop app, spatial computing, web, AI agent — same bundle, infinite representations. The rendering is the reader's choice.
5. **Semantically atomic** — one bundle = one coherent concept. The boundary is semantic, not technical.
6. **Primitives over binaries** — irreducible content (images, audio, video) stays binary. Everything else is described, not embedded as opaque blobs.

## What a bundle looks like

A bundle is a directory (or a zipped archive for transfer) with a simple structure:

```
my-research.bundle/
  spec.toml           # manifest — required
  content/            # all content files — required
    paper.pdf
    notes.md
    highlights.json
    figures/
      fig1.png
      fig2.png
    experiment/
      run.py
      data.csv
```

The manifest is a TOML file called `spec.toml`. It describes every part of the bundle:

```toml
[bundle]
name = "Understanding Neural Networks"
description = "Literature review with annotated source paper and experimental data"
author = "Toto Tvalavadze"
created = 2026-02-21
version = 1

[[content]]
path = "paper.pdf"
mediatype = "application/pdf"
main = true
description = "Original 2024 paper by Hinton et al."

[[content]]
path = "notes.md"
main = true

[[content]]
path = "highlights.json"
description = "Page-anchored highlights from the source paper"

[[content]]
path = "figures/fig1.png"

[[content]]
path = "experiment/run.py"
description = "Reproduction script for Table 3 results"

[[content]]
path = "experiment/data.csv"
description = "Raw experimental output"
```

Rules are minimal: `[bundle]` metadata is required. Each file gets a `[[content]]` entry with a `path`. Mark primary content with `main = true`. Add `description` when it's not obvious. Omit everything else—consumers infer what they need.

## Bundle examples

**A movie** — video file, subtitles, chapter markers, poster image. Just a film with its context attached.

**A literature note** — source PDF, highlights with page anchors, reader's commentary, bibliographic metadata. The highlights point back to specific locations in the PDF.

**A scientific paper** — full text, figures, raw data, executable scripts, generated charts. A capable reader could re-run the analysis, challenge the conclusions. The paper becomes a living argument with evidence attached.

**An article** — text, embedded images, pull quotes, related links, author bio, revision history. Every piece travels together.

## The separation

Two layers, deliberately independent:

**The bundle** (the standard) — content, manifest, provenance. This is the universal part. It doesn't know or care about any specific application.

**Consumer applications** (implementations) — each reads the manifest, understands the content, and renders it however it sees fit. A CLI tool might list parts and dump text. A desktop app might build a rich multi-pane layout. An AI agent might generate an entirely new representation based on intent. Their architecture is their own business.

The bundle is the truth. The rendering is the consumer's choice.

## Open questions

This is an active design effort. Key questions still being worked through:

- **Packaging**: directory on disk (inspectable, editable) vs. single archive (portable)? Probably both—directory as working format, zipped for sharing.
- **Collaboration**: CRDTs inside the bundle for real-time editing? Or immutable-once-published, where commentary becomes a new bundle referencing the original? [Automerge](https://automerge.org/) is on the radar.
- **Inter-bundle references**: bundles referencing other bundles—embed or link? Content addressing (hash-based) could solve both.
- **Relationship graphs**: how to express connections between parts? Flat triples, typed edges, or anchored references à la the [W3C Web Annotation Data Model](https://www.w3.org/TR/annotation-model/)?

## Prior art

The idea has deep roots. macOS `.bundle` and `.app` directories pioneered the directory-as-file concept. EPUB packages content with an OPF manifest. [IIIF](https://iiif.io/get-started/) describes images and annotations in JSON so any viewer can render them. [Frictionless Data Packages](https://specs.frictionlessdata.io/data-package/) put schema next to data files. Jupyter Notebooks combine code, output, and narrative.

Further back: Ted Nelson's Xanadu imagined documents carrying their own context. Bret Victor's [Explorable Explanations](https://worrydream.com/ExplorableExplanations/) made documents interactive. Alan Kay's Smalltalk objects carried their own behavior. HyperCard bundled content and interaction. More recently, [Ink & Switch](https://www.inkandswitch.com/) (Potluck, Cambria) and Geoffrey Litt (Wildcard, Riffle) have been pushing toward malleable software that adapts to data shapes rather than forcing data into app shapes.

Universal Content Bundle is part of **[Plaintext Commons](/plaintext-commons/)**—continuing the thread that files, not apps, should be the durable layer for knowledge work.
