// The Walks map: OpenFreeMap's vector tiles drawn in the site's tokens after
// the figures guide's map (north up, land ground, parks surface, water
// edge), with streets, rail, and expressways stepped back toward the
// ground, and every walk on it as a line. Colors are read from the custom
// properties and redrawn when the scheme changes. docs/figures.md, Map;
// docs/walks.md.

const LIB = "/vendor/maplibre/6.15.0/maplibre-gl.mjs";
const WORKER = "/vendor/maplibre/6.15.0/maplibre-gl-worker.mjs";
const NAME = ["coalesce", ["get", "name:en"], ["get", "name_en"], ["get", "name:latin"], ["get", "name"]];
const LINES = ["match", ["geometry-type"], ["LineString", "MultiLineString"], true, false];
const DOTS = ["match", ["geometry-type"], ["Point", "MultiPoint"], true, false];
const PHOTO_ZOOM = 11.5;
const PLACE_ZOOM = 6;

const reducedMotion = () => matchMedia("(prefers-reduced-motion: reduce)").matches;

export function pointsOf(feature) {
  const g = feature?.geometry;
  if (!g) return [];
  if (g.type === "MultiLineString") return g.coordinates.flat();
  if (g.type === "LineString" || g.type === "MultiPoint") return g.coordinates;
  return [];
}

