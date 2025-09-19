# Timetable to Calendar ZJNU

Convert ZJNU timetable PDFs (EN/CN) into iCalendar (.ics) for Samsung, Google, Apple, and Outlook.

[![Release](https://img.shields.io/github/v/release/Al-rimi/Timetable-to-Calendar)](https://github.com/Al-rimi/Timetable-to-Calendar/releases)
![Platforms](https://img.shields.io/badge/platforms-Windows%20%7C%20macOS%20%7C%20Linux-2ea44f)
![License](https://img.shields.io/badge/license-MIT-blue)

> Prototype: provided “as is,” without warranty or liability. Not affiliated with ZJNU.

## Features

- Bilingual parsing with robust course block detection (△ ★ ▲ ☆)
- Exact section times for reliable imports
- Keeps “Not yet/未定”; outside items placed Sundays 14:00+ (1‑hour slots)
- Always‑on detailed per‑course summary (CLI/GUI)
- Simple Windows GUI (Browse/Drag‑and‑drop, Pick date, preset “2025 1st Semester”)
- CI builds for Windows, macOS, and Linux

## Downloads

| Platform | File     | Notes                            | Download             |
| -------- | -------- | -------------------------------- | -------------------- |
| Windows  | EXE      | duoble-click to run              | [Download][win-dl]   |
| macOS    | .app.zip | Unsigned; right‑click → Open     | [Download][mac-dl]   |
| Linux    | .tar.gz  | chmod +x; ensure Tk is installed | [Download][linux-dl] |

## Run from source

- From source (GUI):
  ```pwsh
  python gui_win.py
  ```
- From source (CLI):
  ```pwsh
  python timetable_to_calendar_zjnu.py
  ```

## Build (all platforms)

These steps produce a standalone binary using PyInstaller. Ensure Python 3.9+ and pip are installed.

Common Python dependencies:

```bash
pip install -r requirements.txt
pip install pyinstaller
```

### Windows

Using the provided spec (recommended):

```pwsh
pyinstaller --noconfirm gui_win.spec
```

One-file alternative with icon:

```pwsh
pyinstaller --onefile --noconsole --icon assets/icon.ico --name "Timetable to Calendar ZJNU" gui_win.py
```

Output appears in the `dist/` folder.

### macOS

Build a windowed .app bundle:

```bash
pyinstaller --noconfirm --windowed --name "Timetable to Calendar ZJNU" gui_win.py
```

Notes:

- The app is unsigned; on first run, right‑click the app and choose Open.
- If Tk is missing, install it (for example, via Homebrew: `brew install tcl-tk`).
- To use an icon, provide a `.icns` file and add `--icon path/to/icon.icns`.

### Linux

Install system Tk (example for Debian/Ubuntu):

```bash
sudo apt-get update
sudo apt-get install -y python3-tk
```

Build a one-file binary:

```bash
pyinstaller --noconfirm --noconsole --onefile --name "timetable-to-calendar-zjnu" gui_win.py
```

Notes:

- After extracting on another machine, ensure the file is executable: `chmod +x timetable-to-calendar-zjnu`.
- For broader compatibility, build on an older distribution (glibc compatibility).

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

<!-- Download link references -->

[win-dl]: https://github.com/Al-rimi/Timetable-to-Calendar/releases/download/v0.0.3/Timetable.to.Calendar.ZJNU.exe
[mac-dl]: https://github.com/Al-rimi/Timetable-to-Calendar/releases/download/v0.0.3/Timetable.to.Calendar.ZJNU.app.zip
[linux-dl]: https://github.com/Al-rimi/Timetable-to-Calendar/releases/download/v0.0.3/timetable-to-calendar-zjnu.tar.gz
