import tkinter as tk
from tkinter import ttk, filedialog
# from tkinter import scrolledtext  # removed old output pane
from pathlib import Path
from datetime import datetime
import os, sys, json, calendar, locale, subprocess
from typing import Literal, Optional, Any, Callable
try:
    import winreg  # type: ignore
except Exception:
    winreg = None  # type: ignore
try:
    import ctypes
    from ctypes import wintypes
except Exception:
    ctypes = None  # type: ignore

# Core module
# Lazy import heavy conversion module to speed GUI startup
app = None  # type: ignore


# --- i18n (EN, zh, FR) -------------------------------------------------------
Lang = Literal["en", "zh", "fr"]

TR: dict[Lang, dict[str, object]] = {
    "en": {
        "title": "Timetable to Calendar",
        "subtitle": "Convert ZJNU timetable PDF to calendar (.ics)",
        "inputs": "Inputs",
        "pdf_label": "Timetable PDF:",
        "browse": "Browse…",
        "choose_or_drop": "Choose PDF or Drag & Drop",
        "date_label": "Week 1 Monday (YYYY-MM-DD):",
        "pick_date": "Pick date",
        "sem_button": "2025 1st Semester",
    "generate": "Generate Calendar",
        "output": "Output",
    "share": "Copy",
    "share_copied": "Copied! Paste into anywhere",
        "open_folder": "Open folder",
        "warning_choose_pdf": "Warning: Choose a PDF timetable file.",
        "no_file": "No file selected",
        "working": "Working…",
        "select_date": "Select date",
    "prompt_monday": "Please select the Monday date for week 1",
    "ok": "OK",
    "cancel": "Cancel",
    "selected_date": "Selected date:",
        "year": "Year",
        "month": "Month",
        "weekdays": ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
        "courses": "Courses",
        "include": "Include",
    "day": "Day",
        "name": "Name",
        "type": "Type",
        "location": "Location",
        "weeks": "Weeks",
        "teacher": "Teacher",
    "session": "Session",
        "term": "Term",
        "auto_monday": "Auto Monday",
        "change_date": "Change date",
        "apply": "Apply",
        "select_all": "Select all",
        "deselect_all": "Deselect all",
        "no_courses": "No courses detected in the PDF.",
    },
    "zh": {
        "title": "课表转日历",
        "subtitle": "将浙师大课表 PDF 转为日历 (.ics)",
        "inputs": "输入",
        "pdf_label": "课表 PDF：",
        "browse": "浏览…",
        "choose_or_drop": "选择 PDF 或拖放",
        "date_label": "第1周周一（YYYY-MM-DD）：",
        "pick_date": "选择日期",
        "sem_button": "2025 第一学期",
    "generate": "生成日历",
        "output": "输出",
    "share": "复制",
    "share_copied": "已复制！粘贴到任意位置",
        "open_folder": "打开文件夹",
        "warning_choose_pdf": "提示：请选择课表 PDF 文件。",
        "no_file": "未选择文件",
        "working": "处理中…",
        "select_date": "选择日期",
    "prompt_monday": "请选择第1周周一的日期",
    "ok": "确定",
    "cancel": "取消",
    "selected_date": "已选日期：",
        "year": "年",
        "month": "月",
        "weekdays": ["一", "二", "三", "四", "五", "六", "日"],
        "courses": "课程",
        "include": "包含",
    "day": "星期",
        "name": "名称",
        "type": "类型",
        "location": "地点",
        "weeks": "周次",
        "teacher": "教师",
    "session": "节次",
        "term": "学期",
        "auto_monday": "自动周一",
        "change_date": "更改日期",
        "apply": "应用",
        "select_all": "全选",
        "deselect_all": "全不选",
        "no_courses": "未检测到课程。",
    },
    "fr": {
        "title": "Emploi du temps → Calendrier",
        "subtitle": "Convertir un PDF d'emploi du temps ZJNU en calendrier (.ics)",
        "inputs": "Entrées",
        "pdf_label": "PDF de l'emploi du temps :",
        "browse": "Parcourir…",
        "choose_or_drop": "Choisir un PDF ou Glisser-Déposer",
        "date_label": "Lundi de la semaine 1 (AAAA-MM-JJ) :",
        "pick_date": "Choisir la date",
        "sem_button": "1er semestre 2025",
    "generate": "Générer le calendrier",
        "output": "Sortie",
    "share": "Copier",
    "share_copied": "Copié ! Collez n'importe où",
        "open_folder": "Ouvrir le dossier",
        "warning_choose_pdf": "Attention : choisissez un fichier PDF.",
        "no_file": "Aucun fichier sélectionné",
        "working": "Traitement…",
        "select_date": "Choisir la date",
    "prompt_monday": "Veuillez sélectionner le lundi de la semaine 1",
    "ok": "OK",
    "cancel": "Annuler",
    "selected_date": "Date sélectionnée :",
        "year": "Année",
        "month": "Mois",
        "weekdays": ["Lu", "Ma", "Me", "Je", "Ve", "Sa", "Di"],
        "courses": "Cours",
        "include": "Inclure",
    "day": "Jour",
        "name": "Nom",
        "type": "Type",
        "location": "Lieu",
        "weeks": "Semaines",
        "teacher": "Enseignant",
    "session": "Séances",
        "term": "Semestre",
        "auto_monday": "Lundi auto",
        "change_date": "Changer la date",
        "apply": "Appliquer",
        "select_all": "Tout sélectionner",
        "deselect_all": "Tout désélectionner",
        "no_courses": "Aucun cours détecté dans le PDF.",
    },
}


class I18N:
    def __init__(self, lang: Optional[Lang] = None):
        self.lang: Lang = lang or self.detect()

    @staticmethod
    def detect() -> Lang:
        lang: Lang = "en"
        try:
            lc = None
            try:
                lc_tuple = locale.getlocale()
                lc = lc_tuple[0] if lc_tuple and lc_tuple[0] else None
            except Exception:
                lc = None
            if not lc:
                lc2 = getattr(locale, "getdefaultlocale", lambda: (None, None))()[0]
                lc = lc2 or os.environ.get("LANG") or ""
            lc = (lc or "").lower()
            if lc.startswith("zh"):
                return "zh"
            if lc.startswith("fr"):
                return "fr"
        except Exception:
            pass
        return lang

    def t(self, key: str, default: Optional[Any] = None) -> Any:
        d = TR.get(self.lang, TR["en"])  # type: ignore
        return d.get(key, default if default is not None else TR["en"].get(key, key))


