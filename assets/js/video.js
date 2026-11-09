// The youtube shortcode's Play key (layouts/shortcodes/youtube.html). The
// key is a link to the video on YouTube; here a press swaps the frame's
// poster and key for the player, from youtube-nocookie.com, so nothing is
// requested from YouTube until the reader asks for it.
document.addEventListener("click", (event) => {
  const key = event.target.closest("[data-video-play]");
  if (!key || event.button !== 0) return;
  if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
  const figure = key.closest("figure.video");
  const frame = figure && figure.querySelector(".video-frame");
  if (!frame || !figure.dataset.video) return;
  event.preventDefault();

  const player = document.createElement("iframe");
  player.src = `https://www.youtube-nocookie.com/embed/${encodeURIComponent(figure.dataset.video)}?autoplay=1`;
  player.title = figure.dataset.title || "Video on YouTube";
  player.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share; fullscreen";
  player.allowFullscreen = true;
  player.referrerPolicy = "strict-origin-when-cross-origin";
  frame.replaceChildren(player);
  frame.classList.add("is-playing");
  player.focus();
});
