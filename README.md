# Timetable to Calendar ZJNU

Parse Zhejiang Normal University (ZJNU) timetable PDFs and export an iCalendar (.ics) file you can import into Samsung/Google/Apple calendars.

Why a prototype? Because the best place to generate calendars is upstream, at the university portal itself. The same page that renders the timetable already has clean, structured data in the database; adding a “Download .ics” button there would be simpler, more reliable, and far easier to maintain than parsing PDFs. We hope universities adopt this idea in the future.

## What it does

- Reads a ZJNU timetable PDF (English or Chinese).
- Extracts course blocks (using the markers △ ★ ▲ ☆) and parses:
  - Weeks and sections (节 / Section)
  - Day of week
  - Teacher and location (keeps “Not yet/未定” as-is)
- Maps “Sections” to exact start/end times provided by you.
- Builds a standards-compliant ICS with calendar metadata suitable for Samsung/Google/Apple calendars.
- Outside (dayless) courses are scheduled on Sunday in 1-hour slots starting at 14:00 (14–15, 15–16, …) per week.
- Prints a detailed, per-course summary (always on) to help verify parsing.

## How it works (brief)

- Uses `pdfplumber` to reconstruct the main table and stitch split rows.
- Splits cell content by course markers (△ ★ ▲ ☆) and assembles multi-line course titles (ignoring PDF line breaks).
- Parses weeks (Week … / 第…周) and sections ((a-b Section)/(a-b 节)).
- Extracts teacher/location from English or Chinese labels; preserves “Not yet/未定”. Outside items default to “Online/线上”.
- Generates `.ics` via the `ics` library with proper headers and DTSTAMP; times follow the configured section timetable exactly.

## Core function: build_ics

The heart of this project is the `build_ics` function. Everything else (PDF parsing, cleanup) just prepares data for it. If your system already has structured data, you can skip all parsing and call this function directly.

Function signature (simplified):

```
build_ics(
  courses: list[dict],        # parsed classes
  monday_date: str,           # YYYY-MM-DD, week 1 Monday
  output_path: str,           # where to write .ics
  tz: str = "Asia/Shanghai",
  tz_mode: str = "floating", # "floating"|"tzid"|"utc"
  cal_name: str | None = None,
  cal_desc: str | None = None,
  uid_domain: str | None = None,
  chinese: bool = False,
) -> None
```

Expected `courses` item shape:

- name: str — full title + type (e.g., "Software Testing Theory")
- day: str — Mon/Tue/Wed/Thu/Fri/Sat/Sun (omit for “outside”)
- weeks: list[int] — academic weeks (1-based)
- periods: list[int] — section numbers (e.g., [6,7])
- teacher: str — instructor name
- location: str — room/campus; keep empty to default to Not yet/未定
- outside: bool — true for items not on a timetable day

What it does:

1. Computes each class date by adding (week-1) weeks and day offset to `monday_date`.

2. Maps `periods` to exact start/end times using SECTION_TIMES (authoritative bell times).

3. Creates one VEVENT per (course × week) with:

   - Name, DTSTART, DTEND
   - Location: in-table empty → Not yet/未定; outside → Online/线上
   - Description: localized "Teacher: …"
   - Stable UID with optional `uid_domain` (e.g., studentId.term)

4. Writes an ICS with:
   - CALSCALE, METHOD, X-WR-CALNAME, X-WR-CALDESC, X-WR-TIMEZONE
   - DTSTAMP on each VEVENT
   - CRLF line endings for importer compatibility

Special handling:

- tz_mode:

  - floating (default): write local times without TZ, avoids device shifts
  - tzid: add TZID parameter for DTSTART/DTEND
  - utc: write UTC and strip trailing Z for uniformity

- Outside courses (no day): placed on Sunday in 1-hour slots starting at 14:00 per week (14–15, 15–16, …).

Re-implementing elsewhere: If you already know week numbers, weekday, section spans, and room/teacher, you can build `courses` and call `build_ics` without any PDF work.

## Requirements

- Python 3.9+
- pip packages: `pdfplumber`, `ics`
 - Optional (for drag-and-drop in the GUI): `tkinterdnd2`

Install:

```pwsh
pip install pdfplumber ics
# optional for GUI drag-and-drop support
pip install tkinterdnd2
```

## Usage

Run interactively and provide the PDF path and the Monday date of week 1:

```pwsh
python timetable_to_calendar_zjnu.py
```

The script writes the `.ics` file next to your PDF.

### Windows GUI (Tkinter, no extra deps)

Tkinter comes with Python. Run the GUI:

```pwsh
python gui_win.py
```

Build a standalone EXE with an icon:

```pwsh
pip install pyinstaller
pyinstaller --onefile --noconsole --icon assets/icon.ico --name "Timetable to Calendar ZJNU" gui_win.py
```

CLI also available via `timetable_to_calendar_zjnu.py`.

GUI features:

- Browse to pick a PDF, or drag-and-drop a PDF anywhere in the window (requires `tkinterdnd2`, optional).
- Enter “Week 1 Monday” date, or use the small Pick date dialog.
- Quick preset button “2025 1st Semester” fills the date for Fall 2025.
- Centered “Generate ICS” primary button.
- Output panel shows the full, detailed per-course summary and a completion line.
- Buttons to open the generated `.ics` or its folder.

### Example (English PDF)

Input:

```text
Enter the PDF timetable path: .\samples\AL RAIMI ABDULLAH(2025-2026-1)课表 EN.pdf
Enter the Monday date of week 1 (YYYY-MM-DD): 2025-09-08
```

Output (excerpt; the same detailed summary also appears in the GUI output panel):

```text
Detected 17 courses; generating calendar…
-- Course summary --
01. [Sun] Experiment … :: Individual Project Training Experiment @ Not yet | Li Minshuo
02. [Fri] Theory … :: Cyber Security Theory @ 25-315 | Md Shaiful Islam Babu
…
17. [outside] Theory … :: Cross-cultural Communication Theory @ Online 1035877982 | 郑晓红
Calendar exported: …\AL_RAIMI_ABDULLAH(2025-2026-1)课表_EN.ics (events: 174)
```

### Example (Chinese PDF)

```text
Detected 17 courses; generating calendar…
-- Course summary --
01. [Sun] 实验 … :: 个人项目实训 实验 @ 未定 |
02. [Fri] 理论 … :: 网络安全 理论 @ 主校区（金华）25-315 |
…
17. [outside] 理论 … :: 跨文化交际 理论 @ 线上 | 郑晓红
Calendar exported: …\AL_RAIMI_ABDULLAH(2025-2026-1)课表_CH.ics (events: 175)
```

## Behavior notes

- In-table missing locations remain “Not yet/未定”. Only outside/extra items use “Online/线上”.
- Outside items are placed on Sundays (14:00–), one hour per item per week.
- Event times strictly follow the section-to-time mapping configured in the script.
- ICS includes calendar name/description/timezone headers; each event has a DTSTAMP for importer compatibility.

## Limitations

- PDF extraction varies; this prototype handles common ZJNU formats but may need tweaks for new layouts.
- Heuristics avoid hardcoding course names, but edge cases are possible with unusual PDF line breaks.

## Roadmap

- Native “Download .ics” from the university system (ideal)
- Optional CLI flags (non-interactive mode)
- More robust location normalization (EN/CN variants)

## License

MIT — see `LICENSE`.