class ThemeManager:
    def __init__(self):
        self._last_dark_state: Optional[bool] = None

    def is_windows_dark(self) -> bool:
        if sys.platform.startswith("win") and winreg is not None:
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize",
                )
                val, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                winreg.CloseKey(key)
                return int(val) == 0
            except Exception:
                return False
        return False

    # No titlebar manipulation; keep native OS frame as-is

    def apply_theme(self, master: tk.Misc, outbox: Optional[tk.Text] = None) -> None:
        try:
            import sv_ttk  # type: ignore
            sv_ttk.set_theme("dark" if self.is_windows_dark() else "light")
            return
        except Exception:
            pass
        if self.is_windows_dark():
            style = ttk.Style(master)
            try:
                style.theme_use("clam")
            except Exception:
                pass
            fg = "#ffffff"; bg = "#202020"; bg2 = "#303030"; acc = "#0a84ff"
            style.configure("TFrame", background=bg)
            style.configure("TLabelframe", background=bg, foreground=fg)
            style.configure("TLabelframe.Label", background=bg, foreground=fg)
            style.configure("TLabel", background=bg, foreground=fg)
            style.configure("TEntry", fieldbackground=bg2, foreground=fg, background=bg2)
            style.configure("TButton", background=bg2, foreground=fg)
            style.map("TButton", background=[["active", acc]], foreground=[["active", fg]])
            style.configure("Primary.TButton", background=acc, foreground="#000000")
            style.map("Primary.TButton", background=[["active", "#66b3ff"]])
            try:
                if outbox is not None:
                    outbox.configure(bg=bg2, fg=fg, insertbackground=fg)
            except Exception:
                pass

    def apply_titlebar(self, master: tk.Misc) -> None:
        # Attempt native dark title bar on Windows 10 1809+
        try:
            if not (sys.platform.startswith("win") and ctypes is not None and self.is_windows_dark()):
                return
            hwnd = master.winfo_id()
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            value = wintypes.BOOL(1)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                wintypes.HWND(hwnd),
                wintypes.DWORD(DWMWA_USE_IMMERSIVE_DARK_MODE),
                ctypes.byref(value),
                ctypes.sizeof(value),
            )
        except Exception:
            # If not supported, silently keep default title bar
            pass

    def start_theme_watch(self, master: tk.Misc, on_change: Optional[Callable[[bool], None]] = None, interval_ms: int = 1500) -> None:
        # Poll system setting and re-apply theme if it changes
        def _tick():
            try:
                cur = self.is_windows_dark()
                if self._last_dark_state is None:
                    self._last_dark_state = cur
                elif cur != self._last_dark_state:
                    self._last_dark_state = cur
                    # Re-apply ttk theme and (on Windows) native title bar mode
                    try:
                        self.apply_theme(master, None)
                    except Exception:
                        pass
                    try:
                        self.apply_titlebar(master)
                    except Exception:
                        pass
                    if on_change is not None:
                        try:
                            on_change(cur)
                        except Exception:
                            pass
            except Exception:
                # Ignore detection errors and keep polling
                pass
            try:
                master.after(interval_ms, _tick)
            except Exception:
                # Master likely destroyed; stop polling
                return
        try:
            master.after(interval_ms, _tick)
        except Exception:
            pass


theme = ThemeManager()

def resource_path(rel: str) -> str:
    # Absolute path to resource for both dev and PyInstaller
    try:
        base = sys._MEIPASS  # type: ignore[attr-defined]
    except Exception:
        base = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base, rel)


