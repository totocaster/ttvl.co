// A walk's day, down its sheet: the clock runs down the left, beside it the
// walking and standing, the shutter, and the ground (wider where it is
// higher); in the column at right, the photographs, neighborhoods, and
// rivers, each where it happened in time and joined to its moment by a
// hairline. The day's data comes from tools/walks-day.py. docs/walks.md.

const NS = "http://www.w3.org/2000/svg";
function svg(tag, attrs = {}, parent) {
  const node = document.createElementNS(NS, tag);
  for (const [key, value] of Object.entries(attrs)) if (value !== null && value !== undefined) node.setAttribute(key, value);
  if (parent) parent.append(node);
  return node;
}
function text(parent, x, y, value, attrs = {}) {
  const node = svg("text", {x, y, ...attrs}, parent);
  node.textContent = value;
  return node;
}
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const pad = (v, w = 2) => String(v).padStart(w, "0");
const minus = (v) => `${v < 0 ? "−" : ""}${Math.abs(v)}`;
export const clock = (m) => { m = ((Math.round(m) % 1440) + 1440) % 1440; return `${pad(Math.floor(m / 60))}:${pad(m % 60)}`; };

// Columns, in px from the timeline's left edge; the items' column is set in
// _walks.scss to match.
const COL = {clock: 40, bar: 46, barW: 6, shutter: 56, shutterW: 10, ground: 72, groundW: 100, items: 184};
const TOP = 14;
// A photograph's row: a small thumb in its own shape, at most 64 wide and
// 52 tall, its number beside it. The lightbox shows it whole.
const THUMB_W = 64, THUMB_H = 52;
function thumbSize(photo) {
  const ratio = photo.height / photo.width;
  return ratio <= THUMB_H / THUMB_W ? [THUMB_W, Math.round(THUMB_W * ratio)] : [Math.round(THUMB_H / ratio), THUMB_H];
}
const anchor = (item) => (item.kind === "photo" ? item.h / 2 : 11);

export class Day {
  // onScrub(t), onPhoto(placed|null), describe(t) → readout HTML
  constructor(options) {
    Object.assign(this, options);
    this.box = null;
  }

