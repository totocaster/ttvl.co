#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow>=11"]
# ///
"""Draw the specimen figures for docs/figures.md, from the site's own data.

    uv run tools/figure-specimens.py

Writes SVG files to static/visuals/figures/, shown on the Figures page
(content/figures.md). Every figure is drawn in the drawing palette with
the guide's lines and type through tools/figurelib.py, which measures
each label with the IBM Plex font files so no word outgrows its box.

This is also the worked example for a script-drawn figure: copy a
function, change the data, keep the helpers. The data below is a snapshot
from 2026-10-20. For a chart from a CSV, use tools/chart.py; for a map,
tools/map.py.
"""
import datetime as dt
import math
import statistics
import os
import sys

from figurelib import *  # the palette, the type, and the drawing helpers

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "static", "visuals", "figures")


def write(name, content):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", name)


# 1. The palette ------------------------------------------------------------
def palette():
    swatches = [
        ("Ink", "#000000", INK),
        ("Tone 2", "#4F4F4F", TONE2),
        ("Tone 3", "#7A7A7A", TONE3),
        ("Tone 4", "#A3A3A3", TONE4),
        ("Edge", "#D9D9D9", EDGE),
        ("Surface", "#F7F7F7", SURFACE),
        ("Ground", "#FFFFFF", GROUND),
        ("Highlight", "#FFEB3B", HIGHLIGHT),
        ("Signal", "#FF4F00", SIGNAL),
    ]
    step = 760 / len(swatches)
    body = []
    for i, (name, literal, value) in enumerate(swatches):
        x = round(i * step)
        frame = f' stroke="{EDGE}"' if value in (GROUND, SURFACE) else ""
        if name == "Signal":
            # The signal is a lamp, never an area.
            body.append(f'<rect x="{x + 0.5}" y="0.5" width="71" height="47" stroke="{EDGE}" fill="{GROUND}"/>')
            body.append(f'<circle cx="{x + 36}" cy="24" r="3" fill="{value}"/>')
        else:
            body.append(f'<rect x="{x + 0.5}" y="0.5" width="71" height="47" fill="{value}"{frame}/>')
        body.append(text(x, 72, name, fill=INK))
        body.append(text(x, 92, literal, mono=True))
        check("swatch", literal, step - 6, mono=True)
    write("palette.svg", svg(760, 100, body))


# 2. Lines --------------------------------------------------------------------
def lines():
    cols = [
        ("Outline", [("1", True), (" px ink", False)]),
        ("Subject", [("2", True), (" px ink", False)]),
        ("Context", [("1", True), (" px edge", False)]),
        ("Not yet real", [("1", True), (" px faint, dashed", False)]),
        ("Leader", [("1", True), (" px faint", False)]),
    ]
    step = 152
    body = []
    for i, (name, spec) in enumerate(cols):
        x = i * step
        if name == "Outline":
            body.append(f'<rect x="{x + 0.5}" y="8.5" width="120" height="64" stroke="{INK}"/>')
        elif name == "Subject":
            body.append(f'<rect x="{x + 1}" y="9" width="119" height="63" stroke="{INK}" stroke-width="2"/>')
        elif name == "Context":
            for gx in range(0, 121, 24):
                body.append(f'<path d="M{x + gx + 0.5} 8V72" stroke="{EDGE}"/>')
            for gy in (8, 40, 72):
                body.append(f'<path d="M{x} {gy + 0.5}H{x + 121}" stroke="{EDGE}"/>')
            body.append(f'<rect x="{x + 24.5}" y="24.5" width="48" height="32" stroke="{INK}"/>')
        elif name == "Not yet real":
            body.append(f'<rect x="{x + 0.5}" y="8.5" width="120" height="64" stroke="{FAINT}" stroke-dasharray="4 4"/>')
        elif name == "Leader":
            body.append(f'<rect x="{x + 64.5}" y="40.5" width="56" height="32" stroke="{INK}"/>')
            body.append(f'<path d="M{x + 0.5} 20.5H{x + 40.5}V40" stroke="{FAINT}"/>')
            body.append(text(x, 14, "Drawer", fill=MUTED))
        body.append(text(x, 100, name, fill=INK))
        body.append(mixed(x, 120, spec))
        check("lines", name, step - 8)
    write("lines.svg", svg(760, 128, body))


# 4. Words in each Log month: a line chart, wide and narrow -------------------
LOG = [114, 107, 123, 101, 91, 106, 81, 89, 96, 94, 104, 113, 137, 94, 97, 99, 100, 78, 90, 96, 87, 91, 107, 105, 88, 100, 101, 94, 82, 91, 88, 58, 63, 86, 51, 48, 60, 65, 48, 46, 71, 88, 95, 80, 101, 84, 99, 74, 78, 104, 103, 39, 78, 99, 113, 45, 39, 99, 145, 138, 109, 79, 100, 137, 126, 166, 39, 15, 63, 86, 180, 231, 264, 257, 464, 394, 433, 403, 306, 265, 323, 384, 235, 258, 295, 480, 490, 272, 313, 380, 317, 348, 372]


def log_words(w, h, years_labeled, note, name):
    gutter = 36 if w > 400 else 32
    end_room = 40
    px0, px1 = gutter + 8, w - end_room
    top, base = 20, h - 40
    vmax = 500
    n = len(LOG)  # 2019-01 … 2026-09
    months_total = 8 * 12  # axis runs to 2026-12

    def X(i):
        return px0 + (px1 - px0) * i / (months_total - 1)

    def Y(v):
        return base - (base - top) * v / vmax

    body = []
    for v in range(100, vmax + 1, 100):
        y = round(Y(v)) + 0.5
        body.append(f'<path d="M{px0} {y}H{px1}" stroke="{EDGE}"/>')
        body.append(text(gutter, y + 5, str(v), mono=True, anchor="end"))
    body.append(text(gutter, base + 5, "0", mono=True, anchor="end"))
    for k in range(8):
        x = round(X(k * 12)) + 0.5
        body.append(f'<path d="M{x} {base}V{base + 6}" stroke="{INK}"/>')
        if 2019 + k in years_labeled:
            body.append(text(x - 0.5, base + 24, str(2019 + k), mono=True))
    pts = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(LOG))
    body.append(f'<polyline points="{pts}" stroke="{INK}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>')
    body.append(f'<path d="M{px0} {base + 0.5}H{px1}" stroke="{INK}"/>')
    # The note: where the months got longer, on an elbow leader.
    i = 70  # 2024-11
    lx, ly = X(i), Y(LOG[i]) - 10
    ny = Y(400)
    nw = mixed_width(note)
    body.append(f'<path d="M{lx:.1f} {ly:.1f}V{ny - 5:.1f}H{lx - 10:.1f}" stroke="{FAINT}"/>')
    body.append(mixed(lx - 16, ny, note, fill=MUTED, anchor="end"))
    if lx - 16 - nw < px0:
        print("  ! note runs past the plot")
    # The latest month: a dot with a ground ring and its value.
    ex, ey = X(n - 1), Y(LOG[-1])
    body.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="4" fill="{INK}" stroke="{GROUND}" stroke-width="2"/>')
    body.append(text(ex + 10, ey + 5, str(LOG[-1]), mono=True, fill=INK))
    write(name, svg(w, h, body))


# 5. Research entries by day: an instrument, wide and narrow ------------------
DAYS = [(3, 0), (4, 1), (3, 0), (3, 0), (4, 0), (7, 0)] + [(0, 0)] * 12 + [(3, 0)]


def day_readout(d, a, t):
    date = (dt.date(2026, 10, 1) + dt.timedelta(days=d)).isoformat()
    total = a + t
    if not total:
        return f"{date} · No entries"
    word = "entry" if total == 1 else "entries"
    if a and t:
        return f"{date} · {total} {word}: {a} in Ambient Computing, {t} in Tools for Thought"
    return f"{date} · {total} {word} in " + ("Ambient Computing" if a else "Tools for Thought")


