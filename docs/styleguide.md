# ttvl.co Style Guide

This guide is the visual standard for ttvl.co. It records what a page looks like, why, and where each rule lives in the code, so new pages and components land in the same system instead of inventing their own. Editorial rules (spelling, capitalization, measurements) live in `AGENTS.md` under Editorial style; this guide covers everything a reader sees.

The standard is called **Air**. It was chosen on 2026-10-06 after a site-wide audit found that color and type had held but spacing, page heads, list grammars, and date formats had drifted section by section. The study canvas with the audit, the shared floor, and the five options compared is at <https://claude.ai/artifact/4YvBRtPxJg5qkoBZLWzabj>. Air shipped as site version v7.11.

## Principles

1. **Legibility above everything.** Every text tier passes 4.5:1 contrast in both themes. Nothing is smaller than 14 px. No uppercase, no letter-spacing, no faded small type pretending to be a heading.
2. **Space does the work.** Structure comes from space on one scale, not from lines. Lines that mark a kind of content stay: table frames, code sheets and terminals, the quotation rule, image frames on tiles. Lines that only separate or group things do not exist.
3. **Color encodes role; opacity is state.** Ink, muted, and faint are three roles with three tokens. Opacity is reserved for hover and disabled states.
4. **Hierarchy by weight and space, not size.** Three sizes for the whole site. Headings below the page title are text size, bold.
5. **One way to do each thing.** One page head, one row, one group head, one figure, one card, one date format. When a page needs something new, it extends one of these instead of starting over.
6. **The look is the stylesheet.** Markup stays semantic and shared; a section never restyles a shared pattern locally.

## Color

Themed colors come only from the custom properties in `assets/scss/_tokens.scss`. Dark mode and high contrast override tokens, never component rules. Values are solid, not alpha, so each tier keeps its contrast on `--surface` panels too.

| Token | Role | Light | Dark | Contrast (light / dark) |
|---|---|---|---|---:|
| `--ground` | Page background | `#fff` | `#212121` | |
| `--ink` | Text, links, buttons, frames | `#000` | `#e3e3e3` | 21:1 / 12.5:1 |
| `--ink-muted` | Deks, captions, secondary prose | `#555` | `#b4b4b4` | 7.46:1 / 7.77:1 |
| `--ink-faint` | Meta: dates, counts, kickers, legends, footer | `#707070` | `#949494` | 4.95:1 / 5.31:1 |
| `--rule` | Hairlines inside tables and code bands | `#eee` | `rgba(255,255,255,.1)` | |
| `--edge` | Frames: tiles, inputs, chips, table borders | `#ddd` | `rgba(227,227,227,.2)` | |
| `--surface` | Raised panels: sheets, table headers, image wells | `#fafafa` | `rgba(255,255,255,.05)` | |
| `--surface-input` | Form fields | `#fff` | `rgb(48,48,48)` | |
| `--highlight` | Text fragments and selection, the one accent | yellow, 80% | amber, 30% | |

High contrast (`prefers-contrast: more`) folds faint into muted, turns edges to ink, and flattens surfaces.

Deliberate exceptions keep literal colors and say so in a comment where they live: over-photo chrome on the 3D and splat viewers, the viewers' media wells, the terminal (dark in both themes), the lightbox, and print.

## Type

One sans family for everything, one mono family for code only.

- Sans: the system stack (`-apple-system`, `BlinkMacSystemFont`, Helvetica Neue, Helvetica, Arial).
- Mono: SF Mono and its fallbacks, for code, sheets, and terminals. Metadata is never mono.

### Sizes

| Size | Line | Used for | Variable |
|---|---|---|---|
| 20 px | 25 px | The page title (`h1`) and home section titles | `$font-size-title` |
| 16 px | 25 px | Body text and every heading below the title | `$font-size-base` |
| 14 px | 20 px | Meta, captions, code, chips, table headers, footer | `$font-size-small` |

Deks and table cells use text size on tight leading: 16/22 (`$line-height-tight`). Density comes from leading, never from smaller type.

### Voices

| Voice | Spec | Where |
|---|---|---|
| Title | 20/25, bold, ink | `h1` |
| Heading | 16/25, bold, ink | `h2` to `h5` |
| Body | 16/25, regular, ink | Prose, row titles |
| Prose link | Body, weight 500, underlined | Links inside running text |
| Quiet link | Weight 400, underlined | Row and card titles, footer, meta links |
| Dek | 16/22, muted | The line under a row or card title, filter deks |
| Meta | 14/20, faint, tabular numerals | Dates, counts, kickers, legends, page meta line |
| Caption | 14/20, muted | Figure captions, chip notes |
| Code | Mono 14 | Inline code, sheets, terminals |

