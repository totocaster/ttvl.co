#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow>=11"]
# ///
"""Draw the kit for the Tools I Use page, to scale, in the drawing palette.

    uv run tools/tool-drawings.py

Writes one SVG per figure to static/visuals/tools/, placed on the page
(content/tools.md) with the drawing shortcode. Each figure follows "Sizes
to scale" in docs/figures.md: front views at the makers' published sizes
on surface faces, standing on one line, the width over each object, the
name and its job under it, and a scale bar at the end. Retired things are
the same drawings in tone 4 outlines (ghost). Sizes that aren't published
are marked approximate with a "≈".

An object is a function that draws in millimetres from its bottom-left
corner with a Pen; an item (it) adds its name, job lines, and overhangs;
FIGURES at the end lays items out in rows at one scale per figure. A job
line can be a (text, href) pair, which becomes a link. Labels are
measured with the Plex fonts through tools/figurelib.py.
"""
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figurelib import INK, MUTED, FAINT, TONE4, EDGE, SURFACE, GROUND, text, mixed, width, mixed_width  # noqa: E402

W = 880
TRANSLUCENT = (SURFACE, EDGE)  # white at 5 and 20 % in dark mode: knock out what is behind


def f(v):
    return f'{v:.1f}'.rstrip('0').rstrip('.')


class Pen:
    """Draws in millimetres from an object's bottom-left corner, y up."""

    def __init__(self, s, x0, base):
        self.s, self.x0, self.base, self.out = s, x0, base, []

    def X(self, mm):
        return self.x0 + mm * self.s

    def Y(self, mm):
        return self.base - mm * self.s

    def _shape(self, tag, attrs, fill, stroke):
        st = f' stroke="{stroke}"' if stroke != 'none' else ''
        if fill in TRANSLUCENT:
            self.out.append(f'<{tag} {attrs} fill="{GROUND}"></{tag}>')
        self.out.append(f'<{tag} {attrs} fill="{fill}"{st}></{tag}>')

    def rect(self, x, y, w, h, fill=GROUND, rx=0, stroke=INK):
        r = f' rx="{f(rx * self.s)}"' if rx else ''
        self._shape('rect', f'x="{f(self.X(x))}" y="{f(self.Y(y + h))}" width="{f(w * self.s)}" height="{f(h * self.s)}"{r}', fill, stroke)

    def circle(self, cx, cy, r, fill=GROUND, stroke=INK):
        self._shape('circle', f'cx="{f(self.X(cx))}" cy="{f(self.Y(cy))}" r="{f(r * self.s)}"', fill, stroke)

    def line(self, x1, y1, x2, y2, stroke=INK):
        self.out.append(f'<path d="M{f(self.X(x1))} {f(self.Y(y1))}L{f(self.X(x2))} {f(self.Y(y2))}" stroke="{stroke}"></path>')

    def poly(self, pts, fill=GROUND, stroke=INK, radii=None):
        """A closed polygon, each corner rounded by its radius in mm."""
        n = len(pts)
        radii = radii or [0] * n
        P = [(self.X(x), self.Y(y)) for x, y in pts]
        d = []
        for i in range(n):
            (px, py), (cx, cy), (nx, ny) = P[i - 1], P[i], P[(i + 1) % n]
            r = radii[i] * self.s
            if not r:
                d.append(('M' if not d else 'L') + f'{f(cx)} {f(cy)}')
                continue
            a = math.hypot(px - cx, py - cy) or 1
            b = math.hypot(nx - cx, ny - cy) or 1
            r = min(r, a / 2, b / 2)
            ax, ay = cx + (px - cx) * r / a, cy + (py - cy) * r / a
            bx, by = cx + (nx - cx) * r / b, cy + (ny - cy) * r / b
            d.append(('M' if not d else 'L') + f'{f(ax)} {f(ay)}Q{f(cx)} {f(cy)} {f(bx)} {f(by)}')
        self._shape('path', f'd="{"".join(d)}Z"', fill, stroke)

    def knurl(self, x, y, w, h, step=2.0):
        k = x + step
        while k < x + w - step / 2:
            self.line(k, y + 0.6, k, y + h - 0.6, TONE4)
            k += step

    def ticks(self, cx, cy, r0, r1, n=36):
        for i in range(n):
            a = 2 * math.pi * i / n
            self.line(cx + r0 * math.cos(a), cy + r0 * math.sin(a), cx + r1 * math.cos(a), cy + r1 * math.sin(a), TONE4)

    def glass(self, cx, cy, r):
        self.circle(cx, cy, r, INK)
        self.circle(cx - r * .38, cy + r * .38, r * .16, GROUND, 'none')


# ---------------------------------------------------------------- objects ---
# Each: (draw, width mm, height mm, left overhang mm, right overhang mm)

def lugs(p, w, y):
    p.circle(-1.4, y, 2.2)
    p.circle(w + 1.4, y, 2.2)


def m11p(p):
    Wd, H = 139, 80.3
    lugs(p, Wd, 49.3)
    p.rect(15, H - 1, 17, 6.3, rx=1)
    p.knurl(15, H, 17, 5.3, 2.2)
    p.rect(34.7, H - 1, 22, 5.2, rx=1)
    p.knurl(34.7, H, 22, 4.2, 2.2)
    p.rect(0, 0, Wd, H, rx=5)
    p.rect(0, 4, Wd, 54, EDGE)
    p.rect(40.1, 63.6, 10.7, 7.1, INK, rx=1)
    p.rect(100.6, 57.7, 29.7, 20.2, rx=1.5)
    p.rect(102.4, 59.5, 26.1, 16.6, INK, rx=1)
    p.circle(60.9, 75.6, 1.6, INK)
    p.circle(78.5, 68.3, 3.4)
    p.line(76.4, 66.2, 80.6, 70.4)
    p.circle(46.4, 34, 3.6)
    p.circle(112, 34, 3)
    cx, cy = 78.9, 34
    p.circle(cx, cy, 29.3)
    p.ticks(cx, cy, 27.4, 29.3, 48)
    p.circle(cx, cy, 27.4)
    p.circle(cx, cy, 24.6)
    p.circle(cx, cy, 21.2, SURFACE)
    p.glass(cx, cy, 15.5)


