// The contents rail: a lamp after the entry whose section is in view, so
// the list reads as a position indicator while the page scrolls. The
// current section is the last heading above the top third of the window;
// above the first heading nothing is lit, and at the foot of the page the
// last section is. Loaded only on pages with the rail (block-body.html).
(() => {
  const toc = document.querySelector(".rail-toc .toc");
  if (!toc) return;

  const targets = Array.from(toc.querySelectorAll('a[href^="#"]'))
    .map((a) => ({ a, el: document.getElementById(decodeURIComponent(a.getAttribute("href").slice(1))) }))
    .filter((t) => t.el);
  if (!targets.length) return;

  let current = null;

  const update = () => {
    const line = window.innerHeight * 0.3;
    let next = null;
    for (const t of targets) {
      if (t.el.getBoundingClientRect().top <= line) next = t;
      else break;
    }
    const root = document.documentElement;
    if (window.innerHeight + window.scrollY >= root.scrollHeight - 2) next = targets[targets.length - 1];
    if (next === current) return;
    if (current) current.a.removeAttribute("aria-current");
    if (next) next.a.setAttribute("aria-current", "true");
    current = next;
  };

  let queued = false;
  const schedule = () => {
    if (queued) return;
    queued = true;
    requestAnimationFrame(() => {
      queued = false;
      update();
    });
  };

  window.addEventListener("scroll", schedule, { passive: true });
  window.addEventListener("resize", schedule);
  update();
})();
