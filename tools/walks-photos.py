# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow", "boto3"]
# ///
"""Pick the photographs each walk features, in the browser.

    make walk-photos                     # or: uv run tools/walks-photos.py
    uv run tools/walks-photos.py --port 8791 --manifest ~/path/to/manifest.json

Open http://localhost:8790. Every walk is listed at left; a walk shows its
picks in order (with their alt text) and, under them, every frame its photo
session offers: the edited Capture One exports (the "Unedited" switch adds
frames that were never exported, rendered from the DNG), or a film walk's
roll scans. Picks are kept as a private draft in .local/walks/picks.json as
you go. Apply renders the new picks the way the current ones were made
(1600 px on the long edge, sRGB, no metadata, a 360 px thumbnail) into the
private .local/walks/media, records their provenance in the private
.local/walks/photos.json, uploads them to the Space (tools/walks-media.py),
rebuilds data/walks.json with tools/build-walks.py, and runs
tools/test-walks.py.

macOS only: thumbnails, previews, and renders go through sips, capture times
come from the originals through sips and GPS through Spotlight's mdls. The
server listens on 127.0.0.1 and never publishes a source path. docs/walks.md.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import hashlib
import importlib.util
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import threading
from urllib.parse import unquote, urlparse

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / ".local/walks"
PHOTOS = LOCAL / "photos.json"
DRAFT = LOCAL / "picks.json"
CACHE = LOCAL / "cache"
OUT = ROOT / ".local/walks/media"
PAGE = Path(__file__).with_name("walks-photos.html")
FONTS = ROOT / "static/fonts/plex"
SRGB = "/System/Library/ColorSync/Profiles/sRGB Profile.icc"
PICTURES = {".jpg", ".jpeg", ".tif", ".tiff", ".png", ".heic"}
RAWS = {".dng", ".raf", ".nef", ".cr3", ".arw"}
# Which export of a frame to render from, best first, by its Output folder's name.
EXPORTS = ("web+social", "ig optimized", "apple photos", "jpegs")
LONG_EDGE, THUMB_EDGE, QUALITY, THUMB_QUALITY = 1600, 360, 85, 82

lock = threading.Lock()
frames = {}  # frame id -> frame, filled as walks are opened
pool = ThreadPoolExecutor(max_workers=4)


def load(path, fallback):
    return json.loads(path.read_text()) if path.exists() else fallback


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n")
    temp.replace(path)


def visible(path):
    return not path.name.startswith(("._", "."))


def frame_id(path):
    return hashlib.sha1(str(path).encode()).hexdigest()[:16]


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as file:
        for block in iter(lambda: file.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


# Capture times from the originals, one sips call per folder, cached by path
# and modification time so a session is read once.
def capture_times(paths):
    meta = load(CACHE / "times.json", {})
    stamp = lambda p: f"{p}|{p.stat().st_mtime_ns}"
    missing = [p for p in paths if stamp(p) not in meta]
    for start in range(0, len(missing), 200):
        batch = missing[start:start + 200]
        result = subprocess.run(["sips", "-g", "creation", "-g", "model", *map(str, batch)], capture_output=True, text=True)
        current = None
        for line in result.stdout.splitlines():
            if not line.startswith(" "):
                current = line.strip()
                continue
            key, _, value = line.strip().partition(": ")
            if current:
                meta.setdefault(current, {})[key] = value
        for p in batch:
            meta[stamp(p)] = meta.pop(str(p), {})
    if missing:
        save(CACHE / "times.json", meta)
    times = {}
    for p in paths:
        creation = meta.get(stamp(p), {}).get("creation", "")
        match = re.match(r"(\d{4}):(\d{2}):(\d{2}) (\d{2}:\d{2}:\d{2})", creation)
        times[p] = f"{match[1]}-{match[2]}-{match[3]}T{match[4]}" if match else None
    return times


def session_frames(record):
    """Every frame a walk's photo session offers, keyed by frame name: the best
    edited export of each, or the DNG alone ("unedited"), or a film scan."""
    found = {}
    for folder in map(Path, record["source_folders"]):
        if not folder.is_dir():
            continue
        if record["is_film"]:
            for scan in sorted(p for p in folder.iterdir() if visible(p) and p.suffix.lower() in PICTURES):
                found[scan.stem] = {"render": scan, "source": scan, "edited": True, "folder": folder.name}
            continue
        capture = folder / "Capture"
        raws = {p.stem: p for p in capture.iterdir() if visible(p) and p.suffix.lower() in RAWS} if capture.is_dir() else {}
        output = folder / "Output"
        exports = [p for p in output.rglob("*") if visible(p) and p.suffix.lower() in PICTURES and "Trash" not in p.parts] if output.is_dir() else []
        rank = lambda p: next((i for i, name in enumerate(EXPORTS) if name in p.parent.name.lower()), len(EXPORTS))
        for export in sorted(exports, key=rank):
            # An export carries its frame's name, sometimes with a suffix (L1002239-web1600).
            stem = max((s for s in raws if export.stem.startswith(s)), key=len, default=re.sub(r"[-_]web\d+$", "", export.stem))
            found.setdefault(stem, {"render": export, "source": raws.get(stem, export), "edited": True, "folder": folder.name})
        for stem, raw in raws.items():
            found.setdefault(stem, {"render": raw, "source": raw, "edited": False, "folder": folder.name})
    times = capture_times([f["source"] for f in found.values() if f["source"].suffix.lower() in RAWS])
    result = []
    for name, frame in found.items():
        frame.update(name=name, id=frame_id(frame["render"]), film=record["is_film"], time=times.get(frame["source"]))
        frames[frame["id"]] = frame
        result.append(frame)
    result.sort(key=lambda f: (f["time"] or "", f["folder"], f["name"]))
    return result


def walks_and_records():
    walks = load(ROOT / "data/walks.json", {"walks": []})["walks"]
    records = {r["date"]: r for r in load(PHOTOS, {"records": []})["records"]}
    return [(walk, records[walk["date"]]) for walk in walks if walk["date"] in records]


def find(walk_id):
    return next(((w, r) for w, r in walks_and_records() if w["id"] == walk_id), (None, None))


def applied_picks(record, offered):
    """The record's current images as picks: matched to a session frame by the
    original's name, or kept as they are when the session no longer has it."""
    by_name = {f["name"]: f for f in offered}
    picks = []
    for n, image in enumerate(record["images"], 1):
        frame = by_name.get(Path(image.get("source", "")).stem)
        if not frame:
            current = OUT / Path(image["src"]).name
            frame = {"render": current, "source": current, "edited": True, "film": record["is_film"], "folder": "On the site",
                     "name": Path(image.get("source_filename") or image["src"]).stem, "id": f"site-{record['key']}-{n:02}",
                     "time": image.get("capture_time_local"), "image": image}
            frames[frame["id"]] = frame
        picks.append({"id": frame["id"], "alt": image.get("alt", "")})
    return picks


