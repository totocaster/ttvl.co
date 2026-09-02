#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow>=11"]
# ///
"""Render the social (Open Graph) cards for ttvl.co.

Hugo emits a manifest of every page that gets a card (layouts/index.social.json,
built alone with `hugo --renderSegments social`). This script renders one
1200 x 630 card per entry with Pillow and writes it under static/social/, where
it is committed. The deploy never renders anything; head.html only resolves the
committed file. Helvetica Neue is read from the macOS system font file, which
the build box does not have, so cards are rendered on a Mac.

Usage:
  uv run tools/social-cards.py              render cards that are missing (or: make cards)
  uv run tools/social-cards.py --check      list missing, stale, and orphaned cards; render nothing
  uv run tools/social-cards.py --stale      also re-render cards whose inputs changed
  uv run tools/social-cards.py --all        re-render everything (after a design change)
  uv run tools/social-cards.py --only /notes/walking/ /darkroom/roll-id/
  uv run tools/social-cards.py --drafts     include draft pages, to prepare cards before publishing
  uv run tools/social-cards.py --manifest public/social.json   use an existing manifest

uv reads the inline metadata above, provisions Python and Pillow on first run,
and caches the environment; nothing is installed into the system Python.

Card styles (one per section voice):
  note           Ledger: kicker, rule, highlighted title, wordmark
  project        Mount: poster on a white mat over pale blueprint grid, wall label (JPEG)
  hub, site      Ledger with a dek
  flaneur        Plate: cover photo with a white label bottom left (JPEG). Dormant:
  flaneur-plain  Ledger with the engraving. Dispatch pages are email sources and
                 carry no metadata, so the manifest emits no entries for them.

The manifest sidecar static/social/manifest.json records a hash of each card's
inputs so --check and --stale can tell when a title, date, or poster changed.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile

try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps
except ImportError:  # pragma: no cover
    sys.exit("Pillow is required: run this script with `uv run tools/social-cards.py`")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC = os.path.join(ROOT, "static")
OUT_DIR = os.path.join(STATIC, "social")
SIDECAR = os.path.join(OUT_DIR, "manifest.json")

# Bump when the design changes so --check reports every card as stale.
DESIGN_VERSION = "1"

FONT_PATH = os.environ.get("SOCIAL_CARDS_FONT", "/System/Library/Fonts/HelveticaNeue.ttc")
FONT_INDEX = {"regular": 0, "bold": 1, "medium": 10}  # faces inside the .ttc

WORDMARK = os.path.join(STATIC, "ui", "ttvl_logo@3x.png")
ENGRAVING = os.path.join(STATIC, "ui", "flaneur_logo@3x.png")

W, H = 1200, 630
MARGIN = 96
LIVE = W - 2 * MARGIN  # 1008, the site's own container width

# Fixed light palette: the card is an image, so the site's tokens are baked in.
WHITE = (255, 255, 255)
INK = (0, 0, 0)
MUTED = (115, 115, 115)      # --ink-muted, 55% black on white
FAINT = (153, 153, 153)      # --ink-faint, 40% black on white
RULE = (238, 238, 238)       # --rule
EDGE = (221, 221, 221)       # --edge
SURFACE = (250, 250, 250)    # --surface
HIGHLIGHT = (255, 239, 98)   # --highlight, rgba(255,235,59,.8) on white
GRID_MINOR = (245, 247, 250)  # blueprint blue-grey at 5%
GRID_MAJOR = (235, 239, 244)  # blueprint blue-grey at 10%

SECTION_NAME = {
    "note": "Notes",
    "project": "Projects",
    "flaneur": "The Flâneur",
    "flaneur-plain": "The Flâneur",
    "hub": "ttvl.co",
    "site": "ttvl.co",
}

# Characters Helvetica Neue has no glyph for, or that should not break lines.
GLYPH_FIXES = {
    "‑": "-",   # non-breaking hyphen
    "‐": "-",   # hyphen
    " ": " ",   # no-break space
    " ": " ",   # thin space
    " ": " ",   # narrow no-break space
}


# --- text -------------------------------------------------------------------

_fonts = {}


def font(weight, size):
    key = (weight, size)
    if key not in _fonts:
        if not os.path.exists(FONT_PATH):
            sys.exit(f"Font not found: {FONT_PATH} (set SOCIAL_CARDS_FONT to a Helvetica Neue .ttc)")
        _fonts[key] = ImageFont.truetype(FONT_PATH, size, index=FONT_INDEX[weight])
    return _fonts[key]


def clean(text):
    text = str(text or "")
    for bad, good in GLYPH_FIXES.items():
        text = text.replace(bad, good)
    return " ".join(text.split())


def width(f, text):
    return f.getlength(text)


def wrap(text, f, max_w):
    """Greedy wrap by measured width; an overlong word is broken by character."""
    lines, current = [], ""
    for word in clean(text).split(" "):
        candidate = f"{current} {word}".strip()
        if width(f, candidate) <= max_w:
            current = candidate
            continue
        if current:
            lines.append(current)
        current = word
        while width(f, current) > max_w and len(current) > 1:
            cut = len(current)
            while cut > 1 and width(f, current[:cut]) > max_w:
                cut -= 1
            lines.append(current[:cut])
            current = current[cut:]
    if current:
        lines.append(current)
    return lines or [""]


def clamp(lines, max_lines, f, max_w):
    """Keep at most max_lines, ending the last kept line with an ellipsis."""
    if len(lines) <= max_lines:
        return lines
    kept = lines[:max_lines]
    last = kept[-1]
    while last and width(f, last + "…") > max_w:
        last = last[:-1].rstrip()
    kept[-1] = last + "…"
    return kept


def text_at(draw, x, y, text, f, fill, line_h, anchor="l"):
    """Draw one line inside a CSS-style line box of height line_h starting at y."""
    ascent, descent = f.getmetrics()
    top = y + (line_h - (ascent + descent)) / 2
    if anchor == "r":
        x = x - width(f, text)
    draw.text((x, top), text, font=f, fill=fill)


def kicker(draw, x, y, section, parts, size=26, line_h=34, fill_section=INK):
    """Section name in ink, the rest faint, separated by middle dots. Returns width."""
    f = font("regular", size)
    text_at(draw, x, y, section, f, fill_section, line_h)
    used = width(f, section)
    rest = "".join(f" · {clean(p)}" for p in parts if clean(p))
    if rest:
        text_at(draw, x + used, y, rest, f, FAINT, line_h)
        used += width(f, rest)
    return used


# --- images -----------------------------------------------------------------

_assets = {}


def asset(path):
    if path not in _assets:
        _assets[path] = Image.open(path).convert("RGBA")
    return _assets[path]


def paste_height(img, src, x, y, height, align="left"):
    """Paste an RGBA asset scaled to a height; align left or right on x."""
    ratio = height / src.height
    scaled = src.resize((max(1, round(src.width * ratio)), height), Image.LANCZOS)
    if align == "right":
        x = x - scaled.width
    img.paste(scaled, (round(x), round(y)), scaled)
    return scaled.width


def paste_contain(img, src, box):
    x, y, w, h = box
    scaled = ImageOps.contain(src, (w, h), Image.LANCZOS)
    img.paste(scaled, (x + (w - scaled.width) // 2, y + (h - scaled.height) // 2), scaled)


def paste_cover(img, path, box):
    x, y, w, h = box
    with Image.open(path) as src:
        src = ImageOps.exif_transpose(src).convert("RGB")
        fitted = ImageOps.fit(src, (w, h), Image.LANCZOS, centering=(0.5, 0.5))
    img.paste(fitted, (x, y))


def wordmark_and_url(img, draw):
    """The Ledger foot: wordmark bottom left, ttvl.co bottom right."""
    bottom = H - MARGIN
    paste_height(img, asset(WORDMARK), MARGIN, bottom - 72, 72)
    text_at(draw, W - MARGIN, bottom - 34, "ttvl.co", font("regular", 26), MUTED, 34, anchor="r")


def rule(draw, y, x0=MARGIN, x1=W - MARGIN):
    draw.rectangle([x0, y, x1 - 1, y + 1], fill=RULE)


# --- card styles ------------------------------------------------------------

def ledger_head(draw, entry):
    """Kicker on the first row and the hairline under it; returns the body's top y."""
    kicker(draw, MARGIN, MARGIN, SECTION_NAME[entry["style"]], entry.get("meta", []))
    rule(draw, MARGIN + 34 + 18)
    return MARGIN + 34 + 18 + 2 + 44


