# ttvl.co Figures Guide

This guide is the standard for the figures the site draws itself: diagrams, plans, charts, timelines, and the interactive figures called instruments. It extends `docs/styleguide.md` (Panel), whose Figures and Media Chrome sections still govern photographs, screenshots, clips, and the 3D viewers. Where the two meet, Panel wins; this guide never restyles the chrome.

The working specimen is the Figures page, `content/figures.md`, published at `/figures/` and linked from the Colophon. Every figure on it is built with the parts described here, from the site's own data, and it is the place to check a change in both themes and on a phone. A change to a shared part shows there first.

## Principles

1. **A figure is Panel at another scale.** The same two families, the same ink, the same hairlines, the same 14 px floor. A drawing should look as if the stylesheet drew it.
2. **Ink does the work.** Figures are monochrome. Position, length, labels, line weight, and four tones of ink carry every distinction; there is no palette of hues. Two colors are reserved, as they are in the chrome: the highlight marks what the reader selected, and the signal marks what is live, as a lamp and nothing else.
3. **Words in Sans, numbers in Mono.** Labels are sentence case, never uppercase or tracked. Dates are ISO.
4. **Label the thing itself.** Names sit on or beside what they name. A key appears only when labels cannot, and like every legend it sits under what it explains.
5. **Every number is also text.** The caption, the key, the readout, or a table carries the values; nothing is reachable only by hovering.
6. **Figures follow the theme.** A drawing is an SVG in the drawing palette, inlined into the page, so it turns dark with everything else. A raster image on a white plate is the exception, kept for pictures and for illustrations made for a single page.
7. **One way to do each thing.** Each form has one tool: `drawing` for anything drawn in SVG; `bars`, `units`, `{.bars}` tables, and `spark` for the charts better made of HTML; `annotate` and `compare` for pictures; `site-chart` for a figure the build draws; and three scripts to draw the files (Making Figures).

## Which Figure

| The material | The figure | Built with |
|---|---|---|
| A photograph | Picture, unframed in letters | Hugo's `figure` (`class="plain"`) |
| A screenshot, render, scan, or another program's interface | Picture on the edge frame | `figure` |
| Something that moves | Clip | `clip` |
| A 3D scan | Viewer | `model-viewer`, `gaussian-splat` |
| An illustration for one page: a plan, an elevation, an object | Picture drawn on white | `figure` (Pictures) |
| The parts of a picture named | Annotated picture | `annotate` |
| The same view at two times, or two takes of it | Comparison | `compare` |
| A how-to in a few moves | Steps | `drawing` |
| Parts and how they connect | System diagram | `drawing` |
| Steps in order | Pipeline | `drawing` |
| What holds what | Tree | `drawing` |
| How long things ran | Spans | `drawing` |
| When things happened | Events on a timeline | `drawing` |
| Periods with events inside them | Eras on a timeline | `drawing` |
| The shape of an argument: poles, quadrants, a loop, what holds what, layers | Spectrum, matrix, cycle, containment, stack | `drawing` |
| What a thing can be and what moves it on | States | `drawing` |
| Who says what to whom, in order | Sequence | `drawing` |
| Real sizes side by side | Sizes to scale | `drawing` |
| Keys to press | Keyboard | `drawing` |
| Where things are | Map | `drawing` from `tools/map.py` |
| Amounts compared across categories | Bar list | `bars` |
| One category is the point | Bar list with emphasis | `bars emphasis="…"` |
| Change over time | Line (many points) or columns (a few days or months) | `drawing` |
| Two series across categories | Paired bar list | `bars series="…"` |
| Two series across a few periods | Grouped columns | `drawing` |
| Two series of the same unit over many dates | Two lines on one scale | `drawing` |
| The same items at two times | Before and after | `drawing` |
| Things counted one by one; a share of a small total | Unit chart | `units` |
| How a whole splits, period by period | Stacked bars | `drawing` |
| Above or below a baseline | Diverging columns | `drawing` |
| Two measures of the same items | Scatter | `drawing` |
| A value for every month (or day) across years | Calendar | `drawing` |
| One series split by period, or more than three series | Small multiples | `drawing` |
| How one measure spreads | Distribution | `drawing` |
| A column of numbers that should compare at a glance | Bars in a table | Markdown table `{.bars}` |
| A number's history inside a sentence | Sparkline | `spark` |
| Tones of a print; a film's response | Zone scale, characteristic curve | `drawing` |
| Anything the site can count about itself | Live figure | `site-chart`, or a partial like it |
| A spreadsheet's numbers | Columns or a line | `drawing` from `tools/chart.py` |
| A figure worth exploring | Instrument | `drawing` with `states`, `toggle`, or `scrub` |
| Exact values, or more than about seven categories | Table | Markdown table |
| One number | The number in the sentence | prose |

