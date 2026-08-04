# Repository Agent Guide

This is the canonical guidance for coding agents working in this repository. `AGENTS.md` is a symlink to this file, so editing `CLAUDE.md` updates both entry points.

## Project overview

ttvl.co is Toto Tvalavadze's Hugo-based public notebook and project archive. Its main subjects are analog photography, bookbinding, notebook systems, humane interfaces, Obsidian tools, creative writing, and a monthly work log.

The repository has no Node/npm toolchain, package manifest, or theme. Hugo Extended renders Markdown, compiles SCSS, and processes the site's vanilla JavaScript. Third-party browser code consists of a vendored `model-viewer` module plus hosted Campaign Monitor and Memberful scripts on the pages that need them.

## Essential commands

```bash
# Development
hugo server -D              # Include content marked as draft
hugo server                 # Published content only

# Production-equivalent build
sh ./tools/build-production.sh

# Direct build without cleaning public/
HUGO_SITE_UPDATE=$(git rev-list --count HEAD) hugo --destination ./public
```

`tools/build-production.sh` is the deployment entry point. It unshallows Git when necessary, derives `HUGO_SITE_UPDATE` from the commit count, removes `public/`, and invokes Hugo. There are no custom archetypes, so `hugo new` only supplies Hugo's generic frontmatter; copy a nearby content file when its schema matters.

## Architecture

### Content and canonical URLs

- Monthly logs: `content/log/YYYY-MM.md` → `/log/YYYY/MM/` from the page date.
- Flaneur dispatches: `content/flaneur/NNN.md` → `/flaneur/NNN/` and `/flaneur/NNN/email.html`.
- Newsletter landing/archive: `content/newsletter/_index.md` → `/newsletter/`.
- Photography: `content/darkroom/*.md` → `/darkroom/…/`.
- Bookbinding: `content/bookbinding/*.md` → `/bookbinding/…/`.
- Notes: `content/notes/*.md` → `/notes/…/`; `/writings/` and `/essays/` are legacy aliases.
- Obsidian: `content/obsidian/*.md` → `/obsidian/…/`.
- Project Humane: `content/project-humane/*.md` → `/project-humane/…/`.
- Unbound Notebook System: the section index is canonical at `/project-humane/notebook-system/`; child guides currently remain under `/notebook-system/…/`.
- Projects archive: `content/projects/_index.md` discovers pages and sections with `project` frontmatter.
- Loose Leaves: `content/leaves/_index.md` renders date-prefixed JPEG files from `static/leaves/`; there are no per-leaf Markdown pages.
- Traces: `content/traces/*.md` → `/traces/…/` for scans, photographs, documents, and spatial records.

Prefer canonical internal paths with trailing slashes. Do not add aliases unless an intentional short URL or a real historical URL must remain valid. Preserve existing aliases when moving content.

The A–Z index ignores the initial English articles `A`, `An`, and `The` when sorting and grouping titles, while displaying each title unchanged. Set `sort_title` in a page's frontmatter to supply an explicit filing title when the automatic behavior is not appropriate.

### Hugo configuration and output

- `hugo.toml` owns the base URL, language, log permalink, output formats, Memberful checkout URLs, and site version.
- Memberful plan IDs are `121779` for monthly membership and `121780` for yearly membership.
- Home emits HTML, RSS, and the JSON search index. Hugo also generates `sitemap.xml` and `robots.txt`; there is no tracked `static/robots.txt`.
- The `email` output format is declared globally, while every Flaneur dispatch currently opts into `HTML` and `email` in its frontmatter.
- Goldmark unsafe rendering is enabled because content includes trusted inline HTML.
- The custom RSS template includes Log, Darkroom, Bookbinding, Notes, Flaneur, Project Humane, and Obsidian content.
- `data/` is currently unused except for `.gitkeep`.

### Templates and assets

