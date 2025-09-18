# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and the versioning follows SemVer while we are in early prototype stage.

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
