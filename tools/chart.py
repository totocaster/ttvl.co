#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow>=11"]
# ///
"""Draw a chart in the drawing palette from a CSV file.

    uv run tools/chart.py columns static/visuals/figures/research-kinds.csv
    uv run tools/chart.py line static/visuals/notes/words.csv --width 640

The first column is the x (categories, numbers, or ISO dates such as
2026-10 or 2026-10-06); the columns after it are the series, one or two.
The chart is written beside the CSV under the same name (kinds.csv makes
kinds.svg) for the drawing shortcode, at the design width (760 by
default); render its PNG for feeds and email with tools/drawing-png.py.
docs/figures.md, Charts.

columns  One column per row of the CSV from a 1 px ink baseline. One
         series is ink; two are paired, the first in tone 3 and the second
         in ink, with a key under the axis. A dozen columns or fewer carry
         their values on their caps and no gridlines; more get gridlines
         with their numbers in a gutter.
line     One 2 px line per series across the x, the last in ink and an
         earlier one in tone 3, gridlines at round values, the last point
         a dot with its value, and each line's name at its end when there
         are two. ISO dates make a time axis with a tick each year.
"""
import argparse
import csv
import datetime as dt
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figurelib import EDGE, FAINT, INK, MUTED, TONE3, check, dot, save, svg, swatch_key, text, width  # noqa: E402


def nice_max(v):
    """The round number at or above v that gridlines can step to."""
    if v <= 0:
        return 1
    e = 10 ** math.floor(math.log10(v))
    for m in (1, 2, 2.5, 5, 10):
        if v <= m * e:
            return m * e
    return 10 * e


def number(s):
    return f"{s:g}" if isinstance(s, float) else str(s)


def as_date(s):
    try:
        if len(s) == 7:
            return dt.date.fromisoformat(s + "-01")
        if len(s) == 10:
            return dt.date.fromisoformat(s)
    except ValueError:
        return None
    return None


def columns(xs, series, names, w, h):
    multi = len(series) == 2
    vmax = nice_max(max(max(s) for s in series))
    labeled = len(xs) * len(series) <= 12
    gutter = 0 if labeled else 36
    top = 28
    base = h - (64 if multi else 36)
    slot = (w - gutter) / len(xs)
    col = min(24 if not multi else 20, slot / len(series) - 6)
    body = []

    def Y(v):
        return base - (base - top) * v / vmax

    if not labeled:
        step = vmax / 4
        for i in range(1, 5):
            y = round(Y(step * i)) + 0.5
            body.append(f'<path d="M{gutter} {y}H{w}" stroke="{EDGE}"/>')
            body.append(text(gutter - 8, y + 5, number(step * i), mono=True, anchor="end"))
    fills = (TONE3, INK) if multi else (INK,)
    mono = all(as_date(x) or x.replace(".", "").isdigit() for x in xs)
    for i, x in enumerate(xs):
        cx = gutter + slot * i + slot / 2
        for j, (values, fill) in enumerate(zip(series, fills)):
            v = values[i]
            left = cx - (len(series) * col + (len(series) - 1) * 2) / 2 + j * (col + 2)
            if v:
                body.append(f'<rect x="{left:.1f}" y="{Y(v):.1f}" width="{col:.1f}" height="{base - Y(v):.1f}" fill="{fill}"/>')
                if labeled:
                    body.append(text(left + col / 2, Y(v) - 8, number(v), mono=True, fill=INK, anchor="middle"))
            else:
                body.append(f'<rect x="{left:.1f}" y="{base - 2}" width="{col:.1f}" height="2" fill="{EDGE}"/>')
        body.append(text(cx, base + 24, x, mono=mono, fill=FAINT if mono else MUTED, anchor="middle"))
        check("label", x, slot - 4, mono=mono)
    body.append(f'<path d="M{gutter} {base + 0.5}H{w}" stroke="{INK}"/>')
    if multi:
        body += swatch_key(gutter, base + 56, list(zip(names, fills)))
    return svg(w, h, body)


