---
title: "Cataloging a drawer from a photograph"
date: 2026-10-02T22:20:00+04:00
slug: catalog-by-photo
category: progress
---

The catalog of things gets filled from photographs:

1. Snap the shelf, drawer, or open box with its label in frame.
2. Claude reads the label for the [address](/research/ambient-computing/addresses/) and lists the items, counts, and brands.
3. It compares that with what the catalog expects there: new, still here, not seen, or unsure.
4. I confirm with one tap or fix a line.
5. The catalog updates, and the photo stays as evidence of when the place was last seen.

Claude proposes, a person confirms. Anything a photo misses is marked as not seen since that date, never deleted.

The first version needs no new infrastructure: photos go into an inbox folder, Claude Code updates plain files, and I review the change as a git diff. Later, an iOS Shortcut could post one photo to a small service.
