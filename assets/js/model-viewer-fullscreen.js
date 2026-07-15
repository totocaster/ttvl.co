const modelViewerFullscreen = {
  fallbackViewport: null,

  init() {
    const viewports = document.querySelectorAll("[data-model-viewer-viewport]");

    viewports.forEach((viewport) => {
      const button = viewport.querySelector("[data-model-viewer-fullscreen]");
      if (!button) return;

      button.hidden = false;
      button.addEventListener("click", () => this.toggle(viewport));
    });

    document.addEventListener("fullscreenchange", () => this.update(viewports));
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && this.fallbackViewport) {
        event.preventDefault();
        this.exitFallback();
        this.update(viewports);
      }
    });
  },

  async toggle(viewport) {
    if (document.fullscreenElement === viewport) {
      await document.exitFullscreen();
      return;
    }

    if (viewport.classList.contains("is-fullscreen")) {
      this.exitFallback();
      this.update(document.querySelectorAll("[data-model-viewer-viewport]"));
      return;
    }

    if (viewport.requestFullscreen) {
      try {
        await viewport.requestFullscreen();
        return;
      } catch (error) {
        // Use the full-viewport fallback when the browser rejects the request.
      }
    }

    this.enterFallback(viewport);
    this.update(document.querySelectorAll("[data-model-viewer-viewport]"));
  },

  enterFallback(viewport) {
    this.exitFallback();
    this.fallbackViewport = viewport;
    viewport.classList.add("is-fullscreen");
    document.documentElement.classList.add("model-viewer-fullscreen-active");
  },

  exitFallback() {
    if (!this.fallbackViewport) return;

    this.fallbackViewport.classList.remove("is-fullscreen");
    this.fallbackViewport = null;
    document.documentElement.classList.remove("model-viewer-fullscreen-active");
  },

  update(viewports) {
    viewports.forEach((viewport) => {
      const button = viewport.querySelector("[data-model-viewer-fullscreen]");
      const isFullscreen =
        document.fullscreenElement === viewport ||
        viewport.classList.contains("is-fullscreen");

      button.setAttribute(
        "aria-label",
        isFullscreen ? "Exit full screen" : "View 3D model full screen",
      );
      button.title = isFullscreen ? "Exit full screen" : "View full screen";
    });
  },
};

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => modelViewerFullscreen.init());
} else {
  modelViewerFullscreen.init();
}