def q3(p):
    Wd = 130
    lugs(p, Wd, 64.6)
    p.rect(15.9, 74.6, 16.2, 6.7, rx=1)
    p.knurl(15.9, 75.6, 16.2, 5.7, 2.2)
    p.rect(33.4, 74.6, 21.4, 6.2, rx=1)
    p.knurl(33.4, 75.6, 21.4, 5.2, 2.2)
    p.poly([(0, 0), (Wd, 0), (Wd, 80.3), (55.5, 80.3), (55.5, 75.6), (0, 75.6)], radii=[4, 4, 4, 1.5, 1, 4])
    p.rect(0, 3.4, Wd, 66.5, EDGE)
    p.rect(42.6, 65.9, 4.7, 2.6, INK, rx=.6)
    p.circle(109.1, 69.9, 4.7, INK)
    cx, cy = 77.8, 36.4
    p.circle(cx, cy, 35)
    p.ticks(cx, cy, 32.6, 35, 60)
    p.circle(cx, cy, 32.6)
    p.circle(cx, cy, 29.6)
    p.circle(cx, cy, 21.4, SURFACE)
    p.circle(cx, cy, 16.2)
    p.glass(cx, cy, 11.7)


def bigmini(p):
    p.rect(20.8, 62, 10.7, 2.4, rx=1.2)
    p.rect(35.7, 62, 7.6, 1.6, rx=.8)
    p.rect(0, 0, 115, 63, rx=6)
    p.line(3, 59.6, 112, 59.6)
    p.rect(38.8, 42.7, 48.1, 12.8, INK, rx=6.4)
    p.rect(58.8, 45.4, 12.7, 7.4, EDGE, rx=1)
    p.rect(90, 45.9, 20.7, 10.1, rx=1)
    for x in (94.5, 98.5, 102.5, 106.5):
        p.line(x, 47, x, 55, TONE4)
    p.rect(9.7, 7.8, 26.9, 34.4, EDGE, rx=4)
    cx, cy = 64.2, 25.7
    p.circle(cx, cy, 18.2)
    p.circle(cx, cy, 15.4)
    p.circle(cx, cy, 12, SURFACE)
    p.glass(cx, cy, 8)


def g2(p):
    lugs(p, 139, 66)
    p.rect(10, 79, 15, 4.6, rx=1)
    p.knurl(10, 80, 15, 3.6, 2)
    p.rect(28, 79, 13, 3.6, rx=1)
    p.rect(0, 0, 139, 80, rx=5)
    p.rect(0, 0, 24, 58, EDGE, rx=4)
    p.line(24, 58, 139, 58)
    p.rect(44, 61, 23, 12, rx=1.5)
    p.rect(46, 63, 9, 8, INK, rx=1)
    p.rect(57.5, 63, 7.5, 8, INK, rx=1)
    p.rect(84, 61, 30, 12, rx=1.5)
    p.rect(86, 63, 12, 8, INK, rx=1)
    p.rect(100, 63, 12, 8, INK, rx=1)
    p.rect(117, 63.5, 6.5, 7, INK, rx=1)
    p.circle(30, 49, 4.5)
    p.circle(30, 49, 2.8)
    p.circle(103, 31, 3)
    cx, cy = 59, 29
    p.circle(cx, cy, 28)
    p.circle(cx, cy, 25)
    p.circle(cx, cy, 18.5, SURFACE)
    p.circle(cx, cy, 13)
    p.glass(cx, cy, 8.5)
    p.circle(cx, cy + 26.5, .8, INK)


def gr4(p):
    p.rect(14.1, 60, 13.8, 2.8, rx=1)
    p.knurl(14.1, 61.1, 13.8, 1.7, 1.6)
    p.rect(0, 0, 109.4, 61.1, rx=4)
    p.rect(0, 2, 36.5, 55, EDGE, rx=3)
    p.circle(40, 51.8, 1.5, INK)
    cx, cy = 69.3, 29.5
    p.circle(cx, cy, 26.5)
    p.circle(cx, cy, 23.5)
    p.rect(cx - 9.5, cy - 9.5, 19, 19, SURFACE, rx=3)
    p.glass(cx, cy, 6.8)


def tp7(p):
    k = 13
    p.rect(8.3, k + 94, 1.6, 7)
    p.rect(-3.2, k + 31.7, 2.7, 51, rx=1.3)
    p.rect(52.5, 0, 14, k + 1, rx=1)
    p.knurl(52.5, 0, 14, k, 1.8)
    p.rect(0, k, 68, 96, rx=3.5)
    for i, x in enumerate((0, 17, 34)):
        p.rect(x, k, 17, 22.4, rx=1)
    p.circle(8.5, k + 11.2, 1.7, INK)
    p.poly([(23.8, k + 9.2), (23.8, k + 13.2), (27.4, k + 11.2)], INK, 'none')
    p.rect(41, k + 9.7, 3, 3, INK)
    p.rect(51, k, 17, 22.4, rx=1)
    for x in (56.5, 62.5):
        p.line(x, k + 3, x, k + 19.4, TONE4)
    cx, cy = 29.4, k + 59.5
    p.circle(cx, cy, 26, SURFACE)
    p.line(cx - 18.4, cy - 18.4, cx + 18.4, cy + 18.4, TONE4)
    p.circle(cx, cy, 8.3)
    for a in (90, 210, 330):
        r = math.radians(a)
        p.circle(cx + 4.4 * math.cos(r), cy + 4.4 * math.sin(r), .7, INK, 'none')
    p.rect(50, k + 86, 15, 7.5, INK, rx=1)
    p.circle(23, k + 91.5, .6, INK, 'none')
    p.circle(33.5, k + 91.5, .6, INK, 'none')
    p.circle(8, k + 29, 2.6)
    p.circle(56.3, k + 28, 2.6)
    p.circle(61.8, k + 33.3, 2.6)