def research_days(w, h, labels, name):
    slots = len(DAYS)
    slot = w / slots
    col = min(16, slot - 6)
    top, base = 24, h - 64
    top_key = base + 50
    unit = (base - top) / 7
    body = []
    # The key, drawn into the figure: a square per stream.
    kx = 0
    for label, fill in (("Ambient Computing", INK), ("Tools for Thought", TONE3)):
        body.append(f'<rect x="{kx}" y="{top_key - 9}" width="10" height="10" fill="{fill}"/>')
        body.append(text(kx + 16, top_key, label, fill=MUTED))
        kx += 16 + width(label) + 20
    for d, (a, t) in enumerate(DAYS):
        cx = slot * d + slot / 2
        x = cx - col / 2
        parts = [f'<rect data-band="" x="{x - 4:.1f}" y="{top - 8}" width="{col + 8:.1f}" height="{base - top + 8}" fill="none"/>']
        if a + t == 0:
            parts.append(f'<rect x="{x:.1f}" y="{base - 2}" width="{col:.1f}" height="2" fill="{EDGE}"/>')
        else:
            ha = a * unit
            parts.append(f'<rect x="{x:.1f}" y="{base - ha:.1f}" width="{col:.1f}" height="{ha:.1f}" fill="{INK}"/>')
            if t:
                ht = t * unit
                parts.append(f'<rect x="{x:.1f}" y="{base - ha - 2 - ht:.1f}" width="{col:.1f}" height="{ht:.1f}" fill="{TONE3}"/>')
        body.append(f'<g data-mark="" data-readout="{escape(day_readout(d, a, t))}">' + "".join(parts) + "</g>")
    # The busiest day carries its number; the readout carries the rest.
    peak = max(range(slots), key=lambda d: sum(DAYS[d]))
    body.append(text(slot * peak + slot / 2, base - sum(DAYS[peak]) * unit - 8, str(sum(DAYS[peak])), mono=True, fill=INK, anchor="middle"))
    body.append(f'<path d="M0 {base + 0.5}H{w}" stroke="{INK}"/>')
    for d, label in labels:
        x = slot * d + slot / 2
        anchor = "start" if d == 0 else ("end" if d == slots - 1 else "middle")
        if d == 0:
            x = 0
        if d == slots - 1:
            x = w
        body.append(text(x, base + 22, label, mono=True, anchor=anchor))
    write(name, svg(w, h, body))


# 6. Dispatches on a timeline -------------------------------------------------
DISPATCHES = ["2021-02-08", "2021-05-30", "2021-06-29", "2022-08-07", "2022-12-27", "2023-01-12", "2024-01-05", "2024-01-10", "2025-03-14", "2025-04-14", "2025-06-25", "2025-07-22", "2025-12-12", "2026-06-26", "2026-07-31", "2026-09-02", "2026-10-16"]


def dispatches():
    w, h = 760, 112
    start, end = dt.date(2021, 1, 1), dt.date(2027, 1, 1)
    span = (end - start).days
    base = 64

    def X(d):
        return w * (d - start).days / span

    body = [f'<path d="M0 {base + 0.5}H{w}" stroke="{INK}"/>']
    for year in range(2021, 2028):
        x = round(X(dt.date(year, 1, 1))) + 0.5
        x = min(x, w - 0.5)
        body.append(f'<path d="M{x} {base}V{base + 6}" stroke="{INK}"/>')
        if year < 2027:
            body.append(text(x - 0.5, base + 24, str(year), mono=True))
    placed = []
    for i, s in enumerate(DISPATCHES):
        d = dt.date.fromisoformat(s)
        x = X(d)
        level = 0
        while any(abs(px - x) < 11 and pl == level for px, pl in placed):
            level += 1
        placed.append((x, level))
        y = base - 8 - level * 12
        body.append(f'<circle cx="{x:.1f}" cy="{y}" r="4" fill="{INK}" stroke="{GROUND}" stroke-width="2"/>')
        if i in (0, len(DISPATCHES) - 1):
            body.append(text(x, y - 14, f"{i + 1:03d}", mono=True, fill=INK, anchor="middle"))
    write("dispatches.svg", svg(w, h, body))


# 7. One brain, five surfaces: a wide flow diagram ----------------------------


def studio_brain():
    A, B, C, D = (0, 210), (294, 210), (592, 230), (900, 220)
    top, bh, gap = 32, 64, 16
    rows = [top + k * (bh + gap) for k in range(5)]
    body = []
    for (x, _), head in zip((A, B, C, D), ("In the studio", "Device layer", "Studio brain", "Surfaces")):
        body.append(text(x, 14, head))
    studio = [
        ("Hue Bridge Pro", "16 lamps, 2 controls", "Local API"),
        ("Aqara Hub M200", "3 contacts, climate sensor", "Matter"),
        ("Broadlink RM4 ×2", "2 ACs, planned", "IR, local"),
        ("Printers", "Saturn now, Bambu later", "Integration"),
    ]
    for k, (name, line, link) in enumerate(studio):
        y = rows[k]
        body += box(A[0], y, A[1], bh, name, [line])
        my = y + bh / 2 + 0.5
        body.append(f'<path d="M{A[0] + A[1]} {my}H{B[0] - 1}" stroke="{INK}"/>')
        body.append(arrow_head(B[0], my, "right"))
        body.append(text((A[0] + A[1] + B[0]) / 2, my - 7, link, anchor="middle"))
        check("link", link, B[0] - A[0] - A[1] - 8)
    ha_bottom = rows[3] + bh
    body += box(B[0], top, B[1], ha_bottom - top, "Home Assistant Green", ["Entities and history", "Automations that work", "without the brain", "Tag scans from labels"])
    brain_bottom = rows[4] + bh
    body += box(C[0], top, C[1], brain_bottom - top, "Studio brain", ["Mac mini now, NAS later", "", "Model and its 73 places", "Catalog and photos", "Scenes and checks", "State mirror, event log", "Serves every screen"], sw=2, fill=SURFACE)
    # States up to the brain, calls back down to Home Assistant.
    gx0, gx1 = B[0] + B[1], C[0]
    for y, label, direction in ((rows[1] + 8, "States", "right"), (rows[2] + 8, "Calls", "left")):
        y = y + 0.5
        body.append(f'<path d="M{gx0 + (0 if direction == "right" else 7)} {y}H{gx1 - (2 if direction == "right" else 0)}" stroke="{INK}"/>')
        body.append(arrow_head(gx1 - 1, y, "right") if direction == "right" else arrow_head(gx0, y, "left"))
        body.append(text((gx0 + gx1) / 2, y - 7, label, anchor="middle"))
    surfaces = [
        ("Wall screen", "Always on, read-only"),
        ("Phones", "Web app: find, capture"),
        ("Manage", "Catalog, entity map"),
        ("Stream Deck + XL", "Keys and dials at the desk"),
        ("Lab and Study iPads", "Control panels"),
    ]
    sx0, sx1 = C[0] + C[1], D[0]
    for k, (name, line) in enumerate(surfaces):
        y = rows[k]
        body += box(D[0], y, D[1], bh, name, [line])
        my = y + bh / 2 + 0.5
        body.append(f'<path d="M{sx0 + 8} {my}H{sx1 - 7}" stroke="{INK}"/>')
        body.append(arrow_head(sx0 + 2, my, "left"))
        body.append(arrow_head(sx1 - 1, my, "right"))
        if k == 0:
            body.append(text((sx0 + sx1) / 2, my - 7, "Live", anchor="middle"))
    # Claude under the brain.
    cy = brain_bottom + 48
    body += box(C[0], cy, C[1], 88, "Claude", ["Reads drawer photos", "Answers where-is questions"])
    ax = C[0] + 40.5
    body.append(f'<path d="M{ax} {brain_bottom + 8}V{cy - 8}" stroke="{INK}"/>')
    body.append(arrow_head(ax, brain_bottom + 2, "up"))
    body.append(arrow_head(ax, cy - 1, "down"))
    body.append(text(ax + 10, (brain_bottom + cy) / 2 + 5, "Photos down, changes up"))
    # Outside the brain, dashed: the cameras go to Apple Home over HomeKit.
    oy = cy + 88 + 40
    body += box(A[0], oy, A[1], bh, "Cameras, doorbell", ["Camera E1 ×2, G4"], stroke=FAINT, dashed=True)
    body += box(D[0], oy, D[1], bh, "Apple Home", ["HomePod hub, iPad views"], stroke=FAINT, dashed=True)
    my = oy + bh / 2 + 0.5
    body.append(f'<path d="M{A[0] + A[1]} {my}H{D[0] - 7}" stroke="{FAINT}" stroke-dasharray="4 4"/>')
    body.append(arrow_head(D[0] - 1, my, "right"))
    body.append(text((A[0] + A[1] + C[0]) / 2 + 40, my - 7, "HomeKit, outside the brain", anchor="middle"))
    vx = D[0] + D[1] / 2 + 0.5
    body.append(f'<path d="M{vx} {oy - 1}V{rows[4] + bh + 8}" stroke="{FAINT}" stroke-dasharray="4 4"/>')
    body.append(arrow_head(vx, rows[4] + bh + 1, "up"))
    body.append(text(vx + 10, (oy + rows[4] + bh) / 2 + 5, "Camera views"))
    write("studio-brain.svg", svg(1120, oy + bh + 1, body))


