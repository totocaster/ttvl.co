# ttvl.co Style Guide

This guide is the visual standard for ttvl.co. It records what a page looks like, why, and where each rule lives in the code, so new pages and components land in the same system instead of inventing their own. Editorial rules (spelling, capitalization, measurements) live in `AGENTS.md` under Editorial style; this guide covers everything a reader sees.

The standard is called **Panel**. It replaced Air on 2026-10-07 and ships as site version v8.0. The design canvas with the study, the menu and button variants, and every page mocked up is at <https://claude.ai/artifact/CYz5wjj2V8LQ1Y4uzVkeAk>. The voice is a technical instrument panel: the content sits alone in a column, and everything that describes it (dates, counts, sections, kinds) stands in a rail to its left, small and faint. Words in the chrome are set in IBM Plex Sans; numbers are set in IBM Plex Mono.

## Principles

1. **Content over chrome.** Body text is full ink at 18/28. Metadata is 14 px and faint; controls use 16 px labels. Nothing is smaller than 14 px, and every text tier passes 4.5:1 in both themes.
2. **The rail carries the metadata.** A page head and every block are two columns: a 192 px rail at left for the label, date, count, or kind, and the column for the content. On wide screens the rail is the page's one column of labels: a list's dates sit in it too, so titles and text start at one edge. Metadata stays in the rail; deks and resource links may sit under a title. A page carries one count at most, in its head rail (`75 notes · updated 2026-09`): how many pages a hub lists. Block rails and end matter carry none; a reader who wants the number has it at the top. The one exception is the Projects switches, which are controls rather than labels and carry each hub's count on their faces.
3. **Words in Sans, numbers in Mono.** Dates, counts, issue and entry numbers, sizes, and the version are set in Plex Mono with tabular figures. Every other label is Plex Sans in sentence case. No uppercase, no letter-spacing.
4. **One way to do each thing.** One page head, one block, one row, one card, one button, one legend, one form. Everything that is listed is a row: streams, doors, search results, the index's hubs, the pager.
5. **Hairlines you have to look for.** Lines sit only between rows and under the masthead. Nothing frames a list, nothing rules the footer. Frames stay on tiles, tables, sheets, and the quotation.
6. **Buttons are blocks.** A control is a flat block on a hard offset shadow. Pressing moves the block into its shadow. No gradients, no glow.
7. **The look is the stylesheet.** Markup stays semantic and shared; a section never restyles a shared pattern locally.

## Type

Two families, self-hosted as subset WOFF2 files under `static/fonts/plex/`, declared in `assets/scss/_fonts.scss`, with the Sans Regular and Mono Regular files preloaded from `partials/head.html`.

- Sans: `"IBM Plex Sans"`, then `system-ui`, Helvetica Neue, Arial. Weights 400, 400 italic, 500, 600.
- Mono: `"IBM Plex Mono"`, then `ui-monospace`, SF Mono, Menlo. Weights 400 and 500. For numbers in the chrome and for code.

Weights are 400, 500, and 600. `strong` is 600. Weight 700 is retired.

### Sizes

| Size | Line | Used for | Variable |
|---|---|---|---|
| 34 px | 40 px | The page title (`h1`) | `$font-size-title` |
| 28 px | 34 px | The page title on phones | `$font-size-title-narrow` |
| 26 px | 34 px | The search field | `$font-size-search` |
| 22 px | 30 px | Prose section headings and research entry titles | `$font-size-entry` |
| 18 px | 28 px | Body text, prose subheadings, rail headings, row and card titles | `$font-size-base` |
| 16 px | 24 px | Deks, table cells, navigation, and control labels | `$font-size-dek` |
| 14 px | 20 px | Labels, meta, captions, legends, chips, the footer, code blocks | `$font-size-small` |

### Voices

| Voice | Spec | Where |
|---|---|---|
| Title | Sans 34/40, 500, ink | `h1` |
| Section heading | Sans 22/30, 600, ink | `h2` in prose |
| Rail heading | Sans 18/28, 600, ink | Block labels |
| Subheading | Sans 18/28, 500, ink | `h3` in prose |
| Body | Sans 18/28, 400, ink | Prose, row titles, card titles (500) |
| Prose link | Body, 500, underlined | Links inside running text |
| Quiet link | 400, no underline until hover | Row and card titles, rail links, footer |
| Head dek | Sans 18/27, muted | The line under a page title |
| Dek | Sans 16/24, muted | Under row and card titles |
| Label | Sans 14/20, faint, sentence case | Rail lines, tails, legends, chips, captions (muted), footer |
| Number | Mono 14/20, tabular, inherits color | Dates, counts, issue and entry numbers, sizes, the version; `time` and `.n` |
| Nav | Sans 16/25, muted; current in ink, underlined | The masthead |
| Control | Sans 16/24, 500 | Buttons, resource links, filters, the search key |
| Code | Mono 16 inline; Mono 14/22 in sheets and terminals | |

Headings follow the house rule in `AGENTS.md`: sentence case for Note and research entry titles, Chicago Title Case for everything else.