RINGS = (25, 44, 63, 113, 132, 151)


def notebook(p):
    for y in RINGS:
        p.circle(0, y, 5, 'none')
    p.rect(0, 0, 100, 176, SURFACE, rx=2)


def leaf(p):
    p.rect(0, 0, 95, 170)
    for y in RINGS:
        p.circle(5.5, y - 3, 2.6)
    y = 12
    while y < 158:
        p.line(13, y, 89, y, TONE4)
        y += 6


def lens_m50(p):
    D = 58.6
    p.rect(D / 2 - 22, 0, 44, 2.5)
    p.rect(0, 2.5, D, 13)
    p.knurl(0, 2.5, D, 13, 2.2)
    p.rect(2.55, 15.5, 53.5, 21)
    p.circle(D / 2, 24, .9, INK, 'none')
    p.rect(1.8, 36.5, 55, 8)
    p.knurl(1.8, 36.5, 55, 8, 2.2)
    p.rect(1.55, 44.5, 55.5, 14.8, rx=1)
    p.line(1.55, 55.3, 57.05, 55.3)


def lens_m35(p):
    D = 56
    p.rect(D / 2 - 22, 0, 44, 2.5)
    p.rect(0, 2.5, D, 11)
    p.knurl(0, 2.5, D, 11, 2.2)
    p.rect(1.5, 13.5, 53, 15)
    p.circle(D / 2, 21, .9, INK, 'none')
    p.rect(1, 28.5, 54, 7)
    p.knurl(1, 28.5, 54, 7, 2.2)
    p.rect(1.5, 35.5, 53, 10.5, rx=1)


def g_lens(D, L, kind=None):
    def draw(p):
        p.rect(D / 2 - D * .39, 0, D * .78, 2.5)
        if kind == 'hologon':
            p.poly([(D / 2 - 12, L - .5), (D / 2, L + 6), (D / 2 + 12, L - .5)], INK, INK, [0, 10, 0])
        if kind == 'hologon':
            p.rect(0, 2.5, D, L - 2.5, rx=1)
        else:
            p.rect(4, L - 2, D - 8, 2, rx=.5)
            p.rect(0, 2.5, D, L - 4.5, rx=1)
        if L > 14:
            p.line(0, L - 7, D, L - 7)
        p.circle(D / 2, 5.5 if L > 14 else 6.75, .9, INK, 'none')
        if kind == 'zoom':
            p.rect(0, 22, D, 16)
            p.knurl(0, 22, D, 16, 2.2)
        if kind == 'tele':
            p.line(0, 24, D, 24)
    return draw


def canister(p):
    p.rect(10, 0, 5, 2.4)
    p.rect(8.5, 41.6, 8, 5.6, rx=.8)
    p.line(10.5, 45.2, 14.5, 45.2)
    p.poly([(27, 6.5), (49, 6.5), (53, 6.5), (53, 18), (53, 21), (41, 21), (37, 21.5), (36, 26), (36, 37.5), (27, 37.5)],
           radii=[0, 0, 3, 0, 3, 0, 3, 0, 0, 0])
    x = 29
    while x < 50:
        p.rect(x, 8, 2, 1.4, INK, stroke='none')
        x += 4.75
    for x in (29, 33.5):
        p.rect(x, 35, 2, 1.4, INK, stroke='none')
    p.rect(23.5, 5.5, 4, 33, INK, rx=1)
    p.rect(0, 2, 25, 40, rx=1.5)
    p.line(0, 5.2, 25, 5.2)
    p.line(0, 38.8, 25, 38.8)
    p.rect(0, 14, 25, 16, SURFACE)


def jobo(p):
    # the lift lever, behind everything
    p.poly([(150, 300), (158, 292), (318, 440), (310, 448)])
    p.poly([(282, 414), (296, 400), (346, 446), (332, 460)], EDGE, radii=[3, 3, 3, 3])
    p.rect(165, 0, 490, 135, rx=4)
    p.line(165, 118, 655, 118)
    p.line(300, 146, 640, 146, TONE4)
    p.rect(312, 172, 22, 64, rx=3)
    p.rect(330, 150, 260, 108, rx=8)
    p.rect(365, 128, 28, 152, EDGE, rx=6)
    p.rect(527, 128, 28, 152, EDGE, rx=6)
    p.rect(0, 0, 178, 255, rx=4)
    p.rect(16, 16, 146, 152, SURFACE, rx=3)
    p.circle(56, 124, 16)
    p.circle(122, 124, 16)
    p.circle(56, 62, 16, INK)
    p.poly([(0, 255), (205, 255), (205, 335), (160, 400), (0, 400)], radii=[0, 4, 4, 6, 6])
    p.rect(14, 352, 104, 36, SURFACE, rx=4)
    p.rect(30, 274, 104, 26, EDGE, rx=4)
    for x in (172, 182, 192):
        p.line(x, 270, x, 330, TONE4)


def therm_panel(p):
    p.rect(0, 0, 250, 82, SURFACE, rx=2)
    for i in range(4):
        x = 9 + i * 59.5
        p.rect(x, 46, 54, 28)
        p.rect(x + 3, 9, 48, 30, EDGE, rx=2)
        p.rect(x + 8, 14, 38, 20, rx=1)