  // walk: the archive's record; day: its entry in days.json; placed:
  // [{photo, t, lonlat, approx}] for the photographs with a time or a place.
  render(walk, day, placed, width) {
    this.walk = walk;
    this.day = day;
    this.placed = placed;
    this.t = 0;
    const minutes = day.T / 60;
    const section = document.createElement("section");
    section.className = "walks-section walks-day";
    section.innerHTML = `<div class="walks-day-head"><h3 class="walks-heading">Hour by Hour</h3><p class="walks-day-readout" aria-live="polite"></p><ul class="chart-key walks-day-key"></ul></div><div class="walks-timeline" data-lightbox-gallery></div>`;
    this.readout = section.querySelector(".walks-day-readout");
    const box = section.querySelector(".walks-timeline");
    this.box = box;

    // What happened, in order of time, each with its height.
    const S = day.samples;
    const timeAt = (c) => { let a = 0, b = S.length - 1; while (b - a > 1) { const m = (a + b) >> 1; if (S[m][2] <= c) a = m; else b = m; } return S[a][3] ?? 0; };
    const items = [];
    for (const p of placed) {
      const [w, h] = thumbSize(p.photo);
      items.push({kind: "photo", t: p.t, w, h, p});
    }
    day.hoods.forEach(([a, b, name]) => items.push({kind: "hood", t: timeAt(a), h: 22, name, a}));
    for (const [at, name] of day.rivers) items.push({kind: "river", t: timeAt(at), h: 22, name});
    items.sort((x, y) => x.t - y.t || (x.kind === "photo") - (y.kind === "photo"));
    // The scale gives every item room near its moment: px a minute.
    const scale = clamp((items.reduce((sum, item) => sum + item.h + 6, 0) * 1.1) / Math.max(minutes, 1), 2, 10);
    const yOf = (t) => TOP + (t / 60) * scale;
    this.yOf = yOf;
    this.tOf = (y) => clamp(((y - TOP) / scale) * 60, 0, day.T);
    let bottom = 0;
    for (const item of items) {
      item.ideal = yOf(item.t);
      item.y = Math.max(item.ideal - anchor(item), bottom + (bottom ? 6 : 0));
      bottom = item.y + item.h;
    }
    const height = Math.max(yOf(day.T) + 24, bottom + 8);
    box.style.height = `${height}px`;
    const chart = svg("svg", {class: "walks-chart", width, height, viewBox: `0 0 ${width} ${height}`, "aria-hidden": "true"}, box);
    this.chart = chart;

    // The clock: hours, and half hours where there is room.
    const step = scale * 30 >= 64 ? 30 : 60;
    for (let m = Math.ceil(day.t0 / step) * step; m <= day.t0 + minutes; m += step) {
      const y = yOf((m - day.t0) * 60);
      svg("line", {x1: COL.clock + 2, x2: COL.bar - 2, y1: y + 0.5, y2: y + 0.5, class: "walks-chart-tick"}, chart);
      text(chart, COL.clock, y + 5, clock(m), {class: m % 60 ? "n is-half" : "n", "text-anchor": "end"});
    }
    // On foot: walking in ink, standing in tone 4, gaps in the recording dashed.
    for (const [a, b, state] of day.runs) {
      const ya = yOf((a - day.t0) * 60), yb = yOf((b - day.t0) * 60);
      if (state === "g") svg("line", {x1: COL.bar + COL.barW / 2, x2: COL.bar + COL.barW / 2, y1: ya, y2: yb, class: "walks-chart-gap"}, chart);
      else svg("rect", {x: COL.bar, y: ya, width: COL.barW, height: Math.max(0.6, yb - ya), class: state === "w" ? "walks-chart-walking" : "walks-chart-standing"}, chart);
    }
    // The shutter: every frame of the session a hairline, the published ones in ink.
    for (const t of day.frames) {
      if (t < 0 || t > day.T) continue;
      svg("line", {x1: COL.shutter, x2: COL.shutter + COL.shutterW, y1: yOf(t) + 0.5, y2: yOf(t) + 0.5, class: "walks-chart-frame"}, chart);
    }
    for (const p of placed) svg("line", {x1: COL.shutter - 2, x2: COL.shutter + COL.shutterW + 2, y1: yOf(p.t) + 0.5, y2: yOf(p.t) + 0.5, class: "walks-chart-published"}, chart);
    // The ground: height across, time down, stretched across the middle 90%
    // of the walk's own heights, so a city walk's few meters read as clearly
    // as a mountain's hundreds; the rare heights beyond rest at the edges.
    const ground = S.filter((s) => s[3] !== null && s[4] !== null);
    const sorted = ground.map((s) => s[4]).sort((a, b) => a - b), q = (f) => sorted[Math.round(f * (sorted.length - 1))];
    let lo = q(0.05), hi = q(0.95);
    if (hi - lo < 4) { const mid = (hi + lo) / 2; lo = mid - 2; hi = mid + 2; }
    const xOf = (v) => COL.ground + clamp((v - lo) / (hi - lo), 0, 1) * COL.groundW;
    this.xOf = xOf;
    if (lo < 0 && hi > 0) svg("line", {x1: xOf(0) + 0.5, x2: xOf(0) + 0.5, y1: TOP, y2: yOf(day.T), class: "walks-chart-sea"}, chart);
    let line = "", prev = null;
    for (const s of ground) { line += (prev && prev[5] === s[5] ? "L" : "M") + `${xOf(s[4]).toFixed(1)} ${yOf(s[3]).toFixed(1)}`; prev = s; }
    const area = `M${COL.ground} ${yOf(ground[0][3]).toFixed(1)}` + ground.map((s) => `L${xOf(s[4]).toFixed(1)} ${yOf(s[3]).toFixed(1)}`).join("") + `L${COL.ground} ${yOf(ground.at(-1)[3]).toFixed(1)}Z`;
    svg("path", {d: area, class: "walks-chart-area"}, chart);
    svg("path", {d: line, class: "walks-chart-ground"}, chart);
    for (const p of placed) {
      const s = ground.reduce((b, g) => Math.abs(g[3] - p.t) < Math.abs(b[3] - p.t) ? g : b, ground[0]);
      svg("circle", {cx: xOf(s[4]), cy: yOf(p.t), r: 3, class: "walks-chart-dot"}, chart);
    }
    // Hairlines from each moment to its item.
    for (const item of items) {
      item.leader = svg("path", {d: `M${COL.ground + COL.groundW + 2} ${item.ideal}H${COL.items - 14}L${COL.items - 4} ${item.y + anchor(item)}`, class: "walks-chart-leader"}, chart);
    }
    // The cursor: a rule across the clock and the ground, its time on a knockout, the lamp.
    this.cursor = svg("line", {x1: COL.clock + 2, x2: COL.ground + COL.groundW + 4, class: "walks-chart-cursor"}, chart);
    this.tag = text(chart, COL.clock, 0, "", {class: "n walks-chart-tag", "text-anchor": "end"});
    this.lamp = svg("circle", {r: 4.5, class: "walks-chart-lamp"}, chart);
    this.height = text(chart, 0, 0, "", {class: "n walks-chart-height"});

    // The column of things that happened.
    for (const item of items) {
      let node;
      if (item.kind === "photo") {
        const {photo, approx} = item.p;
        node = document.createElement("figure");
        node.className = "walks-moment walks-moment--photo";
        node.dataset.photoId = photo.id;
        // The lightbox reads the full picture from src; the browser fetches the thumb.
        node.innerHTML = `<a href="${photo.src}" data-date="${walk.date}"><img src="${photo.src}" srcset="${photo.thumb} 360w, ${photo.src} 1600w" sizes="64px" alt="" width="${item.w}" height="${item.h}" style="width:${item.w}px;height:${item.h}px" loading="lazy"></a><figcaption><span class="n">${pad(photo.sequence)}</span>${approx ? ` <span class="walks-moment-approx" title="Placed on the route by its time">≈</span>` : ""}</figcaption>`;
        node.querySelector("a").setAttribute("aria-label", `Photograph ${photo.sequence}${photo.time ? `, ${photo.time}` : ""}, enlarge`);
        node.querySelector("img").alt = photo.alt || "";
        node.style.height = `${item.h}px`;
        node.addEventListener("mouseenter", () => this.onPhoto(item.p));
        node.addEventListener("mouseleave", () => this.onPhoto(null));
        node.querySelector("a").addEventListener("focus", () => this.onPhoto(item.p));
        node.querySelector("a").addEventListener("blur", () => this.onPhoto(null));
        item.p.el = node;
      } else {
        node = document.createElement("p");
        node.className = `walks-moment walks-moment--${item.kind}`;
        node.textContent = item.kind === "river" ? `Over the ${item.name.replace(/ River$/, "")}` : item.name;
      }
      node.style.top = `${item.y}px`;
      item.el = node;
      box.append(node);
    }
    this.items = items;

    // The key: swatches shaped like the marks, one line. The ground's height
    // is not in it: it follows the cursor, in small type beside the lamp.
    const key = [
      `<li><i class="walks-key-walking"></i>Walking</li>`,
      `<li><i class="walks-key-standing"></i>Standing</li>`,
      day.frames.length ? `<li><i class="walks-key-shutter"></i>Shutter</li>` : "",
      `<li><i class="walks-key-ground"></i>Ground</li>`,
    ];
    section.querySelector(".walks-day-key").innerHTML = key.join("");

    // Scrubbing: anywhere over the clock and the ground.
    this.inChart = false;
    const scrub = (event) => {
      const r = box.getBoundingClientRect();
      this.inChart = event.clientX - r.left < COL.items - 8;
      if (!this.inChart) return;
      if (event.type === "pointermove" && event.buttons === 0 && event.pointerType !== "mouse") return;
      this.onScrub(this.tOf(event.clientY - r.top));
    };
    box.addEventListener("pointermove", scrub);
    box.addEventListener("pointerdown", scrub);
    box.addEventListener("pointerleave", () => { this.inChart = false; });
    return section;
  }

