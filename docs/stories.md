# Instagram Stories

`/traces/stories/` keeps every story posted to Instagram since December 2017:
2,285 of them on 994 days, about six hours. The sea is the page. Every day is a
small tile that flicks through that day's frames, newest at the top, edge to
edge and up under the masthead, which a partial veil keeps readable while the
stories stay faintly behind it. Nothing else is on the page; below the last
row the footer is black. A lens follows the pointer at three times and names
the day under its center (date, time, place, how many stories). A click opens
the time key over the sea at the page's full width: the story large, the rest
of its day, Play and Sound, a Time scrubber over the years, and a day at a
time. While it is open the sea goes gray, the year playing comes back in
color, and the day playing is lit in the signal color.

The design was chosen on 2026-11-27 from studies on the design canvas (a
calendar, a wall, reels, a tape, a spectrum, then three "sea" versions: peek,
time key, loupe). This is the loupe, opening the time key on a click.

The layout is `layouts/traces/stories.html`, the script `assets/js/stories.js`
(bundled by `js.Build`, loaded when the page sets `stories: true`), and the
styles `assets/scss/sections/_stories.scss`. The data is `data/stories.json`.

## The Sea

The days fill the page's container, as many 33 × 59 tiles across as fit, and
the window beyond it is filled with repeats of other days, full strength, so
the sea runs to the window's edges at any width. The repeats are decoration:
they do nothing under the pointer. A chip marks each year's newest day.

Each tile flicks through up to six of its day's frames by CSS steps over its
row of a day sheet, on its own timing, so the sea shimmers rather than blinks.
Readers who prefer reduced motion get still tiles. Without the script the days
are a centered grid that still flickers, and a line says that opening a day
needs JavaScript.

The sea is focusable: the arrow keys move the lens across the days and Enter
opens one. On touch screens there is no lens; a tap opens the day.

## The Time Key

On wide screens the time key opens over the sea near where it was clicked, on
the page grid: the day's weekday, date, place, time, `1 of 3 that day`, and
length in the rail, flush right; the keys, the Time scrubber with a tick at
each new year, the story in a 288 × 512 media well, and the day's thumbnails in
the column. Below 1024 px the rail joins the column; on phones the time key
covers the window and scrolls, with Close beside the date.

A story starts playing as soon as the time key opens (the click that opened it
lets it play with sound), from the Space, and runs on through the archive in
order; Pause stops it, Play starts it again. Sound mutes and unmutes. The well
shows the story's frame until its video plays, `Loading…` while it waits, and
`The video did not load` if it fails, which stops playback. The left third of the well steps back, the rest
forward; ← → do the same from the keyboard, and Esc closes. Day before and Day
after jump a day; the Time scrubber jumps to the first story on or after its
day; any tile in the sea jumps to its day.

## Places and Times

The export names each video with the moment it was posted, in UTC. A story is
first put in Tokyo time. When the journal note for that day (the vault's
`YYYY-MM-DD.md`, its `location` frontmatter) puts the day in another country,
the story moves to that country's offset (Georgia +4, Italy and France +1 or +2
in summer, and so on) and takes the place of its new local day. About 150
stories moved that way.

The place is the city: Tokyo, Ito, Shizuoka, Tbilisi, Paris. Japan outside
Tokyo shows the city and prefecture, or the prefecture alone for districts.
Street addresses never leave the vault; the builder reads them and writes only
the city. Days without a journal location (208 of 994, most of them in 2017
and 2018) show "Place not recorded", and their stories stay in Tokyo time even
when the day was spent elsewhere, such as Tbilisi in August 2018.

## Media

The videos and two kinds of picture sheet live on the shared Space
`ttvl-websites` (fra1) under `ttvl.co/traces/stories/`, beside the walks'
photographs, each named with a hash of its contents and cached for a year as
immutable:

- the videos, byte for byte from the export (H.264 and AAC with the index at
  the front, which every browser streams), named by their posting time in UTC:
  `2021-05-07T012345Z.3f2a9c1b0d.mp4`;
- day sheets `d-<YYYY><a|b>`: every day of a half-year as a row of up to six
  66 × 118 frames (a = January to June), which the sea flicks through;
- month sheets `m-<YYYY-MM>`: every story of a month as 180 × 320 frames, six
  across, for the lens, the thumbnails, and the frame under each video.

About 1.6 GB in all. The page itself carries only `data/stories.json` (public
fields: dates, times, lengths, whether a story has sound, the city, and file
names) and the card, `static/visuals/traces/stories/card.jpg`, which is also
the page's social preview.

## Rebuilding

After a new export, replace the folder (one folder per year) and run:

```sh
make stories                                     # both steps below
uv run tools/build-stories.py                    # data, sheets, card
uv run tools/stories-media.py                    # what the Space lacks; --check lists it, --sheets skips the videos
```

The builder reads the export from `~/Movies/Instagram Stories` and the journal
from `~/Notes/totocaster` (`--source` and `--vault` change them). It keeps its
probes, hashes, and frames in `.local/stories` (ignored), so a rebuild takes
seconds, and writes the private upload manifest there. The uploader skips
files already in the Space and never deletes; it uses the walks' Spaces key
(`ttvl-websites-spaces` in the Keychain, or `SPACES_KEY` and `SPACES_SECRET`).

## Publishing

The page was published on 2026-11-27, once every video was on the Space. The
archive holds other people's faces and screenshots of messages that went out
for a day each; to take a story out, delete its video from the export folder,
rebuild, and push (its file stays on the Space, at an address nothing links
to). After a new export: `make stories`, then commit `data/stories.json` and
the card, and push; DigitalOcean deploys `main`. The dek is still a
placeholder.