def rig(p):
    ax = 205
    p.rect(0, 0, 360, 20, SURFACE, rx=2)
    p.rect(22, 20, 28, 550)
    p.rect(17, 566, 38, 7, rx=1.5)
    p.rect(ax - 82, 20, 164, 42, rx=3)
    for x in range(ax - 66, ax + 70, 14):
        p.line(x, 26, x, 34, TONE4)
    p.rect(ax - 64, 62, 128, 13, SURFACE, rx=2)
    p.rect(ax - 98, 75, 196, 10, rx=2)
    p.rect(ax - 120, 78.5, 240, 3, INK, stroke='none')
    p.rect(14, 438, 44, 44, rx=2)
    p.rect(2, 452, 12, 16, rx=2)
    p.rect(58, 450, ax + 36 - 58, 18)
    p.rect(ax + 36, 250, 14, 230)
    p.rect(ax + 50, 300, 10, 14, rx=2)
    p.rect(ax - 17, 228, 34, 36, rx=2)
    p.line(ax - 17, 236, ax + 17, 236)
    p.rect(ax - 40, 264, 80, 12)
    pts_l, pts_r = [], []
    y = 276
    i = 0
    while y <= 346:
        dx = 36 if i % 2 == 0 else 30
        pts_l.append((ax - dx, y))
        pts_r.append((ax + dx, y))
        y += 7
        i += 1
    p.poly(pts_r + list(reversed(pts_l)))
    for (x1, y1), (x2, y2) in zip(pts_l, pts_r):
        p.line(x1, y1, x2, y2, TONE4)
    p.rect(ax - 40, 346, 80, 12)
    p.rect(ax - 50, 358, 98, 74, rx=5)
    p.rect(ax + 26, 358, 22, 74, EDGE, rx=4)
    p.rect(ax - 44, 432, 64, 5, INK, rx=1)
    p.rect(ax - 14, 437, 26, 14, rx=3)


def rig_named(p):
    rig(p)
    lx = 350
    for pts, label in (
        ([(287, 40), (338, 40), (338, 70), (345, 70)], 'Negative Supply light'),
        ([(269, 68), (330, 68), (330, 110), (345, 110)], 'VNS adapter'),
        ([(280, 85), (280, 150), (345, 150)], 'Valoi easy120 carrier'),
        ([(222, 246), (345, 246)], 'Apo-Rodagon'),
        ([(256, 311), (345, 311)], 'Leica Bellows-R'),
        ([(256, 400), (345, 400)], 'Panasonic Lumix S5'),
    ):
        d = 'M' + 'L'.join(f'{f(p.X(x))} {f(p.Y(y) + .5)}' for x, y in pts)
        p.out.append(f'<path d="{d}" stroke="{FAINT}"></path>')
        p.out.append(text(p.X(lx), p.Y(pts[-1][1]) + 5, label, size=16, weight=500, fill=INK))


def studio_display(p):
    Wd, ph, sh = 623, 362.7, 115.3
    p.rect(Wd / 2 - 95, 0, 190, 8, rx=3)
    p.rect(Wd / 2 - 82, 8, 164, sh, SURFACE)
    p.rect(0, sh, Wd, ph, rx=6)
    p.rect(12, sh + 12, Wd - 24, ph - 24, SURFACE, rx=2)
    p.circle(Wd / 2, sh + ph - 6, 1.6, INK, 'none')


def macbook(p):
    Wd = 312.6
    p.rect(5, 15.5, Wd - 10, 205, rx=7)
    p.rect(11, 22, Wd - 22, 192, SURFACE, rx=3)
    p.rect(Wd / 2 - 16, 207, 32, 7, INK, rx=2, stroke='none')
    p.rect(0, 0, Wd, 15.5, rx=3)
    p.line(Wd / 2 - 30, 15.5, Wd / 2 + 30, 15.5, TONE4)


def macmini(p):
    p.rect(0, 0, 127, 50, rx=7)
    for x in (16, 29):
        p.rect(x, 23.7, 8.4, 2.6, INK, rx=1.3)
    p.circle(43, 25, 1.8, INK)
    p.circle(113, 25, .9, INK, 'none')


def iphone(p):
    p.rect(0, 0, 71.5, 146.7, rx=9)
    p.circle(13.5, 132.5, 6.5, SURFACE)
    p.glass(13.5, 132.5, 4.4)
    p.circle(25.5, 134.5, 1.8)


def streamdeck(p):
    p.rect(0, 0, 118, 84, SURFACE, rx=6)
    for r in range(3):
        for c in range(5):
            p.rect(12.75 + c * 19.5, 15 + r * 19.5, 14.5, 14.5, INK, rx=2)


def a3_sheet(p):
    p.rect(0, 0, 297, 420, SURFACE)
    for x, y, w, h in ((40, 300, 80, 50), (170, 300, 90, 50), (100, 170, 100, 60), (40, 60, 60, 40)):
        p.rect(x, y, w, h, 'none', rx=4)
    p.line(120, 325, 166, 325)
    p.poly([(160, 320), (168, 325), (160, 330)], INK, 'none')
    p.line(80, 300, 130, 234)
    p.line(215, 300, 170, 234)
    p.line(150, 170, 90, 104)
    p.circle(220, 90, 30, 'none')
    p.line(110, 80, 186, 88)


def sharpie(p):
    p.rect(3, 0, 7, 4, rx=1)
    p.rect(0.5, 4, 12, 80, rx=2)
    p.rect(0.5, 40, 12, 30, SURFACE)
    p.rect(0, 84, 13, 53, INK, rx=2)
    p.rect(9.5, 92, 2.5, 38, GROUND, rx=1.2, stroke='none')


