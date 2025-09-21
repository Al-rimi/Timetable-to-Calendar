from pathlib import Path
from datetime import datetime

try:
  import tomllib  # Python 3.11+
except Exception:  # pragma: no cover
  import tomli as tomllib


def read_pyproject(pyproject_path: Path) -> dict:
  with pyproject_path.open('rb') as f:
    return tomllib.load(f)


def coalesce_company(authors: list[dict] | None) -> str:
  if not authors:
    return ""
  first = authors[0] or {}
  return str(first.get('name') or "")


def detect_license_name(project: dict) -> str:
  classifiers = project.get('classifiers') or []
  if isinstance(classifiers, list):
    for c in classifiers:
      if isinstance(c, str) and 'MIT License' in c:
        return 'MIT License'
  return 'All rights reserved'


def to_tuple_version(v: str) -> tuple[int, int, int, int]:
  parts = [p for p in v.split('.') if p.isdigit()]
  nums = [int(p) for p in parts[:3]]
  while len(nums) < 3:
    nums.append(0)
  nums.append(0)
  return tuple(nums[:4])  # type: ignore[return-value]


def build_version_info_content(meta: dict, product_name: str) -> str:
  project = meta.get('project', {})
  version = str(project.get('version') or '1.0.0')
  desc = str(project.get('description') or product_name)
  company = coalesce_company(project.get('authors'))
  homepage = (project.get('urls') or {}).get('Homepage') if isinstance(project.get('urls'), dict) else None
  year = datetime.now().year
  license_name = detect_license_name(project)
  copyright_line = f"Copyright (c) {year} {company}, {license_name}".strip(', ')
  filevers = to_tuple_version(version)
  prodvers = filevers
  lang_codepage = '040904B0'
  original_filename = f"{product_name}.exe"
  comments = homepage or ''

  template = (
    "VSVersionInfo(\n"
    "  ffi=FixedFileInfo(\n"
    "    filevers={filevers},\n"
    "    prodvers={prodvers},\n"
    "    mask=0x3f,\n"
    "    flags=0x0,\n"
    "    OS=0x4,\n"
    "    fileType=0x1,\n"
    "    subtype=0x0,\n"
    "    date=(0, 0)\n"
    "  ),\n"
    "  kids=[\n"
    "    StringFileInfo([\n"
    "      StringTable(\n"
    "        '{lang_codepage}',\n"
    "        [\n"
    "          StringStruct('CompanyName', '{company}'),\n"
    "          StringStruct('FileDescription', '{desc}'),\n"
    "          StringStruct('FileVersion', '{version}'),\n"
    "          StringStruct('InternalName', '{product_name}'),\n"
    "          StringStruct('LegalCopyright', '{copyright_line}'),\n"
    "          StringStruct('OriginalFilename', '{original_filename}'),\n"
    "          StringStruct('ProductName', '{product_name}'),\n"
    "          StringStruct('ProductVersion', '{version}'),\n"
    "          StringStruct('Comments', '{comments}')\n"
    "        ]\n"
    "      )\n"
    "    ]),\n"
    "    VarFileInfo([VarStruct('Translation', [1033, 1200])])\n"
    "  ]\n"
    ")\n"
  )
  return template.format(
    filevers=filevers,
    prodvers=prodvers,
    lang_codepage=lang_codepage,
    company=company.replace("'", "\'"),
    desc=desc.replace("'", "\'"),
    version=version,
    product_name=product_name.replace("'", "\'"),
    copyright_line=copyright_line.replace("'", "\'"),
    original_filename=original_filename,
    comments=(comments or '').replace("'", "\'"),
  )


def main() -> int:
  root = Path(__file__).resolve().parents[1]
  meta = read_pyproject(root / 'pyproject.toml')
  content = build_version_info_content(meta, 'Timetable to Calendar ZJNU')
  out_dir = root / 'build'
  out_dir.mkdir(parents=True, exist_ok=True)
  out_file = out_dir / 'version_info.txt'
  out_file.write_text(content, encoding='utf-8')
  print(f"Wrote version info → {out_file}")
  return 0


if __name__ == '__main__':
  raise SystemExit(main())
