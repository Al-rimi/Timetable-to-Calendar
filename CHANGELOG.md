# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and the versioning follows SemVer while we are in early prototype stage.

## [v0.0.4] - 2025-09-20

Packaging hardening and AV/SmartScreen guidance

- Windows build: disabled UPX packing to reduce antivirus false positives.
- Embedded Windows version resource (`version_file.txt`) in the EXE to improve file metadata and reputation.
- README: added a “Security/AV notes (Windows)” section with SmartScreen steps and signing recommendations.
- Docs: improved downloads layout and added platform-specific import instructions.

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
