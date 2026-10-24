// The site's map: OpenFreeMap's vector tiles drawn in the tokens after the
// figures guide's map (north up, land ground, parks surface, water edge),
// with streets, rail, expressways, and borders stepped back toward the
// ground so what a page draws on top stays the darkest thing on it. The
// Walks map and the spatial long exposure share it. docs/figures.md, Map.

const LIB = "/vendor/maplibre/6.15.0/maplibre-gl.mjs";
const WORKER = "/vendor/maplibre/6.15.0/maplibre-gl-worker.mjs";
export const NAME = ["coalesce", ["get", "name:en"], ["get", "name_en"], ["get", "name:latin"], ["get", "name"]];
export const LINES = ["match", ["geometry-type"], ["LineString", "MultiLineString"], true, false];
export const DOTS = ["match", ["geometry-type"], ["Point", "MultiPoint"], true, false];
export const ROUND = {"line-cap": "round", "line-join": "round"};

export const reducedMotion = () => matchMedia("(prefers-reduced-motion: reduce)").matches;
export const zoomWidth = (...stops) => ["interpolate", ["exponential", 1.5], ["zoom"], ...stops];

let library;
export async function maplibre() {
  if (!library) {
    // A variable keeps the bundler from resolving the vendored module.
    const url = LIB;
    library = await import(url);
    library.setWorkerUrl(WORKER);
  }
  return library;
}

// A token as a solid color over the ground, so translucent dark-mode tokens
// can be blended: one pixel on a canvas does the compositing.
const probe = document.createElement("canvas").getContext("2d", {willReadFrequently: true});
function solid(color, ground) {
  probe.clearRect(0, 0, 1, 1);
  probe.fillStyle = ground;
  probe.fillRect(0, 0, 1, 1);
  probe.fillStyle = color;
  probe.fillRect(0, 0, 1, 1);
  return [...probe.getImageData(0, 0, 1, 1).data.slice(0, 3)];
}
const mix = (a, b, t) => `rgb(${a.map((v, i) => Math.round(v * t + b[i] * (1 - t))).join(", ")})`;

export function tokens() {
  const css = getComputedStyle(document.documentElement);
  const t = Object.fromEntries(["ground", "ink", "ink-muted", "ink-faint", "edge", "rule", "surface", "tone-3", "signal"].map((name) => [name, css.getPropertyValue(`--${name}`).trim()]));
  // Streets step back from the edge toward the ground, so lines in tone 3
  // stay the darkest on the map in both themes.
  const ground = solid(t.ground, t.ground), edge = solid(t.edge, t.ground);
  t.street = mix(edge, ground, 0.5);
  t.way = mix(edge, ground, 0.75);
  return t;
}

// Redraw a map in the new tokens when the scheme changes.
export function followScheme(map, style) {
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => map.setStyle(style(tokens()), {diff: true}));
}

