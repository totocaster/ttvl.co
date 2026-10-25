// Walks: the map is the page. The panel holds the index (rendered by the
// layout: the head, place switches, every walk as a row) or the chosen
// walk's sheet; a walk is picked from a row or a route, a place switch
// narrows both, and #walk-s0399 or #walk-s0399/photo-3 opens one. The sheet
// draws the walk's day hour by hour (walks-day.js); moving through it, by
// hand or by scrolling, walks a lamp along the route.
// docs/walks.md.

import {WalkMap} from "./walks-map.js";
import {Day, clock} from "./walks-day.js";

const root = document.querySelector("[data-walks]");
const $ = (selector) => root.querySelector(selector);
const $$ = (selector) => [...root.querySelectorAll(selector)];
const data = JSON.parse(document.getElementById("walks-data").textContent);
const panel = $("[data-panel]");
const index = $("[data-index]");
const sheet = $("[data-sheet]");
const list = $("[data-list]");
const narrow = matchMedia("(max-width: 768px)");
const reducedMotion = () => matchMedia("(prefers-reduced-motion: reduce)").matches;
const STRIDE = 0.75; // metres a step, for the walker's 170 cm
let place = null;
let chosen = null;
let indexScroll = 0;

// The layout's full-window form needs the script: until it runs, the index
// and the records below it are an ordinary page.
root.dataset.ready = "";

// The map runs up under the masthead and fades into the ground there; the
// panel, the keys, and every fit keep below it.
const masthead = document.querySelector("header.site");
function measure() {
  const style = document.documentElement.style;
  style.setProperty("--walks-masthead", `${masthead.offsetHeight}px`);
  style.setProperty("--walks-top", `${root.getBoundingClientRect().top + scrollY}px`);
}
measure();
addEventListener("resize", measure);

function el(tag, props = {}, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(props)) {
    if (value === null || value === undefined || value === false) continue;
    if (key === "class") node.className = value;
    else if (key === "text") node.textContent = value;
    else if (key === "dataset") Object.assign(node.dataset, value);
    else node.setAttribute(key, value === true ? "" : value);
  }
  node.append(...children.flat().filter((child) => child !== null && child !== undefined && child !== false));
  return node;
}

const n = (text) => el("span", {class: "n", text: String(text)});
const time = (iso, text = iso) => el("time", {datetime: iso, text});
const pad = (value, width = 3) => String(value).padStart(width, "0");

// Parts joined with " · ", skipping empty ones.
function joined(...parts) {
  const frag = document.createDocumentFragment();
  parts.filter((part) => part !== null && part !== undefined && part !== "").forEach((part, i) => {
    if (i) frag.append(" · ");
    frag.append(part);
  });
  return frag;
}

// A number and its noun in Mono and Sans: "19.5 km", "8 photographs".
function counted(value, unit) {
  const frag = document.createDocumentFragment();
  frag.append(n(value), ` ${unit}`);
  return frag;
}

const km = (walk) => (walk.distance_km === null ? null : counted(walk.distance_km, "km"));

// The archive: the layout's walks, each with its place, number, and middle,
// joined to its route.
const routes = await (await fetch(data.routes)).json();
const features = new Map(routes.features.map((feature) => [feature.properties.walk, feature]));
const walks = data.walks.map((walk) => ({...walk, feature: features.get(walk.id)}));
// Each walk's day (tools/walks-day.py) arrives after the page answers; a
// sheet opened before it does is drawn again when it lands.
const days = fetch(data.days).then((response) => response.json()).then((file) => file.walks).catch(() => ({}));
const byId = new Map(walks.map((walk) => [walk.id, walk]));
const places = data.places.map((p) => ({...p, walks: walks.filter((walk) => walk.place === p.key)}));
const placeName = (key) => places.find((p) => p.key === key)?.name || "";
const visibleIds = () => walks.filter((walk) => !place || walk.place === place).map((walk) => walk.id);

