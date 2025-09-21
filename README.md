# Timetable to Calendar

<div align="center">

[![Release](https://img.shields.io/github/v/release/Al-rimi/Timetable-to-Calendar)](https://github.com/Al-rimi/Timetable-to-Calendar/releases)
![Platforms](https://img.shields.io/badge/platforms-Windows%20%7C%20macOS%20%7C%20Linux-2ea44f)
![License](https://img.shields.io/badge/license-MIT-blue)

![](assets/showcase.gif)

</div>

Convert ZJNU timetable PDFs (English/Chinese) into standards‑compliant iCalendar (.ics) files that import cleanly into all major calendar apps.

## Why Calendars, Not Timetables

- Less manual work: add once, see every class automatically.
- Fewer mistakes: time/location changes propagate to calendars.
- Works everywhere: one .ics fits all calendar apps.
- Lower support load for universities: fewer “when/where” questions.

## Downloads

<div align="center">

![](assets/screenshot.png)

| Windows | [Download][win-dl]   |
| ------- | -------------------- |
| macOS   | [Download][mac-dl]   |
| Linux   | [Download][linux-dl] |

</div>

<details>
<summary><strong>How to import .ics files</strong></summary>

- **iOS** (Apple Calendar): save the `.ics` to Files, then drag the file into Calendar.
- **Android**: some calendar apps import `.ics` directly just double click. If not, import via web at `calendar.google.com` → Settings → Import, then sync to your phone.
- **Windows** (Outlook/Calendar): double‑click the `.ics` and choose Outlook/Calendar, or Outlook → File → Open & Export → Import/Export → iCalendar (.ics).
- **macOS** (Calendar): double‑click the `.ics` to open in Calendar, or drag it onto the Calendar app.
- **Linux**: open with your calendar app (e.g., GNOME Calendar: File → Import; Thunderbird: File → Open → Calendar File).

</details>

---

Need help or want to improve this project?

- Open an [issue](https://github.com/Al-rimi/Timetable-to-Calendar/issues) for bugs or feature requests.
- Or [Contribute via PRs](https://github.com/Al-rimi/Timetable-to-Calendar/pulls).

See [Changelog](CHANGELOG.md) for updates.

## How It Works

- Input: ZJNU timetable PDF (EN/CN).
- Parse: extract tables and normalize course data.
- Generate: `build_ics` creates RFC 5545‑compliant events with stable UIDs and correct time handling (floating/TZID/UTC). One VEVENT is emitted per week occurrence for maximum importer compatibility.
- Output: a clean `.ics` you can import or subscribe to.

## For Universities

Direct server‑side ICS requires fewer resources and is more reliable than PDF parsing because the structured timetable rows already exist in the same session as the PDF generation. Implement:

- Direct iCalendar export: a “Download .ics” button generated from the same data source used for the PDF.
- Subscription feeds: secure, tokenized `webcal`/HTTPS URLs per user for auto‑updated schedules.
- Minimal mapping: course → VEVENT (summary, location, weekday/section → start/end, weeks → RRULE/EXDATE or one instance per week), stable `UID`, `DTSTAMP`, and consistent timezone handling.

Outcome: no client parsing, lower CPU usage, instant updates across all calendar apps.

<details>
<summary><strong>Technical Details (build_ics)</strong></summary>

Suggested field mapping (server‑side):

- Summary: course name (+ type if needed)
- Location: explicit room/campus; fallback to “Not yet/未定”
- DTSTART/DTEND: computed from weekday + section times (or your canonical schedule)
- Weeks: either `RRULE:FREQ=WEEKLY;BYDAY=...` with selective `EXDATE`s, or pre‑expanded instances (what this tool does)
- UID: stable key such as `<student-id>.<term>.<course-id>-<occurrence>@your-domain`

Tiny example using RRULE/EXDATE (server‑side):

```
BEGIN:VEVENT
UID:20251234.2025-2026-1.CS101-07@calendar.zjnu.edu.cn
DTSTAMP:20240901T000000Z
SUMMARY:CS101 Theory
LOCATION:Main Campus 25-315
DTSTART;TZID=Asia/Shanghai:20250908T080000
DTEND;TZID=Asia/Shanghai:20250908T092500
RRULE:FREQ=WEEKLY;BYDAY=MO;COUNT=16
EXDATE;TZID=Asia/Shanghai:20251006T080000
END:VEVENT
```

Core generation function:

```
build_ics(courses, monday_date, output_path,
          tz="Asia/Shanghai", tz_mode="floating",
          cal_name=None, cal_desc=None,
          uid_domain=None, chinese=False)
```

- Input model: each course dict may include `name`, `day` (`Mon`…`Sun`), `periods` (section numbers), `weeks` (list of week indices), `location`, `teacher`, and optional `outside=True`.
- Time map: section numbers are mapped via `SECTION_TIMES` (08:00–21:10). `monday_date` anchors week 1; dates are derived by weekday + (`week-1`).
- Timezone modes:
  - `floating` (default): writes local wall‑times without `TZID`/`Z` for best cross‑app behavior.
  - `tzid`: writes `DTSTART;TZID=<tz>`/`DTEND;TZID=<tz>` and adds `X‑WR‑TIMEZONE`.
  - `utc`: currently normalized to floating (no trailing `Z`) to keep campus times fixed across clients.
- UID strategy: stable, deterministic UIDs like `class-0001@<domain>`. The CLI derives `<domain>` from student id and term when available; otherwise from a sanitized calendar name. This keeps event identities stable across re‑exports.
- Outside‑of‑table items: scheduled on Sunday starting 14:00, one hour per item; multiple outside items in the same week are placed at 15:00, 16:00, …
- Import robustness: all event descriptions are single‑line; empty in‑table locations become `Not yet/未定`; outside items default to `Online/线上` when no location is present.
- ICS normalization: after serialization, the tool enforces CRLF line endings and injects missing calendar headers: `CALSCALE:GREGORIAN`, `METHOD:PUBLISH`, `X‑WR‑CALNAME`, `X‑WR‑CALDESC`, `X‑WR‑TIMEZONE`. It also ensures each `VEVENT` has a `DTSTAMP` and adjusts `DTSTART/DTEND` to match the selected `tz_mode`.
- Event granularity: no `RRULE`s are used in the generated file; the tool emits one `VEVENT` per week occurrence to maximize compatibility across calendar clients.

</details>

## Quick Start (from source)

- Requirements: Python 3.10+ and `pip`.
- Install:
  ```pwsh
  pip install -r requirements.txt
  ```
- Run GUI:
  ```pwsh
  python gui_win.py
  ```
- Run CLI:
  ```pwsh
  python timetable_to_calendar_zjnu.py
  ```
  The CLI is interactive: it prompts for the PDF path and the Week 1 Monday date, then writes the `.ics` next to the PDF.

## Build (Windows)

Quick local build producing `dist/Timetable to Calendar ZJNU.exe` with icon and version info:

```powershell
# From repo root
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\build.ps1
```

Options:

- OneDir (may reduce AV false positives and ease debugging):

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\build.ps1 -OneDir
```

- Clean artifacts and rebuild:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\build.ps1 -Clean
```

VS Code: Run task "Build: Windows (onefile)" (Terminal → Run Task) or choose the onedir/clean variants.

The build script will:

- Create/upgrade a local venv at `.venv`
- Install deps from `requirements.txt` and `pyinstaller`
- Generate Windows version info from `pyproject.toml`
- Build using `gui_win.spec`

- macOS (app bundle, unsigned):
  ```bash
  pyinstaller --noconfirm --windowed --name "Timetable to Calendar ZJNU" gui_win.py
  ```
- Linux (one‑file binary; ensure Tk is installed):
  ```bash
  sudo apt-get update && sudo apt-get install -y python3-tk
  pyinstaller --noconfirm --noconsole --onefile --name "timetable-to-calendar-zjnu" gui_win.py
  ```

Notes

- Requires Python 3.10+.
- On Linux/macOS, ensure Tk is available (e.g., `python3-tk` on Debian/Ubuntu).
- Binaries are unsigned; first‑run prompts may appear on some systems.

## Safe Distribution (reduce AV/SmartScreen warnings)

- Windows
  - Sign the EXE with an EV Code Signing certificate (best) or standard Authenticode to build SmartScreen reputation.
  - Avoid packers/obfuscators (UPX already disabled); keep stable file names and embedded version info.
  - Optionally package as MSIX and sign, or publish via Microsoft Store for the smoothest install.
  - If flagged, submit the file to Microsoft for review: https://www.microsoft.com/wdsi/filesubmission
  - Provide SHA256 checksums so users can verify integrity:
    ```pwsh
    Get-FileHash "dist/Timetable to Calendar ZJNU.exe" -Algorithm SHA256
    ```
- macOS
  - Sign with Developer ID Application and notarize with Apple (`codesign` + `notarytool`), then staple.
  - Distribute the `.app` (or a signed `.dmg`) to avoid Gatekeeper blocks.
- Linux
  - Provide `.AppImage` or `.tar.gz` plus a detached signature (GPG or `cosign`) and published checksums.

These steps are optional for development, but recommended for sharing executables widely without false positives.

## License & Disclaimer

- MIT License — see [LICENSE](LICENSE).
  > Research prototype provided “as is.” Not affiliated with ZJNU.

<!-- Download link references -->

[win-dl]: https://github.com/Al-rimi/Timetable-to-Calendar/releases/download/v0.0.3/Timetable.to.Calendar.ZJNU.exe
[mac-dl]: https://github.com/Al-rimi/Timetable-to-Calendar/releases/download/v0.0.3/Timetable.to.Calendar.ZJNU.app.zip
[linux-dl]: https://github.com/Al-rimi/Timetable-to-Calendar/releases/download/v0.0.3/timetable-to-calendar-zjnu.tar.gz

## Debugging & Dev Tools

- Always‑on course summary (CLI): running `timetable_to_calendar_zjnu.py` prints a detailed breakdown of detected courses (day, sections, weeks, location, teacher). Use this to validate parsing.
- GUI inline edits: double‑click a cell in the table to edit Day/Session/Weeks/Name/Type/Location/Teacher. The ICS reflects your edits.
- Sorting: the table enforces Monday→Sunday order. If a day looks wrong, fix the “Day” cell; the row will re‑sort automatically.
- Term/Monday date: the GUI infers known terms (e.g., 2025‑2026‑1 ⇒ 2025‑09‑08) and prompts a date picker if unknown.
- Theme: Windows dark mode changes are detected at runtime; the UI adjusts automatically.

Tip: For deeper analysis, add prints in `timetable_to_calendar_zjnu.py` (e.g., around `extract_courses_from_table`) and run the CLI. The generated `.ics` is normalized with headers, CRLF line endings, and `DTSTAMP` for each event so you can diff cleanly.

## Testing & Debugging Tools

Two helper scripts live under `tools/` to validate parsing and ICS generation without the GUI.

- `tools/debug_extract.py`: Deep dive into a single PDF

  - What it does: prints detected header metadata, raw non-empty table cells per weekday, the block splits inside cells, and the final parsed courses list (table + outside items). Also shows extracted student name/ID and term.
  - Run (PowerShell):
    ```pwsh
    # Activate venv if you use one
    .\.venv\Scripts\Activate.ps1  # optional
    python tools/debug_extract.py "samples/AL RAIMI ABDULLAH(2025-2026-1)课表 EN.pdf"
    ```
  - Look for:
    - "-- Extracted --" section with Name/ID/Term
    - "-- Table cells (non-empty) --" with block breakdowns
    - "-- Parsed courses (table) --" lines showing day, periods, time spans, weeks, teacher, location

- `tools/smoke_test.py`: End-to-end ICS smoke test
  - What it does: parses a sample PDF, prints a concise course summary, and writes an `.ics` (floating time) under `samples/`.
  - Run (PowerShell):
    ```pwsh
    # Activate venv if you use one
    .\.venv\Scripts\Activate.ps1  # optional
    python tools/smoke_test.py
    ```
  - Expected output: a final line like `Wrote: samples/AL_RAIMI_ABDULLAH(2025-2026-1)课表_EN.smoke.ics exists: True size: <bytes>`

Tip: If parsing looks off, compare the raw cell dumps and the parsed courses to spot where a split/merge heuristic needs tuning.

## Packaging via pyproject (sdist/wheel)

You can build pip-installable artifacts using `pyproject.toml`.

```pwsh
# In a clean environment
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip build

# Build source distribution and wheel into dist/
python -m build

# (Optional) Install locally to test CLI entry points
pip install --force-reinstall dist\timetable_to_calendar_zjnu-*.whl

# Now you can run the scripts defined in pyproject:
zjnu-ics        # CLI
zjnu-ics-gui    # GUI
```

This uses `[project]` and `[project.scripts]` from `pyproject.toml`, keeping packaging metadata in one place.
