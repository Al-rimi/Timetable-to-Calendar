import tkinter as tk
from tkinter import ttk, filedialog
from tkinter import scrolledtext
from pathlib import Path
from datetime import datetime
import os, sys, json, calendar

# Core module
import timetable_to_calendar_zjnu as app


def resource_path(rel: str) -> str:
    # Absolute path to resource for both dev and PyInstaller
    try:
        base = sys._MEIPASS  # type: ignore[attr-defined]
    except Exception:
        base = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base, rel)


def run_convert(pdf_path: str, monday_date: str) -> str:
    pdf = Path(pdf_path)
    if not pdf.exists():
        return "Error: PDF not found."
    try:
        datetime.strptime(monday_date, "%Y-%m-%d")
    except Exception:
        return "Error: Monday date must be YYYY-MM-DD."

    tables = app.extract_tables(str(pdf), strategy="lines")
    result = app.merge_main_table(tables, collapse_newlines=False)
    if not result or not result[0]:
        return "Error: Could not detect timetable header."
    headers, rows, meta, _notes, is_chinese = result
    rows = app.merge_continuation_rows(headers, rows)
    app.set_active_type_map(use_chinese=is_chinese)
    courses = app.extract_courses_from_table(headers, rows, preserve_newlines=True)
    courses += app.extract_outside_courses(meta)
    if not courses:
        return "Error: No courses detected."

    pdf_dir = pdf.resolve().parent
    pdf_stem = pdf.stem
    ics_output = pdf_dir / f"{pdf_stem.replace(' ', '_')}.ics"
    cal_name = pdf_stem.replace("课表", "").strip() or pdf_stem
    cal_desc = f"Generated timetable starting Monday {monday_date}"

    # Always generate and return a detailed summary for GUI output and terminal
    try:
        summary = app.summarize_courses(courses, is_chinese)
        print(summary)
    except Exception:
        summary = None

    app.build_ics(
        courses,
        monday_date=monday_date,
        output_path=str(ics_output),
        tz="Asia/Shanghai",
        tz_mode="floating",
        cal_name=cal_name,
        cal_desc=cal_desc,
        uid_domain=None,
        chinese=is_chinese,
    )
    # Compute simple metrics for the output channel
    events = sum(len(c.get("weeks", []) or []) for c in courses)
    # Include summary in the returned text so GUI can show all details by default
    if summary:
        return summary + f"\nDone → {ics_output} (courses: {len(courses)}, events: {events})"
    return f"Done → {ics_output} (courses: {len(courses)}, events: {events})"