Prefer HTML whenever it can do the job: a bar list, a unit chart, or a table keeps its words at real size on every screen and needs no phone drawing. Reach for SVG when the figure is a picture of something.

Never: pie or donut charts, two y-axes (two units are two charts, or small multiples on one time axis), 3D charts, stacked areas with many series, gradients, drop shadows, a number on every mark, dashed gridlines, decorative icons.

## The Drawing Palette

Draw in these eleven values and nothing else. The stylesheet (`components/_drawing.scss`) matches each literal `fill` and `stroke` by attribute selector and replaces it with its token, so the file stays correct on its own in light mode and turns dark on the page. CSS outranks presentation attributes, so nothing in the file is rewritten. `currentColor` follows the ink as well; `fill="none"` stays empty.

| Literal | Token | Light | Dark | For |
|---|---|---|---|---|
| `#000000` | `--ink` | `#000` | `#ededed` | Words, outlines, the subject, a filled place, the baseline |
| `#555555` | `--ink-muted` | `#555` | `#b5b5b5` | Words: descriptions and direct labels |
| `#6E6E6E` | `--ink-faint` | `#6e6e6e` | `#929292` | Words: axes, column heads, notes; dashed and leader lines |
| `#4F4F4F` | `--tone-2` | `#4f4f4f` | `#b0b0b0` | The second step of an ordered category |
| `#7A7A7A` | `--tone-3` | `#7a7a7a` | `#7f7f7f` | The third step; context marks beside an emphasized one |
| `#A3A3A3` | `--tone-4` | `#a3a3a3` | `#5c5c5c` | The fourth step; the outline of an open mark |
| `#D9D9D9` | `--edge` | `#d9d9d9` | white at 20% | Context lines: grids, gridlines, surroundings; empty-day stubs |
| `#F7F7F7` | `--surface` | `#f7f7f7` | white at 5% | The face of the subject when it is a container, a drawer, a zone |
| `#FFFFFF` | `--ground` | `#fff` | `#141414` | Faces of boxes, knockouts behind words, words on ink |
| `#FFEB3B` | `--highlight` | yellow at 80% | amber at 30% | The reader's selection; the region a figure is about |
| `#FF4F00` | `--signal` | `#ff4f00` | same | A lamp: what is live. Never an area, never under words |

The tones are an ordinal ramp from ink toward the ground, so dark mode flips them. Checked with the dataviz validator: lightness falls in even, visible steps in both themes, and the light end clears 2:1 on the ground. Against the ground, tone 2 is 8.2:1 (8.5:1 dark), tone 3 is 4.3:1 (4.6:1), and tone 4 is 2.5:1 (2.8:1), below the 3:1 a mark needs on its own, so a tone 4 mark always carries a label or a key.

There is no categorical palette. Identity comes from labels and position; two series take tone 3 and ink, three take tone 3, tone 2, and ink, always with direct labels; more series become small multiples, one small chart each on shared scales. The one place hue may appear is a thing's own color shown as itself, such as a film stock's box or the studio's room codes, set as a labeled swatch the way a photograph of it would show it. Such a literal is outside the palette, so it does not change with the theme; say so in the caption if it matters.

## Lines

| Line | Spec | Means |
|---|---|---|
| Outline | 1 px ink | The edge of an object |
| Subject | 2 px ink | The thing the figure is about; one per drawing |
| Context | 1 px edge | Grids, gridlines, surroundings, what stands behind |
| Not yet real | 1 px faint, dashed 4 4 | Planned, estimated, derived, outside the system, a boundary that is not a wall |
| Leader | 1 px faint, square elbows | From a word to the part it names |
| Connector | 1 px ink, a 6 px filled head | A flow from one part to another; a head at each end for an exchange |
| Baseline | 1 px ink | The zero of every bar and column chart; the axis of a timeline |
| Series | 2 px ink, round joins | A line chart's line; context series in tone 3 |

Strokes never scale: the stylesheet gives every element `vector-effect: non-scaling-stroke`, so a 1 px line stays a hairline when a drawing shrinks on a phone or grows on a wide screen. Draw 1 px lines on half-pixel coordinates (`x="0.5"`) so they land crisp. Objects have square corners; the 2 px radius belongs to the interface's frames, not to drawn things. No shadows, no gradients, no perspective.

## Fills

