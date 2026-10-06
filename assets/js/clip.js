// Clips loop silently. Readers who ask for reduced motion get the poster
// frame and the browser's controls instead, so nothing moves until they
// press play. Loaded only on pages that use the clip shortcode.
(() => {
  if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  document.querySelectorAll("video.clip__video").forEach((video) => {
    video.removeAttribute("autoplay");
    video.pause();
    video.controls = true;
  });
})();