- `layouts/_default/baseof.html` is the standard shell; section layouts override list or single rendering through Hugo's lookup order.
- `layouts/partials/` contains shared head, navigation, footer, cards, subscription forms, search, lightbox, and home-page components.
- `assets/scss/style.scss` is the main entry point. `assets/scss/membership.scss` is a separate stylesheet for the Membership page.
- Hugo Pipes compiles/minifies SCSS and minifies/fingerprints most JavaScript. There is no separate npm build step.
- Dark mode follows `prefers-color-scheme`; there is no manual theme toggle.
- The narrow navigation is a horizontally scrollable CSS row; there is no mobile-menu JavaScript.

### Browser features

- Search is available on layouts using the shared head. `?` opens the overlay when focus is not in an input, textarea, or editable element. Arrow keys select results, Enter follows one, Escape closes, and Tab remains trapped in the dialog.
- `layouts/index.json` indexes regular pages whose Hugo type is neither `page` nor `json`. This includes section content but excludes standalone root pages such as About and Colophon.
- Notes use `assets/js/notes-filter.js` for query-string category filtering. Individual note pages compute backlinks from internal links at build time.
- The lightbox is loaded for Loose Leaves and pages with `lightbox: true`; it supports Escape, arrow keys, backdrop close, focus trapping, and focus restoration.
- Text Fragments are feature-detected through `document.fragmentDirective`. Selecting 6–499 characters updates the URL; `Cmd/Ctrl+Shift+L` updates it from the current selection, and Escape clears a live selection. There is no polyfill.
- The pronunciation control is loaded only when `pronunciation_audio` is set.
- The vendored `model-viewer` `4.3.1` module is loaded only when `model_viewer: true` is set.

## Content workflows

### Flaneur dispatches

1. Copy the latest issue to the next zero-padded number, such as `content/flaneur/015.md`.
2. Set `title`, `description`, `date`, and `outputs: ["HTML", "email"]`.
3. Store dispatch images under `static/flaneur/`.
4. Use `flaneur-gallery` for responsive image groups.
5. Verify both `/flaneur/015/` and `/flaneur/015/email.html`, including absolute image resolution and Campaign Monitor compatibility.

The archive itself is `/newsletter/`; do not treat `/flaneur/` as the canonical archive URL.

### Monthly logs

- Use the filename `content/log/YYYY-MM.md` and the title `YYYY.MM`.
- Set `date` to a date inside the represented month. For new entries, use the month's final calendar day so the permalink and ordering are unambiguous.
- Put the public bullet summary immediately after frontmatter. The log layouts render full page content; they do not depend on a `summary` frontmatter field.
- Use `-` bullets with one hierarchy level, canonical internal links, `_italics_`, and `**names**` where appropriate.
- Preserve or leave room for manually written prose after the bullets.

When journal text is supplied for summarization, use this instruction:

> Act as somebody who summarizes journal entries into publicly shareable bullet points of things created, made, or done. Generate bullet points of major events and projects from first person perspective. Everything that could be of interest to others about what was produced or made should be mentioned. Omit overly personal details. Reference previous months if relevant but keep self-contained. Output in Markdown with single-level lists only (no sublists).

### Projects

Pages participate in `/projects/` through nested frontmatter:

```yaml
date: 2026-07-13
description: "Page-level summary"
featured: true # optional home-page placement
project:
  year: 2026 # or: ongoing
  category: /obsidian
  description: "Short card description"
  image: /visuals/project-thumbs/example.png
```

Use `project.category: /obsidian` for Obsidian work, `/project-humane` for Project Humane, `/darkroom` for photography tooling, and `/bookbinding` for bindery tools. Store card images in `static/visuals/`, usually `static/visuals/project-thumbs/`.

Project Humane pages normally live in `content/project-humane/`. Obsidian pages are the deliberate exception: even when philosophically related to Project Humane, they live in `content/obsidian/` and use `/obsidian/…/` canonical URLs.

### Obsidian hub