# Shared pieces for the charts below ----------------------------------------
BULLETS = [8, 8, 10, 9, 8, 9, 8, 9, 10, 9, 12, 10, 12, 9, 9, 9, 10, 9, 8, 10, 9, 11, 9, 7, 8, 7, 8, 8, 5, 6, 6, 5, 5, 9, 5, 4, 6, 6, 4, 3, 6, 9, 7, 7, 7, 8, 5, 5, 7, 9, 9, 4, 8, 7, 9, 3, 4, 5, 7, 7, 7, 7, 7, 6, 6, 8, 4, 2, 6, 8, 7, 9, 9, 12, 15, 12, 16, 9, 17, 10, 9, 13, 11, 9, 10, 14, 17, 10, 9, 10, 12, 10, 12]
NOTE_DATES = ["2018-11-26", "2024-01-10", "2025-01-07", "2025-01-13", "2025-06-06", "2025-12-05", "2025-12-05", "2026-02-21", "2026-02-28", "2026-05-07", "2026-05-26", "2026-06-28", "2026-06-28", "2026-06-28", "2026-08-29", "2026-10-06", "2026-10-10"]


# 8. Two series side by side: grouped columns ---------------------------------
NOTES_BY_YEAR = {2021: 0, 2022: 0, 2023: 0, 2024: 1, 2025: 5, 2026: 10}
DISPATCHES_BY_YEAR = {2021: 3, 2022: 2, 2023: 1, 2024: 2, 2025: 5, 2026: 4}


def grouped_columns():
    w = 760
    years = sorted(NOTES_BY_YEAR)
    top, base = 28, 168
    unit = (base - top) / 10
    slot = w / len(years)
    col, gap = 20, 2
    body = []
    for k, year in enumerate(years):
        cx = slot * k + slot / 2
        # The comparison first, in tone 3; the subject second, in ink.
        for j, (fill, data) in enumerate(((TONE3, DISPATCHES_BY_YEAR), (INK, NOTES_BY_YEAR))):
            x = cx - col - gap / 2 + j * (col + gap)
            v = data[year]
            if v:
                body.append(f'<rect x="{x:.1f}" y="{base - v * unit:.1f}" width="{col}" height="{v * unit:.1f}" fill="{fill}"/>')
                body.append(text(x + col / 2, base - v * unit - 8, str(v), mono=True, fill=INK, anchor="middle"))
            else:
                body.append(f'<rect x="{x:.1f}" y="{base - 2}" width="{col}" height="2" fill="{EDGE}"/>')
        body.append(text(cx, base + 24, str(year), mono=True, anchor="middle"))
    body.append(f'<path d="M0 {base + 0.5}H{w}" stroke="{INK}"/>')
    body += swatch_key(0, base + 56, [("Flâneur dispatches", TONE3), ("Notes", INK)])
    write("pages-by-year.svg", svg(w, base + 64, body))


# 9. Two series on one scale: counted up over time ----------------------------
def two_lines():
    w, h = 760, 300
    start, end = dt.date(2021, 1, 1), dt.date(2027, 1, 1)
    gutter, px0, px1 = 28, 36, w - 40
    top, base, vmax = 16, 250, 20

    def X(d):
        return px0 + (px1 - px0) * (d - start).days / (end - start).days

    def Y(v):
        return base - (base - top) * v / vmax

    def steps(dates, count):
        pts = [(X(start), Y(count))]
        for s in dates:
            d = dt.date.fromisoformat(s)
            if d < start:
                continue
            pts.append((X(d), Y(count)))
            count += 1
            pts.append((X(d), Y(count)))
        return pts, count

    body = []
    for v in range(5, vmax + 1, 5):
        y = round(Y(v)) + 0.5
        body.append(f'<path d="M{px0} {y}H{px1}" stroke="{EDGE}"/>')
        body.append(text(gutter, y + 5, str(v), mono=True, anchor="end"))
    body.append(text(gutter, base + 5, "0", mono=True, anchor="end"))
    body += year_axis(X, base, list(range(2021, 2027)), px1)

    def line(pts, fill):
        return f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" stroke="{fill}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>'

    flaneur, n_f = steps(DISPATCHES, 0)
    notes, n_n = steps(NOTE_DATES, sum(d < "2021" for d in NOTE_DATES))
    # The comparison is an optional layer: the toggle shows or hides it.
    body.append('<g data-optional="">' + line(flaneur, TONE3)
                + text(X(dt.date(2021, 3, 1)), Y(3) - 8, "Flâneur dispatches", fill=MUTED)
                + dot(*flaneur[-1], fill=TONE3) + "</g>")
    body.append(line(notes, INK))
    body.append(text(X(dt.date(2023, 3, 1)), Y(1) - 10, "Notes", fill=MUTED))
    body.append(dot(*notes[-1]))
    body.append(text(notes[-1][0] + 12, notes[-1][1] + 5, str(n_n), mono=True, fill=INK))
    assert n_n == n_f == 17
    write("notes-and-dispatches.svg", svg(w, h, body))


# 10. Before and after: one row per section -----------------------------------
CHANGE = [("Research", 0, 28), ("Project Humane", 0, 7), ("Notes", 5, 10), ("Obsidian", 2, 4), ("Flâneur", 5, 4), ("Log", 12, 9), ("Darkroom", 8, 0)]


def dumbbell():
    w = 760
    names_x, px0, px1 = 120, 136, 616
    c1, c2 = 688, 748  # the value columns, right-aligned
    top, row = 40, 32
    vmax = 30

    def X(v):
        return px0 + (px1 - px0) * v / vmax

    body = []
    # Column heads double as the key: the dot beside each year.
    body.append(f'<circle cx="{c1 - width("2025", True) - 10}" cy="12" r="4" fill="{TONE3}"/>')
    body.append(text(c1, 17, "2025", mono=True, anchor="end"))
    body.append(dot(c2 - width("2026", True) - 10, 12))
    body.append(text(c2, 17, "2026", mono=True, anchor="end", fill=INK))
    bottom = top + row * len(CHANGE) - row / 2
    for v in range(0, vmax + 1, 10):
        x = round(X(v)) + 0.5
        body.append(f'<path d="M{x} {top - 12}V{bottom}" stroke="{EDGE}"/>')
        body.append(text(x, bottom + 22, str(v), mono=True, anchor="middle"))
    for k, (name, a, b) in enumerate(CHANGE):
        y = top + k * row + 0.5
        body.append(text(names_x, y + 5, name, fill=MUTED, anchor="end"))
        check("dumbbell name", name, names_x)
        body.append(f'<path d="M{X(a):.1f} {y}H{X(b):.1f}" stroke="{EDGE}" stroke-width="2"/>')
        body.append(f'<circle cx="{X(a):.1f}" cy="{y}" r="4" fill="{TONE3}"/>')
        body.append(dot(X(b), y))
        body.append(text(c1, y + 5, str(a), mono=True, anchor="end"))
        body.append(text(c2, y + 5, str(b), mono=True, anchor="end", fill=INK))
    write("sections-change.svg", svg(w, bottom + 30, body))


