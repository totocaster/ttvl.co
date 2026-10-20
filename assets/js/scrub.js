// Instruments with a scrubber (the drawing shortcode's scrub parameter).
// The range picks one of the drawing's [data-mark] elements: the mark
// takes data-on (its [data-band] lights in the highlight) and the readout
// under the well shows its data-readout, numbers in Mono. A pointer over
// the well picks the mark nearest it across, so hovering or dragging
// scrubs too. A drawing with a phone version draws the same marks twice;
// only the visible frame's marks count. docs/figures.md, Instruments.
(() => {
  const NUMBER = /(\d[\d.,:×–-]*\d|\d)/;

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

  for (const figure of document.querySelectorAll(".instrument[data-scrub]")) {
    const scrubber = figure.querySelector(".scrubber");
    const range = scrubber?.querySelector("input");
    const readout = figure.querySelector(".readout");
    const frames = [...figure.querySelectorAll(".drawing__frame")];
    if (!range) continue;

    // The marks of the frame on screen.
    const marks = () => {
      const frame = frames.find((f) => f.offsetParent !== null) || frames[0];
      return [...frame.querySelectorAll("[data-mark]")];
    };

    const count = marks().length;
    if (!count) continue;
    range.max = String(count - 1);
    range.value = String(count - 1);

    const show = () => {
      const index = Number(range.value);
      for (const frame of frames) {
        frame.querySelectorAll("[data-mark]").forEach((mark, i) => {
          mark.toggleAttribute("data-on", i === index);
        });
      }
      const text = marks()[index]?.getAttribute("data-readout") || "";
      if (readout) write(readout, text);
      range.setAttribute("aria-valuetext", text);
    };

    const pick = (event) => {
      if (event.pointerType === "mouse" && event.buttons > 1) return;
      let nearest = 0;
      let distance = Infinity;
      marks().forEach((mark, i) => {
        const box = mark.getBoundingClientRect();
        const d = Math.abs(box.left + box.width / 2 - event.clientX);
        if (d < distance) {
          distance = d;
          nearest = i;
        }
      });
      if (String(nearest) !== range.value) {
        range.value = String(nearest);
        show();
      }
    };

    range.addEventListener("input", show);
    for (const frame of frames) {
      frame.addEventListener("pointermove", pick);
      frame.addEventListener("pointerdown", pick);
    }
    scrubber.hidden = false;
    show();
  }
})();
