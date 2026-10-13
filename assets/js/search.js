(function() {
  'use strict';

  let searchIndex = null;
  let searchOverlay = null;
  let searchInput = null;
  let searchResults = null;
  let searchStatus = null;
  let selectedIndex = -1;
  let focusTrapHandler = null;
  let previousActiveElement = null;
  let searchIndexPromise = null;
  let searchRequest = 0;

  // Initialize search functionality
  function initSearch() {
    createSearchOverlay();
    bindEvents();
  }

  // Create the overlay: the hint with keycaps, the input with one rule
  // under it, the results as rows, and the count or state under them.
  // docs/styleguide.md, Search Overlay.
  function createSearchOverlay() {
    searchOverlay = document.createElement('div');
    searchOverlay.id = 'search-overlay';
    searchOverlay.className = 'search-overlay';
    searchOverlay.style.display = 'none';
    searchOverlay.setAttribute('role', 'dialog');
    searchOverlay.setAttribute('aria-modal', 'true');
    searchOverlay.setAttribute('aria-label', 'Site search');

    const searchContainer = document.createElement('div');
    searchContainer.className = 'search-container';

    const toolbar = document.createElement('div');
    toolbar.className = 'search-toolbar';
    const label = document.createElement('label');
    label.htmlFor = 'site-search-input';
    label.textContent = 'Search site';
    const close = document.createElement('button');
    close.type = 'button';
    close.className = 'btn btn--quiet search-close';
    close.textContent = 'Close';
    close.setAttribute('aria-label', 'Close search');
    close.addEventListener('click', hideSearch);
    toolbar.append(label, close);

    // Static markup only — never interpolate query text here.
    const hint = document.createElement('p');
    hint.className = 'search-hint';
    hint.innerHTML =
      '<kbd>↑</kbd> <kbd>↓</kbd> select · <kbd>↩</kbd> open · <kbd>esc</kbd> close · <kbd>?</kbd> opens search from any page';

    const field = document.createElement('div');
    field.className = 'search-field';
    searchInput = document.createElement('input');
    searchInput.type = 'search';
    searchInput.id = 'site-search-input';
    searchInput.className = 'search-input';
    searchInput.placeholder = 'Search notes, projects, and more';
    searchInput.setAttribute('aria-controls', 'search-results');
    searchInput.setAttribute('autocomplete', 'off');
    searchInput.setAttribute('spellcheck', 'false');
    field.appendChild(searchInput);

    searchResults = document.createElement('ul');
    searchResults.id = 'search-results';
    searchResults.className = 'rows with-deks search-results';

    searchStatus = document.createElement('p');
    searchStatus.className = 'legend search-status';
    searchStatus.setAttribute('aria-live', 'polite');

    searchContainer.append(toolbar, field, hint, searchResults, searchStatus);
    searchOverlay.appendChild(searchContainer);
    document.body.appendChild(searchOverlay);
  }

  // Bind keyboard and input events
  function bindEvents() {
    // Show search on '?' key press
    document.addEventListener('keydown', function(e) {
      if (e.key === '?' && !e.metaKey && !e.ctrlKey && !e.altKey && !isInputFocused()) {
        e.preventDefault();
        showSearch();
      } else if (e.key === 'Escape' && searchOverlay.style.display !== 'none') {
        hideSearch();
      }
    });

    // The masthead's search key opens the overlay like '?' does.
    document.addEventListener('click', function(e) {
      const key = e.target.closest && e.target.closest('.search-key');
      if (key) {
        e.preventDefault();
        showSearch();
      }
    });

    // Handle search input
    const queueSearch = debounce(handleSearch, 300);
    searchInput.addEventListener('input', () => queueSearch(++searchRequest));

    // Handle keyboard navigation
    searchInput.addEventListener('keydown', function(e) {
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        navigateResults(1);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        navigateResults(-1);
      } else if (e.key === 'Enter' && selectedIndex >= 0) {
        e.preventDefault();
        const links = searchResults.querySelectorAll('.row-title');
        if (links[selectedIndex]) {
          window.location.href = links[selectedIndex].href;
        }
      }
    });

    // Close on overlay click
    searchOverlay.addEventListener('click', function(e) {
      if (e.target === searchOverlay) {
        hideSearch();
      }
    });
  }

  // Show search overlay
  function showSearch() {
    previousActiveElement = document.activeElement;
    searchOverlay.style.display = 'flex';
    searchInput.focus();
    searchInput.select();
    document.body.style.overflow = 'hidden';
    focusTrapHandler = createFocusTrapHandler();
    searchOverlay.addEventListener('keydown', focusTrapHandler);

    // Load search index if not already loaded
    if (!searchIndex) {
      fetchSearchIndex().catch((error) => {
        console.error('Failed to load search index:', error);
        setStatus('Search failed to load. Close it and try again.', 'is-error');
      });
    }
  }

  // Hide search overlay
  function hideSearch() {
    searchRequest += 1;
    searchOverlay.style.display = 'none';
    searchInput.value = '';
    searchResults.innerHTML = '';
    setStatus('');
    selectedIndex = -1;
    document.body.style.overflow = '';
    if (focusTrapHandler) {
      searchOverlay.removeEventListener('keydown', focusTrapHandler);
      focusTrapHandler = null;
    }
    if (previousActiveElement) {
      previousActiveElement.focus();
      previousActiveElement = null;
    }
  }

  // Load search index
  function fetchSearchIndex() {
    if (searchIndex) {
      return Promise.resolve(searchIndex);
    }

    if (searchIndexPromise) {
      return searchIndexPromise;
    }

    searchIndexPromise = fetch('/index.json')
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Search index request failed with status ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        searchIndex = data;
        return data;
      })
      .catch((error) => {
        searchIndexPromise = null;
        throw error;
      });

    return searchIndexPromise;
  }

  // Handle search input
  async function handleSearch(request) {
    if (request !== searchRequest) return;
    const query = searchInput.value.trim().toLowerCase();

    if (!query) {
      searchResults.innerHTML = '';
      setStatus('');
      selectedIndex = -1;
      return;
    }

    searchResults.innerHTML = '';
    selectedIndex = -1;
    setStatus('Searching…');

    try {
      const index = await fetchSearchIndex();
      if (request !== searchRequest) return;
      const results = index.filter(item => {
        return item.title.toLowerCase().includes(query) ||
               item.content.toLowerCase().includes(query) ||
               item.summary.toLowerCase().includes(query) ||
               (item.tags && item.tags.some(tag => tag.toLowerCase().includes(query)));
      });

      displayResults(results, query);
    } catch (error) {
      if (request !== searchRequest) return;
      console.error('Failed to load search index:', error);
      setStatus('Search failed to load. Close it and try again.', 'is-error');
    }
  }

  // The line under the results: the count, or the state.
  function setStatus(text, state) {
    // The live region stays in the DOM, empty when there is nothing to say,
    // so assistive tech hears each change.
    searchStatus.textContent = text;
    searchStatus.classList.toggle('is-error', state === 'is-error');
  }

  // Section names as the site shows them; anything else reads its folder
  // name in sentence case.
  const sectionNames = {
    bookbinding: 'Bookbinding',
    darkroom: 'Darkroom',
    flaneur: 'Dispatch',
    leaves: 'Loose Leaves',
    log: 'Log',
    'notebook-system': 'Notebook System',
    notes: 'Notes',
    obsidian: 'Obsidian',
    'project-humane': 'Project Humane',
    projects: 'Projects',
    research: 'Research',
    traces: 'Traces'
  };

  function sectionName(section) {
    if (!section) return '';
    if (sectionNames[section]) return sectionNames[section];
    const words = section.replace(/[-_]+/g, ' ');
    return words.charAt(0).toUpperCase() + words.slice(1);
  }

  // Display search results as rows: the section as the meta, the title
  // with the match marked, the summary as the dek, the date as the tail.
  function displayResults(results, query) {
    selectedIndex = -1;

    if (results.length === 0) {
      searchResults.innerHTML = '';
      setStatus('No results');
      return;
    }

    const shown = results.slice(0, 10);
    searchResults.innerHTML = shown.map((result, index) => {
      const date = /^\d{4}-\d{2}-\d{2}$/.test(result.date) && result.date !== '0001-01-01'
        ? `<time datetime="${result.date}">${result.date}</time>`
        : '';
      const dek = highlightText(searchExcerpt(result, query), query);
      return `<li class="row" data-index="${index}">` +
        `<span class="row-meta">${escapeHTML(sectionName(result.section))}</span>` +
        `<span class="row-main"><a class="row-title" href="${escapeHTML(result.permalink)}">${highlightText(result.title, query)}</a>` +
        (dek ? `<span class="row-dek">${dek}</span>` : '') +
        `</span>` +
        (date ? `<span class="row-tail">${date}</span>` : '') +
        `</li>`;
    }).join('');

    const n = results.length;
    let status = `${n} ${n === 1 ? 'result' : 'results'}`;
    if (n > shown.length) status += ` · showing the first ${shown.length}`;
    setStatus(status);
    // Numbers in the chrome are Mono.
    searchStatus.innerHTML = escapeHTML(status).replace(/\d+/g, '<span class="n">$&</span>');

    // Hovering a row selects it, as the arrow keys do.
    searchResults.querySelectorAll('.row').forEach((row, index) => {
      row.addEventListener('mouseenter', () => {
        selectedIndex = index;
        updateSelection(false);
      });
    });
  }

  // A short excerpt around a match, so a phone result stays scannable.
  function searchExcerpt(result, query) {
    const summary = toText(result.summary || '').replace(/\s+/g, ' ').trim();
    const content = toText(result.content || '').replace(/\s+/g, ' ').trim();
    const text = summary.toLowerCase().includes(query) ? summary : content || summary;
    const match = text.toLowerCase().indexOf(query);
    let start = Math.max(0, match - 40);
    if (start) {
      const boundary = text.indexOf(' ', start);
      start = boundary >= 0 && boundary < match ? boundary + 1 : start;
    }
    let end = Math.min(text.length, start + 160);
    if (end < text.length) {
      const boundary = text.lastIndexOf(' ', end);
      if (boundary > start) end = boundary;
    }
    return (start ? '…' : '') + text.slice(start, end) + (end < text.length ? '…' : '');
  }

  // The index holds plain text that may still carry entities; read it as
  // text, escape it, then mark every match.
  function highlightText(text, query) {
    const plain = toText(text || '');
    if (!query) return escapeHTML(plain);
    const regex = new RegExp(`(${escapeRegExp(query)})`, 'gi');
    // split with a capture group puts the matches at the odd indexes.
    return plain.split(regex).map((part, i) =>
      i % 2 ? `<mark>${escapeHTML(part)}</mark>` : escapeHTML(part)
    ).join('');
  }

  const decoder = document.createElement('textarea');
  function toText(value) {
    decoder.innerHTML = value;
    return decoder.value;
  }

  function escapeHTML(value) {
    return String(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  // Navigate through results with keyboard
  function navigateResults(direction) {
    const rows = searchResults.querySelectorAll('.row');
    if (rows.length === 0) return;

    selectedIndex += direction;

    if (selectedIndex < 0) selectedIndex = rows.length - 1;
    if (selectedIndex >= rows.length) selectedIndex = 0;

    updateSelection(true);
  }

  // The selected row takes a surface wash.
  function updateSelection(scroll) {
    const rows = searchResults.querySelectorAll('.row');
    rows.forEach((row, index) => {
      const selected = index === selectedIndex;
      row.classList.toggle('is-selected', selected);
      if (selected && scroll) row.scrollIntoView({ block: 'nearest' });
    });
  }

  // Utility functions
  function isInputFocused() {
    const activeElement = document.activeElement;
    return activeElement && (
      activeElement.tagName === 'INPUT' ||
      activeElement.tagName === 'SELECT' ||
      activeElement.tagName === 'TEXTAREA' ||
      activeElement.isContentEditable
    );
  }

  function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  function createFocusTrapHandler() {
    return function(e) {
      if (e.key !== 'Tab') return;
      const focusable = searchOverlay.querySelectorAll(
        'a[href], button:not([disabled]), textarea, input, select, [tabindex]:not([tabindex="-1"])'
      );
      if (!focusable.length) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (e.shiftKey) {
        if (document.activeElement === first) {
          e.preventDefault();
          last.focus();
        }
      } else if (document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    };
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSearch);
  } else {
    initSearch();
  }
})();
