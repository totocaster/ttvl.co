#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow>=11"]
# ///
"""Draw a map in the drawing palette from OpenStreetMap data.

    uv run tools/map.py static/visuals/solaris-highways/map.toml

A map is described by a TOML file beside the drawing it makes (map.toml
writes map.svg): the area, the places to number, the stations to name, and
any routes walked. North is up. docs/figures.md, Diagrams: A map.

    south = 35.654          # the area, in degrees
    west = 139.716
    north = 35.686
    east = 139.752
    width = 760             # the design width; the height follows the area
    narrow = 335            # optional: also draw map-narrow.svg for phones
    stations = ["Yotsuya", "Akasaka-mitsuke"]

    [[places]]              # numbered 1, 2, … in the order written
    lat = 35.6807191
    lon = 139.7263565
    name = "The view from Minami-motomachi Park"

    [[routes]]              # a walk or a drive: 2 px ink through the points
    points = [[35.68, 139.72], [35.67, 139.73]]

Streets, expressways, water, parks, and station names come from the
Overpass API (overpass.kumi.systems, then overpass-api.de), cached in the
temp folder by area. The map's caption must credit the data:
"Map data © OpenStreetMap contributors", linked to
https://www.openstreetmap.org/copyright. The places' names are printed as
a numbered list to use in that caption.
"""
import hashlib
import json
import math
import os
import sys
import tempfile
import tomllib
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figurelib import EDGE, GROUND, INK, MUTED, SURFACE, TONE3, TONE4, mixed, save, svg, text, width  # noqa: E402

SERVERS = ("https://overpass.kumi.systems/api/interpreter", "https://overpass-api.de/api/interpreter")


def fetch(south, west, north, east):
    pad = 0.002
    bbox = f"{south - pad},{west - pad},{north + pad},{east + pad}"
    query = (
        "[out:json][timeout:90];("
        f'way["highway"~"^(motorway|motorway_link|trunk|primary|secondary)$"]({bbox});'
        f'way["natural"="water"]({bbox});way["waterway"="riverbank"]({bbox});'
        f'way["leisure"="park"]({bbox});node["railway"="station"]({bbox});'
        ");out geom;"
    )
    cache = os.path.join(tempfile.gettempdir(), f"ttvl-map-{hashlib.sha1(query.encode()).hexdigest()[:12]}.json")
    if os.path.exists(cache):
        return json.load(open(cache))
    data = urllib.parse.urlencode({"data": query}).encode()
    for server in SERVERS:
        try:
            req = urllib.request.Request(server, data=data, headers={"User-Agent": "ttvl.co tools/map.py"})
            with urllib.request.urlopen(req, timeout=180) as r:
                body = r.read()
            osm = json.loads(body)
        except Exception as error:  # a busy server answers with HTML
            print(f"  {server}: {error}", file=sys.stderr)
            continue
        with open(cache, "wb") as f:
            f.write(body)
        return osm
    sys.exit("No Overpass server answered; try again later.")


def scale_bar(metres_across):
    """A round length near a sixth of the map's width."""
    target = metres_across / 6
    for step in (50, 100, 200, 250, 500, 1000, 2000, 2500, 5000, 10000):
        if step >= target * 0.6:
            return step
    return 10000