- **Ground** is the face of every box, and the knockout behind a word that crosses a line.
- **Surface** is the face of the subject when it is a container (the studio brain), or of a drawer or a zone.
- **Ink** fills the one place in question, with its words in ground (Bookshelf c3). One, or very few, per drawing.
- **Tones 2 to 4** step through ordered categories, ink first: measured, confirmed, specified, drawn.
- **Open** marks (no fill, a 1 px tone 4 outline) are what is not yet known; **dashed** marks are derived.
- **Highlight** is the reader's selection in an instrument, a band behind the chosen mark, or the region the figure is about, under an ink stroke (the square-crops crop).
- **Signal** is a lamp, a 6 px dot, on what is live now. A static drawing rarely has anything live, so it usually has no signal at all.

## Type

| Voice | Spec | For |
|---|---|---|
| Name | Sans 16, 500, ink | The names of parts: `a4`, `Home Assistant Green`, column letters |
| Label | Sans 14, muted | Descriptions inside boxes, direct labels, a series' name |
| Note | Sans 14, faint | Column heads, connector words, axis titles, orientation (`Street end`) |
| Number | Mono 14, faint on axes, ink as a direct value | Ticks, row numbers, `372`, `7` |
| On ink | Any voice in ground | Words on a filled place |

- 14 px is the floor at the drawing's design width. Nothing is bold beyond 500.
- Keep words as text, never outlines, so they theme, scale crisply, and can be selected and found.
- Name the families in the file (`font-family="IBM Plex Sans"` or `"IBM Plex Mono"`); the page enforces them anyway.
- In mixed text only the digits are Mono, through a `tspan`: `1` in Mono, ` px ink` in Sans.
- Dates are ISO (`2026-10-06`, `2026-10`). An axis may write one full date and then day numbers (`2026-10-01`, `05`, `10`).
- A drawing has no title inside it. Its headline belongs in the sentence before it or in the caption; a number that is the point (`116 of 179`) goes there too.

## Size and Layout

| Width | Design at | Shortcode |
|---|---:|---|
| Measure | 640 px | `width="measure"` |
| Bleed (default) | 760 px | |
| Wide | 1120 px | `width="wide"`: spans the page beside an empty rail, fills the 880 px column beside a contents rail |
| Phone | 335 px | the `narrow` drawing |

Draw at one user unit per pixel at the design width, aligned to the 4 px grid, with nothing around the content: the file's bounds are the drawing's bounds. Inside, boxes pad words by 12, stand 16 apart, and two-line boxes are 64 tall; leave 80 between columns that carry connector words.

A drawing stands on the ground with no frame, like a table. Pictures keep the edge frame; instruments sit in a well.

A drawing never grows past its design width, so a narrow one keeps its 14 px words in a wide column. On narrower screens it shrinks to three quarters of that width at most, so 14 px words never fall under 10.5 px; below that its frame scrolls sideways with the code sheet's right-edge fade. The shortcode reads the floor from the viewBox; `min="0"` lets a drawing without small words shrink freely. A drawing that matters on a phone gets a second file drawn at 335 px wide, passed as `narrow`, shown at 768 px and below. Wide drawings belong on pages without a contents rail, where they can reach their full width.

## Charts

**Anatomy.** No frame and no background. Bars and columns grow from a 1 px ink baseline at zero. Gridlines are 1 px edge, solid, at round values; their numbers sit in a gutter at the left, right-aligned, in Mono 14 faint. Time runs left to right with ticks on the baseline and labels under them.

**Marks.** Bars in a bar list are 12 px thick with square ends, their rows 8 px apart; columns in a drawing are at most 16 px wide. Stacked segments keep a 2 px ground gap. An empty value is a 2 px edge stub, as in the research pulse, so a timeline reads as continuous. Lines are 2 px ink with round joins; the last point is an 8 px dot with a 2 px ground ring and its value beside it in Mono. Timeline events are the same dots; events too close to separate stack upward 12 px apart.

**Labels.** Label selectively: the line's end, the extreme, the one change worth naming on a faint elbow leader. Never a number on every mark; the readout, the caption, or a table holds the rest.

**Series.** One series is ink. When one category is the point, it stays ink and the rest step back to tone 3 (`bars emphasis`). Two series: the subject in ink (the newer year, the thing the text is about) and the comparison in tone 3, drawn first: left in a pair, above in a row, behind on a plot. Three: tone 3, tone 2, ink. Each is named where it runs clear. More than three become small multiples. Two series share a chart only when they share a unit.

**Ordered categories.** The tone ramp in order, then open and dashed for what is unknown or derived (`units`). Three ordered steps with words inside them take ink, tone 2, and tone 4: ground words on the first two and ink words on the last read at 4.5:1 or better in both themes.

**The key.** Only when labels cannot sit on the marks. Swatches shaped like the marks (a 10 px square for fills, a 16 × 2 line for lines), each with its name and count in the label voice. In HTML it is `ul.chart-key` under the chart; in a drawing, one line under the axis.

