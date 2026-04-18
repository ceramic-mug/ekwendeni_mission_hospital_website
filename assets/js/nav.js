/**
 * nav.js — Shared navigation and footer loader
 *
 * This script:
 *  1. Loads fragments/nav.html and fragments/footer.html into every page
 *  2. Highlights the active page link in the navigation
 *  3. Handles the mobile hamburger menu toggle
 *
 * NOTE: This script requires the site to be served over HTTP (not opened
 * as a file:// URL) because it uses fetch(). When editing locally, run:
 *
 *   python3 -m http.server 8080
 *
 * in the project root, then open http://localhost:8080
 */

(function () {
  'use strict';

  /**
   * Load an HTML fragment into a container element.
   * @param {string} selector - CSS selector for the container element
   * @param {string} url - URL of the HTML fragment to load
   * @param {Function} [callback] - Optional function to call after the fragment loads
   */
  function loadFragment(selector, url, callback) {
    var container = document.querySelector(selector);
    if (!container) return;

    fetch(url)
      .then(function (response) {
        if (!response.ok) {
          throw new Error('Could not load fragment: ' + url + ' (HTTP ' + response.status + ')');
        }
        return response.text();
      })
      .then(function (html) {
        container.innerHTML = html;
        if (typeof callback === 'function') {
          callback();
        }
      })
      .catch(function (err) {
        console.warn('[nav.js] Fragment load failed:', err.message);
        // Show a minimal fallback so the page is still usable
        if (selector === '#nav-container') {
          container.innerHTML = '<nav style="background:#1a5276;padding:1rem;text-align:center">'
            + '<a href="/index.html" style="color:white;font-weight:bold">Ekwendeni Mission Hospital</a>'
            + ' | <a href="/about.html" style="color:rgba(255,255,255,0.8)">About</a>'
            + ' | <a href="/services.html" style="color:rgba(255,255,255,0.8)">Services</a>'
            + ' | <a href="/events.html" style="color:rgba(255,255,255,0.8)">Events</a>'
            + ' | <a href="/donate.html" style="color:rgba(255,255,255,0.8)">Donate</a>'
            + ' | <a href="/contact.html" style="color:rgba(255,255,255,0.8)">Contact</a>'
            + '</nav>';
        }
      });
  }

  /**
   * Highlight the nav link that matches the current page URL.
   * Adds the class 'active' to the matching anchor element.
   */
  function setActiveNavLink() {
    var path = window.location.pathname;

    // Normalise: treat /index.html and / as the same
    var currentFile = path.split('/').pop() || 'index.html';
    if (currentFile === '') currentFile = 'index.html';

    var navLinks = document.querySelectorAll('.nav-links a');
    navLinks.forEach(function (link) {
      var href = link.getAttribute('href');
      if (!href) return;

      // Strip query string and fragment from href
      var hrefFile = href.split('?')[0].split('#')[0].split('/').pop();

      if (hrefFile === currentFile && !href.includes('#')) {
        link.classList.add('active');
      }
    });
  }

  /**
   * Set up the mobile hamburger menu toggle.
   * Looks for .nav-toggle button and .site-nav element after fragment loads.
   */
  function setupMobileMenu() {
    var nav = document.querySelector('.site-nav');
    var toggle = document.querySelector('.nav-toggle');
    if (!nav || !toggle) return;

    // Inject backdrop element after the nav container
    var backdrop = document.createElement('div');
    backdrop.className = 'nav-backdrop';
    backdrop.style.display = 'none';
    var navContainer = document.getElementById('nav-container');
    if (navContainer) navContainer.insertAdjacentElement('afterend', backdrop);

    function closeMenu() {
      nav.classList.remove('nav-open');
      toggle.setAttribute('aria-expanded', 'false');
      backdrop.style.display = 'none';
      closeAllDropdowns();
    }

    function closeAllDropdowns() {
      document.querySelectorAll('.nav-dropdown.is-open').forEach(function (li) {
        li.classList.remove('is-open');
        var btn = li.querySelector('.nav-dropdown-toggle');
        if (btn) btn.setAttribute('aria-expanded', 'false');
      });
    }

    // Hamburger toggle
    toggle.addEventListener('click', function () {
      var isOpen = nav.classList.toggle('nav-open');
      toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      backdrop.style.display = isOpen ? 'block' : 'none';
      if (!isOpen) closeAllDropdowns();
    });

    // Backdrop click closes menu
    backdrop.addEventListener('click', closeMenu);

    // Accordion: chevron buttons expand/collapse submenus
    document.querySelectorAll('.nav-dropdown-toggle').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var parentLi = btn.closest('.nav-dropdown');
        var opening = !parentLi.classList.contains('is-open');

        // Close all dropdowns first (accordion)
        closeAllDropdowns();

        if (opening) {
          parentLi.classList.add('is-open');
          btn.setAttribute('aria-expanded', 'true');
        }
      });
    });

    // Close menu when a nav link is clicked
    document.querySelectorAll('.nav-links a').forEach(function (link) {
      link.addEventListener('click', closeMenu);
    });
  }

  /**
   * Set up the sticky subnav active link highlighting
   * (used on about.html and services.html).
   * Uses IntersectionObserver to track which section is in view.
   */
  function setupSubnavHighlight() {
    var subnav = document.querySelector('.subnav');
    if (!subnav) return;

    var sections = document.querySelectorAll('section[id]');
    var subnavLinks = subnav.querySelectorAll('a');
    if (!sections.length || !subnavLinks.length) return;

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            var id = entry.target.id;
            subnavLinks.forEach(function (link) {
              var href = link.getAttribute('href');
              if (href && href.endsWith('#' + id)) {
                link.classList.add('active');
              } else {
                link.classList.remove('active');
              }
            });
          }
        });
      },
      { rootMargin: '-120px 0px -60% 0px', threshold: 0 }
    );

    sections.forEach(function (section) {
      observer.observe(section);
    });
  }

  // ---- Initialise on DOM ready ----
  document.addEventListener('DOMContentLoaded', function () {
    loadFragment('#nav-container', '/fragments/nav.html', function () {
      setActiveNavLink();
      setupMobileMenu();
    });

    loadFragment('#footer-container', '/fragments/footer.html');

    // Subnav highlight runs after a short delay to ensure
    // the page sections are all in the DOM
    setTimeout(setupSubnavHighlight, 100);
  });

})();
