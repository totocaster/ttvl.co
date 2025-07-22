(function() {
  'use strict';

  let searchIndex = null;
  let searchOverlay = null;
  let searchInput = null;
  let searchResults = null;
  let selectedIndex = -1;

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

    // Create search container
    const searchContainer = document.createElement('div');
    searchContainer.className = 'search-container';

    // Create search input
    searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.className = 'search-input';
    searchInput.placeholder = 'Search...';
    searchInput.setAttribute('autocomplete', 'off');

    // Create results container
    searchResults = document.createElement('div');
    searchResults.className = 'search-results';

    // Assemble elements
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
    searchOverlay.style.display = 'flex';
    searchInput.focus();
    searchInput.select();
    document.body.style.overflow = 'hidden';

    // Load search index if not already loaded
    if (!searchIndex) {
      loadSearchIndex();
    }
  }

  // Hide search overlay
  function hideSearch() {
    searchOverlay.style.display = 'none';
    searchInput.value = '';
    searchResults.innerHTML = '';
    selectedIndex = -1;
    document.body.style.overflow = '';
  }

  // Load search index
  async function loadSearchIndex() {
    try {
      const response = await fetch('/index.json');
      searchIndex = await response.json();
    } catch (error) {
      console.error('Failed to load search index:', error);
      searchResults.innerHTML = '<div class="search-error">Failed to load search index</div>';
    }
  }

  // Handle search input
  function handleSearch() {
    const query = searchInput.value.trim().toLowerCase();
    
    if (!query) {
      searchResults.innerHTML = '';
      selectedIndex = -1;
      return;
    }

    if (!searchIndex) {
      searchResults.innerHTML = '<div class="search-loading">Loading search index...</div>';
      return;
    }

    const results = searchIndex.filter(item => {
      return item.title.toLowerCase().includes(query) ||
             item.content.toLowerCase().includes(query) ||
             item.summary.toLowerCase().includes(query) ||
             (item.tags && item.tags.some(tag => tag.toLowerCase().includes(query)));
    });

    displayResults(results, query);
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

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSearch);
  } else {
    initSearch();
  }
})();