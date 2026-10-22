// The reply-following instrument (layouts/shortcodes/reply-following.html):
// four phones play one simulated reply. Raw chunks shows each chunk as it
// lands, half-written Markdown and all, and snaps to the end; the other
// three reveal whole words at Hank's pace, from a steady copy of the
// Markdown, and differ only in where the view goes: to the end, to the
// question at the top, or with the first paragraph and then nowhere.
//
// The stream and its Markdown come from the Reply Streaming Lab Hank's
// presets were picked in; the timing is Hank's own (HankKit's
// ReplyStreamingTiming, 2026-10-22). Each phone is laid out once, as the
// browser sets its type, then simulated frame by frame, so Play and the
// scrubber only look up a moment. Nothing plays until the reader presses
// Play. With reduced motion, words appear whole and the view moves without
// gliding, as Hank does under Reduce Motion. docs/figures.md, Instruments.
(() => {
  // Hank's timing: words fade in over 0.28 s, paced to trail the network by
  // 0.45 s (0.2 s once the stream ends) at no less than 30 characters a
  // second; a burst staggers in reading order; the view glides with a
  // 0.11 s time constant.
  const FADE = 0.28;
  const LAG = 0.45;
  const FINAL_LAG = 0.2;
  const FLOOR = 30;
  const STAGGER = 0.009;
  const MAX_STAGGER = 0.36;
  const GLIDE = 0.11;
  // The stream: the Lab's normal model (55 tokens a second) on its bursty
  // network, from one seed, so every reader sees the same reply.
  const RATE = 55;
  const SEED = 7;
  const NET = { min: 60, max: 240, p: 0.07, stall: [450, 1300] };
  const STEP = 1 / 240; // simulation step, s
  const FPS = 60; // the stored frames
  const TAIL = 1.2; // the still holds this long after the last word

  const NUMBER = /(\d[\d.,:×–-]*\d|\d)/;
  const motion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const ease = (x) => 1 - (1 - x) ** 3;

  // Text with every number wrapped in .n, built as nodes, never as HTML.
  const write = (element, text) => {
    element.replaceChildren();
    for (const part of text.split(NUMBER)) {
      if (!part) continue;
      if (NUMBER.test(part) && /^\d/.test(part)) {
        const number = document.createElement("span");
        number.className = "n";
        number.textContent = part;
        element.append(number);
      } else {
        element.append(part);
      }
    }
  };

  // --- Markdown, every word tagged with its offset in the source ----------
  // The Lab's renderer. steady holds back what would restyle later (an open
  // marker, a table before it's whole); complete means the reply has ended.
  const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
  const words = (text, base) => {
    let out = "";
    const re = /(\s+)|(\S+)/g;
    let m;
    while ((m = re.exec(text))) {
      if (m[1]) out += esc(m[1]);
      else out += `<span class="w" data-o="${base + m.index}">${esc(m[2])}</span>`;
    }
    return out;
  };
  const inline = (text, base, tail, steady) => {
    if (steady && tail && (/[^*]\*$/.test(text) || text === "*")) text = text.slice(0, -1);
    let out = "";
    let buf = "";
    let bufStart = 0;
    let i = 0;
    const flush = () => {
      if (buf) {
        out += words(buf, base + bufStart);
        buf = "";
      }
    };
    while (i < text.length) {
      if (text.startsWith("**", i)) {
        const close = text.indexOf("**", i + 2);
        if (close >= 0 || (steady && tail)) {
          flush();
          const end = close >= 0 ? close : text.length;
          const inner = text.slice(i + 2, end);
          if (inner) out += `<strong>${words(inner, base + i + 2)}</strong>`;
          i = close >= 0 ? close + 2 : text.length;
          continue;
        }
      }
      if (!buf) bufStart = i;
      buf += text[i];
      i++;
    }
    flush();
    return out;
  };
  const cells = (line, o) => {
    const res = [];
    let i = line[0] === "|" ? 1 : 0;
    let start = i;
    for (; i <= line.length; i++) {
      if (i === line.length || line[i] === "|") {
        if (i === line.length && start === i) break;
        let a = start;
        let b = i;
        while (a < b && line[a] === " ") a++;
        while (b > a && line[b - 1] === " ") b--;
        res.push({ text: line.slice(a, b), o: o + a });
        start = i + 1;
      }
    }
    return res;
  };
  const DELIM = /^\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?\s*$/;
  const LI = /^[-*](?:[ \t]+(.*))?$/;
  const MARKER_ONLY = /^(#{1,6}|[-*]|`{1,2})?\s*$/;
  const markdown = (src, { steady, complete }) => {
    const lines = [];
    let offset = 0;
    for (const t of src.split("\n")) {
      lines.push({ t, o: offset });
      offset += t.length + 1;
    }
    const openLast = !complete && !src.endsWith("\n");
    const lastIdx = lines.length - 1;
    let html = "";
    let para = null;
    let i = 0;
    const flushPara = (tail) => {
      if (!para) return;
      html += `<p>${para.map((p, k) => inline(p.t, p.o, tail && k === para.length - 1, steady)).join(" ")}</p>`;
      para = null;
    };
    while (i < lines.length) {
      const { t, o } = lines[i];
      const open = i === lastIdx && openLast;
      if (steady && open && MARKER_ONLY.test(t)) break;
      if (t.trim() === "") {
        flushPara(false);
        i++;
        continue;
      }
      if (LI.test(t)) {
        flushPara(false);
        let items = "";
        let j = i;
        while (j < lines.length) {
          const lt = lines[j].t;
          const m = lt.match(LI);
          if (!m) break;
          const txt = m[1] || "";
          if (steady && j === lastIdx && openLast && !txt) break;
          items += `<li>${txt ? inline(txt, lines[j].o + lt.length - txt.length, j === lastIdx && !complete, steady) : "&nbsp;"}</li>`;
          j++;
        }
        if (items) html += `<ul>${items}</ul>`;
        if (j === i) break;
        i = j;
        continue;
      }
      if (t.startsWith("|")) {
        const next = lines[i + 1];
        const header = cells(t, o);
        const delimOK = !!next && DELIM.test(next.t) && cells(next.t, next.o).length === header.length;
        if (steady && !complete) {
          let j = i + 1;
          while (j < lines.length && lines[j].t.startsWith("|")) j++;
          const ended = j < lastIdx || (j === lastIdx && lines[j].t !== "");
          if (!delimOK || !ended) break;
        }
        if (delimOK) {
          flushPara(false);
          let j = i + 2;
          let rows = "";
          while (j < lines.length && lines[j].t.startsWith("|")) {
            const cs = cells(lines[j].t, lines[j].o);
            rows += `<tr>${header.map((_, k) => `<td>${cs[k] ? inline(cs[k].text, cs[k].o, false, steady) : ""}</td>`).join("")}</tr>`;
            j++;
          }
          html += `<table><thead><tr>${header.map((c) => `<th>${inline(c.text, c.o, false, steady)}</th>`).join("")}</tr></thead><tbody>${rows}</tbody></table>`;
          i = j;
          continue;
        }
      }
      (para || (para = [])).push({ t, o });
      i++;
    }
    flushPara(!complete);
    return html;
  };

  // --- The stream ------------------------------------------------------------
  // Tokens of up to five characters at RATE a second, flushed by a network
  // that sometimes stalls: [{ t, length }] in seconds and characters.
  const mulberry32 = (a) => () => {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
  const schedule = (source) => {
    const rnd = mulberry32(SEED);
    const tokens = source.match(/\s*\S{1,5}|\s+/g);
    let t = 650 + rnd() * 250;
    let length = 0;
    const emitted = [];
    for (const token of tokens) {
      t += (1000 / RATE) * (0.55 + rnd() * 0.9);
      length += token.length;
      emitted.push({ t, length });
    }
    const chunks = [];
    let flushAt = emitted[0].t - 1;
    let i = 0;
    while (i < emitted.length) {
      flushAt += NET.min + rnd() * (NET.max - NET.min);
      if (rnd() < NET.p) flushAt += NET.stall[0] + rnd() * (NET.stall[1] - NET.stall[0]);
      while (i < emitted.length && emitted[i].t <= flushAt) i++;
      if (i > 0 && (!chunks.length || chunks[chunks.length - 1].length < emitted[i - 1].length)) {
        chunks.push({ t: flushAt / 1000, length: emitted[i - 1].length });
      }
    }
    return chunks;
  };
  const received = (chunks, t) => {
    let length = 0;
    for (const chunk of chunks) {
      if (chunk.t > t) break;
      length = chunk.length;
    }
    return length;
  };

  // When each word appears with Hank's pacing: a point that moves at least
  // FLOOR characters a second, faster as the backlog grows, shows whole
  // words that have arrived; a table waits until it's whole.
  const pace = (list, chunks, total, end) => {
    let point = 0;
    let t = 0;
    let k = 0;
    let last = null;
    while (k < list.length && t < 60) {
      t += STEP;
      const recv = received(chunks, t);
      const final = t >= end;
      const rate = Math.max(FLOOR, (recv - point) / (final ? FINAL_LAG : LAG));
      point = Math.min(recv, point + rate * STEP);
      let fresh = 0;
      while (k < list.length && point > list[k].start && recv >= list[k].end && recv >= list[k].hold) {
        let at = t + Math.min(fresh * STAGGER, MAX_STAGGER);
        if (last !== null) at = Math.max(at, last);
        list[k].at = last = at;
        fresh++;
        k++;
      }
      if (final && point >= total) {
        for (; k < list.length; k++) list[k].at = last = Math.max(t, last ?? t);
      }
    }
  };

  const top = (el, origin) => el.getBoundingClientRect().top - origin;
  const bottom = (el, origin) => el.getBoundingClientRect().bottom - origin;

  for (const figure of document.querySelectorAll(".reply-following")) {
    // A stream page shows entries in full and may load this script twice.
    if (figure.hasAttribute("data-ready")) continue;
    figure.setAttribute("data-ready", "");
    const key = figure.querySelector("[data-play]");
    const range = figure.querySelector(".scrubber input");
    const readout = figure.querySelector(".readout");
    const data = figure.querySelector("[data-reply]");
    if (!key || !range || !data) continue;
    const source = JSON.parse(data.textContent);
    const chunks = schedule(source);
    const total = source.length;
    const endOfStream = chunks[chunks.length - 1].t + 0.09;

    const phones = [...figure.querySelectorAll(".reply-following__column")].map((column) => ({
      mode: column.dataset.mode,
      phone: column.querySelector(".hank-phone"),
      track: column.querySelector(".hank-phone__track"),
      live: column.querySelector("[data-live]"),
      question: column.querySelector("[data-question]"),
      receipt: column.querySelector("[data-receipt]"),
      header: column.querySelector(".hank-pill"),
      composer: column.querySelector(".hank-phone__composer"),
      jump: column.querySelector("[data-jump]"),
      status: column.querySelector("[data-status]"),
    }));

    // The paced phones render the whole reply once from the steady copy;
    // its words wait, unpainted, for their moment.
    let list = null;
    for (const p of phones) {
      if (p.mode === "raw") continue;
      p.live.innerHTML = markdown(source, { steady: true, complete: true });
      p.spans = [...p.live.querySelectorAll(".w")];
      p.blocks = [...p.live.children];
      p.marks = [...p.live.querySelectorAll("li, table")];
      if (!list) {
        list = p.spans.map((span) => {
          const start = Number(span.dataset.o);
          const end = start + span.textContent.length;
          let hold = 0;
          const table = span.closest("table");
          if (table) {
            // The steady copy holds a table until a line follows it.
            const last = [...table.querySelectorAll(".w")].pop();
            const after = source.indexOf("\n", Number(last.dataset.o) + last.textContent.length);
            hold = after < 0 ? total : after + 2;
          }
          return { start, end, hold, at: Infinity };
        });
        pace(list, chunks, total, endOfStream);
      }
    }
    const lastAt = Math.max(...list.map((w) => w.at));
    const duration = Math.ceil((lastAt + FADE + TAIL) * 10) / 10;
    const arrivals = list.map((w) => w.end).sort((a, b) => a - b);

    // The marks a word brings with it: a list item's bullet, a table's rules.
    for (const p of phones) {
      if (!p.marks) continue;
      p.markAt = p.marks.map((mark) => list[p.spans.indexOf(mark.querySelector(".w"))].at);
    }

    // The geometry each rule reads, in px from the top of the track.
    const measure = (p) => {
      const origin = p.track.getBoundingClientRect().top;
      const phone = p.phone.getBoundingClientRect();
      const g = {
        height: phone.height,
        insetTop: p.header.getBoundingClientRect().bottom - phone.top + 8,
        insetBottom: phone.bottom - p.composer.getBoundingClientRect().top + 8,
        qTop: top(p.question, origin),
        qBottom: bottom(p.question, origin),
        before: bottom(p.question.previousElementSibling, origin),
        after: bottom(p.receipt, origin),
      };
      if (p.spans) {
        // How far down the reply reaches with its first n words shown.
        let reach = g.after;
        g.reach = [g.after, ...p.spans.map((span) => (reach = Math.max(reach, bottom(span, origin) + 2)))];
        g.firstBreak = p.spans.findIndex((span) => p.blocks.indexOf(span.closest("[data-live] > *")) > 0);
      }
      return g;
    };

    // Each paced phone's view, frame by frame: where it stands, whether the
    // jump button shows, whether the question is in view.
    const simulate = (p) => {
      const g = measure(p);
      p.g = g;
      // The view's end with the words shown by t: the reach of the reply
      // drawn so far, over the composer.
      const shown = (t, n = 0) => {
        while (n < list.length && list[n].at <= t) n++;
        return n;
      };
      const endWith = (n) => g.reach[n] + g.insetBottom - g.height;
      const anchor = g.qTop - g.insetTop;
      const direct = motion.matches;
      const move = (from, to) => (direct ? to : Math.abs(to - from) <= 0.25 ? to : from + (to - from) * (1 - Math.exp(-STEP / GLIDE)));
      let offset = g.before + g.insetBottom - g.height; // the end, before sending
      let following = true;
      let settle = null;
      const stopAt = g.firstBreak > 0 ? list[g.firstBreak].at : Infinity;
      const frames = [];
      const every = Math.round(1 / (FPS * STEP));
      let n = 0;
      for (let step = 0, t = 0; t <= duration + 1e-9; step++, t = step * STEP) {
        n = shown(t, n);
        const end = endWith(n);
        let jump = false;
        if (p.mode === "end") {
          offset = move(offset, end);
        } else if (p.mode === "top") {
          // The question rests under the header; space kept below it lets
          // the view stay there while the reply is short.
          offset = move(offset, anchor);
          jump = end > anchor && end - offset > 24;
        } else if (p.mode === "first") {
          if (following && t >= stopAt) {
            following = false;
            settle = Math.min(endWith(shown(stopAt - 1e-6)), anchor);
          }
          if (following && end > anchor) {
            following = false;
            settle = anchor;
          }
          offset = move(offset, following ? Math.min(end, anchor) : settle);
          jump = !following && end - offset > 24;
        }
        if (step % every === 0) frames.push([offset, jump, (g.qTop + g.qBottom) / 2 - offset > g.insetTop - 8]);
      }
      p.frames = frames;
    };

    // The raw phone at a moment: what has arrived, rendered as it stands,
    // and the view snapped to its end.
    const raw = (p, t) => {
      const recv = received(chunks, t);
      const complete = t >= endOfStream;
      if (recv !== p.recv || complete !== p.complete) {
        p.recv = recv;
        p.complete = complete;
        p.live.innerHTML = markdown(source.slice(0, recv), { steady: false, complete });
        p.g = null;
      }
      if (!p.g) {
        const g = measure(p);
        const origin = p.track.getBoundingClientRect().top;
        const reach = p.live.firstChild ? bottom(p.live, origin) + 2 : g.after;
        p.g = g;
        p.offset = Math.max(reach, g.after) + g.insetBottom - g.height;
      }
      return [p.offset, false, (p.g.qTop + p.g.qBottom) / 2 - p.offset > p.g.insetTop - 8];
    };

    const frameAt = (p, t) => {
      const f = p.frames;
      const x = Math.min(f.length - 1, Math.max(0, t * FPS));
      const i = Math.floor(x);
      const j = Math.min(f.length - 1, i + 1);
      return [f[i][0] + (f[j][0] - f[i][0]) * (x - i), f[i][1], f[i][2]];
    };

    let said = null;
    let now = duration;
    const show = (t) => {
      now = t;
      const whole = motion.matches;
      for (const p of phones) {
        const [offset, jump, inView] = p.mode === "raw" ? raw(p, t) : frameAt(p, t);
        const y = Math.round(offset * 10) / 10;
        if (y !== p.y) {
          p.y = y;
          p.track.style.transform = `translate3d(0, ${-y}px, 0)`;
        }
        if (p.jump.hidden === jump) p.jump.hidden = !jump;
        const status = inView ? "Question in view" : "Question off the top";
        if (p.status.textContent !== status) p.status.textContent = status;
        const receipt = t < 0.25 ? "Sent" : t < endOfStream ? "Delivered" : "Completed";
        if (p.receipt.textContent !== receipt) p.receipt.textContent = receipt;
        if (!p.spans) continue;
        p.spans.forEach((span, i) => {
          const at = list[i].at;
          let opacity = t < at ? 0 : 1;
          if (opacity && !whole) opacity = Math.round(ease(Math.min(1, (t - at) / FADE)) * 100) / 100;
          if (opacity !== span._opacity) {
            span._opacity = opacity;
            span.style.opacity = opacity === 1 ? "" : String(opacity);
          }
        });
        p.marks.forEach((mark, i) => {
          const on = t >= p.markAt[i] ? "1" : "0";
          if (mark.style.getPropertyValue("--m") !== on) mark.style.setProperty("--m", on);
        });
      }
      const recv = received(chunks, t);
      let n = 0;
      while (n < arrivals.length && arrivals[n] <= recv) n++;
      const words =
        n === 0
          ? `${t.toFixed(1)} s · message sent`
          : n < arrivals.length
            ? `${t.toFixed(1)} s · ${n} of ${arrivals.length} words arrived`
            : `${t.toFixed(1)} s · all ${arrivals.length} words arrived`;
      if (words !== said) {
        said = words;
        if (readout) write(readout, words);
        range.setAttribute("aria-valuetext", words);
      }
    };

    const layout = () => {
      for (const p of phones) {
        if (p.mode === "raw") p.g = null;
        else simulate(p);
      }
      show(now);
    };

    // Play runs in real time from where the scrubber stands, or from the
    // start once it has reached the end; the scrubber pauses it.
    let frame = 0;
    let from = 0;
    let started = 0;
    let playing = false;
    const pause = () => {
      cancelAnimationFrame(frame);
      playing = false;
      key.textContent = "Play";
    };
    const tick = (stamp) => {
      const t = Math.min(duration, from + (stamp - started) / 1000);
      range.value = String(t);
      show(t);
      if (t >= duration) pause();
      else frame = requestAnimationFrame(tick);
    };
    key.addEventListener("click", () => {
      if (playing) {
        pause();
        return;
      }
      from = Number(range.value) >= duration ? 0 : Number(range.value);
      playing = true;
      key.textContent = "Pause";
      frame = requestAnimationFrame((stamp) => {
        started = stamp;
        tick(stamp);
      });
    });
    range.addEventListener("input", () => {
      if (playing) pause();
      show(Number(range.value));
    });
    motion.addEventListener?.("change", layout);

    // Show the figure, put the still away, and open on the end of the reply.
    figure.hidden = false;
    const still = figure.nextElementSibling;
    if (still?.classList.contains("reply-following-fallback")) still.hidden = true;
    range.max = String(duration);
    range.value = String(duration);
    layout();
    document.fonts?.ready.then(layout);
    let pending = 0;
    new ResizeObserver(() => {
      cancelAnimationFrame(pending);
      pending = requestAnimationFrame(layout);
    }).observe(phones[0].phone);
  }
})();
