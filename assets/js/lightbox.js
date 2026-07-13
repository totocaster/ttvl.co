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

    const counter = document.createElement("p");
    counter.className = "lightbox__counter";
    counter.setAttribute("aria-live", "polite");

    closeButton.addEventListener("click", () => this.close());
    previousButton.addEventListener("click", () => this.previous());
    nextButton.addEventListener("click", () => this.next());
    overlay.addEventListener("click", (event) => {
      if (event.target === overlay) this.close();
    });

    figure.appendChild(image);
    overlay.append(figure, closeButton, previousButton, nextButton, counter);
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
    this.counter.textContent = `${this.index + 1} / ${this.items.length}`;

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