Weights are 400, 500, and 700. Weight 600, uppercase, and letter-spacing are retired.

Headings follow the house rule in `AGENTS.md`: sentence case for Note and research entry titles, Chicago Title Case for everything else.

## Space

### The Scale

Every margin, padding, and gap between things uses a step. Spacing never uses rem or em.

| Step | Value | Variable |
|---|---:|---|
| 1 | 4 px | `$space-1` |
| 2 | 8 px | `$space-2` |
| 3 | 16 px | `$space-3` |
| 4 | 24 px | `$space-4` |
| 5 | 32 px | `$space-5` |
| 6 | 48 px | `$space-6` |
| 7 | 64 px | `$space-7` |
| 8 | 96 px | `$space-8` |

A component's internal geometry (the padding inside a chip, a keycap, a code sheet, a viewer control) may use its own values. Those are documented in the component's SCSS file, not borrowed elsewhere.

### The Proximity Rule

The space above a heading is at least three times the space below it, so a heading always belongs to what follows.

### Rhythm

| Between | Space | Variable |
|---|---:|---|
| Paragraphs, list blocks, quotations | 16 | `$rhythm-paragraph` |
| Page head and the body | 48 | `$rhythm-head` |
| Article `h2`: above / below | 48 / 8 | `$rhythm-h2-above`, `$rhythm-heading-below` |
| Article `h3` to `h5`: above / below | 32 / 8 | `$rhythm-h3-above`, `$rhythm-heading-below` |
| Hub and index sections (`h2`), home sections (`h1`): above / below | 64 / 16 | `$rhythm-section-above`, `$rhythm-section-below` |
| Groups inside a hub section (`h3`): above / below | 32 / 8 | `$rhythm-h3-above`, `$rhythm-heading-below` |
| Rows without deks | 4 | `$rhythm-row` |
| Rows with deks | 16 | `$rhythm-row-dek` |
| Figure: above / below / caption | 32 / 48 / 8 | |
| Article and its end matter | 64 | `$rhythm-section-above` |
| Main content and the footer | 96 | `$space-8` |

Three adjustments keep the proximity rule true where elements meet:

- A heading directly under a heading sits 8 px below it (`Current version` over `0.3.0`).
- The first group in a section sits on the section heading's 16 px, not its own 32 px (`Archive` over `2026`).
- Media directly under a heading (a figure, gallery, viewer, video, table, sheet, terminal, resource manifest, or card grid) takes the heading's 8 px instead of its own 32 px above.

## Layout

| Width | Value | For |
|---|---:|---|
| Measure | 588 px | Running text everywhere, the home intro included |
| List measure | 548 px | List items inside the 40 px indent |
| Bleed | 694 px | Figures, images, clips, and sheets that may pass the measure |
| Container | 1008 px | Card grids, galleries, viewers, wide tables |

Pages have 20 px side padding. The narrow breakpoint is 768 px. The header is 180 px tall: logo, then the navigation row. On phones the navigation scrolls sideways without a visible scrollbar.

## Patterns

Each pattern below is one partial or shortcode and one stylesheet. Use them; don't rebuild them.

### Page Head

Every page opens the same way: the title, one meta line, and optionally the strip of canonical doors.

```text
Triage                                   h1, title voice
2026-06-12 · Obsidian · Project          meta line: date first, then context
[↗ GitHub] [↗ Obsidian Community]        strip, from `resources:` front matter
```

- The meta line sits 4 px under the title. A dek, where a page type has one (the dispatch subtitle), sits 16 px under the meta line in muted text size. The strip sits 24 px under the meta line. The body starts 48 px under the head.
- Parts are separated by a middle dot. Context parts link to their page in the quiet link voice.
- Rendered by `layouts/partials/page-head.html`; the meta line comes from `layouts/partials/page-meta.html`. `hide_title: true` suppresses the whole head (About and Jinny write their own opening).
- Every hub shows its title, Projects, Notes, and Log included.

| Page | Meta line |
|---|---|
| Note | `2026-06-28 · Notes · Thinking Notes` |
| Project page | `2026-06-12 · Obsidian · Project` (hub from `project.category`) |
| Section article | `2024-12-24 · Darkroom` |
| Research entry | `2026-10-06 · Progress · Research · Ambient Computing · 021` |
| Research stream | `Research stream · Active · 24 entries since 2026-10 · updated 2026-10-06 · RSS` |
| Research hub | `2 streams · 25 entries · updated 2026-10-06` |
| Log month | `Log` (the title is the month, `2026-09`) |
| Flâneur dispatch | `2026-07-31 · The Flâneur · Dispatch 015`, with the subtitle as a dek under it |
| Hub | `13 pages · updated 2025-08-01`, with the section's own noun where it has one: `16 notes`, `31 projects`, `57 leaves`, `16 dispatches`, `93 months` |
| Trace | `2026-09-20 · Traces · 3D scan` |

