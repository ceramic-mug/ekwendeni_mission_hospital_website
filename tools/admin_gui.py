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

  Or double-click: tools/launch_admin.command  (macOS only)

REQUIREMENTS:
  Python 3.6 or later. No additional packages needed.
  tkinter is included with standard Python on Windows and macOS.
  On Ubuntu/Debian Linux, install it with: sudo apt-get install python3-tk
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import shutil
import uuid
import calendar
from datetime import date, datetime

# ── Path resolution ─────────────────────────────────────────────────────────
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
SITE_ROOT    = os.path.dirname(SCRIPT_DIR)
EVENTS_JSON  = os.path.join(SITE_ROOT, 'data', 'events.json')
IMAGES_ROOT  = os.path.join(SITE_ROOT, 'assets', 'images')
EVENTS_IMAGES = os.path.join(IMAGES_ROOT, 'events')

CATEGORIES = ['community-health', 'training', 'outreach', 'fundraising', 'general']
STATUSES   = ['upcoming', 'ongoing', 'past', 'cancelled']
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.webp')


# ── Event data helpers ───────────────────────────────────────────────────────

def load_events():
    if not os.path.exists(EVENTS_JSON):
        return {"version": "1.0", "last_updated": str(date.today()), "events": []}
    with open(EVENTS_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_events(data):
    data['last_updated'] = str(date.today())
    os.makedirs(os.path.dirname(EVENTS_JSON), exist_ok=True)
    with open(EVENTS_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def new_event_id(events):
    existing = [e.get('id', '') for e in events]
    nums = []
    for eid in existing:
        if eid.startswith('evt-'):
            try:
                nums.append(int(eid[4:]))
            except ValueError:
                pass
    return 'evt-{:03d}'.format(max(nums, default=0) + 1)


def copy_image_to_events(source_path):
    if not source_path:
        return None
    ext = os.path.splitext(source_path)[1].lower()
    dest_filename = 'event-' + str(uuid.uuid4())[:8] + ext
    os.makedirs(EVENTS_IMAGES, exist_ok=True)
    dest_path = os.path.join(EVENTS_IMAGES, dest_filename)
    shutil.copy2(source_path, dest_path)
    return 'assets/images/events/' + dest_filename


def count_events_by_status(events):
    today = str(date.today())
    upcoming = sum(1 for e in events if e.get('date', '') >= today and e.get('status') != 'cancelled')
    past = sum(1 for e in events if e.get('date', '') < today or e.get('status') == 'past')
    return upcoming, past


# ── Calendar date-picker dialog ──────────────────────────────────────────────

class CalendarDialog(tk.Toplevel):
    """A simple month-grid date picker that requires no external packages."""

    def __init__(self, parent, initial_date_str=''):
        super().__init__(parent)
        self.title('Pick a Date')
        self.resizable(False, False)
        self.result = None

        try:
            d = datetime.strptime(initial_date_str, '%Y-%m-%d')
            self._year, self._month = d.year, d.month
        except (ValueError, TypeError):
            today = date.today()
            self._year, self._month = today.year, today.month

        self._build()
        self._render()

        # Centre over parent
        self.update_idletasks()
        px = parent.winfo_rootx() + parent.winfo_width() // 2 - self.winfo_width() // 2
        py = parent.winfo_rooty() + parent.winfo_height() // 2 - self.winfo_height() // 2
        self.geometry('+{}+{}'.format(px, py))

        self.grab_set()
        self.wait_window()

    def _build(self):
        # Header: prev / month-year label / next
        hdr = tk.Frame(self, bg='#1a5276', pady=6)
        hdr.pack(fill='x')
        tk.Button(hdr, text='◀', command=self._prev_month,
                  bg='#1a5276', fg='white', relief='flat',
                  font=('Helvetica', 12), cursor='hand2').pack(side='left', padx=8)
        self._hdr_label = tk.Label(hdr, text='', bg='#1a5276', fg='white',
                                    font=('Helvetica', 12, 'bold'), width=16)
        self._hdr_label.pack(side='left', expand=True)
        tk.Button(hdr, text='▶', command=self._next_month,
                  bg='#1a5276', fg='white', relief='flat',
                  font=('Helvetica', 12), cursor='hand2').pack(side='right', padx=8)

        # Day-of-week labels
        days_frame = tk.Frame(self, bg='#f4f6f7', pady=4)
        days_frame.pack(fill='x')
        for i, d in enumerate(['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']):
            tk.Label(days_frame, text=d, width=4, bg='#f4f6f7',
                     fg='#626567', font=('Helvetica', 9, 'bold')).grid(row=0, column=i, padx=2)

        # Grid of day buttons
        self._grid_frame = tk.Frame(self, bg='white', padx=6, pady=4)
        self._grid_frame.pack(fill='both', expand=True)

        # Today / Cancel row
        foot = tk.Frame(self, bg='#f4f6f7', pady=6)
        foot.pack(fill='x')
        tk.Button(foot, text='Today', command=self._pick_today,
                  font=('Helvetica', 10), cursor='hand2').pack(side='left', padx=8)
        tk.Button(foot, text='Cancel', command=self.destroy,
                  font=('Helvetica', 10), cursor='hand2').pack(side='right', padx=8)

    def _render(self):
        for w in self._grid_frame.winfo_children():
            w.destroy()
        self._hdr_label.config(
            text=calendar.month_name[self._month] + ' ' + str(self._year))

        today = date.today()
        cal = calendar.monthcalendar(self._year, self._month)
        for r, week in enumerate(cal):
            for c, day in enumerate(week):
                if day == 0:
                    tk.Label(self._grid_frame, text='', width=4, bg='white').grid(
                        row=r, column=c, padx=2, pady=2)
                else:
                    is_today = (day == today.day and
                                self._month == today.month and
                                self._year == today.year)
                    bg = '#1a5276' if is_today else '#f4f6f7'
                    fg = 'white' if is_today else '#1c2833'
                    btn = tk.Button(
                        self._grid_frame, text=str(day), width=3,
                        bg=bg, fg=fg, relief='flat',
                        font=('Helvetica', 10),
                        cursor='hand2',
                        command=lambda d=day: self._pick(d)
                    )
                    btn.grid(row=r, column=c, padx=2, pady=2)
                    btn.bind('<Enter>', lambda e, b=btn, orig=bg: b.config(
                        bg='#d6eaf8' if orig != '#1a5276' else '#295287'))
                    btn.bind('<Leave>', lambda e, b=btn, orig=bg: b.config(bg=orig))

    def _prev_month(self):
        if self._month == 1:
            self._month, self._year = 12, self._year - 1
        else:
            self._month -= 1
        self._render()

    def _next_month(self):
        if self._month == 12:
            self._month, self._year = 1, self._year + 1
        else:
            self._month += 1
        self._render()

    def _pick(self, day):
        self.result = '{:04d}-{:02d}-{:02d}'.format(self._year, self._month, day)
        self.destroy()

    def _pick_today(self):
        self.result = str(date.today())
        self.destroy()


# ── Main Application ─────────────────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Ekwendeni Mission Hospital — Admin Tool')
        self.geometry('1020x720')
        self.minsize(800, 520)
        self.configure(bg='#f4f6f7')

        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TNotebook', background='#f4f6f7')
        style.configure('TNotebook.Tab', padding=[12, 6], font=('Helvetica', 11))
        style.configure('TButton', padding=[8, 4])
        style.configure('Header.TLabel', font=('Helvetica', 13, 'bold'),
                        background='#1a5276', foreground='white', padding=10)
        style.configure('Status.TLabel', font=('Helvetica', 9),
                        background='#e8e8e8', foreground='#555')
        style.configure('Hint.TLabel', font=('Helvetica', 8),
                        background='#f4f6f7', foreground='#888')
        style.configure('Required.TLabel', font=('Helvetica', 10),
                        background='#f4f6f7', foreground='#c0392b')

        header = ttk.Label(self,
            text='  Ekwendeni Mission Hospital — Website Admin Tool',
            style='Header.TLabel')
        header.pack(fill='x', side='top')

        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self.events_tab = EventsTab(notebook)
        self.photos_tab = PhotosTab(notebook)

        notebook.add(self.events_tab, text='📅  Events Manager')
        notebook.add(self.photos_tab, text='🖼️  Photo Manager')

        self.status_var = tk.StringVar(value='Ready  |  Site folder: ' + SITE_ROOT)
        status_bar = ttk.Label(self, textvariable=self.status_var,
                               style='Status.TLabel', anchor='w')
        status_bar.pack(fill='x', side='bottom')

        self.events_tab.app = self
        self.photos_tab.app = self

    def set_status(self, msg):
        self.status_var.set(
            '  ' + msg + '  |  ' + datetime.now().strftime('%H:%M:%S') +
            '  |  ' + SITE_ROOT)


# ── Events Tab ───────────────────────────────────────────────────────────────

class EventsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.app = None
        self._selected_id = None
        self._image_path = None
        self._build()
        self._load()

    def _build(self):
        # Left panel: event list
        left = ttk.Frame(self, width=300)
        left.pack(side='left', fill='y', padx=(0, 5), pady=5)
        left.pack_propagate(False)

        self._list_header = ttk.Label(left, text='Events',
                                      font=('Helvetica', 11, 'bold'))
        self._list_header.pack(anchor='w', padx=5, pady=(5, 2))

        list_frame = ttk.Frame(left)
        list_frame.pack(fill='both', expand=True, padx=5)

        scrollbar = ttk.Scrollbar(list_frame, orient='vertical')
        self.listbox = tk.Listbox(
            list_frame, yscrollcommand=scrollbar.set,
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

        # Right panel: scrollable form
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
        canvas.bind_all('<MouseWheel>',
            lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), 'units'))

        self._build_form(self.form_frame)

    def _hint(self, parent, text):
        """Render a small gray hint line under a field."""
        ttk.Label(parent, text=text, style='Hint.TLabel').pack(
            anchor='w', padx=10, pady=(0, 4))

    def _build_form(self, parent):
        pad = {'padx': 10, 'pady': 2}
        self.fields = {}

        ttk.Label(parent, text='Edit Event',
                  font=('Helvetica', 12, 'bold')).pack(anchor='w', padx=10, pady=(10, 2))

        # Required fields legend
        legend_frame = ttk.Frame(parent)
        legend_frame.pack(anchor='w', padx=10, pady=(0, 8))
        ttk.Label(legend_frame, text='* ', style='Required.TLabel').pack(side='left')
        ttk.Label(legend_frame, text='Required field',
                  font=('Helvetica', 9), background='#f4f6f7',
                  foreground='#888').pack(side='left')

        # Title
        self._field_label(parent, 'Title', required=True)
        var = tk.StringVar()
        ttk.Entry(parent, textvariable=var, font=('Helvetica', 10)).pack(fill='x', **pad)
        self.fields['title'] = var
        self._hint(parent, 'The name of the event as it will appear on the website.')

        # Date with calendar picker
        self._field_label(parent, 'Date', required=True)
        date_frame = ttk.Frame(parent)
        date_frame.pack(fill='x', padx=10, pady=2)
        var_date = tk.StringVar()
        date_entry = ttk.Entry(date_frame, textvariable=var_date, font=('Helvetica', 10), width=16)
        date_entry.pack(side='left', padx=(0, 5))
        ttk.Button(date_frame, text='📅 Pick Date',
                   command=lambda: self._open_calendar(var_date)).pack(side='left')
        self.fields['date'] = var_date
        self._hint(parent, 'Click "Pick Date" or type in YYYY-MM-DD format (e.g. 2026-06-15).')

        # End Date
        self._field_label(parent, 'End Date (optional)')
        end_frame = ttk.Frame(parent)
        end_frame.pack(fill='x', padx=10, pady=2)
        var_end = tk.StringVar()
        ttk.Entry(end_frame, textvariable=var_end, font=('Helvetica', 10), width=16).pack(side='left', padx=(0, 5))
        ttk.Button(end_frame, text='📅 Pick Date',
                   command=lambda: self._open_calendar(var_end)).pack(side='left')
        self.fields['end_date'] = var_end
        self._hint(parent, 'Only needed for multi-day events. Leave blank for single-day events.')

        # Time
        self._field_label(parent, 'Time (optional)')
        var = tk.StringVar()
        ttk.Entry(parent, textvariable=var, font=('Helvetica', 10), width=12).pack(anchor='w', **pad)
        self.fields['time'] = var
        self._hint(parent, '24-hour format, e.g. 08:30 or 14:00. Leave blank if time is not set.')

        # Category
        self._field_label(parent, 'Category')
        var = tk.StringVar()
        ttk.Combobox(parent, textvariable=var, font=('Helvetica', 10),
                     values=CATEGORIES, state='readonly').pack(fill='x', **pad)
        self.fields['category'] = var
        self._hint(parent, 'Choose the type that best describes this event.')

        # Status
        self._field_label(parent, 'Status')
        var = tk.StringVar()
        ttk.Combobox(parent, textvariable=var, font=('Helvetica', 10),
                     values=STATUSES, state='readonly').pack(fill='x', **pad)
        self.fields['status'] = var
        self._hint(parent, 'Set "upcoming" for future events. Update to "past" after the event is over.')

        # Location
        self._field_label(parent, 'Location (optional)')
        var = tk.StringVar()
        ttk.Entry(parent, textvariable=var, font=('Helvetica', 10)).pack(fill='x', **pad)
        self.fields['location'] = var
        self._hint(parent, 'Where the event takes place, e.g. "Ekwendeni Hospital Main Grounds".')

        # Contact
        self._field_label(parent, 'Contact email/phone (optional)')
        var = tk.StringVar()
        ttk.Entry(parent, textvariable=var, font=('Helvetica', 10)).pack(fill='x', **pad)
        self.fields['contact'] = var
        self._hint(parent, 'Who to contact for more information about this event.')

        # Description
        self._field_label(parent, 'Description', required=True)
        w = tk.Text(parent, font=('Helvetica', 10), height=5, wrap='word',
                    relief='solid', bd=1)
        w.pack(fill='x', **pad)
        self.fields['description'] = w
        self._hint(parent, 'A plain-text description shown on the events page. 2–4 sentences is ideal.')

        # Image
        ttk.Label(parent, text='Image (optional):',
                  font=('Helvetica', 10)).pack(anchor='w', **pad)
        img_frame = ttk.Frame(parent)
        img_frame.pack(fill='x', padx=10, pady=2)
        self.fields['image'] = tk.StringVar()
        ttk.Entry(img_frame, textvariable=self.fields['image'],
                  font=('Helvetica', 10), state='readonly').pack(
                      side='left', fill='x', expand=True, padx=(0, 5))
        ttk.Button(img_frame, text='Browse…', command=self._browse_image).pack(side='left')
        ttk.Button(img_frame, text='Clear', command=self._clear_image).pack(side='left', padx=(3, 0))
        self._hint(parent, 'Optional photo for this event. JPG or PNG recommended.')

        # Image alt text
        self._field_label(parent, 'Image description (alt text)')
        var = tk.StringVar()
        ttk.Entry(parent, textvariable=var, font=('Helvetica', 10)).pack(fill='x', **pad)
        self.fields['image_alt'] = var
        self._hint(parent, 'Describe the image for screen readers, e.g. "Staff at community health day".')

        # Recurring
        self.recurring_var = tk.BooleanVar()
        ttk.Checkbutton(parent, text='Recurring event',
                        variable=self.recurring_var).pack(anchor='w', padx=10, pady=3)

        # Save / Clear buttons
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill='x', padx=10, pady=12)
        ttk.Button(btn_frame, text='💾  Save Event',
                   command=self._save_event).pack(side='left', padx=(0, 5))
        ttk.Button(btn_frame, text='✕  Clear Form',
                   command=self._clear_form).pack(side='left')

        self._clear_form()

    def _field_label(self, parent, text, required=False):
        """Render a field label, with a red asterisk if required."""
        frame = ttk.Frame(parent)
        frame.pack(anchor='w', padx=10, pady=(6, 1))
        ttk.Label(frame, text=text + ':', font=('Helvetica', 10)).pack(side='left')
        if required:
            ttk.Label(frame, text=' *', style='Required.TLabel').pack(side='left')

    def _open_calendar(self, string_var):
        dlg = CalendarDialog(self, string_var.get())
        if dlg.result:
            string_var.set(dlg.result)

    # ── List management ──

    def _load(self):
        data = load_events()
        self._events = data.get('events', [])
        self._events.sort(key=lambda e: e.get('date', ''))
        self.listbox.delete(0, 'end')
        for ev in self._events:
            label = '{} — {}'.format(ev.get('date', '?'), ev.get('title', '(no title)'))
            self.listbox.insert('end', label)
        self._selected_id = None

        upcoming, past = count_events_by_status(self._events)
        self._list_header.config(
            text='Events  ({} upcoming, {} past)'.format(upcoming, past))

    def _on_select(self, event):
        sel = self.listbox.curselection()
        if not sel:
            return
        ev = self._events[sel[0]]
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
            messagebox.showinfo('Select an Event',
                                'Please click on an event in the list first.')

    def _delete_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo('Select an Event',
                                'Please click on an event in the list first.')
            return
        ev = self._events[sel[0]]
        if messagebox.askyesno(
                'Delete Event',
                'Are you sure you want to delete:\n\n"{}"\n\nThis cannot be undone.'.format(
                    ev.get('title', ''))):
            data = load_events()
            data['events'] = [e for e in data['events'] if e.get('id') != ev.get('id')]
            save_events(data)
            self._load()
            self._clear_form()
            if self.app:
                self.app.set_status('Event deleted: {}'.format(ev.get('title', '')))

    def _populate_form(self, ev):
        self.fields['title'].set(ev.get('title', ''))
        self.fields['date'].set(ev.get('date', ''))
        self.fields['time'].set(ev.get('time', '') or '')
        self.fields['end_date'].set(ev.get('end_date', '') or '')
        self.fields['category'].set(ev.get('category', 'general'))
        self.fields['status'].set(ev.get('status', 'upcoming'))
        self.fields['location'].set(ev.get('location', ''))
        self.fields['contact'].set(ev.get('contact', ''))
        self.fields['image'].set(ev.get('image', ''))
        self.fields['image_alt'].set(ev.get('image_alt', ''))
        self.recurring_var.set(ev.get('is_recurring', False))

        desc = self.fields['description']
        desc.delete('1.0', 'end')
        desc.insert('1.0', ev.get('description', ''))
        self._image_path = None

    def _clear_form(self):
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
            filetypes=[('Image files', '*.jpg *.jpeg *.png *.gif *.webp'),
                       ('All files', '*.*')])
        if path:
            self._image_path = path
            self.fields['image'].set('(new image: {})'.format(os.path.basename(path)))

    def _clear_image(self):
        self._image_path = None
        self.fields['image'].set('')

    def _save_event(self):
        title = self.fields['title'].get().strip()
        date_str = self.fields['date'].get().strip()
        description = self.fields['description'].get('1.0', 'end').strip()

        if not title:
            messagebox.showerror('Missing Field', 'Please enter a title for the event.')
            return
        if not date_str:
            messagebox.showerror('Missing Field',
                                 'Please enter a date.\n\nUse the "Pick Date" button or type YYYY-MM-DD.')
            return
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror('Invalid Date',
                                 'Date must be in YYYY-MM-DD format (e.g. 2026-06-15).\n\n'
                                 'Use the "Pick Date" button to choose a date easily.')
            return
        if not description:
            messagebox.showerror('Missing Field', 'Please enter a description.')
            return

        # Auto-detect: warn if date is past but status is "upcoming"
        status_val = self.fields['status'].get() or 'upcoming'
        if date_str < str(date.today()) and status_val == 'upcoming':
            answer = messagebox.askyesnocancel(
                'Date Is in the Past',
                'The event date ({}) is in the past, but the status is set to "upcoming".\n\n'
                'Would you like to change the status to "past" before saving?'.format(date_str))
            if answer is None:
                return  # Cancel — don't save
            if answer:
                status_val = 'past'

        # Handle image copy
        image_value = self.fields['image'].get().strip()
        if self._image_path:
            try:
                image_value = copy_image_to_events(self._image_path)
                self._image_path = None
            except Exception as e:
                messagebox.showerror('Image Error',
                                     'Could not copy image: {}'.format(str(e)))
                return

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
            'status': status_val,
        }

        data = load_events()
        if self._selected_id:
            for i, ev in enumerate(data['events']):
                if ev.get('id') == self._selected_id:
                    event_dict['id'] = self._selected_id
                    data['events'][i] = event_dict
                    break
        else:
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
        left = ttk.Frame(self, width=220)
        left.pack(side='left', fill='y', padx=(0, 5), pady=5)
        left.pack_propagate(False)

        ttk.Label(left, text='Image Folders',
                  font=('Helvetica', 11, 'bold')).pack(anchor='w', padx=5, pady=(5, 2))

        self.folder_listbox = tk.Listbox(
            left, font=('Helvetica', 10),
            selectbackground='#1a5276', selectforeground='white',
            activestyle='none', relief='flat', bd=1)
        self.folder_listbox.pack(fill='both', expand=True, padx=5)
        self.folder_listbox.bind('<<ListboxSelect>>', self._on_folder_select)

        folder_btns = ttk.Frame(left)
        folder_btns.pack(fill='x', padx=5, pady=5)
        ttk.Button(folder_btns, text='+ New Folder',
                   command=self._new_folder).pack(fill='x', pady=2)
        ttk.Button(folder_btns, text='↻ Refresh',
                   command=self._load_folders).pack(fill='x', pady=2)

        right = ttk.Frame(self)
        right.pack(side='left', fill='both', expand=True, pady=5)

        self.folder_label = ttk.Label(right, text='Select a folder',
                                      font=('Helvetica', 11, 'bold'))
        self.folder_label.pack(anchor='w', padx=10, pady=(5, 2))

        self.file_listbox = tk.Listbox(
            right, font=('Helvetica', 10),
            selectbackground='#1a5276', selectforeground='white',
            activestyle='none', relief='flat', bd=1, selectmode='extended')
        scrollbar = ttk.Scrollbar(right, orient='vertical',
                                   command=self.file_listbox.yview)
        self.file_listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.file_listbox.pack(fill='both', expand=True, padx=10, pady=5)

        file_btns = ttk.Frame(right)
        file_btns.pack(fill='x', padx=10, pady=5)
        ttk.Button(file_btns, text='+ Add Images…',
                   command=self._add_images).pack(side='left', padx=(0, 5))
        ttk.Button(file_btns, text='✕ Delete Selected',
                   command=self._delete_images).pack(side='left')

        self.info_label = ttk.Label(right, text='',
                                    font=('Helvetica', 9), foreground='#626567')
        self.info_label.pack(anchor='w', padx=10, pady=(0, 5))

    def _load_folders(self):
        self.folder_listbox.delete(0, 'end')
        if not os.path.exists(IMAGES_ROOT):
            return
        for d in sorted(os.listdir(IMAGES_ROOT)):
            if os.path.isdir(os.path.join(IMAGES_ROOT, d)):
                self.folder_listbox.insert('end', d)

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
        files = sorted(f for f in os.listdir(folder_path)
                       if f.lower().endswith(IMAGE_EXTENSIONS))
        for fname in files:
            self.file_listbox.insert('end', fname)
        self.info_label.config(
            text='{} image(s) in this folder'.format(len(files)))

    def _new_folder(self):
        dialog = FolderNameDialog(self, 'New Folder')
        name = dialog.result
        if name:
            name = name.strip().replace(' ', '-').lower()
            new_path = os.path.join(IMAGES_ROOT, name)
            if os.path.exists(new_path):
                messagebox.showerror('Error',
                    'A folder named "{}" already exists.'.format(name))
                return
            os.makedirs(new_path, exist_ok=True)
            self._load_folders()
            if self.app:
                self.app.set_status('Created folder: ' + name)

    def _add_images(self):
        if not self._current_folder:
            messagebox.showinfo('Select a Folder',
                                'Please select a folder from the list first.')
            return
        paths = filedialog.askopenfilenames(
            title='Select images to add',
            filetypes=[('Image files', '*.jpg *.jpeg *.png *.gif *.webp'),
                       ('All files', '*.*')])
        if not paths:
            return
        folder_path = os.path.join(IMAGES_ROOT, self._current_folder)
        copied = 0
        for src in paths:
            dest = os.path.join(folder_path, os.path.basename(src))
            if os.path.exists(dest):
                base, ext = os.path.splitext(os.path.basename(src))
                dest = os.path.join(folder_path,
                                    '{}-{}{}'.format(base, str(uuid.uuid4())[:6], ext))
            shutil.copy2(src, dest)
            copied += 1
        self._load_files()
        if self.app:
            self.app.set_status('{} image(s) added to {}'.format(
                copied, self._current_folder))
        messagebox.showinfo('Done',
            '{} image(s) added to "{}".'.format(copied, self._current_folder))

    def _delete_images(self):
        sel = self.file_listbox.curselection()
        if not sel:
            messagebox.showinfo('Select Images',
                                'Please select one or more images to delete.')
            return
        filenames = [self.file_listbox.get(i) for i in sel]
        if messagebox.askyesno(
                'Delete Images',
                'Delete {} image(s)? This cannot be undone.\n\n{}'.format(
                    len(filenames),
                    '\n'.join(filenames[:10]) + ('…' if len(filenames) > 10 else ''))):
            folder_path = os.path.join(IMAGES_ROOT, self._current_folder)
            for fname in filenames:
                try:
                    os.remove(os.path.join(folder_path, fname))
                except OSError as e:
                    messagebox.showerror('Error',
                        'Could not delete {}: {}'.format(fname, str(e)))
            self._load_files()
            if self.app:
                self.app.set_status('{} image(s) deleted from {}'.format(
                    len(filenames), self._current_folder))