def clapton(p):
    p.rect(0, 0, 300, 384, SURFACE, rx=10)
    p.rect(0, 0, 300, 118, EDGE, rx=10)
    p.poly([(186, 384), (300, 384), (300, 214)], EDGE, INK, [0, 8, 0])
    p.rect(-6, 378, 312, 58, rx=26)
    p.line(10, 407, 290, 407, TONE4)
    p.rect(176, 34, 52, 15, INK, rx=1.5)
    p.rect(137.5, 8, 25, 440, INK, rx=2)
    p.rect(130, 392, 40, 28, rx=3)
    p.rect(137, 399, 26, 4, INK, stroke='none')
    p.rect(137, 409, 26, 4, INK, stroke='none')


def cheyenne(p):
    p.rect(185, 18, 20, 13, INK, rx=6)
    p.rect(0, 0, 195, 85, SURFACE, rx=9)
    p.rect(3, 58, 189, 7, INK, rx=2)
    for x in (82, 95):
        p.rect(x, 37, 8, 21, INK, rx=4)
        p.circle(x + 4, 43, 1.7, GROUND, 'none')
    p.rect(20, 11, 32, 10, INK, rx=1)


def blair(p):
    p.rect(-7, 75, 14, 6, rx=3)
    p.rect(0, 0, 125, 85, rx=4)
    p.poly([(0, 0), (44, 0), (0, 32)], EDGE, 'none', [4, 0, 0])
    p.line(0, 32, 44, 0, INK)
    p.poly([(72, 81), (125, 81), (125, 37)], EDGE, 'none')
    p.line(72, 81, 125, 37, INK)
    p.rect(2, 78, 121, 5, INK, rx=2)
    p.rect(80, 62, 28, 9, INK, rx=1)


def gshock(p):
    b = 26
    p.rect(11.4, 0, 20, b + 4, EDGE, rx=2)
    for y in (6, 12, 18):
        p.circle(21.4, y, 1.3)
    p.rect(11.4, b + 44.9, 20, 26, EDGE, rx=2)
    p.rect(10.2, b + 62, 22.4, 4.5, rx=1)
    for y in (12, 31):
        p.rect(-2.4, b + y, 3, 6, rx=1)
        p.rect(42.2, b + y, 3, 6, rx=1)
    p.rect(0, b, 42.8, 48.9, rx=8)
    p.rect(4.2, b + 5, 34.4, 38.9, SURFACE, rx=5)
    p.rect(8.4, b + 14, 26, 17, EDGE, rx=1.5)
    p.out.append(text(p.X(21.4), p.Y(b + 19.2), '10:58', size=14, fill=INK, anchor='middle', mono=True))


def whoop(p):
    p.rect(0, 0, 24, 112, EDGE, rx=2)
    for y in range(8, 108, 6):
        p.line(2, y, 22, y, TONE4)
    p.rect(-1.5, 37, 27, 38, rx=7)
    p.rect(2.5, 41, 19, 30, SURFACE, rx=4)


# ------------------------------------------------------------------ layout --

def words(s):
    """Sans words with Mono digits, per the figures guide."""
    return [(t, bool(re.match(r'\d', t))) for t in re.split(r'(\d[\d.:–/]*)', s) if t]


HREF = ''  # set to '#' for mockups whose links go nowhere
OUT = None


def job_line(x, y, j, anchor='start'):
    if isinstance(j, str):
        return mixed(x, y, words(j), fill=MUTED, anchor=anchor)
    t, href = j
    line = mixed(x, y, words(t), fill=MUTED, anchor=anchor).replace('<text ', '<text text-decoration="underline" ', 1)
    return f'<a href="{HREF or href}">{line}</a>'


def row(items, s, y_top, gap=36, rule=True):
    """One bottom-aligned row. items: dict(draw, w, h, l, r, name, job, dim). Returns (svg parts, bottom y)."""
    slots = []
    for it in items:
        wpx = (it['l'] + it['w'] + it['r']) * s
        jobs = it.get('job', [])
        tw = max([width(it['name'], weight=500, size=16)] + [mixed_width(words(j if isinstance(j, str) else j[0])) for j in jobs])
        slots.append(max(wpx, tw))
    total = sum(slots) + gap * (len(items) - 1)
    if total > W:
        print(f'  ! row is {total:.0f} px wide at {s} px/mm')
    hmax = max((it['h'] + it.get('top', 0)) * s for it in items)
    base = y_top + 42 + hmax
    out = []
    if rule:
        out.append(f'<path d="M0 {f(base + .5)}H{f(min(W, total + 12))}" stroke="{EDGE}"></path>')
    x = 0
    for it, sw in zip(items, slots):
        ox = x + it['l'] * s
        p = Pen(s, ox, base)
        it['draw'](p)
        out += p.out
        wpx = it['w'] * s
        top = base - (it['h'] + it.get('top', 0)) * s
        dy = top - 14.5
        x0, x1 = ox + .5, ox + wpx - .5
        out.append(f'<path d="M{f(x0)} {f(dy)}H{f(x1)}M{f(x0)} {f(dy - 4)}V{f(dy + 4)}M{f(x1)} {f(dy - 4)}V{f(dy + 4)}" stroke="{FAINT}"></path>')
        out.append(mixed(ox + wpx / 2, dy - 7, [(it.get('dim', f(it['w'])), True), (' mm', False)], anchor='middle'))
        ny = base + 28
        out.append(text(x, ny, it['name'], size=16, weight=500, fill=INK))
        for k, j in enumerate(it.get('job', [])):
            out.append(job_line(x, ny + 20 + 20 * k, j))
        x += sw + gap
    lines = max(len(it.get('job', [])) for it in items)
    return out, base + 28 + 20 * lines + 8


def scale_bar(s, y):
    for mm in (10, 20, 50, 100, 200):
        if mm * s >= 80:
            break
    step = mm / 5
    out = [f'<path d="M0.5 {f(y + .5)}H{f(mm * s + .5)}" stroke="{INK}"></path>']
    for k in range(6):
        tx = k * step * s + .5
        out.append(f'<path d="M{f(tx)} {f(y - 3.5)}V{f(y + 4.5)}" stroke="{INK}"></path>')
    out.append(text(0, y + 24, '0', mono=True))
    out.append(mixed(mm * s, y + 24, [(str(mm), True), (' mm', False)], anchor='middle'))
    return out, y + 30