### Prose

- Paragraphs hold the measure and sit 16 px apart. Lists indent 40 px; items hold 548 px.
- Prose links are weight 500 and underlined.
- Quotations carry a 2 px `--edge` rule on the left with 20 px padding, text in full ink. A `.quote-attribution` line under a quotation uses the meta voice.
- A `---` in Markdown renders as a short rule at the left, a fifth of the measure wide: a pause the author wrote, not structure. On About, where `---` opens each section, it renders as space alone.
- The table of contents heading is an `h2`; entries carry `01.` counters in the meta voice.
- Tables: framed with `--edge`, header band on `--surface`, headers in the small voice bold, cells 16/22. Append `{.wide}` to span the container. Right-aligned columns get tabular numerals.
- Code: untagged and data fences are sheets in page materials; `sh`, `bash`, `shell`, and `zsh` fences are terminals, dark in both themes. Comments are the only colored token.

### Figures

- One global rule: bleed width, block image, 32 px above, 48 px below.
- Captions use the caption voice, 8 px under the image, held to the measure.
- Figures in prose are unframed. A screenshot whose white edge would vanish into the ground opts into the frame with `class="framed"`.
- `class="portrait"` holds tall captures (phone screens) to 360 px.

### Tiles and Frames

Anything shown as a tile gets a 1 px `--edge` frame on a `--surface` well: project and trace cards, photo galleries, the newsletter contact sheet, Loose Leaves scans. Tiles are grayscale until hover or focus where the section already does so (project cards).

### Rows

The row is the site's one grammar for a list of pages.

```text
2026-06-28    Hands Are Not Cursors  Thinking Notes
              A dek from the page's description, muted, on tight leading.
```

- A 128 px meta column (a date, a number, or a key), then the title in the quiet link voice, then an optional tail inline after the title in the meta voice, then an optional dek on its own line.
- Rows without deks sit 4 px apart; rows with deks sit 16 px apart. No hairlines between rows.
- A list whose tails would wrap unevenly is **stacked** (`rows stacked`): the tail becomes the row's second line, in the meta voice, and rows sit 16 px apart. The Research hub's entry list is stacked. Home page lists carry no tails at all: date and title only.
- On narrow screens the meta column stays; long titles wrap inside the title column.
- Rendered by `layouts/partials/row.html`, styled by `components/_row.scss`. Used by the Notes index, home lists, the newsletter archive, research rows, the research bench, Open Questions, and entry relations, About's record, hub lists, and end matter.
- Resource manifests (`resources` shortcode) are the one variant: the meta column sits on the right because it describes the file (`PDF · 2.4 MB`, `GitHub`) rather than ordering it. Same voices, same spacing, no hairlines.

### Group Heads

A heading that groups a list (a year, a letter, a topic) carries its count inline after the title, 8 px away, in the meta voice: `2025  5 notes`. It is one level below the section it sits in: `h2` directly under the page title, `h3` inside a section. The look is the same at either level; only the space differs (see Rhythm).

### Cards

For things with a poster: projects, traces, featured work on the home page.

- A 16:9 tile, then the title in the quiet link voice, then the dek on its own line. No "Title – description" run-ons.
- Three columns on wide screens, two on narrow, 24 px gaps.
- Trace cards add the trace kind in the meta voice under the dek, sentence case.
- Rendered by `layouts/partials/card.html`; explicit groups on hub pages use the `project-grid` shortcode.

### Hub Lists

Hubs list their pages with the `page-list` shortcode, which renders rows from each page's front matter: date, title, and description. Titles can't drift from the pages they name. Curate order and grouping in the hub's Markdown; write the group headings and any introduction line as ordinary content.

```markdown
## DIY Projects

For enhancing the shooting process and overall experience:

{{< page-list pages="darkroom/canister-stickers, darkroom/foldable-film-reminder" >}}
```

Write every `description` as a sentence: capital first letter, final period. Descriptions appear as deks, as meta descriptions, and on social cards.

### Filter Rail

Category chips on Notes, Projects, and the Research hub: text links in faint ink, 16 px apart, the active one in ink and underlined. The dek for the active filter is a full-ink line at text size. Behavior lives in `assets/js/category-filter.js`; see `AGENTS.md`.

### End Matter

Articles end the same way, 64 px after the last paragraph:

