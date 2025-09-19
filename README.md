# Timetable to Calendar ZJNU

Convert ZJNU timetable PDFs (EN/CN) into iCalendar (.ics) for Samsung/Google/Apple/Outlook.

## Features

- Bilingual parsing with robust course block detection (△ ★ ▲ ☆)
- Exact section times for reliable imports
- Keeps “Not yet/未定”; outside items placed Sundays 14:00+ (1‑hour slots)
- Always‑on detailed per‑course summary (CLI/GUI)
- Simple Windows GUI (Browse/Drag‑and‑drop, Pick date, preset “2025 1st Semester”)
- CI builds for Windows/macOS/Linux

## Download & run

- Get builds from GitHub Actions artifacts or Releases:
  - Windows: “Timetable to Calendar ZJNU.exe”
  - macOS: “Timetable to Calendar ZJNU.app” (unsigned; right‑click → Open)
  - Linux: “timetable-to-calendar-zjnu” (make executable; Tk required)
- From source (GUI):
  ```pwsh
  python gui_win.py
  ```
- From source (CLI):
  ```pwsh
  python timetable_to_calendar_zjnu.py
  ```

## Importing the .ics

- Samsung/Google/Apple: import normally
- Outlook (Windows):
  - New Outlook: use Outlook on the web → Calendar → Add calendar → Upload from file (choose destination calendar), or use Classic Outlook
  - Classic Outlook: File → Open & Export → Import/Export → Import an iCalendar (.ics) → choose destination calendar

## Requirements

- Python 3.9+
- pip: pdfplumber, ics
- Optional (GUI drag‑and‑drop): tkinterdnd2

## Server‑side ICS (ideal)

Universities can skip PDFs and provide either:

- A “Download .ics” button (on‑demand file), or
- A tokenized subscribe‑able ICS URL (webcal/https) that auto‑updates in users’ calendars

Benefits: zero client setup, fewer errors, instant updates, and true cross‑platform support.

## License

MIT — see LICENSE.