def draw(spec, osm, w, quiet=False):
    south, west, north, east = spec["south"], spec["west"], spec["north"], spec["east"]
    mx = 111320 * math.cos(math.radians((south + north) / 2))
    my = 110950
    k = w / ((east - west) * mx)
    h = round((north - south) * my * k)

    def P(lat, lon):
        return (lon - west) * mx * k, (north - lat) * my * k

    def path(points, close=False):
        out, last = [], None
        for lat, lon in points:
            x, y = P(lat, lon)
            if last and abs(x - last[0]) + abs(y - last[1]) < 1.5:
                continue
            out.append(f"{x:.1f} {y:.1f}")
            last = (x, y)
        return ("M" + "L".join(out) + ("z" if close else "")) if len(out) > 1 else ""

    layers = {"park": [], "water": [], "minor": [], "major": [], "motorway": []}
    stations = {}
    for e in osm["elements"]:
        t = e.get("tags", {})
        if e["type"] == "node":
            stations.setdefault(t.get("name:en") or t.get("name"), (e["lat"], e["lon"]))
            continue
        g = [(p["lat"], p["lon"]) for p in e.get("geometry", [])]
        if t.get("leisure") == "park":
            layers["park"].append(path(g, True))
        elif t.get("natural") == "water" or t.get("waterway") == "riverbank":
            layers["water"].append(path(g, True))
        elif t.get("highway") in ("motorway", "motorway_link"):
            layers["motorway"].append(path(g))
        elif t.get("highway") in ("trunk", "primary"):
            layers["major"].append(path(g))
        elif t.get("highway") == "secondary":
            layers["minor"].append(path(g))

    def joined(name):
        return " ".join(p for p in layers[name] if p)

    # Land is the ground; parks a surface, water the edge gray; streets in
    # edge and tone 4, expressways in 2 px tone 3, routes in 2 px ink.
    body = [f'<defs><clipPath id="map"><rect width="{w}" height="{h}"/></clipPath></defs><g clip-path="url(#map)">']
    body.append(f'<path d="{joined("park")}" fill="{SURFACE}"/>')
    body.append(f'<path d="{joined("water")}" fill="{EDGE}"/>')
    body.append(f'<path d="{joined("minor")}" stroke="{EDGE}"/>')
    body.append(f'<path d="{joined("major")}" stroke="{TONE4}"/>')
    body.append(f'<path d="{joined("motorway")}" stroke="{TONE3}" stroke-width="2" stroke-linejoin="round"/>')
    for route in spec.get("routes", []):
        body.append(f'<path d="{path(route["points"])}" stroke="{INK}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>')
    for name in spec.get("stations", []):
        if name not in stations:
            if not quiet:
                print(f"  ! no station named {name} in the area", file=sys.stderr)
            continue
        x, y = P(*stations[name])
        body.append(f'<rect x="{x - 3:.1f}" y="{y - 3:.1f}" width="6" height="6" fill="{GROUND}" stroke="{INK}"/>')
        body.append(f'<rect x="{x + 6:.1f}" y="{y - 10:.1f}" width="{width(name) + 8:.0f}" height="20" fill="{GROUND}"/>')
        body.append(text(x + 10, y + 5, name, fill=MUTED))
    body.append("</g>")

    # Places: numbered ink markers on ground rings; one that would cover
    # another steps aside on a short leader from a dot at the true point.
    placed = []
    for n, place in enumerate(spec.get("places", []), 1):
        x, y = P(place["lat"], place["lon"])
        px, py = x, y
        while any(math.hypot(px - qx, py - qy) < 26 for qx, qy in placed):
            px += 28
        if (px, py) != (x, y):
            body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{INK}"/>')
            body.append(f'<path d="M{x:.1f} {y:.1f}L{px:.1f} {py:.1f}" stroke="{INK}"/>')
        body.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="12" fill="{INK}" stroke="{GROUND}" stroke-width="2"/>')
        body.append(text(px, py + 5, str(n), mono=True, fill=GROUND, anchor="middle"))
        placed.append((px, py))
        if not quiet:
            print(f"{n} {place.get('name', '')}")

    # The scale bar at the bottom left, on a ground plate.
    metres = scale_bar((east - west) * mx)
    bar = metres * k
    label = [(f"{metres / 1000:g}", True), (" km", False)] if metres >= 1000 else [(str(metres), True), (" m", False)]
    body.append(f'<rect x="8" y="{h - 40}" width="{bar + 80:.0f}" height="32" fill="{GROUND}"/>')
    body.append(f'<path d="M16 {h - 19.5}H{16 + bar:.1f}M16.5 {h - 24}V{h - 15}M{16 + bar:.1f} {h - 24}V{h - 15}" stroke="{INK}"/>')
    body.append(mixed(24 + bar, h - 14, label))
    body.append(f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" stroke="{EDGE}"/>')
    return svg(w, h, body)


def main():
    if len(sys.argv) != 2 or not sys.argv[1].endswith(".toml"):
        sys.exit(__doc__.split("\n\n")[1])
    spec_path = sys.argv[1]
    spec = tomllib.load(open(spec_path, "rb"))
    osm = fetch(spec["south"], spec["west"], spec["north"], spec["east"])
    stem = spec_path[: -len(".toml")]
    save(stem + ".svg", draw(spec, osm, spec.get("width", 760)))
    if spec.get("narrow"):
        save(stem + "-narrow.svg", draw(spec, osm, spec["narrow"], quiet=True))


if __name__ == "__main__":
    main()
