# Walks

The draft at `/traces/walks/` is a separate Traces project. The map is the
page: every walk is drawn on one full-window map, and a panel floating at the
container's left edge holds the index (the head, place switches, every walk as
a row) or, once a walk is chosen from a row or a route, that walk's sheet: its
photographs, a journal excerpt, and links to published writing. Individual
walks and photographs have hash links, for example
`/traces/walks/#walk-s0399/photo-2`.

The layout is `layouts/traces/walks.html`, the script `assets/js/walks.js` with
the map in `assets/js/walks-map.js` (bundled by `js.Build`), and the styles
`assets/scss/sections/_walks.scss`. The design was chosen from five versions on
2026-10-23 (Atlas, Ledger, Places, Sequence, Field); this is Field.

## Places

The one filter is place. The layout assigns each walk a place from the middle
of its bounds: Tokyo within 18 km of Tokyo Station, Around Tokyo beyond that
(the day trips to Nikko, Mitake, Chichibu, Kawagoe, and Omiya), and Rome. A
place's switch narrows the rows and the map together; pressing it again shows
every walk. Zoomed out past the cities, each place is a key on the map that
zooms to it. Walk numbers (`001`, `002`, …) run upward by date, like research
entries; never write them.

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
kept in the macOS Keychain as `ttvl-websites-spaces`. Only the page's social
card, `static/visuals/traces/walks/card.jpg`, stays in `static/`.

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
summary, then the day at a glance: the weekday and date; the time, from the
first to the last retained point of the recording, with its duration (left out
for sparse recordings); the distance; the weather from the journal's
frontmatter (`weather` in the editorial file, or the passage's); and the
camera, from the photographs, or Film. The journal's `location` stays out: it
is where the entry was written, often at home. The builder writes `started`,
`ended`, `minutes`, `weather`, and `film` for each walk.

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
`mdls`; a new pick's alt text starts as "Photograph from" and the walk's title,
which is worth replacing. Apply applies every walk with a draft, so finish or
undo the others first. macOS only; the originals' drive must be mounted, and a
sleeping external drive can take a minute to answer.

## Map and Fallback

MapLibre GL JS 6.15.0 is vendored under `static/vendor/maplibre/6.15.0/`, with its
license. OpenFreeMap supplies the vector tiles; the style is built in
`walks-map.js` from the site's tokens after the figures guide's map: north up,
no tilt or rotation, land on the ground, parks on the surface, water in the
edge grey, and streets, rail, and expressways stepped halfway from the edge
toward the ground, so the walks are the darkest lines on it. Every walk is drawn
in tone 3; the chosen one is ink on a ground casing with a start ring and an
end dot; the one under the hand, on the map or in the rows, is drawn in the
signal orange on a ground casing, above everything else. Its
photographs are the guide's numbered 24 px markers from z11.5, and the one under
the hand, or whose tile is, takes a signal ring. Colors are read from the
custom properties and redrawn when the scheme changes. The site sends no
photographs or journals to the tile service; the credit sits at the map's
corner.

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
"Photograph from" and the walk's title), add verified place labels, and add
missing outings without needing a new page structure.