def run_convert(pdf_path: str, monday_date: str) -> str:
    global app  # type: ignore
    if app is None:
        import importlib
        app = importlib.import_module("timetable_to_calendar_zjnu")
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
    try:
        app._backfill_teachers(courses)
    except Exception:
        pass
    if not courses:
        return "Error: No courses detected."

    # Prefer content-based student name + term for ICS filename
    try:
        ics_out, cal_name = app.compute_ics_output_path(str(pdf), meta, monday_date)
        ics_output = Path(ics_out)
    except Exception:
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
    def __init__(self, master: tk.Tk, initial: datetime, on_pick, tr: dict[str, object]):
        super().__init__(master)
        self.title(str(tr.get("select_date", "Select date")))
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        # Keep native window frame; no titlebar changes
        self._on_pick = on_pick
        frm = ttk.Frame(self, padding=12)
        frm.pack(fill=tk.BOTH, expand=True)
        # Header: month/year selectors
        top = ttk.Frame(frm)
        top.pack(fill=tk.X)
        # Prompt
        ttk.Label(frm, text=str(tr.get("prompt_monday", "Please select the Monday date for week 1"))).pack(fill=tk.X, pady=(0,6))
        self.var_year = tk.IntVar(value=initial.year)
        self.var_month = tk.IntVar(value=initial.month)
        years = [y for y in range(initial.year - 3, initial.year + 4)]
        ttk.Label(top, text=str(tr.get("year", "Year"))).pack(side=tk.LEFT)
        self.cb_year = ttk.Combobox(top, width=6, values=years, textvariable=self.var_year, state="readonly")
        self.cb_year.pack(side=tk.LEFT, padx=(6, 12))
        ttk.Label(top, text=str(tr.get("month", "Month"))).pack(side=tk.LEFT)
        self.cb_month = ttk.Combobox(top, width=4, values=list(range(1, 13)), textvariable=self.var_month, state="readonly")
        self.cb_month.pack(side=tk.LEFT, padx=(6, 0))
        self.cb_year.bind("<<ComboboxSelected>>", lambda e: self._render_days())
        self.cb_month.bind("<<ComboboxSelected>>", lambda e: self._render_days())
        # Weekday header
        grid = ttk.Frame(frm)
        grid.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
        self._grid = grid
        wds = tr.get("weekdays", ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"])  # type: ignore
        for i, wd in enumerate(wds):
            ttk.Label(grid, text=wd, anchor="center").grid(row=0, column=i, padx=2, pady=2)
        self._buttons = []
        self._render_days()
        # Selected date + actions
        bottom = ttk.Frame(frm)
        bottom.pack(fill=tk.X, pady=(8,0))
        self.var_selected = tk.StringVar(value="")
        ttk.Label(bottom, text=str(tr.get("selected_date", "Selected date:"))).pack(side=tk.LEFT)
        self.lbl_sel = ttk.Label(bottom, textvariable=self.var_selected)
        self.lbl_sel.pack(side=tk.LEFT, padx=(6,0))
        actions = ttk.Frame(frm)
        actions.pack(fill=tk.X, pady=(6,0))
        ttk.Button(actions, text=str(tr.get("ok", "OK")), command=self._ok).pack(side=tk.RIGHT)
        ttk.Button(actions, text=str(tr.get("cancel", "Cancel")), command=self._cancel).pack(side=tk.RIGHT, padx=(0,6))
        self._picked_dt = None

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
            self._picked_dt = dt
            self.var_selected.set(dt.strftime("%Y-%m-%d"))
        except Exception:
            self._picked_dt = None

    def _ok(self):
        if self._picked_dt is not None:
            try:
                self._on_pick(self._picked_dt)
            finally:
                self.destroy()
        else:
            # No date selected; keep window open
            pass

    def _cancel(self):
        try:
            self.destroy()
        except Exception:
            pass

    # No custom title bar fallback; only native methods are used


class App(ttk.Frame):
    def __init__(self, master: tk.Tk, lang: Lang):
        super().__init__(master, padding=16)
        self.master = master
        self.lang: Lang = lang
        self.tr = TR.get(self.lang, TR["en"])  # translations for current language
        master.title(str(self.tr.get("title", "Timetable to Calendar ZJNU")))
        try:
            master.iconbitmap(resource_path("assets/icon.ico"))
        except Exception:
            pass
        self.pack(fill=tk.BOTH, expand=True)

        # Header
        header = ttk.Label(self, text=str(self.tr.get("title", "Timetable to Calendar ZJNU")), font=("Segoe UI", 16, "bold"))
        sub = ttk.Label(self, text=str(self.tr.get("subtitle", "Convert ZJNU timetable PDF to calendar (.ics)")))
        header.grid(row=0, column=0, columnspan=4, sticky="w")
        sub.grid(row=1, column=0, columnspan=4, sticky="w")

        # Inputs group (modernized)
        grp = ttk.LabelFrame(self, text=str(self.tr.get("inputs", "Inputs")), padding=16)
        grp.grid(row=2, column=0, columnspan=4, sticky="nsew", pady=(12, 0))

        # Big choose button + drag-and-drop
        self.var_pdf = tk.StringVar(value="")
        self.btn_choose = ttk.Button(
            grp,
            text=str(self.tr.get("choose_or_drop", "Choose PDF or Drag & Drop")),
            command=self.pick_pdf,
            style="Choose.TButton",
            width=56,
        )
        try:
            self.btn_choose.configure(cursor="hand2")
        except Exception:
            pass
        self.btn_choose.grid(row=0, column=0, columnspan=4, sticky="we", pady=(0, 6))
        # Status label (left): kept blank; later shows student + term
        self.lbl_pdf = ttk.Label(grp, text="")
        self.lbl_pdf.grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 4))
        # Detected term label
        self.var_term = tk.StringVar(value="")
        self.lbl_term = ttk.Label(grp, textvariable=self.var_term)
        self.lbl_term.grid(row=1, column=3, sticky="e")
        # Hidden Monday-of-week-1 storage (only set programmatically)
        self.var_date = tk.StringVar(value="")

        grp.columnconfigure(0, weight=1)
        grp.columnconfigure(1, weight=0)
        grp.columnconfigure(2, weight=0)
        grp.columnconfigure(3, weight=0)

        # No explicit Analyze button; analysis runs automatically on pick/drop

        # Courses table and editor
        self.courses_pane = CoursesPane(self, self.tr)
        self.courses_pane.grid(row=3, column=0, columnspan=4, sticky="nsew", pady=(12, 0))
        # Initialize day display locale to UI language (updated after analyze)
        try:
            self.courses_pane.set_day_locale(self.lang, False)
        except Exception:
            pass
        # Footer actions: left (open folder + share), right (generate)
        actions = ttk.Frame(self)
        actions.grid(row=4, column=0, sticky="we", pady=(8, 0))
        actions.columnconfigure(0, weight=1)
        left = ttk.Frame(actions)
        left.grid(row=0, column=0, sticky="w")
        right = ttk.Frame(actions)
        right.grid(row=0, column=1, sticky="e")

        self.btn_open_folder = ttk.Button(left, text=str(self.tr.get("open_folder", "Open folder")), command=self.open_folder, state=tk.DISABLED)
        self.btn_open_folder.pack(side=tk.LEFT)
        self.btn_share = ttk.Button(left, text=str(self.tr.get("share", "Copy")), command=self.share_ics, state=tk.DISABLED)
        self.btn_share.pack(side=tk.LEFT, padx=(8,0))
        self.btn_generate = ttk.Button(right, text=str(self.tr.get("generate", "Generate Calendar")), command=self.on_generate, style="Primary.TButton")
        self.btn_generate.configure(state=tk.DISABLED)
        self.btn_generate.pack(side=tk.RIGHT)

        self._last_ics = None
        # Drag & drop support on the big button
        self._setup_drag_and_drop(self.btn_choose)
        # Layout weights
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)
        # Apply styles and theme
        self._apply_styles()
        self._apply_dark_mode_if_needed()
        # Start watching for OS theme changes to auto-switch
        try:
            def _on_theme_change(is_dark: bool):
                try:
                    # Recompute table sizing under new style
                    self.courses_pane._auto_size_columns()
                except Exception:
                    pass
            theme.start_theme_watch(self.master, on_change=_on_theme_change, interval_ms=1500)
        except Exception:
            pass
        self._last_courses = []
        self._last_is_chinese = False
        self._last_term = None
        self._asked_for_monday_term = None
        self._last_meta = None

    # Styling
    def _apply_styles(self):
        self.master.option_add("*Font", ("Segoe UI", 11))
        style = ttk.Style(self.master)
        try:
            style.configure("TButton", padding=(14, 10))
            style.configure("TLabel", padding=(2, 2))
            style.configure("TEntry", padding=6)
            style.configure("TLabelframe.Label", font=("Segoe UI", 10, "bold"))
            style.configure("Primary.TButton", padding=(18, 12), font=("Segoe UI", 12, "bold"))
            style.configure("Small.TButton", padding=(6, 4), font=("Segoe UI", 10))
            style.configure("Choose.TButton", padding=(22, 16), font=("Segoe UI", 12, "bold"))
        except Exception:
            pass

    # Drag & drop
    def _setup_drag_and_drop(self, widget):
        self._dnd_enabled = False
        try:
            from tkinterdnd2 import DND_FILES  # type: ignore
        except Exception:
            return
        # Try on: provided widget (big button), this frame, and the root window
        candidates = [widget, self]
        try:
            if hasattr(self.master, 'drop_target_register'):
                candidates.append(self.master)
        except Exception:
            pass
        for tgt in candidates:
            try:
                if hasattr(tgt, 'drop_target_register'):
                    tgt.drop_target_register(DND_FILES)
                    # Encourage a 'copy' action so the OS shows an allowed cursor
                    try:
                        tgt.dnd_bind('<<DropEnter>>', self._on_drop_enter)
                        tgt.dnd_bind('<<DropPosition>>', self._on_drop_position)
                    except Exception:
                        pass
                    tgt.dnd_bind('<<Drop>>', self._on_drop)
                    self._dnd_enabled = True
            except Exception:
                continue
        # No debug or hint output; button still works without DnD

    def _on_drop(self, event):
        raw = (event.data or "").strip()
        if not raw:
            return
        # Reset open buttons when a new PDF is dropped
        try:
            self.btn_share.configure(state=tk.DISABLED)
            self.btn_open_folder.configure(state=tk.DISABLED)
            self._last_ics = None
        except Exception:
            pass
        # TkinterDnD on Windows may provide brace-wrapped paths; support multiple files
        paths: list[str] = []
        if raw.startswith('{') and raw.endswith('}'):
            # Could be one or many: {C:\path a.pdf} {C:\path b.pdf}
            parts = []
            buf = ""
            depth = 0
            for ch in raw:
                if ch == '{':
                    if depth == 0:
                        buf = ""
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        parts.append(buf)
                else:
                    if depth > 0:
                        buf += ch
            paths = [p.strip() for p in parts if p.strip()]
        else:
            # Space-separated unbraced list; take first token
            paths = [raw.split()[0]]
        if not paths:
            return
        # Prefer first path that is a PDF; if a folder is dropped, try to locate a PDF inside
        chosen: Optional[str] = None
        for p in paths:
            if p.lower().endswith('.pdf'):
                chosen = p
                break
        if not chosen:
            # Take the first entry and inspect
            p0 = paths[0]
            if os.path.isdir(p0):
                # Look for PDFs within the folder (non-recursive, then recursive)
                try:
                    pdfs = [str(x) for x in Path(p0).glob('*.pdf')]
                    if not pdfs:
                        pdfs = [str(x) for x in Path(p0).rglob('*.pdf')]
                    if pdfs:
                        chosen = pdfs[0]
                except Exception:
                    pass
        if not chosen:
            return
        self.var_pdf.set(chosen)
        try:
            self.btn_generate.configure(state=tk.NORMAL)
        except Exception:
            pass
        # Do not display file name; analysis will show student+term
        # Auto-analyze after drop
        try:
            self.master.after(10, self.on_analyze)
        except Exception:
            self.on_analyze()

    # DnD helpers: return an allowed action to improve UX
    def _on_drop_enter(self, event):
        try:
            return event.action or "copy"
        except Exception:
            return "copy"

    def _on_drop_position(self, event):
        try:
            return event.action or "copy"
        except Exception:
            return "copy"

    # Actions
    def pick_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if path:
            self.var_pdf.set(path)
            try:
                self.btn_generate.configure(state=tk.NORMAL)
            except Exception:
                pass
            # Reset open buttons when a new PDF is picked
            try:
                self.btn_share.configure(state=tk.DISABLED)
                self.btn_open_folder.configure(state=tk.DISABLED)
                self._last_ics = None
            except Exception:
                pass
            # Do not display file name; analysis will show student+term
            # Auto-analyze after picking
            try:
                self.master.after(10, self.on_analyze)
            except Exception:
                self.on_analyze()
    # Removed complex button status; keep UI simple

    def on_analyze(self):
        pdf = self.var_pdf.get().strip()
        if not pdf:
            try:
                self.btn_generate.configure(state=tk.DISABLED)
            except Exception:
                pass
            return
        # On every analyze, ensure open buttons are disabled until a new ICS is generated
        try:
            self.btn_share.configure(state=tk.DISABLED)
            self.btn_open_folder.configure(state=tk.DISABLED)
            self._last_ics = None
        except Exception:
            pass
        # Analyze PDF and populate courses table
        self.master.update_idletasks()
        data = self._extract_pdf(pdf)
        if not data:
            self.courses_pane.set_courses([])
            self.var_term.set("")
            try:
                self.btn_generate.configure(state=tk.DISABLED)
            except Exception:
                pass
            return
        headers, rows, meta, is_chinese = data
        self._last_meta = meta
        rows = self._merge_continuations(headers, rows)
        self._set_type_map(is_chinese)
        courses = self._extract_courses(headers, rows, meta)
        try:
            app._backfill_teachers(courses)
        except Exception:
            pass
        self._last_courses = courses
        self._last_is_chinese = is_chinese
        # Update day display locale: Chinese if UI is zh OR timetable is Chinese; else French if UI is fr; else English
        try:
            self.courses_pane.set_day_locale(self.lang, is_chinese)
        except Exception:
            pass
        # Student info + term
        try:
            info = app.extract_student_info_from_pdf(pdf, meta)
            student_name = (info.get("name") or "").strip()
        except Exception:
            student_name = ""
        try:
            term = app.extract_term_from_content(pdf, meta)
        except Exception:
            term = self._extract_term_from_meta(meta)
        self._last_term = term
        display_term = self._format_term_display(term, is_chinese) if term else ""
        # Right side: academic year/term only
        self.var_term.set(display_term)
        # Left side: student name formatted
        if student_name:
            left_label = f"{student_name}课表" if is_chinese else f"{student_name}'s Curriculum"
        else:
            left_label = ""
        try:
            self.lbl_pdf.configure(text=left_label)
        except Exception:
            pass
        # Known term Mondays; prompt only if unknown/missing
        known_mondays = {"2025-2026-1": "2025-09-08"}
        if term and term in known_mondays:
            self.var_date.set(known_mondays[term])
        else:
            key = term or "unknown"
            if self._asked_for_monday_term != key:
                self._asked_for_monday_term = key
                self.open_date_picker()
        self.courses_pane.set_courses(courses)
        # Keep generate enabled while a PDF is loaded; courses may be toggled later
        try:
            self.btn_generate.configure(state=tk.NORMAL)
        except Exception:
            pass

    def on_generate(self):
        pdf = self.var_pdf.get().strip()
        if not pdf:
            return
        monday = self.var_date.get().strip()
        # Validate Monday date
        try:
            datetime.strptime(monday, "%Y-%m-%d")
        except Exception:
            # Prompt for Monday date if invalid
            self.open_date_picker()
            return
        selected = self.courses_pane.get_selected_courses()
        if not selected:
            return
        # Build ICS directly using the helper in module
        try:
            # Compute ICS path using content-based name + term
            ics_path_str, cal_name = app.compute_ics_output_path(pdf, self._last_meta or [], monday)
            ics_path = Path(ics_path_str)
            self._build_ics(selected, monday, str(ics_path), self._last_is_chinese)
            self._last_ics = str(ics_path)
            if ics_path.exists():
                self.btn_share.configure(state=tk.NORMAL)
                self.btn_open_folder.configure(state=tk.NORMAL)
        except Exception:
            self.btn_share.configure(state=tk.DISABLED)
            self.btn_open_folder.configure(state=tk.DISABLED)

    # Output log removed; modern UI replaces the scrolled text

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
            try:
                print(f"Error opening file: {e}")
            except Exception:
                pass

    def open_folder(self):
        if not self._last_ics:
            return
        folder = str(Path(self._last_ics).parent)
        try:
            if sys.platform.startswith("win"):
                subprocess.run(["explorer", "/select,", self._last_ics])
            elif sys.platform == "darwin":
                os.system(f'open -R "{self._last_ics}"')
            else:
                os.system(f'nautilus --select "{self._last_ics}" || xdg-open "{folder}"')
        except Exception as e:
            try:
                print(f"Error opening folder: {e}")
            except Exception:
                pass

    def share_ics(self):
        if not self._last_ics:
            return
        path = os.path.abspath(self._last_ics)
        try:
            if sys.platform.startswith("win") and ctypes is not None:
                # Share file via Windows clipboard as CF_HDROP (file drop)
                import ctypes.wintypes as wt
                CF_HDROP = 15
                GMEM_MOVEABLE = 0x0002
                GMEM_ZEROINIT = 0x0040

                k32 = ctypes.windll.kernel32
                u32 = ctypes.windll.user32
                # Set function signatures to avoid truncation on 64-bit
                k32.GlobalAlloc.restype = wt.HGLOBAL
                k32.GlobalAlloc.argtypes = [wt.UINT, ctypes.c_size_t]
                k32.GlobalLock.restype = ctypes.c_void_p
                k32.GlobalLock.argtypes = [wt.HGLOBAL]
                k32.GlobalUnlock.argtypes = [wt.HGLOBAL]
                k32.GlobalFree.argtypes = [wt.HGLOBAL]
                u32.OpenClipboard.argtypes = [wt.HWND]
                u32.OpenClipboard.restype = wt.BOOL
                u32.EmptyClipboard.restype = wt.BOOL
                u32.SetClipboardData.argtypes = [wt.UINT, wt.HANDLE]
                u32.SetClipboardData.restype = wt.HANDLE
                u32.CloseClipboard.restype = wt.BOOL

                class DROPFILES(ctypes.Structure):
                    _fields_ = [
                        ("pFiles", wt.DWORD),
                        ("pt", wt.POINT),
                        ("fNC", wt.BOOL),
                        ("fWide", wt.BOOL),
                    ]

                file_list = (path + "\0\0").encode("utf-16le")
                size = ctypes.sizeof(DROPFILES) + len(file_list)
                hGlobal = k32.GlobalAlloc(GMEM_MOVEABLE | GMEM_ZEROINIT, size)
                if not hGlobal:
                    raise RuntimeError("GlobalAlloc failed")
                ptr = k32.GlobalLock(hGlobal)
                if not ptr:
                    k32.GlobalFree(hGlobal)
                    raise RuntimeError("GlobalLock failed")
                try:
                    df = DROPFILES.from_address(ptr)
                    df.pFiles = ctypes.sizeof(DROPFILES)
                    df.pt = wt.POINT(0, 0)
                    df.fNC = True
                    df.fWide = True
                    ctypes.memmove(ptr + ctypes.sizeof(DROPFILES), file_list, len(file_list))
                finally:
                    k32.GlobalUnlock(hGlobal)
                if not u32.OpenClipboard(None):
                    k32.GlobalFree(hGlobal)
                    raise RuntimeError("OpenClipboard failed")
                try:
                    u32.EmptyClipboard()
                    if not u32.SetClipboardData(CF_HDROP, hGlobal):
                        # On failure, we must free the memory
                        k32.GlobalFree(hGlobal)
                        raise RuntimeError("SetClipboardData failed")
                    # On success, ownership is transferred to the clipboard; do not free hGlobal
                    hGlobal = None  # type: ignore
                finally:
                    u32.CloseClipboard()
                # Quick feedback on the Share button text
                try:
                    orig = self.btn_share.cget("text")
                    self.btn_share.configure(text=str(self.tr.get("share_copied", "Copied! Paste into anywhere")))
                    self.master.after(1500, lambda: self.btn_share.configure(text=orig))
                except Exception:
                    pass
            else:
                # Fallback: copy file path as text for manual sharing
                try:
                    self.master.clipboard_clear()
                    self.master.clipboard_append(path)
                except Exception:
                    pass
        except Exception as e:
            try:
                print(f"Error sharing file: {e}")
            except Exception:
                pass

    def open_date_picker(self):
        def _set(dt: datetime):
            self.var_date.set(dt.strftime("%Y-%m-%d"))
        try:
            cur = datetime.strptime(self.var_date.get().strip() or "2025-09-08", "%Y-%m-%d")
        except Exception:
            cur = datetime.today()
        DatePicker(self.master, cur, _set, self.tr)

    def set_fall_2025(self):
        self.var_date.set("2025-09-08")

    def _apply_dark_mode_if_needed(self):
        theme.apply_theme(self.master, None)

    # --- Internal helpers that wrap the core library ---
    def _extract_pdf(self, pdf_path: str):
        global app
        if app is None:
            import importlib
            app = importlib.import_module("timetable_to_calendar_zjnu")
        tables = app.extract_tables(pdf_path, strategy="lines")
        result = app.merge_main_table(tables, collapse_newlines=False)
        if not result or not result[0]:
            return None
        headers, rows, meta, _notes, is_chinese = result
        return headers, rows, meta, is_chinese

    def _merge_continuations(self, headers, rows):
        return app.merge_continuation_rows(headers, rows)

    def _set_type_map(self, is_chinese: bool):
        app.set_active_type_map(use_chinese=is_chinese)

    def _extract_courses(self, headers, rows, meta):
        courses = app.extract_courses_from_table(headers, rows, preserve_newlines=True)
        courses += app.extract_outside_courses(meta)
        return courses

    def _build_ics(self, courses, monday_date, output, is_chinese: bool):
        app.build_ics(
            courses,
            monday_date=monday_date,
            output_path=output,
            tz="Asia/Shanghai",
            tz_mode="floating",
            cal_name=Path(output).stem,
            cal_desc=f"Generated timetable starting Monday {monday_date}",
            uid_domain=None,
            chinese=is_chinese,
        )

    def _extract_term_from_meta(self, metadata_lines: list[str]) -> Optional[str]:
        # Look for patterns like 2025-2026-1; handle Unicode dashes/fullwidth digits
        import re as _re

        def _normalize(s: str) -> str:
            if not s:
                return ""
            # map unicode dashes to ASCII hyphen-minus
            dash_chars = "\u2010\u2011\u2012\u2013\u2014\u2212\ufe63\uff0d"
            trans = {ord(ch): '-' for ch in dash_chars}
            # map fullwidth digits to ASCII
            for i in range(10):
                trans[ord(chr(0xFF10 + i))] = ord('0') + i
            s = s.translate(trans)
            return s

        pat = _re.compile(r"(\d{4})[-](\d{4})[-]([1-9])")

        # 1) Scan metadata
        for line in (metadata_lines or []):
            ln = _normalize(line)
            m = pat.search(ln)
            if m:
                return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"

        # 2) Fallback: scan filename if available
        try:
            pdf_name = Path(self.var_pdf.get()).stem
            ln = _normalize(pdf_name)
            m = pat.search(ln)
            if m:
                return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
        except Exception:
            pass

        return None

    @staticmethod
    def _format_term_display(term: str, is_chinese: bool) -> str:
        # term like '2025-2026-1'
        try:
            start, end, sem = term.split('-')
            if is_chinese:
                return f"{start}-{end}学年第{sem}学期"
            else:
                # English display
                return f"{start}-{end} academic year {sem} term"
        except Exception:
            return term

    # No busy/progress UI needed due to fast analysis