def drawing(name, rows, s, alt, gap=36):
    parts, y = [], 0
    for items in rows:
        out, y = row(items, s, y, gap)
        parts += out
        y += 12
    bar, y = scale_bar(s, y + 14)
    parts += bar
    h = math.ceil(y + 2)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" fill="none" '
           f'role="img" aria-label="{alt}">\n' + '\n'.join(parts) + '\n</svg>\n')
    if OUT:
        with open(os.path.join(OUT, name + '.svg'), 'w') as fh:
            fh.write(svg)
        print(f'{name}: {W} x {h}')
    return svg


def it(draw, w, h, name, job=(), l=0, r=0, dim=None, top=0):
    return dict(draw=draw, w=w, h=h, l=l, r=r, name=name, job=list(job), dim=dim or f(w), top=top)



# A thing's own color, shown as itself (docs/figures.md): literals outside the palette, unthemed.
OWN_BLACK, OWN_GRAY, OWN_ORANGE = '#1A1A1A', '#8C8C8C', '#E8712D'


def ghost(draw):
    """A retired thing: the same drawing in tone 4 outlines on ground faces."""
    def g(p):
        q = Pen(p.s, p.x0, p.base)
        draw(q)
        for e in q.out:
            e = e.replace(f'fill="{EDGE}"', f'fill="{GROUND}"').replace(f'fill="{SURFACE}"', f'fill="{GROUND}"')
            e = e.replace(f'fill="{INK}"', f'fill="{EDGE}"').replace(f'stroke="{INK}"', f'stroke="{TONE4}"')
            p.out.append(e)
    return g


def rings(p, cx, cy, radii, glass):
    for i, r in enumerate(radii):
        p.circle(cx, cy, r, SURFACE if i == len(radii) - 1 else GROUND)
    p.glass(cx, cy, glass)


# ------------------------------------------------------------ new objects ---

def iphone17pro(p):
    W, H = 71.9, 150
    p.rect(0, 0, W, H, rx=10)
    p.rect(4.5, 5, W - 9, 95, SURFACE, rx=7)
    p.poly([(0, 104), (W, 104), (W, H), (0, H)], SURFACE, INK, [0, 0, 10, 10])
    for cx, cy in ((14, 137), (14, 116), (33, 126.5)):
        p.circle(cx, cy, 8.2)
        p.glass(cx, cy, 5.6)
    p.circle(60, 137, 3.4)
    p.circle(60, 116, 2.6, INK)


def streamdeck_xl(p):
    W, H = 205, 147
    p.rect(0, 0, W, H, SURFACE, rx=8)
    k, g = 15, 4.2
    x0 = (W - (9 * k + 8 * g)) / 2
    for r in range(4):
        for c in range(9):
            p.rect(x0 + c * (k + g), H - 12 - k - r * (k + g), k, k, INK, rx=2)
    p.rect((W - 161) / 2, 42, 161, 14, INK, rx=2)
    for i in range(6):
        cx = x0 + 8.5 + i * (9 * k + 8 * g - 17) / 5
        p.circle(cx, 20, 9)
        p.circle(cx, 20, 6.5)


def bound_notebook(p):
    p.rect(0, 0, 112, 182, rx=1.5)
    p.rect(0, 0, 9, 182, SURFACE)
    p.line(9, 0, 9, 182)
    for y in (30, 70, 112, 152):
        p.line(3.5, y, 5.5, y, TONE4)


def s5(p):
    p.poly([(43, 71), (91, 71), (85, 97.1), (49, 97.1)], radii=[0, 0, 4, 4])
    p.rect(8, 70, 18, 5.5, rx=1)
    p.knurl(8, 71, 18, 4.5, 1.8)
    p.rect(101, 70, 23, 8, rx=1.5)
    p.knurl(101, 71, 23, 7, 1.8)
    p.rect(0, 0, 132.6, 72, rx=6)
    p.rect(0, 2, 31, 68, EDGE, rx=5)
    p.circle(35, 62, 1.5, INK)
    p.circle(107, 24, 4)
    cx, cy = 71, 39.5
    p.circle(cx, cy, 38.7)
    p.ticks(cx, cy, 35.6, 38.7, 60)
    rings(p, cx, cy, (35.6, 30, 24), 15)


def lumix_lens(D, L, kind):
    def draw(p):
        p.rect(D / 2 - D * .39, 0, D * .78, 2.5)
        p.rect(0, 2.5, D, L - 4.5, rx=1.5)
        p.rect(4, L - 2, D - 8, 2, rx=.5)
        if kind == 'zoom':
            p.rect(0, 30, D, 24)
            p.knurl(0, 30, D, 24, 2.2)
            p.rect(0, 60, D, 12)
            p.knurl(0, 60, D, 12, 1.6)
        else:
            p.rect(0, 42, D, 26)
            p.knurl(0, 42, D, 26, 2.2)
        p.circle(D / 2, 7, .9, INK, 'none')
    return draw


def waai(p, band):
    # One FriXion Waai, upright: tip, grip, barrel, ink band, cap end with clip, plunger.
    p.poly([(4, 0), (7, 0), (10.5, 8), (0.5, 8)], radii=[.5, .5, 0, 0])
    p.rect(.5, 8, 10, 38, SURFACE, rx=1)
    p.rect(0, 46, 11, 72, rx=1)
    p.rect(0, 118, 11, 4, band, stroke=INK)
    p.rect(0, 122, 11, 13, rx=1)
    p.rect(9, 86, 3.2, 47, rx=1.2)
    p.rect(2.5, 135, 6, 7, rx=1.5)


