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
committed file. IBM Plex Sans and Mono are read from the owner's OTF files in
~/Library/Fonts (override the folder with SOCIAL_CARDS_FONT_DIR), which the
build box does not have, so cards are rendered on a Mac.

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

Card styles, all in the Panel language (docs/styleguide.md):
  note, article, hub, site   Panel: a 280 px rail (date in Mono, section and
                             kind, the signal square and ttvl.co) beside a
                             column with the title, the dek, and the signature;
                             a hairline 48 px above the bottom edge
  project                    Panel split: rail stacked over the title on the
                             left 55%, the poster in a framed surface well on
                             the right 45% (JPEG)
  flaneur                    Plate: cover photo with a white label bottom left (JPEG). Dormant:
  flaneur-plain              Ledger with the engraving. Dispatch pages are email sources and
                             carry no metadata, so the manifest emits no entries for them.

The manifest sidecar static/social/manifest.json records a hash of each card's
inputs so --check and --stale can tell when a title, date, or poster changed.
"""

import argparse
import hashlib
import json
import os
import re
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
DESIGN_VERSION = "2"

FONT_DIR = os.path.expanduser(os.environ.get("SOCIAL_CARDS_FONT_DIR", "~/Library/Fonts"))
FONT_FILES = {
    "regular": "IBMPlexSans-Regular.otf",
    "medium": "IBMPlexSans-Medium.otf",
    "semibold": "IBMPlexSans-SemiBold.otf",
    "mono": "IBMPlexMono-Regular.otf",
}

WORDMARK = os.path.join(STATIC, "ui", "ttvl_logo@3x.png")
ENGRAVING = os.path.join(STATIC, "ui", "flaneur_logo@3x.png")

W, H = 1200, 630

# The Panel grid.
PAD_X, PAD_Y = 72, 64           # card padding: sides, top and bottom
RAIL_W, GUTTER = 280, 64        # rail width and the gap to the column
RAIL_DROP = 14                  # the rail's first line sits on the title's x-height
COL_X = PAD_X + RAIL_W + GUTTER  # 416
COL_W = W - PAD_X - COL_X        # 712
DEK_W = 700
RULE_Y = H - 48 - 1              # the hairline, 48 px above the bottom edge
SIGN_H = 44                      # the signature wordmark
SPLIT = round(W * 0.55)          # project cards: text left of this, poster right

# The legacy grid the dormant Flâneur renderers still use.
MARGIN = 96

# Fixed light palette: the card is an image, so the site's tokens are baked in.
WHITE = (255, 255, 255)
INK = (0, 0, 0)              # --ink
MUTED = (0x55, 0x55, 0x55)   # --ink-muted
FAINT = (0x6E, 0x6E, 0x6E)   # --ink-faint
RULE = (0xEC, 0xEC, 0xEC)    # --rule
EDGE = (0xD9, 0xD9, 0xD9)    # --edge
SURFACE = (0xF7, 0xF7, 0xF7)  # --surface
SIGNAL = (0xFF, 0x4F, 0x00)  # --signal: the 10 px square only, never text

SECTION_NAME = {
    "note": "Notes",
    "project": "Project",
    "flaneur": "The Flâneur",
    "flaneur-plain": "The Flâneur",
    "hub": "ttvl.co",
    "site": "ttvl.co",
}

# Characters that should not break lines or that the cards normalize.
GLYPH_FIXES = {
    "‑": "-",   # non-breaking hyphen
    "‐": "-",   # hyphen
    " ": " ",   # no-break space
    " ": " ",   # thin space
    " ": " ",   # narrow no-break space
}

NUMERIC = re.compile(r"^[\d\-–./:]+$")  # dates, years, counts: set in Mono


# --- text -------------------------------------------------------------------

_fonts = {}


def font(weight, size):
    """Plex at a weight: regular, medium, or semibold Sans, or mono."""
    weight = {"bold": "semibold"}.get(weight, weight)
    key = (weight, size)
    if key not in _fonts:
        path = os.path.join(FONT_DIR, FONT_FILES[weight])
        if not os.path.exists(path):
            sys.exit(f"Font not found: {path} (set SOCIAL_CARDS_FONT_DIR to the folder holding the IBM Plex OTF files)")
        _fonts[key] = ImageFont.truetype(path, size)
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
    kept[-1] = last.rstrip(" ,;:·—–-") + "…"
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
    return (x + (w - scaled.width) // 2, y + (h - scaled.height) // 2, scaled.width, scaled.height)


def paste_cover(img, path, box):
    x, y, w, h = box
    with Image.open(path) as src:
        src = ImageOps.exif_transpose(src).convert("RGB")
        fitted = ImageOps.fit(src, (w, h), Image.LANCZOS, centering=(0.5, 0.5))
    img.paste(fitted, (x, y))


def poster(path):
    """A poster as RGBA, upright, so transparent PNGs sit on the well."""
    with Image.open(path) as src:
        return ImageOps.exif_transpose(src).convert("RGBA")


def wordmark_and_url(img, draw):
    """The old Ledger foot, kept for the dormant Flâneur plain card."""
    bottom = H - MARGIN
    paste_height(img, asset(WORDMARK), MARGIN, bottom - 72, 72)
    text_at(draw, W - MARGIN, bottom - 34, "ttvl.co", font("regular", 26), MUTED, 34, anchor="r")


def rule(draw, y, x0=MARGIN, x1=W - MARGIN, fill=RULE, thickness=2):
    draw.rectangle([x0, y, x1 - 1, y + thickness - 1], fill=fill)


# --- the Panel ----------------------------------------------------------------

RAIL_SIZE, RAIL_LINE = 22, 32


def rail_lines(entry):
    """The rail's two lines: the ordering key (date or year) and section · kind."""
    style, meta = entry["style"], [clean(m) for m in entry.get("meta") or []]
    if style == "note":    # meta: category, date
        return (meta[1] if len(meta) > 1 else ""), " · ".join(p for p in ("Notes", meta[0] if meta else "") if p)
    if style == "project":  # meta: hub label, year
        hub, year = (meta + ["", ""])[:2]
        return year, " · ".join(p for p in (hub, "Project") if p)
    if style == "hub":
        return "", "ttvl.co · Hub"
    if style == "site":
        return "", ""     # the signal line below already says ttvl.co
    # article and research stream: section, then a date or a kind
    section = clean(entry.get("section"))
    dates = [m for m in meta if NUMERIC.match(m)]
    kinds = [m for m in meta if m and not NUMERIC.match(m)]
    return (dates[0] if dates else ""), " · ".join([section] + kinds if section else kinds)