class CoursesPane(ttk.Frame):
    def __init__(self, master: tk.Misc, tr: dict[str, object]):
        super().__init__(master, padding=8)
        self.tr = tr
        self._day_locale: Lang = "en"  # how to display day names
        # Table
        table_frame = ttk.LabelFrame(self, text=str(tr.get("courses", "Courses")), padding=8)
        table_frame.pack(fill=tk.BOTH, expand=True)
        self._columns = ("include", "day", "name", "type", "session", "location", "weeks", "teacher")
        cols = self._columns
        # Container for tree (grid inside, pack outside)
        tree_container = ttk.Frame(table_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)
        self.tree = ttk.Treeview(tree_container, columns=cols, show="headings", selectmode="browse", height=10)
        self.tree.heading("include", text=str(tr.get("include", "Include")))
        self.tree.heading("day", text=str(tr.get("day", "Day")))
        self.tree.heading("name", text=str(tr.get("name", "Name")))
        self.tree.heading("type", text=str(tr.get("type", "Type")))
        self.tree.heading("session", text=str(tr.get("session", "Session")))
        self.tree.heading("location", text=str(tr.get("location", "Location")))
        self.tree.heading("weeks", text=str(tr.get("weeks", "Weeks")))
        self.tree.heading("teacher", text=str(tr.get("teacher", "Teacher")))
        # Initial column hints; auto-resize will refine these and keep within window
        self.tree.column("include", width=50, stretch=True, anchor="center")
        self.tree.column("day", width=60, stretch=True, anchor="center")
        self.tree.column("name", width=240, stretch=True)
        self.tree.column("type", width=90, stretch=True)
        self.tree.column("session", width=70, stretch=True, anchor="center")
        self.tree.column("location", width=180, stretch=True)
        self.tree.column("weeks", width=110, stretch=True)
        self.tree.column("teacher", width=140, stretch=True)

        # Layout with grid inside the container
        self.tree.grid(row=0, column=0, sticky="nsew")
        tree_container.rowconfigure(0, weight=1)
        tree_container.columnconfigure(0, weight=1)

        # Auto-resize columns when the widget size changes
        self.tree.bind("<Configure>", self._auto_size_columns, add=True)
        # Column size config: relative weights used by auto sizer
        self._col_weight = {
            "include": 0.9, "day": 1.2, "name": 4.0, "type": 1.0,
            "session": 0.9, "location": 1.2, "weeks": 1.2, "teacher": 1.0,
        }
        # Select/deselect all
        btns = ttk.Frame(table_frame)
        btns.pack(fill=tk.X, pady=(6,0))
        ttk.Button(btns, text=str(tr.get("select_all", "Select all")), command=self.select_all).pack(side=tk.LEFT)
        ttk.Button(btns, text=str(tr.get("deselect_all", "Deselect all")), command=self.deselect_all).pack(side=tk.LEFT, padx=(6,0))
        # Inline edit bindings
        self.tree.bind("<Button-1>", self._on_click, add=True)
        self.tree.bind("<Double-1>", self._on_double_click, add=True)
        self._courses: list[dict] = []
        self._rows: list[str] = []
        self._edit_entry: Optional[tk.Entry] = None
        self._edit_iid: Optional[str] = None
        self._edit_col: Optional[int] = None

    def set_courses(self, courses: list[dict]):
        self._courses = [] if not courses else [self._normalize_course(c) for c in courses]
        self._sort_courses_inplace()
        self._rebuild_table()
        # no editor: selection not required
        # Ensure columns fit the available space
        try:
            self._auto_size_columns()
        except Exception:
            pass

    def get_selected_courses(self) -> list[dict]:
        out: list[dict] = []
        for c in self._courses:
            if not c.get("include", True):
                continue
            item = self._to_output_course(c)
            out.append(item)
        return out

    def select_all(self):
        for c in self._courses:
            c["include"] = True
        self._refresh_table()

    def _auto_size_columns(self, event=None):
        try:
            total = max(0, int(self.tree.winfo_width()))
            if total <= 0:
                return
            cols = list(self._columns)
            wsum = sum(self._col_weight.get(c, 1.0) for c in cols) or 1.0
            assigned = 0
            # Assign widths proportionally, last column takes any remainder to match total
            for i, c in enumerate(cols):
                if i == len(cols) - 1:
                    w = max(1, total - assigned)
                else:
                    share = self._col_weight.get(c, 1.0) / wsum
                    w = max(1, int(total * share))
                    assigned += w
                self.tree.column(c, width=w, stretch=True)
        except Exception:
            pass

    def _day_index(self, day: Optional[str]) -> int:
        d = self._normalize_day(day or "") or ""
        order = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}
        return order.get(d, 7)

    def _first_period(self, periods: list[int]) -> int:
        try:
            return min(int(x) for x in (periods or [])) if periods else 0
        except Exception:
            return 0

    def _sort_courses_inplace(self) -> None:
        try:
            self._courses.sort(key=lambda c: (
                self._day_index(c.get("day")),
                self._first_period(c.get("periods") or []),
                (c.get("name") or ""),
            ))
        except Exception:
            pass

    def _rebuild_table(self) -> None:
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        self._rows.clear()
        if not self._courses:
            return
        for c in self._courses:
            disp_day = self._display_day(c.get("day") or "")
            row = (
                "✔" if c.get("include", True) else "✖",
                disp_day,
                c.get("name", ""),
                c.get("type", ""),
                self._periods_to_session(c.get("periods") or []),
                c.get("location", ""),
                self._weeks_to_text(c.get("weeks") or []),
                c.get("teacher", ""),
            )
            iid = self.tree.insert("", "end", values=row)
            self._rows.append(iid)

    def deselect_all(self):
        for c in self._courses:
            c["include"] = False
        self._refresh_table()

    def _on_click(self, event):
        # Toggle include on single click in the first column
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        rowid = self.tree.identify_row(event.y)
        colid = self.tree.identify_column(event.x)  # '#1', '#2', ...
        if not rowid or not colid:
            return
        col_idx = int(colid.replace('#','')) - 1
        if col_idx == 0:  # include
            try:
                idx = self._rows.index(rowid)
                self._courses[idx]["include"] = not bool(self._courses[idx].get("include", True))
                self._refresh_table()
            except Exception:
                pass

    def _on_double_click(self, event):
        # Start editing the clicked cell (except Include column)
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        rowid = self.tree.identify_row(event.y)
        colid = self.tree.identify_column(event.x)
        if not rowid or not colid:
            return
        col_idx = int(colid.replace('#','')) - 1
        if col_idx == 0:
            return
        self._start_edit(rowid, col_idx)

    def _start_edit(self, rowid: str, col_idx: int):
        try:
            bbox = self.tree.bbox(rowid, f"#{col_idx+1}")
        except Exception:
            return
        if not bbox:
            return
        x, y, w, h = bbox
        vals = self.tree.item(rowid, "values")
        current = vals[col_idx] if col_idx < len(vals) else ""
        # Destroy previous editor
        if self._edit_entry is not None:
            try:
                self._edit_entry.destroy()
            except Exception:
                pass
        entry = tk.Entry(self.tree)
        entry.insert(0, current)
        entry.place(x=x, y=y, width=w, height=h)
        entry.focus_set()
        entry.select_range(0, tk.END)
        self._edit_entry = entry
        self._edit_iid = rowid
        self._edit_col = col_idx
        entry.bind("<Return>", lambda e: self._finish_edit(True))
        entry.bind("<Escape>", lambda e: self._finish_edit(False))
        entry.bind("<FocusOut>", lambda e: self._finish_edit(True))

    def _finish_edit(self, commit: bool):
        if self._edit_entry is None or self._edit_iid is None or self._edit_col is None:
            return
        text = self._edit_entry.get() if commit else None
        try:
            self._edit_entry.destroy()
        except Exception:
            pass
        entry, iid, col = self._edit_entry, self._edit_iid, self._edit_col
        self._edit_entry = None
        self._edit_iid = None
        self._edit_col = None
        if text is None:
            return
        try:
            idx = self._rows.index(iid)
        except Exception:
            return
        field = self._columns[col]
        c = self._courses[idx]
        if field == "weeks":
            c["weeks"] = self._parse_weeks(text)
        elif field == "day":
            norm = self._normalize_day(text) or c.get("day")
            c["day"] = norm
        elif field == "session":
            c["periods"] = self._parse_session(text)
        else:
            c[field] = text.strip()
        self._refresh_table()

    def _refresh_table(self):
        # Keep rows ordered Monday→Sunday, then by session
        self._sort_courses_inplace()
        self._rebuild_table()
        # After updating rows, adjust column widths
        try:
            self._auto_size_columns()
        except Exception:
            pass

    @staticmethod
    def _normalize_course(c: dict) -> dict:
        out = {
            "include": True if c.get("outside") is None else not bool(c.get("outside") is False),
            "name": (c.get("name") or "").strip(),
            "type": (c.get("type") or "").strip(),
            "location": (c.get("location") or "").strip(),
            "weeks": list(c.get("weeks") or []),
            "teacher": (c.get("teacher") or "").strip(),
            "periods": list(c.get("periods") or []),
            "day": c.get("day"),
        }
        return out

    @staticmethod
    def _weeks_to_text(weeks: list[int]) -> str:
        if not weeks:
            return ""
        return ",".join(str(w) for w in sorted(set(weeks)))

    @staticmethod
    def _periods_to_session(periods: list[int]) -> str:
        if not periods:
            return ""
        p = sorted(set(int(x) for x in periods))
        # Condense consecutive numbers into ranges
        out = []
        s = p[0]
        prev = p[0]
        for x in p[1:]:
            if x == prev + 1:
                prev = x
                continue
            out.append(f"{s}-{prev}" if s != prev else f"{s}")
            s = prev = x
        out.append(f"{s}-{prev}" if s != prev else f"{s}")
        return ",".join(out)

    @staticmethod
    def _parse_session(text: str) -> list[int]:
        if not text:
            return []
        import re
        parts = [t.strip() for t in text.replace("，", ",").split(",") if t.strip()]
        out = set()
        for p in parts:
            m = re.match(r"^(\d+)-(\d+)$", p)
            if m:
                a, b = int(m.group(1)), int(m.group(2))
                if a <= b:
                    for x in range(a, b + 1):
                        out.add(x)
            elif p.isdigit():
                out.add(int(p))
        return sorted(out)

    @staticmethod
    def _parse_weeks(text: str) -> list[int]:
        if not text:
            return []
        parts = [t.strip() for t in text.split(',') if t.strip()]
        out = set()
        import re
        for p in parts:
            m = re.match(r"^(\d+)-(\d+)$", p)
            if m:
                a, b = int(m.group(1)), int(m.group(2))
                if a <= b:
                    for x in range(a, b + 1):
                        out.add(x)
            elif p.isdigit():
                out.add(int(p))
        return sorted(out)

    def _to_output_course(self, c: dict) -> dict:
        # Preserve periods and day so ICS times remain correct
        return {
            "name": c.get("name", ""),
            "type": c.get("type", ""),
            "location": c.get("location", ""),
            "weeks": list(c.get("weeks") or []),
            "teacher": c.get("teacher", ""),
            "periods": list(c.get("periods") or []),
            "day": c.get("day"),
        }

    @staticmethod
    def _normalize_day(text: str) -> Optional[str]:
        t = (text or "").strip().lower()
        if not t:
            return None
        mapping = {
            "mon": "Mon", "monday": "Mon", "周一": "Mon", "星期一": "Mon",
            "tue": "Tue", "tuesday": "Tue", "周二": "Tue", "星期二": "Tue",
            "wed": "Wed", "wednesday": "Wed", "周三": "Wed", "星期三": "Wed",
            "thu": "Thu", "thursday": "Thu", "周四": "Thu", "星期四": "Thu",
            "fri": "Fri", "friday": "Fri", "周五": "Fri", "星期五": "Fri",
            "sat": "Sat", "saturday": "Sat", "周六": "Sat", "星期六": "Sat",
            "sun": "Sun", "sunday": "Sun", "周日": "Sun", "星期日": "Sun",
            # French full/abbr
            "lundi": "Mon", "lun": "Mon", "lun.": "Mon",
            "mardi": "Tue", "mar": "Tue", "mar.": "Tue",
            "mercredi": "Wed", "mer": "Wed", "mer.": "Wed",
            "jeudi": "Thu", "jeu": "Thu", "jeu.": "Thu",
            "vendredi": "Fri", "ven": "Fri", "ven.": "Fri",
            "samedi": "Sat", "sam": "Sat", "sam.": "Sat",
            "dimanche": "Sun", "dim": "Sun", "dim.": "Sun",
        }
        return mapping.get(t)

    # --- Day display localization ---
    def set_day_locale(self, ui_lang: Lang, timetable_is_chinese: bool) -> None:
        # If UI is Chinese OR timetable is Chinese → display Chinese.
        # Else if UI is French → display French. Else English.
        if ui_lang == "zh" or timetable_is_chinese:
            self._day_locale = "zh"
        elif ui_lang == "fr":
            self._day_locale = "fr"
        else:
            self._day_locale = "en"
        try:
            self._refresh_table()
        except Exception:
            pass

    def _display_day(self, canon: str) -> str:
        c = (canon or "").strip()
        if not c:
            return ""
        # Canonical → localized
        if self._day_locale == "zh":
            mapping = {"Mon": "星期一", "Tue": "星期二", "Wed": "星期三", "Thu": "星期四", "Fri": "星期五", "Sat": "星期六", "Sun": "星期日"}
        elif self._day_locale == "fr":
            mapping = {"Mon": "Lundi", "Tue": "Mardi", "Wed": "Mercredi", "Thu": "Jeudi", "Fri": "Vendredi", "Sat": "Samedi", "Sun": "Dimanche"}
        else:
            mapping = {"Mon": "Monday", "Tue": "Tuesday", "Wed": "Wednesday", "Thu": "Thursday", "Fri": "Friday", "Sat": "Saturday", "Sun": "Sunday"}
        return mapping.get(c, c)



def main():
    # Determine language from system; default to English
    lang = I18N.detect()
    # Set AppUserModelID so taskbar shows the app correctly
    try:
        if sys.platform.startswith("win") and ctypes is not None:
            appid = "ZJNU.TimetableToCalendar"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)
    except Exception:
        pass
    # Try to enable real drag & drop by using TkinterDnD when available
    try:
        from tkinterdnd2 import TkinterDnD  # type: ignore
        root = TkinterDnD.Tk()
    except Exception:
        root = tk.Tk()
    app_ui = App(root, lang)
    # Narrower default width; restore previous height to avoid overlap
    try:
        root.geometry("780x480")
        root.minsize(760, 480)
    except Exception:
        root.minsize(800, 480)
    # Attempt native dark title bar when supported (no custom frames)
    try:
        theme.apply_titlebar(root)
        # Watch for system theme changes and reapply automatically
        theme.start_theme_watch(root, on_change=None, interval_ms=1500)
    except Exception:
        pass
    root.mainloop()


if __name__ == "__main__":
    main()