// The fits keep clear of the masthead's fade and of the panel.
function clearance() {
  const top = masthead.offsetHeight;
  if (narrow.matches) return {top: top + 32, right: 64, bottom: 32, left: 32};
  // The panel stands at the container's edge; the zoom keys mirror it at right.
  const box = panel.getBoundingClientRect();
  return {top: top + 48, right: Math.round(box.left + 80), bottom: 48, left: Math.round(box.right + 48)};
}

const map = new WalkMap($("[data-map]"), {walks, routes, places}, {
  cooperative: narrow.matches, // phones scroll the page, so two fingers move the map there
  onHover: (id) => light(id, "map"),
  onSelect: (id) => open(id),
  onPhoto: (walkId, photoId) => openPhoto(photoId),
  onPhotoHover: (photoId) => {
    $$(".walks-gallery figure").forEach((figure) => figure.classList.toggle("is-lit", figure.dataset.photoId === photoId));
    hoverPhoto(day.placed?.find((p) => p.photo.id === photoId) || null, {move: false});
  },
  onPlace: (key) => { if (chosen) close({fit: false}); setPlace(key); },
  onFail: () => {
    const badge = $("[data-readout]");
    badge.textContent = "The map could not load. Every walk and its record are still here.";
    badge.hidden = false;
  },
  padding: clearance,
});

// The walk under the hand lights its row and its route; its row names it,
// so the map carries no badge of its own (the corner speaks only when the
// map fails).
function light(id, from) {
  for (const li of list.children) li.classList.toggle("is-lit", li.dataset.walk === id);
  if (from === "list") map.setHover(id);
  if (from === "map" && id && !chosen) scrollRow(list.querySelector(`[data-walk="${id}"]`));
}

// Keep a lit row in view inside the panel's own scroll.
function scrollRow(li) {
  if (!li || narrow.matches) return;
  const top = li.getBoundingClientRect().top - panel.getBoundingClientRect().top;
  if (top < 16 || top > panel.clientHeight - 48) panel.scrollTo({top: panel.scrollTop + top - panel.clientHeight / 3, behavior: reducedMotion() ? "instant" : "smooth"});
}

for (const li of list.children) {
  const link = li.querySelector(".row-title");
  li.addEventListener("mouseenter", () => light(li.dataset.walk, "list"));
  li.addEventListener("mouseleave", () => light(null, "list"));
  link.addEventListener("focus", () => light(li.dataset.walk, "list"));
  link.addEventListener("blur", () => light(null, "list"));
  link.addEventListener("click", (event) => {
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    open(li.dataset.walk);
  });
}

for (const key of $$("[data-places] .switch-key")) {
  key.addEventListener("click", () => setPlace(place === key.dataset.place ? null : key.dataset.place));
}

function setPlace(key, {fit = true} = {}) {
  place = key;
  for (const button of $$("[data-places] .switch-key")) button.setAttribute("aria-pressed", String(button.dataset.place === key));
  const ids = visibleIds();
  for (const li of list.children) li.hidden = !ids.includes(li.dataset.walk);
  $("[data-list-label]").textContent = key ? `${placeName(key)}, newest first` : "Every walk, newest first";
  map.setVisible(key ? ids : null);
  if (fit) map.fitIds(ids);
}

// Photographs the day cannot hold (no time, no place): small thumbs in
// their own shape that the shared lightbox opens. The lightbox reads the
// full picture from src; the browser fetches the thumb. Each carries its id,
// so a marker and a thumb can find each other.
function gallery(walk, photos) {
  const grid = el("div", {class: "walks-gallery", "data-lightbox-gallery": true}, photos.map((photo) => {
    const figure = el("figure", {dataset: {photoId: photo.id}},
      el("a", {href: photo.src, "data-date": walk.date, "aria-label": `Photograph ${photo.sequence}, enlarge`},
        el("img", {src: photo.src, srcset: `${photo.thumb} 360w, ${photo.src} 1600w`, sizes: "96px", alt: photo.alt, loading: "lazy", width: photo.width, height: photo.height})),
      el("figcaption", {}, n(pad(photo.sequence, 2))));
    figure.addEventListener("mouseenter", () => map.lightPhoto(photo.id));
    figure.addEventListener("mouseleave", () => map.lightPhoto(null));
    return figure;
  }));
  return grid;
}

