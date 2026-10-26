#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow", "mapbox-vector-tile"]
# ///
"""Build each walk's day for the Walks sheet: the ground under the route,
the clock (walking and standing), the neighborhoods and rivers it passes,
and every frame of its photo session.

Reads the vault manifest and the private photo manifest like build-walks.py
and writes static/traces/walks/days.json. Heights come from GSI's 10 m model
in Japan and from Terrarium elsewhere, never from the GPS; neighborhoods and
rivers from OpenFreeMap's vector tiles. Tiles are cached in
.local/walks/tiles. A session folder that is offline (the archive drive)
keeps the frames from the last run. docs/walks.md, The Day.

    uv run tools/walks-day.py
"""
import argparse
import importlib.util
import io
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import urllib.request
from zoneinfo import ZoneInfo

from PIL import Image
import mapbox_vector_tile

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / ".local/walks"
TILES = LOCAL / "tiles"
OUT = ROOT / "static/traces/walks/days.json"
RAWS = {".dng", ".raf", ".nef", ".cr3", ".arw"}
STEP = 20  # metres between samples along a route
AGENT = {"User-Agent": "Mozilla/5.0 (ttvl.co walks)"}

spec = importlib.util.spec_from_file_location("walks", Path(__file__).with_name("build-walks.py"))
walks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(walks)
distance = walks.distance

# Names the tiles carry only in Japanese, and channels too small to name.
NAMES = {
    "笄川": "Kogai River", "立会川": "Tachiai River", "笹目川": "Sasame River", "入間川": "Iruma River", "高沼用水東縁": None,
    "大字久下": "Kuge", "大字大河原": "Okawara", "大字永田": "Nagata", "永田台二丁目": "Nagatadai", "永田台三丁目": "Nagatadai",
    "大字川寺": "Kawadera", "大字阿須": "Asu", "大字岩沢": "Iwasawa", "舞浜": "Maihama", "舞浜二丁目": "Maihama",
    "松原町": "Matsubara-cho", "石屋町": "Ishiya-machi", "稲荷町一丁目": "Inari-machi", "稲荷町": "Inari-machi",
    "中鉢石町": "Naka-Hatsuishi", "上鉢石町": "Kami-Hatsuishi", "下鉢石町": "Shimo-Hatsuishi", "安川町": "Yasukawa-cho",
    "本町": "Hon-machi", "西町": "Nishi-machi", "匠町": "Takumi-cho", "山内": "Sannai", "花石町": "Hanaishi-cho",
    "久次良町": "Kujira-machi", "萩垣面": "Hagigakimen", "清滝": "Kiyotaki", "細尾町": "Hosoo-machi", "中宮祠": "Chugushi",
}
MACRON = str.maketrans("ōūāēīŌŪĀĒĪ", "ouaeiOUAEI")


def fetch(url, name):
    path = TILES / name
    if not path.exists():
        for attempt in range(4):
            try:
                path.write_bytes(urllib.request.urlopen(urllib.request.Request(url, headers=AGENT), timeout=40).read())
                break
            except Exception:
                if attempt == 3:
                    raise
    return path.read_bytes()


def tile_xy(lon, lat, z):
    n = 2 ** z
    return (lon + 180) / 360 * n, (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n


def tile_lonlat(x, y, z):
    n = 2 ** z
    return x / n * 360 - 180, math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))


# ---------- the ground ----------
_dem = {}


def dem_tile(z, x, y, japan):
    key = (z, x, y, japan)
    if key not in _dem:
        try:
            if japan:
                data = fetch(f"https://cyberjapandata.gsi.go.jp/xyz/dem_png/{z}/{x}/{y}.png", f"gsi-{z}-{x}-{y}.png")
            else:
                data = fetch(f"https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png", f"terr-{z}-{x}-{y}.png")
            px = Image.open(io.BytesIO(data)).convert("RGB").load()
        except Exception:
            px = None
        grid = [[None] * 256 for _ in range(256)]
        if px:
            for j in range(256):
                for i in range(256):
                    r, g, b = px[i, j]
                    if not japan:
                        grid[j][i] = r * 256 + g + b / 256 - 32768
                    else:
                        v = r * 65536 + g * 256 + b
                        grid[j][i] = None if v == 8388608 else (v * 0.01 if v < 8388608 else (v - 16777216) * 0.01)
        _dem[key] = grid
    return _dem[key]


