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

    groups.forEach((group) => {
      const items = Array.from(group.querySelectorAll("[data-category]"));
      let visibleCount = 0;

      items.forEach((item) => {
        const match = activeSlug === "all" || item.dataset.category === activeSlug;
        item.hidden = !match;
        if (match) visibleCount += 1;
      });

      group.hidden = visibleCount === 0;
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
