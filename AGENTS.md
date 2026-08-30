# Repository Agent Guide

This guide gives coding agents the project context, conventions, and workflows needed to work safely and consistently in this repository. Follow it when inspecting, editing, verifying, and publishing changes.

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
- `layouts/partials/` contains shared head, navigation, footer, the project/trace card (`card.html`, which takes `variant: trace` for trace pages), the Campaign Monitor form (`subscribe-form.html`, which takes a per-page `id`), search, lightbox, and home-page components. Partial filenames are kebab-case.
- `assets/scss/style.scss` is an import-only manifest. `_tokens.scss` defines the themed color custom properties, `_variables.scss` holds the Sass type/spacing/width/stacking values, `_base.scss` and `_layout.scss` hold the document shell, `components/` holds patterns shared by two or more sections, and `sections/` holds page-specific composition. `assets/scss/membership.scss` is a separate stylesheet for the Membership page.
- Hugo Pipes compiles/minifies SCSS and minifies/fingerprints most JavaScript. There is no separate npm build step.
- Dark mode follows `prefers-color-scheme`; there is no manual theme toggle.
- The narrow navigation is a horizontally scrollable CSS row; there is no mobile-menu JavaScript.
- Pages can set `content_css` frontmatter to add a class to their `article` element; `about` is the only value in use.

### Design standard

- Themed colors come exclusively from the custom properties in `assets/scss/_tokens.scss` (`--ground`, `--ink`, `--ink-muted`, `--ink-faint`, `--rule`, `--edge`, `--surface`, `--surface-input`, `--highlight`). Dark mode and high contrast override tokens only, never component rules. Deliberate exceptions are commented in place: over-photo chrome, the viewers' media wells, and print.
- Color encodes role; reserve opacity for state (hover, disabled), never for establishing a text tier.
- Type, spacing, widths, and motion values come from `assets/scss/_variables.scss`. Full-viewport layers use `$z-overlay`/`$z-search` instead of literal z-indexes.
- Put a style in `assets/scss/components/` when two or more sections use it, and in `assets/scss/sections/` when one does.

### Browser features

- Search is available on layouts using the shared head. `?` opens the overlay when focus is not in an input, textarea, or editable element. Arrow keys select results, Enter follows one, Escape closes, and Tab remains trapped in the dialog.
- `layouts/index.json` indexes regular pages whose Hugo type is neither `page` nor `json`. This includes section content but excludes standalone root pages such as About and Colophon.
- Notes and Projects share `assets/js/category-filter.js` for query-string category filtering (`.category-filter` rail, `data-filter-group` sections, `data-category` items, `data-filter-show` per-state elements). The projects rail is driven by hub `_index.md` frontmatter: `filter_label` (chip name), `filter_dek` (one-line description shown while filtered), `filter_ref` (name of the arrow reference to the hub), and `filter_weight` (rail position; unweighted hubs sort alphabetically). Individual note pages compute backlinks from internal links at build time.
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

- `resources`: manifest of files and external sources from a Markdown-style link list; file rows read type and size from `static/` at build time (↓), external rows name their destination (↗). Trailing text after a link renders as a muted note. Pages can also declare a `resources:` frontmatter list (title + url) to render a chip strip of canonical links under the title.
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

## Editorial style

### Authorities

- Use [The Chicago Manual of Style, 18th Edition](https://www.chicagomanualofstyle.org/) as the default authority for grammar, punctuation, capitalization, numbers, titles, and other general editorial questions.
- For technical content, supplement Chicago with the [Google developer documentation style guide](https://developers.google.com/style). Use Google’s guidance for technical voice, document structure, procedures, code examples, and developer terminology.
- Use the [Merriam-Webster.com Dictionary](https://www.merriam-webster.com/) as the default authority for spelling and word forms.
- Follow explicit repository house rules when they differ from any external authority. For technical content not covered by a house rule, Google’s guidance takes precedence over Chicago. Record each exception in this section so future editing remains consistent.

### Titles and headings

- Use sentence case for Note page titles because they are primarily statements rather than conventional titles. Use Chicago-style Title Case for every other page title and heading, including headings within Notes.

### In-house dictionary

Use the forms below even when Merriam-Webster or a source uses another form. Entries are alphabetical, with one headword per entry. Preserve the original wording in direct quotations and the official styling of names and titles.

- **3D** *(noun or adjective)*: use this exact capitalization.
- **agent-friendly** *(adjective)*: hyphenate.
- **AI** *(noun or adjective)*: use this exact capitalization.
- **bookbinding** *(noun)*: write as one word.
- **bookmaking** *(noun)*: write as one word; use for the craft of making books.
- **CLI** *(noun or adjective)*: use this exact capitalization.
- **command line** *(noun)*: write as two words.
- **command-line** *(adjective)*: hyphenate.
- **email** *(noun or verb)*: write without a hyphen.
- **file-first** *(adjective)*: hyphenate.
- **file-native** *(adjective)*: hyphenate.
- **fine art** *(noun)*: write as two words.
- **fine-art** *(adjective)*: hyphenate.
- **Flâneur** *(proper name)*: preserve the capitalization and diacritic.
- **GitHub** *(proper name)*: preserve this capitalization.
- **handbound** *(adjective)*: write as one word without a hyphen.
- **human-computer interaction** *(noun)*: hyphenate **human-computer**.
- **iOS** *(proper name)*: preserve this capitalization.
- **keyboard-friendly** *(adjective)*: hyphenate.
- **local-first** *(adjective)*: hyphenate.
- **macOS** *(proper name)*: preserve this capitalization.
- **Obsidian** *(proper name)*: preserve this capitalization.
- **photobook** *(noun)*: write as one word.
- **plain text** *(noun)*: write as two words.
- **plain-text** *(adjective)*: hyphenate.
- **Plaintext Commons** *(proper name)*: preserve this spelling and capitalization.
- **plugin** *(noun)*: write as one word without a hyphen.
- **realtime** *(noun or adjective)*: write as one word without a hyphen.
- **set up** *(verb)*: write as two words.
- **setup** *(noun)*: write as one word.
- **website** *(noun)*: write as one word.
- **work in progress** *(noun)*: write as three words.
- **work-in-progress** *(adjective)*: hyphenate.

#### Preferred usage

- **everyone**: prefer over **everybody**.
- **someone**: prefer over **somebody**.
- **toward**: prefer over **towards**.

### Measurements, dimensions, and ranges

- Follow the [NIST Guide to the SI](https://www.nist.gov/pml/special-publication-811/nist-guide-si-chapter-7-rules-and-style-conventions-expressing-values) for unit spacing: put a space between the number and unit symbol, as in `0.5 mm`, `600 mL`, `8 km`, and `39.6 °C`.
- Plane angles are the spacing exception: write `45°` with no space. Use the degree sign (`°`), not the masculine ordinal indicator (`º`). For Celsius, `°C` is the complete unit symbol and still takes a preceding space: `39.6 °C`.
- Use the multiplication sign for dimensions: `10 × 22 m`, not `10 x 22 m`.
- Express every range with an en dash: `8–10 days`, `2025–26`, and `0.5–3.0 mm`. When both endpoints share a measurement unit, place it only after the second value.
- Keep established photographic format names closed: `35mm film`, `120 film`, `4×5`, and `6×17`.
- Preserve native syntax in code, CSS, filenames, URLs, postal addresses, and official product names.

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
