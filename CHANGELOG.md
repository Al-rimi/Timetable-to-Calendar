# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and the versioning follows SemVer while we are in early prototype stage.

## [v0.0.1] - 2025-09-19

Initial prototype

- Parse ZJNU timetable PDFs (EN/CN) and export ICS.
- Recognize course markers (△ ★ ▲ ☆) and extract weeks/sections/teacher/location.
- Assemble multi-line titles; ignore PDF-only metadata lines.
- Map sections → exact times; generate Samsung/Google/Apple-friendly ICS.
- Keep in-table missing locations as “Not yet/未定”; outside use “Online/线上”.
- Place outside courses on Sunday (14:00–) in 1-hour slots per week.
- Add debug summaries via `TT_DEBUG=1`.

[Unreleased]

- CLI flags for non-interactive runs
- Extended location normalization and translations
- Unit tests for parsing edge cases
