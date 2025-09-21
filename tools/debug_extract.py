import os
import sys
from pathlib import Path
from datetime import datetime

# Local imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import timetable_to_calendar_zjnu as core  # type: ignore


def main(pdf_path: str):
    print(f"PDF: {pdf_path}")
    tables = core.extract_tables(pdf_path, strategy="lines")
    header = core.merge_main_table(tables, collapse_newlines=False)
    if not header or not header[0]:
        print("No header detected.")
        return
    headers, rows, meta, notes, is_chinese = header
    # Merge continuation rows to attach Campus/Area/Teacher fragments to the correct cells
    try:
        rows = core.merge_continuation_rows(headers, rows)
    except Exception:
        pass
    print(f"Header cols: {len(headers)} | Chinese: {is_chinese}")
    print("-- Metadata lines (top) --")
    for i, line in enumerate(meta[:20], 1):
        print(f"{i:02d}: {line}")
    print("-- Notes (bottom) --")
    for i, line in enumerate(notes[:10], 1):
        print(f"{i:02d}: {line}")

    # Name/ID/Term extraction
    info_meta = core.extract_student_info(meta)
    info_pdf = core.extract_student_info_from_pdf(pdf_path, meta)
    term = core.extract_term_from_content(pdf_path, meta)
    print("-- Extracted --")
    print(f"Name(meta): {info_meta.get('name')}")
    print(f"Name(pdf):  {info_pdf.get('name')}")
    print(f"ID:         {info_pdf.get('id') or info_meta.get('id')}")
    print(f"Term:       {term}")

    # Dump raw table non-empty cells per day with block splits
    def _detect_days(headers):
        cn_day_map = {
            "周一": "Mon", "星期一": "Mon",
            "周二": "Tue", "星期二": "Tue",
            "周三": "Wed", "星期三": "Wed",
            "周四": "Thu", "星期四": "Thu",
            "周五": "Fri", "星期五": "Fri",
            "周六": "Sat", "星期六": "Sat",
            "周日": "Sun", "星期日": "Sun",
        }
        days = []
        for idx, h in enumerate(headers):
            hh_raw = (h or "").strip()
            hh = hh_raw.lower()
            if hh in ("mon","tue","wed","thu","fri","sat","sun"):
                days.append((idx, hh_raw if hh_raw in ("Mon","Tue","Wed","Thu","Fri","Sat","Sun") else hh_raw))
            else:
                for key, eng in cn_day_map.items():
                    if key in hh_raw:
                        days.append((idx, eng))
                        break
        return days

    print("-- Table cells (non-empty) --")
    days = _detect_days(headers)
    for r_i, row in enumerate(rows, 1):
        sec_text = (row[1] or "").strip() if len(row) > 1 else ""
        for c_idx, day in days:
            if c_idx < len(row):
                cell = row[c_idx] or ""
                if cell.strip():
                    print(f"[row {r_i:02d} sec={sec_text:>2}] {day}:")
                    print(cell)
                    try:
                        blocks = core.split_blocks_smart(cell)
                    except Exception:
                        blocks = []
                    if blocks:
                        print(f"  -> blocks({len(blocks)}):")
                        for bi, bl in enumerate(blocks, 1):
                            try:
                                print(f"     [{bi}] {' | '.join(bl)}")
                            except Exception:
                                print(f"     [{bi}] {bl}")

    # Parse courses and backfill teachers
    core.set_active_type_map(use_chinese=is_chinese)
    courses_tbl = core.extract_courses_from_table(headers, rows, preserve_newlines=True)
    try:
        core._backfill_teachers(courses_tbl)
    except Exception:
        pass
    courses_meta = core.extract_outside_courses(meta)
    print(f"Courses parsed (table): {len(courses_tbl)} | (outside): {len(courses_meta)} | total: {len(courses_tbl)+len(courses_meta)}")

    # Detailed parsed output for table courses
    print("-- Parsed courses (table) --")
    for i, c in enumerate(courses_tbl, 1):
        day = c.get('day')
        name = c.get('name')
        ctype = c.get('type')
        tchr = (c.get('teacher') or '').strip()
        loc = (c.get('location') or '').strip()
        periods = c.get('periods') or []
        pspan = f"{min(periods)}-{max(periods)}" if periods else "-"
        tspan = ""
        if periods:
            ts = core.SECTION_TIMES.get(min(periods))
            te = core.SECTION_TIMES.get(max(periods))
            if ts and te:
                tspan = f"{ts[0]}-{te[1]}"
        weeks = c.get('weeks') or []
        condensed = core._condense_weeks(weeks)
        print(f"- [{i:02d}] {day} | {name} | {ctype} | periods={periods} ({pspan}) {tspan} | weeks={weeks} ({condensed}) | teacher={tchr} | loc={loc}")

    # Outside-of-table courses
    if courses_meta:
        print("-- Parsed courses (outside) --")
        for i, c in enumerate(courses_meta, 1):
            name = c.get('name')
            ctype = c.get('type')
            tchr = (c.get('teacher') or '').strip()
            loc = (c.get('location') or '').strip()
            weeks = c.get('weeks') or []
            condensed = core._condense_weeks(weeks)
            print(f"- [O{i:02d}] {name} | {ctype} | weeks={weeks} ({condensed}) | teacher={tchr} | loc={loc}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/debug_extract.py <path-to-pdf>")
        sys.exit(1)
    main(sys.argv[1])
