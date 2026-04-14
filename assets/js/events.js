/**
 * events.js — Event listing and calendar renderer
 *
 * Fetches data/events.json and renders:
 *   - A list of upcoming events as cards (#events-list)
 *   - A collapsible list of past events (#past-events-list)
 *   - An optional monthly calendar view (#calendar-grid)
 *   - A preview of upcoming events on the home page (#news-preview)
 *
 * The data source is data/events.json.
 * Use the Python admin GUI (tools/admin_gui.py) to manage events.
 */

(function () {
  'use strict';

  var EVENTS_URL = '/data/events.json';

  /* ---- Date helpers ---- */

  var MONTHS_SHORT = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  var MONTHS_LONG  = ['January','February','March','April','May','June',
                      'July','August','September','October','November','December'];
  var DAYS_SHORT   = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];

  function parseDate(str) {
    // Parse YYYY-MM-DD without timezone shifting
    var parts = str.split('-');
    return new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]));
  }

  function today() {
    var d = new Date();
    return new Date(d.getFullYear(), d.getMonth(), d.getDate());
  }

  function formatDateLong(dateStr) {
    var d = parseDate(dateStr);
    return DAYS_SHORT[d.getDay()] + ', ' +
           MONTHS_LONG[d.getMonth()] + ' ' +
           d.getDate() + ', ' +
           d.getFullYear();
  }

  function formatTime(timeStr) {
    if (!timeStr) return '';
    var parts = timeStr.split(':');
    var h = parseInt(parts[0]);
    var m = parts[1];
    var ampm = h >= 12 ? 'PM' : 'AM';
    h = h % 12 || 12;
    return h + ':' + m + ' ' + ampm;
  }

  /* ---- Category tag rendering ---- */

  var CATEGORY_LABELS = {
    'community-health': 'Community Health',
    'training':         'Training',
    'outreach':         'Outreach',
    'fundraising':      'Fundraising',
    'general':          'General'
  };

  function categoryTag(cat) {
    var label = CATEGORY_LABELS[cat] || cat;
    return '<span class="card-tag card-tag--' + (cat || 'general') + '">' + escHtml(label) + '</span>';
  }

  /* ---- Security: escape HTML entities ---- */

  function escHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  /* ---- Event card HTML ---- */

  function renderEventCard(event) {
    var d = parseDate(event.date);
    var day   = d.getDate();
    var month = MONTHS_SHORT[d.getMonth()];

    var timeHtml = event.time
      ? '<span>&#128336; ' + escHtml(formatTime(event.time)) + '</span> &nbsp; '
      : '';

    var locationHtml = event.location
      ? '<span>&#128205; ' + escHtml(event.location) + '</span>'
      : '';

    var imgHtml = '';
    if (event.image) {
      imgHtml = '<img src="/' + escHtml(event.image) + '" '
              + 'alt="' + escHtml(event.image_alt || event.title) + '" '
              + 'style="width:140px;height:100%;object-fit:cover;flex-shrink:0;" '
              + 'loading="lazy">';
    }

    var cancelledBadge = event.status === 'cancelled'
      ? '<span style="color:#c0392b;font-weight:bold;font-size:0.8rem;">[CANCELLED] </span>'
      : '';

    return '<article class="event-card">'
      + '<div class="event-card-date">'
      +   '<span class="event-card-day">' + day + '</span>'
      +   '<span class="event-card-month">' + month + '</span>'
      + '</div>'
      + '<div class="event-card-body">'
      +   categoryTag(event.category)
      +   '<h3>' + cancelledBadge + escHtml(event.title) + '</h3>'
      +   '<p class="event-card-meta">' + timeHtml + locationHtml + '</p>'
      +   '<p style="font-size:0.95rem;color:#626567;">' + escHtml(event.description) + '</p>'
      +   (event.contact
          ? '<p style="font-size:0.85rem;margin-top:0.5rem;">Contact: '
            + escHtml(event.contact) + '</p>'
          : '')
      + '</div>'
      + '</article>';
  }

  /* ---- Small preview card for home page ---- */

  function renderPreviewCard(event) {
    var d = parseDate(event.date);
    var dateLabel = MONTHS_SHORT[d.getMonth()] + ' ' + d.getDate() + ', ' + d.getFullYear();

    return '<article class="card">'
      + '<div class="card-body">'
      +   categoryTag(event.category)
      +   '<p class="card-meta">&#128197; ' + escHtml(dateLabel) + '</p>'
      +   '<h3 style="font-size:1rem;margin-bottom:0.5rem;">' + escHtml(event.title) + '</h3>'
      +   '<p style="font-size:0.9rem;">' + escHtml(truncate(event.description, 120)) + '</p>'
      + '</div>'
      + '</article>';
  }

  function truncate(str, maxLen) {
    if (!str) return '';
    return str.length > maxLen ? str.slice(0, maxLen).trimEnd() + '…' : str;
  }

  /* ---- List view renderer ---- */

  function renderListView(upcoming, pastContainer, upcomingContainer) {
    if (!upcoming.length) {
      upcomingContainer.innerHTML =
        '<div class="events-empty">'
        + '<p>No upcoming events scheduled at this time.</p>'
        + '<p>Check back soon or <a href="/contact.html">contact us</a> for more information.</p>'
        + '</div>';
    } else {
      upcomingContainer.innerHTML = upcoming.map(renderEventCard).join('');
    }
  }

  /* ---- Calendar view renderer ---- */

  function renderCalendar(allEvents, calendarContainer, year, month) {
    var monthName = MONTHS_LONG[month];

    // Build a set of event dates for quick lookup
    var eventDates = {};
    allEvents.forEach(function (ev) {
      var d = parseDate(ev.date);
      if (d.getFullYear() === year && d.getMonth() === month) {
        var day = d.getDate();
        if (!eventDates[day]) eventDates[day] = [];
        eventDates[day].push(ev);
      }
    });

    var todayDate = today();
    var firstDay = new Date(year, month, 1).getDay();  // 0=Sun
    var daysInMonth = new Date(year, month + 1, 0).getDate();
    var daysInPrevMonth = new Date(year, month, 0).getDate();

    var html = '<div class="calendar-header">'
      + '<button class="btn btn-outline-primary" id="cal-prev" style="padding:0.4rem 1rem;font-size:0.85rem;">&laquo; Prev</button>'
      + '<h3 style="margin:0;">' + monthName + ' ' + year + '</h3>'
      + '<button class="btn btn-outline-primary" id="cal-next" style="padding:0.4rem 1rem;font-size:0.85rem;">Next &raquo;</button>'
      + '</div>';

    html += '<div class="calendar-month-grid">';

    // Day-of-week headers
    DAYS_SHORT.forEach(function (d) {
      html += '<div class="calendar-day-label">' + d + '</div>';
    });

    // Trailing days from previous month
    for (var i = 0; i < firstDay; i++) {
      var prevDay = daysInPrevMonth - firstDay + i + 1;
      html += '<div class="calendar-day calendar-day--other-month">' + prevDay + '</div>';
    }

    // Days in current month
    for (var d2 = 1; d2 <= daysInMonth; d2++) {
      var isToday = (year === todayDate.getFullYear() &&
                     month === todayDate.getMonth() &&
                     d2 === todayDate.getDate());
      var hasEvent = !!eventDates[d2];

      var classes = 'calendar-day';
      if (isToday) classes += ' calendar-day--today';
      if (hasEvent) classes += ' calendar-day--has-event';

      var title = hasEvent
        ? eventDates[d2].map(function (e) { return e.title; }).join(', ')
        : '';

      html += '<div class="' + classes + '" title="' + escHtml(title) + '">' + d2 + '</div>';
    }

    // Leading days of next month to fill the grid
    var totalCells = firstDay + daysInMonth;
    var remainder = totalCells % 7;
    if (remainder !== 0) {
      for (var n = 1; n <= 7 - remainder; n++) {
        html += '<div class="calendar-day calendar-day--other-month">' + n + '</div>';
      }
    }

    html += '</div>';  // .calendar-month-grid

    calendarContainer.innerHTML = html;

    // Wire up prev/next buttons
    document.getElementById('cal-prev').addEventListener('click', function () {
      var newMonth = month - 1;
      var newYear = year;
      if (newMonth < 0) { newMonth = 11; newYear--; }
      renderCalendar(allEvents, calendarContainer, newYear, newMonth);
    });
    document.getElementById('cal-next').addEventListener('click', function () {
      var newMonth = month + 1;
      var newYear = year;
      if (newMonth > 11) { newMonth = 0; newYear++; }
      renderCalendar(allEvents, calendarContainer, newYear, newMonth);
    });
  }

  /* ---- Main events page init ---- */

  function initEventsPage() {
    var upcomingContainer = document.getElementById('events-list');
    var pastContainer     = document.getElementById('past-events-list');
    var calendarContainer = document.getElementById('calendar-grid');
    var listToggle        = document.getElementById('view-list');
    var calToggle         = document.getElementById('view-calendar');
    var pastToggle        = document.getElementById('past-events-toggle');

    if (!upcomingContainer) return;

    upcomingContainer.innerHTML = '<div class="events-loading">Loading events&hellip;</div>';

    fetch(EVENTS_URL)
      .then(function (r) {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.json();
      })
      .then(function (data) {
        var allEvents = (data.events || []).slice()
          .sort(function (a, b) { return parseDate(a.date) - parseDate(b.date); });

        var now = today();
        var upcoming = allEvents.filter(function (e) {
          return parseDate(e.date) >= now && e.status !== 'cancelled';
        });
        // Include cancelled events that are upcoming so they are visible
        var upcomingAll = allEvents.filter(function (e) {
          return parseDate(e.date) >= now;
        });
        var past = allEvents.filter(function (e) {
          return parseDate(e.date) < now;
        }).reverse();  // most recent first

        // Render list view
        renderListView(upcomingAll, pastContainer, upcomingContainer);

        // Render past events
        if (pastContainer) {
          if (past.length) {
            pastContainer.innerHTML = past.map(renderEventCard).join('');
          } else {
            pastContainer.innerHTML = '<p style="color:#626567;padding:1rem 0;">No past events to show.</p>';
          }
        }

        // Set up calendar view
        if (calendarContainer) {
          var now2 = new Date();
          renderCalendar(allEvents, calendarContainer, now2.getFullYear(), now2.getMonth());
        }

        // View toggle buttons
        if (listToggle && calToggle && calendarContainer) {
          listToggle.classList.add('active');

          listToggle.addEventListener('click', function () {
            listToggle.classList.add('active');
            calToggle.classList.remove('active');
            upcomingContainer.style.display = '';
            calendarContainer.style.display = 'none';
          });

          calToggle.addEventListener('click', function () {
            calToggle.classList.add('active');
            listToggle.classList.remove('active');
            upcomingContainer.style.display = 'none';
            calendarContainer.style.display = 'block';
          });
        }

        // Past events toggle
        if (pastToggle && pastContainer) {
          pastToggle.addEventListener('click', function () {
            var open = pastContainer.classList.toggle('open');
            pastToggle.textContent = open
              ? '▲ Hide past events'
              : '▼ Show past events (' + past.length + ')';
          });
          pastToggle.textContent = '▼ Show past events (' + past.length + ')';
        }
      })
      .catch(function (err) {
        console.error('[events.js] Failed to load events:', err);
        upcomingContainer.innerHTML =
          '<div class="events-empty">'
          + '<p>Unable to load events at this time.</p>'
          + '<p>Please try again later or <a href="/contact.html">contact us</a>.</p>'
          + '</div>';
      });
  }

  /* ---- Home page news preview init ---- */

  function initNewsPreview() {
    var container = document.getElementById('news-preview');
    if (!container) return;

    fetch(EVENTS_URL)
      .then(function (r) { return r.json(); })
      .then(function (data) {
        var allEvents = (data.events || []).slice()
          .sort(function (a, b) { return parseDate(a.date) - parseDate(b.date); });

        var now = today();
        var upcoming = allEvents
          .filter(function (e) { return parseDate(e.date) >= now && e.status !== 'cancelled'; })
          .slice(0, 3);  // show up to 3

        if (!upcoming.length) {
          container.innerHTML = '<p style="color:#626567;grid-column:1/-1;">No upcoming events at this time.</p>';
          return;
        }

        container.innerHTML = upcoming.map(renderPreviewCard).join('');
      })
      .catch(function () {
        // Home page — fail silently, events preview is non-critical
        var section = container.closest('.section');
        if (section) section.style.display = 'none';
      });
  }

  /* ---- Entry point ---- */

  document.addEventListener('DOMContentLoaded', function () {
    initEventsPage();
    initNewsPreview();
  });

})();