def height(lon, lat, japan, z=14):
    fx, fy = tile_xy(lon, lat, z)
    px, py = fx * 256 - 0.5, fy * 256 - 0.5
    x0, y0 = math.floor(px), math.floor(py)
    vals = [dem_tile(z, (x0 + dx) // 256, (y0 + dy) // 256, japan)[(y0 + dy) % 256][(x0 + dx) % 256] for dy in (0, 1) for dx in (0, 1)]
    if any(v is None for v in vals):
        good = [v for v in vals if v is not None]
        return sum(good) / len(good) if good else None
    tx, ty = px - x0, py - y0
    return (vals[0] * (1 - tx) + vals[1] * tx) * (1 - ty) + (vals[2] * (1 - tx) + vals[3] * tx) * ty


def climb(heights, threshold=2.0):
    vals = [v for v in heights if v is not None]
    if len(vals) < 3:
        return 0, 0
    smooth = [sum(vals[max(0, i - 2):i + 3]) / len(vals[max(0, i - 2):i + 3]) for i in range(len(vals))]
    up = down = 0
    ref = smooth[0]
    for v in smooth[1:]:
        if v - ref >= threshold:
            up += v - ref
            ref = v
        elif ref - v >= threshold:
            down += ref - v
            ref = v
    return up, down


# ---------- the map's names ----------
_tiles = {}


def vector_tile(z, x, y):
    if (z, x, y) not in _tiles:
        if not hasattr(vector_tile, "url"):
            tilejson = json.loads(urllib.request.urlopen(urllib.request.Request("https://tiles.openfreemap.org/planet", headers=AGENT), timeout=30).read())
            vector_tile.url = tilejson["tiles"][0]
        data = fetch(vector_tile.url.format(z=z, x=x, y=y), f"omt-{z}-{x}-{y}.pbf")
        _tiles[(z, x, y)] = mapbox_vector_tile.decode(data, default_options={"y_coord_down": True})
    return _tiles[(z, x, y)]


def latin(props):
    for key in ("name:latin", "name_en", "name:en", "name_int", "name"):
        value = props.get(key)
        if value and re.search("[A-Za-z]", value):
            return value
    return props.get("name")


def clean(name):
    if not name:
        return None
    if name in NAMES:
        return NAMES[name]
    name = re.sub(r"^大字", "", name)
    name = re.sub(r"\s*\d+(-chome|\s*Chome)?$", "", name).translate(MACRON)
    return re.sub(r"^(Nishi|Higashi|Minami|Kita|Moto|Naka) (\w)", r"\1-\2", name)


def features(samples, layers, z=14):
    """Places and rivers from the tiles under a route and around it."""
    tiles = set()
    for s in samples[::5]:
        fx, fy = tile_xy(s[0], s[1], z)
        tiles.update((int(fx) + dx, int(fy) + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1))
    for tx, ty in sorted(tiles):
        tile = vector_tile(z, tx, ty)
        for name in layers:
            if name not in tile:
                continue
            extent = tile[name].get("extent", 4096)
            ll = lambda p: tile_lonlat(tx + p[0] / extent, ty + p[1] / extent, z)
            for f in tile[name]["features"]:
                g = f["geometry"]
                if g["type"] == "Point":
                    yield name, f["properties"], [[ll(g["coordinates"])]]
                elif g["type"] == "LineString":
                    yield name, f["properties"], [[ll(p) for p in g["coordinates"]]]
                elif g["type"] == "MultiLineString":
                    yield name, f["properties"], [[ll(p) for p in line] for line in g["coordinates"]]


def crossing(p1, p2, p3, p4):
    d = (p2[0] - p1[0]) * (p4[1] - p3[1]) - (p2[1] - p1[1]) * (p4[0] - p3[0])
    if abs(d) < 1e-12:
        return None
    t = ((p3[0] - p1[0]) * (p4[1] - p3[1]) - (p3[1] - p1[1]) * (p4[0] - p3[0])) / d
    u = ((p3[0] - p1[0]) * (p2[1] - p1[1]) - (p3[1] - p1[1]) * (p2[0] - p1[0])) / d
    return t if 0 <= t <= 1 and 0 <= u <= 1 else None


# ---------- the route ----------
def local_minutes(t, zone):
    lt = t.astimezone(zone)
    return lt.hour * 60 + lt.minute + lt.second / 60


def resample(segments):
    """A sample every STEP metres along each segment: lon, lat, metres from
    the start, the time (interpolated), and the segment."""
    out, cum = [], 0.0
    for si, seg in enumerate(segments):
        if len(seg) < 2:
            continue
        nxt = 0.0
        for a, b in zip(seg, seg[1:]):
            d = distance(a["coord"], b["coord"])
            while nxt <= d:
                f = nxt / d if d else 0
                t = a["time"].timestamp() + f * (b["time"].timestamp() - a["time"].timestamp()) if a["time"] and b["time"] else None
                out.append([a["coord"][0] + f * (b["coord"][0] - a["coord"][0]), a["coord"][1] + f * (b["coord"][1] - a["coord"][1]), cum + nxt, t, si])
                nxt += STEP
            nxt -= d
            cum += d
        last = seg[-1]
        out.append([last["coord"][0], last["coord"][1], cum, last["time"].timestamp() if last["time"] else None, si])
    return out


def on_foot(segments, zone):
    """Runs of walking (w) and standing (s) in local minutes, and the
    unrecorded gaps between segments (g). Under 0.4 m/s is standing; a
    stand under 90 s counts as walking."""
    runs = []
    for si, seg in enumerate(segments):
        pts = [p for p in seg if p["time"]]
        for a, b in zip(pts, pts[1:]):
            dt = (b["time"] - a["time"]).total_seconds()
            if dt <= 0:
                continue
            state = "w" if distance(a["coord"], b["coord"]) / dt >= 0.4 else "s"
            t0, t1 = local_minutes(a["time"], zone), local_minutes(b["time"], zone)
            if runs and runs[-1][2] == state and abs(runs[-1][1] - t0) < 0.01:
                runs[-1][1] = t1
            else:
                runs.append([t0, t1, state])
        nxt = [p for p in segments[si + 1] if p["time"]] if si + 1 < len(segments) else []
        if pts and nxt:
            runs.append([local_minutes(pts[-1]["time"], zone), local_minutes(nxt[0]["time"], zone), "g"])
    merged = []
    for a, b, state in runs:
        if state == "s" and b - a < 1.5:
            state = "w"
        if merged and merged[-1][2] == state:
            merged[-1][1] = b
        else:
            merged.append([a, b, state])
    return [[round(a, 2), round(b, 2), s] for a, b, s in merged]


def shutter(record, zone, t0, previous):
    """Every frame of the session, in seconds from the walk's start. A
    session that is offline keeps what the last run found."""
    folders = [Path(f) / "Capture" for f in record.get("source_folders", [])]
    if record.get("is_film") or not folders:
        return []
    if not all(f.is_dir() for f in folders):
        return previous
    raws = sorted(p for f in folders for p in f.iterdir() if p.suffix.lower() in RAWS and not p.name.startswith("."))
    times = []
    for start in range(0, len(raws), 200):
        result = subprocess.run(["sips", "-g", "creation", *map(str, raws[start:start + 200])], capture_output=True, text=True)
        for match in re.finditer(r"creation: (\d{4}):(\d{2}):(\d{2}) (\d{2}):(\d{2}):(\d{2})", result.stdout):
            times.append(int(match[4]) * 60 + int(match[5]) + int(match[6]) / 60)
    return sorted(round((m - t0) * 60) for m in times)


def build(args):
    manifest_path = Path(args.manifest).expanduser()
    manifest = json.loads(manifest_path.read_text())
    vault = manifest_path.parents[2]
    photos = {r["route_sha256"]: r for r in json.loads(Path(args.photos).expanduser().read_text())["records"]}
    public = {w["date"]: w for w in json.loads((ROOT / "data/walks.json").read_text())["walks"]}
    previous = json.loads(OUT.read_text())["walks"] if OUT.exists() else {}
    TILES.mkdir(parents=True, exist_ok=True)
    days = {}
    for record in manifest["records"]:
        if walks.EXCLUDED.intersection(record["flags"]) or record["date"] in walks.LEFT_OUT:
            continue
        walk = public[record["date"]]
        if walk["recording"] == "Sparse recording":
            continue
        rome = walk["region"] == "Rome"
        zone = ZoneInfo("Europe/Rome" if rome else "Asia/Tokyo")
        segments, _, _ = walks.reading_route(vault / record["vault_file"], record["date"], zone)
        samples = resample(segments)
        timed = [s for s in samples if s[3]]
        if not timed:
            continue
        start = timed[0][3]
        t0 = local_minutes(walks.datetime.fromtimestamp(start, zone), zone)
        for s in samples:
            s.append(height(s[0], s[1], not rome))
        heights = [s[5] for s in samples if s[5] is not None]
        up, down = climb([s[5] for s in samples])
        # Local metres, for crossings.
        lon0, lat0 = walk["bounds"][0]
        kx, ky = math.cos(math.radians(lat0)) * 111320, 110540
        xy = [((s[0] - lon0) * kx, (s[1] - lat0) * ky) for s in samples]
        labels, rivers = [], []
        for layer, props, parts in features(samples, ["place", "waterway"]):
            if layer == "place" and props.get("class") in ("suburb", "quarter", "neighbourhood", "village", "hamlet", "town"):
                name = clean(latin(props))
                if name:
                    lon, lat = parts[0][0]
                    labels.append((name, ((lon - lon0) * kx, (lat - lat0) * ky)))
            elif layer == "waterway" and props.get("class") in ("river", "canal") and props.get("name"):
                name = NAMES.get(props["name"], latin(props) or props["name"])
                if name:
                    for line in parts:
                        rivers.append((name, [((lon - lon0) * kx, (lat - lat0) * ky) for lon, lat in line]))
        # The neighborhood nearest each sample (within 900 m), held for 200 m or more.
        hoods = []
        for s, p in zip(samples, xy):
            best = min(labels, key=lambda l: (l[1][0] - p[0]) ** 2 + (l[1][1] - p[1]) ** 2, default=None)
            if not best or math.dist(best[1], p) > 900:
                continue
            if hoods and hoods[-1][2] == best[0]:
                hoods[-1][1] = s[2]
            else:
                hoods.append([s[2], s[2], best[0]])
        merged = []
        for a, b, name in (h for h in hoods if h[1] - h[0] >= 200):
            if merged and merged[-1][2] == name:
                merged[-1][1] = b
            else:
                merged.append([round(a), round(b), name])
        # Rivers crossed: the route 100 m either side lies on opposite banks,
        # at least 30 m from the line, so a walk along a bank is not a crossing.
        def opposite(i, u, v):
            lx, ly = v[0] - u[0], v[1] - u[1]
            length = math.hypot(lx, ly) or 1
            side = lambda q: ((q[0] - u[0]) * ly - (q[1] - u[1]) * lx) / length
            j0, j1 = max(0, i - 5), min(len(xy) - 1, i + 6)
            if samples[j0][4] != samples[i][4] or samples[j1][4] != samples[i][4]:
                return False
            a, b = side(xy[j0]), side(xy[j1])
            return a * b < 0 and abs(a) >= 30 and abs(b) >= 30
        crossed = []
        for i in range(len(samples) - 1):
            if samples[i][4] != samples[i + 1][4]:
                continue
            for name, line in rivers:
                for u, v in zip(line, line[1:]):
                    t = crossing(xy[i], xy[i + 1], u, v)
                    if t is not None and opposite(i, u, v):
                        at = samples[i][2] + t * (samples[i + 1][2] - samples[i][2])
                        if not any(c[1] == name and abs(c[0] - at) < 300 for c in crossed):
                            crossed.append([round(at), name])
        runs = on_foot(segments, zone)
        session = photos.get(record["sha256"], {})
        days[walk["id"]] = {
            "t0": round(t0, 2),
            "T": round(timed[-1][3] - start),
            "samples": [[round(s[0], 5), round(s[1], 5), round(s[2]), round(s[3] - start) if s[3] else None,
                         round(s[5], 1) if s[5] is not None else None, s[4]] for s in samples],
            "hoods": merged,
            "rivers": sorted(crossed),
            "runs": runs,
            "walking": round(sum(b - a for a, b, s in runs if s == "w")),
            "standing": round(sum(b - a for a, b, s in runs if s == "s")),
            "climb": round(up),
            "low": round(min(heights)) if heights else None,
            "high": round(max(heights)) if heights else None,
            "frames": shutter(session, zone, t0, previous.get(walk["id"], {}).get("frames", [])),
            "frames_total": session.get("candidate_count"),
        }
        print(f"{walk['id']}: {len(samples)} samples, {len(merged)} neighborhoods, {len(crossed)} rivers, {len(days[walk['id']]['frames'])} frames", file=sys.stderr)
    OUT.write_text(json.dumps({"walks": days}, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(f"{len(days)} days, {OUT.stat().st_size // 1024} KB → {OUT.relative_to(ROOT)}", file=sys.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--manifest", default="~/Notes/totocaster/Attachments/Walks/manifest.json", help="Private vault manifest.json")
    parser.add_argument("--photos", default=str(LOCAL / "photos.json"), help="Private photo manifest (source folders, frame counts)")
    build(parser.parse_args())