def draw_rail(img, draw, entry, x, y, w=RAIL_W):
    """Rail: key in Mono, section and kind in Sans, then the signal and ttvl.co.
    Lines that are empty collapse. Returns the y under the last line."""
    first, second = rail_lines(entry)
    fs, fm = font("regular", RAIL_SIZE), font("mono", RAIL_SIZE)
    if first:
        text_at(draw, x, y, first, fm if NUMERIC.match(first) else fs, FAINT, RAIL_LINE)
        y += RAIL_LINE
    if second:
        for line in clamp(wrap(second, fs, w), 2, fs, w):
            text_at(draw, x, y, line, fs, FAINT, RAIL_LINE)
            y += RAIL_LINE
    if first or second:
        y += 24
    sq = 10
    top = y + (RAIL_LINE - sq) // 2
    draw.rectangle([x, top, x + sq - 1, top + sq - 1], fill=SIGNAL)
    text_at(draw, x + sq + 12, y, "ttvl.co", fs, FAINT, RAIL_LINE)
    return y + RAIL_LINE


def title_lines(title, max_w):
    """Sans Medium 56/64 in at most 3 lines; 48/56 in up to 4 when it needs more."""
    f = font("medium", 56)
    lines = wrap(title, f, max_w)
    if len(lines) <= 3:
        return lines, f, 64
    f = font("medium", 48)
    return clamp(wrap(title, f, max_w), 4, f, max_w), f, 56


def draw_title(draw, entry, x, y, max_w):
    lines, f, lh = title_lines(entry["title"], max_w)
    for line in lines:
        text_at(draw, x, y, line, f, INK, lh)
        y += lh
    return y


def draw_signature(img, x):
    """The signature wordmark, 44 px tall, on the bottom padding line."""
    paste_height(img, asset(WORDMARK), x, H - PAD_Y - SIGN_H, SIGN_H)