- New Obsidian project pages belong in `content/obsidian/project-name.md`.
- Update `content/obsidian/_index.md` in the same change so its explicitly ordered `project-grid` groups remain current.
- Use canonical hub paths such as `/obsidian/triage/`, not legacy short aliases.
- Add an alias only when a deliberate short URL is worth preserving; do not remove existing compatibility aliases.

### Notes

- Put notes in `content/notes/` and use one supported category: `collected`, `thinking`, or `longform`.
- A missing category is treated as `thinking` by the list template.
- Link to another note by its canonical `/notes/slug/` path so the build-time backlink detector can find it.

### Photography, downloads, and visual assets

- Put Darkroom articles in `content/darkroom/` with descriptive page and `project` metadata when they should appear in the Projects archive.
- Store content images under `static/visuals/<section>/`; Flaneur and Loose Leaves are the established `static/flaneur/` and `static/leaves/` exceptions.
- Store PDFs, printable files, and STL downloads in `static/downloads/`. Downloadable Trace assets such as GLB files live in `static/traces/`.
- Keep technical photography images at the quality their subject needs. For general page images, aim for no more than 2000 pixels wide unless the page needs more detail.

### Loose Leaves and Traces

- Loose Leaves images must use `YYYY-MM-DD-description.jpeg`; the list template extracts the date and sorts filenames newest first.
- A page using `photo-gallery` must also set `lightbox: true` until script loading is coupled directly to the shortcode.
- A page using `model-viewer` must set `model_viewer: true` and supply shortcode `src`, `poster`, and accessible `alt` values.

## Shortcodes

- `download-section`: styled box around Markdown download links.
- `flaneur-gallery`: responsive newsletter image grid.
- `membership-link`: link to `params.membershipURL`.
- `model-viewer`: interactive GLB viewer with poster, caption, download, and no-JavaScript fallback.
- `photo-gallery`: linked-image gallery prepared for the lightbox.
- `project-grid`: explicitly ordered project-card group from a comma-separated `pages` parameter.
- `pronunciation-name`: accessible audio pronunciation control.
- `toc`: current page's generated table of contents.
- `youtube`: lazy-loaded responsive video embed.

## Site versioning and deployment

- The footer format is `vMAJOR.MINOR.UPDATE`.
- The configured site era is currently `v7.7` under `[params.version]` in `hugo.toml`.
- `MAJOR` identifies the site era. Change `MINOR` only for a visible site-structure or publishing-system revision, not for routine content.
- `UPDATE` is the repository commit count supplied through `HUGO_SITE_UPDATE` by `tools/build-production.sh`.
- `params.version.update` is only a fallback for direct local Hugo invocations and can lag behind Git history.
- DigitalOcean App Platform watches `main`, uses Hugo Extended `0.164.0`, and runs `sh ./tools/build-production.sh`.
- There is no `.github/` workflow or automated test suite in this repository.

## Conventions

1. Keep the site content-first and avoid adding a Node/npm pipeline without a concrete need.
2. Use descriptive titles and descriptions for search/social metadata.
3. Preserve semantic HTML, visible focus behavior, keyboard access, system dark mode, and high-contrast support.
4. Prefer browser-native features with graceful feature detection over polyfills.
5. Minimize third-party requests and optimize images before committing them.
6. Preserve unrelated working-tree changes and generated directories.

## Verification

There are no automated tests. Match verification to the change:

1. Run `hugo server -D` and inspect affected pages at multiple widths.
2. Run `sh ./tools/build-production.sh` and investigate new build warnings.
3. Exercise `?` search, keyboard navigation, and focus restoration when shared layout or JavaScript changes.
4. Emulate light and dark `prefers-color-scheme`; there is no theme toggle.
5. Check Notes filtering/backlinks, lightbox controls, Text Fragment URLs, or pronunciation when touching those features.
6. Verify both browser and email outputs for Flaneur changes.
7. Inspect `/index.json`, `/index.xml`, aliases, redirects, `robots.txt`, and `sitemap.xml` when changing outputs or routing.
