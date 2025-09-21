# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and the versioning follows SemVer while we are in early prototype stage.

## [1.0.1] - 2025-09-22

Parsing, Windows metadata, and repeatable builds

- Parsing robustness:
  - Fixed continuation-row merging so multi-line fragments (Campus/Area/Building/Room/Teacher) attach to the correct course block. This resolves locations like "20-206软件实验室", "16-428" that previously degraded to partial values (e.g., just "Main").
  - Improved block parsing to reduce mis-association of teacher/location lines and to preserve Unicode consistently.
- Windows EXE metadata:
  - Added a generator `tools/generate_version_info.py` that reads `pyproject.toml` and emits `build/version_info.txt` consumed by PyInstaller.
  - Embedded Company, Product, Description, Version, Homepage (Comments), and Copyright into the EXE.
  - Updated `gui_win.spec` to reference the generated version resource and keep icon embedding.
- Build quality of life:
  - New PowerShell script `scripts/build.ps1` to create/upgrade a local venv, install deps (including `pyinstaller`), generate version info, and build via the spec.
  - Added VS Code tasks to run one-file/one-dir builds and a clean target.
  - README updated with short, copyable Windows build commands and task usage.
- Smart App Control guidance:
  - Documented options to reduce false positives (metadata, avoiding UPX, trying onedir) and recommended Authenticode signing for trusted distribution.

## [1.0.0] - 2025-09-21

Modernized Windows GUI and UX polish

- Multilingual UI (EN/中文/FR) with automatic language detection.
- Windows dark mode support with live switching at runtime; uses native title bar.
- Redesigned minimal layout: big “Choose PDF or Drag & Drop” button; filename hidden in favor of student name + term.
- Content‑based ICS naming: extracts student name and term from the PDF and writes “<Student Name> <Term>.ics”.
- Courses table enhancements:
  - Inline editing (Include, Day, Name, Type, Session, Location, Weeks, Teacher).
  - Monday→Sunday sorting and by period within each day.
  - Proportional column auto‑sizing so the entire table fits (no scrollbars).
- Footer actions: “Open folder” and “Copy” on the left; “Generate Calendar” on the right.
- “Copy” uses Windows clipboard CF_HDROP to share the generated `.ics` (paste directly into apps like WeChat). Shows a brief “Copied! Paste into anywhere” confirmation.
- “Generate ICS” renamed to “Generate Calendar” and stays disabled until a PDF is selected/dropped and analysis succeeds.

Packaging

- Windows build includes conversion module and assets in the bundle to fix a startup “does nothing” report when selecting a PDF (adds `timetable_to_calendar_zjnu` to `hiddenimports` and `assets/icon.ico` to `datas`).

Build

- Kept `gui_win.spec` minimal with `upx=False` to reduce antivirus false positives.
- README updated with build steps and safe distribution guidance.

## [v0.0.4] - 2025-09-20

Safer distribution

- Windows build: UPX disabled in `gui_win.spec` to reduce antivirus false positives.
- Simplified packaging assets: removed `gui_win_onedir.spec`, `scripts/sign-windows.ps1`, and `version_file.txt`; keep a single minimal spec.
- Documentation:
  - Restored a generic Downloads section pointing to Releases (no per‑OS direct links).
  - Consolidated Build section with one clear command per platform (Windows/macOS/Linux).
  - Added “Safe Distribution” guidance (SmartScreen/AV, Apple notarization, checksums).
  - Kept concise “Importing .ics” steps.
- Packaging (maintainer‑facing):
  - Added `pyproject.toml` with project metadata and entry points.
  - Added `publish.yml` for tag‑based PyPI publishing via trusted publishing (optional).
- Tooling: added `tools/smoke_test.py` for quick end‑to‑end verification (sample produced 174 events with correct headers/CRLF).
- No functional changes to ICS generation.

## [v0.0.3] - 2025-09-19

Multi‑platform builds and documentation overhaul

- CI builds for Windows/macOS/Linux using PyInstaller (download artifacts from Actions or Releases).
- README summarized and reorganized (Features, Quick start, Importing, Server‑side ICS, Requirements, Advanced notes).
- Importing guidance for Outlook (New vs Classic) added.
- “Server‑side ICS (ideal)” section: recommends a subscribe‑able ICS feed for automatic updates.

## [v0.0.2] - 2025-09-19

Added Windows GUI and usability improvements

- New Tkinter GUI (`gui_win.py`) with a simple layout:
  - Browse for PDF; drag-and-drop supported across the window (optional via `tkinterdnd2`).
  - Date input for “Week 1 Monday” with a small Pick date button and a preset “2025 1st Semester”.
  - Centered primary “Generate ICS” button.
  - Output panel logs a detailed per-course summary by default and shows the result path.
  - “Open .ics” and “Open folder” convenience buttons.
- Always-on detailed per-course summary in both CLI and GUI.
- README updated; PyInstaller instructions name the app “Timetable to Calendar ZJNU”.
- Minor UI polish and safer fallbacks when drag-and-drop is unavailable.

Continuous delivery & docs

- CI workflow added to build artifacts for Windows/macOS/Linux via PyInstaller.
- README reorganized with Quick start, Importing (including Outlook guidance), and a “Server-side ICS (ideal)” section explaining auto-updatable ICS feeds universities can host.

## [v0.0.1] - 2025-09-19

Initial prototype

- Parse ZJNU timetable PDFs (EN/CN) and export ICS.
- Recognize course markers (△ ★ ▲ ☆) and extract weeks/sections/teacher/location.
- Assemble multi-line titles; ignore PDF-only metadata lines.
- Map sections → exact times; generate Samsung/Google/Apple-friendly ICS.
- Keep in-table missing locations as “Not yet/未定”; outside use “Online/线上”.
- Place outside courses on Sunday (14:00–) in 1-hour slots per week.
- Add debug summaries via `TT_DEBUG=1`. (Replaced by always-on summaries in v0.0.2)

[Unreleased]

- CLI flags for non-interactive runs
- Extended location normalization and translations
- Unit tests for parsing edge cases