def render_note(entry):
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)
    y = ledger_head(draw, entry)
    f = font("bold", 64)
    lines = clamp(wrap(entry["title"], f, LIVE - 20), 3, f, LIVE - 20)
    for line in lines:  # the highlight: one band per line, as a selection renders
        draw.rectangle([MARGIN - 10, y, MARGIN + width(f, line) + 10, y + 76 - 1], fill=HIGHLIGHT)
        text_at(draw, MARGIN, y, line, f, INK, 76)
        y += 76
    wordmark_and_url(img, draw)
    return img


def render_flaneur_plain(entry):
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)
    y = ledger_head(draw, entry)
    body_w = 640
    f = font("bold", 56)
    for line in clamp(wrap(entry["title"], f, body_w), 3, f, body_w):
        text_at(draw, MARGIN, y, line, f, INK, 66)
        y += 66
    if entry.get("dek"):
        y += 20
        fd = font("regular", 30)
        for line in clamp(wrap(entry["dek"], fd, body_w), 3, fd, body_w):
            text_at(draw, MARGIN, y, line, fd, MUTED, 40)
            y += 40
    paste_contain(img, asset(ENGRAVING), (W - MARGIN - 300, 88, 300, 300))
    wordmark_and_url(img, draw)
    return img


def render_hub(entry):
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)
    y = ledger_head(draw, entry)
    f = font("bold", 64)
    for line in clamp(wrap(entry["title"], f, LIVE), 2, f, LIVE):
        text_at(draw, MARGIN, y, line, f, INK, 76)
        y += 76
    if entry.get("dek"):
        y += 20
        fd = font("regular", 30)
        for line in clamp(wrap(entry["dek"], fd, 900), 3, fd, 900):
            text_at(draw, MARGIN, y, line, fd, MUTED, 40)
            y += 40
    wordmark_and_url(img, draw)
    return img


