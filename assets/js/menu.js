const menu = {
  toggle: null,
  nav: null,
  body: null,

  init() {
    this.toggle = document.getElementById('menu-toggle');
    this.nav = document.querySelector('nav');
    this.body = document.body;

    if (this.toggle && this.nav) {
      this.toggle.addEventListener('click', () => this.toggleMenu());
    }
  },

  toggleMenu() {
    const isActive = this.nav.classList.contains('is-active');
    this.nav.classList.toggle('is-active');
    this.toggle.classList.toggle('is-active');
    this.body.classList.toggle('menu-open');
    this.toggle.textContent = isActive ? 'Menu' : 'Close';
  },
};

// Initialize when loaded
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => menu.init());
} else {
  menu.init();
}