## Color

Themed colors come only from the custom properties in `assets/scss/_tokens.scss`. Dark mode and high contrast override tokens, never component rules.

| Token | Role | Light | Dark | Contrast (light / dark) |
|---|---|---|---|---:|
| `--ground` | Page background | `#fff` | `#141414` | |
| `--ink` | Text, frames, buttons, the masthead rule's pair | `#000` | `#ededed` | 21:1 / 15.8:1 |
| `--ink-muted` | Deks, captions, the nav at rest | `#555` | `#b5b5b5` | 7.5:1 / 9:1 |
| `--ink-faint` | Labels, meta, legends, rail lines, the subscribe key's shadow | `#6e6e6e` | `#929292` | 5.1:1 / 6:1 |
| `--rule` | Hairlines between rows, under the masthead, inside tables | `#f2f2f2` | `rgba(255,255,255,.06)` | barely there: it marks a row's end without competing with the text |
| `--edge` | Frames: tiles, sheets, figures, keycaps, the quotation | `#d9d9d9` | `rgba(255,255,255,.2)` | |
| `--surface` | Raised panels: sheets, hover tints, the selected search row | `#f7f7f7` | `rgba(255,255,255,.05)` | |
| `--surface-input` | Form fields | `#fff` | `#1e1e1e` | |
| `--highlight` | Text fragments and selection | yellow, 80% | amber, 30% | |
| `--signal` | What is live: the current month, this week's pulse, the focus ring | `#ff4f00` | same | never under text |
| `--term`, `--term-ink`, `--term-faint` | The terminal block, dark in both themes | `#161616`, `#e6e6e6`, `#8f8f8f` | `#0a0a0a`, same, same | |

High contrast (`prefers-contrast: more`) folds faint into muted, turns edges and rules to ink, and flattens surfaces.

