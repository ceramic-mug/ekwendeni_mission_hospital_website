# Ekwendeni Mission Hospital Website

Website for Ekwendeni Mission Hospital, Ekwendeni, Mzimba District, Malawi.

**Hosted on:** GitHub Pages  
**Domain via:** Cloudflare  
**Technology:** Plain HTML, CSS, JavaScript — no build tools required

---

## Quick Start: Preview the Site Locally

```bash
# From the project root folder:
python3 -m http.server 8080
```

Then open: **http://localhost:8080**

> Note: Opening HTML files directly (double-clicking) will NOT work because the shared navigation uses JavaScript fetch(). Always use the local server above.

---

## Project Structure

```
ekwendeni_mission_hospital_website/
│
├── index.html          Home page
├── about.html          About Us (history, mission, vision, stats, location)
├── services.html       Services (wards, OPD, maternal, under-5)
├── events.html         Events (auto-loaded from data/events.json)
├── donate.html         Donate
├── contact.html        Contact Us
├── CNAME               Custom domain for GitHub Pages
│
├── assets/
│   ├── css/main.css    Complete site stylesheet (all styles in one file)
│   ├── js/
│   │   ├── nav.js      Loads shared nav/footer, handles mobile menu
│   │   └── events.js   Renders events from JSON (list + calendar views)
│   └── images/
│       ├── services/   Service photos
│       └── events/     Event photos (managed by admin tool)
│
├── data/
│   └── events.json     Event data — edit via admin GUI or directly
│
├── fragments/
│   ├── nav.html        Shared site navigation (edit once → updates all pages)
│   └── footer.html     Shared site footer
│
├── tools/
│   └── admin_gui.py    Desktop tool to manage events and photos (Python 3)
│
└── docs/
    ├── UPDATING_CONTENT.md   How to edit page content
    ├── MANAGING_EVENTS.md    How to manage events
    ├── GITHUB_PAGES.md       How to deploy
    └── CLOUDFLARE_DOMAIN.md  How to set up the custom domain
```

---

## Managing Events

Use the admin tool:

```bash
python3 tools/admin_gui.py
```

Or edit `data/events.json` directly. See [docs/MANAGING_EVENTS.md](docs/MANAGING_EVENTS.md).

---

## Updating Content

- **All pages** have clearly marked `<!-- SECTION: ... -->` and `<!-- TODO: ... -->` comments
- **Navigation and footer**: edit `fragments/nav.html` or `fragments/footer.html` — changes propagate to all pages
- **Styles**: all in `assets/css/main.css`, section-commented for easy navigation
- Full guide: [docs/UPDATING_CONTENT.md](docs/UPDATING_CONTENT.md)

---

## Deploying Changes

```bash
git add .
git commit -m "Brief description of changes"
git push
```

Site updates within 30–60 seconds. Full guide: [docs/GITHUB_PAGES.md](docs/GITHUB_PAGES.md)

---

## Placeholder Content

All text and statistics marked `<!-- TODO: ... -->` or styled with `.placeholder-text` are awaiting confirmation from hospital administration. Search for `TODO` in any HTML file to find items needing real content.

---

## Technical Notes

- **No build step** — all files are plain HTML/CSS/JS, editable in any text editor
- **System fonts only** — avoids CDN dependencies and loads faster on low-bandwidth connections
- **Map**: OpenStreetMap `<iframe>` embed — free, no API key
- **Contact form**: Formspree (free tier) — update `YOUR_FORM_ID` in `contact.html`
- **Absolute URL paths** (`/assets/css/main.css`) — require a custom domain (see CLOUDFLARE_DOMAIN.md)
