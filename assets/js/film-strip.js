// The Contact Sheet's strip of film (layouts/newsletter/list.html): fade
// whichever edge still has frames beyond it. The strip scrolls natively;
// this only sets data-more="start", "end", "both", or nothing, and
// sections/_newsletter.scss draws the fades from it.
(() => {
  const strips = document.querySelectorAll("[data-film]");

  const update = (film) => {
    const max = film.scrollWidth - film.clientWidth;
    const atStart = film.scrollLeft <= 1;
    const atEnd = film.scrollLeft >= max - 1;
    let more = "";
    if (!atStart && !atEnd) more = "both";
    else if (!atStart) more = "start";
    else if (!atEnd) more = "end";
    if (film.dataset.more !== more) film.dataset.more = more;
  };

  strips.forEach((film) => {
    let queued = false;
    const onScroll = () => {
      if (queued) return;
      queued = true;
      requestAnimationFrame(() => {
        queued = false;
        update(film);
      });
    };
    film.addEventListener("scroll", onScroll, { passive: true });
    if ("ResizeObserver" in window) new ResizeObserver(onScroll).observe(film);
    else window.addEventListener("resize", onScroll);
    update(film);
  });
})();
