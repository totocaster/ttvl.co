---
title: "Figures"
description: "How this site draws its diagrams, charts, and interactive figures, each one shown with the site's own numbers."
date: 2026-10-20
---

Each figure here is built from the same parts a note or a research entry uses, drawn with the site's own numbers as of 2026-10-20, and grouped by the job it does. Switch your system to dark mode and every figure follows; on a phone, the line chart, the small multiples, and the instrument change to drawings of their own.

## The Palette

{{< drawing src="/visuals/figures/palette.svg" alt="Nine swatches with their names and literal values: ink #000000, tone 2 #4F4F4F, tone 3 #7A7A7A, tone 4 #A3A3A3, edge #D9D9D9, surface #F7F7F7, ground #FFFFFF, highlight #FFEB3B, and signal #FF4F00, drawn as a single dot" caption="Every figure is drawn in these nine values. On the page each one becomes a color of the theme, so the drawing turns with dark mode, while the file on its own stays correct in light. Words take #000000, #555555, or #6E6E6E." >}}

## Lines

{{< drawing src="/visuals/figures/lines.svg" alt="Five line specimens: a rectangle in 1 px ink as an outline, one in 2 px ink as the subject, a 1 px edge grid as context behind a small outlined box, a dashed faint rectangle for what is not yet real, and a faint elbow leader from the word Drawer to a box" caption="Two weights of ink, one context line, one dash, one leader. Strokes keep their width at any scale." >}}

## Diagrams

### A system

{{< drawing src="/visuals/figures/studio-brain.svg" width="wide" alt="Diagram: four devices in the studio feed Home Assistant Green, the device layer, which sends states to the studio brain and takes calls back. The brain serves five surfaces: the wall screen, phones, the management site, the Stream Deck, and the iPads. Claude reads drawer photos for the brain. Outside it, the cameras reach Apple Home over HomeKit, which shows camera views on the iPads" caption="One brain, five surfaces, from the Ambient Computing stream, at the page's full width so every word is 14 px or more. The brain is the subject, so it alone takes the 2 px line and the surface fill; what runs outside it is dashed." >}}

### A pipeline

{{< drawing src="/visuals/figures/site-pipeline.svg" alt="Five numbered steps from left to right: write in Markdown, SCSS, and JavaScript; build with Hugo Extended 0.164.0; output pages, feeds, and a sitemap; deploy on DigitalOcean from main; read at ttvl.co. From the output, each dispatch also leaves as email.html, which Campaign Monitor, outside the site, sends to subscribers" caption="How a page gets from a text file to ttvl.co, and how a dispatch also leaves as email. Steps carry their numbers like the sections of a note." >}}

### A tree

{{< drawing src="/visuals/figures/site-tree.svg" width="measure" alt="Tree of the site's sections from ttvl.co: Projects with Darkroom 12, Project Humane 8, Obsidian 6, Notebook system 3, and Bookbinding 1; Notes 17; Research 28 with Ambient Computing 27 and Tools for Thought 1; Log 93; Newsletter 17; Traces 3; and About" caption="The site's sections and the pages in each." >}}

### Spans in time

{{< drawing src="/visuals/figures/section-spans.svg" alt="Horizontal spans from 2018 to 2026, one per section, from its first page to its latest: Notes from 2018-11, the Log from 2019-01, the Flâneur from 2021-02, all still running; Darkroom 2024-12 to 2025-08; Project Humane 2024-12 to 2026-09; the notebook system and Bookbinding as single moments; Obsidian 2025-09 to 2026-06; Traces 2026-07 to 2026-09; Research since 2026-10" caption="Each section from its first page to its latest. The dashed line is today." >}}

### Events in time

{{< drawing src="/visuals/figures/dispatches.svg" alt="Timeline from 2021 to 2026 with a dot for each of the 17 Flâneur dispatches, from 001 in 2021-02 to 017 in 2026-10; dispatches close in time stack" caption="Every Flâneur dispatch. Dispatches that went out within days of each other stack." >}}

## One Series

### A bar list

{{< bars caption="Published pages in each section." >}}
Log | 93
Research | 28
Notes | 17
Flâneur | 17
Darkroom | 12
Project Humane | 8
Obsidian | 6
Traces | 3
Notebook system | 3
Bookbinding | 1
{{< /bars >}}

### One bar as the point

{{< bars emphasis="Research" caption="Research reached 28 entries in its first three weeks." >}}
Log | 93
Research | 28
Notes | 17
Flâneur | 17
Darkroom | 12
{{< /bars >}}

### A line over time

{{< drawing src="/visuals/figures/log-words.svg" narrow="/visuals/figures/log-words-narrow.svg" alt="Line chart of the words in each Log month from 2019-01 to 2026-09: about 100 a month until 2024, then from 2024-11 between 230 and 490, ending at 372" caption="Words in each Log month. One line, labeled at its end and at the one change worth naming." >}}

## Two Series

### Side by side in rows

{{< bars series="2025, 2026" caption="Pages published in each section in 2025 and in 2026 so far. Built in HTML like the single bar list, so it reflows on a phone." >}}
Log | 12 | 9
Research | 0 | 28
Notes | 5 | 10
Darkroom | 8 | 0
Project Humane | 0 | 7
Flâneur | 5 | 4
Obsidian | 2 | 4
{{< /bars >}}

