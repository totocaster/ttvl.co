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

    if (!viewer || !buttons.length || !status || !download) return;

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
        status.textContent = `Showing ${modelLabel} · ${modelDate}.`;
        download.href = modelSrc;
        download.textContent = `Download the selected GLB model${
          modelSize ? ` (${modelSize})` : ""
        }`;
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
