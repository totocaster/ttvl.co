# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow"]
# ///
"""Build the Instagram Stories trace from the untouched export.

    uv run tools/build-stories.py              # probe, place, render, write data/stories.json
    uv run tools/build-stories.py --source DIR # another copy of the export

The export is one MP4 per story, in a folder per year, named with the moment
it was posted in UTC (`2021/2021-05-07 01.23.45 UTC.mp4`); photo stories are
videos too. Nothing in it is changed or copied into the repository.

Each story gets a local date and time and a city-level place. A story is first
put in Tokyo time; when the journal note for that day (the vault's
`YYYY-MM-DD.md`, its `location` frontmatter) puts the day in another country,
the story moves to that country's offset and takes the place of its new local
day. Only the city is kept (the prefecture for Japan outside Tokyo); street
addresses never leave the vault. Days without a journal location have no place.

Two kinds of picture sheet are rendered into .local/stories/media, both from
one frame of each story:
  d-<YYYY><a|b>  every day of a half-year as a row of up to six 66x118 frames,
                 which the sea flicks through by CSS steps (a = January-June)
  m-<YYYY-MM>    every story of a month as 180x320 frames, six across, for the
                 lens, the day's thumbnails, and the frame under each video
Each file is named with a hash of its contents, so a changed sheet is a new
address. tools/stories-media.py uploads the sheets and the videos to the Space.

Writes data/stories.json (public fields only), the page's card at
static/visuals/traces/stories/card.jpg, and the private upload manifest at
.local/stories/manifest.json. docs/stories.md.
"""
import argparse
from collections import OrderedDict, defaultdict
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / ".local/stories"
MEDIA = LOCAL / "media"
FRAMES = LOCAL / "frames"
CARD = ROOT / "static/visuals/traces/stories/card.jpg"
DATA = ROOT / "data/stories.json"
MEDIA_URL = "https://ttvl-websites.fra1.cdn.digitaloceanspaces.com/ttvl.co/traces/stories/"
SOURCE = Path.home() / "Movies/Instagram Stories"
VAULT = Path.home() / "Notes/totocaster"
EPOCH = dt.date(2017, 12, 1)

DAY_W, DAY_H, DAY_FRAMES = 66, 118, 6
MONTH_W, MONTH_H, MONTH_COLS = 180, 320, 6

# Journal locations come from the phone's geocoder: English, sometimes Japanese.
NAMES = {"東京都": "Tokyo", "茨城県": "Ibaraki", "神奈川県": "Kanagawa", "日本": "Japan", "Italia": "Italy",
         "ひたちなか市": "Hitachinaka", "小田原市": "Odawara", "Roma": "Rome", "Ha Noi": "Hanoi",
         "Île-de-France": "Paris", "Lazio": "Rome", "Karangasem": "Bali", "Honkoshimmachi": "Kagoshima",
         "Colonnato di Piazza San Pietro": "Vatican City", "Jewel Changi": "Singapore", "138A Arab St": "Singapore",
         "Palmas": "Canary Islands"}
REGIONS = {"Lazio", "Campania", "Tuscany", "Île-de-France", "Bali", "Liguria", "Lombardy", "Veneto"}


def offset(country, day):
    """Hours from UTC for the countries the journal visits; summer time by month."""
    summer = 4 <= day.month <= 10
    return {"Georgia": 4, "Armenia": 4, "Vietnam": 7, "China": 8, "Singapore": 8, "Indonesia": 8,
            "Italy": 2 if summer else 1, "France": 2 if summer else 1, "Spain": 2 if summer else 1,
            "Germany": 2 if summer else 1, "Vatican City": 2 if summer else 1,
            "Romania": 3 if summer else 2}.get(country, 9)


def journal(vault, date, cache={}):
    if date not in cache:
        note, parts = vault / f"{date}.md", None
        if note.is_file():
            m = re.search(r'^location:\s*"?(.*?)"?\s*$', note.read_text(encoding="utf-8")[:1500], re.M)
            if m and m.group(1).strip():
                parts = [NAMES.get(x.strip(), x.strip()) for x in m.group(1).split(",")]
        cache[date] = parts
    return cache[date]