def draw_hairline(draw):
    rule(draw, RULE_Y, PAD_X, W - PAD_X, fill=RULE, thickness=1)


def render_text(entry):
    """Note, article, research stream, hub, and site: rail beside the column."""
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)
    draw_rail(img, draw, entry, PAD_X, PAD_Y + RAIL_DROP)
    y = draw_title(draw, entry, COL_X, PAD_Y, COL_W)
    dek = clean(entry.get("dek"))
    if dek:
        y += 24
        fd = font("regular", 28)
        room = min(3, (H - PAD_Y - SIGN_H - 32 - y) // 40)
        for line in clamp(wrap(dek, fd, DEK_W), room, fd, DEK_W):
            text_at(draw, COL_X, y, line, fd, MUTED, 40)
            y += 40
    draw_signature(img, COL_X)
    draw_hairline(draw)
    return img


def render_project(entry):
    """Rail stacked over the title on the left 55%, the poster on the right 45%."""
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)
    # The poster well: a surface mat 24 px wide in a 1 px edge frame with a
    # 2 px radius, sized to the poster inside the area right of the split
    # (72 px from the right edge, on the top and bottom padding lines) and
    # centered in it vertically.
    ax0, ax1, ay0, ay1 = SPLIT, W - PAD_X, PAD_Y, H - PAD_Y
    mat = 24
    image = entry.get("image")
    src = poster(os.path.join(STATIC, image.lstrip("/"))) if image else None
    inner_w, inner_h = ax1 - ax0 - 2 * mat - 2, ay1 - ay0 - 2 * mat - 2
    if src:
        fitted = ImageOps.contain(src, (inner_w, inner_h), Image.LANCZOS)
    else:
        fitted = None
    pw, ph = (fitted.size if fitted else (inner_w, round(inner_w * 9 / 16)))
    ww, wh = pw + 2 * mat + 2, ph + 2 * mat + 2
    wx0 = ax1 - ww
    wy0 = ay0 + (ay1 - ay0 - wh) // 2
    draw.rounded_rectangle([wx0, wy0, wx0 + ww - 1, wy0 + wh - 1], radius=2, fill=SURFACE, outline=EDGE, width=1)
    if fitted:
        img.paste(fitted, (wx0 + 1 + mat, wy0 + 1 + mat), fitted)
    text_w = SPLIT - GUTTER - PAD_X
    y = draw_rail(img, draw, entry, PAD_X, PAD_Y, w=text_w)
    draw_title(draw, entry, PAD_X, y + 40, text_w)
    draw_signature(img, PAD_X)
    draw_hairline(draw)
    return img


# --- the dormant Flâneur cards -----------------------------------------------

def ledger_head(draw, entry):
    """Kicker on the first row and the hairline under it; returns the body's top y."""
    section = entry.get("section") or SECTION_NAME[entry["style"]]
    kicker(draw, MARGIN, MARGIN, section, entry.get("meta", []))
    rule(draw, MARGIN + 34 + 18)
    return MARGIN + 34 + 18 + 2 + 44


def render_flaneur_plain(entry):
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)
    y = ledger_head(draw, entry)
    body_w = 640
    f = font("medium", 56)
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


def render_flaneur(entry):
    img = Image.new("RGB", (W, H), WHITE)
    cover = entry.get("image")
    if cover:
        paste_cover(img, os.path.join(STATIC, cover.lstrip("/")), (0, 0, W, H))
    draw = ImageDraw.Draw(img)
    # The label shrinks to its content and never exceeds 760 px outside.
    pad_l, pad_r, pad_t, pad_b, border = 44, 44, 40, 36, 2
    inner_max = 760 - pad_l - pad_r - 2 * border
    fk, ft, fu = font("regular", 24), font("medium", 48), font("regular", 26)
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
    "note": render_text,
    "project": render_project,
    "flaneur": render_flaneur,
    "flaneur-plain": render_flaneur_plain,
    "hub": render_text,
    "article": render_text,
    "site": render_text,
}
PALETTE_STYLES = {"note", "hub", "article", "site", "flaneur-plain"}  # flat cards quantize cleanly


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