def render_site(entry):
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)
    y = ledger_head(draw, entry)
    paste_height(img, asset(WORDMARK), MARGIN, y, 150)
    y += 150 + 28
    if entry.get("dek"):
        fd = font("regular", 30)
        for line in clamp(wrap(entry["dek"], fd, 900), 3, fd, 900):
            text_at(draw, MARGIN, y, line, fd, MUTED, 40)
            y += 40
    text_at(draw, W - MARGIN, H - MARGIN - 34, "ttvl.co", font("regular", 26), MUTED, 34, anchor="r")
    return img


def render_project(entry):
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)
    # Blueprint grid: minor line every 20 px, a heavier one every fifth.
    for x in range(0, W, 20):
        draw.line([(x, 0), (x, H)], fill=GRID_MINOR, width=1)
    for y in range(0, H, 20):
        draw.line([(0, y), (W, y)], fill=GRID_MINOR, width=1)
    for x in range(0, W, 100):
        draw.rectangle([x, 0, x + 1, H], fill=GRID_MAJOR)
    for y in range(0, H, 100):
        draw.rectangle([0, y, W, y + 1], fill=GRID_MAJOR)
    # White mat, frame, and the poster fitted inside.
    px, py, pw, ph = 200, 40, 800, 450
    draw.rectangle([px - 12, py - 12, px + pw + 11, py + ph + 11], fill=WHITE)
    draw.rectangle([px, py, px + pw - 1, py + ph - 1], fill=SURFACE, outline=EDGE, width=2)
    image = entry.get("image")
    if image:
        paste_cover(img, os.path.join(STATIC, image.lstrip("/")), (px + 2, py + 2, pw - 4, ph - 4))
    # Wall label: kicker over title at the left, wordmark 96 px tall at the right.
    label_bottom = 606
    mark_w = paste_height(img, asset(WORDMARK), px + pw, label_bottom - 96, 96, align="right")
    text_w = pw - mark_w - 40
    kicker(draw, px, label_bottom - 38 - 4 - 32, "Projects", entry.get("meta", []), size=24, line_h=32)
    ft = font("bold", 30)
    title = clamp(wrap(entry["title"], ft, 10_000), 1, ft, text_w)[0]
    text_at(draw, px, label_bottom - 38, title, ft, INK, 38)
    return img


