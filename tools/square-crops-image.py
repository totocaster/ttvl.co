#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow>=11"]
# ///
"""Render the square-crops shortcode's RSS/print fallback.

Run `uv run tools/square-crops-image.py` after changing data/square-crops.json.
The interactive diagram and this renderer share the point and screen ratios.
The committed PNG requires no scripts, SVG support, or site styles in readers.
"""

import json
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "static/visuals/notes/square-sensors-crops.png"
DATA = json.loads((ROOT / "data/square-crops.json").read_text())

# A fixed light palette is baked into the image for feed/print portability.
GROUND, INK, FAINT = "#ffffff", "#000000", "#707070"
SURFACE, EDGE, HIGHLIGHT = "#fafafa", "#dddddd", "#ffef62"
WIDTH, HEIGHT, SCALE = 1120, 640, 2
image = Image.new("RGB", (WIDTH * SCALE, HEIGHT * SCALE), GROUND)
draw = ImageDraw.Draw(image)
font = ImageFont.truetype(
    os.environ.get("SOCIAL_CARDS_FONT", "/System/Library/Fonts/HelveticaNeue.ttc"),
    56 * SCALE,
    index=0,
)


def line(points, color, width=2):
    draw.line([(round(x * SCALE), round(y * SCALE)) for x, y in points],
              fill=color, width=width * SCALE)


def rectangle(box, **kwargs):
    draw.rectangle([round(n * SCALE) for n in box], **kwargs)


def crop_bounds(crop):
    width = min(100, 100 * crop["width"] / crop["height"])
    height = min(100, 100 * crop["height"] / crop["width"])
    x = max(0, min(100 - width, DATA["point"]["x"] - width / 2))
    y = max(0, min(100 - height, DATA["point"]["y"] - height / 2))
    return x, y, width, height


for column, key in enumerate(("portrait", "widescreen")):
    crop = next(c for c in DATA["crops"] if c["key"] == key)
    left, top, size = 48 + column * 544, 112, 480
    draw.text((left * SCALE, 24 * SCALE), crop["ratio"], font=font, fill=INK)
    rectangle((left, top, left + size, top + size), fill=SURFACE)

    for fraction in (0.25, 0.5, 0.75):
        offset = size * fraction
        line(((left + offset, top), (left + offset, top + size)), EDGE)
        line(((left, top + offset), (left + size, top + offset)), EDGE)

    # Dashed perimeter denotes the uncut square recording.
    for offset in range(0, size, 16):
        end = min(offset + 8, size)
        for edge in (0, size):
            line(((left + offset, top + edge), (left + end, top + edge)), FAINT)
            line(((left + edge, top + offset), (left + edge, top + end)), FAINT)

    x, y, width, height = crop_bounds(crop)
    rectangle((left + size * x / 100, top + size * y / 100,
               left + size * (x + width) / 100, top + size * (y + height) / 100),
              fill=HIGHLIGHT, outline=INK, width=4 * SCALE)

    px = left + size * DATA["point"]["x"] / 100
    py = top + size * DATA["point"]["y"] / 100
    radius = 10
    draw.ellipse([round(n * SCALE) for n in
                  (px - radius, py - radius, px + radius, py + radius)],
                 fill=INK, outline=GROUND, width=3 * SCALE)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
image.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS).save(OUTPUT, optimize=True)
print(f"Rendered {OUTPUT.relative_to(ROOT)} ({OUTPUT.stat().st_size // 1024} KB)")