### Side by side in columns

{{< drawing src="/visuals/figures/pages-by-year.svg" alt="Grouped columns for 2021 to 2026, Flâneur dispatches in gray beside notes in ink: dispatches 3, 2, 1, 2, 5, 4; notes 0, 0, 0, 1, 5, 10" caption="Notes and Flâneur dispatches published each year. With a dozen small counts the values sit on the columns and the gridlines go." >}}

### On one scale over time

{{< drawing src="/visuals/figures/notes-and-dispatches.svg" toggle="Compare with the Flâneur" toggle-on="true" alt="Two step lines counting up from 2021 to 2026: Flâneur dispatches rise steadily from 0 to 17; notes stay at 1 or 2 until 2025, then climb to 17 by 2026-10" caption="Notes and dispatches counted up since 2021 (one note predates it). Both reach 17 in 2026-10: the dispatches over six years, most of the notes since 2025. The comparison is an optional layer." >}}

### Before and after

{{< drawing src="/visuals/figures/sections-change.svg" alt="One row per section from its 2025 count to its 2026 count: Research 0 to 28, Project Humane 0 to 7, Notes 5 to 10, Obsidian 2 to 4, Flâneur 5 to 4, Log 12 to 9, Darkroom 8 to 0" caption="The same numbers as the paired rows, drawn for the change: each row runs from 2025 to 2026, rises first and falls last, with the values in columns at the right." >}}

## Part to Whole

### Counted one by one

{{< units caption="Every recorded fact in the studio specification, from the Ambient Computing entry on what to measure next: 63 known, 116 still to check." >}}
Measured | 2 | ink
Confirmed | 34 | tone-2
Product specification | 16 | tone-3
CAD drawing | 11 | tone-4
Derived | 3 | dashed
Estimated | 113 | open
{{< /units >}}

### Year by year

{{< drawing src="/visuals/figures/log-lengths.svg" alt="One bar per year from 2019 to 2026, each split into long, medium, and short Log months. Through 2024 every month is medium or short; 2025 has 11 long months and 1 medium; 2026 has 9 long months so far" caption="Log months by length. Through 2024 none reached 250 words; since 2025 almost all have. Bars keep their true length, so 2026 stops at nine months." >}}

## Difference

### Above and below a baseline

{{< drawing src="/visuals/figures/log-difference.svg" alt="Columns for each Log month from 2019 to 2026, measured from the 2019–2024 median of 94 words: small rises and falls until 2024, then from 2024-11 every month above, by 140 to nearly 400 words" caption="Each Log month against the 2019–2024 median of 94 words: above it in ink, below it in tone 3." >}}

## Relationship

### Two measures of the same thing

{{< drawing src="/visuals/figures/log-scatter.svg" alt="Scatter plot of every Log month by bullets and words. The 2019–2024 months cluster in gray near 10 words a bullet; the 2025–2026 months in ink sit higher, near 30 words a bullet" caption="Every Log month by its bullets and its words. Since 2025 the bullets themselves run longer, from about 10 words each to about 30." >}}

## Calendar

### Year by month

{{< drawing src="/visuals/figures/log-calendar.svg" states="Words, Bullets" alt="Calendar of Log months, years 2019 to 2026 down and months 01 to 12 across, each cell shaded by its words in four steps; the 2025 and 2026 rows are the darkest. The last three months of 2026 are open" caption="Every Log month in four steps. The control switches the measure; the steps of each are in the key." >}}

## Small Multiples

### One small chart per year

{{< drawing src="/visuals/figures/log-years.svg" narrow="/visuals/figures/log-years-narrow.svg" alt="Eight small line charts, one per year from 2019 to 2026, each showing that year's words per Log month on the same scale: flat near 100 through 2024, then near 300 to 490 in 2025 and 2026. Totals run from 911 words in 2022 to 3,986 in 2025" caption="Words in each Log month, one panel per year, every panel on the same 0–500 scale so their heights compare. Four across, two on a phone." >}}

## Instruments

The two series over time above carry a toggle and the calendar a segmented control; both work by CSS alone. A scrubber moves through marks:

{{< drawing src="/visuals/figures/research-days.svg" narrow="/visuals/figures/research-days-narrow.svg" scrub="Day" alt="Column chart of research entries per day from 2026-10-01 to 2026-10-19: three to seven a day through 2026-10-06, none for twelve days, then three on 2026-10-19" caption="Research entries per day, from the journal's first day to its latest entry. Drag the scrubber, or move across the chart, and the readout names the day." >}}

## Pictures

An illustration made for one page, a shelf in elevation or a drawer from above, stays an image. Drawn on white in the palette and in Plex, it stands on a white plate in both themes, framed like any picture.

{{< figure src="/visuals/research/ambient-computing/2026-10-19-place-names.png" alt="Elevation drawing of the Bookshelf, a tall IVAR on the Lab's left wall, as a grid of columns a to e and rows 1 to 5 with every cell named; c3 is filled in black, a2 and e2 each hold a drawer above an open shelf, and the Alex carts park in b1 and c1" caption="The Bookshelf from the Ambient Computing stream, a PNG drawn on white." >}}
