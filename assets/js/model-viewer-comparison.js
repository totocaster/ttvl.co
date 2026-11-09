const modelViewerComparison = {
  init() {
    const comparisons = document.querySelectorAll(
      "[data-model-viewer-comparison]",
    );

    comparisons.forEach((comparison) => this.initComparison(comparison));
  },

  initComparison(comparison) {
    if (comparison.dataset.modelViewerComparisonReady === "true") return;

    const viewer = comparison.querySelector("[data-model-viewer]");
    const buttons = Array.from(
      comparison.querySelectorAll("[data-model-variant]"),
    );
    const status = comparison.querySelector("[data-model-comparison-status]");
    const download = comparison.querySelector(
      "[data-model-comparison-download]",
    );
    const size = comparison.querySelector("[data-model-comparison-size]");

    // The download and its size are optional: the legend leaves them out
    // when the page's head already offers both scans.
    if (!viewer || !buttons.length || !status) return;

    // Dates and sizes are numbers: <time> and .n set them in Mono.
    const numeral = (tag, text) => {
      const element = document.createElement(tag);
      if (tag === "time") element.dateTime = text;
      else element.className = "n";
      element.textContent = text;
      return element;
    };

    buttons.forEach((button) => {
      button.addEventListener("click", () => {
        if (button.getAttribute("aria-pressed") === "true") return;

        const { modelSrc, modelAlt, modelLabel, modelDate, modelSize } =
          button.dataset;

        viewer.setAttribute("src", modelSrc);
        viewer.setAttribute("alt", modelAlt);
        buttons.forEach((candidate) => {
          candidate.setAttribute(
            "aria-pressed",
            String(candidate === button),
          );
        });
        status.replaceChildren(
          `Showing ${modelLabel} · `,
          numeral("time", modelDate),
        );
        if (download) download.href = modelSrc;
        if (size) {
          size.replaceChildren(
            ...(modelSize ? [" (", numeral("span", modelSize), ")"] : []),
          );
        }
      });
    });

    comparison.dataset.modelViewerComparisonReady = "true";
  },
};

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () =>
    modelViewerComparison.init(),
  );
} else {
  modelViewerComparison.init();
}
