// Walks: the map is the page. The panel holds the index (rendered by the
// layout: the head, place switches, every walk as a row) or the chosen
// walk's sheet; a walk is picked from a row or a route, a place switch
// narrows both, and #walk-s0399 or #walk-s0399/photo-3 opens one.
// docs/walks.md.

import {WalkMap} from "./walks-map.js";

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
const photoCount = (walk) => (walk.photos.length ? counted(walk.photos.length, walk.photos.length === 1 ? "photograph" : "photographs") : null);

// The archive: the layout's walks, each with its place, number, and middle,
// joined to its route.
const routes = await (await fetch(data.routes)).json();
const features = new Map(routes.features.map((feature) => [feature.properties.walk, feature]));
const walks = data.walks.map((walk) => ({...walk, feature: features.get(walk.id)}));
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
  return {top: top + 48, right: Math.round(box.left + 80), bottom: 72, left: Math.round(box.right + 48)};
}

const map = new WalkMap($("[data-map]"), {walks, routes, places}, {
  cooperative: narrow.matches, // phones scroll the page, so two fingers move the map there
  onHover: (id) => light(id, "map"),
  onSelect: (id) => open(id),
  onPhoto: (walkId, photoId) => openPhoto(photoId),
  onPhotoHover: (photoId) => $$(".walks-gallery figure").forEach((figure) => figure.classList.toggle("is-lit", figure.dataset.photoId === photoId)),
  onPlace: (key) => { if (chosen) close({fit: false}); setPlace(key); },
  onFail: () => {
    const badge = $("[data-readout]");
    badge.textContent = "The map could not load. Every walk and its record are still here.";
    badge.hidden = false;
  },
  padding: clearance,
});

// The badge at the map's corner names the walk under the hand; the open
// one is named by its sheet, so with nothing under the hand it is hidden.
function light(id, from) {
  for (const li of list.children) li.classList.toggle("is-lit", li.dataset.walk === id);
  if (from === "list") map.setHover(id);
  const walk = byId.get(id);
  const badge = $("[data-readout]");
  if ($("[data-map]").dataset.mapState === "failed") return;
  badge.replaceChildren(walk ? joined(n(pad(walk.number)), time(walk.date), walk.title, km(walk), photoCount(walk)) : "");
  badge.hidden = !walk;
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

// Photographs: 4:3 tiles the shared lightbox opens; each carries its id,
// so a marker and a tile can find each other.
function gallery(walk) {
  if (!walk.photos.length) return el("p", {class: "legend", text: "Photographs from this walk have not been matched yet."});
  const grid = el("div", {class: "walks-gallery", "data-lightbox-gallery": true}, walk.photos.map((photo) => {
    const figure = el("figure", {dataset: {photoId: photo.id}},
      el("a", {href: photo.src, "data-date": walk.date, "aria-label": `Photograph ${photo.sequence}, enlarge`},
        el("img", {src: photo.src, alt: photo.alt, loading: "lazy", width: photo.width, height: photo.height})),
      el("figcaption", {}, joined(n(pad(photo.sequence, 2)), photo.time ? time(photo.captured, photo.time) : null, photo.coordinates ? null : "Not placed")));
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

// The day at a glance: when (from the recording), how far, the weather (from
// the journal), and the camera (from the photographs).
const weekday = (iso) => new Date(`${iso}T12:00:00`).toLocaleDateString("en-GB", {weekday: "long"});
function duration(minutes) {
  const frag = document.createDocumentFragment();
  const hours = Math.floor(minutes / 60), rest = minutes % 60;
  if (hours) frag.append(counted(hours, "h"));
  if (hours && rest) frag.append(" ");
  if (rest || !hours) frag.append(counted(rest, "min"));
  return frag;
}
const cameraName = (name) => name.trim().replace(/^LEICA\b/, "Leica").replace(/^RICOH\b/, "Ricoh");

function facts(walk) {
  const rows = [];
  const add = (label, ...value) => rows.push(el("dt", {text: label}), el("dd", {}, ...value));
  add("Date", `${weekday(walk.date)} `, time(walk.date));
  if (walk.started && walk.minutes && walk.recording !== "Sparse recording") {
    const span = document.createDocumentFragment();
    span.append(n(walk.started), "–", n(walk.ended));
    add("Time", joined(span, duration(walk.minutes)));
  }
  add("Distance", km(walk) || "Not measured");
  const weather = walk.weather?.match(/^(-?\d+) °C\s*(.*)$/);
  if (weather) add("Weather", counted(weather[1], "°C"), weather[2] ? `, ${weather[2].toLowerCase()}` : "");
  const cameras = [...new Set(walk.photos.map((photo) => photo.camera).filter(Boolean).map(cameraName))];
  if (cameras.length || walk.film) add(cameras.length > 1 ? "Cameras" : "Camera", cameras.join(", ") || "Film");
  return el("dl", {class: "walks-facts"}, rows);
}

// The sheet: the chosen walk's record, set for the panel.
function renderSheet(walk) {
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
  sheet.replaceChildren(...[
    back,
    el("div", {class: "walks-rail"}, el("p", {}, joined(n(pad(walk.number)), placeName(walk.place)))),
    el("h2", {class: "walks-title", tabindex: "-1", text: walk.title}),
    walk.summary ? el("p", {class: "walks-summary", text: walk.summary}) : null,
    facts(walk),
    walk.video ? section("On Video", video(walk.video)) : null,
    section("Along the Way", gallery(walk)),
    paragraphs.length ? section("From the Journal",
      el("blockquote", {class: "walks-journal"}, paragraphs.map((text) => el("p", {text}))),
      walk.places.length ? el("p", {class: "legend", text: `Places in the entry: ${walk.places.join(" · ")}`}) : null) : null,
    links.length ? section("Elsewhere", el("ul", {class: "rows walks-links"}, links)) : null,
  ].filter(Boolean));
}

function writeHash(hash) {
  if (location.hash !== hash) history.pushState(null, "", hash || location.pathname + location.search);
}

function open(id, {fit = true, hash = true, animate = true} = {}) {
  const walk = byId.get(id);
  if (!walk) return;
  if (!chosen) indexScroll = panel.scrollTop;
  chosen = id;
  for (const li of list.children) li.toggleAttribute("aria-current", li.dataset.walk === id);
  renderSheet(walk);
  index.hidden = true;
  sheet.hidden = false;
  panel.scrollTop = 0;
  // On phones the sheet follows the map down the page: bring the map back
  // into view so the walk is seen before it is read.
  if (narrow.matches && animate) $("[data-map]").scrollIntoView({block: "start", behavior: reducedMotion() ? "instant" : "smooth"});
  map.setChosen(id);
  if (fit) map.fitIds([id], {animate});
  light(null);
  sheet.querySelector(".walks-title").focus({preventScroll: true});
  if (hash) writeHash(`#walk-${id}`);
}

function close({fit = true, hash = true} = {}) {
  const was = chosen;
  chosen = null;
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
setPlace(null, {fit: false});
const first = readHash();
if (first) open(first.walk, {hash: false, animate: false, fit: false});
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