- **Links**, when the page has them: the `resources` shortcode, written in the page's content.
- **Mentioned in**: rows for every page whose text links to this one, generated at build time by `layouts/partials/mentioned-in.html`: hubs first, then pages newest first, each keyed by what it is (`Hub`, `Note`, `Log`, `Research 021`, `Dispatch 015`, `Project`). A link counts when the page's Markdown holds the permalink, or the content path inside a `page-list` or `project-grid` shortcode.
- Research entries end with **Related** instead: the same rows, keyed by relation (`Answers`, `Answered in`, `Referenced by`), followed by the in-stream pager.

### Forms, Chips, and Keycaps

- The subscribe form: an input and a button 44 px tall, 8 px radius. Input border in ink (an edge in dark), button in ink on ground.
- Chips: small voice, 1 px `--edge`, 5 px radius, 6 × 14 px padding, `↗` for external and `↓` for files.
- Keycaps (`<kbd>`): small voice, soft cap with a 5 px radius and a 1 px shadow.

## Dates, Numbers, and Marks

- Templates write ISO dates: `2026-10-06` for a day, `2026-10` for a month. The dot notation (`2024.12.22.R6`) is a personal ID system and belongs in prose only.
- Meta uses tabular numerals.
- Counts read as words after the number: `13 pages`, `1 page`, `24 entries`.
- The middle dot `·` separates parts of a meta line. Generated copy avoids em dashes.
- `↓` means the link saves a file. `↗` means the link leaves the site.

## Out of Scope

These keep their own design on purpose:

- The Flâneur email output (`single.email.html`), with its own inline styles. Dispatch HTML pages follow this guide, but keep their bare `<head>`: no metadata, no site navigation. The engraving sits where the site logo would.
- ROAM (`/membership/`), with its own stylesheet.
- `/links/` and `/found/` keep their own layouts: a centered column of 44 px pills for phones, no site header. Inside, they follow the tokens, type, and spacing scale, and their `---` is space.
- Viewer and lightbox chrome, the terminal, print styles: literal colors and control geometry, commented in place.
- The Log archive's year by month grid and the research activity pulse: data displays with their own grammar.
- The A–Z index's hub deks stay in the small voice, muted, so two columns of hubs stay scannable.

## Implementation Map

| What | Where |
|---|---|
| Color tokens | `assets/scss/_tokens.scss` |
| Sizes, weights, scale, rhythm, widths, mixins | `assets/scss/_variables.scss` |
| Document shell, prose, figures, quotations | `assets/scss/_base.scss` |
| Header, navigation, footer | `assets/scss/_layout.scss` |
| Page head, group heads, end matter spacing | `layouts/partials/page-head.html`, `page-meta.html`, `components/_page-head.scss` |
| Hub rhythm | `.hub` on a list template's `article`, or `.section-head` on a template-written `h2` (`_base.scss`) |
| Rows | `layouts/partials/row.html`, `components/_row.scss` |
| Hub lists | `layouts/shortcodes/page-list.html` |
| End matter | `layouts/partials/mentioned-in.html` |
| Cards | `layouts/partials/card.html`, `components/_card.scss` |
| Resources | `layouts/shortcodes/resources.html`, `partials/resource-strip.html`, `components/_resources.scss` |

Mixins: `type-title`, `type-body`, `type-heading`, `type-small`, and `type-meta` (small plus tabular numerals; color is the caller's job). Placement rule: a style used by two or more sections goes in `components/`, by one in `sections/`.

## Checklists

**A new page type.** Use `page-head.html`. Add its row to the Page Head table above and its case to `page-meta.html`. End with `mentioned-in.html` if it's an article.

**A new list.** Use `row.html`. If it groups, use a group head with a count. If it needs a new slot, add it to the row, not a new list.

**A new component.** Colors from tokens, sizes from the three, spacing from the scale, internal geometry documented in the file. Check it in light, dark, and high contrast, and at 375 px.

**A new hub.** Title, meta line with the count, an introduction, then `page-list` groups or `project-grid` cards. Give it a `filter_dek` if it joins the Projects rail, and run `make cards`.

## Changelog

- **2026-10-07.** Site-wide review: dispatch pages, Jinny, the A–Z, `/links/`, and `/found/` moved onto the page head, end matter, and scale; heading-pair, first-group, and media-under-heading spacing rules; `strong` is one weight.
- **2026-10-06, v7.11.** Air adopted. Contrast floor (muted and faint retuned), three sizes, spacing scale and rhythm, one page head with a meta line, one row, inline group counts, global figures, ISO dates in templates including Log titles, hub lists from front matter, Mentioned in for every article, hairlines removed from indexes and ledgers. Supersedes the 2026-08-30 standard's type-label voice, 13 px meta, and ruled ledgers.
