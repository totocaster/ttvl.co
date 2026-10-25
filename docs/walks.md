# Walks

`/traces/walks/` is a separate Traces project. The map is the
page: every walk is drawn on one full-window map, and a panel floating at the
container's left edge holds the index (the head, place switches, every walk as
a row) or, once a walk is chosen from a row or a route, that walk's sheet: its
day hour by hour with the photographs on it, a journal excerpt, its details,
and links to published writing. Individual walks and photographs have hash
links, for example `/traces/walks/#walk-s0399/photo-2`.

The layout is `layouts/traces/walks.html`, the script `assets/js/walks.js` with
the map in `assets/js/walks-map.js` on the site's map in `assets/js/panel-map.js`
and the day in `assets/js/walks-day.js` (bundled by `js.Build`), and the styles
`assets/scss/sections/_walks.scss`. The design was chosen from five versions on
2026-10-23 (Atlas, Ledger, Places, Sequence, Field); this is Field. The day in
the sheet was chosen on 2026-10-25 from studies of a scrubber along the map's
foot, 3D views, and route shapes in the list; it keeps everything in the panel
and the map's foot clear.

## Places

The one filter is place. The layout assigns each walk a place from the middle
of its bounds: Tokyo within 18 km of Tokyo Station, Around Tokyo beyond that
(the day trips to Nikko, Mitake, Hanno, Kawagoe, and Omiya), and Rome. A
place's switch narrows the rows and the map together; pressing it again shows
every walk. Zoomed out past the cities, each place is a key on the map that
zooms to it. Walk numbers (`001`, `002`, …) run upward by date, like research
entries; never write them.

## Titles

A walk's title is its route, written from the track rather than the journal,
in Title Case: `Start to End` (Ochanomizu to Mizumoto Park), with `via X` for
the one stop that shapes the route, if any (Ueno to Shinjuku via Takadanobaba);
`Around X` for a loop or a wander that ends where it began (Around Kawagoe);
and `Along X` for a feature followed (Along the Aurelian Walls). Name stations,
parks, temples, and neighborhoods as the map does, in Hepburn without macrons
and with official hyphens (Yotsuya-sanchome, Kita-Senju). No "Walk", no city
(the place switch says it), and no mood: that belongs in the summary. The
title lives in `data/walks-editorial.json` and wins over the one the builder
derives; revise it there when a track is cut or extended.

## Reading Copy

`data/walks.json` is the public reading copy. The selection contains 41
outings from the 48 unique files in the vault archive. Waypoints, partial and
alternative exports, the cycling recording, and the combined backup are not
separate walking outings. Kuala Lumpur (2017-03-25: eleven points, no
photographs) is left out by choice through `LEFT_OUT` in the builder. The
original GPX and photo files remain in their archives. This site contains
derived route geometry and selected JPEGs only.

The JPEGs are not in the repository. The picker renders them into the ignored
`.local/walks/media`, and `tools/walks-media.py` publishes them to the shared
DigitalOcean Space `ttvl-websites` (fra1), the one toto.photo uses, under
`ttvl.co/traces/walks/` on its CDN. Each name carries a hash of its contents
(`2022-10-01-s0399-01.c99e1edf2c.jpg`), so a changed picture is a new address
and every file is cached for a year as immutable; the builder writes the same
addresses into `data/walks.json`, and fails when a rendered file is missing.
The upload key is a Spaces key scoped to that bucket (`ttvl-websites-walks`),
kept in the macOS Keychain as `ttvl-websites-spaces`. Only the page's card,
`static/visuals/traces/walks/map.jpg` (the Traces hub tile and the social
image: the map with every Tokyo walk and Ochanomizu to Mizumoto Park in the
signal orange, captured from the page itself), stays in `static/`.

`data/walks-editorial.json` contains the reviewed walk passages, descriptions,
place mentions, and published links. Quotes retain the journal's wording;
wikilinks become plain text. The initial research found 33 journal dates and
31 usable walk passages. Mentions of places are not automatically map stops.
Crosslinks identify writing about the outing, not proof that a particular
photograph was published there.

The photo export manifest is private input, retained in the ignored
`.local/walks/photos.json` alongside `journal-evidence.json`, not under `static/`.
It contains original file paths and metadata used to check
the selection. Exported JPEGs have their metadata removed. The builder only
copies an explicit set of public photo fields.

The first draft has 174 photographs across 40 outings, including 14 film
photographs. Of these, 143 can be placed using a nearby geotag or an approximate
camera-time match. Two film roll selections exclude unrelated scenes. Guitar
Street awaits reconciliation of conflicting camera and route dates. All
derivative hashes are verified; 33 of the private source-file hashes remain
explicitly pending in the provenance file.