def walk_payload(walk_id):
    walk, record = find(walk_id)
    if not walk:
        return None
    offered = session_frames(record)
    applied = applied_picks(record, offered)
    draft = load(DRAFT, {}).get(record["key"])
    picks = draft if draft is not None else applied
    known = {f["id"] for f in offered}
    extra = [frames[p["id"]] for p in applied if p["id"] not in known]
    public = lambda f: {k: f[k] for k in ("id", "name", "folder", "edited", "film", "time")}
    return {"id": walk["id"], "key": record["key"], "date": walk["date"], "title": walk["title"],
            "distance_km": walk["distance_km"], "film": record["is_film"],
            "folders": [Path(f).name for f in record["source_folders"]],
            "frames": [public(f) for f in offered + extra], "picks": picks, "applied": applied,
            "changed": draft is not None and draft != applied}


def walks_payload():
    drafts = load(DRAFT, {})
    return [{"id": w["id"], "date": w["date"], "title": w["title"], "film": r["is_film"],
             "picked": len(drafts.get(r["key"], r["images"])), "changed": r["key"] in drafts}
            for w, r in walks_and_records()]


# Pictures for the page: a 480 px thumbnail and a 1600 px preview of any
# frame, in sRGB, cached under .local/walks/cache.
def picture(frame, edge):
    target = CACHE / f"{frame['id']}-{edge}.jpg"
    if not target.exists():
        if frame["id"].startswith("site-") and edge >= LONG_EDGE:
            return frame["render"]
        target.parent.mkdir(parents=True, exist_ok=True)
        temp = target.with_suffix(".part.jpg")
        subprocess.run(["sips", "-Z", str(edge), "-s", "format", "jpeg", "-s", "formatOptions", "80",
                        "--matchTo", SRGB, str(frame["render"]), "--out", str(temp)], capture_output=True, check=True)
        temp.replace(target)
    return target


def render(frame, out, thumb):
    """The site's copy of a frame: 1600 px on the long edge, sRGB, progressive,
    no metadata; and its 360 px thumbnail."""
    with tempfile.TemporaryDirectory() as folder:
        middle = Path(folder) / "middle.jpg"
        subprocess.run(["sips", "-Z", str(LONG_EDGE), "-s", "format", "jpeg", "-s", "formatOptions", "best",
                        "--matchTo", SRGB, str(frame["render"]), "--out", str(middle)], capture_output=True, check=True)
        with Image.open(middle) as opened:
            image = ImageOps.exif_transpose(opened).convert("RGB")
        image.save(out, "JPEG", quality=QUALITY, progressive=True, optimize=True)
        small = image.copy()
        small.thumbnail((THUMB_EDGE, THUMB_EDGE), Image.Resampling.LANCZOS)
        small.save(thumb, "JPEG", quality=THUMB_QUALITY, progressive=True, optimize=True)
        return image.size


