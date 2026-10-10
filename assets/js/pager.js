// The pager: on a research entry and on a Log month, the Left and Right
// arrow keys follow the end block's rows to the previous and next page.
// Keys typed into a field, a media player, or a viewer, keys with modifiers, keys
// another handler already took, and keys pressed while text is selected
// are left alone.
(() => {
  const prev = document.querySelector('.pager a[rel="prev"]');
  const next = document.querySelector('.pager a[rel="next"]');
  if (!prev && !next) return;

  document.addEventListener("keydown", (e) => {
    if (e.defaultPrevented || e.altKey || e.ctrlKey || e.metaKey || e.shiftKey) return;
    const link = e.key === "ArrowLeft" ? prev : e.key === "ArrowRight" ? next : null;
    if (!link) return;

    const active = document.activeElement;
    if (active && (active.isContentEditable || active.matches("input, textarea, select, video, audio, canvas, model-viewer") || active.closest(".viewer"))) return;
    if (!window.getSelection().isCollapsed) return;

    e.preventDefault();
    window.location.href = link.href;
  });
})();