**Text twins.** The caption names the values that matter. A unit chart's key carries every count. For exact values, follow the chart with a Markdown table.

### Forms

Each form below is drawn on the specimen page from the site's own data, and each has a function in `tools/figure-specimens.py`.

- **Line over time.** One 2 px ink line, the last point a dot with its value, the one change worth naming on a faint elbow leader. Gridlines at round values. A phone gets a `narrow` drawing with fewer year labels.
- **Paired bar list** (`bars series="2025, 2026"`). Two 8 px bars per row, 2 px apart, rows 12 apart, the comparison above in tone 3 and the subject under it in ink, each with its value; the key under the list. Screen readers hear each value with its series name.
- **Grouped columns.** Two columns per period at most, 20 px wide and 2 px apart, the comparison on the left; a zero is a 2 px edge stub. With a dozen values or fewer they sit on the caps and the gridlines go; with more, keep the gridlines and label the extremes only.
- **Two lines on one scale.** One unit only. Counts that grow one at a time are step lines. Each line is named once along its length where it runs clear of the other; where the ends meet, one value serves both. The comparison can be the instrument's optional layer, so the reader can take it away.
- **Before and after.** One row per item, sorted by the change, rises first. The earlier value is a tone 3 dot, the later an ink dot on its ground ring, joined by a 2 px edge line. The values stand in two Mono columns at the right whose heads, each with its dot, are the key; nothing is written beside the dots, where values would collide.
- **Stacked bars over periods.** Up to three ordered parts from the baseline out, 2 px ground gaps between them, counts inside 8 px from each segment's start. Bars keep their true length, so an unfinished year is shorter. The key under them names each step with its range.
- **Diverging columns.** An ink zero line, its meaning in the caption; above in ink, below in tone 3; signed gutter labels with a true minus (`+100`, `−100`).
- **Scatter.** 8 px dots on ground rings; the context group in tone 4 drawn first, the subject group in ink on top, each named once beside its cloud. Guides (a ratio, a trend) are 1 px edge lines named at their far end, clear of the gridlines. Each axis is titled once in the note voice: the y title above its numbers, the x title under its ticks at the right.
- **Calendar.** Years down, months across (or weeks and days), cells on 4 px ground gaps. Four sequential steps from tone 4 to ink, more is darker in light and lighter in dark; months still to come are open. The key under the grid gives each step's range. A second measure is a second state, not a second calendar.
- **Small multiples.** One panel per period or series, all on one scale, said once in the caption. Each panel is named in Mono ink at its top left with its total at its top right; one midline gridline, labeled in the first column only. Four across at 760 px; two on a phone through a `narrow` drawing.
- **Distribution.** A histogram of even bins, columns 2 px apart, groups stacked in tone 3 and ink and named beside their humps; the scale rounds up to the tallest bin. Both axes titled once.
- **Bars in a table.** A Markdown table with `{.bars}` after it: every right-aligned numeric column draws an 8 px ink bar from the cell's left edge, scaled to the column, the value at its right. Left-aligned numbers, such as years, stay plain.
- **Sparkline.** `{{</* spark values="…" label="…" */>}}` inside a sentence: 64 × 16 on the x-height, a 1.5 px ink line, the last point a dot. The label is what a screen reader hears; feeds and email drop the line, so the sentence must say the number itself.
- **Zone scale.** Eleven abutting patches for zones 0 to X, Roman numerals under them, the named zones described. The tones are the print's, so they are literal grays outside the palette and stay put in dark mode; 0 and X avoid the palette's own `#000000` and `#FFFFFF`.
- **Characteristic curve.** Density against exposure, a tick a stop, base plus fog as an edge line, toe, straight line, and shoulder named on faint elbows. A curve without measured data says "schematic" in its caption.

### `bars`

```markdown
{{</* bars caption="Published pages in each section, 2026-10-20." */>}}
Log | 93
Research | 28
Notes | 17
{{</* /bars */>}}
```

One line per bar: name, value, and optionally `tone-2`, `tone-3`, or `tone-4`. `emphasis="Research"` keeps that bar in ink and steps the rest to tone 3. `series="2025, 2026"` takes two values per line (`Notes | 5 | 10`) and pairs them, the first series in tone 3 and the second in ink, with a key under the list. Names stand right-aligned against the baseline, like the keys in a ledger; values print as written and the bars scale to the largest. The figure holds to the 640 px measure unless `width="bleed"` or `"wide"`.

### `units`

```markdown
{{</* units caption="Every recorded fact in the studio specification." */>}}
Measured | 2 | ink
Confirmed | 34 | tone-2
Product specification | 16 | tone-3
CAD drawing | 11 | tone-4
Derived | 3 | dashed
Estimated | 113 | open
{{</* /units */>}}
```

