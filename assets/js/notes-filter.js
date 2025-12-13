(() => {
  const filterNav = document.querySelector(".notes-filter");
  if (!filterNav) return;

  const links = Array.from(filterNav.querySelectorAll("[data-category]"));
  const yearSections = Array.from(document.querySelectorAll(".notes-year"));

  const applyFilter = (slug) => {
    const activeSlug = slug && slug !== "" ? slug : "all";

    links.forEach((link) => {
      link.classList.toggle("is-active", link.dataset.category === activeSlug);
    });

    yearSections.forEach((section) => {
      const items = Array.from(section.querySelectorAll("li[data-category]"));
      let visibleCount = 0;

      items.forEach((item) => {
        const match = activeSlug === "all" || item.dataset.category === activeSlug;
        item.hidden = !match;
        if (match) visibleCount += 1;
      });

      section.hidden = visibleCount === 0;
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
