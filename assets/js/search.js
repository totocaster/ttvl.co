(function() {
  'use strict';

  let searchIndex = null;
  let searchOverlay = null;
  let searchInput = null;
  let searchResults = null;
  let selectedIndex = -1;
  let focusTrapHandler = null;
  let previousActiveElement = null;
  let searchIndexPromise = null;

  // Initialize search functionality
  function initSearch() {
    createSearchOverlay();
    bindEvents();
  }

  // Create search overlay elements
  function createSearchOverlay() {
    // Create overlay container
    searchOverlay = document.createElement('div');
    searchOverlay.id = 'search-overlay';
    searchOverlay.className = 'search-overlay';
    searchOverlay.style.display = 'none';
    searchOverlay.setAttribute('role', 'dialog');
    searchOverlay.setAttribute('aria-modal', 'true');
    searchOverlay.setAttribute('aria-label', 'Site search');

    // Create search container
    const searchContainer = document.createElement('div');
    searchContainer.className = 'search-container';

    // Create logo element
    const logoContainer = document.createElement('div');
    logoContainer.className = 'search-logo';
    const logoImg = document.createElement('img');
    logoImg.src = '/ui/ttvl_logo.png';
    logoImg.srcset = '/ui/ttvl_logo@2x.png 2x, /ui/ttvl_logo@3x.png 3x';
    logoImg.alt = 'TTVL';
    logoContainer.appendChild(logoImg);

    // Search instructions
    const searchInstructions = document.createElement('p');
    searchInstructions.className = 'search-instructions';
    searchInstructions.textContent = 'Type to search. Use the arrow keys to navigate, or press Esc to close.';

    // Create search input
    searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.className = 'search-input';
    searchInput.placeholder = 'Search...';
    searchInput.setAttribute('aria-label', 'Search');
    searchInput.setAttribute('autocomplete', 'off');

    // Create results container
    searchResults = document.createElement('div');
    searchResults.className = 'search-results';
    searchResults.setAttribute('role', 'listbox');

    // Assemble elements
    searchContainer.appendChild(logoContainer);
    searchContainer.appendChild(searchInstructions);
    searchContainer.appendChild(searchInput);
    searchContainer.appendChild(searchResults);
    searchOverlay.appendChild(searchContainer);
    document.body.appendChild(searchOverlay);
  }

  // Bind keyboard and input events
  function bindEvents() {
    // Show search on '?' key press
    document.addEventListener('keydown', function(e) {
      if (e.key === '?' && !isInputFocused()) {
        e.preventDefault();
        showSearch();
      } else if (e.key === 'Escape' && searchOverlay.style.display !== 'none') {
        hideSearch();
      }
    });

    // Handle search input
    searchInput.addEventListener('input', debounce(handleSearch, 300));

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
        const links = searchResults.querySelectorAll('.search-result-link');
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
        searchResults.innerHTML = '<div class="search-error">Failed to load search index</div>';
      });
    }
  }

  // Hide search overlay
  function hideSearch() {
    searchOverlay.style.display = 'none';
    searchInput.value = '';
    searchResults.innerHTML = '';
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
  async function handleSearch() {
    const query = searchInput.value.trim().toLowerCase();
    
    if (!query) {
      searchResults.innerHTML = '';
      selectedIndex = -1;
      return;
    }

    searchResults.innerHTML = '<div class="search-loading">Searching…</div>';

    try {
      const index = await fetchSearchIndex();
      const results = index.filter(item => {
        return item.title.toLowerCase().includes(query) ||
               item.content.toLowerCase().includes(query) ||
               item.summary.toLowerCase().includes(query) ||
               (item.tags && item.tags.some(tag => tag.toLowerCase().includes(query)));
      });

      displayResults(results, query);
    } catch (error) {
      console.error('Failed to load search index:', error);
      searchResults.innerHTML = '<div class="search-error">Failed to load search index</div>';
    }
  }

  // Display search results
  function displayResults(results, query) {
    selectedIndex = -1;
    
    if (results.length === 0) {
      searchResults.innerHTML = '<div class="search-no-results">No results found</div>';
      return;
    }

    const html = results.slice(0, 10).map((result, index) => {
      const highlightedTitle = highlightText(result.title, query);
      const highlightedContent = highlightText(result.summary || result.content, query);
      
      return `
        <a href="${result.permalink}" class="search-result-link" data-index="${index}">
          <div class="search-result">
            <div class="search-result-title">${highlightedTitle}</div>
            <div class="search-result-meta">
              <span class="search-result-section">${result.section}</span>
              <span class="search-result-date">${result.date}</span>
            </div>
            <div class="search-result-content">${highlightedContent}</div>
          </div>
        </a>
      `;
    }).join('');

    searchResults.innerHTML = html;

    // Add hover events
    const links = searchResults.querySelectorAll('.search-result-link');
    links.forEach((link, index) => {
      link.addEventListener('mouseenter', () => {
        selectedIndex = index;
        updateSelection();
      });
    });
  }

  // Highlight matching text
  function highlightText(text, query) {
    if (!query) return text;
    
    const regex = new RegExp(`(${escapeRegExp(query)})`, 'gi');
    return text.replace(regex, '<mark>$1</mark>');
  }

  // Navigate through results with keyboard
  function navigateResults(direction) {
    const links = searchResults.querySelectorAll('.search-result-link');
    if (links.length === 0) return;

    selectedIndex += direction;
    
    if (selectedIndex < 0) selectedIndex = links.length - 1;
    if (selectedIndex >= links.length) selectedIndex = 0;
    
    updateSelection();
  }

  // Update visual selection
  function updateSelection() {
    const links = searchResults.querySelectorAll('.search-result-link');
    links.forEach((link, index) => {
      if (index === selectedIndex) {
        link.classList.add('selected');
        link.scrollIntoView({ block: 'nearest' });
      } else {
        link.classList.remove('selected');
      }
    });
  }

  // Utility functions
  function isInputFocused() {
    const activeElement = document.activeElement;
    return activeElement && (
      activeElement.tagName === 'INPUT' ||
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