# 11. Part to whole, year by year: Log months by length -----------------------
LENGTHS = {2019: (0, 7, 5), 2020: (0, 4, 8), 2021: (0, 2, 10), 2022: (0, 1, 11), 2023: (0, 5, 7), 2024: (0, 7, 5), 2025: (11, 1, 0), 2026: (9, 0, 0)}


def log_lengths():
    w = 760
    gutter, x0 = 40, 56
    unit = (w - x0) / 12
    top, row, bar = 0, 28, 20
    # Three ordered steps with words inside each: ink and tone 2 take
    # ground words, tone 4 takes ink words, in both themes.
    steps = ((INK, GROUND), (TONE2, GROUND), (TONE4, INK))
    body = []
    for k, (year, counts) in enumerate(sorted(LENGTHS.items())):
        y = top + k * row
        body.append(text(gutter, y + 15, str(year), mono=True, anchor="end"))
        x = x0
        for n, (fill, ink) in zip(counts, steps):
            if not n:
                continue
            seg = n * unit - 2
            body.append(f'<rect x="{x:.1f}" y="{y}" width="{seg:.1f}" height="{bar}" fill="{fill}"/>')
            body.append(text(x + 8, y + 15, str(n), mono=True, fill=ink))
            x += n * unit
    base = top + len(LENGTHS) * row
    body += swatch_key(x0, base + 20, [
        ([("Long, ", False), ("250", True), (" words or more", False)], INK),
        ([("Medium, ", False), ("100–249", True)], TONE2),
        ([("Short, under ", False), ("100", True)], TONE4),
    ])
    write("log-lengths.svg", svg(w, base + 28, body))


# 12. Difference from a baseline: diverging columns ---------------------------
def log_difference():
    w, h = 760, 300
    median = statistics.median(LOG[:72])
    gutter, px0, px1 = 36, 44, w
    top, bottom = 16, 252
    vmax, vmin = 400, -100

    def Y(v):
        return top + (bottom - top) * (vmax - v) / (vmax - vmin)

    slot = (px1 - px0) / 96
    col = slot - 2
    body = []
    for v in (400, 300, 200, 100, -100):
        y = round(Y(v)) + 0.5
        body.append(f'<path d="M{px0} {y}H{px1}" stroke="{EDGE}"/>')
        body.append(text(gutter, y + 5, f"+{v}" if v > 0 else f"−{-v}", mono=True, anchor="end"))
    for i, v in enumerate(LOG):
        d = v - median
        x = px0 + i * slot + 1
        y0, y1 = Y(max(d, 0)), Y(min(d, 0))
        fill = INK if d > 0 else TONE3
        body.append(f'<rect x="{x:.1f}" y="{y0:.1f}" width="{col:.1f}" height="{max(y1 - y0, 1):.1f}" fill="{fill}"/>')
    zy = round(Y(0)) + 0.5
    body.append(f'<path d="M{px0} {zy}H{px1}" stroke="{INK}"/>')
    body.append(text(gutter, zy + 5, "0", mono=True, anchor="end"))
    for k in range(8):
        x = round(px0 + k * 12 * slot) + 0.5
        body.append(f'<path d="M{x} {bottom}V{bottom + 6}" stroke="{INK}"/>')
        body.append(text(x - 0.5, bottom + 24, str(2019 + k), mono=True))
    body.append(f'<path d="M{px0} {bottom + 0.5}H{px1}" stroke="{EDGE}"/>')
    write("log-difference.svg", svg(w, h, body))


# 13. Relationship: a scatter of two measures ---------------------------------
def scatter():
    w, h = 760, 356
    gutter, px0, px1 = 36, 44, w - 8
    top, base = 36, 296
    xmax, ymax = 18, 500

    def X(v):
        return px0 + (px1 - px0) * v / xmax

    def Y(v):
        return base - (base - top) * v / ymax

    body = [text(gutter, 14, "Words in the month", anchor="start", fill=FAINT).replace(f'x="{gutter}"', 'x="0"')]
    for v in range(100, ymax + 1, 100):
        y = round(Y(v)) + 0.5
        body.append(f'<path d="M{px0} {y}H{px1}" stroke="{EDGE}"/>')
        body.append(text(gutter, y + 5, str(v), mono=True, anchor="end"))
    for v in (0, 5, 10, 15):
        x = round(X(v)) + 0.5
        body.append(f'<path d="M{x} {base}V{base + 6}" stroke="{INK}"/>')
        body.append(text(x, base + 24, str(v), mono=True, anchor="middle"))
    body.append(f'<path d="M{px0} {base + 0.5}H{px1}" stroke="{INK}"/>')
    body.append(text(px1, base + 48, "Bullets in the month", anchor="end"))
    # Two guides: words per bullet, as straight lines from zero.
    for rate, label in ((10, "10 words a bullet"), (30, "30 words a bullet")):
        xe = min(xmax, ymax / rate)
        body.append(f'<path d="M{X(0):.1f} {Y(0):.1f}L{X(xe):.1f} {Y(xe * rate):.1f}" stroke="{EDGE}"/>')
        lx, ly = X(xe), Y(xe * rate)
        # Each guide is named at its far end, clear of the gridlines.
        body.append(text(lx - 6, ly - 8, label, anchor="end") if rate == 30 else text(lx, ly + 22, label, anchor="end"))
    old = [(b, v) for b, v in zip(BULLETS[:72], LOG[:72])]
    new = [(b, v) for b, v in zip(BULLETS[72:], LOG[72:])]
    for b, v in old:
        body.append(dot(X(b), Y(v), fill=TONE4))
    for b, v in new:
        body.append(dot(X(b), Y(v)))
    body.append(text(X(8.4), Y(318), "2025–2026", fill=INK, anchor="end"))
    body.append(text(X(12.6), Y(105), "2019–2024", fill=MUTED))
    write("log-scatter.svg", svg(w, h, body))