One line per category: name, count, and its mark (`ink`, `tone-2` to `tone-4`, `open`, `dashed`). Squares are 12 px, 3 px apart, 25 to a row (20 on phones; `per-row` and `per-row-narrow` change them). The key under the squares carries every count, so the squares themselves are hidden from screen readers. Suits totals up to a few hundred.

## Diagrams

Diagrams are drawn for the site when they explain how something works and can be redrawn as it changes. An illustration of one particular thing (a shelf, a label sheet, a drawer) stays an image (Pictures).

- **A system.** Parts as boxes, 64 px tall for a name and one line, 12 px padding; the layers named by column heads in the note voice; connectors between parts with their words above the line. The subject alone takes the 2 px line and the surface face; whatever runs outside the system is dashed, boxes and connectors alike.
- **A pipeline.** Equal boxes left to right, 20 px apart, joined by arrows without words, each step numbered `01`, `02` in Mono faint above its box, like a note's section numerals. A branch drops from the step it leaves and runs right below the main line; an outside service is dashed.
- **A tree.** Left to right, without boxes: the root in the name voice, its children in a column joined by a 1 px ink bracket, their children in the label voice one column further; a count in Mono faint after a name.
- **Spans.** One row per item, the names right-aligned in a gutter, an 8 px ink bar from start to end (a single day is an 8 px square), a dashed faint line for today with its date in Mono over it, year ticks under the rows.
- **Events.** 8 px dots on a 1 px ink axis, stacked upward 12 px apart where they meet; the first and last numbered in Mono.
- **Eras.** Bands above the events' axis, 15 px tall on surface with an edge frame, 3 px apart, each named at its outer edge in the label voice; the events keep their dots under them.
- **Shapes for an argument.** A spectrum is a 1 px ink line between two poles named under its ends, the things on it as dots with a name and a muted line above. A matrix is a square with an edge frame and an ink cross, its axes named at their ends, things as dots named to the right. A cycle is three or four dots on a circle joined by arcs with heads. Containment is boxes inset 14 px, the innermost the subject. A stack is full-width bands 44 px tall, 8 apart, name and description in each, the subject at 2 px on surface.
- **States.** Boxes for states, a 12 px ink dot for the start, connectors with their trigger above; a state not yet real is dashed, and a loop above a box is what can happen without changing it.
- **Sequence.** One lane per party, a box with its name over an edge lifeline; each message a connector from lane to lane in order down the page, its words above it and its number in Mono at the left.
- **Sizes to scale.** Real objects at one stated scale (2 px to the millimetre for film and paper), on surface faces, bottom-aligned, each with faint dimension lines and end ticks, the measure in Mono with its unit spaced (`36 mm`), a scale bar under them.
- **Keyboard.** Keycaps 46 px on a 50 px pitch, radius 2. Keys that matter in ink with a 2 px bottom edge and their legend in Mono; the rest an edge outline without legends.
- **Map.** North up. Land is the ground, parks surface, water edge, streets edge and tone 4, expressways 2 px tone 3, a route 2 px ink; stations a 6 px square with the name on a ground knockout; places numbered 24 px ink markers on ground rings, stepping aside on a leader where they meet; a scale bar at the bottom left; an edge frame. The caption lists the places and credits OpenStreetMap. Drawn by `tools/map.py` (Making Figures), with a phone version from the same file, since a map is read on a phone.
- **Steps.** Numbered panels across the width, `01` in Mono faint above each, the drawing in the panel, two muted lines under it; a fold or cut still to come dashed, a movement a curved connector. A process in photographs would take the same panels; that form waits for a page that needs it.

## Drawings

```markdown
{{</* drawing src="/visuals/notes/2026-11-02-log-words.svg"
     alt="Line chart of the words in each Log month from 2019-01 to 2026-09…"
     caption="Words in each Log month." */>}}
```

| Parameter | Does |
|---|---|
| `src` | The SVG under `static/`, beside the page's other media. Required |
| `alt` | What the drawing shows and its point; becomes the SVG's title. Required |
| `caption` | Markdown, in the label voice under the drawing |
| `width` | `measure` or `wide`; the bleed by default |
| `min` | The width in px below which it scrolls; three quarters of the viewBox by default; `0` to shrink freely |
| `narrow` | A second SVG drawn at 335 px, shown on phones |
| `states` | Makes an instrument with a segmented control of up to five comma-separated states; `states-label` names it (`Show` by default) |
| `toggle` | Makes an instrument with a toggle of this name; `toggle-on="true"` starts it on |
| `scrub` | Makes an instrument with a scrubber of this name |

