// Instagram Stories: the sea, the loupe, and the time key. The sea is every
// day of stories as a 33 x 59 tile, newest at the top, laid out so its days
// fill the page's container and repeats fill the window beyond it. A lens
// follows a fine pointer (or the arrow keys) at three times and names the day
// under its center; a click or Enter opens the time key over the sea, which
// plays the day's videos from the Space and steps through time. docs/stories.md.

const TW = 33;
const TH = 59;
const GAP = 2;
const PX = TW + GAP;
const PY = TH + GAP;
const ZOOM = 3;
const R = 150; // the lens's radius
const EPOCH = Date.UTC(2017, 11, 1);
const DOW = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
const PLAY = 'M4.5 2.75v10.5l8.5-5.25z';
const PAUSE = 'M5.25 3v10M10.75 3v10';

const root = document.querySelector('[data-stories]');
if (root) init(root);

function init(root) {
  const data = JSON.parse(root.querySelector('#stories-data').textContent);
  const S = data.story.map((s, i) => ({
    i, date: s[0], time: s[1], dur: s[2] / 10, audio: s[3] === 1, month: s[4], slot: s[5],
    place: data.places[s[6]], video: data.media + s[7],
  }));
  const D = data.day.map(([date, sheet, row, ids], k) => ({ k, date, year: date.slice(0, 4), sheet, row, ids }));
  const dayOf = new Map(D.map((d) => [d.date, d.k]));
  const dayNum = (date) => Math.round((Date.UTC(+date.slice(0, 4), +date.slice(5, 7) - 1, +date.slice(8, 10)) - EPOCH) / 864e5);
  S.forEach((s) => { s.day = dayNum(s.date); });

  const stage = root.querySelector('[data-stage]');
  const sea = root.querySelector('[data-sea]');
  const veil = root.querySelector('.stories-veil');
  const masthead = document.querySelector('body > header.site');
  const lens = root.querySelector('[data-lens]');
  const glass = root.querySelector('[data-lens-glass]');
  const label = root.querySelector('[data-lens-label]');
  const lit = root.querySelector('[data-lit]');
  const key = root.querySelector('[data-key]');
  const video = key.querySelector('[data-video]');
  const fine = matchMedia('(hover: hover) and (pointer: fine)');
  const narrow = matchMedia('(max-width: 768px)');

  // A story's frame on its month sheet, as percentages so any size can show it.
  function paint(el, s) {
    const rows = data.month_sheets[s.month][1];
    const c = s.slot % 6;
    const r = Math.floor(s.slot / 6);
    el.className = el.className.replace(/\bm-\S+/g, '').trim() + ' m-' + s.month;
    el.style.backgroundSize = `600% ${rows * 100}%`;
    el.style.backgroundPosition = `${c * 20}% ${rows > 1 ? (r / (rows - 1)) * 100 : 0}%`;
  }

  // ---------------------------------------------------------------- the sea

  let G = null; // the current layout
  function hash(n) { n = Math.imul(n ^ 0x9e3779b9, 0x85ebca6b); n ^= n >>> 13; n = Math.imul(n, 0xc2b2ae35); return (n ^ (n >>> 16)) >>> 0; }

  function layout() {
    const vw = document.documentElement.clientWidth;
    const pad = narrow.matches ? 20 : 40;
    const page = Math.min(vw, 1200);
    const container = page - 2 * pad;
    const dc = Math.max(6, Math.floor((container + GAP) / PX));
    const dataW = dc * PX - GAP;
    const x0 = (vw - page) / 2 + pad + (container - dataW) / 2; // the days' left edge
    const lc = Math.ceil(x0 / PX);
    const rc = Math.ceil((vw - x0 - dataW) / PX);
    // Behind the masthead the sea is repeats, like the edges; the newest day
    // starts on the first row below it.
    const mast = masthead ? masthead.offsetHeight : 0;
    const top = Math.ceil(mast / PY);
    const sig = [dc, lc, rc, top].join(':');
    if (G && G.sig === sig) return;
    const cols = lc + dc + rc;
    const rows = top + Math.ceil(D.length / dc);
    const cells = new Int32Array(cols * rows);
    const frag = document.createDocumentFragment();
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const k = (r - top) * dc + (c - lc);
        const real = r >= top && c >= lc && c < lc + dc && k < D.length;
        const d = real ? D[k] : D[hash(r * 977 + c) % D.length];
        cells[r * cols + c] = real ? d.k : -1 - d.k;
        const t = document.createElement('i');
        const n = Math.min(6, d.ids.length);
        t.className = `t d-${d.sheet} y${d.year}${real ? '' : ' dup'}${n > 1 ? ' n' + n : ''}`;
        t.style.backgroundPosition = `0 ${-d.row * TH}px`;
        if (n > 1) {
          const dur = n * (1.3 + (hash(r * 31 + c * 7) % 1000) / 900);
          t.style.animationDuration = dur.toFixed(2) + 's';
          t.style.animationDelay = (-(hash(c * 131 + r) % 1000) / 1000 * dur).toFixed(2) + 's';
        }
        frag.append(t);
      }
    }
    // A chip at each year's newest day.
    const seen = new Set();
    D.forEach((d) => {
      if (seen.has(d.year)) return;
      seen.add(d.year);
      const chip = document.createElement('span');
      chip.className = 'stories-year n';
      chip.textContent = d.year;
      chip.style.left = ((d.k % dc) + lc) * PX + 2 + 'px';
      chip.style.top = (top + Math.floor(d.k / dc)) * PY + 2 + 'px';
      frag.append(chip);
    });
    sea.replaceChildren(frag);
    sea.style.left = x0 - lc * PX + 'px';
    sea.style.width = cols * PX - GAP + 'px';
    sea.style.gridTemplateColumns = `repeat(${cols}, ${TW}px)`;
    stage.style.height = rows * PY - GAP + 'px';
    // The veil holds over the masthead and clears by the newest row.
    veil.style.setProperty('--stories-masthead', mast + 'px');
    veil.style.height = Math.max(top * PY, mast + 32) + 'px';
    G = { sig, cols, rows, dc, lc, top, mast, left: x0 - lc * PX, cells, h: rows * PY - GAP };
    if (state.open) placeLit();
  }

  function cellXY(k) {
    return { x: G.left + ((k % G.dc) + G.lc) * PX, y: (G.top + Math.floor(k / G.dc)) * PY };
  }

  function cellAt(clientX, clientY) {
    const r = sea.getBoundingClientRect();
    const x = clientX - r.left;
    const y = clientY - r.top;
    const c = Math.floor(x / PX);
    const row = Math.floor(y / PY);
    if (c < 0 || c >= G.cols || row < 0 || row >= G.rows) return null;
    const v = G.cells[row * G.cols + c];
    return { k: v < 0 ? null : v, any: v < 0 ? -v - 1 : v, x, y };
  }

  // ---------------------------------------------------------------- the lens

  const pool = [];
  function showLens(x, y) {
    lens.hidden = false;
    lens.style.left = G.left + x - R + 'px';
    lens.style.top = y - R + 'px';
    const reach = R / ZOOM + PX;
    const c0 = Math.max(0, Math.floor((x - reach) / PX));
    const c1 = Math.min(G.cols - 1, Math.floor((x + reach) / PX));
    const r0 = Math.max(0, Math.floor((y - reach) / PY));
    const r1 = Math.min(G.rows - 1, Math.floor((y + reach) / PY));
    let n = 0;
    for (let r = r0; r <= r1; r++) {
      for (let c = c0; c <= c1; c++) {
        const v = G.cells[r * G.cols + c];
        const d = D[v < 0 ? -v - 1 : v];
        let tile = pool[n];
        if (!tile) {
          tile = document.createElement('span');
          tile.append(document.createElement('span'));
          tile.firstChild.className = 'stories-frame';
          pool.push(tile);
          glass.prepend(tile);
        }
        // The sea's own frame waits underneath while the sharp one loads.
        tile.className = 'stories-lens-t d-' + d.sheet;
        tile.style.backgroundPosition = `0 ${-d.row * TH * ZOOM}px`;
        tile.style.left = (c * PX - x) * ZOOM + R + 'px';
        tile.style.top = (r * PY - y) * ZOOM + R + 'px';
        tile.hidden = false;
        paint(tile.firstChild, S[d.ids[0]]);
        n++;
      }
    }
    for (; n < pool.length; n++) pool[n].hidden = true;
    const at = G.cells[Math.floor(y / PY) * G.cols + Math.floor(x / PX)];
    if (at === undefined || at < 0) {
      label.hidden = true;
    } else {
      const d = D[at];
      const s = S[d.ids[0]];
      const count = d.ids.length;
      label.hidden = false;
      label.innerHTML = `${dow(d.date)} <time>${d.date}</time> · <span class="n">${s.time}</span>${s.place ? ' · ' + esc(s.place) : ''} · <span class="muted"><span class="n">${count}</span> ${count === 1 ? 'story' : 'stories'}</span>`;
    }
    const lx = G.left + x;
    label.classList.toggle('is-left', lx < 260);
    label.classList.toggle('is-right', lx > document.documentElement.clientWidth - 260);
  }

  let frame = 0;
  sea.addEventListener('pointermove', (e) => {
    if (state.open || !fine.matches) return;
    const { clientX, clientY } = e;
    cancelAnimationFrame(frame);
    frame = requestAnimationFrame(() => {
      const h = cellAt(clientX, clientY);
      if (h) showLens(h.x, h.y);
    });
  });
  sea.addEventListener('pointerleave', () => { cancelAnimationFrame(frame); lens.hidden = true; });
  sea.addEventListener('click', (e) => {
    const h = cellAt(e.clientX, e.clientY);
    if (!h || h.k === null) return;
    if (state.open) show(D[h.k].ids[0]);
    else open(D[h.k].ids[0], h.y);
  });

  // Keyboard: the arrows move a cursor over the days, Enter opens one.
  let cursor = 0;
  sea.addEventListener('keydown', (e) => {
    const moves = { ArrowLeft: -1, ArrowRight: 1, ArrowUp: -G.dc, ArrowDown: G.dc };
    if (e.key in moves && !state.open) {
      e.preventDefault();
      cursor = Math.max(0, Math.min(D.length - 1, cursor + moves[e.key]));
      const at = cellXY(cursor);
      showLens(at.x - G.left + TW / 2, at.y + TH / 2);
    } else if ((e.key === 'Enter' || e.key === ' ') && !state.open) {
      e.preventDefault();
      open(D[cursor].ids[0], cellXY(cursor).y);
    }
  });
  sea.addEventListener('blur', () => { if (!fine.matches || !sea.matches(':hover')) lens.hidden = true; });

  // ---------------------------------------------------------------- the time key

  const state = { open: false, cur: 0, playing: false };
  const order = S.map((s) => s.i); // already oldest first
  const f = (name) => key.querySelector(`[data-f="${name}"]`);
  const playBtn = key.querySelector('[data-play]');
  const sound = key.querySelector('[data-sound]');
  const range = key.querySelector('[data-range]');
  const segs = key.querySelector('[data-segs]');
  const thumbs = key.querySelector('[data-thumbs]');
  const well = key.querySelector('[data-well]');
  const status = key.querySelector('[data-status]');

  range.max = dayNum(data.last);
  const years = key.querySelector('[data-years]');
  for (let y = 2018; y <= +data.last.slice(0, 4); y++) {
    const tick = document.createElement('span');
    tick.className = 'n';
    tick.textContent = y;
    tick.style.left = (dayNum(`${y}-01-01`) / range.max) * 100 + '%';
    years.append(tick);
  }

  function open(i, y) {
    state.open = true;
    lens.hidden = true;
    key.hidden = false;
    sea.classList.add('is-dim');
    show(i);
    // A story opens playing: the click that opened it lets it play with sound.
    play();
    if (!narrow.matches) {
      const top = Math.max(G.mast + 16, Math.min(G.h - key.offsetHeight - 16, Math.round(y - 180)));
      key.style.top = Math.max(16, top) + 'px';
    }
    key.focus({ preventScroll: !narrow.matches });
  }

  function close() {
    state.open = false;
    pause();
    key.hidden = true;
    lit.hidden = true;
    sea.classList.remove('is-dim');
    sea.focus({ preventScroll: true });
  }

  function placeLit() {
    const at = cellXY(dayOf.get(S[state.cur].date));
    lit.hidden = false;
    lit.style.left = at.x + 'px';
    lit.style.top = at.y + 'px';
    paint(lit.firstChild, S[state.cur]);
  }

  function show(i) {
    const s = S[i];
    const d = D[dayOf.get(s.date)];
    const k = d.ids.indexOf(i);
    state.cur = i;
    cursor = d.k;
    sea.dataset.year = d.year;
    f('dow').textContent = dow(s.date);
    f('date').textContent = s.date;
    f('date').dateTime = s.date;
    f('place').textContent = s.place || 'Place not recorded';
    f('time').textContent = s.time;
    f('k').textContent = k + 1;
    f('n').textContent = d.ids.length;
    f('dur').textContent = s.dur.toFixed(1);
    f('quiet').textContent = s.audio ? '' : ' · no sound';
    f('badge').textContent = `${k + 1} / ${d.ids.length}`;
    key.setAttribute('aria-label', `Stories of ${s.date}`);
    paint(key.querySelector('[data-frame]'), s);
    segs.replaceChildren(...d.ids.map((j, n) => {
      const seg = document.createElement('span');
      seg.className = 'stories-seg' + (n < k ? ' is-done' : n === k ? ' is-current' : '');
      seg.append(document.createElement('i'));
      return seg;
    }));
    thumbs.replaceChildren(...d.ids.map((j, n) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'stories-thumb' + (j === i ? ' is-current' : '');
      b.setAttribute('aria-label', `Story ${n + 1} of ${d.ids.length}`);
      if (j === i) b.setAttribute('aria-current', 'true');
      const fr = document.createElement('span');
      fr.className = 'stories-frame';
      paint(fr, S[j]);
      b.append(fr);
      b.addEventListener('click', () => show(j));
      return b;
    }));
    range.value = s.day;
    range.setAttribute('aria-valuetext', s.date);
    placeLit();
    if (state.playing) load(s, true);
    else unload();
  }

  function load(s, play) {
    well.classList.remove('is-playing');
    status.hidden = true;
    video.src = s.video;
    video.muted = !sound.checked;
    if (play) start();
  }
  // Browsers may refuse to play with sound (Safari often does, and Chrome on a
  // first visit): then the story plays muted and the Sound switch turns off,
  // so one press brings the sound back. An interrupted play (a quick step to
  // the next story) is not a refusal and leaves playback on.
  function start() {
    video.play().catch((e) => {
      if (e.name === 'AbortError') return;
      if (e.name === 'NotAllowedError' && !video.muted) {
        video.muted = true;
        sound.checked = false;
        video.play().catch((again) => { if (again.name !== 'AbortError') pause(); });
        return;
      }
      pause();
    });
  }
  function unload() {
    well.classList.remove('is-playing');
    status.hidden = true;
    if (video.getAttribute('src')) { video.pause(); video.removeAttribute('src'); video.load(); }
  }
  function play() {
    state.playing = true;
    playBtn.querySelector('[data-play-icon]').setAttribute('d', PAUSE);
    playBtn.querySelector('[data-play-label]').textContent = 'Pause';
    if (video.getAttribute('src') && video.paused && !video.ended) start();
    else load(S[state.cur], true);
  }
  function pause() {
    state.playing = false;
    playBtn.querySelector('[data-play-icon]').setAttribute('d', PLAY);
    playBtn.querySelector('[data-play-label]').textContent = 'Play';
    status.hidden = true;
    video.pause();
  }
  function step(dir) {
    const n = state.cur + dir; // S is in order
    if (n >= 0 && n < S.length) show(order[n]);
  }

  // A tab in the background may pause a silent video to save power; carry on
  // when the page is seen again.
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden && state.open && state.playing && video.paused && video.getAttribute('src')) start();
  });
  video.addEventListener('playing', () => { well.classList.add('is-playing'); status.hidden = true; });
  video.addEventListener('waiting', () => { if (state.playing) { status.textContent = 'Loading…'; status.hidden = false; } });
  // A video that will not load leaves its frame and says so; Play tries again.
  video.addEventListener('error', () => {
    if (!video.getAttribute('src')) return;
    pause();
    well.classList.remove('is-playing');
    status.textContent = 'The video did not load';
    status.hidden = false;
  });
  video.addEventListener('timeupdate', () => {
    const cur = segs.querySelector('.is-current i');
    if (cur && video.duration) cur.style.width = (video.currentTime / video.duration) * 100 + '%';
  });
  video.addEventListener('ended', () => { if (state.playing) step(1); });
  playBtn.addEventListener('click', () => (state.playing ? pause() : play()));
  sound.addEventListener('change', () => { video.muted = !sound.checked; });
  key.querySelectorAll('[data-step]').forEach((b) => b.addEventListener('click', () => step(+b.dataset.step)));
  key.querySelectorAll('[data-day]').forEach((b) => b.addEventListener('click', () => {
    const k = dayOf.get(S[state.cur].date) + +b.dataset.day; // the days run newest first
    if (k >= 0 && k < D.length) show(D[k].ids[0]);
  }));
  key.querySelector('[data-close]').addEventListener('click', close);
  range.addEventListener('input', () => {
    const want = +range.value;
    let lo = 0;
    let hi = S.length - 1;
    while (lo < hi) { const mid = (lo + hi) >> 1; if (S[mid].day < want) lo = mid + 1; else hi = mid; }
    show(lo);
  });
  document.addEventListener('keydown', (e) => {
    if (!state.open || e.metaKey || e.ctrlKey || e.altKey) return;
    if (e.key === 'Escape') { e.preventDefault(); close(); return; }
    if (e.target === range || e.target.closest('input, textarea, select')) return;
    if (e.key === 'ArrowLeft') { e.preventDefault(); step(-1); }
    if (e.key === 'ArrowRight') { e.preventDefault(); step(1); }
  });

  // ---------------------------------------------------------------- start

  layout();
  root.dataset.ready = '';
  let resize = 0;
  addEventListener('resize', () => { clearTimeout(resize); resize = setTimeout(layout, 150); });
}

function dow(date) { return DOW[new Date(date + 'T00:00:00Z').getUTCDay()]; }
function esc(t) { return t.replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c])); }