def place(parts):
    """The city, never the street: Tokyo, Ito, Shizuoka, Tbilisi, Paris."""
    if not parts:
        return ""
    country = parts[-1]
    if country in ("Singapore", "Vatican City"):
        return country
    if country == "Japan":
        pref = parts[-2] if len(parts) > 1 else ""
        if pref == "Tokyo":
            return "Tokyo"
        city = re.sub(r"(-shi|-Shi| City)$", "", parts[-3]) if len(parts) > 2 else ""
        city = NAMES.get(city, city)
        if not city or re.match(r"^\d", city) or city.endswith("-Gun") or city == pref:
            return pref
        return f"{city}, {pref}"
    region = parts[-2] if len(parts) > 1 else country
    if region in REGIONS:
        city = parts[-3] if len(parts) > 2 and not re.match(r"^\d", parts[-3]) else ""
        if region == "Île-de-France" or not city:
            return NAMES.get(region, region)
        return NAMES.get(city, city)
    return NAMES.get(region, region)


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type:format=duration",
                          "-of", "json", str(path)], capture_output=True, text=True, check=True).stdout
    info = json.loads(out)
    return {"dur": round(float(info["format"]["duration"]), 1),
            "audio": any(s.get("codec_type") == "audio" for s in info.get("streams", []))}


def sha10(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:10]


def frame(story):
    """One 180x320 frame a third of the way in (or 1.2 s, whichever is sooner)."""
    out = FRAMES / (story["key"] + ".jpg")
    if not out.exists():
        t = min(1.2, story["dur"] * 0.35)
        subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", str(story["path"]), "-frames:v", "1",
                        "-vf", f"scale={MONTH_W}:{MONTH_H}:force_original_aspect_ratio=increase,crop={MONTH_W}:{MONTH_H},setsar=1",
                        "-q:v", "3", "-y", str(out)], check=True)
    return out


