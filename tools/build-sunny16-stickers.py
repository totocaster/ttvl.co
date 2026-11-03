# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Draw the Sunny 16 stickers, their A4 sheet, and the page's figures.

    uv run tools/build-sunny16-stickers.py

Writes the six sticker SVGs (ISO 100 to 1600) and the placement drawings,
with their PNGs, to static/visuals/darkroom/sunny-16/, and the A4 PDF and
the ZIP of SVGs to static/downloads/sunny-16/.

The sticker keeps the 229:76 ratio of the 2023 Sketch artboards; at 80 mm
wide it matches their cut frame. The plate comes from Leica's dimension
drawing of the M6 (technical data, October 2022): the film M bodies other
than the M5 share its bottom plate.
"""

import base64
import html
import importlib.util
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parent.parent
sys.dont_write_bytecode = True
VISUALS = ROOT / "static/visuals/darkroom/sunny-16"
DOWNLOADS = ROOT / "static/downloads/sunny-16"
FONTS = ROOT / "static/fonts/plex"
PREFIX = "2023-06-29"
REVISED = "2026-11-03"

ISOS = (100, 200, 400, 800, 1000, 1600)
APERTURES = ("16", "11", "8", "5.6", "4", "2.8", "2")
ROWS = ("Sun on snow / sand", "Sun · distinct shadows", "Haze · soft shadows",
        "Cloud · no shadows", "Overcast / open shade", "Deep shade")
SPEEDS = (1, 2, 4, 8, 15, 30, 60, 125, 250, 500, 1000)
COLUMNS = [296 + c * 69 for c in range(7)]

WIDTH = 80                      # sticker, mm
HEIGHT = WIDTH * 76 / 229       # 26.55 mm
# The bottom plate seen from below, lens side up, in mm from the
# advance-side end, measured off Leica's M6 drawing.
PLATE = (138.6, 32.3)           # outline: length, depth
FACE = 1.1                      # the flat face's edge, inside the outline
SOCKET = (15.2, 5.5)            # tripod socket: centre, insert radius
LOCK = (122.5, 11.3, 6.7)       # locking key: centre, recess radius, key radius
LENS = 79.2                     # lens axis
# Centred in the clear run between the socket and the lock.
STICKER_X = (SOCKET[0] + SOCKET[1] + LOCK[0] - LOCK[1] - WIDTH) / 2
CLEAR_END = STICKER_X - SOCKET[0] - SOCKET[1]           # 5.3 mm
CLEAR_EDGE = (PLATE[1] - 2 * FACE - HEIGHT) / 2          # 1.8 mm


def values(iso):
    # Standard marked full-stop sequence. At ISO 100, sun = f/16, 1/125 s.
    # ISO 1000 rounds to the same full-stop settings as ISO 800 (1/3 stop).
    sun = 7 + round(math.log2(iso / 100))
    # Past 1/1000 s, the filter to add: ND2 is one stop, ND4 two, and so on.
    return [[str(SPEEDS[q]) if q <= 10 else f"ND{2 ** (q - 10)}"
             for c in range(7) for q in [sun + c + 1 - r]] for r in range(6)]


def n(value):
    return f"{round(value, 2):g}"


def text(x, y, value, size=16, mono=False, anchor="start", color="#000000", weight=400):
    family = "IBM Plex Mono" if mono else "IBM Plex Sans"
    bold = f' font-weight="{weight}"' if weight != 400 else ""
    return (f'<text x="{n(x)}" y="{n(y)}" font-family="{family}" font-size="{size}"{bold} '
            f'text-anchor="{anchor}" fill="{color}">{html.escape(str(value))}</text>')


def line(x1, y1, x2, y2, color="#6E6E6E", width=1):
    stroke = f' stroke-width="{width}"' if width != 1 else ""
    return f'<path d="M{n(x1)} {n(y1)}L{n(x2)} {n(y2)}" stroke="{color}"{stroke}/>'


def circle(cx, cy, r, fill="#FFFFFF", stroke="#000000"):
    return f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="{fill}" stroke="{stroke}"/>'


def fonts(*faces):
    rules = []
    for family, weight, name in faces:
        data = base64.b64encode((FONTS / f"{name}.woff2").read_bytes()).decode()
        rules.append(f'@font-face{{font-family:"{family}";font-weight:{weight};'
                     f'src:url(data:font/woff2;base64,{data}) format("woff2")}}')
    return "".join(rules)


LABEL_FACES = (("IBM Plex Sans", 400, "IBMPlexSans-Regular"),
               ("IBM Plex Mono", 400, "IBMPlexMono-Regular"),
               ("IBM Plex Mono", 500, "IBMPlexMono-Medium"))


def label(iso, embed=False):
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}mm" height="{HEIGHT:.4f}mm" '
             f'viewBox="0 0 760 252.227" fill="none">',
             f'<title>Sunny 16 exposure sticker, ISO {iso}</title>']
    if embed:
        parts.append(f'<style>{fonts(*LABEL_FACES)}</style>')
    parts += ['<rect x="1" y="1" width="758" height="250.227" fill="#FFFFFF" stroke="#000000" stroke-width="2"/>',
              text(12, 29, f"ISO {iso}", 24, mono=True, weight=500),
              text(264, 29, "f/", 18, anchor="end")]
    for x, aperture in zip(COLUMNS, APERTURES):
        parts.append(text(x, 29, aperture, 28, mono=True, anchor="middle", weight=500))
    parts.append(line(12, 39, 748, 39, "#000000", 1.5))
    # The shutter speeds are what the eye looks for: the largest, heaviest
    # figures. The ND filters beyond 1/1000 s step down to Regular.
    for r, row in enumerate(values(iso)):
        top = 39 + r * 34.5
        parts.append(text(12, top + 26, ROWS[r], 18))
        for x, value in zip(COLUMNS, row):
            nd = value.startswith("ND")
            parts.append(text(x, top + 26, value, 17 if nd else 25, mono=True,
                              anchor="middle", weight=400 if nd else 500))
        if r < 5:
            parts.append(line(12, top + 34.5, 748, top + 34.5, "#7A7A7A"))
    return "\n".join(parts) + "\n</svg>\n"


def placement(narrow=False, physical=False):
    k = 2.3 if narrow else 5                    # drawing units per mm
    w = 335 if narrow else 760
    length, depth = PLATE
    x0 = (w - length * k) / 2
    y0 = 44 if narrow else 56
    cy = y0 + depth * k / 2
    at = lambda mm: x0 + mm * k
    socket, lock = at(SOCKET[0]), at(LOCK[0])
    sx, sw, sh = at(STICKER_X), WIDTH * k, HEIGHT * k
    bottom = y0 + depth * k
    ly = bottom + 30
    canvas_height = ly + (54 if narrow else 42)
    # In print, the drawing is the plate at full size.
    size = (f'width="{n(w / k)}mm" height="{n(canvas_height / k)}mm"' if physical
            else f'width="{w}" height="{n(canvas_height)}"')
    face, inner_depth = FACE * k, (depth - 2 * FACE) * k
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" {size} viewBox="0 0 {w} {n(canvas_height)}" fill="none">',
             line(at(LENS), y0 - 14, at(LENS), y0),
             text(at(LENS), y0 - 20, "Lens", 14, anchor="middle"),
             f'<rect x="{n(x0)}" y="{n(y0)}" width="{n(length * k)}" height="{n(depth * k)}" '
             f'rx="{n(depth * k / 2)}" fill="#F7F7F7" stroke="#000000"/>',
             f'<rect x="{n(x0 + face)}" y="{n(y0 + face)}" width="{n(length * k - 2 * face)}" '
             f'height="{n(inner_depth)}" rx="{n(inner_depth / 2)}" stroke="#A3A3A3"/>',
             circle(socket, cy, SOCKET[1] * k),
             circle(socket, cy, 3.2 * k, "none", "#6E6E6E"),
             circle(lock, cy, LOCK[1] * k),
             circle(lock, cy, LOCK[2] * k),
             line(lock - LOCK[2] * k, cy, lock + LOCK[2] * k, cy, "#000000"),
             f'<rect x="{n(sx + 1)}" y="{n(cy - sh / 2 + 1)}" width="{n(sw - 2)}" height="{n(sh - 2)}" '
             f'fill="#FFEB3B" stroke="#000000" stroke-width="2"/>',
             text(sx + sw / 2, cy - (3 if narrow else 4), "Sticker", 14 if narrow else 16, anchor="middle"),
             text(sx + sw / 2, cy + (15 if narrow else 20), f"{WIDTH} × {HEIGHT:.1f} mm", 14 if narrow else 16,
                  mono=True, anchor="middle"),
             line(socket, cy + SOCKET[1] * k, socket, ly - 18),
             line(lock, cy + LOCK[1] * k, lock, ly - 18)]
    clear = f"About {CLEAR_END:.0f} mm to the socket and the key, {CLEAR_EDGE:.0f} mm to each long edge"
    if narrow:
        parts += [text(x0, ly, "Tripod socket", 14),
                  text(lock, ly, "Locking key", 14, anchor="middle"),
                  text(w / 2, ly + 26, f"About {CLEAR_END:.0f} mm to the socket and the key,", 14,
                       anchor="middle", color="#555555"),
                  text(w / 2, ly + 46, f"{CLEAR_EDGE:.0f} mm to each long edge", 14,
                       anchor="middle", color="#555555")]
    else:
        parts += [text(socket, ly, "Tripod socket", 14, anchor="middle"),
                  text(lock, ly, "Locking key", 14, anchor="middle"),
                  text(w / 2, ly + 28, clear, 14, anchor="middle", color="#555555")]
    return "\n".join(parts) + "\n</svg>\n"


ND = range(1, 9)
README = f"""Sunny 16 stickers for Leica M
Toto Tvalavadze, https://ttvl.co/darkroom/sunny-16-sticker/
Revised {REVISED}

