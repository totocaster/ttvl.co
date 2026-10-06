---
title: "The studio catalog starts as plain files"
date: 2026-10-02T22:40:00+04:00
slug: catalog-as-files
category: progress
---

The catalog behind the studio twin, the one I'll fill by [photographing drawers](/research/ambient-computing/catalog-by-photo/), starts as a folder of plain files rather than a database:

```text {title="inventory/"}
places.json       # generated from the 3D model, one record per slot
movables.json     # boxes and carts, and where each one is
items.jsonl       # one line per thing: name, English and Italian aliases, category, place, count, last seen
captures/
  inbox/          # new photos
  2026-10-02/     # photos and what Claude read, before confirmation
```

The places come out of the model build, so they never drift from the 3D model. Each thing is one line, so every change is a readable diff. Claude reads a photo and edits the files; I review the change as a git diff and confirm it, the same way I review code. Nothing needs a server until the phone app does.
