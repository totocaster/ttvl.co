// Research entries: the Left and Right arrow keys follow the in-stream
// pager to the previous and next entry. Keys typed into a field or a media
// player, keys with modifiers, keys another handler already took, and keys
// pressed while text is selected are left alone.
(() => {
  const prev = document.querySelector('.research-pager a[rel="prev"]');
  const next = document.querySelector('.research-pager a[rel="next"]');
  if (!prev && !next) return;

  document.addEventListener("keydown", (e) => {
    if (e.defaultPrevented || e.altKey || e.ctrlKey || e.metaKey || e.shiftKey) return;
    const link = e.key === "ArrowLeft" ? prev : e.key === "ArrowRight" ? next : null;
    if (!link) return;

    const active = document.activeElement;
    if (active && (active.isContentEditable || active.matches("input, textarea, select, video, audio"))) return;
    if (!window.getSelection().isCollapsed) return;

    e.preventDefault();
    window.location.href = link.href;
  });
})();