def render_flaneur(entry):
    img = Image.new("RGB", (W, H), WHITE)
    cover = entry.get("image")
    if cover:
        paste_cover(img, os.path.join(STATIC, cover.lstrip("/")), (0, 0, W, H))
    draw = ImageDraw.Draw(img)
    # The label shrinks to its content and never exceeds 760 px outside.
    pad_l, pad_r, pad_t, pad_b, border = 44, 44, 40, 36, 2
    inner_max = 760 - pad_l - pad_r - 2 * border
    fk, ft, fu = font("regular", 24), font("bold", 48), font("regular", 26)
    kick_text = SECTION_NAME["flaneur"] + "".join(f" · {clean(p)}" for p in entry.get("meta", []) if clean(p))
    foot_w = 132 + 40 + width(fu, "ttvl.co")  # wordmark at 52 px tall is about 132 wide
    natural = max(width(fk, kick_text), width(ft, clean(entry["title"])), foot_w)
    inner = min(inner_max, natural)
    lines = clamp(wrap(entry["title"], ft, inner), 3, ft, inner)
    inner = max(min(inner, natural), max(width(ft, l) for l in lines), width(fk, kick_text), foot_w)
    inner = min(inner_max, inner)
    box_w = inner + pad_l + pad_r + 2 * border
    box_h = pad_t + 32 + 12 + len(lines) * 56 + 28 + 52 + pad_b + 2 * border
    x0, y0 = MARGIN, H - MARGIN - box_h
    draw.rectangle([x0, y0, x0 + box_w - 1, y0 + box_h - 1], fill=WHITE, outline=EDGE, width=border)
    x, y = x0 + border + pad_l, y0 + border + pad_t
    kicker(draw, x, y, SECTION_NAME["flaneur"], entry.get("meta", []), size=24, line_h=32)
    y += 32 + 12
    for line in lines:
        text_at(draw, x, y, line, ft, INK, 56)
        y += 56
    y += 28
    paste_height(img, asset(WORDMARK), x, y, 52)
    text_at(draw, x + inner, y + 52 - 34, "ttvl.co", fu, MUTED, 34, anchor="r")
    return img


RENDERERS = {
    "note": render_note,
    "project": render_project,
    "flaneur": render_flaneur,
    "flaneur-plain": render_flaneur_plain,
    "hub": render_hub,
    "site": render_site,
}
PALETTE_STYLES = {"note", "hub", "site", "flaneur-plain"}  # flat cards quantize cleanly


JPEG_STYLES = {"flaneur", "project"}  # photographic cards; PNG would be 3x the size


def extension(entry):
    return "jpg" if entry["style"] in JPEG_STYLES else "png"


def save(img, entry, path):
    if entry["style"] == "flaneur":
        img.save(path, "JPEG", quality=85, optimize=True, progressive=True)
    elif entry["style"] == "project":
        img.save(path, "JPEG", quality=92, optimize=True, progressive=True)
    elif entry["style"] in PALETTE_STYLES:
        img.convert("P", palette=Image.ADAPTIVE, colors=256).save(path, "PNG", optimize=True)
    else:
        img.save(path, "PNG", optimize=True)


# --- manifest and bookkeeping ------------------------------------------------

def build_manifest(drafts=False):
    """Ask Hugo for the manifest only, through the social render segment."""
    with tempfile.TemporaryDirectory(prefix="social-cards-") as tmp:
        cmd = ["hugo", "--quiet", "--renderSegments", "social", "--destination", tmp]
        if drafts:
            cmd.append("--buildDrafts")
        subprocess.run(cmd, cwd=ROOT, check=True)
        with open(os.path.join(tmp, "social.json"), encoding="utf-8") as fh:
            return json.load(fh)


def input_hash(entry):
    h = hashlib.sha256()
    h.update(DESIGN_VERSION.encode())
    h.update(json.dumps(entry, sort_keys=True, ensure_ascii=False).encode())
    image = entry.get("image")
    if image:
        path = os.path.join(STATIC, image.lstrip("/"))
        if os.path.exists(path):
            with open(path, "rb") as fh:
                h.update(fh.read())
        else:
            h.update(b"missing")
    return h.hexdigest()[:16]


