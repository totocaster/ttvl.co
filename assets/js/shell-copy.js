(() => {
  document.addEventListener("click", (event) => {
    const button = event.target.closest(".shell-copy");
    if (!button) return;

    const line = button.parentElement;
    const command = [];
    const ownText = line.cloneNode(true);
    ownText.querySelector(".shell-copy").remove();
    command.push(ownText.textContent.trim());

    let next = line.nextElementSibling;
    while (next && next.classList.contains("shell-line--cont")) {
      command.push(next.textContent.replace(/^\s{2}/, ""));
      next = next.nextElementSibling;
    }

    navigator.clipboard.writeText(command.join("\n")).then(() => {
      button.textContent = "✓";
      setTimeout(() => {
        button.textContent = "$";
      }, 1200);
    });
  });
})();