def gps(path):
    """[longitude, latitude] from Spotlight, or None. One attribute per call:
    mdls orders several by name, not as asked."""
    read = lambda name: subprocess.run(["mdls", "-raw", "-name", name, str(path)], capture_output=True, text=True).stdout.strip("\0 \n")
    try:
        return [float(read("kMDItemLongitude")), float(read("kMDItemLatitude"))]
    except ValueError:  # "(null)": no position recorded
        return None


def new_image(frame, alt, picked_on):
    """The private record of a newly picked frame: what the builder reads, and
    where it came from."""
    source = frame["source"]
    raw = source.suffix.lower() in RAWS
    image = {"alt": alt, "source": str(source), "source_filename": source.name,
             "source_sha256": sha256(source), "source_hash_status": "verified", "source_size_bytes": source.stat().st_size,
             "source_mtime_ns": source.stat().st_mtime_ns,
             "capture_time_local": frame["time"] if raw else None, "timezone_offset": None,
             "gps": gps(source) if raw else None, "model": None, "make": None,
             "selection_basis": f"Picked in tools/walks-photos.py on {picked_on}"}
    if raw:
        image["capture_time_basis"] = "Camera creation time read with sips; timezone not recorded"
        image["gps_source"] = "Spotlight metadata of the original" if image["gps"] else None
        model = subprocess.run(["sips", "-g", "make", "-g", "model", str(source)], capture_output=True, text=True).stdout
        for key in ("make", "model"):
            found = re.search(rf"^\s+{key}: (.+)$", model, re.M)
            image[key] = found[1].strip() if found else None
    else:
        image["capture_time_basis"] = "Film roll archive date; shutter time unavailable"
    if frame["render"] != source:
        image.update(render_source=str(frame["render"]), render_source_sha256=sha256(frame["render"]),
                     render_source_kind="Existing Capture One edited JPEG export")
    elif raw:
        image["render_source_kind"] = "Rendered from the original with sips"
    return image