def load_sidecar():
    if os.path.exists(SIDECAR):
        with open(SIDECAR, encoding="utf-8") as fh:
            return json.load(fh)
    return {"version": DESIGN_VERSION, "cards": {}}


def save_sidecar(data):
    data["version"] = DESIGN_VERSION
    data["cards"] = dict(sorted(data["cards"].items()))
    with open(SIDECAR, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def existing_files():
    files = set()
    for base, _, names in os.walk(OUT_DIR):
        for name in names:
            if name != "manifest.json":
                files.add(os.path.relpath(os.path.join(base, name), STATIC))
    return files


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="report missing, stale, and orphaned cards; render nothing")
    ap.add_argument("--stale", action="store_true", help="also re-render cards whose inputs changed")
    ap.add_argument("--all", action="store_true", help="re-render every card")
    ap.add_argument("--only", nargs="+", metavar="PATH", help="limit to these page paths, e.g. /notes/walking/")
    ap.add_argument("--drafts", action="store_true", help="include draft pages when building the manifest")
    ap.add_argument("--manifest", metavar="FILE", help="read this manifest instead of running Hugo")
    args = ap.parse_args()

    if args.manifest:
        with open(args.manifest, encoding="utf-8") as fh:
            entries = json.load(fh)
    else:
        entries = build_manifest(drafts=args.drafts)
    if args.only:
        wanted = {p if p.endswith("/") else p + "/" for p in args.only}
        entries = [e for e in entries if e["path"] in wanted]
        missing_paths = wanted - {e["path"] for e in entries}
        for p in sorted(missing_paths):
            print(f"no manifest entry for {p}", file=sys.stderr)

    sidecar = load_sidecar()
    present = existing_files()
    expected = {f"{e['out']}.{extension(e)}" for e in entries}
    orphans = sorted(present - expected) if not args.only else []

    todo, fresh, stale, missing = [], 0, [], []
    for entry in entries:
        rel = f"{entry['out']}.{extension(entry)}"
        digest = input_hash(entry)
        exists = rel in present
        recorded = sidecar["cards"].get(entry["out"], {}).get("hash")
        if not exists:
            missing.append(entry)
        elif recorded != digest:
            stale.append(entry)
        else:
            fresh += 1
        if args.all or not exists or (args.stale and recorded != digest):
            todo.append((entry, rel, digest))

    if args.check:
        print(f"{fresh} up to date, {len(missing)} missing, {len(stale)} stale, {len(orphans)} orphaned")
        for e in missing:
            print(f"  missing  {e['path']}")
        for e in stale:
            print(f"  stale    {e['path']}")
        for f in orphans:
            print(f"  orphan   static/{f}")
        return 1 if (missing or stale) else 0

    if not todo:
        print(f"nothing to render ({fresh} up to date, {len(stale)} stale; use --stale or --all)")
    total = 0
    for entry, rel, digest in todo:
        path = os.path.join(STATIC, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        img = RENDERERS[entry["style"]](entry)
        save(img, entry, path)
        other = os.path.join(STATIC, f"{entry['out']}.{'png' if rel.endswith('.jpg') else 'jpg'}")
        if os.path.exists(other):  # a dispatch that gained or lost its cover
            os.remove(other)
        size = os.path.getsize(path)
        total += size
        sidecar["cards"][entry["out"]] = {"hash": digest, "file": rel, "style": entry["style"]}
        print(f"rendered {rel}  {size // 1024} KB")
    if todo:
        print(f"{len(todo)} cards, {total // 1024} KB")
    # Drop sidecar rows for cards that no longer have a manifest entry.
    if not args.only:
        outs = {e["out"] for e in entries}
        sidecar["cards"] = {k: v for k, v in sidecar["cards"].items() if k in outs}
    if todo or not args.only:
        os.makedirs(OUT_DIR, exist_ok=True)
        save_sidecar(sidecar)
    for f in orphans:
        print(f"orphan (no page for it any more): static/{f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