// A walk's video: the site's YouTube embed (layouts/shortcodes/youtube.html),
// with a way out to YouTube under it.
function video({youtube, title}) {
  const frag = document.createDocumentFragment();
  frag.append(
    el("div", {class: "video-container walks-video"},
      el("iframe", {src: `https://www.youtube.com/embed/${youtube}`, title, allow: "encrypted-media; fullscreen; picture-in-picture", allowfullscreen: true, loading: "lazy"})),
    el("p", {class: "legend"}, el("a", {href: `https://www.youtube.com/watch?v=${youtube}`, text: `${title} on YouTube ↗`})));
  return frag;
}

function openPhoto(photoId) {
  const link = sheet.querySelector(`[data-photo-id="${photoId}"] a`);
  if (link) document.dispatchEvent(new CustomEvent("lightbox:open", {detail: {link, trigger: link}}));
}

// Details, under the day and the journal: when (from the recording), how
// far and how many steps, the time on foot and the ground (from the day),
// the weather (from the journal), and the camera and frames (from the
// photographs and their session).
const weekday = (iso) => new Date(`${iso}T12:00:00`).toLocaleDateString("en-GB", {weekday: "long"});
const fmt = new Intl.NumberFormat("en-US");
const signed = (value) => `${value < 0 ? "−" : ""}${fmt.format(Math.abs(value))}`;
const N = (value) => `<span class="n">${value}</span>`;
function duration(minutes) {
  const frag = document.createDocumentFragment();
  minutes = Math.round(minutes);
  const hours = Math.floor(minutes / 60), rest = minutes % 60;
  if (hours) frag.append(counted(hours, "h"));
  if (hours && rest) frag.append(" ");
  if (rest || !hours) frag.append(counted(rest, "min"));
  return frag;
}
const cameraName = (name) => name.trim().replace(/^LEICA\b/, "Leica").replace(/^RICOH\b/, "Ricoh");

const note = (...parts) => el("span", {class: "walks-facts-note"}, ...parts);

function facts(walk, today) {
  const rows = [];
  const add = (label, ...value) => rows.push(el("dt", {text: label}), el("dd", {}, ...value));
  add("Date", `${weekday(walk.date)} `, time(walk.date));
  if (walk.started && walk.minutes && walk.recording !== "Sparse recording") {
    const span = document.createDocumentFragment();
    span.append(n(walk.started), "–", n(walk.ended));
    add("Time", joined(span, duration(walk.minutes)));
  }
  add("Distance", km(walk) || "Not measured");
  // Steps are distance over a stride; nothing on the walks counted them.
  if (walk.distance_km) add("Steps", "≈ ", n(fmt.format(Math.round(walk.distance_km * 1000 / STRIDE / 100) * 100)));
  if (today) {
    const stops = today.runs.filter(([a, b, state]) => state === "s" && b - a >= 4).length;
    add("On foot", "Walking ", duration(today.walking), ", standing ", duration(today.standing),
      note(stops ? joined(counted(stops, stops === 1 ? "stop" : "stops"), "four minutes or longer") : "No stop of four minutes or longer"));
    // The ground from the survey model, never the GPS.
    let below = 0;
    const S = today.samples;
    for (let i = 1; i < S.length; i++) if (S[i][4] !== null && S[i][4] < 0 && S[i][5] === S[i - 1][5]) below += S[i][2] - S[i - 1][2];
    const range = document.createDocumentFragment();
    range.append(n(signed(today.low)), "–", n(signed(today.high)), " m");
    add("Ground", "Climbed ", counted(fmt.format(today.climb), "m"), " · ", range, below > 300 ? note(n((below / 1000).toFixed(1)), " km below sea level") : null);
  }
  const weather = walk.weather?.match(/^(-?\d+) °C\s*(.*)$/);
  if (weather) add("Weather", counted(weather[1], "°C"), weather[2] ? `, ${weather[2].toLowerCase()}` : "");
  const cameras = [...new Set(walk.photos.map((photo) => photo.camera).filter(Boolean).map(cameraName))];
  if (cameras.length || walk.film) add(cameras.length > 1 ? "Cameras" : "Camera", cameras.join(", ") || "Film");
  if (today?.frames_total) add("Frames", counted(today.frames_total, "in the session"), ", ", counted(walk.photos.length, "here"));
  return el("dl", {class: "walks-facts"}, rows);
}