// The base style: its sources and layers, for a page to add its own above.
export function base(t) {
  const label = {"text-field": NAME, "text-font": ["Noto Sans Regular"], "text-size": 14, "text-max-width": 8, "text-padding": 6};
  const labelPaint = {"text-color": t["ink-faint"], "text-halo-color": t.ground, "text-halo-width": 2};
  return {
    glyphs: "https://tiles.openfreemap.org/fonts/{fontstack}/{range}.pbf",
    sources: {omt: {type: "vector", url: "https://tiles.openfreemap.org/planet"}},
    layers: [
      {id: "b-ground", type: "background", paint: {"background-color": t.ground}},
      {id: "b-park", type: "fill", source: "omt", "source-layer": "park", paint: {"fill-color": t.surface}},
      {id: "b-wood", type: "fill", source: "omt", "source-layer": "landcover", filter: ["match", ["get", "class"], ["wood", "grass"], true, false], paint: {"fill-color": t.surface}},
      {id: "b-water", type: "fill", source: "omt", "source-layer": "water", filter: ["!=", ["get", "brunnel"], "tunnel"], paint: {"fill-color": t.edge}},
      {id: "b-waterway", type: "line", source: "omt", "source-layer": "waterway", minzoom: 9, paint: {"line-color": t.edge, "line-width": zoomWidth(10, 0.5, 16, 2)}},
      {id: "b-border", type: "line", source: "omt", "source-layer": "boundary", filter: ["all", ["==", ["get", "admin_level"], 2], ["!=", ["get", "maritime"], 1]], layout: ROUND, paint: {"line-color": t.street, "line-width": zoomWidth(2, 0.5, 8, 1, 14, 1.5)}},
      {id: "b-building", type: "fill", source: "omt", "source-layer": "building", minzoom: 14, paint: {"fill-color": t.rule}},
      {id: "b-road-minor", type: "line", source: "omt", "source-layer": "transportation", minzoom: 13, filter: ["all", LINES, ["match", ["get", "class"], ["minor", "service", "track"], true, false]], layout: ROUND, paint: {"line-color": t.street, "line-width": zoomWidth(13, 0.5, 16, 2, 18, 7)}},
      {id: "b-road-major", type: "line", source: "omt", "source-layer": "transportation", minzoom: 8, filter: ["all", LINES, ["match", ["get", "class"], ["primary", "secondary", "tertiary", "trunk"], true, false]], layout: ROUND, paint: {"line-color": t.street, "line-width": zoomWidth(9, 0.5, 12, 1, 16, 4, 18, 12)}},
      {id: "b-rail", type: "line", source: "omt", "source-layer": "transportation", minzoom: 9, filter: ["all", LINES, ["match", ["get", "class"], ["rail", "transit"], true, false], ["!", ["has", "service"]], ["!=", ["get", "brunnel"], "tunnel"]], paint: {"line-color": t.way, "line-width": zoomWidth(10, 0.75, 16, 1.5), "line-dasharray": [3, 2]}},
      {id: "b-motorway", type: "line", source: "omt", "source-layer": "transportation", minzoom: 6, filter: ["all", LINES, ["==", ["get", "class"], "motorway"], ["!=", ["get", "brunnel"], "tunnel"]], layout: ROUND, paint: {"line-color": t.way, "line-width": zoomWidth(6, 0.75, 11, 1.5, 16, 4, 18, 10)}},
      {id: "b-label-water", type: "symbol", source: "omt", "source-layer": "water_name", minzoom: 10, layout: {...label, "text-font": ["Noto Sans Italic"]}, paint: labelPaint},
      {id: "b-label-quarter", type: "symbol", source: "omt", "source-layer": "place", minzoom: 13.5, filter: ["match", ["get", "class"], ["quarter", "neighbourhood"], true, false], layout: label, paint: labelPaint},
      {id: "b-label-suburb", type: "symbol", source: "omt", "source-layer": "place", minzoom: 10.5, maxzoom: 15, filter: ["match", ["get", "class"], ["suburb", "village"], true, false], layout: label, paint: labelPaint},
      {id: "b-label-city", type: "symbol", source: "omt", "source-layer": "place", maxzoom: 13, filter: ["match", ["get", "class"], ["city", "town"], true, false], layout: label, paint: {...labelPaint, "text-color": t["ink-muted"]}},
    ],
  };
}

// A map with the site's defaults: no rotation or pitch, MapLibre's own
// attribution off (each page credits OpenFreeMap and OpenStreetMap itself).
export function createMap(lib, container, style, options = {}) {
  const map = new lib.Map({
    container,
    style,
    attributionControl: false,
    dragRotate: false,
    pitchWithRotate: false,
    touchPitch: false,
    maxPitch: 0,
    canvasContextAttributes: {antialias: true},
    ...options,
  });
  map.touchZoomRotate.disableRotation();
  map.keyboard.disableRotation?.();
  return map;
}
