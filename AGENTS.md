# Repository Agent Guide

This guide gives coding agents the project context, conventions, and workflows needed to work safely and consistently in this repository. Follow it when inspecting, editing, verifying, and publishing changes.

## Project overview

ttvl.co is Toto Tvalavadze's Hugo-based public notebook and project archive. Its main subjects are analog photography, bookbinding, notebook systems, humane interfaces, Obsidian tools, creative writing, a research journal, and a monthly work log.

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

# Social cards: render the ones that are missing (macOS; reads IBM Plex from ~/Library/Fonts)
make cards
make cards-check                        # list missing and stale cards without rendering

# Research journal: start a dated entry in a stream
make entry STREAM=ambient-computing SLUG=four-corners
```

`make` lists every target: `serve`, `serve-drafts`, `build`, `entry`, the `cards` family, and `hooks`, which installs a pre-commit hook that refuses commits with missing or stale cards. Python tools under `tools/` declare their dependencies inline and run through `uv run`; nothing is installed into the system Python.

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
- Research journal: `content/research/_index.md` → `/research/`; each stream is a subsection, `content/research/<stream>/_index.md` → `/research/<stream>/`; entries are `content/research/<stream>/YYYY-MM-DD-slug.md` → `/research/<stream>/<slug>/` from their `slug` frontmatter.

Prefer canonical internal paths with trailing slashes. Do not add aliases unless an intentional short URL or a real historical URL must remain valid. Preserve existing aliases when moving content.

The A–Z index ignores the initial English articles `A`, `An`, and `The` when sorting and grouping titles, while displaying each title unchanged. Set `sort_title` in a page's frontmatter to supply an explicit filing title when the automatic behavior is not appropriate. Research entries stay out of the index, like Log months. Start Here lists only the pages named in `hub_sections` in `content/a-z.md`, in that order: hubs the masthead does not reach, and the Ambient Computing stream.

### Hugo configuration and output

- `hugo.toml` owns the base URL, language, log permalink, output formats, Memberful checkout URLs, and site version.
- Memberful plan IDs are `121779` for monthly membership and `121780` for yearly membership.
- Home emits HTML, RSS, the JSON search index, and `social.json`, the social-card manifest rendered by `layouts/index.social.json`. `hugo --renderSegments social` builds only that manifest, which is how `tools/social-cards.py` reads the site. Hugo also generates `sitemap.xml` and `robots.txt`; there is no tracked `static/robots.txt`.
- The `email` output format is declared globally, while every Flaneur dispatch currently opts into `HTML` and `email` in its frontmatter.
- Goldmark unsafe rendering is enabled because content includes trusted inline HTML.
- The custom RSS template includes Log, Darkroom, Bookbinding, Notes, Flaneur, Project Humane, and Obsidian content. Research stays out of it and publishes its own feeds through `layouts/research/rss.xml`: `/research/index.xml` for every stream and `/research/<stream>/index.xml` for one. The hub and each stream opt in with `outputs: ["HTML", "RSS"]`.
- `data/square-crops.json` supplies the point of interest and aspect ratios shared by the square-crops diagram and its static image renderer.

### Templates and assets

- `layouts/_default/baseof.html` is the standard shell; section layouts override list or single rendering through Hugo's lookup order. `layouts/flaneur/baseof.html` has a deliberately bare head: dispatch HTML pages are the source the mailing system ingests, not pages to share.
- `partials/head.html` writes the `<title>` as `Page · Toto Tvalavadze` and resolves the Open Graph image. An explicit `image` frontmatter value wins; otherwise the page's own card at `static/social/<permalink>.png` or `.jpg`, then `social/projects` for pages with `project` frontmatter, then the card of the page's own section (a research entry uses its stream's), then the top-level section hub card, then `social/site`. The URL carries a content hash so scrapers refetch a regenerated card. Hugo warns at build time when a note, project page, article, hub, research stream, or the home page lacks its own card, but still ships the fallback.
- `layouts/partials/` contains shared head, navigation, footer, the project/trace card (`card.html`, which takes `variant: trace` for trace pages), the Campaign Monitor form (`subscribe-form.html`, which takes a per-page `id`), search, lightbox, and home-page components. Partial filenames are kebab-case.
- `assets/scss/style.scss` is an import-only manifest. `_tokens.scss` defines the themed color custom properties, `_variables.scss` holds the Sass type/spacing/width/stacking values, `_base.scss` and `_layout.scss` hold the document shell, `components/` holds patterns shared by two or more sections, and `sections/` holds page-specific composition. `assets/scss/membership.scss` is a separate stylesheet for the Membership page.
- Hugo Pipes compiles/minifies SCSS and minifies/fingerprints most JavaScript. There is no separate npm build step.
- Dark mode follows `prefers-color-scheme`; there is no manual theme toggle.
- The narrow navigation is one line that scrolls sideways with a fade at the right edge; a one-line script in `partials/header.html` scrolls the current section into view. There is no mobile menu.
- Pages can set `content_css` frontmatter to add a class to their `article` element; `about` is the only value in use. `head_title` replaces the page title in the head (About opens with its sentence) and `head_dek` replaces or, when empty, removes the dek.
- Markdown tables render via `_markup/render-table.html`: a 1 px ink rule under the header row and `--rule` hairlines between rows, no frame, cells at 16/23, wrapped for horizontal scroll on narrow screens. Tables sit at prose width; append `{.wide}` after a table (Goldmark block attributes are enabled) to span the container. Right-aligned columns get tabular numerals. Use the `Command | What it does` shape for CLI references.
- Code fences tagged `sh`/`bash`/`shell`/`zsh` render as dark terminal blocks via `_markup/render-codeblock-*.html` and `partials/shell-block.html`: each command's `$` prompt is a quiet copy button (`assets/js/shell-copy.js`, loaded only on pages with shell blocks), continuation lines after a trailing backslash carry no prompt, and `#` comment lines render faint. Every other fence renders as a sheet via `_markup/render-codeblock.html` and `components/_sheet.scss`: the terminal's geometry in page materials (`--surface` fill, `--edge` hairline), following the theme. Chroma runs with `noClasses = false` and no stylesheet, so tagged fences look like untagged ones except that comments render faint; on untagged fences a trailing annotation set off by two spaces and `#` gets the same treatment. A fence attribute such as ```` ```toml {title="manifest.toml"} ```` prints a filename band above the block. Long lines scroll inside the frame with a right-edge fade while there is more to scroll.