let library;
async function maplibre() {
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

function tokens() {
  const css = getComputedStyle(document.documentElement);
  const t = Object.fromEntries(["ground", "ink", "ink-muted", "ink-faint", "edge", "rule", "surface", "tone-3", "signal"].map((name) => [name, css.getPropertyValue(`--${name}`).trim()]));
  // Streets step back from the edge toward the ground, so forty routes in
  // tone 3 stay the darkest lines on the map in both themes.
  const ground = solid(t.ground, t.ground), edge = solid(t.edge, t.ground);
  t.street = mix(edge, ground, 0.5);
  t.way = mix(edge, ground, 0.75);
  return t;
}

const zoomWidth = (...stops) => ["interpolate", ["exponential", 1.5], ["zoom"], ...stops];

export class WalkMap {
  // walks: [{id, place, photos, feature}], routes: a FeatureCollection,
  // places: [{key, name, walks}]. Options:
  //   onHover(id|null), onSelect(id), onPhoto(walkId, photoId),
  //   onPhotoHover(photoId|null), onPlace(key), onFail(),
  //   padding: () => ({top, right, bottom, left}), cooperative: false
  constructor(container, {walks, routes, places}, options = {}) {
    this.container = container;
    this.walks = walks;
    this.byId = new Map(walks.map((walk) => [walk.id, walk]));
    this.routes = routes;
    this.places = places;
    this.options = {cooperative: false, padding: () => ({top: 48, right: 48, bottom: 48, left: 48}), ...options};
    this.visible = null;
    this.hovered = null;
    this.chosen = null;
    this.photoMarkers = [];
    this.placeMarkers = [];
    this.ready = this.init();
  }

  async init() {
    const lib = await maplibre();
    this.lib = lib;
    this.container.dataset.mapState = "loading";
    this.map = new lib.Map({
      container: this.container,
      style: this.style(tokens()),
      center: [139.76, 35.69],
      zoom: 10.5,
      attributionControl: false,
      dragRotate: false,
      pitchWithRotate: false,
      touchPitch: false,
      maxPitch: 0,
      cooperativeGestures: this.options.cooperative,
      locale: {
        "CooperativeGesturesHandler.WindowsHelpText": "Ctrl + scroll zooms the map",
        "CooperativeGesturesHandler.MacHelpText": "⌘ + scroll zooms the map",
        "CooperativeGesturesHandler.MobileHelpText": "Two fingers move the map",
      },
      canvasContextAttributes: {antialias: true},
    });
    this.map.touchZoomRotate.disableRotation();
    this.map.keyboard.disableRotation?.();
    this.map.addControl(new lib.NavigationControl({showCompass: false}), "top-right");
    this.map.addControl(new lib.ScaleControl({maxWidth: 96, unit: "metric"}), "bottom-left");
    // If the tiles never arrive, the page says so; the panel works without
    // the map.
    const watchdog = setTimeout(() => {
      this.container.dataset.mapState = "failed";
      this.options.onFail?.();
    }, 20000);
    await new Promise((resolve) => this.map.once("load", resolve));
    clearTimeout(watchdog);
    this.loaded = true;
    // The state the page and its tests can read: loading, then idle once
    // every tile in view has drawn.
    this.map.on("dataloading", () => { this.container.dataset.mapState = "loading"; });
    this.map.on("idle", () => { this.container.dataset.mapState = "idle"; });
    this.bind();
    this.addPlaceKeys();
    // Catch up with whatever the page chose while the map was loading.
    this.setVisible(this.visible);
    this.setPhotos(this.chosen ? this.byId.get(this.chosen) : null);
    this.zoomed();
    matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => this.map.setStyle(this.style(tokens()), {diff: true}));
    return this;
  }

  filters() {
    const all = this.walks.map((walk) => walk.id);
    const none = "__none__";
    return {
      context: ["in", ["get", "walk"], ["literal", this.visible || all]],
      hover: ["==", ["get", "walk"], this.hovered || none],
      chosen: ["==", ["get", "walk"], this.chosen || none],
    };
  }

  style(t) {
    const f = this.filters();
    const label = {"text-field": NAME, "text-font": ["Noto Sans Regular"], "text-size": 14, "text-max-width": 8, "text-padding": 6};
    const labelPaint = {"text-color": t["ink-faint"], "text-halo-color": t.ground, "text-halo-width": 2};
    const round = {"line-cap": "round", "line-join": "round"};
    return {
      version: 8,
      glyphs: "https://tiles.openfreemap.org/fonts/{fontstack}/{range}.pbf",
      sources: {
        omt: {type: "vector", url: "https://tiles.openfreemap.org/planet"},
        walks: {type: "geojson", data: this.routes},
        ends: {type: "geojson", data: this.endsData()},
      },
      layers: [
        {id: "b-ground", type: "background", paint: {"background-color": t.ground}},
        {id: "b-park", type: "fill", source: "omt", "source-layer": "park", paint: {"fill-color": t.surface}},
        {id: "b-wood", type: "fill", source: "omt", "source-layer": "landcover", filter: ["match", ["get", "class"], ["wood", "grass"], true, false], paint: {"fill-color": t.surface}},
        {id: "b-water", type: "fill", source: "omt", "source-layer": "water", filter: ["!=", ["get", "brunnel"], "tunnel"], paint: {"fill-color": t.edge}},
        {id: "b-waterway", type: "line", source: "omt", "source-layer": "waterway", minzoom: 9, paint: {"line-color": t.edge, "line-width": zoomWidth(10, 0.5, 16, 2)}},
        {id: "b-building", type: "fill", source: "omt", "source-layer": "building", minzoom: 14, paint: {"fill-color": t.rule}},
        {id: "b-road-minor", type: "line", source: "omt", "source-layer": "transportation", minzoom: 13, filter: ["all", LINES, ["match", ["get", "class"], ["minor", "service", "track"], true, false]], layout: round, paint: {"line-color": t.street, "line-width": zoomWidth(13, 0.5, 16, 2, 18, 7)}},
        {id: "b-road-major", type: "line", source: "omt", "source-layer": "transportation", minzoom: 8, filter: ["all", LINES, ["match", ["get", "class"], ["primary", "secondary", "tertiary", "trunk"], true, false]], layout: round, paint: {"line-color": t.street, "line-width": zoomWidth(9, 0.5, 12, 1, 16, 4, 18, 12)}},
        {id: "b-rail", type: "line", source: "omt", "source-layer": "transportation", minzoom: 9, filter: ["all", LINES, ["match", ["get", "class"], ["rail", "transit"], true, false], ["!", ["has", "service"]], ["!=", ["get", "brunnel"], "tunnel"]], paint: {"line-color": t.way, "line-width": zoomWidth(10, 0.75, 16, 1.5), "line-dasharray": [3, 2]}},
        {id: "b-motorway", type: "line", source: "omt", "source-layer": "transportation", minzoom: 6, filter: ["all", LINES, ["==", ["get", "class"], "motorway"], ["!=", ["get", "brunnel"], "tunnel"]], layout: round, paint: {"line-color": t.way, "line-width": zoomWidth(6, 0.75, 11, 1.5, 16, 4, 18, 10)}},
        {id: "b-label-water", type: "symbol", source: "omt", "source-layer": "water_name", minzoom: 10, layout: {...label, "text-font": ["Noto Sans Italic"]}, paint: labelPaint},
        {id: "b-label-quarter", type: "symbol", source: "omt", "source-layer": "place", minzoom: 13.5, filter: ["match", ["get", "class"], ["quarter", "neighbourhood"], true, false], layout: label, paint: labelPaint},
        {id: "b-label-suburb", type: "symbol", source: "omt", "source-layer": "place", minzoom: 10.5, maxzoom: 15, filter: ["match", ["get", "class"], ["suburb", "village"], true, false], layout: label, paint: labelPaint},
        {id: "b-label-city", type: "symbol", source: "omt", "source-layer": "place", maxzoom: 13, filter: ["match", ["get", "class"], ["city", "town"], true, false], layout: label, paint: {...labelPaint, "text-color": t["ink-muted"]}},
        // Walks: every visible one in tone 3, the chosen one in ink on a
        // ground casing with its ends, and the one under the hand (on the map
        // or in the rows) in the signal color on top of everything.
        {id: "w-context", type: "line", source: "walks", filter: ["all", LINES, f.context], layout: round, paint: {"line-color": t["tone-3"], "line-width": zoomWidth(8, 1, 12, 1.5, 16, 2.25)}},
        {id: "w-context-dots", type: "circle", source: "walks", filter: ["all", DOTS, f.context], paint: {"circle-color": t["tone-3"], "circle-radius": 3}},
        {id: "w-chosen-casing", type: "line", source: "walks", filter: ["all", LINES, f.chosen], layout: round, paint: {"line-color": t.ground, "line-width": zoomWidth(8, 6, 12, 7, 16, 9)}},
        {id: "w-chosen", type: "line", source: "walks", filter: ["all", LINES, f.chosen], layout: round, paint: {"line-color": t.ink, "line-width": zoomWidth(8, 2.5, 12, 3, 16, 4)}},
        {id: "w-chosen-dots", type: "circle", source: "walks", filter: ["all", DOTS, ["any", f.chosen, f.hover]], paint: {"circle-color": t.ink, "circle-radius": 4.5, "circle-stroke-color": t.ground, "circle-stroke-width": 2}},
        {id: "w-start", type: "circle", source: "ends", filter: ["==", ["get", "end"], "start"], paint: {"circle-color": t.ground, "circle-radius": 5, "circle-stroke-color": t.ink, "circle-stroke-width": 2}},
        {id: "w-end", type: "circle", source: "ends", filter: ["==", ["get", "end"], "end"], paint: {"circle-color": t.ink, "circle-radius": 5, "circle-stroke-color": t.ground, "circle-stroke-width": 2}},
        {id: "w-hover-casing", type: "line", source: "walks", filter: ["all", LINES, f.hover], layout: round, paint: {"line-color": t.ground, "line-width": zoomWidth(8, 5, 12, 6, 16, 8)}},
        {id: "w-hover", type: "line", source: "walks", filter: ["all", LINES, f.hover], layout: round, paint: {"line-color": t.signal, "line-width": zoomWidth(8, 2.5, 12, 3, 16, 4)}},
        {id: "w-hit", type: "line", source: "walks", filter: ["all", LINES, f.context], paint: {"line-color": t.ink, "line-width": 14, "line-opacity": 0}},
        {id: "w-hit-dots", type: "circle", source: "walks", filter: ["all", DOTS, f.context], paint: {"circle-color": t.ink, "circle-radius": 10, "circle-opacity": 0}},
      ],
    };
  }

  endsData() {
    const g = this.chosen && this.byId.get(this.chosen)?.feature?.geometry;
    if (!g || g.type !== "MultiLineString" || !g.coordinates.length) return {type: "FeatureCollection", features: []};
    const point = (end, coordinates) => ({type: "Feature", properties: {end}, geometry: {type: "Point", coordinates}});
    return {type: "FeatureCollection", features: [point("start", g.coordinates[0][0]), point("end", g.coordinates.at(-1).at(-1))]};
  }

  applyFilters() {
    if (!this.loaded) return;
    const f = this.filters();
    this.map.setFilter("w-context", ["all", LINES, f.context]);
    this.map.setFilter("w-context-dots", ["all", DOTS, f.context]);
    this.map.setFilter("w-hit", ["all", LINES, f.context]);
    this.map.setFilter("w-hit-dots", ["all", DOTS, f.context]);
    this.map.setFilter("w-hover-casing", ["all", LINES, f.hover]);
    this.map.setFilter("w-hover", ["all", LINES, f.hover]);
    this.map.setFilter("w-chosen-casing", ["all", LINES, f.chosen]);
    this.map.setFilter("w-chosen", ["all", LINES, f.chosen]);
    this.map.setFilter("w-chosen-dots", ["all", DOTS, ["any", f.chosen, f.hover]]);
    this.map.getSource("ends")?.setData(this.endsData());
  }

  bind() {
    const pick = (event) => event.features?.[0]?.properties.walk || null;
    for (const layer of ["w-hit", "w-hit-dots"]) {
      this.map.on("mousemove", layer, (event) => {
        const id = pick(event);
        this.map.getCanvas().style.cursor = "pointer";
        if (id !== this.hovered) {
          this.setHover(id);
          this.options.onHover?.(id);
        }
      });
      this.map.on("mouseleave", layer, () => {
        this.map.getCanvas().style.cursor = "";
        this.setHover(null);
        this.options.onHover?.(null);
      });
      this.map.on("click", layer, (event) => {
        const id = pick(event);
        if (id) this.options.onSelect?.(id);
      });
    }
    this.map.on("zoom", () => this.zoomed());
  }

  zoomed() {
    const z = this.map.getZoom();
    this.container.classList.toggle("walks-photos-off", z < PHOTO_ZOOM);
    this.container.classList.toggle("walks-places-on", z < PLACE_ZOOM);
  }

  // Under z6 each place is a quiet key at its middle that zooms to it.
  addPlaceKeys() {
    for (const place of this.places) {
      if (!place.walks.length) continue;
      const middle = (axis) => place.walks.map((walk) => walk.center[axis]).sort((a, b) => a - b)[Math.floor(place.walks.length / 2)];
      const key = document.createElement("button");
      key.type = "button";
      key.className = "walks-place-key";
      key.dataset.place = place.key;
      key.setAttribute("aria-label", `${place.name}, ${place.walks.length} ${place.walks.length === 1 ? "walk" : "walks"}`);
      key.innerHTML = `<span></span> <span class="n"></span>`;
      key.firstChild.textContent = place.name;
      key.lastChild.textContent = String(place.walks.length);
      key.addEventListener("click", () => this.options.onPlace?.(place.key));
      // Tokyo and Around Tokyo share a point at world scale: stack them west of it.
      const [anchor, offset] = {tokyo: ["bottom-right", [-4, -4]], around: ["top-right", [-4, 4]]}[place.key] || ["center", [0, 0]];
      this.placeMarkers.push(new this.lib.Marker({element: key, anchor, offset}).setLngLat([middle(0), middle(1)]).addTo(this.map));
    }
  }

  setVisible(ids) {
    this.visible = ids;
    for (const marker of this.placeMarkers) {
      const place = this.places.find((p) => p.key === marker.getElement().dataset.place);
      marker.getElement().hidden = !!ids && !place.walks.some((walk) => ids.includes(walk.id));
    }
    this.applyFilters();
  }

  setHover(id) {
    if (id === this.hovered) return;
    this.hovered = id;
    this.applyFilters();
  }

  // Choose a walk: its line in ink, its ends, its numbered photographs.
  setChosen(id) {
    this.chosen = id;
    this.applyFilters();
    this.setPhotos(id ? this.byId.get(id) : null);
  }

  setPhotos(walk) {
    this.photoMarkers.forEach((marker) => marker.remove());
    this.photoMarkers = [];
    if (!walk || !this.loaded) return;
    for (const photo of walk.photos.filter((p) => p.coordinates)) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "walks-marker";
      button.dataset.photoId = photo.id;
      button.textContent = String(photo.sequence).padStart(2, "0");
      button.setAttribute("aria-label", `Photograph ${photo.sequence}${photo.time ? `, ${photo.time}` : ""}`);
      button.addEventListener("click", (event) => { event.stopPropagation(); this.options.onPhoto?.(walk.id, photo.id); });
      for (const [type, value] of [["mouseenter", photo.id], ["focus", photo.id], ["mouseleave", null], ["blur", null]]) {
        button.addEventListener(type, () => this.options.onPhotoHover?.(value));
      }
      this.photoMarkers.push(new this.lib.Marker({element: button, anchor: "center"}).setLngLat(photo.coordinates).addTo(this.map));
    }
  }

  // Light one photograph's marker (from a tile under the hand), or none.
  lightPhoto(photoId) {
    for (const marker of this.photoMarkers) marker.getElement().classList.toggle("is-lit", marker.getElement().dataset.photoId === photoId);
  }

  fitIds(ids, {animate = true, maxZoom = 15.5} = {}) {
    if (!this.loaded || !ids.length) return;
    const bounds = new this.lib.LngLatBounds();
    for (const id of ids) for (const point of pointsOf(this.byId.get(id)?.feature)) bounds.extend(point);
    if (bounds.isEmpty()) return;
    this.map.fitBounds(bounds, {padding: this.options.padding(), maxZoom, duration: animate && !reducedMotion() ? 700 : 0});
  }

  fitPlace(key, options) {
    const place = this.places.find((p) => p.key === key);
    if (place) this.fitIds(place.walks.map((walk) => walk.id), options);
  }

  resize() {
    this.map?.resize();
  }
}