# 14. A calendar: year by month, with two states ------------------------------
def calendar():
    w = 760
    gutter, x0 = 40, 52
    cell, gap, ch = 55, 4, 24
    y0 = 24
    words_bins = ((100, TONE4), (200, TONE3), (300, TONE2), (10_000, INK))
    bullet_bins = ((6, TONE4), (9, TONE3), (12, TONE2), (100, INK))
    body = []
    for m in range(12):
        body.append(text(x0 + m * (cell + gap) + cell / 2, 14, f"{m + 1:02d}", mono=True, anchor="middle"))
    for k in range(8):
        body.append(text(gutter, y0 + k * (ch + gap) + 17, str(2019 + k), mono=True, anchor="end"))
    base = y0 + 8 * (ch + gap)

    def layer(values, bins, key, state):
        out = []
        for i in range(96):
            x = x0 + (i % 12) * (cell + gap)
            y = y0 + (i // 12) * (ch + gap)
            if i >= len(values):
                out.append(f'<rect x="{x + 0.5}" y="{y + 0.5}" width="{cell - 1}" height="{ch - 1}" stroke="{TONE4}"/>')
                continue
            fill = next(f for limit, f in bins if values[i] < limit)
            out.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{ch}" fill="{fill}"/>')
        out += swatch_key(x0, base + 24, key)
        # Every state after the first is hidden in the file itself, so the
        # file and its PNG show the first; the page's CSS takes over inline.
        hidden = ' display="none"' if state > 1 else ""
        return f'<g data-state="{state}"{hidden}>' + "".join(out) + "</g>"

    body.append(layer(LOG, words_bins, [
        ([("Under ", False), ("100", True), (" words", False)], TONE4),
        ([("100–199", True)], TONE3),
        ([("200–299", True)], TONE2),
        ([("300", True), (" or more", False)], INK),
        ("Not yet written", "open"),
    ], 1))
    body.append(layer(BULLETS, bullet_bins, [
        ([("Under ", False), ("6", True), (" bullets", False)], TONE4),
        ([("6–8", True)], TONE3),
        ([("9–11", True)], TONE2),
        ([("12", True), (" or more", False)], INK),
        ("Not yet written", "open"),
    ], 2))
    write("log-calendar.svg", svg(w, base + 32, body))


# 15. Small multiples: one small chart per year, on one scale -----------------
def small_multiples(w, cols, name):
    gutter = 32
    gap = 24 if cols > 2 else 16
    pw = (w - gutter - gap * (cols - 1)) / cols
    ph, head, foot = 64, 24, 20
    rows = 8 // cols
    body = []
    for k in range(8):
        r, c = divmod(k, cols)
        x0 = gutter + c * (pw + gap)
        y0 = r * (head + ph + foot)
        base = y0 + head + ph
        months = LOG[k * 12:(k + 1) * 12]
        body.append(text(x0, y0 + 14, str(2019 + k), mono=True, fill=INK))
        total = f"{sum(months):,}"
        body.append(mixed(x0 + pw, y0 + 14, [(total, True), (" words", False)], anchor="end"))
        gy = round(base - ph / 2) + 0.5
        body.append(f'<path d="M{x0:.1f} {gy}H{x0 + pw:.1f}" stroke="{EDGE}"/>')
        if c == 0:
            body.append(text(gutter - 8, gy + 5, "250", mono=True, anchor="end"))
        pts = " ".join(f"{x0 + pw * i / 11:.1f},{base - ph * v / 500:.1f}" for i, v in enumerate(months))
        body.append(f'<polyline points="{pts}" stroke="{INK}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>')
        body.append(f'<path d="M{x0:.1f} {base + 0.5}H{x0 + pw:.1f}" stroke="{INK}"/>')
    write(name, svg(w, rows * (head + ph + foot) - foot + 4, body))


# 16. A pipeline: numbered steps, left to right -------------------------------
def pipeline():
    w = 760
    bw, gap, bh = 136, 20, 84
    y = 24
    steps = [
        ("Write", [[("Markdown, SCSS,", False)], [("JavaScript", False)]]),
        ("Build", [[("Hugo Extended", False)], [("0.164.0", True)]]),
        ("Output", [[("Pages, feeds,", False)], [("sitemap", False)]]),
        ("Deploy", [[("DigitalOcean,", False)], [("from main", False)]]),
        ("Read", [[("ttvl.co", False)]]),
    ]
    body = []
    for k, (name, sub) in enumerate(steps):
        x = k * (bw + gap)
        body.append(text(x, 14, f"{k + 1:02d}", mono=True))
        body.append(f'<rect x="{x + 0.5}" y="{y + 0.5}" width="{bw - 1}" height="{bh - 1}" fill="{GROUND}" stroke="{INK}"/>')
        body.append(text(x + 12, y + 26, name, size=16, weight=500, fill=INK))
        for j, parts in enumerate(sub):
            body.append(mixed(x + 12, y + 48 + 20 * j, parts, fill=MUTED))
            if mixed_width(parts) > bw - 24:
                print(f"  ! pipeline: {parts} is too wide")
        if k < len(steps) - 1:
            my = y + bh / 2 + 0.5
            body.append(f'<path d="M{x + bw} {my}H{x + bw + gap - 7}" stroke="{INK}"/>')
            body.append(arrow_head(x + bw + gap - 1, my, "right"))
    # The branch: each dispatch also leaves as email, through a service
    # outside the site, so it is dashed.
    ox = 2 * (bw + gap)
    ry = y + bh + 40
    body.append(f'<rect x="{ox + 0.5}" y="{ry + 0.5}" width="{bw - 1}" height="63" fill="{GROUND}" stroke="{INK}"/>')
    body.append(text(ox + 12, ry + 26, "Email", size=16, weight=500, fill=INK))
    body.append(text(ox + 12, ry + 48, "email.html", mono=True, fill=MUTED))
    vx = ox + bw / 2 + 0.5
    body.append(f'<path d="M{vx} {y + bh}V{ry - 7}" stroke="{INK}"/>')
    body.append(arrow_head(vx, ry - 1, "down"))
    body.append(text(vx + 10, y + bh + 25, "Each dispatch"))
    cx, cw = 3 * (bw + gap), 2 * bw + gap
    body.append(f'<rect x="{cx + 0.5}" y="{ry + 0.5}" width="{cw - 1}" height="63" stroke="{FAINT}" stroke-dasharray="4 4"/>')
    body.append(text(cx + 12, ry + 26, "Campaign Monitor", size=16, weight=500, fill=INK))
    body.append(text(cx + 12, ry + 48, "Sends it to subscribers", fill=MUTED))
    my = ry + 32.5
    body.append(f'<path d="M{ox + bw} {my}H{cx - 7}" stroke="{INK}"/>')
    body.append(arrow_head(cx - 1, my, "right"))
    write("site-pipeline.svg", svg(w, ry + 64, body))


# 17. A tree: the site's sections, left to right ------------------------------
TREE = [
    ("Projects", None, [("Darkroom", 12), ("Project Humane", 8), ("Obsidian", 6), ("Notebook system", 3), ("Bookbinding", 1)]),
    ("Notes", 17, []),
    ("Research", 28, [("Ambient Computing", 27), ("Tools for Thought", 1)]),
    ("Log", 93, []),
    ("Newsletter", 17, []),
    ("Traces", 3, []),
    ("About", None, []),
]


def tree():
    w, row = 640, 28
    x1, x2, x3 = 0, 152, 360
    body = []
    y = 0
    placed = []
    for name, count, children in TREE:
        n = max(1, len(children))
        cy = y + row * (n - 1) / 2 + 14
        placed.append((name, count, children, y, cy))
        y += row * n
    height = y
    root_y = height / 2
    body.append(text(x1, root_y + 6, "ttvl.co", size=16, weight=500, fill=INK))
    trunk = width("ttvl.co", weight=500, size=16) + 12
    first, last = placed[0][4], placed[-1][4]
    tx = round(x2 - 24) + 0.5
    body.append(f'<path d="M{trunk:.1f} {root_y + 0.5}H{tx}" stroke="{INK}"/>')
    body.append(f'<path d="M{tx} {first + 0.5}V{last + 0.5}" stroke="{INK}"/>')
    for name, count, children, top, cy in placed:
        body.append(f'<path d="M{tx} {cy + 0.5}H{x2 - 8}" stroke="{INK}"/>')
        parts = [(name, False)]
        body.append(text(x2, cy + 6, name, size=16, weight=500, fill=INK))
        end = x2 + width(name, weight=500, size=16)
        if count is not None:
            body.append(text(end + 8, cy + 6, str(count), mono=True))
            end += 8 + width(str(count), mono=True)
        if children:
            cx = round(x3 - 24) + 0.5
            body.append(f'<path d="M{end + 12:.1f} {cy + 0.5}H{cx}" stroke="{INK}"/>')
            ys = [top + row * i + 14 for i in range(len(children))]
            body.append(f'<path d="M{cx} {ys[0] + 0.5}V{ys[-1] + 0.5}" stroke="{INK}"/>')
            for (child, n), yy in zip(children, ys):
                body.append(f'<path d="M{cx} {yy + 0.5}H{x3 - 8}" stroke="{INK}"/>')
                body.append(text(x3, yy + 5, child, fill=MUTED))
                body.append(text(x3 + width(child) + 8, yy + 5, str(n), mono=True))
    write("site-tree.svg", svg(w, height, body))


# 18. Spans in time: from each section's first page to its latest -------------
SPANS = [
    ("Notes", "2018-11-26", "2026-10-10"),
    ("Log", "2019-01-31", "2026-09-30"),
    ("Flâneur", "2021-02-08", "2026-10-16"),
    ("Darkroom", "2024-12-02", "2025-08-01"),
    ("Project Humane", "2024-12-20", "2026-09-25"),
    ("Notebook system", "2025-01-08", "2025-01-10"),
    ("Obsidian", "2025-09-18", "2026-06-12"),
    ("Bookbinding", "2026-02-27", "2026-02-27"),
    ("Traces", "2026-07-13", "2026-09-19"),
    ("Research", "2026-10-01", "2026-10-19"),
]


def spans():
    w = 760
    names_x, px0, px1 = 120, 136, 752
    start, end = dt.date(2018, 1, 1), dt.date(2027, 1, 1)
    top, row = 32, 24

    def X(d):
        return px0 + (px1 - px0) * (d - start).days / (end - start).days

    body = []
    base = top + row * len(SPANS)
    today = X(dt.date(2026, 10, 20))
    tx = round(today) + 0.5
    body.append(f'<path d="M{tx} {top - 12}V{base}" stroke="{FAINT}" stroke-dasharray="4 4"/>')
    body.append(text(tx, 14, "2026-10-20", mono=True, anchor="end"))
    for k, (name, a, b) in enumerate(SPANS):
        y = top + k * row
        body.append(text(names_x, y + 5, name, fill=MUTED, anchor="end"))
        check("span name", name, names_x)
        x0, x1 = X(dt.date.fromisoformat(a)), X(dt.date.fromisoformat(b))
        body.append(f'<rect x="{x0:.1f}" y="{y - 4}" width="{max(x1 - x0, 8):.1f}" height="8" fill="{INK}"/>')
    body += year_axis(X, base + 8, list(range(2018, 2027)), px1)
    write("section-spans.svg", svg(w, base + 40, body))


# More forms: argument shapes, states, sequences, scale, keys, eras, a
# distribution, the darkroom's zones and curve, steps ----------------------


def shapes():
    w = 760
    body = []
    # A spectrum: three sections between a record and an argument.
    body.append(text(0, 14, "A spectrum"))
    y = 84.5
    body.append(f'<path d="M0 {y}H{w}" stroke="{INK}"/>')
    body.append(text(0, y + 28, "A record"))
    body.append(text(w, y + 28, "An argument", anchor="end"))
    for f, name, desc in ((0.2, "Log", "What I made"), (0.5, "Research", "What I tried and found"), (0.8, "Notes", "What I think")):
        x = f * w
        body.append(dot(x, y))
        body.append(text(x, y - 36, name, size=16, weight=500, fill=INK, anchor="middle"))
        body.append(text(x, y - 16, desc, fill=MUTED, anchor="middle"))
    # Three panels: a matrix, a cycle, containment.
    y0 = 160
    for x, name in ((0, "A matrix"), (260, "A cycle"), (520, "Containment")):
        body.append(text(x, y0 + 14, name))
    # A matrix: how long the pages are against how often they come.
    mx, my, ms = 56, y0 + 36, 176
    body.append(f'<rect x="{mx + 0.5}" y="{my + 0.5}" width="{ms - 1}" height="{ms - 1}" stroke="{EDGE}"/>')
    body.append(f'<path d="M{mx + ms / 2 + 0.5} {my}V{my + ms}M{mx} {my + ms / 2 + 0.5}H{mx + ms}" stroke="{INK}"/>')
    body.append(text(mx - 8, my + 14, "Often", anchor="end"))
    body.append(text(mx - 8, my + ms, "Seldom", anchor="end"))
    body.append(text(mx, my + ms + 22, "Short"))
    body.append(text(mx + ms, my + ms + 22, "Long", anchor="end"))
    for fx, fy, name in ((0.06, 0.14, "Research"), (0.18, 0.38, "Log"), (0.6, 0.6, "Notes"), (0.62, 0.84, "Flâneur")):
        px, py = mx + fx * ms, my + fy * ms
        body.append(dot(px, py))
        body.append(text(px + 10, py + 5, name, fill=INK))
    # A cycle: a question, the work on it, what it finds, the next question.
    cx, cy, r = 260 + 120, y0 + 36 + 88, 64
    nodes = ((-90, "Question", "middle", 0, -14), (30, "Progress", "start", 12, 18), (150, "Finding", "end", -12, 18))
    for k, (a, name, anchor, ox, oy) in enumerate(nodes):
        t = math.radians(a)
        nx, ny = cx + r * math.cos(t), cy + r * math.sin(t)
        body.append(dot(nx, ny))
        body.append(text(nx + ox, ny + oy, name, fill=INK, anchor=anchor))
        a2 = nodes[(k + 1) % 3][0] + (360 if k == 2 else 0)
        s0, s1 = math.radians(a + 14), math.radians(a2 - 14)
        x1, y1 = cx + r * math.cos(s0), cy + r * math.sin(s0)
        x2, y2 = cx + r * math.cos(s1), cy + r * math.sin(s1)
        body.append(f'<path d="M{x1:.1f} {y1:.1f}A{r} {r} 0 0 1 {x2:.1f} {y2:.1f}" stroke="{INK}"/>')
        body.append(arrow_dir(x2, y2, -math.sin(s1), math.cos(s1)))
    # Containment: the site holds the section, the stream, the entry.
    nx0, ny0 = 520, y0 + 36
    levels = ("ttvl.co", "Research", "Ambient Computing", "Entry 019")
    for i, name in enumerate(levels):
        rx, ry = nx0 + 14 * i, ny0 + 28 * i
        rw, rh = 240 - 28 * i, 196 - 38 * i
        last = i == len(levels) - 1
        if last:
            body.append(f'<rect x="{rx + 1}" y="{ry + 1}" width="{rw - 2}" height="{rh - 2}" fill="{SURFACE}" stroke="{INK}" stroke-width="2"/>')
            body.append(text(rx + 10, ry + 22, name, size=16, weight=500, fill=INK))
        else:
            body.append(f'<rect x="{rx + 0.5}" y="{ry + 0.5}" width="{rw - 1}" height="{rh - 1}" fill="{GROUND}" stroke="{INK}"/>')
            body.append(text(rx + 10, ry + 19, name, fill=INK if i else MUTED))
    # A stack: the studio system's layers, the brain as the subject.
    y1 = y0 + 36 + 196 + 48
    body.append(text(0, y1 + 14, "A stack"))
    layers = (("Surfaces", "Wall screen, touch panels, phones, Stream Deck"),
              ("Studio brain", "Model, catalog, and events; serves every screen"),
              ("Home Assistant", "Devices and the automations that must always work"),
              ("Devices", "Lamps, sensors, IR blasters, printers"))
    ly = y1 + 26
    for i, (name, desc) in enumerate(layers):
        sub = i == 1
        sw, off = (2, 1) if sub else (1, 0.5)
        body.append(f'<rect x="{off}" y="{ly + off}" width="{w - 2 * off}" height="{44 - 2 * off}" fill="{SURFACE if sub else GROUND}" stroke="{INK}" stroke-width="{sw}"/>')
        body.append(text(12, ly + 27, name, size=16, weight=500, fill=INK))
        body.append(text(176, ly + 27, desc, fill=MUTED))
        ly += 44 + 8
    write("argument-shapes.svg", svg(w, ly - 8, body))


def states():
    w = 760
    by, bh = 72, 84
    boxes = ((36, 150, "Draft", ["Seen only on the", "dev server"], True),
             (290, 180, "Open", ["Listed under", "Open Questions"], False),
             (610, 150, "Answered", ["Struck through,", "answers inline"], False))
    body = []
    body.append(f'<circle cx="8" cy="{by + bh / 2}" r="6" fill="{INK}"/>')
    body.append(f'<path d="M14 {by + bh / 2 + 0.5}H{36 - 7}" stroke="{INK}"/>')
    body.append(arrow_head(35, by + bh / 2 + 0.5, "right"))
    for x, bw, name, sub, dashed in boxes:
        body += box(x, by, bw, bh, name, sub, stroke=FAINT if dashed else INK, dashed=dashed)
    for (x1, w1, *_), (x2, *_), label in ((boxes[0], boxes[1], "Published"), (boxes[1], boxes[2], "An entry answers it")):
        my = by + bh / 2 + 0.5
        body.append(f'<path d="M{x1 + w1} {my}H{x2 - 7}" stroke="{INK}"/>')
        body.append(arrow_head(x2 - 1, my, "right"))
        body.append(text((x1 + w1 + x2) / 2, my - 8, label, anchor="middle"))
        check("state label", label, x2 - x1 - w1 - 8)
    # Loops over a state: what can happen to it without leaving it.
    for (x, bw, *_), label in ((boxes[1], "Other entries refer to it"), (boxes[2], "Another answer")):
        a, b = x + 40.5, x + bw - 40.5
        body.append(f'<path d="M{a} {by}V{by - 24.5}H{b}V{by - 7}" stroke="{INK}"/>')
        body.append(arrow_head(b, by - 1, "down"))
        body.append(text((a + b) / 2, by - 32, label, anchor="middle"))
    write("question-states.svg", svg(w, by + bh + 1, body))


def sequence():
    w = 760
    lanes = ((120, "Phone"), (380, "Studio brain"), (640, "Wall screen"))
    top, step = 40, 52
    msgs = ((0, 1, "Find “solder”"), (1, 0, "Three matches, in drawer C2·3"), (0, 1, "Show on the wall screen"), (1, 2, "Fly to C2·3"))
    bottom = top + step * (len(msgs) + 1) - 16
    body = []
    for x, name in lanes:
        body.append(f'<rect x="{x - 80 + 0.5}" y="0.5" width="159" height="{top - 1}" fill="{GROUND}" stroke="{INK}"/>')
        body.append(text(x, 26, name, size=16, weight=500, fill=INK, anchor="middle"))
        body.append(f'<path d="M{x + 0.5} {top}V{bottom}" stroke="{EDGE}"/>')
    for k, (a, b, label) in enumerate(msgs):
        y = top + step * (k + 1) + 0.5
        xa, xb = lanes[a][0] + 0.5, lanes[b][0] + 0.5
        d = 1 if xb > xa else -1
        body.append(f'<path d="M{xa} {y}H{xb - 7 * d}" stroke="{INK}"/>')
        body.append(arrow_head(xb - d, y, "right" if d > 0 else "left"))
        body.append(text((xa + xb) / 2, y - 8, label, fill=MUTED, anchor="middle"))
        body.append(text(0, y + 5, f"{k + 1:02d}", mono=True))
    write("find-sequence.svg", svg(w, bottom, body))


def film_formats():
    mm = 2  # px per millimetre
    formats = (("35mm", 36, 24), ("6×7", 70, 56), ("4×5", 127, 102))
    base, gap = 264, 88
    body = []
    x = 0
    for name, fw, fh in formats:
        pw, ph = fw * mm, fh * mm
        top = base - ph
        body.append(f'<rect x="{x + 0.5}" y="{top + 0.5}" width="{pw - 1}" height="{ph - 1}" fill="{SURFACE}" stroke="{INK}"/>')
        # Width: a dimension line above with end ticks, the measure over it.
        dy = top - 16.5
        body.append(f'<path d="M{x + 0.5} {dy}H{x + pw - 0.5}M{x + 0.5} {dy - 5}V{dy + 5}M{x + pw - 0.5} {dy - 5}V{dy + 5}" stroke="{FAINT}"/>')
        body.append(mixed(x + pw / 2, dy - 8, [(str(fw), True), (" mm", False)], anchor="middle"))
        # Height: the same at the right, the measure beside it.
        dx = x + pw + 16.5
        body.append(f'<path d="M{dx} {top + 0.5}V{base - 0.5}M{dx - 5} {top + 0.5}H{dx + 5}M{dx - 5} {base - 0.5}H{dx + 5}" stroke="{FAINT}"/>')
        body.append(mixed(dx + 10, top + ph / 2 + 5, [(str(fh), True), (" mm", False)]))
        body.append(text(x, base + 28, name, size=16, weight=500, fill=INK))
        x += pw + gap
    # A scale bar: 50 mm in steps of 10.
    sy = base + 64.5
    body.append(f'<path d="M0.5 {sy}H{50 * mm + 0.5}" stroke="{INK}"/>')
    for k in range(6):
        tx = k * 10 * mm + 0.5
        body.append(f'<path d="M{tx} {sy - 4}V{sy + 4}" stroke="{INK}"/>')
    body.append(text(0, sy + 24, "0", mono=True))
    body.append(mixed(50 * mm, sy + 24, [("50", True), (" mm", False)], anchor="middle"))
    write("film-formats.svg", svg(760, sy + 30, body))


def site_keys():
    u, gap, kh = 50, 4, 46
    rows = (
        [("esc", 1, True)] + [(c, 1, False) for c in "1234567890-="] + [("delete", 2, False)],
        [("tab", 1.5, False)] + [(c, 1, False) for c in "QWERTYUIOP[]"] + [("\\", 1.5, False)],
        [("caps", 1.75, False)] + [(c, 1, c == "L") for c in "ASDFGHJKL;'"] + [("return", 2.25, True)],
        [("shift", 2.25, True)] + [(c, 1, c == "/") for c in "ZXCVBNM,./"] + [("shift", 1.75, False), ("↑", 1, True)],
        [("control", 1.25, False), ("option", 1.25, False), ("cmd", 1.25, True), ("", 6, False), ("cmd", 1.25, False), ("option", 1, False), ("←", 1, True), ("↓", 1, True), ("→", 1, True)],
    )
    body = []
    for r, row in enumerate(rows):
        x = 5.0
        y = r * u
        assert abs(sum(k[1] for k in row) - 15) < 0.01, r
        for label, size, lit in row:
            kw = size * u - gap
            if lit:
                body.append(f'<rect x="{x + 0.5:.1f}" y="{y + 0.5}" width="{kw - 1:.1f}" height="{kh - 1}" rx="2" fill="{GROUND}" stroke="{INK}"/>')
                body.append(f'<path d="M{x + 2:.1f} {y + kh - 0.5}H{x + kw - 2:.1f}" stroke="{INK}" stroke-width="2"/>')
                shown = "?" if label == "/" else label
                body.append(text(x + kw / 2, y + 28, shown, mono=True, fill=INK, anchor="middle"))
            else:
                body.append(f'<rect x="{x + 0.5:.1f}" y="{y + 0.5}" width="{kw - 1:.1f}" height="{kh - 1}" rx="2" stroke="{EDGE}"/>')
            x += size * u
    write("site-keys.svg", svg(760, 5 * u - gap + 1, body))


def eras():
    w = 760
    start, end = dt.date(2021, 1, 1), dt.date(2027, 1, 1)

    def X(d):
        return w * (d - start).days / (end - start).days

    body = []
    eras = (("Dreaming with One Eye Open", dt.date(2021, 1, 1), dt.date(2022, 1, 1), "start"),
            ("The Flâneur", dt.date(2022, 1, 1), end, "end"))
    for name, a, b, anchor in eras:
        x0, x1 = X(a), X(b)
        body.append(f'<rect x="{x0 + 0.5:.1f}" y="24.5" width="{x1 - x0 - 3:.1f}" height="15" fill="{SURFACE}" stroke="{EDGE}"/>')
        body.append(text(x0 if anchor == "start" else x1 - 2, 14, name, fill=MUTED, anchor=anchor))
    base = 96
    body.append(f'<path d="M0 {base + 0.5}H{w}" stroke="{INK}"/>')
    for year in range(2021, 2028):
        x = min(round(X(dt.date(year, 1, 1))) + 0.5, w - 0.5)
        body.append(f'<path d="M{x} {base}V{base + 6}" stroke="{INK}"/>')
        if year < 2027:
            body.append(text(x - 0.5, base + 24, str(year), mono=True))
    placed = []
    for i, s in enumerate(DISPATCHES):
        x = X(dt.date.fromisoformat(s))
        level = 0
        while any(abs(px - x) < 11 and pl == level for px, pl in placed):
            level += 1
        placed.append((x, level))
        body.append(dot(x, base - 8 - level * 12))
    write("newsletter-eras.svg", svg(w, base + 30, body))


def distribution():
    w, h = 760, 300
    gutter, px0, px1 = 28, 36, w
    top, base = 36, 236
    bins = 20
    width_bin = 25
    old = [0] * bins
    new = [0] * bins
    for i, v in enumerate(LOG):
        b = min(v // width_bin, bins - 1)
        (old if i < 72 else new)[b] += 1
    vmax = math.ceil(max(o + n for o, n in zip(old, new)) / 10) * 10
    slot = (px1 - px0) / bins

    def Y(v):
        return base - (base - top) * v / vmax

    body = []
    for v in range(10, vmax + 1, 10):
        y = round(Y(v)) + 0.5
        body.append(f'<path d="M{px0} {y}H{px1}" stroke="{EDGE}"/>')
        body.append(text(gutter, y + 5, str(v), mono=True, anchor="end"))
    for b in range(bins):
        x = px0 + b * slot + 1
        y = base
        for n, fill in ((old[b], TONE3), (new[b], INK)):
            if n:
                hgt = (base - Y(n))
                body.append(f'<rect x="{x:.1f}" y="{y - hgt:.1f}" width="{slot - 2:.1f}" height="{hgt:.1f}" fill="{fill}"/>')
                y -= hgt + 2
    body.append(f'<path d="M{px0} {base + 0.5}H{px1}" stroke="{INK}"/>')
    for v in range(0, 501, 100):
        x = round(px0 + v / width_bin * slot) + 0.5
        x = min(x, px1 - 0.5)
        body.append(f'<path d="M{x} {base}V{base + 6}" stroke="{INK}"/>')
        body.append(text(x, base + 24, str(v), mono=True, anchor="middle" if v < 500 else "end"))
    body.append(text(px0 + 5 * slot + 8, Y(12), "2019–2024", fill=MUTED))
    body.append(text(px0 + 12 * slot + slot / 2, Y(5) - 8, "2025–2026", fill=INK, anchor="middle"))
    body.append(text(0, 14, "Months"))
    body.append(text(px1, base + 48, "Words in the month", anchor="end"))
    write("log-distribution.svg", svg(w, h, body))


def zones():
    w = 760
    n = 11
    pw = (w - 1) / n
    names = ("0", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X")
    notes = {0: "Black", 3: "Dark detail", 5: "Middle gray", 7: "Light detail", 10: "Paper white"}

    def gray(L):
        Y = ((L + 16) / 116) ** 3 if L > 8 else L / 903.3
        c = 12.92 * Y if Y <= 0.0031308 else 1.055 * Y ** (1 / 2.4) - 0.055
        return round(max(0, min(1, c)) * 255)

    body = []
    for k in range(n):
        v = gray(k * 10)
        # The zones are tones of a print, not of the page: they stay put in
        # dark mode, so 0 and X avoid the palette's own black and white.
        v = min(max(v, 1), 254)
        x = 0.5 + k * pw
        body.append(f'<rect x="{x:.1f}" y="0.5" width="{pw:.1f}" height="64" fill="#{v:02X}{v:02X}{v:02X}"/>')
        body.append(text(x + pw / 2, 90, names[k], fill=INK, anchor="middle"))
        if k in notes:
            anchor = "start" if k == 0 else ("end" if k == n - 1 else "middle")
            tx = x if k == 0 else (x + pw if k == n - 1 else x + pw / 2)
            body.append(text(tx, 112, notes[k], fill=MUTED, anchor=anchor))
    body.append(f'<rect x="0.5" y="0.5" width="{w - 1}" height="64" stroke="{EDGE}"/>')
    write("zones.svg", svg(w, 120, body))


def curve():
    w, h = 760, 300
    px0, px1, top, base = 24, 720, 28, 256

    def D(x):
        return 0.12 + 2.1 / (1 + math.exp(-1.15 * (x - 5)))

    def X(x):
        return px0 + (px1 - px0) * x / 10

    def Y(d):
        return base - (base - top) * d / 2.4

    body = [text(0, 14, "Density")]
    fy = round(Y(0.12)) + 0.5
    body.append(f'<path d="M{px0} {fy}H{px1}" stroke="{EDGE}"/>')
    body.append(text(px1, fy - 8, "Base plus fog", anchor="end"))
    pts = " ".join(f"{X(i / 10):.1f},{Y(D(i / 10)):.1f}" for i in range(0, 101))
    body.append(f'<polyline points="{pts}" stroke="{INK}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>')
    body.append(f'<path d="M{px0 + 0.5} {top}V{base}H{px1}" stroke="{INK}"/>')
    for k in range(1, 11):
        x = round(X(k)) + 0.5
        body.append(f'<path d="M{x} {base}V{base + 6}" stroke="{INK}"/>')
    body.append(text(px1, base + 28, "Exposure, one stop a tick", anchor="end"))
    # Toe: up from the line; straight line: out to the right, under the
    # rising curve; shoulder: down from the flat top.
    x, y = X(2.4), Y(D(2.4))
    body.append(f'<path d="M{x:.1f} {y - 8:.1f}V{y - 40:.1f}" stroke="{FAINT}"/>')
    body.append(text(x, y - 48, "Toe", anchor="middle"))
    x, y = X(5.0), Y(D(5.0))
    body.append(f'<path d="M{x + 8:.1f} {y:.1f}H{x + 64:.1f}" stroke="{FAINT}"/>')
    body.append(text(x + 72, y + 5, "Straight line"))
    x, y = X(8.4), Y(D(8.4))
    body.append(f'<path d="M{x:.1f} {y + 8:.1f}V{y + 36:.1f}" stroke="{FAINT}"/>')
    body.append(text(x, y + 54, "Shoulder", anchor="middle"))
    write("characteristic-curve.svg", svg(w, h, body))


def steps():
    pw, gap = 175, 20
    top, area = 24, 130
    captions = (["A printed sheet, its", "folds still dashed"], ["Fold it in half across", "the long side"],
                ["Fold again at right", "angles"], ["One signature: four", "leaves, eight pages"])
    body = []
    for k in range(4):
        x0 = k * (pw + gap)
        cx, cy = x0 + pw / 2, top + area / 2
        body.append(text(x0, 14, f"{k + 1:02d}", mono=True))
        if k == 0:
            body.append(f'<rect x="{cx - 70 + 0.5}" y="{cy - 50 + 0.5}" width="139" height="99" fill="{GROUND}" stroke="{INK}"/>')
            body.append(f'<path d="M{cx + 0.5} {cy - 50}V{cy + 50}M{cx - 70} {cy + 0.5}H{cx + 70}" stroke="{FAINT}" stroke-dasharray="4 4"/>')
        elif k == 1:
            body.append(f'<rect x="{cx - 35 + 0.5}" y="{cy - 50 + 0.5}" width="69" height="99" fill="{GROUND}" stroke="{INK}"/>')
            body.append(f'<path d="M{cx - 35} {cy + 0.5}H{cx + 35}" stroke="{FAINT}" stroke-dasharray="4 4"/>')
            body.append(f'<path d="M{cx + 62} {cy - 22}Q{cx + 40} {cy - 62} {cx + 8} {cy - 46}" stroke="{INK}"/>')
            body.append(arrow_dir(cx + 6, cy - 45, -1, 0.45))
        elif k == 2:
            body.append(f'<rect x="{cx - 35 + 0.5}" y="{cy - 25 + 0.5}" width="69" height="49" fill="{GROUND}" stroke="{INK}"/>')
            body.append(f'<path d="M{cx + 50} {cy + 46}Q{cx + 62} {cy + 18} {cx + 40} {cy + 12}" stroke="{INK}"/>')
            body.append(arrow_dir(cx + 38, cy + 12, -1, -0.25))
        else:
            body.append(f'<rect x="{cx - 35 + 0.5}" y="{cy - 25 + 0.5}" width="69" height="49" fill="{SURFACE}" stroke="{INK}"/>')
            body.append(f'<path d="M{cx - 34} {cy - 25}V{cy + 25}" stroke="{INK}" stroke-width="2"/>')
            body.append(text(cx - 42, cy + 5, "Spine", anchor="end"))
        for j, line in enumerate(captions[k]):
            body.append(text(x0, top + area + 22 + 20 * j, line, fill=MUTED))
            check("step caption", line, pw)
    write("folding-steps.svg", svg(760, top + area + 46, body))


palette()
lines()
log_words(760, 300, set(range(2019, 2027)), [("Longer months from ", False), ("2024-11", True)], "log-words.svg")
log_words(335, 240, {2019, 2022, 2025}, [("Longer from ", False), ("2024-11", True)], "log-words-narrow.svg")
research_days(760, 196, [(0, "2026-10-01"), (4, "05"), (9, "10"), (14, "15"), (18, "19")], "research-days.svg")
research_days(335, 176, [(0, "2026-10-01"), (9, "10"), (18, "19")], "research-days-narrow.svg")
dispatches()
studio_brain()
grouped_columns()
two_lines()
dumbbell()
log_lengths()
log_difference()
scatter()
calendar()
small_multiples(760, 4, "log-years.svg")
small_multiples(335, 2, "log-years-narrow.svg")
pipeline()
tree()
spans()
shapes()
states()
sequence()
film_formats()
site_keys()
eras()
distribution()
zones()
curve()
steps()