## Rebuilding

```sh
python3 tools/build-walks.py \
  --manifest /path/to/vault/Attachments/Walks/manifest.json \
  --photos /path/to/reviewed-photo-manifest.json \
  --editorial data/walks-editorial.json
uv run tools/walks-media.py   # photographs the Space lacks; --check lists them
uv run tools/walks-day.py     # each walk's day for the sheet (The Day)
PYTHONDONTWRITEBYTECODE=1 python3 tools/test-walks.py
hugo server -D --port 1328 --destination /tmp/toto-walks-preview
```

The builder verifies archived GPX checksums, isolates the outing's local date,
and preserves gaps of over 30 minutes or 2 km. It retains the recorded shape;
it does not snap the track to roads or invent missing paths. Sparse recordings
are points. Transport-inclusive recordings do not imply a walking distance.
Two recordings ran on into train rides, and `WALK_WINDOWS` in the builder keeps
only the walk, cut at the stations by local time: Nikko (2019-03-08) from
arriving at JR Nikko to leaving it, and Kita-Ayase to Kita-Senju (2020-10-11) up
to Kita-Senju station, before the Yamanote loop. Each says so in its notes, and
with the rides gone both are measured as walks. Displayed distances are lengths
of retained recorded segments, not corrected activity totals.

Photo geotags are accepted only within 1 km of the retained route. Otherwise a
digital camera's capture time can be matched within a continuous track segment
whose bracketing points are no more than five minutes apart. These matches are
labeled approximate: camera clocks may be wrong. An explicit camera timezone
wins; otherwise the route's local timezone is assumed. Film scan dates are not
capture times. Unlocated photographs stay in sequence without map markers.

## The Sheet

A chosen walk's sheet opens with its number and place, the title, and the
summary; then its video, where it has one (On Video); the day hour by hour
(Hour by Hour, below); the photographs the day cannot hold, as small thumbs
(Without a Time or Place, or Along the Way when none has either, as on the
film walks and the sparse Kawagoe recording); the journal passage (From the
Journal), set as plain text in full ink, since every passage is quoted; and
then Details: the weekday and date; the time, from the first to the last
retained point of the recording, with its duration (left out for sparse
recordings); the distance; the steps (≈, the distance over a 0.75 m stride,
for a walker of 170 cm, since nothing on the walks counted them); the time on
foot, walking and standing, with the stops of four minutes or more; the
ground, the climb and the range of heights from the survey model, with the
distance below sea level where there is one; the weather from the journal's
frontmatter (`weather` in the editorial file, or the passage's); the camera,
from the photographs, or Film; and the frames, the session's count beside the
published ones. Elsewhere closes it. The journal's `location` stays out: it
is where the entry was written, often at home. The builder writes `started`,
`ended`, `minutes`, `weather`, `film`, and `video` for each walk.

## The Day

Hour by Hour draws the walk down the sheet (`assets/js/walks-day.js`): the
clock runs down the left, half hours where there is room; beside it the time
on foot (walking in ink, standing in tone 4, unrecorded gaps dashed); the
shutter (every frame of the session a hairline, the published ones in ink);
and the ground, wider where it is higher, stretched across the middle 90% of
the walk's own heights so a city walk's few meters read as clearly as a
mountain's hundreds (the rare heights beyond rest at the column's edges; the
height under the cursor follows it in 11 px type beside the lamp). In the
column at right, the photographs (small thumbs in their own shape with their
number; ≈ marks one placed on the route by its time, and says so under the
hand), the neighborhoods, and the rivers crossed, each where it happened in
time and joined to its moment by a hairline. The heading, a readout (the
time, distance, steps, ground, and what the walk was doing where), and
the key (Walking, Standing, Shutter, Ground: one line in 12 px type) stay at
the top of the sheet while the day scrolls under them.

Moving through the day walks a signal lamp along the route on the map: by
hand over the clock and the ground, or by scrolling (with the hand off the
clock, the cursor sits two fifths of the way down the panel).
The photograph last passed, or the one under the hand, takes an ink ring;
under the hand, in the sheet or on the map, its spot on the map takes a signal
ring. The lightbox opens any thumb and steps through the day's photographs.
A photograph sits on the clock by its capture time, or, without one, by the
time the recording passed its place.