### Design standard

`docs/styleguide.md` is the visual standard, called Panel (v8.0, 2026-10): principles, the two IBM Plex families and their voices, tokens with their contrast ratios, the spacing scale and rhythm, the rail-and-column layout, and every shared pattern (masthead, page head, block, rows, cards, doors, buttons and forms, legends, end matter, media chrome), plus a page-by-page map. Read it before adding a page type, a list, or a component. The rules below are its short form.

- Content over chrome: body text is full ink at 18/28; metadata is 14/20 and faint, prose section headings are 22/30, and control labels are 16/24. Every text tier passes 4.5:1 in both themes, and nothing is smaller than 14 px. No uppercase labels, no letter-spacing.
- The rail carries the metadata: a page head and every block are a 192 px rail (label, date, count, kind) beside an 880 px column within the 1200 px outer container. The rail stacks at 1024 px; metadata stays in the rail, while deks and resource links may sit under a title. A page carries one count at most, in its head rail (`page-meta.html`); block rails, home blocks, and end matter carry none (the Projects switches, being controls, carry each hub's count). Viewers, galleries, and `{.wide}` tables span the full page when the rail beside the body is empty. Templates build blocks from `partials/page-head.html` (rail lines from `page-meta.html`), `partials/block-body.html` for an article body, and the `section`, `page-list`, and `project-grid` shortcodes for authored pages and hubs.
- Words in Plex Sans, numbers in Plex Mono: dates are `<time>`, other numbers in the chrome are `<span class="n">` (`partials/count.html` and `numerals.html` help). Labels are sentence case.
- One way to do each thing: every list is `partials/row.html` (meta column, title with one tail inline after it; no hairlines, 4 px apart, the key right-aligned in the rail on wide screens); on wide screens a list's meta column is the rail itself and nothing groups rows inside a block, so a year, a stream, or a kind of record is a block of its own (a ledger block, `components/_block.scss`); cards are `partials/card.html` (quiet at rest, the tile a key under the hand); articles end with `partials/mentioned-in.html`; the subscribe form is `subscribe-form.html` with `subscribe-legend.html`; a `p.legend` explains the thing directly above it.
- A hairline sits only under the masthead; lists are held by space. Frames stay on tiles, tables, sheets, and the quotation. Buttons are blocks on hard offset shadows (`components/_control.scss`); the door strip under a title is one joined row on one shadow.
- Themed colors come exclusively from the custom properties in `assets/scss/_tokens.scss` (`--ground`, `--ink`, `--ink-muted`, `--ink-faint`, `--rule`, `--edge`, `--surface`, `--surface-input`, `--highlight`, `--signal`, and the `--term*` terminal set). Dark mode and high contrast override tokens only, never component rules. Deliberate exceptions are commented in place: controls over photographs, the viewers' media wells, the terminal, and print.
- Type, spacing (`$space-1` to `$space-9`, 4 to 96 px), widths, and motion values come from `assets/scss/_variables.scss`. Full-viewport layers use `$z-overlay`/`$z-search` instead of literal z-indexes.
- Put a style in `assets/scss/components/` when two or more sections use it, and in `assets/scss/sections/` when one does. The media chrome (viewers, clip, pronunciation) lives in `components/_model-viewer.scss`.
- Fonts are self-hosted subsets under `static/fonts/plex/` (six WOFF2 files, about 154 KB), declared in `assets/scss/_fonts.scss` and preloaded from `partials/head.html`. Regenerate them with `pyftsubset` (through `uvx --from fonttools --with brotli pyftsubset`) from the OTFs in `~/Library/Fonts` when a glyph is missing.

### Browser features

- Search is available on layouts using the shared head. `?` opens the overlay when focus is not in an input, textarea, select, or editable element, as does the `Search ?` button in the masthead. The overlay has a visible label, a Close key, and a live status line; Escape and Close return focus to the opener. Arrow keys select results, Enter follows one, Escape closes, and Tab remains trapped in the dialog.
- `layouts/index.json` indexes regular pages whose Hugo type is neither `page` nor `json`. This includes section content but excludes standalone root pages such as About and Colophon. The overlay renders results as rows (section, title, summary, date).
- `layouts/404.html` is the not-found page; DigitalOcean serves it for unknown paths.
- Notes and Projects share `assets/js/category-filter.js` for query-string category filtering (the Research hub has one block per stream instead): Notes with a `.category-filter` chip rail, Projects with one switch per hub (`.switches`, `components/_switch.scss`, which the Index's Start Here reuses as door tiles; each face is a `[data-filter-control]` button that filters and releases on a second press, the door under it opens the hub). Items carry `data-category` inside `data-filter-group` sections; a group the filter empties is hidden by one rule in `components/_filter-nav.scss`. The switches come from hub `_index.md` frontmatter: `filter_label` (the switch's name), `filter_dek` (its dek, also the hub's dek on the Index and the social cards), and `filter_weight` (order; unweighted hubs sort alphabetically). The head rail's count (`.count` with `data-singular`/`data-plural`, from `count.html` with `live`) follows the filter. Every article computes "Mentioned In" rows from internal links at build time (`partials/mentioned-in.html`), including content paths named in `page-list` and `project-grid`.
- The lightbox is loaded for Loose Leaves and pages with `lightbox: true`; it supports Escape, arrow keys, backdrop close, focus trapping, and focus restoration.
- Research entry pages and Log months map the Left and Right arrow keys to their end-matter pager (In This Stream, In the Log). The keys are ignored in fields and media players, with modifiers, and while text is selected.
- Text Fragments are feature-detected through `document.fragmentDirective`. Selecting 6–499 characters updates the URL; `Cmd/Ctrl+Shift+L` updates it from the current selection, and Escape clears a live selection. There is no polyfill.
- On pages with a contents rail, `assets/js/toc-spy.js` marks the entry whose section is in view with `aria-current` (the lamp), updated on scroll.
- The pronunciation control is loaded only when `pronunciation_audio` is set.
- The vendored `model-viewer` `4.3.1` module is loaded only when `model_viewer: true` is set.
- Gaussian splats use vendored Spark `2.1.0` and Three.js `0.180.0`, loaded only when `gaussian_splat: true` is set.

## Content workflows

### Flaneur dispatches

1. Copy the latest issue to the next zero-padded number, such as `content/flaneur/015.md`.
2. Set `title`, `description`, `date`, and `outputs: ["HTML", "email"]`.
3. Store dispatch images under `static/flaneur/`.
4. Use `flaneur-gallery` for responsive image groups.
5. Verify both `/flaneur/015/` and `/flaneur/015/email.html`, including absolute image resolution and Campaign Monitor compatibility.

The archive itself is `/newsletter/`; do not treat `/flaneur/` as the canonical archive URL.

### Monthly logs

- Use the filename `content/log/YYYY-MM.md` and the title `YYYY-MM`. Templates write ISO dates everywhere; the dot notation (`2024.12.22.R6`) is a personal ID system for prose only.
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

Write `description` and `project.description` as sentences, with a capital first letter and a final period: they appear as deks under row and card titles, in meta descriptions, and on social cards.

Use `project.category: /obsidian` for Obsidian work, `/project-humane` for Project Humane, `/darkroom` for photography tooling, and `/bookbinding` for bindery tools. Store card images in `static/visuals/`, usually `static/visuals/project-thumbs/`. The same image becomes the page's social card; run `make cards` after adding or replacing it.

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
- After adding a note, run `make cards` and commit its card under `static/social/notes/`.

### Social cards

Every note, project page, article, hub with a `filter_dek`, research stream, and the home page has a 1200 × 630 Open Graph card under `static/social/`, committed to the repository. An article is any other regular page inside a section except Log months, Traces, research entries, and Flâneur dispatches, such as a Darkroom essay or a notebook guide. Cards are rendered locally, never on the build server.

- Run `make cards` (`uv run tools/social-cards.py`) after adding a note, project page, article, or research stream, or after changing a title, date, category, description, or poster. It builds the manifest through Hugo, renders only the cards that are missing, and updates `static/social/manifest.json`. Commit the new files with the content change; `make hooks` installs a pre-commit hook that refuses a commit while cards are missing or stale.
- `make cards-check` lists missing, stale, and orphaned cards without rendering; `make cards-stale` also re-renders cards whose inputs changed; `make cards-all` re-renders everything after a design change (bump `DESIGN_VERSION` in the script when the design changes); `uv run tools/social-cards.py --only /notes/walking/` limits a run, and `--drafts` includes draft pages.
- Card voices: every text card (notes, articles, hubs, research streams, the site) is the Panel ledger: a rail at left with the date in Plex Mono and the section and kind in Plex Sans, a signal square with `ttvl.co`, then the title and the dek in the column, the signature at the bottom, and one rule across. Projects put the rail and title at left and the poster from `project.image` on a framed surface well at right (JPEG). Hub deks come from `filter_dek`; the site dek from `params.description` in `hugo.toml`. Give every article a `description`, since a card without one is a bare title.
- Flaneur dispatches get no card: their HTML pages are email sources with no metadata. The plate and engraving renderers remain in the script, dormant, and the manifest template says how to re-enable them.
- Rendering needs the IBM Plex OTFs (Sans Regular, Medium, SemiBold; Mono Regular) in `~/Library/Fonts` (override the folder with `SOCIAL_CARDS_FONT_DIR`). uv provisions Python and Pillow from the script's inline metadata.
- Log months fall back to the Log hub card, and research entries to their stream's card. About, Colophon, AI, and other root pages fall back to the site card. Traces set `image` in frontmatter and keep it.

### Research journal

- `/research/` is a working journal of short, dated entries: what was tried, found, or asked. Arguments and opinions belong in Notes.
- Streams are subsections. A stream's `_index.md` sets `title`, `description` (the hub dek and the card dek), `status` (`active`, `paused`, or `concluded`), `weight` (order on the hub), and `outputs: ["HTML", "RSS"]`, plus an optional `bench` list of `[label, text]` pairs describing the current apparatus. Its body is the stream's brief. Current streams: `ambient-computing` and `tools-for-thought`; plain-text systems belong to Tools for Thought.
- Start an entry with `make entry STREAM=<stream> SLUG=<slug>` (`tools/new-entry.sh`). It writes `YYYY-MM-DD-<slug>.md` with `date` (local time and offset), `slug`, and `category`. Keep `slug`: it sets the URL, and the filename's date prefix only orders the folder.
- `category` is one of `finding`, `progress`, `question`, or `reading`. Hugo reserves `kind`, so do not use it.
- `answers:` names a question in the same stream by slug or filename (one value or a list) and closes it. Unanswered questions collect under Open Questions on the stream page; an entry page lists Answers, Answered in, and Referenced by rows, the last from any page whose text links to it.
- Entry numbers (001, 002, …) come from date order within the stream. Never write them; a backdated entry renumbers the ones after it.
- Store media in `static/visuals/research/<stream>/`. Use Hugo's built-in `figure` shortcode for images and `clip` for short silent loops (an MP4 with a JPEG poster frame).
- The stream page shows every entry in full, newest first, so a stream reads as one page. The hub lists the streams with their activity pulse, then one block per stream with rows `date | title | 024 · Question`; there is no filter. On an entry page, the Left and Right arrow keys follow the previous and next links within the stream (`assets/js/pager.js`, loaded only on entry pages and Log months).
- Entries have no social card of their own and use their stream's. Run `make cards` after adding or retitling a stream.

### Photography, downloads, and visual assets

- Put Darkroom articles in `content/darkroom/` with descriptive page and `project` metadata when they should appear in the Projects archive.
- Store content images under `static/visuals/<section>/`; Flaneur and Loose Leaves are the established `static/flaneur/` and `static/leaves/` exceptions.
- Store PDFs, printable files, and STL downloads in `static/downloads/`. Downloadable Trace assets such as GLB files live in `static/traces/`.
- Keep technical photography images at the quality their subject needs. For general page images, aim for no more than 2000 pixels wide unless the page needs more detail.

### Loose Leaves and Traces

- Loose Leaves images must use `YYYY-MM-DD-description.jpeg`; the list template extracts the date and sorts filenames newest first, and tags leaves that share a day `/1`, `/2`, … in the order shown.
- A page using `photo-gallery` must also set `lightbox: true` until script loading is coupled directly to the shortcode.
- A page using `model-viewer` must set `model_viewer: true` and supply shortcode `src`, `poster`, and accessible `alt` values.

## Shortcodes

- `resources`: manifest of files and external sources from a Markdown-style link list, rendered as plates (`.files`, `components/_resources.scss`): file plates read type and size from `static/` at build time and end in `Download ↓`, external plates name their destination and host (↗). Trailing text after a link renders as a muted note. A file link inside a paragraph renders as an inline key with its type and ↓. Pages can also declare a `resources:` frontmatter list (title + url) to render a chip strip of canonical links under the title.
- `flaneur-gallery`: responsive newsletter image grid.
- `page-list`: a block of rows for a hub from a comma-separated `pages` parameter (content paths), each showing the page's date, title, and `description` as a dek. `title` names the block in the rail, `lead` adds a sentence in the rail, `meta` a meta line (no count by default), and `id` the anchor (it defaults to the anchorized title). Titles come from the pages, so they can't drift; hubs no longer write `##` headings around it. Records its pages so the hub's rail can count them.
- `section`: a paired shortcode for Markdown-authored pages (About) that wraps its inner Markdown in a block with `title`, `meta`, `lead`, and `id`; `---` inside it renders as space. It only works in content rendered through `partials/block-body.html`.
- `clip`: short silent looping video with `src`, `poster`, `alt`, and an optional Markdown `caption`; plays muted on repeat, and readers who prefer reduced motion get the poster and controls (`assets/js/clip.js`, loaded only on pages with a clip).
- `membership-link`: link to `params.membershipURL`.
- `model-viewer`: interactive GLB viewer with poster, caption, download, and no-JavaScript fallback.
- `gaussian-splat`: interactive SPZ viewer with poster, download, and no-JavaScript fallback; requires `gaussian_splat: true`. Optional `camera-position` and `camera-target` values are space-separated x/y/z coordinates in the scan's coordinate system; use them when automatic framing puts the camera outside the scanned space.
- `photo-gallery`: linked-image gallery prepared for the lightbox.
- `square-crops`: interactive aspect-ratio diagram (the ratios as one segmented control, the frame as a figure tile) with a PNG fallback for RSS, print, and readers without the site's styles. After changing `data/square-crops.json`, run `uv run tools/square-crops-image.py` and include the updated image under `static/visuals/notes/`. `partials/rss-content.html` removes the interactive figure from feeds and retains the image, alt text, and caption.
- `project-grid`: a block of explicitly ordered project cards from a comma-separated `pages` parameter, with the same `title`, `meta`, `lead`, and `id` parameters as `page-list`; the inner Markdown is the lead. Also counted by the hub's rail.
- `pronunciation-name`: accessible audio pronunciation control.
- `toc`: marks the page as wanting a table of contents (an optional `title` names the rail heading, default `Contents`; an optional `intro` lists the body block itself first under that name and gives it the anchor); `partials/block-body.html` renders it in the body block's rail (sticky on wide screens, two columns on phones) from the page's `section` shortcodes when it has them (About) or from its Markdown headings, and the prose drops its heading numerals. Where the shortcode sits in the Markdown does not matter.
- `youtube`: lazy-loaded responsive video embed.

## Site versioning and deployment

- The footer format is `vMAJOR.MINOR.UPDATE`.
- The configured site era is currently `v8.0` under `[params.version]` in `hugo.toml` (v8 is Panel; v7 was the Helvetica era).
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

- Use sentence case for Note page titles and research entry titles because they are primarily statements or questions rather than conventional titles. Use Chicago-style Title Case for every other page title and heading, including headings within Notes.

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

1. Run `hugo server -D` and inspect affected pages at multiple widths. The dev server renders to `public/`, so a production build run beside it overwrites what it serves with production-base pages until it rebuilds; restart it after `tools/build-production.sh`.
2. Run `sh ./tools/build-production.sh` and investigate new build warnings.
3. Exercise `?` search, keyboard navigation, and focus restoration when shared layout or JavaScript changes.
4. Emulate light and dark `prefers-color-scheme`; there is no theme toggle.
5. Check Notes filtering/backlinks, the Research hub's stream blocks, stream Open Questions, an entry's Mentioned In and In This Stream blocks, lightbox controls, Text Fragment URLs, or pronunciation when touching those features.
6. Verify both browser and email outputs for Flaneur changes.
7. Inspect `/index.json`, `/index.xml`, aliases, redirects, `robots.txt`, and `sitemap.xml` when changing outputs or routing.
8. Run `make cards-check` before committing content. A production build warns about missing cards but still ships the fallback.