# ── Folder name dialog ───────────────────────────────────────────────────────

class FolderNameDialog(tk.Toplevel):
    def __init__(self, parent, title):
        super().__init__(parent)
        self.title(title)
        self.geometry('340x130')
        self.resizable(False, False)
        self.result = None

        ttk.Label(self, text='Folder name (lowercase, no spaces):').pack(
            padx=20, pady=(20, 5))
        self._var = tk.StringVar()
        entry = ttk.Entry(self, textvariable=self._var, width=30)
        entry.pack(padx=20)
        entry.focus()

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text='Create', command=self._ok).pack(
            side='left', padx=5)
        ttk.Button(btn_frame, text='Cancel', command=self.destroy).pack(
            side='left', padx=5)

        entry.bind('<Return>', lambda e: self._ok())
        self.grab_set()
        self.wait_window()

    def _ok(self):
        self.result = self._var.get()
        self.destroy()


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == '__main__':
    if not os.path.exists(os.path.join(SITE_ROOT, 'index.html')):
        print('WARNING: Could not find index.html in expected location: {}'.format(SITE_ROOT))
        print('Make sure you run this script from within the project folder.')

    print('Ekwendeni Mission Hospital — Admin Tool')
    print('Site folder: {}'.format(SITE_ROOT))
    print('Close the window to exit.')

    app = App()
    app.mainloop()