// The photographs the day can hold: those with a time, or a place on the
// route (their time then comes from the recording). A photograph with a
// time but no place is set on the route by its time, approximately.
function placedPhotos(walk, today) {
  const S = today.samples;
  const nearest = ([lon, lat]) => {
    const k = Math.cos(lat * Math.PI / 180);
    let best = null, bd = Infinity;
    for (const s of S) {
      if (s[3] === null) continue;
      const d = ((s[0] - lon) * k) ** 2 + (s[1] - lat) ** 2;
      if (d < bd) { bd = d; best = s; }
    }
    return Math.sqrt(bd) * 111320 < 400 ? best : null;
  };
  const placed = [];
  for (const photo of walk.photos) {
    let t = null;
    if (photo.time) {
      const [h, m] = photo.time.split(":").map(Number);
      t = ((h * 60 + m) - today.t0) * 60;
    } else if (photo.coordinates) t = nearest(photo.coordinates)?.[3] ?? null;
    if (t === null || t < -900 || t > today.T + 900) continue;
    t = Math.max(0, Math.min(today.T, t));
    placed.push({photo, t, lonlat: photo.coordinates || stateAt(today, t).lonlat, approx: !photo.coordinates});
  }
  return placed.sort((a, b) => a.t - b.t);
}

// The sheet: the chosen walk's record, set for the panel. The day needs its
// data; without it (a sparse recording, or while it loads) the photographs
// are a gallery.
function renderSheet(walk, today = null) {
  const back = el("button", {type: "button", class: "btn btn--quiet walks-back", text: "← All walks"});
  back.addEventListener("click", () => close());
  const section = (title, ...body) => el("section", {class: "walks-section"}, el("h3", {class: "walks-heading", text: title}), ...body);
  const paragraphs = walk.journal?.paragraphs || [];
  const links = walk.links.map((link) => {
    const [kind, ...rest] = link.title.split(" · ");
    return el("li", {class: "row"},
      el("span", {class: "row-meta", text: rest.length ? kind : "Page"}),
      el("span", {class: "row-main"}, el("a", {class: "row-title", href: link.url, text: rest.join(" · ") || kind})));
  });
  const placed = today ? placedPhotos(walk, today) : [];
  const loose = walk.photos.filter((photo) => !placed.some((p) => p.photo === photo));
  sheet.hidden = false;
  const hours = today ? day.render(walk, today, placed, sheet.clientWidth || 336) : null;
  if (!hours) day.clear();
  const looseNote = !walk.photos.length ? "Photographs from this walk have not been matched yet."
    : placed.length ? "No time or place was recorded for these photographs."
    : walk.film ? "Film photographs, in the order of the roll; the scans carry no time or place." : null;
  sheet.replaceChildren(...[
    back,
    el("div", {class: "walks-rail"}, el("p", {}, joined(n(pad(walk.number)), placeName(walk.place)))),
    el("h2", {class: "walks-title", tabindex: "-1", text: walk.title}),
    walk.summary ? el("p", {class: "walks-summary", text: walk.summary}) : null,
    walk.video ? section("On Video", video(walk.video)) : null,
    hours,
    loose.length || !walk.photos.length ? section(placed.length ? "Without a Time or Place" : "Along the Way",
      loose.length ? gallery(walk, loose) : null, looseNote ? el("p", {class: "legend", text: looseNote}) : null) : null,
    paragraphs.length ? section("From the Journal",
      el("blockquote", {class: "walks-journal"}, paragraphs.map((text) => el("p", {text}))),
      walk.places.length ? el("p", {class: "legend", text: `Places in the entry: ${walk.places.join(" · ")}`}) : null) : null,
    section("Details", facts(walk, today)),
    links.length ? section("Elsewhere", el("ul", {class: "rows walks-links"}, links)) : null,
  ].filter(Boolean));
}