def waai_three(p):
    for i, band in enumerate((OWN_BLACK, OWN_GRAY, OWN_ORANGE)):
        q = Pen(p.s, p.X(i * 18), p.base)
        waai(q, band)
        p.out += q.out


# retired, drawn in outline

def hexar(p):
    p.rect(14, 79, 18, 5.5, rx=1)
    p.rect(0, 0, 139.5, 80, rx=4)
    p.rect(0, 4, 139.5, 53, EDGE)
    p.rect(30, 63, 11, 8, INK, rx=1)
    p.rect(66, 64, 9, 7, INK, rx=1)
    p.rect(98, 59, 30, 17, INK, rx=1.5)
    rings(p, 70, 33, (25, 22, 17), 11)


def klasse(p):
    p.rect(17, 63, 14, 3, rx=1)
    p.rect(0, 0, 123, 64, rx=5)
    p.rect(0, 3, 26, 52, EDGE, rx=3)
    p.rect(97, 3, 26, 40, EDGE, rx=3)
    p.rect(42, 52, 9, 5.5, INK, rx=1)
    p.circle(62, 54, 2.2, INK)
    p.rect(71, 51, 9, 6.5, INK, rx=1)
    p.rect(90, 47, 23, 11, rx=1)
    rings(p, 51, 26, (21, 18, 13), 8)
    p.circle(80, 13, 6.5)


def q2(p):
    q3(p)


def rz67(p):
    p.circle(-4, 34, 11)
    p.circle(112, 34, 11)
    p.rect(4, 100, 100, 33.4, rx=2)
    p.line(4, 116, 104, 116, TONE4)
    p.rect(0, 0, 108, 100, rx=3)
    p.rect(12, 8, 84, 84, rx=2)
    rings(p, 54, 50, (40, 35, 27), 16)


def h203(p):
    p.rect(3, 88, 85, 22, rx=2)
    p.rect(0, 0, 91, 88, rx=4)
    p.rect(-6, 50, 6, 12, rx=1)
    rings(p, 45.5, 45, (34, 30, 22), 13)


def shenhao(p):
    p.circle(-6, 60, 7)
    p.circle(266, 60, 7)
    p.rect(0, 0, 260, 200, rx=4)
    p.rect(14, 14, 232, 172, SURFACE, rx=2)
    p.rect(70, 18, 120, 164, rx=3)
    p.rect(90, 60, 80, 80, rx=2)
    rings(p, 130, 100, (32, 27, 20), 13)


def horseman(p):
    p.rect(-14, 0, 200, 10, rx=2)
    p.rect(0, 10, 172, 162, rx=6)
    p.rect(12, 22, 148, 138, SURFACE, rx=3)
    p.rect(30, 14, 112, 128, rx=3)
    p.rect(46, 40, 80, 80, rx=2)
    rings(p, 86, 80, (30, 25, 19), 12)


# ---------------------------------------------------------------- items ---
L = {
    'tp7': it(tp7, 68, 109, 'TP-7', ['Teenage Engineering,', 'for voice notes'], l=3.2, dim='68', top=5),
    'notebook': it(notebook, 100, 176, 'Unbound notebook', ['Bible size, loose covers'], l=5, dim='100'),
    'iphone': it(iphone17pro, 71.9, 150, 'iPhone 17 Pro', ['Cosmic orange']),
    'gshock': it(gshock, 42.8, 96.9, 'Casio G-Shock', ['One wrist'], l=2.4, r=2.4, dim='42.8'),
    'whoop': it(whoop, 24, 112, 'Whoop', ['The other'], l=1.5, r=1.5, dim='24'),
    'clapton': it(clapton, 300, 448, 'F155 Clapton', ['For everything'], l=6, r=6, dim='300'),
    'blair': it(blair, 125, 85, 'F05 Blair', ['For money'], l=7),
    'cheyenne': it(cheyenne, 195, 85, 'F35 Cheyenne', ['Several, for travel'], r=10),
    'm11p': it(m11p, 139, 80.3, 'Leica M11-P', ['The primary body, with the', 'Summilux-M 50mm f/1.4 ASPH'], l=3.6, r=3.6, top=5.3),
    'q3': it(q3, 130, 80.3, 'Leica Q3 43', ['The fixed-lens pairing'], l=3.6, r=3.6, top=1),
    'g2': it(g2, 139, 80, 'Contax G2', ['Mostly with the G 28mm', 'or the G 35mm'], l=3.6, r=3.6, top=3.6),
    'gr4': it(gr4, 109.4, 61.1, 'Ricoh GR IV Monochrome', ['My fourth GR'], top=1.7),
    'bigmini': it(bigmini, 115, 63, 'Konica Big Mini F', ['Two, for the family', 'rolls, 80–100 a year'], top=1.4),
    'hp5': it(canister, 53, 47.2, 'HP5 Plus', ['Black and white'], dim='25'),
    'portra': it(canister, 53, 47.2, 'Portra', ['Color'], dim='25'),
    'ultramax': it(canister, 53, 47.2, 'Ultramax', ['Color'], dim='25'),
    'm50': it(lens_m50, 58.6, 59.3, 'Summilux-M 50', ['f/1.4 ASPH, close focus']),
    'm35': it(lens_m35, 56, 46, 'Summilux-M 35', ['f/1.4 ASPH FLE']),
    's5': it(s5, 132.6, 97.1, 'Lumix S5', ['The original, the studio’s', 'utility camera'], dim='132.6'),
    'l2060': it(lumix_lens(77.4, 87.2, 'zoom'), 77.4, 87.2, 'Lumix S 20–60mm', ['f/3.5–5.6']),
    'l100': it(lumix_lens(73.6, 82, 'prime'), 73.6, 82, 'Lumix S 100mm', ['f/2.8 Macro']),
    'l50': it(lumix_lens(73.6, 82, 'prime'), 73.6, 82, 'Lumix S 50mm', ['f/1.8']),
    'jobo': it(jobo, 655, 460, 'JOBO CPE-3 with the Lift', ['A 1500 tank on the rollers'], dim='655'),
    'panel': it(therm_panel, 250, 82, 'Thermometer panel', [('Four probes, built for it', '/darkroom/thermometer-panel-for-jobo-systems/')], dim='≈ 250'),
    'rig': it(rig_named, 360, 573, 'LPL DS-4 copy stand', ['Side view'], r=290, dim='360'),
    'display': it(studio_display, 623, 478, 'Studio Display', ['Apple']),
    'bound': it(bound_notebook, 112, 182, 'Bound notebook', ['My own, still', 'in development']),
    'macbook': it(macbook, 312.6, 220.5, 'MacBook Pro', ['14-inch, M4 Max']),
    'macmini': it(macmini, 127, 50, 'Mac mini', ['Never sleeps.', ('Hank lives here', '/research/hank/')]),
    'sdxl': it(streamdeck_xl, 205, 147, 'Stream Deck + XL', ['The studio,', ('ambient computing,', '/research/ambient-computing/'), ('and Refmode', '/project-humane/refmode/')]),
    'a3': it(a3_sheet, 297, 420, 'A3 kraft paper', ['For ideation']),
    'waai': it(waai_three, 11, 142, 'Pilot FriXion Waai', ['0.5 mm, black, gray,', 'and orange'], r=36),
    'leaf': it(leaf, 95, 170, 'Unbound leaf', [('Bible size, six holes', '/project-humane/notebook-system/')]),
    'md': it(ghost(m11p), 138, 80, 'Leica M-D', [('The first gear-freeze', '/flaneur/010/')], l=3.6, r=3.6, top=5.3),
    'hexar': it(ghost(hexar), 139.5, 80, 'Konica Hexar RF', [], top=5.5),
    'q2': it(ghost(q2), 130, 80.3, 'Leica Q2 Monochrom', [], l=3.6, r=3.6, top=1),
    'klasse': it(ghost(klasse), 123, 64, 'Fujifilm Klasse S', [], top=2),
    'rx100': it(ghost(lambda p: None), 101.6, 58.1, 'Sony RX100 VII', [], top=2.2),
    'gr3': it(ghost(gr4), 109.4, 61.9, 'Ricoh GR III', ['Many of them'], top=1.7),
    'rz67': it(ghost(rz67), 108, 133.4, 'Mamiya RZ67 Pro II', [('A new fine-focus gear', '/darkroom/rz67-focus-gear-stl/')], l=15, r=15),
    'h203': it(ghost(h203), 91, 110, 'Hasselblad 203FE', [], l=6),
    'shenhao': it(ghost(shenhao), 260, 200, 'Shen Hao 6×17', [], l=13, r=13),
    'horseman': it(ghost(horseman), 172, 172, 'Horseman 45FA', [('Lensboards I made', '/darkroom/horseman-lensboards/')], l=14, r=14),
}


