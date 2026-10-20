// Category filtering for the Notes hub (chips), the Projects hub (switches),
// and the Research hub (one switch per stream). A control is any [data-filter-control] or chip in
// .category-filter with a data-category; items with data-category inside
// [data-filter-group] blocks are shown or hidden, an emptied block is hidden,
// and the head rail's live count follows. Pressing a pressed switch releases
// the filter. The state lives in ?category=.
(() => {
  const controls = Array.from(
    document.querySelectorAll("[data-filter-control][data-category], .category-filter [data-category]")
  );
  if (!controls.length) return;

  const groups = Array.from(document.querySelectorAll("[data-filter-group]"));

  const applyFilter = (slug) => {
    const activeSlug = slug && slug !== "" ? slug : "all";
    // While a category is chosen, qualifiers that would only repeat it
    // (.filter-key: a note's category, a card's hub) step aside.
    document.documentElement.toggleAttribute("data-filtered", activeSlug !== "all");

    controls.forEach((control) => {
      const on = control.dataset.category === activeSlug;
      if (control.tagName === "BUTTON") {
        control.setAttribute("aria-pressed", on ? "true" : "false");
      } else {
        control.classList.toggle("is-active", on);
      }
    });

    let total = 0;
    groups.forEach((group) => {
      const items = Array.from(group.querySelectorAll("[data-category]"));
      let visibleCount = 0;

      items.forEach((item) => {
        const match = activeSlug === "all" || item.dataset.category === activeSlug;
        item.hidden = !match;
        if (match) visibleCount += 1;
      });

      group.hidden = visibleCount === 0;
      total += visibleCount;
    });

    // The page head's count follows the filter ("12 projects").
    document.querySelectorAll(".count[data-singular]").forEach((count) => {
      const noun = total === 1 ? count.dataset.singular : count.dataset.plural;
      count.innerHTML = `<span class="n">${total}</span> ${noun}`;
    });
  };

  const setFilter = (slug) => {
    const url = new URL(window.location.toString());
    if (slug && slug !== "all") {
      url.searchParams.set("category", slug);
    } else {
      url.searchParams.delete("category");
    }
    window.history.replaceState({}, "", url);
    applyFilter(slug);
  };

  const params = new URLSearchParams(window.location.search);
  applyFilter(params.get("category") || "all");

  controls.forEach((control) => {
    control.addEventListener("click", (event) => {
      event.preventDefault();
      let slug = control.dataset.category;
      // A pressed switch releases to everything.
      if (control.tagName === "BUTTON" && control.getAttribute("aria-pressed") === "true") slug = "all";
      setFilter(slug);
    });
  });
})();
