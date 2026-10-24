// The spatial long exposure: every recorded place on the site's map
// (panel-map.js), in the signal color the Walks map lights a walk with, and
// the connections between consecutive visits under them in tone 3, the
// walks' own color. Overlaps build up like light on film: a place visited
// often, or a line travelled often, is denser. Colors come from the tokens
// and are redrawn when the scheme changes. docs/figures.md, Map.

import {LINES, ROUND, base, createMap, followScheme, maplibre, reducedMotion, tokens} from "./panel-map.js";

const root = document.querySelector("[data-spatial-long-exposure]");
if (root) start(root);

async function start(root) {
  const container = root.querySelector("[data-map]");
  const frame = root.querySelector(".spatial-long-exposure__frame");
  const loading = root.querySelector("[data-map-loading]");
  const modeButtons = [...root.querySelectorAll("[data-map-mode]")];
  const resetButton = root.querySelector("[data-map-reset]");
  const fullscreenButton = root.querySelector("[data-map-fullscreen]");
  let mode = "both";
  let touched = false;

  const fail = () => {
    loading.hidden = false;
    loading.textContent = "The map could not be developed.";
  };

  let lib, trace;
  try {
    [lib, trace] = await Promise.all([
      maplibre(),
      fetch(root.dataset.traceUrl).then((response) => {
        if (!response.ok) throw new Error("Location data could not be loaded");
        return response.json();
      }),
    ]);
  } catch {
    fail();
    return;
  }

  // Recurrence is the log of the count: a place seen twice is one step
  // denser than a place seen once.
  const places = {
    type: "FeatureCollection",
    features: trace.points.map(([lon, lat, count, kind]) => ({type: "Feature", properties: {r: Math.log2(Math.max(1, count)), k: kind}, geometry: {type: "Point", coordinates: [lon, lat]}})),
  };
  const connections = {
    type: "FeatureCollection",
    features: trace.segments.map(([lon1, lat1, lon2, lat2, count]) => ({type: "Feature", properties: {r: Math.log2(Math.max(1, count))}, geometry: {type: "LineString", coordinates: [[lon1, lat1], [lon2, lat2]]}})),
  };
  const bounds = new lib.LngLatBounds();
  for (const feature of places.features) bounds.extend(feature.geometry.coordinates);
  const padding = () => Math.round(Math.min(container.clientWidth, container.clientHeight) * 0.06);

  const visible = (layer) => (mode === "both" || mode === layer ? "visible" : "none");
  const style = (t) => {
    const map = base(t);
    const r = ["get", "r"];
    return {
      version: 8,
      glyphs: map.glyphs,
      sources: {
        ...map.sources,
        connections: {type: "geojson", data: connections},
        places: {type: "geojson", data: places},
      },
      layers: [
        ...map.layers,
        {id: "s-connections", type: "line", source: "connections", filter: LINES, layout: {...ROUND, visibility: visible("connections")}, paint: {
          "line-color": t["tone-3"],
          "line-opacity": ["min", 0.9, ["+", 0.45, ["*", 0.12, r]]],
          "line-width": ["interpolate", ["exponential", 1.5], ["zoom"], 1, ["+", 0.5, ["*", 0.15, r]], 8, ["+", 0.75, ["*", 0.25, r]], 14, ["+", 1.5, ["*", 0.4, r]]],
        }},
        {id: "s-places", type: "circle", source: "places", layout: {visibility: visible("places")}, paint: {
          "circle-color": t.signal,
          // Photographs (kind 2) a step lighter than visits.
          "circle-opacity": ["min", 0.95, ["+", ["match", ["get", "k"], 2, 0.5, 0.6], ["*", 0.08, r]]],
          "circle-radius": ["interpolate", ["linear"], ["zoom"], 1, ["+", 1.5, ["*", 0.25, r]], 8, ["+", 2, ["*", 0.3, r]], 14, ["+", 3, ["*", 0.4, r]], 18, ["+", 4.5, ["*", 0.4, r]]],
        }},
      ],
    };
  };

  const map = createMap(lib, container, style(tokens()), {
    bounds,
    fitBoundsOptions: {padding: padding()},
    minZoom: 1,
    maxZoom: 17,
  });
  map.getCanvas().setAttribute("aria-label", `${trace.uniquePointCount.toLocaleString("en")} undated locations from location history and geotagged photographs, with connections between recorded visits`);
  const watchdog = setTimeout(fail, 20000);
  map.once("load", () => {
    clearTimeout(watchdog);
    loading.hidden = true;
  });
  // The state a capture can wait for: idle once every tile in view has drawn.
  map.on("dataloading", () => { container.dataset.mapState = "loading"; });
  map.on("idle", () => { container.dataset.mapState = "idle"; });
  followScheme(map, style);

  // Until the reader moves the map, it keeps every place in view.
  const fit = (animate) => map.fitBounds(bounds, {padding: padding(), duration: animate && !reducedMotion() ? 500 : 0});
  map.on("movestart", (event) => { if (event.originalEvent) touched = true; });
  map.on("resize", () => { if (!touched) fit(false); });
  const reset = () => {
    touched = false;
    fit(true);
  };

  const setMode = (next) => {
    mode = next;
    for (const button of modeButtons) button.setAttribute("aria-pressed", String(button.dataset.mapMode === mode));
    if (map.getLayer("s-places")) {
      map.setLayoutProperty("s-connections", "visibility", visible("connections"));
      map.setLayoutProperty("s-places", "visibility", visible("places"));
    }
  };
  for (const button of modeButtons) button.addEventListener("click", () => setMode(button.dataset.mapMode));
  resetButton.addEventListener("click", reset);
  // MapLibre's keys move and zoom; 0 returns to the whole exposure.
  map.getCanvas().addEventListener("keydown", (event) => {
    if (event.key === "0" && !event.metaKey && !event.ctrlKey && !event.altKey) {
      event.preventDefault();
      reset();
    }
  });

  // Full screen, with a fixed-position fallback where the API is refused.
  const isFullscreen = () => document.fullscreenElement === frame || frame.classList.contains("is-fullscreen");
  const updateFullscreenButton = () => {
    const fullscreen = isFullscreen();
    fullscreenButton.setAttribute("aria-label", fullscreen ? "Exit full screen" : "View map full screen");
    fullscreenButton.title = fullscreen ? "Exit full screen" : "View full screen";
  };
  const exitFallback = () => {
    frame.classList.remove("is-fullscreen");
    document.documentElement.classList.remove("spatial-long-exposure-fullscreen-active");
  };
  const toggleFullscreen = async () => {
    if (document.fullscreenElement === frame) {
      await document.exitFullscreen();
      return;
    }
    if (frame.classList.contains("is-fullscreen")) {
      exitFallback();
    } else {
      try {
        if (frame.requestFullscreen) {
          await frame.requestFullscreen();
          return;
        }
      } catch {
        // The fixed-position fallback below.
      }
      frame.classList.add("is-fullscreen");
      document.documentElement.classList.add("spatial-long-exposure-fullscreen-active");
    }
    updateFullscreenButton();
    requestAnimationFrame(() => map.resize());
  };
  fullscreenButton.hidden = false;
  fullscreenButton.addEventListener("click", toggleFullscreen);
  document.addEventListener("fullscreenchange", () => {
    updateFullscreenButton();
    requestAnimationFrame(() => map.resize());
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && frame.classList.contains("is-fullscreen")) {
      event.preventDefault();
      exitFallback();
      updateFullscreenButton();
      requestAnimationFrame(() => map.resize());
    }
  });
}