Deliberate exceptions keep literal colors and say so in a comment where they live: controls over photographs (the lightbox, the viewers' fullscreen key and status badge), the viewers' media wells, the terminal, and print.

## Space

Every margin, padding, and gap uses a step. Spacing never uses rem or em.

| Step | Value | Variable |
|---|---:|---|
| 1 | 4 px | `$space-1` |
| 2 | 8 px | `$space-2` |
| 3 | 12 px | `$space-3` |
| 4 | 16 px | `$space-4` |
| 5 | 24 px | `$space-5` |
| 6 | 32 px | `$space-6` |
| 7 | 48 px | `$space-7` |
| 8 | 64 px | `$space-8` |
| 9 | 96 px | `$space-9` |

### Rhythm

| Between | Space |
|---|---:|
| Masthead and the page head | 56 |
| Page head and the first block | 48 |
| Blocks | 64 (40 between tight blocks: year groups, end matter) |
| A rail heading and its meta line | 4 |
| Paragraphs, lists, quotations | 18 |
| Prose `h2`: above / below | 48 / 8 |
| Prose `h3`: above / below | 32 / 8 |
| Rows | 10 px padding each side of the hairline; 12 with deks |
| Figure: above / below / caption | 32 / 48 / 8 |
| A form and its legend | 12 |
| Last block and the footer | 96 |

A heading directly under a heading sits 8 px below it. Media directly under a heading takes the heading's 8 px.

## Layout

| Width | Value | For |
|---|---:|---|
| Outer page | 1200 px including 40 px side padding (20 on phones) | Masthead, main, footer |
| Rail | 192 px, then a 48 px gap | Labels, dates, counts, kinds, headings of blocks |
| Column | 880 px after padding, rail, and gap | Rows, cards, prose blocks |
| Measure | 640 px | Running text, deks, forms, legends |
| Bleed | 760 px | Figures, sheets, terminals, tables |
| Inner page | 1120 px | Viewers, galleries, and wide tables, which reach back across the rail |

The rail stacks at 1024 px, with its lines joining at 12 px gaps. The phone breakpoint remains 768 px: the masthead nav becomes one line that scrolls with a fade, the index becomes one column, and row tails drop below their titles. Card grids adapt independently: each card needs 240 px, giving three columns at full desktop width, two at intermediate widths, and one on small phones.

## The Grammar

Each pattern below is one partial or shortcode and one stylesheet. Use them; don't rebuild them.

### Masthead

```html
<header class="site wrap">
  <a class="logo" href="/"><img src="/ui/ttvl_logo.png" srcset="…" alt="Toto Tvalavadze"></a>
  <a class="search-key" href="#search">Search <kbd>?</kbd></a>
  <nav class="nav" aria-label="Primary"><a href="/projects/">Projects</a> … <a href="/about/">About</a></nav>
</header>
```

Two lines: the signature logo 44 px tall at left (large enough to stay crisp on 1x screens) with the search key at right in faint ink, then the nav on its own line in 16 px Sans with 32 px gaps, the current section in ink and underlined 6 px below the baseline. Padding 36 above, 16 below, then one `--rule` hairline. The logo is a `p` on every page; the page head owns the `h1`. The search key is a button that opens the overlay like the `?` shortcut does. On phones the logo is 32 px and the nav is one line that scrolls sideways: 44 px link targets, a 48 px fade at the right edge as the affordance, and the current section scrolled into view on load.

Rendered by `partials/header.html` and `partials/nav.html`, styled in `_layout.scss`.

### Footer

No rule. 96 px after the last block, faint 14 px: the copyright and version at left (`© 2008–2026 Toto Tvalavadze · v8.0.351`, numbers in Mono), then `Colophon · Index · RSS` at right. On dispatch pages: `ttvl.co · Archive`.

### Page Head

```html
<header class="page-head">
  <div class="rail"><p><time>2026-10-06</time> · <span class="n">019</span></p><p><a href="…">Ambient Computing</a> · Progress</p></div>
  <div class="main">
    <h1>A wall screen that reports the studio</h1>
    <p class="page-dek">…</p>
    <p class="strip"><a class="chip chip--external" href="…">GitHub</a>…</p>
    <nav class="category-filter">…</nav>
  </div>
</header>
```

The rail holds at most two lines; the column holds the title, the dek where the page has one, the strip of doors from `resources:` front matter, and on Notes and Projects the filter. The rail's first line starts 11 px down so it sits on the title's x-height. The head starts 56 px under the masthead and the first block 48 px under the head.

| Page | Rail line 1 | Rail line 2 |
|---|---|---|
| Note | `2026-02-21` | `Notes · Thinking` (both link) |
| Project page | `2026-05-07` | `Project Humane · Project` (hub links) |
| Section article (Darkroom, Bookbinding, notebook guide) | `2024-12-24` | `Darkroom` |
| Trace | `2026-09-19` | `Traces · 3D scan` |
| Research entry | `2026-10-06 · 019` | `Ambient Computing · Progress`; `· answers 003` when it closes a question |
| Dispatch | `2026-09-02 · 016` | `The Flâneur · Dispatch` |
| Log month | `Month 93` | `Log` |
| Hub (Notes, Projects, Traces, Leaves, Darkroom, …) | `16 notes · updated 2026-10-06` | |
| Research hub | `25 entries · updated 2026-10-06` | |
| Research stream | `24 entries · updated 2026-10-06` | `Research · Active` |
| Newsletter | `16 dispatches · updated 2026-09-02` | |
| Home | `Public notebook · since 2008` | |
| About | `Updated 2026-09-16` | |
| Colophon | `v8.0.351` | |
| Index | `78 entries` | |
| 404 | `404 · Not found` | the path that was asked for |

Counts read as words after the number: `13 pages`, `1 page`. Hubs use their own noun: notes, projects, months, dispatches, leaves, traces, entries. `hide_title: true` suppresses the whole head. Front matter `head_title` replaces the title with another line (About opens with its sentence) and `head_dek` replaces or, when empty, removes the dek.

Rendered by `partials/page-head.html`; the rail lines come from `partials/page-meta.html`, which returns them as a list.

### Block

```html
<section class="block">
  <div class="rail"><h2>Projects</h2><p class="meta"><a href="/projects/">All projects →</a></p></div>
  <div class="main">…</div>
</section>
```

The unit of every page below the head. The rail holds a heading and, where there is something to say, one meta line: `All notes →` where the home page lists a few of many, `RSS` on the research ledgers, `Updated 2026-09` on About's record. Never a count: the head rail already says how many the page lists. A block whose rail is empty (an article's body) still keeps the grid, so prose and figures align with every other column on the site.

- `.block.year`: a year or letter group directly under a hub's head; tight blocks sit 40 px apart.
- `.block.entry`: a research entry on a stream page; the rail holds `date · number`, then the kind.
- `.block.end`: end matter; sits 64 px after the body, 40 px after another end block.
- Markdown-authored pages (About) wrap each section in the paired `section` shortcode: `{{< section title="Record" meta="Updated 2026-09 · Not awards. Things that exist." id="record" >}}…{{< /section >}}`. The shortcode closes the body block the template opened and reopens it after itself, so it only works in content rendered through `partials/block-body.html`. Numbers in `meta` are set in Mono automatically and `[text](url)` links work there; `id` defaults to the anchorized title. Hubs that curate lists in Markdown use `page-list` and `project-grid` with `title`, `meta`, and `lead` parameters, which emit a block each; they no longer write `##` headings around them.

### Prose

The article body is one block with an empty rail. Prose holds the measure.

