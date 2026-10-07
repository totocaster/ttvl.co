const lightbox = {
  overlay: null,
  items: [],
  index: 0,
  trigger: null,
  previousBodyOverflow: "",

  init() {
    document
      .querySelectorAll("[data-lightbox-gallery], .leaves-grid")
      .forEach((gallery) => {
        const items = Array.from(gallery.querySelectorAll("a > img"))
          .filter((image) => image.parentElement.href === image.src)
          .map((image) => ({
            alt: image.alt,
            date: this.dateOf(image.parentElement),
            link: image.parentElement,
            src: image.parentElement.href,
          }));

        items.forEach((item, index) => {
          item.link.addEventListener("click", (event) => {
            event.preventDefault();
            this.open(items, index, item.link);
          });
        });
      });
  },

  // The date an item carries, for the counter: a data-date on the link,
  // a <time datetime> beside it in its tile (Loose Leaves), or a
  // YYYY-MM-DD at the start of the file's name. Empty when it has none.
  dateOf(link) {
    const iso = /^\d{4}-\d{2}-\d{2}$/;
    if (iso.test(link.dataset.date || "")) return link.dataset.date;
    const tile = link.closest("li, figure, .leaf");
    const time = tile && tile.querySelector("time[datetime]");
    if (time && iso.test(time.getAttribute("datetime"))) {
      return time.getAttribute("datetime");
    }
    const name = decodeURIComponent(link.pathname.split("/").pop() || "");
    const match = name.match(/^(\d{4}-\d{2}-\d{2})/);
    return match ? match[1] : "";
  },

  open(items, index, trigger) {
    if (this.overlay) this.close(false);

    this.items = items;
    this.index = index;
    this.trigger = trigger;
    this.previousBodyOverflow = document.body.style.overflow;

    const overlay = document.createElement("div");
    overlay.className = "lightbox";
    overlay.setAttribute("role", "dialog");
    overlay.setAttribute("aria-modal", "true");
    overlay.setAttribute("aria-label", "Image viewer");

    const figure = document.createElement("figure");
    figure.className = "lightbox__figure";

    const image = document.createElement("img");
    image.className = "lightbox__image";

    const closeButton = this.createButton(
      "lightbox__close",
      "Close image viewer",
      "×",
    );
    const previousButton = this.createButton(
      "lightbox__previous",
      "Previous image",
      "←",
    );
    const nextButton = this.createButton(
      "lightbox__next",
      "Next image",
      "→",
    );

    // The bar along the bottom: the counter at left, the keys at right.
    const bar = document.createElement("div");
    bar.className = "lightbox__bar";

    const counter = document.createElement("p");
    counter.className = "lightbox__counter";
    counter.setAttribute("aria-live", "polite");

    const legend = document.createElement("p");
    legend.className = "lightbox__legend";
    legend.setAttribute("aria-hidden", "true");
    legend.append("esc closes");
    if (items.length > 1) {
      ["←", "→"].forEach((key) => {
        const kbd = document.createElement("kbd");
        kbd.textContent = key;
        legend.append(" ", kbd);
      });
    }

    bar.append(counter, legend);

    closeButton.addEventListener("click", () => this.close());
    previousButton.addEventListener("click", () => this.previous());
    nextButton.addEventListener("click", () => this.next());
    overlay.addEventListener("click", (event) => {
      if (event.target === overlay) this.close();
    });

    figure.appendChild(image);
    overlay.append(figure, bar, closeButton, previousButton, nextButton);
    document.body.appendChild(overlay);
    document.body.style.overflow = "hidden";

    this.overlay = overlay;
    this.image = image;
    this.counter = counter;
    this.previousButton = previousButton;
    this.nextButton = nextButton;
    this.handleKeydown = (event) => this.onKeydown(event);
    document.addEventListener("keydown", this.handleKeydown);

    this.update();
    closeButton.focus();
  },

  createButton(className, label, text) {
    const button = document.createElement("button");
    button.className = `lightbox__button ${className}`;
    button.type = "button";
    button.setAttribute("aria-label", label);
    button.textContent = text;
    return button;
  },

  update() {
    const item = this.items[this.index];
    this.image.src = item.src;
    this.image.alt = item.alt;
    // "2 / 57 · 2025-04-19", the numbers in Mono.
    const numbers = document.createElement("span");
    numbers.className = "n";
    numbers.textContent = `${this.index + 1} / ${this.items.length}`;
    this.counter.replaceChildren(numbers);
    if (item.date) {
      const time = document.createElement("time");
      time.dateTime = item.date;
      time.textContent = item.date;
      this.counter.append(" · ", time);
    }

    const hasMultipleImages = this.items.length > 1;
    this.previousButton.hidden = !hasMultipleImages;
    this.nextButton.hidden = !hasMultipleImages;
  },

  previous() {
    this.index = (this.index - 1 + this.items.length) % this.items.length;
    this.update();
  },

  next() {
    this.index = (this.index + 1) % this.items.length;
    this.update();
  },

  onKeydown(event) {
    if (event.key === "Escape") {
      event.preventDefault();
      this.close();
    } else if (event.key === "ArrowLeft" && this.items.length > 1) {
      event.preventDefault();
      this.previous();
    } else if (event.key === "ArrowRight" && this.items.length > 1) {
      event.preventDefault();
      this.next();
    } else if (event.key === "Tab") {
      this.trapFocus(event);
    }
  },

  trapFocus(event) {
    const controls = Array.from(
      this.overlay.querySelectorAll("button:not([hidden])"),
    );
    const firstControl = controls[0];
    const lastControl = controls[controls.length - 1];

    if (event.shiftKey && document.activeElement === firstControl) {
      event.preventDefault();
      lastControl.focus();
    } else if (!event.shiftKey && document.activeElement === lastControl) {
      event.preventDefault();
      firstControl.focus();
    }
  },

  close(restoreFocus = true) {
    if (!this.overlay) return;

    document.removeEventListener("keydown", this.handleKeydown);
    this.overlay.remove();
    this.overlay = null;
    document.body.style.overflow = this.previousBodyOverflow;

    if (restoreFocus && this.trigger) this.trigger.focus();
  },
};

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => lightbox.init());
} else {
  lightbox.init();
}