def line(xs, series, names, w, h):
    dates = [as_date(x) for x in xs]
    timed = all(dates)
    vmax = nice_max(max(max(s) for s in series))
    gutter, top = 36, 16
    base = h - 36
    end_room = 16 + max(width(number(s[-1]), mono=True) for s in series) + (max(width(n) for n in names) + 8 if len(series) == 2 else 0)
    px0, px1 = gutter + 8, w - end_room
    if timed:
        t0, t1 = dates[0], dates[-1]

        def X(i):
            return px0 + (px1 - px0) * (dates[i] - t0).days / max((t1 - t0).days, 1)
    else:
        def X(i):
            return px0 + (px1 - px0) * i / max(len(xs) - 1, 1)

    def Y(v):
        return base - (base - top) * v / vmax

    body = []
    step = vmax / 5 if vmax / 5 == int(vmax / 5) else vmax / 4
    v = step
    while v <= vmax + 1e-9:
        y = round(Y(v)) + 0.5
        body.append(f'<path d="M{px0} {y}H{px1}" stroke="{EDGE}"/>')
        body.append(text(gutter, y + 5, number(v), mono=True, anchor="end"))
        v += step
    body.append(text(gutter, base + 5, "0", mono=True, anchor="end"))
    if timed:
        for year in range(t0.year if t0.month == 1 and t0.day == 1 else t0.year + 1, t1.year + 1):
            x = round(px0 + (px1 - px0) * (dt.date(year, 1, 1) - t0).days / max((t1 - t0).days, 1)) + 0.5
            body.append(f'<path d="M{x} {base}V{base + 6}" stroke="{INK}"/>')
            body.append(text(x - 0.5, base + 24, str(year), mono=True))
    else:
        every = max(1, math.ceil(len(xs) / 8))
        for i in range(0, len(xs), every):
            body.append(text(X(i), base + 24, xs[i], mono=xs[i].replace(".", "").isdigit(), fill=FAINT, anchor="middle"))
    fills = (TONE3, INK) if len(series) == 2 else (INK,)
    for values, fill, name in zip(series, fills, names):
        pts = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(values))
        body.append(f'<polyline points="{pts}" stroke="{fill}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>')
        ex, ey = X(len(values) - 1), Y(values[-1])
        body.append(dot(ex, ey, fill=fill))
        label = number(values[-1])
        body.append(text(ex + 10, ey + 5, label, mono=True, fill=INK))
        if len(series) == 2:
            body.append(text(ex + 18 + width(label, mono=True), ey + 5, name, fill=MUTED))
    body.append(f'<path d="M{px0} {base + 0.5}H{px1}" stroke="{INK}"/>')
    return svg(w, h, body)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("kind", choices=("columns", "line"))
    parser.add_argument("csv", help="the data: x in the first column, one or two series after it")
    parser.add_argument("--width", type=int, default=760, help="design width in px (default 760)")
    parser.add_argument("--height", type=int, default=None, help="height in px (default 240 for columns, 300 for a line)")
    parser.add_argument("--out", help="where to write the SVG (default: beside the CSV)")
    args = parser.parse_args()
    with open(args.csv, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    head, rows = rows[0], [r for r in rows[1:] if r]
    if not 2 <= len(head) <= 3:
        sys.exit("A chart takes an x column and one or two series.")
    xs = [r[0] for r in rows]
    series = [[float(r[i]) if "." in r[i] else int(r[i]) for r in rows] for i in range(1, len(head))]
    names = head[1:]
    h = args.height or (240 if args.kind == "columns" else 300)
    draw = columns if args.kind == "columns" else line
    out = args.out or os.path.splitext(args.csv)[0] + ".svg"
    save(out, draw(xs, series, names, args.width, h))


if __name__ == "__main__":
    main()