  clear() {
    this.box = null;
    this.chart = null;
    this.placed = [];
  }

  // The cursor, the lamp, and what is lit: the photograph last passed (or
  // under the hand) and the neighborhood the walk is in.
  setTime(t, state, active) {
    if (!this.chart) return;
    this.t = t;
    const y = this.yOf(t);
    this.cursor.setAttribute("y1", y + 0.5);
    this.cursor.setAttribute("y2", y + 0.5);
    this.tag.setAttribute("y", y + 5);
    this.tag.textContent = state.clock;
    if (state.ele !== null) {
      const x = this.xOf(state.ele);
      this.lamp.setAttribute("cx", x);
      this.lamp.setAttribute("cy", y);
      // The height under the cursor, just above the rule, on the side of the
      // lamp with room.
      const right = x < COL.ground + COL.groundW - 34;
      this.height.textContent = `${minus(Math.round(state.ele))} m`;
      this.height.setAttribute("x", right ? x + 7 : x - 7);
      this.height.setAttribute("y", y - 5);
      this.height.setAttribute("text-anchor", right ? "start" : "end");
    } else this.height.textContent = "";
    for (const item of this.items) {
      const lit = item.kind === "photo" ? item.p === active : item.kind === "hood" && state.hood?.[0] === item.a;
      item.el.classList.toggle("is-lit", lit);
      item.leader.classList.toggle("is-lit", lit);
    }
    this.readout.innerHTML = this.describe(t);
  }
}