Six exposure stickers, ISO 100 to 1600, as SVG at {WIDTH} x {HEIGHT:.1f} mm.
They fit the bottom plate of every film Leica M except the M5, whose
rewind crank folds into the plate.

Reading
Find the row for the light and the column for your aperture. The number
is the shutter speed: 1000 is 1/1000 s, 8 is 1/8 s. Past 1/1000 s, it
names the neutral density filter to use at 1/1000 s: ND2 is one stop
(0.3), ND4 two (0.6), ND8 three (0.9), ND16 four (1.2).
The steps follow Kodak's daylight table for Tri-X 400: front-lit
subjects, two hours after sunrise to two hours before sunset. Open up a
stop for backlit close-ups. Deep shade is an estimate. Use your film's
exposure index and compensate separately for color filters. ISO 800 and
1000 share the nearest full-stop settings.

Printing
Print at 100% and try one on plain paper first. Use removable matte
sticker paper and cut on the black border. Place the sticker between the
tripod socket and the locking key, about {CLEAR_END:.0f} mm from each and {CLEAR_EDGE:.0f} mm inside
each long edge.

Editing
Browsers show the fonts embedded in each file. Illustrator and Inkscape
need IBM Plex Sans and Mono installed: https://github.com/IBM/plex
The fonts are under the SIL Open Font License, in OFL-fonts.txt.
"""


def sheet():
    stickers = "".join(f'<div class="label">{label(iso)}</div>' * 2 for iso in ISOS)
    filters = "".join(f"<td>ND{2 ** s}</td>" for s in ND)
    stops = "".join(f"<td>{s}</td>" for s in ND)
    densities = "".join(f"<td>{0.3 * s:.1f}</td>" for s in ND)
    faces = fonts(*LABEL_FACES, ("IBM Plex Sans", 600, "IBMPlexSans-SemiBold"))
    return f'''<!doctype html><html lang="en"><meta charset="utf-8"><title>Sunny 16 Stickers for Leica M</title>
<style>{faces}
@page {{ size: A4; margin: 14mm; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; color: #000; font: 10pt/1.4 "IBM Plex Sans"; }}
h1 {{ font-size: 18pt; font-weight: 400; margin: 0 0 2mm; }}
h2 {{ font-size: 11pt; font-weight: 600; margin: 7mm 0 2mm; }}
h2:first-child {{ margin-top: 0; }}
p {{ margin: 0 0 2mm; max-width: 160mm; }}
b {{ font-weight: 600; }}
.meta {{ font-size: 8pt; color: #555; }}
.page {{ break-after: page; }}
.page:last-child {{ break-after: auto; }}
.labels {{ display: grid; grid-template-columns: repeat(2, {WIDTH}mm); justify-content: space-between;
  row-gap: 7mm; margin: 7mm 0; }}
.label svg, .fit svg {{ display: block; }}
.fit {{ display: flex; justify-content: center; margin: 5mm 0 3mm; }}
.check {{ display: flex; align-items: center; gap: 3mm; }}
.check span {{ width: 50mm; border-top: .25mm solid #000; }}
table {{ border-collapse: collapse; margin: 1mm 0 3mm; font-family: "IBM Plex Mono"; font-size: 9pt; }}
th {{ font: 9pt "IBM Plex Sans"; text-align: left; padding-right: 4mm; }}
td {{ padding: .8mm 3mm .8mm 0; min-width: 13mm; }}
tr + tr {{ border-top: .2mm solid #7a7a7a; }}
</style>
<section class="page">
<h1>Sunny 16 Stickers for Leica M</h1>
<p><b>Print at 100%.</b> Try one on plain paper first, then print on removable matte sticker paper and cut on the black border.</p>
<p class="meta">Toto Tvalavadze · ttvl.co/darkroom/sunny-16-sticker · 2023, revised {REVISED}</p>
<div class="labels">{stickers}</div>
<p class="check meta"><span></span>This line measures 50 mm at 100%.</p>
</section>
<section class="page">
<h2>Placement</h2>
<p>The sticker sits between the tripod socket and the locking key. It fits every film Leica M except the M5, whose rewind crank folds into the bottom plate.</p>
<div class="fit">{placement(physical=True)}</div>
<p class="meta">Bottom view at full size, lens side up, from Leica’s dimension drawing of the M6. Hold the printout against the camera to check.</p>
<h2>Reading the Sticker</h2>
<p>Find the row for the light and the column for your aperture. The number is the shutter speed: 1000 is 1/1000 s, 8 is 1/8 s. Past 1/1000 s, it names the neutral density filter to use at 1/1000 s.</p>
<table><tr><th>Filter</th>{filters}</tr><tr><th>Stops</th>{stops}</tr><tr><th>Density</th>{densities}</tr></table>
<p>The steps follow Kodak’s daylight table for Tri-X 400, which assumes front-lit subjects from two hours after sunrise to two hours before sunset. Open up a stop for backlit close-ups. Deep shade is an estimate.</p>
<p>Use your film’s exposure index and compensate separately for color filters. ISO 800 and 1000 share the nearest full-stop settings; the difference is about one-third of a stop.</p>
</section>
</html>'''


def main():
    VISUALS.mkdir(parents=True, exist_ok=True)
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    for iso in ISOS:
        (VISUALS / f"{PREFIX}-iso-{iso}.svg").write_text(label(iso))
    (VISUALS / f"{PREFIX}-placement.svg").write_text(placement())
    (VISUALS / f"{PREFIX}-placement-narrow.svg").write_text(placement(narrow=True))
    with zipfile.ZipFile(DOWNLOADS / "sunny-16-svg-labels.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for iso in ISOS:
            z.writestr(f"sunny-16-iso-{iso}.svg", label(iso, embed=True))
        z.write(DOWNLOADS / "OFL-fonts.txt", "OFL-fonts.txt")
        z.writestr("READ-ME.txt", README)
    spec = importlib.util.spec_from_file_location("drawing_png", ROOT / "tools/drawing-png.py")
    drawing = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(drawing)
    chrome = drawing.browser()
    # The PNGs stand in for the drawings in feeds, and the ISO 400 one is
    # the project's card image.
    for name in ("iso-400", "placement", "placement-narrow"):
        drawing.render(VISUALS / f"{PREFIX}-{name}.svg", chrome, 2, 32)
    pdf = DOWNLOADS / "sunny-16-stickers-a4.pdf"
    with tempfile.TemporaryDirectory(prefix="sunny16-") as tmp:
        source = Path(tmp) / "sheet.html"
        source.write_text(sheet())
        proc = subprocess.run([chrome, "--headless", "--no-sandbox", "--disable-gpu",
                              f"--user-data-dir={tmp}/chrome", "--no-pdf-header-footer",
                              "--virtual-time-budget=3000", f"--print-to-pdf={pdf}", source.as_uri()],
                              capture_output=True, text=True, timeout=45)
        if proc.returncode or not pdf.is_file():
            raise RuntimeError(proc.stderr)
    print(f"Wrote six stickers, the placement drawings and PNGs, the SVG ZIP, and {pdf.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
