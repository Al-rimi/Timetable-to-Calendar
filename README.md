# Timetable → Calendar (ZJNU prototype)

This is a small prototype that parses Zhejiang Normal University (ZJNU) PDF timetables and exports an iCalendar (.ics) file you can import into any calendar app.

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
- Optional debug mode prints a concise, per-course summary to help verify parsing.

## How it works (brief)

- Uses `pdfplumber` to reconstruct the main table and stitch split rows.
- Splits cell content by course markers (△ ★ ▲ ☆) and assembles multi-line course titles (ignoring PDF line breaks).
- Parses weeks (Week … / 第…周) and sections ((a-b Section)/(a-b 节)).
- Extracts teacher/location from English or Chinese labels; preserves “Not yet/未定”. Outside items default to “Online/线上”.
- Generates `.ics` via the `ics` library with proper headers and DTSTAMP; times follow the configured section timetable exactly.

## Requirements

- Python 3.9+
- pip packages: `pdfplumber`, `ics`

Install:

```pwsh
pip install pdfplumber ics
```

## Usage

Run interactively and provide the PDF path and the Monday date of week 1:

```pwsh
python timetable_to_calendar_zjnu.py
```

Optional: enable debug summaries

```pwsh
$env:TT_DEBUG=1
python timetable_to_calendar_zjnu.py
```

The script writes the `.ics` file next to your PDF.

### Example (English PDF)

Input:

```text
Enter the PDF timetable path: .\samples\AL RAIMI ABDULLAH(2025-2026-1)课表 EN.pdf
Enter the Monday date of week 1 (YYYY-MM-DD): 2025-09-08
```

Output (excerpt):

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