def rx100(p):
    p.rect(0, 0, 101.6, 58.1, rx=5)
    p.rect(72, 57, 20, 2.2, rx=1)
    rings(p, 41, 28, (22.5, 19.5, 13), 7.5)
    p.circle(88, 47, 1.6, INK)


L['rx100']['draw'] = ghost(rx100)
G = [it(g_lens(53, 11, 'hologon'), 53, 11, 'Hologon', ['16mm f/8'], top=6), it(g_lens(59, 35), 59, 35, 'Biogon', ['21mm f/2.8']),
     it(g_lens(56, 31), 56, 31, 'Biogon', ['28mm f/2.8', 'Mostly']), it(g_lens(56, 29), 56, 29, 'Planar', ['35mm f/2', 'Mostly']),
     it(g_lens(56, 39), 56, 39, 'Planar', ['45mm f/2']), it(g_lens(56, 63, 'tele'), 56, 63, 'Sonnar', ['90mm f/2.8']),
     it(g_lens(59, 54, 'zoom'), 59, 54, 'Vario-Sonnar', ['35–70mm'])]




def r(*keys):
    return [L[k] for k in keys]


DATE = '2026-11-02'
FIGURES = [
    ('walk-on-me', [r('tp7', 'notebook', 'iphone', 'gshock', 'whoop')], 1.6, 36),
    ('walk-bags', [r('clapton', 'blair', 'cheyenne')], .7, 36),
    ('shoot-cameras', [r('m11p', 'q3', 'g2'), r('gr4', 'bigmini', 'hp5', 'portra', 'ultramax')], 1.6, 36),
    ('shoot-lenses', [r('m50', 'm35'), G], 1.9, 14),
    ('shoot-studio', [r('s5', 'l2060', 'l100', 'l50')], 1.6, 36),
    ('develop-darkroom', [r('jobo', 'panel')], .6, 36),
    ('scan-copy-stand', [r('rig')], .6, 36),
    ('edit-desk', [r('display', 'bound', 'macbook', 'macmini', 'sdxl')], .46, 24),
    ('make-pens', [r('waai', 'leaf')], 1.6, 36),
    ('retired', [r('md', 'hexar', 'q2'), r('klasse', 'rx100', 'gr3'), r('rz67', 'h203', 'shenhao', 'horseman')], 1.05, 28),
]


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(root, 'static', 'visuals', 'tools')
    os.makedirs(out, exist_ok=True)
    for name, rows, s, gap in FIGURES:
        svg = drawing(name, rows, s, '', gap)
        # The drawing shortcode adds the role and the title from the page's alt.
        svg = re.sub(r' role="img" aria-label="[^"]*"', '', svg, count=1)
        path = os.path.join(out, f'{DATE}-{name}.svg')
        with open(path, 'w') as fh:
            fh.write(svg)
        print(os.path.relpath(path, root))


if __name__ == '__main__':
    main()