class DatePicker(tk.Toplevel):
    def __init__(self, master: tk.Tk, initial: datetime, on_pick):
        super().__init__(master)
        self.title("Select date")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self._on_pick = on_pick
        frm = ttk.Frame(self, padding=12)
        frm.pack(fill=tk.BOTH, expand=True)
        # Header: month/year selectors
        top = ttk.Frame(frm)
        top.pack(fill=tk.X)
        self.var_year = tk.IntVar(value=initial.year)
        self.var_month = tk.IntVar(value=initial.month)
        years = [y for y in range(initial.year - 3, initial.year + 4)]
        ttk.Label(top, text="Year").pack(side=tk.LEFT)
        self.cb_year = ttk.Combobox(top, width=6, values=years, textvariable=self.var_year, state="readonly")
        self.cb_year.pack(side=tk.LEFT, padx=(6, 12))
        ttk.Label(top, text="Month").pack(side=tk.LEFT)
        self.cb_month = ttk.Combobox(top, width=4, values=list(range(1, 13)), textvariable=self.var_month, state="readonly")
        self.cb_month.pack(side=tk.LEFT, padx=(6, 0))
        self.cb_year.bind("<<ComboboxSelected>>", lambda e: self._render_days())
        self.cb_month.bind("<<ComboboxSelected>>", lambda e: self._render_days())
        # Weekday header
        grid = ttk.Frame(frm)
        grid.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
        self._grid = grid
        for i, wd in enumerate(["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]):
            ttk.Label(grid, text=wd, anchor="center").grid(row=0, column=i, padx=2, pady=2)
        self._buttons = []
        self._render_days()

    def _render_days(self):
        # Clear previous day buttons
        for b in self._buttons:
            b.destroy()
        self._buttons.clear()
        y, m = self.var_year.get(), self.var_month.get()
        first_weekday, days_in_month = calendar.monthrange(y, m)
        # calendar.monthrange: Monday=0 ... Sunday=6; align to our header where Monday is column 0
        row = 1
        col = first_weekday
        for d in range(1, days_in_month + 1):
            btn = ttk.Button(self._grid, text=str(d), width=3, command=lambda dd=d: self._pick(dd))
            btn.grid(row=row, column=col, padx=2, pady=2)
            self._buttons.append(btn)
            col += 1
            if col > 6:
                col = 0
                row += 1

    def _pick(self, day: int):
        y, m = self.var_year.get(), self.var_month.get()
        try:
            dt = datetime(year=y, month=m, day=day)
            self._on_pick(dt)
        finally:
            self.destroy()


class App(ttk.Frame):
    def __init__(self, master: tk.Tk):
        super().__init__(master, padding=16)
        self.master = master
        master.title("Timetable to Calendar ZJNU")
        try:
            master.iconbitmap(resource_path("assets/icon.ico"))
        except Exception:
            pass
        self.pack(fill=tk.BOTH, expand=True)

        self._cfg_path = os.path.join(Path.home(), ".zjnu_ics_gui.json")
        self._cfg = self._load_cfg()

        # Header
        header = ttk.Label(self, text="Timetable to Calendar ZJNU", font=("Segoe UI", 16, "bold"))
        sub = ttk.Label(self, text="Convert ZJNU timetable PDF to calendar (.ics)")
        header.grid(row=0, column=0, columnspan=4, sticky="w")
        sub.grid(row=1, column=0, columnspan=4, sticky="w")

        # Inputs group
        grp = ttk.LabelFrame(self, text="Inputs", padding=12)
        grp.grid(row=2, column=0, columnspan=4, sticky="nsew", pady=(12, 0))

        # PDF row
        ttk.Label(grp, text="Timetable PDF:").grid(row=0, column=0, sticky="e")
        self.var_pdf = tk.StringVar(value=self._cfg.get("last_pdf", ""))
        ent_pdf = ttk.Entry(grp, textvariable=self.var_pdf, width=60)
        ent_pdf.grid(row=0, column=1, sticky="we", padx=8)
        # Right-aligned action column 3 (aligned with semester preset button)
        self.btn_browse = ttk.Button(grp, text="Browse…", command=self.pick_pdf, width=18)
        self.btn_browse.grid(row=0, column=3, sticky="w")

        # Date row
        ttk.Label(grp, text="Week 1 Monday (YYYY-MM-DD):").grid(row=1, column=0, sticky="e", pady=(8, 0))
        self.var_date = tk.StringVar(value=self._cfg.get("last_date", "2025-09-08"))
        self.ent_date = ttk.Entry(grp, textvariable=self.var_date, width=18)
        self.ent_date.grid(row=1, column=1, sticky="w", padx=(8, 2), pady=(8, 0))
        ttk.Button(
            grp,
            text="Pick date",
            command=self.open_date_picker,
            style="Small.TButton",
            width=10,
        ).grid(row=1, column=1, sticky="w", padx=(84, 0), pady=(8, 0))
        self.btn_sem = ttk.Button(grp, text="2025 1st Semester", command=self.set_fall_2025, width=18)
        self.btn_sem.grid(row=1, column=3, sticky="w", pady=(8, 0))

        grp.columnconfigure(1, weight=1)

        # Actions (centered primary button)
        act = ttk.Frame(self)
        act.grid(row=3, column=0, columnspan=4, sticky="we", pady=(12, 0))
        act.columnconfigure(0, weight=1)
        act.columnconfigure(1, weight=0)
        act.columnconfigure(2, weight=1)
        self.btn_gen = ttk.Button(act, text="Generate ICS", command=self.on_generate, style="Primary.TButton")
        self.btn_gen.grid(row=0, column=1, padx=8, pady=4)

        # Status/output
        out = ttk.LabelFrame(self, text="Output", padding=12)
        out.grid(row=4, column=0, columnspan=4, sticky="nsew", pady=(12, 0))
        self.outbox = scrolledtext.ScrolledText(out, height=8, wrap=tk.WORD, state=tk.DISABLED)
        self.outbox.grid(row=0, column=0, columnspan=3, sticky="nsew")
        out.rowconfigure(0, weight=1)
        out.columnconfigure(0, weight=1)
        self.btn_open_file = ttk.Button(out, text="Open .ics", command=self.open_ics, state=tk.DISABLED)
        self.btn_open_file.grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.btn_open_folder = ttk.Button(out, text="Open folder", command=self.open_folder, state=tk.DISABLED)
        self.btn_open_folder.grid(row=1, column=1, sticky="w", pady=(8, 0), padx=(8, 0))

        self._last_ics = None

        # Optional drag & drop (if tkinterdnd2 is available)
        self._setup_drag_and_drop(ent_pdf)

        # Layout weights
        self.columnconfigure(0, weight=1)
        self.rowconfigure(4, weight=1)

        # Apply simple modern-ish styling
        self._apply_styles()

    def _apply_styles(self):
        # Global font
        self.master.option_add("*Font", ("Segoe UI", 11))
        style = ttk.Style(self.master)
        try:
            # Cleaner, modern padding/sizing
            style.configure("TButton", padding=(14, 10))
            style.configure("TLabel", padding=(2, 2))
            style.configure("TEntry", padding=6)
            style.configure("TLabelframe", padding=12)
            style.configure("TLabelframe.Label", font=("Segoe UI", 10, "bold"))
            # Primary action (bigger) and Small button styles
            style.configure("Primary.TButton", padding=(18, 12), font=("Segoe UI", 12, "bold"))
            style.configure("Small.TButton", padding=(6, 4), font=("Segoe UI", 10))
        except Exception:
            pass

    def _load_cfg(self) -> dict:
        try:
            with open(self._cfg_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_cfg(self):
        try:
            with open(self._cfg_path, "w", encoding="utf-8") as f:
                json.dump({
                    "last_pdf": self.var_pdf.get().strip(),
                    "last_date": self.var_date.get().strip(),
                }, f)
        except Exception:
            pass

    def _setup_drag_and_drop(self, widget):
        try:
            from tkinterdnd2 import DND_FILES  # type: ignore
            # Register drop on the entry widget
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind('<<Drop>>', self._on_drop)
            # Also allow dropping anywhere on the main frame
            try:
                self.drop_target_register(DND_FILES)
                self.dnd_bind('<<Drop>>', self._on_drop)
            except Exception:
                pass
        except Exception:
            # tkinterdnd2 not available; no-op
            pass

    def _on_drop(self, event):
        # Windows paths may be quoted and space-separated; take the first file
        raw = event.data.strip()
        if raw.startswith('{') and raw.endswith('}'):
            raw = raw[1:-1]
        path = raw.split('} {')[0].strip()
        self.var_pdf.set(path)

    def pick_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if path:
            self.var_pdf.set(path)

    def on_generate(self):
        pdf = self.var_pdf.get().strip()
        date = self.var_date.get().strip()
        if not pdf:
            self._log("Warning: Choose a PDF timetable file.")
            return
        self.btn_gen.configure(state=tk.DISABLED)
        self._log("Working…")
        self.update_idletasks()
        try:
            msg = run_convert(pdf, date)
            self._log(msg)
            # Compute expected .ics path and enable open buttons if exists
            pdf_path = Path(pdf)
            ics_path = pdf_path.with_name(pdf_path.stem.replace(" ", "_") + ".ics")
            self._last_ics = str(ics_path)
            if ics_path.exists():
                self.btn_open_file.configure(state=tk.NORMAL)
                self.btn_open_folder.configure(state=tk.NORMAL)
            else:
                self.btn_open_file.configure(state=tk.DISABLED)
                self.btn_open_folder.configure(state=tk.DISABLED)
            # Persist last inputs
            self._save_cfg()
        finally:
            self.btn_gen.configure(state=tk.NORMAL)

    def _log(self, text: str):
        self.outbox.configure(state=tk.NORMAL)
        self.outbox.insert(tk.END, text + "\n")
        self.outbox.see(tk.END)
        self.outbox.configure(state=tk.DISABLED)

    def open_ics(self):
        if not self._last_ics:
            return
        path = self._last_ics
        try:
            if sys.platform.startswith("win"):
                os.startfile(path)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                os.system(f'open "{path}"')
            else:
                os.system(f'xdg-open "{path}"')
        except Exception as e:
            self._log(f"Error opening file: {e}")

    def open_folder(self):
        if not self._last_ics:
            return
        folder = str(Path(self._last_ics).parent)
        try:
            if sys.platform.startswith("win"):
                os.startfile(folder)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                os.system(f'open "{folder}"')
            else:
                os.system(f'xdg-open "{folder}"')
        except Exception as e:
            self._log(f"Error opening folder: {e}")

    def open_date_picker(self):
        def _set(dt: datetime):
            self.var_date.set(dt.strftime("%Y-%m-%d"))
        try:
            cur = datetime.strptime(self.var_date.get().strip() or "2025-09-08", "%Y-%m-%d")
        except Exception:
            cur = datetime.today()
        DatePicker(self.master, cur, _set)

    def set_fall_2025(self):
        self.var_date.set("2025-09-08")


def main():
    # Try to enable real drag & drop by using TkinterDnD when available
    try:
        from tkinterdnd2 import TkinterDnD  # type: ignore
        root = TkinterDnD.Tk()
    except Exception:
        root = tk.Tk()
    app_ui = App(root)
    root.minsize(800, 380)
    root.mainloop()


if __name__ == "__main__":
    main()
