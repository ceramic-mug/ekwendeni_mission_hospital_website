#!/usr/bin/env python3
"""
Ekwendeni Mission Hospital — Admin GUI
=======================================
A local desktop tool for managing website content without touching code.

WHAT IT DOES:
  - Events Manager: Add, edit, and delete events that appear on the website.
                    Changes are saved to data/events.json automatically.
  - Photo Manager:  Browse, add, and delete photos in the assets/images/ folder.

HOW TO RUN:
  Open a terminal, navigate to the project folder, then run:
    python3 tools/admin_gui.py

REQUIREMENTS:
  Python 3.6 or later. No additional packages needed.
  tkinter is included with standard Python on Windows and macOS.
  On Ubuntu/Debian Linux, install it with: sudo apt-get install python3-tk

NOTE:
  After making changes, the website must be served over HTTP to see them.
  Run: python3 -m http.server 8080  (from the project root)
  Then visit: http://localhost:8080
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import shutil
import uuid
from datetime import date, datetime

# ── Path resolution ─────────────────────────────────────────────────────────
# All paths are derived from this script's location so the tool works
# regardless of where the repository is cloned.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SITE_ROOT  = os.path.dirname(SCRIPT_DIR)
EVENTS_JSON  = os.path.join(SITE_ROOT, 'data', 'events.json')
IMAGES_ROOT  = os.path.join(SITE_ROOT, 'assets', 'images')
EVENTS_IMAGES = os.path.join(IMAGES_ROOT, 'events')

CATEGORIES = ['community-health', 'training', 'outreach', 'fundraising', 'general']
STATUSES   = ['upcoming', 'ongoing', 'past', 'cancelled']
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.webp')


# ── Event data helpers ───────────────────────────────────────────────────────

def load_events():
    """Load events.json and return the full data dict."""
    if not os.path.exists(EVENTS_JSON):
        return {"version": "1.0", "last_updated": str(date.today()), "events": []}
    with open(EVENTS_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_events(data):
    """Write events data back to events.json."""
    data['last_updated'] = str(date.today())
    os.makedirs(os.path.dirname(EVENTS_JSON), exist_ok=True)
    with open(EVENTS_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def new_event_id(events):
    """Generate the next sequential event ID."""
    existing = [e.get('id', '') for e in events]
    nums = []
    for eid in existing:
        if eid.startswith('evt-'):
            try:
                nums.append(int(eid[4:]))
            except ValueError:
                pass
    next_num = max(nums, default=0) + 1
    return 'evt-{:03d}'.format(next_num)


def copy_image_to_events(source_path):
    """
    Copy an image file into assets/images/events/ and return the
    relative web path (suitable for storing in events.json).
    Returns None if no source_path given.
    """
    if not source_path:
        return None
    ext = os.path.splitext(source_path)[1].lower()
    dest_filename = 'event-' + str(uuid.uuid4())[:8] + ext
    os.makedirs(EVENTS_IMAGES, exist_ok=True)
    dest_path = os.path.join(EVENTS_IMAGES, dest_filename)
    shutil.copy2(source_path, dest_path)
    # Return a path relative to site root (for use in HTML/JSON)
    return 'assets/images/events/' + dest_filename


# ── Main Application ─────────────────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Ekwendeni Mission Hospital — Admin Tool')
        self.geometry('980x680')
        self.minsize(800, 500)
        self.configure(bg='#f4f6f7')

        # Style
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TNotebook', background='#f4f6f7')
        style.configure('TNotebook.Tab', padding=[12, 6], font=('Helvetica', 11))
        style.configure('TButton', padding=[8, 4])
        style.configure('Header.TLabel', font=('Helvetica', 13, 'bold'), background='#1a5276', foreground='white', padding=10)
        style.configure('Status.TLabel', font=('Helvetica', 9), background='#e8e8e8', foreground='#555')

        # Header
        header = ttk.Label(self, text='  Ekwendeni Mission Hospital — Website Admin Tool',
                           style='Header.TLabel')
        header.pack(fill='x', side='top')

        # Notebook (tabs)
        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self.events_tab = EventsTab(notebook)
        self.photos_tab = PhotosTab(notebook)

        notebook.add(self.events_tab, text='📅  Events Manager')
        notebook.add(self.photos_tab, text='🖼️  Photo Manager')

        # Status bar
        self.status_var = tk.StringVar(value='Ready')
        status_bar = ttk.Label(self, textvariable=self.status_var, style='Status.TLabel', anchor='w')
        status_bar.pack(fill='x', side='bottom')

        # Let child tabs update status
        self.events_tab.app = self
        self.photos_tab.app = self

    def set_status(self, msg):
        self.status_var.set('  ' + msg + '  |  ' + datetime.now().strftime('%H:%M:%S'))


# ── Events Tab ───────────────────────────────────────────────────────────────

class EventsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.app = None          # set by App after init
        self._selected_id = None
        self._image_path = None  # temp path for new image selection
        self._build()
        self._load()

    def _build(self):
        # Left panel: event list
        left = ttk.Frame(self, width=300)
        left.pack(side='left', fill='y', padx=(0, 5), pady=5)
        left.pack_propagate(False)

        ttk.Label(left, text='Events', font=('Helvetica', 11, 'bold')).pack(anchor='w', padx=5, pady=(5, 2))

        list_frame = ttk.Frame(left)
        list_frame.pack(fill='both', expand=True, padx=5)

        scrollbar = ttk.Scrollbar(list_frame, orient='vertical')
        self.listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                   font=('Helvetica', 10), selectbackground='#1a5276',
                                   selectforeground='white', activestyle='none',
                                   relief='flat', bd=1)
        scrollbar.config(command=self.listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.listbox.pack(fill='both', expand=True)
        self.listbox.bind('<<ListboxSelect>>', self._on_select)

        btn_row = ttk.Frame(left)
        btn_row.pack(fill='x', padx=5, pady=5)
        ttk.Button(btn_row, text='+ New', command=self._new_event).pack(side='left', padx=(0, 3))
        ttk.Button(btn_row, text='✎ Edit', command=self._edit_selected).pack(side='left', padx=3)
        ttk.Button(btn_row, text='✕ Delete', command=self._delete_selected).pack(side='left', padx=3)

        # Right panel: event edit form
        right_outer = ttk.Frame(self)
        right_outer.pack(side='left', fill='both', expand=True, pady=5)

        canvas = tk.Canvas(right_outer, bg='#f4f6f7', highlightthickness=0)
        scrollbar2 = ttk.Scrollbar(right_outer, orient='vertical', command=canvas.yview)
        self.form_frame = ttk.Frame(canvas)
        self.form_frame.bind('<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all')))

        canvas.create_window((0, 0), window=self.form_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar2.set)
        scrollbar2.pack(side='right', fill='y')
        canvas.pack(fill='both', expand=True)

        # Bind mouse wheel scroll
        canvas.bind_all('<MouseWheel>', lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), 'units'))

        self._build_form(self.form_frame)

    def _build_form(self, parent):
        """Build the event editing form fields."""
        pad = {'padx': 10, 'pady': 3}
        self.fields = {}

        def row(label, key, widget_type='entry', **kwargs):
            ttk.Label(parent, text=label + ':', font=('Helvetica', 10)).pack(anchor='w', **pad)
            if widget_type == 'entry':
                var = tk.StringVar()
                w = ttk.Entry(parent, textvariable=var, font=('Helvetica', 10), **kwargs)
                w.pack(fill='x', **pad)
                self.fields[key] = var
            elif widget_type == 'text':
                w = tk.Text(parent, font=('Helvetica', 10), height=kwargs.get('height', 4),
                            wrap='word', relief='solid', bd=1)
                w.pack(fill='x', **pad)
                self.fields[key] = w
            elif widget_type == 'combo':
                var = tk.StringVar()
                w = ttk.Combobox(parent, textvariable=var, font=('Helvetica', 10),
                                  values=kwargs.get('values', []), state='readonly')
                w.pack(fill='x', **pad)
                self.fields[key] = var

        ttk.Label(parent, text='Edit Event', font=('Helvetica', 12, 'bold')).pack(anchor='w', padx=10, pady=(10, 5))

        row('Title *', 'title')
        row('Date * (YYYY-MM-DD)', 'date')
        row('Time (HH:MM, 24h, optional)', 'time')
        row('End Date (YYYY-MM-DD, optional)', 'end_date')
        row('Category', 'category', 'combo', values=CATEGORIES)
        row('Status', 'status', 'combo', values=STATUSES)
        row('Location (optional)', 'location')
        row('Contact email/phone (optional)', 'contact')
        row('Description *', 'description', 'text', height=5)

        # Image field with Browse button
        ttk.Label(parent, text='Image (optional):', font=('Helvetica', 10)).pack(anchor='w', **pad)
        img_frame = ttk.Frame(parent)
        img_frame.pack(fill='x', padx=10, pady=3)
        self.fields['image'] = tk.StringVar()
        ttk.Entry(img_frame, textvariable=self.fields['image'], font=('Helvetica', 10),
                  state='readonly').pack(side='left', fill='x', expand=True, padx=(0, 5))
        ttk.Button(img_frame, text='Browse…', command=self._browse_image).pack(side='left')
        ttk.Button(img_frame, text='Clear', command=self._clear_image).pack(side='left', padx=(3, 0))

        row('Image alt text (for accessibility)', 'image_alt')

        # Recurring checkbox
        self.recurring_var = tk.BooleanVar()
        ttk.Checkbutton(parent, text='Recurring event', variable=self.recurring_var).pack(anchor='w', padx=10, pady=3)

        # Save/Cancel buttons
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill='x', padx=10, pady=10)
        ttk.Button(btn_frame, text='💾  Save Event', command=self._save_event).pack(side='left', padx=(0, 5))
        ttk.Button(btn_frame, text='✕  Clear Form', command=self._clear_form).pack(side='left')

        self._clear_form()

    # ── List management ──

    def _load(self):
        """Load events from JSON and populate the listbox."""
        data = load_events()
        self._events = data.get('events', [])
        self._events.sort(key=lambda e: e.get('date', ''))
        self.listbox.delete(0, 'end')
        for ev in self._events:
            label = '{} — {}'.format(ev.get('date', '?'), ev.get('title', '(no title)'))
            self.listbox.insert('end', label)
        self._selected_id = None

    def _on_select(self, event):
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        ev = self._events[idx]
        self._selected_id = ev.get('id')
        self._populate_form(ev)

    # ── Form actions ──

    def _new_event(self):
        self._selected_id = None
        self._clear_form()
        self.fields['status'].set('upcoming')
        self.fields['category'].set('general')

    def _edit_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo('Select an Event', 'Please click on an event in the list first.')
            return
        # Form is already populated by _on_select

    def _delete_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo('Select an Event', 'Please click on an event in the list first.')
            return
        idx = sel[0]
        ev = self._events[idx]
        confirm = messagebox.askyesno(
            'Delete Event',
            'Are you sure you want to delete:\n\n"{}"\n\nThis cannot be undone.'.format(ev.get('title', ''))
        )
        if confirm:
            data = load_events()
            data['events'] = [e for e in data['events'] if e.get('id') != ev.get('id')]
            save_events(data)
            self._load()
            self._clear_form()
            if self.app:
                self.app.set_status('Event deleted: {}'.format(ev.get('title', '')))

    def _populate_form(self, ev):
        """Fill form fields with an existing event's data."""
        self.fields['title'].set(ev.get('title', ''))
        self.fields['date'].set(ev.get('date', ''))
        self.fields['time'].set(ev.get('time', ''))
        self.fields['end_date'].set(ev.get('end_date', '') or '')
        self.fields['category'].set(ev.get('category', 'general'))
        self.fields['status'].set(ev.get('status', 'upcoming'))
        self.fields['location'].set(ev.get('location', ''))
        self.fields['contact'].set(ev.get('contact', ''))
        self.fields['image'].set(ev.get('image', ''))
        self.fields['image_alt'].set(ev.get('image_alt', ''))
        self.recurring_var.set(ev.get('is_recurring', False))

        desc_widget = self.fields['description']
        desc_widget.delete('1.0', 'end')
        desc_widget.insert('1.0', ev.get('description', ''))

        self._image_path = None  # reset pending image

    def _clear_form(self):
        """Reset all form fields to blank."""
        for key, var in self.fields.items():
            if isinstance(var, tk.Text):
                var.delete('1.0', 'end')
            else:
                var.set('')
        self.recurring_var.set(False)
        self._image_path = None
        self._selected_id = None

    def _browse_image(self):
        path = filedialog.askopenfilename(
            title='Select image for event',
            filetypes=[('Image files', '*.jpg *.jpeg *.png *.gif *.webp'), ('All files', '*.*')]
        )
        if path:
            self._image_path = path
            # Show the filename (not the full path) as a preview
            self.fields['image'].set('(new image: {})'.format(os.path.basename(path)))

    def _clear_image(self):
        self._image_path = None
        self.fields['image'].set('')

    def _save_event(self):
        """Validate and save the event to events.json."""
        title = self.fields['title'].get().strip()
        date_str = self.fields['date'].get().strip()
        description = self.fields['description'].get('1.0', 'end').strip()

        # Basic validation
        if not title:
            messagebox.showerror('Missing Field', 'Please enter a title for the event.')
            return
        if not date_str:
            messagebox.showerror('Missing Field', 'Please enter a date (YYYY-MM-DD).')
            return
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror('Invalid Date', 'Date must be in YYYY-MM-DD format (e.g. 2026-06-15).')
            return
        if not description:
            messagebox.showerror('Missing Field', 'Please enter a description.')
            return

        # Handle image copy
        image_value = self.fields['image'].get().strip()
        if self._image_path:
            # A new image was selected — copy it to assets/images/events/
            try:
                image_value = copy_image_to_events(self._image_path)
                self._image_path = None
            except Exception as e:
                messagebox.showerror('Image Error', 'Could not copy image: {}'.format(str(e)))
                return

        # Build event dict
        end_date_raw = self.fields['end_date'].get().strip() or None
        event_dict = {
            'title': title,
            'date': date_str,
            'time': self.fields['time'].get().strip() or None,
            'end_date': end_date_raw,
            'category': self.fields['category'].get() or 'general',
            'description': description,
            'image': image_value if not image_value.startswith('(new image:') else '',
            'image_alt': self.fields['image_alt'].get().strip(),
            'location': self.fields['location'].get().strip(),
            'contact': self.fields['contact'].get().strip(),
            'is_recurring': self.recurring_var.get(),
            'status': self.fields['status'].get() or 'upcoming',
        }

        data = load_events()

        if self._selected_id:
            # Update existing event
            for i, ev in enumerate(data['events']):
                if ev.get('id') == self._selected_id:
                    event_dict['id'] = self._selected_id
                    data['events'][i] = event_dict
                    break
        else:
            # New event
            event_dict['id'] = new_event_id(data['events'])
            data['events'].append(event_dict)

        save_events(data)
        self._load()
        self._clear_form()

        if self.app:
            self.app.set_status('Event saved: {}'.format(title))
        messagebox.showinfo('Saved', 'Event "{}" saved successfully.'.format(title))