// ---------- the day: time, the lamp, the photographs ----------
// cur: seconds since the walk's first recorded point.
let cur = 0, hovered = null;

// Where the walk was at t: position, distance, ground, what it was doing,
// the neighborhood, and a river under foot.
function stateAt(today, t) {
  const S = today.samples;
  let a = 0, b = S.length - 1;
  if (t <= (S[0][3] ?? 0)) b = 0;
  else if (t >= (S[b][3] ?? 0)) a = b;
  else while (b - a > 1) { const m = (a + b) >> 1; if ((S[m][3] ?? 0) <= t) a = m; else b = m; }
  const p = S[a], q = S[b];
  let lon = p[0], lat = p[1], cum = p[2], ele = p[4], gap = false;
  if (a !== b && p[5] === q[5] && q[3] > p[3]) {
    const f = (t - p[3]) / (q[3] - p[3]);
    lon += f * (q[0] - p[0]); lat += f * (q[1] - p[1]); cum += f * (q[2] - p[2]);
    if (p[4] !== null && q[4] !== null) ele += f * (q[4] - p[4]);
  } else if (a !== b) gap = true;
  const local = today.t0 + t / 60;
  const run = today.runs.find(([from, to]) => local >= from && local <= to);
  const hood = today.hoods.find(([from, to]) => cum >= from - 100 && cum <= to + 100) || null;
  const river = today.rivers.find(([at]) => Math.abs(at - cum) < 80);
  return {lonlat: [lon, lat], cum, ele, gap, run, hood, river: river?.[1], clock: clock(local)};
}

function describe(today, t) {
  const st = stateAt(today, t);
  const standing = st.run?.[2] === "s" && st.run[1] - st.run[0] >= 2 ? ` ${N(Math.round(st.run[1] - st.run[0]))} min` : "";
  const doing = st.gap ? "not recorded" : st.run?.[2] === "s" ? `standing${standing}` : st.river ? `crossing the ${st.river.replace(/ River$/, "")}` : "walking";
  return `<b>${N(st.clock)}</b> · ${N((st.cum / 1000).toFixed(1))} km · ≈ ${N(fmt.format(Math.round(st.cum / STRIDE / 50) * 50))} steps<br>${N(st.ele !== null ? signed(Math.round(st.ele)) : "–")} m · ${doing}${st.hood ? ` in ${st.hood[2]}` : ""}`;
}

const day = new Day({
  onScrub: (t) => setTime(t),
  onPhoto: (placed) => hoverPhoto(placed, {move: true}),
  describe: (t) => (chosen && byId.get(chosen).day ? describe(byId.get(chosen).day, t) : ""),
});

// The photograph under the hand, or else the one last passed, is the live one.
function activePhoto() {
  if (hovered) return hovered;
  const passed = (day.placed || []).filter((p) => p.t <= cur + 20);
  return passed.at(-1) || null;
}

function setTime(t) {
  const walk = chosen && byId.get(chosen);
  if (!walk?.day || !day.chart) return;
  cur = Math.max(0, Math.min(walk.day.T, t));
  const st = stateAt(walk.day, cur);
  map.setLamp(st.lonlat);
  const active = activePhoto();
  map.lightPhoto(active?.photo.id || null);
  day.setTime(cur, st, active);
}

// A photograph under the hand, in the sheet or on the map, rings its spot;
// from the sheet it also moves the day to its moment.
function hoverPhoto(placed, {move}) {
  hovered = placed;
  map.setSpot(placed ? placed.lonlat : null);
  if (placed && move) setTime(placed.t);
  else setTime(cur);
}

// Reading down the day walks the route: with the hand off the clock, the
// cursor sits where the reading line crosses the day, two fifths of the way
// down what scrolls (the panel on wide screens, the page on phones).
function readingLine() {
  if (narrow.matches) return innerHeight * 0.42;
  const box = panel.getBoundingClientRect();
  return box.top + box.height * 0.42;
}
function followReading() {
  if (!chosen || day.inChart || !day.chart) return;
  const line = readingLine(), box = day.box.getBoundingClientRect();
  if (line < box.top || line > box.bottom) return;
  setTime(day.tOf(line - box.top));
}
panel.addEventListener("scroll", followReading, {passive: true});
addEventListener("scroll", () => { if (narrow.matches) followReading(); }, {passive: true});