- Paragraphs 18 px apart. Lists indent 24 px, markers faint.
- `h2` carries a Mono numeral (`01`, `02`) in the rail, from a CSS counter; `h3` carries none. On phones the numeral sits inline before the heading.
- Prose links are 500 and underlined.
- Quotations: a 2 px `--edge` rule at left, 20 px padding, full ink; `.quote-attribution` in the label voice under it.
- A `---` renders as a 128 px `--edge` rule at the left. Inside a `section` shortcode it renders as space.
- The table of contents (the `toc` shortcode, wherever it sits in the Markdown) renders in the body block's rail under a `Contents` heading, 16 px above the list: a numbered list in the label voice with Mono numerals, muted links, sticky 24 px from the top while the page scrolls. The entry whose section is in view (the last heading above the top third of the window) is in ink with the lamp, a 6 px `--signal` dot, hanging in the gutter before its number so the entry never rewraps; set by `assets/js/toc-spy.js`. Above the first heading nothing is lit. The prose then carries no heading numerals. At 1024 px and below it stacks above the body in two columns.
- Tables: a 1 px ink rule under the header row, `--rule` hairlines between rows, no frame. Headers in the label voice, 500. Cells 16/23. `{.wide}` spans the column.
- Code: untagged and data fences are sheets, `sh`/`bash`/`shell`/`zsh` fences are terminals, dark in both themes. Radius 2. The sheet's filename kicker is Mono, faint. Comments are the only colored token.
- Inline code is Mono 16, no background.
- Keycaps (`kbd`): Mono 14, 1 px `--edge` with a 2 px bottom edge, radius 2, `--surface` fill. Unchanged by the button rule.

### Figures

- Bleed width (760 px), block image, 32 px above, 48 px below. Screenshots and renders carry a 1 px `--edge` frame with radius 2; photographs in letters (`class="plain"`) are unframed.
- Captions: label voice, muted, 8 px under, held to the measure. No numbering.
- `class="portrait"` holds tall captures to 360 px.
- The `clip` shortcode: the same frame, a `Clip · loops muted` badge at the bottom left in 14 px white on 55% black, the caption below. Readers who prefer reduced motion get the poster and controls.

### Rows

```html
<li class="row"><span class="row-meta"><time>2026-06-28</time></span><span class="row-main"><a class="row-title" href="…">Hands Are Not Cursors</a><span class="row-dek">…</span></span><span class="row-tail">Thinking</span></li>
```

The one grammar for anything listed. Three columns: the meta column, the title (with an optional dek under it), and a right-aligned tail. On wide screens a list inside a block reaches left across the gap so its meta column is the rail itself (192 px, then the 48 px gap): dates and kinds line up with every other label on the page, and titles start where content starts. The search overlay's rows are not in a block and keep a 128 px column, as do lists inside a body whose rail holds the table of contents and inside a stream entry, whose rails are taken. A `--rule` hairline between rows, none above the first or under the last. Rows carry 10 px padding, 12 with deks.

- The meta column holds the ordering key or the kind: a date, `#016 · 2026-09` for dispatches, `Hub` / `Note` / `Project` / `Log` / `Research` / `Dispatch` / `About` in end matter, `Active` in the stream ledger, `The essay` on the newsletter's doors, `Model` / `Lights` on the bench, `← 018` / `020 →` in the pager. A list with nothing to order by (the Index's Start Here) leaves the column empty on wide screens, where it is the rail, and drops it when the rail stacks.
- The tail holds one qualifier, the same kind in every row of a list: the category on Notes (`Thinking`), `024 · Question` on research lists, the venue on About's record, the date in end matter, `#008 · 2024-01` on the newsletter's doors. Home lists and the stream ledger carry none; a count never rides in a tail.
- Numbers in either column are wrapped: `<time>` for dates, `<span class="n">` for everything else.
- The stream ledger's rows carry the activity pulse inline after the name, then the dek.
- The search overlay's rows are the same markup; the selected row takes a `--surface` wash 12 px wider than itself.
- On phones the tail drops under the title and the meta column fits its content, 96 to 136 px, with a 16 px gap before the title, so `#016 · 2026-09` never crowds the words.

Rendered by `partials/row.html`, styled by `components/_row.scss`.

### Ledger Blocks

