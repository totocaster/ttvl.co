// The compare shortcode's divider follows its range input, which covers
// the frame, so a drag anywhere or the arrow keys move it.
// docs/figures.md, Pictures; components/_pictures.scss.
(() => {
  for (const frame of document.querySelectorAll(".compare__frame")) {
    const range = frame.querySelector("input");
    const first = frame.querySelector(".compare__badge--first")?.textContent || "";
    const update = () => {
      frame.style.setProperty("--pos", `${range.value}%`);
      range.setAttribute("aria-valuetext", `${range.value}% ${first}`);
    };
    range.addEventListener("input", update);
    update();
  }
})();
