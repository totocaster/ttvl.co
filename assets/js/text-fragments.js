(function() {
  'use strict';

  const textFragments = {
    selectedText: '',
    selectedRange: null,
    selectionTimeout: null,

    init() {
      // Only initialize if browser has native Text Fragments support
      if (!('fragmentDirective' in document)) {
        return;
      }

      this.setupSelectionHandler();
      this.setupKeyboardShortcuts();
    },

    setupSelectionHandler() {
      document.addEventListener('selectionchange', () => {
        clearTimeout(this.selectionTimeout);
        this.selectionTimeout = setTimeout(() => {
          this.handleSelection();
        }, 500);
      });

      document.addEventListener('mouseup', () => {
        setTimeout(() => this.handleSelection(), 10);
      });

      document.addEventListener('touchend', () => {
        setTimeout(() => this.handleSelection(), 10);
      });
    },

    handleSelection() {
      const selection = window.getSelection();
      const selectedText = selection.toString().trim();

      if (selectedText.length > 5 && selectedText.length < 500) {
        this.selectedText = selectedText;
        this.selectedRange = selection.getRangeAt(0);
        this.updateURL();
      } else if (selectedText.length === 0) {
        // Clear fragment when no text is selected
        this.clearFragment();
      }
    },

    clearFragment() {
      const url = new URL(window.location.href);
      if (url.hash.includes(':~:text=')) {
        url.hash = '';
        const newUrl = url.href === window.location.origin + window.location.pathname ?
                       window.location.pathname : url.href;
        history.replaceState(null, '', newUrl);
      }
    },

    async updateURL() {
      try {
        const fragment = await this.generateFragment(this.selectedText);
        const url = new URL(window.location.href);
        url.hash = fragment;
        history.replaceState(null, '', url);
      } catch (error) {
        console.error('Failed to update URL with text fragment:', error);
      }
    },

    async generateFragment(text) {
      const encoded = encodeURIComponent(text);
      const context = this.getTextContext(text);
      let fragment = `:~:text=`;

      if (context.prefix) {
        fragment += encodeURIComponent(context.prefix) + '-,';
      }

      fragment += encoded;

      if (context.suffix) {
        fragment += ',-' + encodeURIComponent(context.suffix);
      }

      return fragment;
    },

    getTextContext(text) {
      if (!this.selectedRange) return { prefix: '', suffix: '' };

      const container = this.selectedRange.commonAncestorContainer;
      const containerText = container.textContent || container.innerText || '';
      const textIndex = containerText.indexOf(text);

      if (textIndex === -1) return { prefix: '', suffix: '' };

      const prefixStart = Math.max(0, textIndex - 20);
      const suffixEnd = Math.min(containerText.length, textIndex + text.length + 20);

      let prefix = containerText.substring(prefixStart, textIndex).trim();
      let suffix = containerText.substring(textIndex + text.length, suffixEnd).trim();

      if (prefix) {
        const words = prefix.split(/\s+/);
        prefix = words.slice(-2).join(' ');
      }

      if (suffix) {
        const words = suffix.split(/\s+/);
        suffix = words.slice(0, 2).join(' ');
      }

      return { prefix, suffix };
    },

    setupKeyboardShortcuts() {
      document.addEventListener('keydown', (e) => {
        // Cmd/Ctrl+Shift+L to generate fragment for current selection
        if ((e.metaKey || e.ctrlKey) && e.shiftKey && e.key === 'L') {
          e.preventDefault();
          const selection = window.getSelection();
          const selectedText = selection.toString().trim();

          if (selectedText.length > 5) {
            this.selectedText = selectedText;
            this.selectedRange = selection.getRangeAt(0);
            this.updateURL();
          }
        }

        // Escape to clear selection and remove fragment
        if (e.key === 'Escape') {
          const selection = window.getSelection();
          if (selection.toString()) {
            selection.removeAllRanges();
            this.clearFragment();
          }
        }
      });
    }
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => textFragments.init());
  } else {
    textFragments.init();
  }
})();