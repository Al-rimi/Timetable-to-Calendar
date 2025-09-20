import os, sys
# Add project root to sys.path so local modules are importable when running from tools/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from timetable_to_calendar_zjnu import (
    extract_tables, merge_main_table, merge_continuation_rows,
    set_active_type_map, extract_courses_from_table, extract_outside_courses,
    summarize_courses, build_ics,
)

PDF = r"samples/AL RAIMI ABDULLAH(2025-2026-1)课表 EN.pdf"
MON = "2025-09-08"

all_tables = extract_tables(PDF, strategy="lines")
headers, rows, meta, _notes, is_cn = merge_main_table(all_tables, collapse_newlines=False)
rows = merge_continuation_rows(headers, rows)
set_active_type_map(use_chinese=is_cn)
courses = extract_courses_from_table(headers, rows, preserve_newlines=True) + extract_outside_courses(meta)
print(summarize_courses(courses, is_cn))
ics_path = os.path.join("samples", "AL_RAIMI_ABDULLAH(2025-2026-1)课表_EN.smoke.ics")
build_ics(courses, monday_date=MON, output_path=ics_path, tz_mode="floating", chinese=is_cn)
print(f"Wrote: {ics_path} exists: {os.path.exists(ics_path)} size: {os.path.getsize(ics_path) if os.path.exists(ics_path) else 0}")
