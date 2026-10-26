// The Walks map: the site's map (panel-map.js) with every walk on it as a
// line. Colors are read from the custom properties and redrawn when the
// scheme changes. docs/figures.md, Map; docs/walks.md.

import {DOTS, LINES, ROUND as round, base, createMap, followScheme, maplibre, reducedMotion, tokens, zoomWidth} from "./panel-map.js";

const PHOTO_ZOOM = 11.5;
const PLACE_ZOOM = 6;

const pointData = (at) => ({type: "FeatureCollection", features: at ? [{type: "Feature", properties: {}, geometry: {type: "Point", coordinates: at}}] : []});

export function pointsOf(feature) {
  const g = feature?.geometry;
  if (!g) return [];
  if (g.type === "MultiLineString") return g.coordinates.flat();
  if (g.type === "LineString" || g.type === "MultiPoint") return g.coordinates;
  return [];
}

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
    this.lampAt = null; // where the sheet's day is, [lon, lat]
    this.spotAt = null; // where the photograph under the hand was made
    this.photoMarkers = [];
    this.placeMarkers = [];
    this.ready = this.init();
  }

  async init() {
    const lib = await maplibre();
    this.lib = lib;
    this.container.dataset.mapState = "loading";
    this.map = createMap(lib, this.container, this.style(tokens()), {
      center: [139.76, 35.69],
      zoom: 10.5,
      cooperativeGestures: this.options.cooperative,
      locale: {
        "CooperativeGesturesHandler.WindowsHelpText": "Ctrl + scroll zooms the map",
        "CooperativeGesturesHandler.MacHelpText": "⌘ + scroll zooms the map",
        "CooperativeGesturesHandler.MobileHelpText": "Two fingers move the map",
      },
    });
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
    this.setChosen(this.chosen);
    this.zoomed();
    followScheme(this.map, (t) => this.style(t));
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

  routePaint(t) {
    // The index shows slightly heavier graphite routes, with the row or
    // route under the hand in ink. An open walk keeps its original styling.
    return {
      context: this.chosen ? t["tone-3"] : t["tone-2"],
      hover: this.chosen ? t.signal : t.ink,
      width: this.chosen ? zoomWidth(8, 1, 12, 1.5, 16, 2.25) : zoomWidth(8, 1.5, 12, 2, 16, 2.75),
    };
  }

  style(t) {
    const f = this.filters();
    const map = base(t);
    const routes = this.routePaint(t);
    return {
      version: 8,
      glyphs: map.glyphs,
      sources: {
        ...map.sources,
        walks: {type: "geojson", data: this.routes},
        ends: {type: "geojson", data: this.endsData()},
        spot: {type: "geojson", data: pointData(this.spotAt)},
        lamp: {type: "geojson", data: pointData(this.lampAt)},
      },
      layers: [
        ...map.layers,
        // The chosen walk stays in ink on a ground casing with its ends;
        // the index and sheet use their own context and hover colors.
        {id: "w-context", type: "line", source: "walks", filter: ["all", LINES, f.context], layout: round, paint: {"line-color": routes.context, "line-width": routes.width}},
        {id: "w-context-dots", type: "circle", source: "walks", filter: ["all", DOTS, f.context], paint: {"circle-color": routes.context, "circle-radius": 3}},
        {id: "w-chosen-casing", type: "line", source: "walks", filter: ["all", LINES, f.chosen], layout: round, paint: {"line-color": t.ground, "line-width": zoomWidth(8, 6, 12, 7, 16, 9)}},
        {id: "w-chosen", type: "line", source: "walks", filter: ["all", LINES, f.chosen], layout: round, paint: {"line-color": t.ink, "line-width": zoomWidth(8, 2.5, 12, 3, 16, 4)}},
        {id: "w-chosen-dots", type: "circle", source: "walks", filter: ["all", DOTS, ["any", f.chosen, f.hover]], paint: {"circle-color": t.ink, "circle-radius": 4.5, "circle-stroke-color": t.ground, "circle-stroke-width": 2}},
        {id: "w-start", type: "circle", source: "ends", filter: ["==", ["get", "end"], "start"], paint: {"circle-color": t.ground, "circle-radius": 5, "circle-stroke-color": t.ink, "circle-stroke-width": 2}},
        {id: "w-end", type: "circle", source: "ends", filter: ["==", ["get", "end"], "end"], paint: {"circle-color": t.ink, "circle-radius": 5, "circle-stroke-color": t.ground, "circle-stroke-width": 2}},
        {id: "w-hover-casing", type: "line", source: "walks", filter: ["all", LINES, f.hover], layout: round, paint: {"line-color": t.ground, "line-width": zoomWidth(8, 5, 12, 6, 16, 8)}},
        {id: "w-hover", type: "line", source: "walks", filter: ["all", LINES, f.hover], layout: round, paint: {"line-color": routes.hover, "line-width": zoomWidth(8, 2.5, 12, 3, 16, 4)}},
        {id: "w-hit", type: "line", source: "walks", filter: ["all", LINES, f.context], paint: {"line-color": t.ink, "line-width": 14, "line-opacity": 0}},
        {id: "w-hit-dots", type: "circle", source: "walks", filter: ["all", DOTS, f.context], paint: {"circle-color": t.ink, "circle-radius": 10, "circle-opacity": 0}},
        // The photograph under the hand: a signal ring around its marker, or
        // around an ink dot where the markers are off or it has none.
        {id: "w-spot-dot", type: "circle", source: "spot", paint: {"circle-color": t.ink, "circle-radius": 4.5, "circle-stroke-color": t.ground, "circle-stroke-width": 2}},
        {id: "w-spot", type: "circle", source: "spot", paint: {"circle-color": t.ground, "circle-opacity": 0, "circle-radius": 16, "circle-stroke-color": t.signal, "circle-stroke-width": 2.5}},
        // The lamp: where the sheet's day is, in the signal on a ground ring.
        {id: "w-lamp", type: "circle", source: "lamp", paint: {"circle-color": t.signal, "circle-radius": 6, "circle-stroke-color": t.ground, "circle-stroke-width": 2.5}},
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
    if (this.loaded) {
      const routes = this.routePaint(tokens());
      this.map.setPaintProperty("w-context", "line-color", routes.context);
      this.map.setPaintProperty("w-context", "line-width", routes.width);
      this.map.setPaintProperty("w-context-dots", "circle-color", routes.context);
      this.map.setPaintProperty("w-hover", "line-color", routes.hover);
    }
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

  // The lamp follows the sheet's day; null puts it out.
  setLamp(lonlat) {
    this.lampAt = lonlat;
    this.map?.getSource("lamp")?.setData(pointData(lonlat));
  }

  // Ring where a photograph was made while it is under the hand; null clears it.
  setSpot(lonlat) {
    this.spotAt = lonlat;
    this.map?.getSource("spot")?.setData(pointData(lonlat));
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
