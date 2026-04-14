# Managing Events

Events on the website are driven by a single JSON file: `data/events.json`.  
You can manage events two ways: using the **Python Admin GUI** (recommended) or by **editing the JSON file directly**.

---

## Method 1: Using the Admin GUI (Recommended)

The admin tool is a desktop application that requires no technical knowledge.

### How to Launch

1. Make sure Python 3 is installed on your computer
   - Check by running: `python3 --version` in a terminal
   - Download from: https://www.python.org/downloads/ if needed
2. Open a terminal
3. Navigate to the project folder:
   ```
   cd /path/to/ekwendeni_mission_hospital_website
   ```
4. Run the tool:
   ```
   python3 tools/admin_gui.py
   ```
5. The GUI window will open

### Adding a New Event

1. Click the **"Events Manager"** tab
2. Click **"+ New"** button
3. Fill in the form:
   - **Title*** — Name of the event (required)
   - **Date*** — Date in YYYY-MM-DD format, e.g., `2026-06-15` (required)
   - **Time** — Start time in 24-hour format, e.g., `09:00` (optional)
   - **End Date** — For multi-day events, the last date (optional)
   - **Category** — Choose from the dropdown (community-health, training, outreach, fundraising, general)
   - **Status** — Usually `upcoming` for new events
   - **Location** — Where the event takes place (optional)
   - **Contact** — Email or phone for enquiries (optional)
   - **Description*** — A clear description of the event (required)
   - **Image** — Click "Browse…" to select a photo. The tool copies it automatically.
   - **Image alt text** — A brief description of the photo (for accessibility)
4. Click **"💾 Save Event"**
5. The event appears immediately on the website

### Editing an Event

1. Click on an event in the list (left panel)
2. The form on the right fills with the event's current details
3. Make your changes
4. Click **"💾 Save Event"**

### Deleting an Event

1. Click on an event in the list
2. Click **"✕ Delete"**
3. Confirm the deletion in the dialog box

### Managing Photos

1. Click the **"Photo Manager"** tab
2. Select a folder from the left panel (e.g., `services`, `events`)
3. To add images: click **"+ Add Images…"** and select files from your computer
4. To delete images: select file(s) in the list, then click **"✕ Delete Selected"**
5. To create a new folder: click **"+ New Folder"** and enter a name

---

## Method 2: Editing events.json Directly

For those comfortable editing JSON, you can edit `data/events.json` directly with a text editor.

### JSON File Format

```json
{
  "version": "1.0",
  "last_updated": "2026-04-14",
  "events": [
    {
      "id": "evt-001",
      "title": "Free Blood Pressure Screening",
      "date": "2026-05-10",
      "time": "08:00",
      "end_date": null,
      "category": "community-health",
      "description": "Free blood pressure checks for all community members.",
      "image": "assets/images/events/screening.jpg",
      "image_alt": "Nurse conducting blood pressure screening",
      "location": "OPD Entrance, Ekwendeni Mission Hospital",
      "contact": "outreach@ekwendenihospital.mw",
      "is_recurring": false,
      "status": "upcoming"
    }
  ]
}
```

### Field Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique ID, format `evt-NNN`. Don't duplicate. |
| `title` | string | Yes | Event name |
| `date` | string | Yes | Date in `YYYY-MM-DD` format |
| `time` | string or null | No | Time in `HH:MM` 24-hour format, or `null` |
| `end_date` | string or null | No | Last date for multi-day events, or `null` |
| `category` | string | Yes | One of: `community-health`, `training`, `outreach`, `fundraising`, `general` |
| `description` | string | Yes | Plain text description (no HTML tags) |
| `image` | string | No | Path from site root, e.g., `assets/images/events/photo.jpg` |
| `image_alt` | string | No | Accessibility description of the photo |
| `location` | string | No | Where the event takes place |
| `contact` | string | No | Contact email or phone |
| `is_recurring` | boolean | No | `true` or `false` |
| `status` | string | Yes | One of: `upcoming`, `ongoing`, `past`, `cancelled` |

### Adding an Event Manually

1. Open `data/events.json` in a text editor
2. Copy an existing event block (from `{` to `}`)
3. Paste it after the last event (before the closing `]`)
4. Add a comma after the previous event's closing `}`
5. Update all the fields
6. Make sure the `id` is unique (increment the number)
7. Update `last_updated` at the top of the file

### Changing Event Status

When an event passes, change its `status` to `"past"`:
```json
"status": "past"
```

Events with a past date are automatically moved to the "Past Events" section on the website, regardless of their status value.

---

## How Events Appear on the Website

- **Upcoming events**: Sorted chronologically on `events.html` and as a preview on the home page
- **Past events**: Collapsed under a "Show past events" toggle on `events.html`
- **Cancelled events**: Shown with a [CANCELLED] badge but still listed
- **Home page preview**: Shows up to 3 upcoming events automatically

The events page also has a calendar view showing which dates have events. Click the month navigation arrows to move between months.

---

## After Making Changes

After updating events (by any method), refresh the site in your browser to see the changes. If testing locally, the server must be running:

```
python3 -m http.server 8080
```

Then visit: http://localhost:8080/events.html
