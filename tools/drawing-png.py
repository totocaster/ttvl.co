# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Render a drawing's PNG: the stand-in for feeds, email, and social cards.

A drawing on the page is its SVG, inlined so it follows the theme
(docs/figures.md). Feed readers and email clients get an image instead,
and they may not have IBM Plex, so a drawing headed for the RSS feed or a
Flâneur dispatch gets a PNG beside it under the same name
(plan.svg -> plan.png). The drawing shortcode and the feed pick it up
from there.

    uv run tools/drawing-png.py static/visuals/research/ambient-computing/2026-10-19-place-names.svg
    uv run tools/drawing-png.py --scale 1 --pad 24 static/visuals/figures/*.svg
    uv run tools/drawing-png.py --width 600 static/visuals/notes/2026-11-02-chart.svg

The PNG is the light drawing on white, set in the site's own Plex subsets,
at twice the drawing's size by default, with 32 px of white around it.
--width sets the size the drawing is shown at instead, such as 600 for
the Flâneur email's column; the PNG is then that wide at the scale.
Rendering uses a Chromium-family headless browser: Playwright's cached
headless shell, Google Chrome, or the path in CHROME.
"""

import argparse
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "static" / "fonts" / "plex"
FACES = [
    ("IBM Plex Sans", 400, "normal", "IBMPlexSans-Regular"),
    ("IBM Plex Sans", 400, "italic", "IBMPlexSans-Italic"),
    ("IBM Plex Sans", 500, "normal", "IBMPlexSans-Medium"),
    ("IBM Plex Sans", 600, "normal", "IBMPlexSans-SemiBold"),
    ("IBM Plex Mono", 400, "normal", "IBMPlexMono-Regular"),
    ("IBM Plex Mono", 500, "normal", "IBMPlexMono-Medium"),
]


def browser():
    candidates = [os.environ.get("CHROME", "")]
    candidates += sorted(
        glob.glob(os.path.expanduser("~/Library/Caches/ms-playwright/chromium_headless_shell-*/*/chrome-headless-shell")),
        reverse=True,
    )
    candidates += [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        shutil.which("chromium") or "",
        shutil.which("google-chrome") or "",
    ]
    for path in candidates:
        if path and os.path.exists(path):
            return path
    sys.exit("No headless Chromium found. Install Playwright's browsers or set CHROME.")


def size(svg):
    box = re.search(r'viewBox="[-\d.]+[\s,]+[-\d.]+[\s,]+([\d.]+)[\s,]+([\d.]+)"', svg)
    if box:
        return float(box.group(1)), float(box.group(2))
    w, h = re.search(r'width="([\d.]+)', svg), re.search(r'height="([\d.]+)', svg)
    if w and h:
        return float(w.group(1)), float(h.group(1))
    sys.exit("The SVG needs a viewBox or a width and height.")


def render(path, chrome, scale, pad, shown=None):
    source = Path(path)
    svg = source.read_text(encoding="utf-8")
    w, h = size(svg)
    if shown:
        w, h = shown, h * shown / w
    faces = "\n".join(
        f'@font-face {{ font-family: "{family}"; font-weight: {weight}; font-style: {style}; '
        f'src: url("{(FONTS / (name + ".woff2")).as_uri()}") format("woff2"); }}'
        for family, weight, style, name in FACES
    )
    # The page CSS the drawing would get on the site: words in Sans,
    # numbers in Mono, strokes at their drawn width.
    page = f"""<!doctype html><meta charset="utf-8"><style>
{faces}
html, body {{ margin: 0; background: #fff; }}
body {{ padding: {pad}px; }}
svg {{ display: block; width: {w:g}px; height: {h:g}px; overflow: visible; }}
svg * {{ vector-effect: non-scaling-stroke; }}
svg text {{ font-family: "IBM Plex Sans", sans-serif; }}
svg [font-family*="Mono"] {{ font-family: "IBM Plex Mono", monospace; font-variant-numeric: tabular-nums; }}
</style>{svg}"""
    out = source.with_suffix(".png")
    with tempfile.TemporaryDirectory() as tmp:
        html = Path(tmp) / "drawing.html"
        html.write_text(page, encoding="utf-8")
        width, height = round(w + 2 * pad), round(h + 2 * pad)
        subprocess.run(
            [
                chrome,
                "--headless",
                "--disable-gpu",
                "--hide-scrollbars",
                "--allow-file-access-from-files",
                f"--force-device-scale-factor={scale}",
                f"--window-size={width},{height}",
                "--virtual-time-budget=2000",
                f"--screenshot={out}",
                html.as_uri(),
            ],
            check=True,
            capture_output=True,
        )
    print(f"{out.relative_to(ROOT) if out.is_relative_to(ROOT) else out}  {width * scale} × {height * scale}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("svg", nargs="+", help="SVG drawings to render")
    parser.add_argument("--scale", type=int, default=2, help="device scale (default 2)")
    parser.add_argument("--pad", type=int, default=32, help="white margin in px (default 32)")
    parser.add_argument("--width", type=int, help="show the drawing this many px wide (default: its own width)")
    args = parser.parse_args()
    chrome = browser()
    for path in args.svg:
        render(path, chrome, args.scale, args.pad, args.width)


if __name__ == "__main__":
    main()