def apply(manifest):
    """Render every walk whose picks changed, record them, rebuild, and test."""
    drafts = load(DRAFT, {})
    data = load(PHOTOS, {"records": []})
    log, changed = [], []
    today = datetime.now().strftime("%Y-%m-%d")
    for record in data["records"]:
        picks = drafts.get(record["key"])
        if picks is None:
            continue
        offered = session_frames(record)
        current = applied_picks(record, offered)
        if picks == current:
            continue
        old = {p["id"]: image for p, image in zip(current, record["images"])}
        if any(not p["alt"].strip() for p in picks):
            raise ValueError(f"{record['key']}: every photograph needs alt text")
        images = []
        with tempfile.TemporaryDirectory() as folder:
            staged = Path(folder)
            for n, pick in enumerate(picks, 1):
                frame = frames[pick["id"]]
                name = f"{record['key']}-{n:02}"
                out, thumb = staged / f"{name}.jpg", staged / f"{name}-thumb.jpg"
                if pick["id"] in old:
                    image = dict(old[pick["id"]])
                    shutil.copy2(OUT / Path(image["src"]).name, out)
                    shutil.copy2(OUT / Path(image["thumb"]).name, thumb)
                    width, height = image["width"], image["height"]
                else:
                    image = new_image(frame, pick["alt"].strip(), today)
                    width, height = render(frame, out, thumb)
                image.update(alt=pick["alt"].strip(), src=out.name, thumb=thumb.name,
                             width=width, height=height, derivative_sha256=sha256(out))
                images.append(image)
            # Replace this walk's files: only names of the form <key>-NN(.|-thumb.)jpg.
            OUT.mkdir(parents=True, exist_ok=True)
            pattern = re.compile(rf"^{re.escape(record['key'])}-\d\d(-thumb)?\.jpg$")
            for stale in [p for p in OUT.iterdir() if pattern.match(p.name)]:
                stale.unlink()
            for made in staged.iterdir():
                shutil.move(made, OUT / made.name)
        record["images"] = images
        changed.append(record["key"])
        log.append(f"{record['key']}: {len(images)} photographs")
    if not changed:
        drafts.clear()
        save(DRAFT, drafts)
        return {"ok": True, "log": "Nothing changed.", "changed": []}
    images = [i for r in data["records"] for i in r["images"]]
    data["summary"].update(photos=len(images), outings_with_photos=sum(bool(r["images"]) for r in data["records"]),
                           film_photos=sum(len(r["images"]) for r in data["records"] if r["is_film"]),
                           photos_with_file_gps=sum(bool(i.get("gps")) for i in images),
                           source_hashes_verified=sum(i.get("source_hash_status") == "verified" for i in images),
                           source_hashes_pending=sum(i.get("source_hash_status") != "verified" for i in images))
    backups = LOCAL / "backups"
    backups.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PHOTOS, backups / f"photos-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json")
    save(PHOTOS, data)
    for key in changed:
        drafts.pop(key, None)
    save(DRAFT, drafts)
    # The Space before the site: the rebuilt data points at the uploaded files.
    spec = importlib.util.spec_from_file_location("media", Path(__file__).with_name("walks-media.py"))
    media = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(media)
    log += ["", "$ walks-media.py"]
    media.publish(media.wanted(), log=log.append)
    build = subprocess.run([sys.executable, "-I", "tools/build-walks.py", "--manifest", str(manifest), "--photos", str(PHOTOS),
                            "--editorial", "data/walks-editorial.json"], cwd=ROOT, capture_output=True, text=True)
    test = subprocess.run([sys.executable, "tools/test-walks.py"], cwd=ROOT, capture_output=True, text=True, env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin"})
    log += ["", "$ build-walks.py", (build.stdout + build.stderr).strip(), "", "$ test-walks.py", (test.stdout + test.stderr).strip()]
    return {"ok": build.returncode == 0 and test.returncode == 0, "log": "\n".join(log), "changed": changed}


class Handler(BaseHTTPRequestHandler):
    manifest = None

    def log_message(self, *args):
        pass

    def send(self, status, body, kind="application/json", cache="no-store"):
        data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", cache)
        self.end_headers()
        self.wfile.write(data)

    def file(self, path, kind):
        self.send(200, Path(path).read_bytes(), kind, "max-age=86400")

    def do_GET(self):
        path = unquote(urlparse(self.path).path)
        try:
            if path == "/":
                return self.send(200, PAGE.read_bytes(), "text/html; charset=utf-8")
            if path.startswith("/fonts/") and (FONTS / Path(path).name).is_file():
                return self.file(FONTS / Path(path).name, "font/woff2")
            if path == "/api/walks":
                return self.send(200, walks_payload())
            if path.startswith("/api/walk/"):
                payload = walk_payload(path.rsplit("/", 1)[1])
                return self.send(200, payload) if payload else self.send(404, {"error": "No such walk"})
            match = re.match(r"^/(thumb|preview)/([\w-]+)$", path)
            if match and match[2] in frames:
                edge = 480 if match[1] == "thumb" else LONG_EDGE
                return self.file(pool.submit(picture, frames[match[2]], edge).result(), "image/jpeg")
            self.send(404, {"error": "Not found"})
        except Exception as error:  # the page shows it; the server keeps running
            self.send(500, {"error": str(error)})

    def do_POST(self):
        path = urlparse(self.path).path
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        try:
            match = re.match(r"^/api/walk/([\w-]+)/(picks|reset)$", path)
            if match:
                walk, record = find(match[1])
                if not walk:
                    return self.send(404, {"error": "No such walk"})
                with lock:
                    # Read the session first, so the frames are known even
                    # after a restart; a draft that matches the site is no draft.
                    applied = applied_picks(record, session_frames(record))
                    drafts = load(DRAFT, {})
                    picks = [{"id": p["id"], "alt": p.get("alt", "")} for p in body.get("picks", []) if p["id"] in frames]
                    if match[2] == "reset" or picks == applied:
                        drafts.pop(record["key"], None)
                    else:
                        drafts[record["key"]] = picks
                    save(DRAFT, drafts)
                return self.send(200, walk_payload(match[1]))
            if path == "/api/apply":
                with lock:
                    return self.send(200, apply(self.manifest))
            self.send(404, {"error": "Not found"})
        except Exception as error:
            self.send(500, {"error": str(error)})


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--port", type=int, default=8790)
    parser.add_argument("--manifest", default="~/Notes/totocaster/Attachments/Walks/manifest.json", help="Private vault manifest.json for the rebuild")
    args = parser.parse_args()
    Handler.manifest = Path(args.manifest).expanduser()
    if not PHOTOS.exists():
        sys.exit(f"No photo manifest at {PHOTOS.relative_to(ROOT)}; see docs/walks.md.")
    if not Handler.manifest.exists():
        sys.exit(f"No vault manifest at {Handler.manifest}; pass --manifest.")
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Walk photographs: http://localhost:{args.port}  (Ctrl-C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