The shortcode drops the file's `<style>`, `<title>`, `<desc>`, comments, and prolog, so nothing in a file can restyle the page; prefixes its ids per figure, so two drawings on one page never share a clip path; and marks the SVG `role="img"` with the alt as its title. In the RSS feed (`partials/rss-content.html`) the drawing becomes an image of its file, or of the PNG beside it when there is one.

A minimal drawing, by hand or by script:

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="760" height="64" viewBox="0 0 760 64" fill="none">
  <rect x="0.5" y="0.5" width="229" height="63" fill="#F7F7F7" stroke="#000"/>
  <text x="12" y="26" font-family="IBM Plex Sans" font-size="16" font-weight="500" fill="#000">Studio brain</text>
  <text x="12" y="48" font-family="IBM Plex Sans" font-size="14" fill="#555555">Mac mini now, NAS later</text>
</svg>
```

Colors are attributes, never classes or a `<style>` block, so the page's mapping can find them.

### Making One

1. Decide whether HTML can do it (`bars`, `units`, a table). If so, stop there.
2. Set the artboard to the design width, one unit per pixel.
3. Draw with the palette, the lines, and the type above. Keep words as text.
4. Export. Figma: SVG, **Outline text off**, **Include "id" attribute** off. Illustrator: Styling **Presentation Attributes**, Font **SVG**, decimal places 1. A script: write attributes, as in the example. `tools/figure-specimens.py` draws every specimen this way and is the worked example: its helpers measure each label with the Plex font files and warn when a word outgrows its box.
5. Save it under `static/visuals/<section>/` with the page's date prefix, like any other media: `2026-11-02-log-words.svg`.
6. Place it with the `drawing` shortcode, with an alt and usually a caption.
7. If the page goes out in the RSS feed or a Flâneur dispatch, render the PNG beside it: `uv run tools/drawing-png.py static/visuals/…/name.svg`. It draws the light version on white at 2× in the site's own Plex subsets, so a reader without Plex sees the same drawing. The same PNG can serve as a project's `image` for its social card.
8. Check it in light and dark, with high contrast, at 375 px, and in the feed. The dev server inlines a drawing when it renders the page and does not watch the file itself: after redrawing an SVG, edit the page or restart the server to see it.

## Instruments

A figure the reader operates is an instrument: its controls above, the well, the readout under the well, then the caption. Without its script it is still a complete figure.

| Control | For | Markup |
|---|---|---|
| Segmented control | One of a few views, at most five | `states="Words, Bullets"`; the file's `<g data-state="1">` to `"5"`, one showing at a time |
| Toggle | Showing or hiding one optional layer, such as a comparison | `toggle="…"`; the file's `<g data-optional="">` |
| Scrubber | Moving through ordered marks: days, frames, steps | `scrub="…"`; the file's `[data-mark]` elements |
| Quiet key | An action: play, step, reset | `.btn.quiet` |

States and the toggle work by CSS alone (`:has()`), as the square-crops ratios do; only the scrubber needs a script. Whatever every state shares stays outside the state layers, and every state after the first carries `display="none"` in the file, so the file and its PNG show the first; the page's CSS takes over inline. All controls are blocks on shadows from `components/_control.scss`, 32 px high (44 px for touch), with the signal focus ring. The toggle is a quiet key with a lamp after its name, edge when off and signal when on, since a layer that is showing is live; its face never inverts, so it never reads as a selected segment. The scrubber is a 2 px edge track (a position, not an amount, so nothing fills) with a 12 × 24 thumb on a 2 px ink shadow that turns ink while held.

**The well.** Ground with a 1 px edge frame, radius 2, 16 px padding (12 on phones). The figure grows by the padding and frame, so the drawing inside keeps its designed width. Ground rather than surface, so the drawing's knockouts stay invisible.

**The readout.** One line under the well in the label voice, muted, numbers in Mono. It opens on the latest or most telling mark, so the still figure already says something, and it is the only tooltip: fixed in place, it works on touch and never covers a mark.

**A scrubbed mark.** Each mark is a group carrying its readout and a band:

```svg
<g data-mark="" data-readout="2026-10-06 · 7 entries in Ambient Computing">
  <rect data-band="" x="…" y="…" width="24" height="120" fill="none"/>
  <rect x="…" y="…" width="16" height="112" fill="#000"/>