function writeHash(hash) {
  if (location.hash !== hash) history.pushState(null, "", hash || location.pathname + location.search);
}

// The day starts at the walk's first point, or at a linked photograph's moment.
function startDay(walk, photoId = null) {
  const linked = photoId && day.placed?.find((p) => p.photo.id === photoId);
  setTime(linked ? linked.t : 0);
  if (!walk.day) map.setLamp(null);
}

function open(id, {fit = true, hash = true, animate = true, photo = null} = {}) {
  const walk = byId.get(id);
  if (!walk) return;
  if (!chosen) indexScroll = panel.scrollTop;
  chosen = id;
  hovered = null;
  map.setSpot(null);
  for (const li of list.children) li.toggleAttribute("aria-current", li.dataset.walk === id);
  index.hidden = true;
  renderSheet(walk, walk.day);
  panel.scrollTop = 0;
  // On phones the sheet follows the map down the page: bring the map back
  // into view so the walk is seen before it is read.
  if (narrow.matches && animate) $("[data-map]").scrollIntoView({block: "start", behavior: reducedMotion() ? "instant" : "smooth"});
  map.setChosen(id);
  startDay(walk, photo);
  // Opened before the days arrived: draw the sheet again once they have.
  if (walk.day === undefined) days.then(() => {
    if (chosen !== id) return;
    renderSheet(walk, walk.day);
    startDay(walk, photo);
  });
  if (fit) map.fitIds([id], {animate});
  light(null);
  sheet.querySelector(".walks-title").focus({preventScroll: true});
  if (hash) writeHash(`#walk-${id}`);
}

function close({fit = true, hash = true} = {}) {
  const was = chosen;
  chosen = null;
  hovered = null;
  day.clear();
  map.setLamp(null);
  map.setSpot(null);
  for (const li of list.children) li.removeAttribute("aria-current");
  sheet.hidden = true;
  sheet.replaceChildren();
  index.hidden = false;
  panel.scrollTop = indexScroll;
  map.setChosen(null);
  if (fit) map.fitIds(visibleIds());
  light(null);
  if (hash) writeHash("");
  list.querySelector(`[data-walk="${was}"] .row-title`)?.focus({preventScroll: true});
}

// Escape closes the sheet, unless the lightbox is open over it.
document.addEventListener("keydown", (event) => {
  if (event.key !== "Escape" || !chosen || document.querySelector(".lightbox")) return;
  if (event.target.closest?.("input, textarea, select, [contenteditable]")) return;
  close();
}, true); // capture: runs before the lightbox's own Escape removes it

function readHash() {
  const match = location.hash.match(/^#walk-([a-z0-9-]+)(?:\/(photo-\d+))?$/);
  return match && byId.has(match[1]) ? {walk: match[1], photo: match[2] || null} : null;
}

// The panel answers at once; the map frames the walk or Tokyo once it loads.
days.then((all) => { for (const walk of walks) walk.day = all[walk.id] || null; });
setPlace(null, {fit: false});
const first = readHash();
if (first) open(first.walk, {hash: false, animate: false, fit: false, photo: first.photo});
map.ready.then(() => {
  if (!first) return map.fitPlace("tokyo", {animate: false});
  if (chosen !== first.walk) return;
  const photo = first.photo && byId.get(first.walk).photos.find((p) => p.id === first.photo);
  if (photo?.coordinates) map.map.jumpTo({center: photo.coordinates, zoom: 16, padding: clearance()});
  else map.fitIds([first.walk], {animate: false});
  if (photo) {
    map.lightPhoto(photo.id);
    sheet.querySelector(`[data-photo-id="${photo.id}"]`)?.classList.add("is-lit");
  }
});
addEventListener("hashchange", () => {
  const hash = readHash();
  if (hash) { if (hash.walk !== chosen) open(hash.walk, {hash: false}); }
  else if (chosen) close({hash: false});
});
addEventListener("resize", () => map.resize());