The day's data is `static/traces/walks/days.json`, written by
`make walk-day` (`tools/walks-day.py`) from the vault manifest and the private
photo manifest: for each walk a sample every 20 m (position, distance, seconds
from the start, the ground's height, the recording segment), the
neighborhoods held for 200 m or more, the rivers crossed, the runs of walking
and standing, the shutter, and the totals. Heights come from GSI's 10 m model
in Japan and Terrarium in Rome, never the GPS, which puts Ochanomizu to
Mizumoto Park at 845 m of climbing where the ground climbs 13. Neighborhoods
and rivers come from OpenFreeMap's tiles; names the tiles carry only in
Japanese are romanized in the script. A river counts as crossed only where the
route 100 m either side lies on opposite banks, so a walk along a bank is not
a crossing. Under 0.4 m/s is standing, and a stand under 90 s counts as
walking. The shutter is read from each session's raw files with `sips`; a
session whose drive is offline keeps the frames from the last run. Tiles are
cached in `.local/walks/tiles`. Rerun it when a recording changes; picking
photographs does not need it, since the page sets them on the clock itself.

## Picking Photographs

`make walk-photos` (`tools/walks-photos.py`, page `tools/walks-photos.html`)
serves a picker at <http://localhost:8790>. Every walk is listed at left; a walk
shows its picks in order, with their alt text, and under them every frame its
photo session offers: the edited Capture One exports (the best of Web+Social,
IG Optimized, Apple Photos, then JPEGs), with frames never exported behind the
Unedited switch, or a film walk's roll scans. Press a frame to pick or drop it;
drag or use the arrows to reorder; ⤢ or Shift-press opens a large preview where
← → move and P picks. Picks are a private draft (`.local/walks/picks.json`) until
Apply, which renders the new ones as the others were made (1600 px on the long
edge, sRGB, no metadata, progressive at quality 85, a 360 px thumbnail) into
`.local/walks/media`, records their provenance in `.local/walks/photos.json` (a
backup goes to `.local/walks/backups/` first), uploads them to the Space,
rebuilds `data/walks.json`, and runs the tests; commit the data and push to
publish.
Capture times come from the original through `sips`, GPS through Spotlight's
`mdls`; a new pick's alt text starts as "Photograph from the walk" and its title,
which is worth replacing. Apply applies every walk with a draft, so finish or
undo the others first. macOS only; the originals' drive must be mounted, and a
sleeping external drive can take a minute to answer.

## Map and Fallback

MapLibre GL JS 6.15.0 is vendored under `static/vendor/maplibre/6.15.0/`, with its
license. OpenFreeMap supplies the vector tiles; the base style is built in
`panel-map.js` from the site's tokens after the figures guide's map: north up,
no tilt or rotation, land on the ground, parks on the surface, water in the
edge grey, and streets, rail, expressways, and borders stepped halfway from the
edge toward the ground, so the walks are the darkest lines on it. The spatial
long exposure draws on the same map, its places in the signal orange and its
connections in tone 3, so the two read as one. Every walk is drawn
in tone 3; the chosen one is ink on a ground casing with a start ring and an
end dot; the one under the hand, on the map or in the rows, is drawn in the
signal orange on a ground casing, above everything else. Its
photographs are the guide's numbered 24 px markers from z11.5, and the one under
the hand, or whose tile is, takes a signal ring. Colors are read from the
custom properties and redrawn when the scheme changes. The site sends no
photographs or journals to the tile service. The walk under the hand is
named by its row, so the map carries no badge; its corner speaks only when the
map fails. The scale bar sits at the foot of the container's right edge, under
the zoom keys' column, and the credit is small (11 px, under the site's 14 px
floor) in the window's corner.

On wide screens the page does not scroll: the map fills the window and runs up
under the masthead, where a fade to the ground replaces the masthead's rule;
the panel, the zoom keys, and every fit keep below it (`walks.js` measures the
masthead into `--walks-masthead`). On phones the map sits on top, under the
masthead the same way, and the panel is the page below it; two fingers move the
map there.

The panel works before and without the map: a walk opens at once and the map
frames it when it loads. If the tiles fail, the routes still draw on the
ground; if the map never loads, the corner says so. The map container's
`data-map-state` reads `loading`, `idle`, or `failed`, which is what captures
and tests wait for. Without JavaScript, the index is an ordinary page and its
rows lead to an expandable record of every walk. The builder's notes on a
recording (sparse, partial, isolated from other days, a ride cut, a folder
label that disagrees) stay in the data as the archive's record; the page does
not show them.

## Publishing

The page was published on 2026-10-24. To change its photographs: pick and
Apply (which uploads), or rebuild and run `tools/walks-media.py`; then commit
`data/walks.json` and push, and DigitalOcean deploys `main`. Check the lightbox
keys after a change, since the shared viewer resolves dynamic galleries at
click time.

The next editorial pass can write alt text for the photographs (most still read
"Photograph from the walk" and its title), add verified place labels, and add
missing outings without needing a new page structure.
