# Updating Website Content

This guide explains how to update the text, images, and information on the Ekwendeni Mission Hospital website.

---

## Before You Start: View the Site Locally

Because the site uses shared navigation (loaded via JavaScript), you **cannot** simply double-click an HTML file in Windows/Mac Finder to preview it. You need a simple local server.

**To preview the site on your computer:**

1. Open a terminal (macOS: `Terminal`; Windows: `Command Prompt` or `PowerShell`)
2. Navigate to the project folder:
   ```
   cd /path/to/ekwendeni_mission_hospital_website
   ```
3. Start the local server:
   ```
   python3 -m http.server 8080
   ```
4. Open your browser and go to: `http://localhost:8080`
5. When done, press `Ctrl+C` in the terminal to stop the server.

---

## File Structure at a Glance

```
ekwendeni_mission_hospital_website/
├── index.html          ← Home page
├── about.html          ← About Us page
├── services.html       ← Services page
├── events.html         ← Events page (auto-populated from data/events.json)
├── donate.html         ← Donate page
├── contact.html        ← Contact Us page
│
├── assets/
│   ├── css/main.css    ← ALL styles for the whole site
│   └── images/         ← All photos and images
│       ├── services/   ← Service photos (wards, OPD, etc.)
│       └── events/     ← Event photos (managed by admin GUI)
│
├── data/
│   └── events.json     ← Event data (managed by admin GUI or edited directly)
│
├── fragments/
│   ├── nav.html        ← Shared navigation menu (edit ONCE, updates all pages)
│   └── footer.html     ← Shared footer (edit ONCE, updates all pages)
│
└── tools/
    └── admin_gui.py    ← Python desktop tool for managing events and photos
```

---

## How to Update Text on a Page

1. Open the `.html` file for the page you want to update (e.g., `about.html`)
2. Use a text editor (e.g., Notepad, TextEdit, VS Code)
3. Look for the `<!-- SECTION: ... -->` comments — these mark where each content block starts
4. Look for `<!-- TODO: ... -->` comments — these mark placeholder text that needs to be replaced
5. Edit the text between the HTML tags. For example:

   **Before (placeholder):**
   ```html
   <!-- TODO: Replace with the hospital's official mission statement -->
   <p class="placeholder-text">
     "Our mission is to provide holistic, quality healthcare..." — [Hospital Administration]
   </p>
   ```

   **After (real content):**
   ```html
   <p>
     "Our mission is to provide compassionate, quality healthcare to all people of Ekwendeni."
   </p>
   ```

6. Save the file
7. Refresh the page in your browser to see the change

---

## How to Update the Navigation Menu

The navigation appears on every page. To update it, edit **only** `fragments/nav.html`.

- To change a link name: find the `<a>` tag and change its text
- To add a new page:
  1. Add a new `<li><a href="/newpage.html">Page Name</a></li>` in `fragments/nav.html`
  2. Create the new `newpage.html` file (copy an existing page as a template)
- To change the logo: replace the `<svg>` placeholder with an `<img>` tag pointing to your logo file

---

## How to Update the Footer

Edit `fragments/footer.html`. Changes will appear on all pages automatically.

Key things to update in the footer:
- Hospital address
- Phone numbers
- Email addresses
- Emergency phone number

---

## How to Replace Placeholder Images

Each image placeholder looks like this in the HTML:

```html
<!-- TODO: Replace with actual photo -->
<div class="img-placeholder" style="height:360px;border-radius:8px;">
  <span>Photo: Inpatient ward</span>
</div>
```

To replace it with a real photo:
1. Copy your image file to `assets/images/services/` (for service photos)
2. In the HTML, remove the `<div class="img-placeholder">` block
3. Replace it with an `<img>` tag:
   ```html
   <img src="/assets/images/services/wards.jpg"
        alt="Inpatient ward at Ekwendeni Mission Hospital"
        style="width:100%;height:360px;object-fit:cover;border-radius:8px;">
   ```
4. The `alt` attribute text is important for accessibility — describe what is in the photo

**Image tips:**
- Use `.jpg` for photos (smaller file size, faster loading)
- Use `.png` for logos or graphics with transparency
- Recommended photo dimensions: at least 800×600 pixels
- Keep file sizes under 500KB when possible (use a tool like squoosh.app to compress)

---

## How to Update Key Statistics

On `index.html` and `about.html`, the statistics blocks use placeholders like `[~350]`.

Find the stat boxes section and update the numbers:

```html
<!-- Before -->
<span class="stat-number">[~350]</span>

<!-- After -->
<span class="stat-number">350</span>
```

---

## How to Update the Contact Form

The contact form uses a free service called **Formspree** to deliver form submissions to an email inbox.

To set it up:
1. Go to [formspree.io](https://formspree.io) and create a free account
2. Create a new form and copy your form ID (looks like `xpwzabcd`)
3. In `contact.html`, find this line:
   ```html
   action="https://formspree.io/f/YOUR_FORM_ID"
   ```
4. Replace `YOUR_FORM_ID` with your actual form ID:
   ```html
   action="https://formspree.io/f/xpwzabcd"
   ```

The free tier allows 50 form submissions per month.

---

## How to Change Colours or Fonts

All site styles are in `assets/css/main.css`. The colours and fonts are defined at the top of the file in the `/* 1. CSS VARIABLES */` section:

```css
:root {
  --color-primary: #1a5276;   /* Main blue colour */
  --color-accent:  #1e8449;   /* Green accent colour */
  ...
}
```

Change any hex colour value (e.g., `#1a5276`) to update it across the entire site.

---

## Tips for Editing HTML Files

- Always save the file before refreshing the browser
- If something looks broken, press `Ctrl+Z` (Undo) to revert your last change
- The browser's Developer Tools (`F12` key) can help diagnose display issues
- To search for a specific piece of text in a large HTML file, use `Ctrl+F` in your text editor