# ── Photos Tab ───────────────────────────────────────────────────────────────

class PhotosTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.app = None
        self._current_folder = None
        self._build()
        self._load_folders()

    def _build(self):
        # Left panel: folder list
        left = ttk.Frame(self, width=220)
        left.pack(side='left', fill='y', padx=(0, 5), pady=5)
        left.pack_propagate(False)

        ttk.Label(left, text='Image Folders', font=('Helvetica', 11, 'bold')).pack(anchor='w', padx=5, pady=(5, 2))

        self.folder_listbox = tk.Listbox(left, font=('Helvetica', 10),
                                          selectbackground='#1a5276', selectforeground='white',
                                          activestyle='none', relief='flat', bd=1)
        self.folder_listbox.pack(fill='both', expand=True, padx=5)
        self.folder_listbox.bind('<<ListboxSelect>>', self._on_folder_select)

        folder_btns = ttk.Frame(left)
        folder_btns.pack(fill='x', padx=5, pady=5)
        ttk.Button(folder_btns, text='+ New Folder', command=self._new_folder).pack(fill='x', pady=2)
        ttk.Button(folder_btns, text='↻ Refresh', command=self._load_folders).pack(fill='x', pady=2)

        # Right panel: file list in selected folder
        right = ttk.Frame(self)
        right.pack(side='left', fill='both', expand=True, pady=5)

        self.folder_label = ttk.Label(right, text='Select a folder', font=('Helvetica', 11, 'bold'))
        self.folder_label.pack(anchor='w', padx=10, pady=(5, 2))

        self.file_listbox = tk.Listbox(right, font=('Helvetica', 10),
                                        selectbackground='#1a5276', selectforeground='white',
                                        activestyle='none', relief='flat', bd=1,
                                        selectmode='extended')
        scrollbar = ttk.Scrollbar(right, orient='vertical', command=self.file_listbox.yview)
        self.file_listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.file_listbox.pack(fill='both', expand=True, padx=10, pady=5)

        file_btns = ttk.Frame(right)
        file_btns.pack(fill='x', padx=10, pady=5)
        ttk.Button(file_btns, text='+ Add Images…', command=self._add_images).pack(side='left', padx=(0, 5))
        ttk.Button(file_btns, text='✕ Delete Selected', command=self._delete_images).pack(side='left')

        # Info label
        self.info_label = ttk.Label(right, text='', font=('Helvetica', 9), foreground='#626567')
        self.info_label.pack(anchor='w', padx=10, pady=(0, 5))

    # ── Folder management ──

    def _load_folders(self):
        self.folder_listbox.delete(0, 'end')
        if not os.path.exists(IMAGES_ROOT):
            return
        folders = sorted([
            d for d in os.listdir(IMAGES_ROOT)
            if os.path.isdir(os.path.join(IMAGES_ROOT, d))
        ])
        for folder in folders:
            self.folder_listbox.insert('end', folder)

    def _on_folder_select(self, event):
        sel = self.folder_listbox.curselection()
        if not sel:
            return
        self._current_folder = self.folder_listbox.get(sel[0])
        self._load_files()

    def _load_files(self):
        if not self._current_folder:
            return
        folder_path = os.path.join(IMAGES_ROOT, self._current_folder)
        self.folder_label.config(text='Folder: ' + self._current_folder)
        self.file_listbox.delete(0, 'end')
        if not os.path.exists(folder_path):
            return
        files = sorted([
            f for f in os.listdir(folder_path)
            if f.lower().endswith(IMAGE_EXTENSIONS)
        ])
        for fname in files:
            self.file_listbox.insert('end', fname)
        self.info_label.config(text='{} image(s) in this folder'.format(len(files)))

    def _new_folder(self):
        dialog = FolderNameDialog(self, 'New Folder')
        name = dialog.result
        if name:
            name = name.strip().replace(' ', '-').lower()
            new_path = os.path.join(IMAGES_ROOT, name)
            if os.path.exists(new_path):
                messagebox.showerror('Error', 'A folder named "{}" already exists.'.format(name))
                return
            os.makedirs(new_path, exist_ok=True)
            self._load_folders()
            if self.app:
                self.app.set_status('Created folder: ' + name)

    # ── File management ──

    def _add_images(self):
        if not self._current_folder:
            messagebox.showinfo('Select a Folder', 'Please select a folder from the list first.')
            return
        paths = filedialog.askopenfilenames(
            title='Select images to add',
            filetypes=[('Image files', '*.jpg *.jpeg *.png *.gif *.webp'), ('All files', '*.*')]
        )
        if not paths:
            return
        folder_path = os.path.join(IMAGES_ROOT, self._current_folder)
        copied = 0
        for src in paths:
            dest = os.path.join(folder_path, os.path.basename(src))
            if os.path.exists(dest):
                # Avoid overwriting — rename with a short unique suffix
                base, ext = os.path.splitext(os.path.basename(src))
                dest = os.path.join(folder_path, '{}-{}{}'.format(base, str(uuid.uuid4())[:6], ext))
            shutil.copy2(src, dest)
            copied += 1
        self._load_files()
        if self.app:
            self.app.set_status('{} image(s) added to {}'.format(copied, self._current_folder))
        messagebox.showinfo('Done', '{} image(s) added to "{}".'.format(copied, self._current_folder))

    def _delete_images(self):
        sel = self.file_listbox.curselection()
        if not sel:
            messagebox.showinfo('Select Images', 'Please select one or more images to delete.')
            return
        filenames = [self.file_listbox.get(i) for i in sel]
        confirm = messagebox.askyesno(
            'Delete Images',
            'Delete {} image(s)? This cannot be undone.\n\n{}'.format(
                len(filenames), '\n'.join(filenames[:10]) + ('…' if len(filenames) > 10 else '')
            )
        )
        if confirm:
            folder_path = os.path.join(IMAGES_ROOT, self._current_folder)
            for fname in filenames:
                try:
                    os.remove(os.path.join(folder_path, fname))
                except OSError as e:
                    messagebox.showerror('Error', 'Could not delete {}: {}'.format(fname, str(e)))
            self._load_files()
            if self.app:
                self.app.set_status('{} image(s) deleted from {}'.format(len(filenames), self._current_folder))


# ── Small dialog for folder names ────────────────────────────────────────────

class FolderNameDialog(tk.Toplevel):
    def __init__(self, parent, title):
        super().__init__(parent)
        self.title(title)
        self.geometry('340x130')
        self.resizable(False, False)
        self.result = None

        ttk.Label(self, text='Folder name (lowercase, no spaces):').pack(padx=20, pady=(20, 5))
        self._var = tk.StringVar()
        entry = ttk.Entry(self, textvariable=self._var, width=30)
        entry.pack(padx=20)
        entry.focus()

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text='Create', command=self._ok).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='Cancel', command=self.destroy).pack(side='left', padx=5)

        entry.bind('<Return>', lambda e: self._ok())
        self.grab_set()
        self.wait_window()

    def _ok(self):
        self.result = self._var.get()
        self.destroy()


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == '__main__':
    # Sanity check: warn if the site root doesn't look right
    if not os.path.exists(os.path.join(SITE_ROOT, 'index.html')):
        print('WARNING: Could not find index.html in expected location: {}'.format(SITE_ROOT))
        print('Make sure you run this script from within the project folder.')
        print('Expected project root: {}'.format(SITE_ROOT))

    app = App()
    app.mainloop()