</g>
```

The band, the mark's width plus 8 and the plot's height, takes the highlight when its mark is chosen. `assets/js/scrub.js` (loaded only where a scrub is) moves through the marks with the range, picks the mark nearest the pointer as it moves or drags across the well, writes the readout with its numbers in Mono, and sets the range's `aria-valuetext`. A `narrow` drawing must draw the same marks in the same order.

**Rules.** One instrument answers one question, with at most two controls, named in the order the reader uses them. Marks never move or resize under the hand; only the band lights. Nothing plays by itself, and anything that animates is a clip. Without the script the scrubber stays hidden and the readout shows the latest mark; without `:has()` the first state and the optional layer show, and the controls do nothing. In feeds the controls and readout drop out and the drawing becomes its image. A new behavior is a small script loaded the same way, never a charting library: the site has no npm build, and D3 or a chart kit would bring its own look.

**Canvas and WebGL.** Read colors from custom properties with `getComputedStyle` and redraw when `prefers-color-scheme` changes, as the live maps do. Walks and the spatial long exposure share one map, `assets/js/panel-map.js`: OpenFreeMap's vector tiles drawn after the Map pattern above (borders and streets stepped back toward the ground), with a page's own lines in tone 3 and its lit thing in the signal color. Media wells for photographs and scans stay dark, per Media Chrome.

## Pictures

Photographs, screenshots, renders, and clips follow the styleguide's Figures and Media Chrome. For figures specifically:

- **Screenshots** of software, including the studio's own apps, are pictures: their colors and uppercase labels belong to the program they show. Capture at 2× in light mode unless the program is dark, crop to the content without browser or desktop chrome, keep them under 2000 px wide, PNG for interfaces and JPEG for 3D and photographs. The method is in the headless capture notes (Playwright's headless shell over the DevTools protocol).
- **Annotated pictures** (`annotate`). Numbered 24 px ink markers on 2 px ground rings over a screenshot or photograph, each beside its part, never on it, placed in percent so the picture can be any size; the key under the picture as numbered lines in the label voice. Feeds keep the picture and the numbered key without the markers.

  ```markdown
  {{</* annotate src="/visuals/…/shot.jpg" alt="…" caption="…" */>}}
  82.5 | 13.6 | Its address
  {{</* /annotate */>}}
  ```

- **Comparisons** (`compare`). Two pictures of one view in one frame at the first picture's ratio, the first clipped at a divider the reader drags or moves with the arrow keys; a white 2 px divider and a handle, and a badge naming each picture in its top corner, in the media chrome's literal colors over photographs. Feeds and email show the two pictures one under the other, each named. The Solaris highway article compares its eight places this way.

  ```markdown
  {{</* compare first="/visuals/…/still.jpg" second="/visuals/…/today.jpg"
       first-label="Solaris, 1972" second-label="Street View" ratio="1.97" alt="…" */>}}
  ```

- **Illustrations for one page** (a plan, an elevation, a label sheet, a drawer from above) stay images, drawn wherever they are easiest to draw. To sit beside the drawn figures: the palette's values on white; Plex for every word, sentence case, never uppercase or tracked; everything at twice its display size (1520 px wide for the bleed), so 28 px words land at 14 and 2 and 4 px lines at 1 and 2; no title or paragraph inside, since the caption holds them; PNG, never JPEG. They stand on a white plate in both themes, the default figure frame, and their words shrink with them on a phone, so keep them sparse.
- **Alt text** says what the figure shows and what it is for, not "a diagram of". **Captions** sit in the label voice, held to the measure, with no "Figure 1".

## Making Figures

| Tool | Makes |
|---|---|
| `tools/figure-specimens.py` | Every drawing on the Figures page; the worked example for a figure drawn by script |
| `tools/figurelib.py` | The palette, the type, and the helpers the scripts share, with each label measured in Plex |
| `tools/chart.py` | Columns or a line from a CSV, written beside it: `uv run tools/chart.py columns data.csv` |
| `tools/map.py` | A map from a TOML file of places, stations, and routes, with OpenStreetMap data: `uv run tools/map.py map.toml` |
| `tools/drawing-png.py` | The PNG beside a drawing, for feeds, email, and social cards; `--width 600` for a dispatch |
| `site-chart` | A figure Hugo draws from the site's own pages at every build |

**Drawn by the build.** A figure about the site itself (how much was published, when, where) is drawn by a template from `site.RegularPages`, like the research pulse and `site-chart`, so it can't go stale. The template writes the drawing palette's literals into an inline SVG inside a `.drawing__frame`, so it themes like any drawing, and puts its summary in `data-live` for feeds. Drafts count only on the dev server.

**From a spreadsheet.** `chart.py` takes the x in the first column and one or two series after it. A dozen columns or fewer carry their values on their caps; more get gridlines. ISO dates make a time axis. The result is an ordinary drawing: place it with `drawing`, render its PNG if the page goes out by feed or email.

**A map.** Write the area, the places in the order the text meets them, and the stations to name into a TOML file beside the drawing (`narrow = 335` adds the phone version); `map.py` fetches the streets once and caches them. The numbered list it prints is the caption's.

**In the email.** A Flâneur dispatch carries a drawing as its PNG, 600 px wide and light in every mail client: render it with `tools/drawing-png.py --width 600`. A drawing for a dispatch is drawn at 600 px, so its words land at 14. The email template warns at build time when a drawing has no PNG. Comparisons arrive as their two pictures, annotated pictures without their markers, sparklines not at all.

## Icons

Interface icons are 16-unit stroke drawings in `layouts/partials/icons/`: a 1.25 stroke (1.5 for the small speaker), round caps and joins, `currentColor`, no fill, `aria-hidden="true"`, shown at 14 to 18 px. They stand in for glyphs Plex lacks (the envelope) and for controls (the loupe), never as decoration. The model viewer's drag hand is the one filled, multi-tone exception.

## Checklist

- Is it a figure at all, or a sentence or a table?
- HTML where HTML can do it; SVG for pictures of things.
- The palette only. Tones in order. Highlight for the selection, signal for a lamp.
- Words at 14 px or more at the design width, sentence case, numbers in Mono, ISO dates, no title inside.
- One subject, at 2 px or filled. Context in edge or tone 3. The unknown dashed or open.
- Labels on the marks; a key under them only if needed; every number also in text.
- Light, dark, high contrast, 375 px, the feed. Alt and caption.
- Instruments: complete without the script, usable by keyboard, a readout that opens on something.

## Audit, 2026-10-20

What the site already draws, measured against this guide.

| Figure | Where | Kind | Standing |
|---|---|---|---|
| Square crops | `/notes/square-sensors/` | Instrument, CSS only | The model for instruments: a segmented control, a figure tile, the grid in edge, the source dashed faint, the crop in the highlight under ink, the point in ink, the selection named under it, a PNG for feeds and print. Its tile is surface, the older well; leave it until the note changes |
| Reply following, 2026-10-22 | Hank for OpenClaw | Instrument, bespoke | Play and a scrubber over four phones that play one reply; the phones are pictures of Hank's interface in its own colors, everything around them Panel; a PNG still from `tools/reply-following-image.py` for feeds and readers without the script |
| Research pulse | Research hub | Chart in the chrome | Conforms: ink marks, edge stubs, the newest mark in the signal while it is live |
| Log archive | Log, Index | Table as chart | Conforms |
| Spatial long exposure | `/traces/spatial-long-exposure/` | WebGL map | Conforms since 2026-10-24: the Walks map (`panel-map.js`), places in the signal color and connections in tone 3, redrawn on a theme change |
| Contact sheet | `/newsletter/` | Drawing in the chrome | Conforms, with its own `--film` token |
| Social cards | `static/social/` | Generated ledger | Conforms |
| Icons | `partials/icons/` | Stroke icons | Conform; the drag hand is the exception |
| What to measure, 2026-10-19 (`facts.png`) | Ambient Computing | Raster unit chart | Close: Plex, grays, open and dashed marks. The headline number is inside the image, and the lightest gray falls under 2:1. The specimen page redraws it with `units` |
| Places get names, 2026-10-19 (`place-names.png`) | Ambient Computing | Illustration for one page | Stays an image, and stands as the example under Pictures on the specimen page. Close to the Pictures rules; `BOOKSHELF c3` and the spaced `A L E X 1` are uppercase and tracked |
| Tracking Highway Sequence from Solaris | Darkroom | Map and comparisons | Conforms since 2026-10-20: a map of the six places from `tools/map.py`, and each film still and Street View view as a comparison |
| Drawer labels, 2026-10-19 (`drawer-labels.png`) | Ambient Computing | Illustration for one page | Stays an image; its two headings (`Closed`, `Open, from above`) are titles inside it that the next one would leave to the caption |
| One brain, five surfaces, 2026-10-06 (`studio-brain.jpg`) | Ambient Computing | Raster diagram, JPEG | Furthest off: a title and a paragraph inside the image, uppercase tracked column heads, descriptions in Mono, words near 9 px on the page, so the caption asks readers to open it full size. Redrawn on the specimen page at 1120 px as `studio-brain.svg` |
| Studio plan, place card, wall screen, find a place, touch panel, Stream Deck, phone | Ambient Computing | Screenshots of the studio's apps | Fine as pictures; their room colors and uppercase are the apps' own |
| Labels REV.A, darkroom renders and photographs, metrics screenshots, historical maps | Research, Darkroom, Project Humane, Notes | Pictures | Fine |

**Next.** Illustrations for one page stay images and follow Pictures when the next one is drawn. The studio brain's SVG redraw is ready if its entry should use it, and the facts could become `units`.
