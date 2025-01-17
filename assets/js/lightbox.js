const lightbox = {
  overlay: null,

  init() {
    document.querySelectorAll('article a > img, .leaves-grid a > img').forEach((img) => {
      if (img.parentElement.href === img.src) {
        img.parentElement.onclick = (e) => {
          e.preventDefault();
          lightbox.open(img.src);
        };
      }
    });

    window.addEventListener('keyup', (e) => {
      if (e.key === 'Escape') {
        lightbox.close();
      }
    });
  },

  open(src) {
    this.overlay = document.createElement('div');
    this.overlay.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.9);z-index:1000;display:flex;align-items:center;justify-content:center;cursor:pointer;';

    const img = document.createElement('img');
    img.src = src;
    img.style.cssText = 'max-height:90vh;max-width:90vw;object-fit:contain;';
    img.onclick = (e) => e.stopPropagation();

    this.overlay.onclick = () => lightbox.close();
    this.overlay.appendChild(img);
    document.body.appendChild(this.overlay);
    document.body.style.overflow = 'hidden';
  },

  close() {
    if (this.overlay) {
      this.overlay.remove();
      this.overlay = null;
      document.body.style.overflow = '';
    }
  },
};

// Initialize when loaded
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => lightbox.init());
} else {
  lightbox.init();
}
