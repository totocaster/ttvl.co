(() => {
  const filterNav = document.querySelector(".category-filter");
  if (!filterNav) return;

  const links = Array.from(filterNav.querySelectorAll("[data-category]"));
  const groups = Array.from(document.querySelectorAll("[data-filter-group]"));

  const applyFilter = (slug) => {
    const activeSlug = slug && slug !== "" ? slug : "all";

    links.forEach((link) => {
      link.classList.toggle("is-active", link.dataset.category === activeSlug);
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
      // A group of doors (the Hubs block on Projects) follows the filter
      // without adding to the count.
      if (!("filterUncounted" in group.dataset)) total += visibleCount;
    });

    // The page head's count follows the filter ("12 projects"). It is the
    // only count on the page; a group carries none.
    document.querySelectorAll(".count[data-singular]").forEach((count) => {
      if (count.closest("[data-filter-group]")) return;
      const noun = total === 1 ? count.dataset.singular : count.dataset.plural;
      count.innerHTML = `<span class="n">${total}</span> ${noun}`;
    });
  };

  const params = new URLSearchParams(window.location.search);
  const initial = params.get("category") || "all";
  applyFilter(initial);

  links.forEach((link) => {
    link.addEventListener("click", (event) => {
      event.preventDefault();
      const slug = link.dataset.category;
      const url = new URL(window.location.toString());

      if (slug && slug !== "all") {
        url.searchParams.set("category", slug);
      } else {
        url.searchParams.delete("category");
      }

      window.history.replaceState({}, "", url);
      applyFilter(slug);
    });
  });
})();
