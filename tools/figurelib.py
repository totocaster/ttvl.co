"""The drawing palette, the type, and the helpers every figure tool shares.

docs/figures.md is the standard. tools/figure-specimens.py, tools/chart.py,
and tools/map.py import this module (it sits beside them, so a uv script
finds it). Text is measured with the IBM Plex font files from
~/Library/Fonts (override the folder with FIGURES_FONT_DIR), like
tools/social-cards.py, so a label that would outgrow its room is named
before anyone sees it.
"""
import datetime as dt
import math
import os
from xml.sax.saxutils import escape

from PIL import ImageFont

FONTS = os.environ.get("FIGURES_FONT_DIR", os.path.expanduser("~/Library/Fonts"))

# The drawing palette: literal values the site's stylesheet maps to tokens.
INK, MUTED, FAINT = "#000", "#555555", "#6E6E6E"
TONE2, TONE3, TONE4 = "#4F4F4F", "#7A7A7A", "#A3A3A3"
EDGE, SURFACE, GROUND = "#D9D9D9", "#F7F7F7", "#FFFFFF"
HIGHLIGHT, SIGNAL = "#FFEB3B", "#FF4F00"

_fonts = {}


def font(mono=False, weight=400, size=14):
    name = ("IBMPlexMono" if mono else "IBMPlexSans") + "-" + {400: "Regular", 500: "Medium", 600: "SemiBold"}[weight] + ".otf"
    key = (name, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(os.path.join(FONTS, name), size)
    return _fonts[key]


def width(s, mono=False, weight=400, size=14):
    return font(mono, weight, size).getlength(s)


def text(x, y, s, size=14, fill=FAINT, anchor="start", mono=False, weight=400, extra=""):
    fam = "IBM Plex Mono" if mono else "IBM Plex Sans"
    w = f' font-weight="{weight}"' if weight != 400 else ""
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    return f'<text x="{x:g}" y="{y:g}" font-family="{fam}" font-size="{size}"{w}{a} fill="{fill}"{extra}>{escape(s)}</text>'


def mixed(x, y, parts, size=14, fill=FAINT, anchor="start"):
    """parts: list of (string, mono) — words in Sans, numbers in Mono."""
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    spans = "".join(
        f'<tspan font-family="IBM Plex Mono">{escape(s)}</tspan>' if m else escape(s) for s, m in parts
    )
    return f'<text x="{x:g}" y="{y:g}" font-family="IBM Plex Sans" font-size="{size}"{a} fill="{fill}">{spans}</text>'


def mixed_width(parts, size=14):
    return sum(width(s, m, 400, size) for s, m in parts)


def svg(w, h, body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none">\n'
        + "\n".join(body)
        + "\n</svg>\n"
    )


def check(label, s, room, **kw):
    w = width(s, **kw)
    if w > room:
        print(f"  ! {label}: '{s}' is {w:.0f} px in {room:.0f}")


def arrow_head(x, y, direction):
    s = 6
    if direction == "right":
        return f'<path d="M{x} {y}l-{s} -{s / 2}v{s}z" fill="{INK}"/>'
    if direction == "left":
        return f'<path d="M{x} {y}l{s} -{s / 2}v{s}z" fill="{INK}"/>'
    if direction == "up":
        return f'<path d="M{x} {y}l-{s / 2} {s}h{s}z" fill="{INK}"/>'
    return f'<path d="M{x} {y}l-{s / 2} -{s}h{s}z" fill="{INK}"/>'


def box(x, y, w, h, name, lines, stroke=INK, sw=1, fill=GROUND, dashed=False):
    off = 0.5 if sw == 1 else 1
    dash = ' stroke-dasharray="4 4"' if dashed else ""
    out = [f'<rect x="{x + off}" y="{y + off}" width="{w - 2 * off}" height="{h - 2 * off}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{dash}/>']
    out.append(text(x + 12, y + 26, name, size=16, weight=500, fill=INK))
    check("box name", name, w - 24, size=16, weight=500)
    for k, line in enumerate(lines):
        if not line:
            continue
        out.append(text(x + 12, y + 48 + 20 * k, line, fill=MUTED))
        check("box line", line, w - 24)
    return out


def dot(x, y, fill=INK, r=4):
    """A data point: an 8 px dot on a 2 px ground ring."""
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{GROUND}" stroke-width="2"/>'


def swatch_key(x, y, items):
    """A key line: square swatches (or open ones) with their words."""
    out = []
    for label, fill in items:
        if fill == "open":
            out.append(f'<rect x="{x + 0.5}" y="{y - 9.5}" width="9" height="9" stroke="{TONE4}"/>')
        elif fill == "dot":
            out.append(f'<circle cx="{x + 5}" cy="{y - 5}" r="4" fill="{TONE3}"/>')
        else:
            out.append(f'<rect x="{x}" y="{y - 10}" width="10" height="10" fill="{fill}"/>')
        parts = label if isinstance(label, list) else [(label, False)]
        out.append(mixed(x + 16, y, parts, fill=MUTED))
        x += 16 + mixed_width(parts) + 20
    return out


def year_axis(X, base, years, w, labeled=None):
    out = [f'<path d="M{X(dt.date(years[0], 1, 1)):.1f} {base + 0.5}H{w}" stroke="{INK}"/>']
    for year in years:
        x = round(X(dt.date(year, 1, 1))) + 0.5
        out.append(f'<path d="M{x} {base}V{base + 6}" stroke="{INK}"/>')
        if labeled is None or year in labeled:
            out.append(text(x - 0.5, base + 24, str(year), mono=True))
    return out


def arrow_dir(x, y, dx, dy, fill=INK, s=6):
    """A filled arrowhead with its point at (x, y), heading along (dx, dy)."""
    n = math.hypot(dx, dy) or 1
    ux, uy = dx / n, dy / n
    bx, by = x - ux * s, y - uy * s
    px, py = -uy * s / 2, ux * s / 2
    return f'<path d="M{x:.1f} {y:.1f}L{bx + px:.1f} {by + py:.1f}L{bx - px:.1f} {by - py:.1f}z" fill="{fill}"/>'


def save(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", os.path.relpath(path))