A block whose column starts with a list is a ledger: on wide screens its rail heading takes its own line, and the list below uses the rail as its meta column, so the page keeps one column of labels. Nothing groups rows inside a block: a year, a stream, or a kind of record is a block of its own, its name in the rail and a qualifier (the newsletter's `as Dreaming with One Eye Open`) beside the name in the label voice, wrapping inside the rail. Ledger mode is set by the content (`:has()`) or by a `ledger` class on the block. The Index's A–Z letters are the one list that keeps headings inside its block: a three-column index, not a ledger. At 1024 px the rail stacks; rows keep a 128 px meta column until the phone breakpoint, where it fits its content between 96 and 136 px.

### Cards

```html
<div class="card" data-category="obsidian">
  <a class="tile" href="…"><img …></a>
  <p class="card-label"><time>2026-06</time> · Obsidian</p>
  <a class="card-title" href="…">Triage</a>
  <span class="card-dek">Resurfaces unprocessed notes in an Anki-style triage queue.</span>
</div>
```

A 16:9 tile on a 1 px `--edge` frame with radius 2 over `--surface`, grayscale at rest; one label line (`date · hub` for projects, `date · kind` for traces, `Since 2023 · Gallery` for ongoing work); the title at 500; the dek. Nothing changes at rest. Under the hand, anywhere on the card, the tile alone becomes a key: the frame turns ink, the 2 px ink shadow appears, the poster colors, the title underlines; pressing drops the tile into its shadow, like every other key. The tile keeps a 2 px margin at right and below for the shadow. Up to three columns in the 880 px column, each at least 240 px wide; two at intermediate widths and one on small phones. Gaps are 32 × 24 px, or 24 × 12 px on phones. Rendered by `partials/card.html`.

### Doors, Chips, and the Strip

The strip under a page title is one row of keys: chips share edges (`margin-left: -1px`), the first and last carry the 2 px outer radius, and the whole row sits on one 2 px ink shadow. Each chip uses the 16/24 control voice, a 1 px ink frame, 3 × 12 px padding, `--ground` face; `↗` after an external door and `↓` after a file, with the size in Mono after a file. Hover tints the face `--surface`; pressing fills it ink. When the rail stacks, the row falls apart into single keys, each on its own shadow, 12 px apart. Keys are at least 32 px high, or 44 px on phones and coarse pointers. Rendered by `partials/resource-strip.html`.

### Buttons and Forms

Every button is a block on a hard shadow. Pressing (`:active`) moves it into the shadow; `:focus-visible` draws a 2 px `--signal` ring 2 px out.

| Control | Face | Shadow | Height |
|---|---|---|---|
| Primary action: subscribe key, `.btn` | ink, ground text, 16/24 500 | 3 px `--ink-faint` | 40 |
| Secondary action: quiet `.btn`, viewer bar buttons | ground, ink text, 16/24 500 | 2 px ink | 32 |
| Resource links: chips | ground, ink text, 16/24 500 | one 2 px ink shadow under the joined row | 32 |
| Pills on `/links/` and `/found/` | ground, ink text, 16/24 500 | 2 px ink | 44 |
| Inline pronunciation action | ground | 1 px ink | 32 |
| Selection: segmented control | joined 16/24 keys; the selected key is ink | one 2 px ink shadow | 32 |

All action and selection controls have at least 44 px targets on phones or coarse pointers. Compact controls use 32 px on desktop; primary actions and fields use 40 px. Primary hover uses muted ink, secondary hover uses surface, and selected segments use ink. Pressing an action moves its key into the shadow; joined keys move as one group. Disabled buttons keep their geometry and do not press. Focus uses the signal ring.

Every block carries a right and bottom margin equal to its shadow, so nothing clips at a column edge.

The subscribe form: a 40 px input, 44 px for touch (1 px ink frame, `--surface-input`, radius 2, the same box as the key beside it in every browser), a 12 px gap, the key. The legend sits 12 px under it and reads `Seasonal, not monthly · one click to leave` wherever the form appears (home, newsletter, About, dispatch end, `/links/`). No boxes around forms.

### Legends

A `p.legend` in the label voice explains the thing directly above it, in the column, never in the rail: under the subscribe form, under the stream ledger (what the pulse marks mean), under the contact sheet, under a viewer (how to orbit, the download), under the index's letters (what the mail icon means), under the pager (which keys move).

### End Matter

Every article ends with one block, `Mentioned In`, 64 px after the body: nothing but the heading in the rail, and rows keyed by what each page is, with the page's date as the tail where it has one. Hubs first, then pages newest first. A research entry adds a second block, `In This Stream`, with the stream's name as its meta line and two rows, `← 018` and `020 →`, then a legend with keycaps: `← → move between entries`. The relation words of the old `Related` block are retired; an entry that answers a question says so in its head rail.

Rendered by `partials/mentioned-in.html` and `research/single.html`.

### Filter Rail and Switches

Notes: `nav.category-filter` under the hub's dek, chips in the control voice, faint, 20 px apart, the active one in ink and underlined 5 px below the baseline. No arrow to a hub, no dek that changes with the filter.

Projects: one switch per hub under the dek (`.switches`, `components/_switch.scss`), a tile on `--surface` with a 1 px `--edge` frame and radius 2, at least 136 px wide, as many across as fit (two on phones). Its face is a button in the control voice: the hub's name, its count in the label voice, its `filter_dek` muted; under the face, `Open the hub →` in the label voice is the door. Pressing a face filters the cards and presses the switch: it stands on `--ground` with an ink frame, a 2 px ink shadow, and the lamp (a 6 px `--signal` dot) after its name, so the name never moves. Pressing it again releases the filter; there is no All switch. A legend under the switches says so. New hubs join by having projects and a `filter_dek`.

Index: the same tiles as doors (`.switches.doors`, `a.switch.door`), three across (two on phones), one per hub with its title and `filter_dek`, the whole tile a link. Under the hand it stands up like a pressed switch (ink frame, shadow, ground) and pressing drops it; no lamp, no count, no door line, since the tile is the door.

Both hubs: the head rail's count follows the filter (`12 projects`): `count.html` with `live` wraps it as `.count[data-singular][data-plural]`, and `category-filter.js` reads every `[data-filter-control]` button and `.category-filter` chip, shows and hides the `[data-category]` items of every `[data-filter-group]`, and keeps the state in `?category=`. Groups carry no count of their own.

### Search Overlay

Full ground. Centered, 96 px down: a “Search site” label and a Close button, a 26/34 input with a visible prompt and focus ring, then desktop keyboard hints (`↑ ↓ select · ↩ open · esc close`). Results use rows: section as meta, title with matches marked, a short excerpt around a match, and date as the tail. On phones the section and date share a line above the full-width title, and excerpts take at most three lines. Keyboard hints hide for touch. Close, Escape, and the backdrop restore focus to the opener. The selected row takes a `--surface` wash. The count under it: `4 results`. Built by `assets/js/search.js`, styled by `components/_search.scss`.

## Page by Page

- **Home.** Head: the intro sentence as the title, the second sentence as the dek, rail `Public notebook · since 2008`. Then six blocks: The Flâneur (`All dispatches →`; a sentence, the form and legend, the five latest dispatches as rows), Projects (`All projects →`; the featured cards), Notes (`All notes →`; five rows without tails), Research (`All entries →`; five rows without tails), the latest month (its title as the rail heading, `Log · all months →`; the month's content), Get in Touch (`toto@ttvl.co`).
- **Notes hub.** Head with the filter and the only count. One tight year block per year: `2026`, rows `date | title | category`.
- **Note.** Head, the body block, Mentioned In.
- **Projects hub.** Head with the switches, one per hub, and the legend; the head's count follows the filter. Year blocks (`Ongoing`, `2026`, …) with card grids and nothing in their rails but the year. No end matter: the doors are on the switches.
- **Long articles** (the notebook system and its guides, Walking) call the `toc` shortcode and get the table of contents in the body block's rail.
- **Project page.** Head with the strip. The body block. Mentioned In. The `resources` manifest, where a page writes one, stays in the body and renders as plates (`.files`, three across, two on phones): the switch tile with the type at the top (a format such as `PDF` or `STL` in Mono, a destination such as `Printables` in Sans), the title at 500, a muted note, and `68 KB · Download ↓` or `printables.com ↗` under it; the whole plate is a door that stands up under the hand. A file link inside a paragraph is a small inline key on a 1 px shadow with `PDF ↓` after the words.
- **Section hubs (Darkroom, Bookbinding, Project Humane, Obsidian, the notebook system).** Head with the intro as the dek. One block per `page-list` or `project-grid`, titled from the shortcode, with the lead (where one is written) in its rail.
- **Research hub.** Head. Streams: rows with `Active` as the meta, the name, the pulse, and the dek; the pulse legend under them. The all-streams `RSS` sits in the Streams rail. On phones the pulse takes its own line under the stream's name. Then one block per stream, its name linked in the rail with the stream's own `RSS` under it, rows `date | title | 024 · Question`. No filter.
- **Research stream.** Head with the brief as the body block. Bench: rows `Model | text`. Open Questions: rows `date | title | 024`; a closed question is struck through in the meta column. Then an `Entries` block whose column is empty, followed by one `.block.entry` per entry, newest first: rail `date · number` then the kind, column the title at 22/30 and the entry in full. Entries sit 56 px apart; the first sits 16 px under the Entries heading.
- **Research entry.** Head (`date · number` / `Stream · Kind`). Body. Mentioned In. In This Stream, with the legend. The arrow keys keep working.
- **Log hub.** Head. One block per month, newest first: the month as the rail heading (linked), its content in the column. Then the Archive block with the year-by-month grid: Mono 14, 64 px year column, twelve cells, hairlines between years, voids as `··`, the current month in 500 with a 2 px `--signal` underline.
- **Log month.** Head (`Month 93` / `Log`). Body. In the Log (`All months →` in the rail): two rows, `← 092 | 2026-08` and `094 → | 2026-10`, then the keycap legend `← → move between months`; the arrow keys follow them (`assets/js/pager.js`, shared with research entries). Then the Archive block.
- **Newsletter.** Head with the intro as the dek, the form and legend in the column. Start Here: rows `The essay | title + dek | #008 · 2024-01`. Contact Sheet: the strip of 150 × 110 frames with `#016 · 2026-09` under each, the legend under the strip. Then one block per year, the year in the rail (2021 adds `as Dreaming with One Eye Open` beside it), rows `#016 · 2026-09 | title`.
- **Dispatch.** No masthead: the engraving centered, 120 px tall. Head (`2026-09-02 · 016` / `The Flâneur · Dispatch`, the subtitle as the dek). The letter, photographs unframed, galleries in two columns. End block `The Flâneur` (`All dispatches →`): one sentence, the form, the legend. Footer `ttvl.co · Archive`. The email output is untouched.
- **Traces hub.** Head. Archive block with trace cards (`date · kind`).
- **Trace.** Head with the download chip in the strip. The viewer and the gallery span the full page width, reaching back across the empty rail; the viewer bar's title then sits in the rail column. (`SPZ scan · 16.7 MB ↓`; sizes are read from the file and use binary megabytes, as the strip does). The body block holds the viewer and the prose; Photographs as a prose `h2` over the gallery. Mentioned In.
- **Loose Leaves.** Head. One year block per year, the year alone in its rail; a six-column grid of tiles at the notebook's page proportion (Bible size, 95 × 171 mm, which the scans share) on `--edge` frames with the 2 px ink shadow of every key, the date in Mono under each (leaves that share a day are tagged `2024-12-17/1`, `/2`, … in the order shown); three columns on phones. Under the hand the frame turns ink; pressing drops the leaf into its shadow. The lightbox shows the whole leaf, contained.
- **About.** Head (`Updated 2026-09-16`) over the opening sentence as the title; the on-page nav in the column in the label voice. Then one block per section through the `section` shortcode: Newsletter (`All dispatches →`), Books (`Not awards. Things that exist.`), Exhibitions, Curation, Programs and training, Speaking, Video, Print, and Tools I made, each a block of its own with the venue as each record row's tail, then Philosophy, Extended About, Tools I use (`Updated 2026-09 · Nothing here is sponsored`), How I use AI, Get in Touch. The principles are `h3.principle` with Mono numerals in the rail.
- **Colophon.** Head (`v8.0.351`). Body.
- **Index.** Head (`78 entries`). Start Here: a grid of door switches, three across, one per page named in the Index's `hub_sections` front matter (hubs the masthead does not reach, and the Ambient Computing stream), with its title and `filter_dek` or description. A–Z: letter groups in three columns (one on phones), each an `h3` without a count; a 14 px mail icon (a stroke icon, since Plex has no envelope) after a title that also went out as a dispatch, and the legend under the letters. Log: the archive grid.
- **Search.** The overlay above.
- **404.** `layouts/404.html`: head (`404 · Not found` / the path), one sentence pointing to search, the index, and home.
- **`/links/` and `/found/`.** Avatar, logo, the description, then pills on 2 px ink shadows 12 px apart with the kind in the label voice at the right, the form and legend under them. No masthead.
- **Membership (`/membership/`) and the Flâneur email output keep their own styles.** The Jinny website page is an ordinary project page; a gallery holding one image renders as a 760 px figure in the image's own proportions.

## Media Chrome

The viewers (`model-viewer`, `model-viewer-comparison`, `gaussian-splat`, `spatial-long-exposure`) share one geometry:

- The viewers and galleries span the inner page (1120 px) on an article whose rail is empty beside the body; on a page with the table of contents in the rail they stay in the column.
- A bar above the frame in the label voice: the title at left, the controls at right as quiet blocks; the comparison viewer's two dates and the map's `Places · Connections · Both` modes are one segmented control, the pressed key in ink. 12 px between the bar and the frame.
- The frame: 16:10, the column's width, a 1 px `--edge` frame with radius 2, the media well dark (`#111`, a deliberate exception). The fullscreen key at the bottom right: 32 px (44 px for touch), 1 px white at 60%, black at 50% behind, a stroke icon. A status badge at the bottom left (`Loading scan…`, `Showing after Kyojima · 2026-08-03`) in 14 px white on black at 55%, which keeps white text at 4.5:1 over a light poster; the map's OpenStreetMap credit is the same badge at the top right.
- A legend under the frame: how to move, and the download with its size in Mono and `↓`.
- Galleries (`photo-gallery`, the trace photographs): three columns of 4:3 tiles on `--edge` frames, 16 px gaps, two columns on phones. The lightbox: black at 94%, the image contained, a counter `2 / 57 · 2025-04-19` in white at 72% at the bottom left with the numbers in Mono, `× ← →` keys as 44 px squares with a 1 px white frame at 50% and radius 2. Escape, the arrow keys, and the focus trap are unchanged.
- The pronunciation control: a 32 px block on a 1 px shadow with the stroke icon, whose touch target grows to 44 px around the same face so the line keeps its rhythm; it stays inline in the sentence, centred on the x-height of the word beside it. Its styles and the clip's live in `components/_model-viewer.scss` with the rest of the media chrome.
- YouTube embeds take the figure frame.
- The square-crops diagram (the `square-crops` shortcode): its screen ratios are one segmented control of radio keys, the checked key in ink; its 320 px square sits on the figure tile (`--surface`, 1 px `--edge`, radius 2) with the grid in `--edge`, the source dashed in faint ink, the chosen crop filled with `--highlight` under an ink stroke, and the point of interest in ink; the chosen ratio reads under it in the label voice. Feeds, print, and browsers without `:has()` get the PNG instead.

## Dark Mode and High Contrast

Dark follows `prefers-color-scheme`; there is no toggle. The signature logo inverts through a CSS filter. Shadows under buttons use the same tokens, so they read as light blocks on the dark ground. High contrast folds the tiers as the Color section says.

## Implementation Map

| What | Where |
|---|---|
| Fonts | `static/fonts/plex/*.woff2`, `assets/scss/_fonts.scss`, preloads in `partials/head.html` |
| Color tokens | `assets/scss/_tokens.scss` |
| Sizes, weights, scale, rhythm, widths, mixins | `assets/scss/_variables.scss` |
| Document shell, prose, figures, quotations, numerals | `assets/scss/_base.scss` |
| Masthead, nav, footer | `partials/header.html`, `nav.html`, `footer.html`, `assets/scss/_layout.scss` |
| Page head and rail lines | `partials/page-head.html`, `page-meta.html`, `components/_page-head.scss` |
| Blocks | `components/_block.scss`; the `section` shortcode; `page-list` and `project-grid` |
| Rows | `partials/row.html`, `components/_row.scss` |
| Cards | `partials/card.html`, `components/_card.scss` |
| Strip, chips, manifest | `partials/resource-strip.html`, `shortcodes/resources.html`, `components/_resources.scss` |
| Buttons, forms, legends | `partials/subscribe-form.html`, `components/_control.scss` |
| End matter | `partials/mentioned-in.html`, `research/single.html` |
| Search | `assets/js/search.js`, `components/_search.scss` |
| Viewers, galleries, lightbox, clip | the shortcodes and `components/_model-viewer.scss`, `_gaussian-splat.scss`, `_spatial-long-exposure.scss`, `_photo-gallery.scss`, `_lightbox.scss` |
| Social cards | `tools/social-cards.py` (Plex from the system font files) |

Mixins: `type-title`, `type-body`, `type-heading`, `type-dek`, `type-control`, `type-small`, `type-meta` (small plus tabular Mono numbers are opted in per element through `time` and `.n`, not the mixin). Placement rule: a style used by two or more sections goes in `components/`, by one in `sections/`.

## Checklists

**A new page type.** Use `page-head.html`; add its rail lines to the table above and its case to `page-meta.html`. Wrap its body in a block. End it with `mentioned-in.html` if it is an article.

**A new list.** Use `row.html`. Decide what the meta column orders by and what the one tail says. If it groups, each group is a block of its own with its name in the rail; nothing groups rows inside a block, and no group carries a count.

**A new control.** It is a block on a shadow; pick the row of the table above. Check it pressed, focused, in dark, and at 375 px.

**A new hub.** Title, one rail line with the count, the intro as the dek, then blocks from `page-list` or `project-grid`. Give it a `filter_dek` if it joins the Projects rail, and run `make cards`.

## Changelog

- **2026-10-10, v8.0, leaves as keys.** Loose Leaves tiles take the notebook's page proportion and the key's shadow; the lightbox fits a tall scan whole.
- **2026-10-10, v8.0, file plates.** The `resources` manifest renders as plates, the switch tile with the type in Mono and Download ↓; file links in paragraphs are inline keys.
- **2026-10-10, v8.0, doors on the Index.** Start Here is a grid of door switches, the switch a shared component; the dispatch marker is a stroke icon instead of a glyph Plex lacks.
- **2026-10-10, v8.0, review pass.** The switch lamp sits after the name; empty meta columns drop when the rail stacks; the newsletter's years are tight blocks with their qualifier in front matter; the pagers use `row.html` with a `rel`; end-matter headings in Title Case; the switch door uses `→`.
- **2026-10-10, v8.0, the card as a key.** A project or trace card stays quiet at rest; under the hand its tile becomes a key (ink frame, shadow, color, the title underlined) and pressing drops it.
- **2026-10-10, v8.0, switches and the phone menu.** The Projects hub filters with one switch per hub, each a face that filters and a door that opens the hub; the Hubs end block is gone. On phones the nav is one line that scrolls with a fade. Hairlines fainter; the newsletter's 2021 qualifier beside its year; phone rows give long keys room; Log months get a pager; the pulse on its own line on phones.
- **2026-10-10, v8.0, flat sections.** Nothing nests inside a block: About's record kinds, the streams on the Research hub, and the newsletter's years are blocks of their own, and the group-head grammar is retired.
- **2026-10-07, v8.0, responsive refinement.** Rails stack at 1024 px; cards keep a 240 px minimum; mobile navigation wraps. Controls share 16/24 labels and 44 px touch targets. Search has a visible Close action, full-width mobile results, and short excerpts. Prose section headings use 22/30. Project Humane has the same name in filters, cards, and page metadata; Note titles use sentence case, preserving proper names. Grayscale tiles and hard shadows remain.

- **2026-10-07, v8.0, second pass.** One column of labels: lists use the rail as their meta column and group heads align with the content column (ledger blocks); viewers and galleries span the page; the table of contents in the body rail; the logo at 44 px; the search key faded; the Projects filter is chips only, like Notes, and the page ends with Hubs; counts only in the head rail, which follows the filter.
- **2026-10-07, v8.0.** Panel replaces Air: IBM Plex Sans and Mono self-hosted; body 18/28 in full ink and titles 34/40; a 192 px rail beside every head and block; words in Sans and numbers in Mono; hairlines only between rows; one row grammar for everything listed; buttons as blocks on hard shadows with the project doors joined into one row; a two-line masthead; research entries with their metadata in the rail; the social cards reset in Plex.
- **2026-10-06, v7.11.** Air: contrast floor, three sizes, one page head, one row, inline group counts. Superseded.