def save_sheet(im, stem):
    buf = io.BytesIO()
    im.save(buf, "WEBP", quality=72, method=6)
    body = buf.getvalue()
    name = f"{stem}.{hashlib.sha256(body).hexdigest()[:10]}.webp"
    (MEDIA / name).write_bytes(body)
    return name


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", type=Path, default=SOURCE, help="the export, a folder per year")
    parser.add_argument("--vault", type=Path, default=VAULT, help="the vault whose daily notes carry `location`")
    args = parser.parse_args()
    for d in (MEDIA, FRAMES):
        d.mkdir(parents=True, exist_ok=True)

    files = sorted(p for p in args.source.glob("[0-9][0-9][0-9][0-9]/*.mp4"))
    if not files:
        raise SystemExit(f"No stories under {args.source}")

    # Probes and hashes are slow on 1.5 GB; keep them while the file is unchanged.
    cache_path = LOCAL / "probe.json"
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}

    def known(path):
        st = path.stat()
        sig = f"{st.st_size}:{int(st.st_mtime)}"
        hit = cache.get(path.name)
        if hit and hit["sig"] == sig:
            return hit
        rec = {"sig": sig, **probe(path), "sha": sha10(path)}
        cache[path.name] = rec
        return rec

    with ThreadPoolExecutor(8) as pool:
        recs = list(pool.map(known, files))
    cache_path.write_text(json.dumps(cache))

    stories = []
    for path, rec in zip(files, recs):
        utc = dt.datetime.strptime(path.stem, "%Y-%m-%d %H.%M.%S UTC").replace(tzinfo=dt.timezone.utc)
        tokyo = utc + dt.timedelta(hours=9)
        parts = journal(args.vault, tokyo.date().isoformat())
        country = parts[-1] if parts else "Japan"
        local = utc + dt.timedelta(hours=offset(country, tokyo.date()))
        if local.date() != tokyo.date():
            later = journal(args.vault, local.date().isoformat())
            if later and later[-1] == country:
                parts = later
        key = utc.strftime("%Y-%m-%dT%H%M%SZ")
        stories.append({"path": path, "key": key, "utc": utc, "date": local.date().isoformat(),
                        "time": local.strftime("%H:%M"), "dur": rec["dur"], "audio": rec["audio"],
                        "place": place(parts), "video": f"{key}.{rec['sha']}.mp4"})
    stories.sort(key=lambda s: s["utc"])

    with ThreadPoolExecutor(8) as pool:
        frames = list(pool.map(frame, stories))
    for s, f in zip(stories, frames):
        s["frame"] = f

    # Month sheets: every story of a local month, 180x320, six across.
    months = OrderedDict()
    for i, s in enumerate(stories):
        months.setdefault(s["date"][:7], []).append(i)
    month_sheets = {}
    for m, ids in months.items():
        rows = (len(ids) + MONTH_COLS - 1) // MONTH_COLS
        im = Image.new("RGB", (MONTH_COLS * MONTH_W, rows * MONTH_H), (17, 17, 17))
        for k, i in enumerate(ids):
            im.paste(Image.open(stories[i]["frame"]).convert("RGB"), ((k % MONTH_COLS) * MONTH_W, (k // MONTH_COLS) * MONTH_H))
            stories[i]["slot"] = k
        month_sheets[m] = [save_sheet(im, f"m-{m}"), rows]

    # Day sheets: a row per day, newest first, up to six frames across.
    days = OrderedDict()
    for i, s in enumerate(stories):
        days.setdefault(s["date"], []).append(i)
    order = sorted(days, reverse=True)
    halves = defaultdict(list)
    for d in order:
        halves[d[:4] + ("a" if int(d[5:7]) <= 6 else "b")].append(d)
    day_sheets, day_rows = {}, {}
    for half, ds in halves.items():
        im = Image.new("RGB", (DAY_FRAMES * DAY_W, len(ds) * DAY_H), (17, 17, 17))
        for r, d in enumerate(ds):
            day_rows[d] = (half, r)
            for k, i in enumerate(days[d][:DAY_FRAMES]):
                t = Image.open(stories[i]["frame"]).convert("RGB").resize((DAY_W, DAY_H), Image.LANCZOS)
                im.paste(t, (k * DAY_W, r * DAY_H))
        day_sheets[half] = save_sheet(im, f"d-{half}")

    # The card for the Traces hub and the social preview: the newest days.
    CARD.parent.mkdir(parents=True, exist_ok=True)
    gap, cols, rows = 4, 23, 8
    card = Image.new("RGB", (cols * (DAY_W + gap), rows * (DAY_H + gap)), (255, 255, 255))
    for n, d in enumerate(order[: cols * rows]):
        t = Image.open(stories[days[d][0]]["frame"]).convert("RGB").resize((DAY_W, DAY_H), Image.LANCZOS)
        card.paste(t, ((n % cols) * (DAY_W + gap), (n // cols) * (DAY_H + gap)))
    card.crop((0, 0, 1600, 900)).save(CARD, "JPEG", quality=85, optimize=True, progressive=True)

    places = sorted({s["place"] for s in stories})
    pix = {p: k for k, p in enumerate(places)}
    data = {
        "media": MEDIA_URL,
        "count": len(stories),
        "days": len(days),
        "seconds": round(sum(s["dur"] for s in stories)),
        "first": stories[0]["date"],
        "last": stories[-1]["date"],
        "places": places,
        "day_sheets": day_sheets,
        "month_sheets": month_sheets,
        # newest first: date, day sheet, row, story indices in order
        "day": [[d, *day_rows[d], days[d]] for d in order],
        # oldest first: date, time, tenths of a second, sound, month, slot, place, video
        "story": [[s["date"], s["time"], round(s["dur"] * 10), int(s["audio"]), s["date"][:7], s["slot"],
                   pix[s["place"]], s["video"]] for s in stories],
    }
    DATA.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n")

    used = set(day_sheets.values()) | {v[0] for v in month_sheets.values()}
    for stale in MEDIA.glob("*.webp"):
        if stale.name not in used:
            stale.unlink()
    manifest = {name: str(MEDIA / name) for name in sorted(used)}
    manifest.update({s["video"]: str(s["path"]) for s in stories})
    (LOCAL / "manifest.json").write_text(json.dumps(manifest, indent=0))
    print(f"{len(stories)} stories on {len(days)} days, {data['seconds'] // 60} minutes; "
          f"{len(month_sheets)} month and {len(day_sheets)} day sheets; "
          f"{sum(1 for s in stories if s['place'])} stories placed, {len(places) - 1} places")


if __name__ == "__main__":
    main()
