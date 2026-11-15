#!/usr/bin/env python3
"""Validate skill layout, frontmatter, and example banners.

No third-party dependencies. Run from anywhere:

    python3 scripts/check_skills.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
EXAMPLES = ROOT / "examples"
MAX_LINES = 500
MAX_DESCRIPTION = 1024
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REQUIRED_HEADINGS = (
    "## When to use",
    "## Verify before you report",
    "## False positives",
)
README_SKILLS_START = "<!-- skills-table:start -->"
README_SKILLS_END = "<!-- skills-table:end -->"


class Finder:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def err(self, message: str) -> None:
        self.errors.append(message)


def parse_frontmatter(text: str, where: str, finder: Finder) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        finder.err(f"{where}: frontmatter must start at the first line")
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        finder.err(f"{where}: unterminated frontmatter")
        return {}, text
    raw = text[4:end]
    body = text[end + 5 :]
    data: dict = {}
    lines = raw.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if line[0] in " \t":
            finder.err(f"{where}: unexpected indent in frontmatter: {line!r}")
            i += 1
            continue
        if ":" not in line:
            finder.err(f"{where}: bad frontmatter line: {line!r}")
            i += 1
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value in {">-", ">", "|", "|-"}:
            i += 1
            chunk: list[str] = []
            while i < len(lines) and (lines[i].startswith("  ") or lines[i].strip() == ""):
                chunk.append("" if lines[i].strip() == "" else lines[i][2:])
                i += 1
            if value.startswith(">"):
                parts = [part.strip() for part in chunk if part.strip()]
                data[key] = " ".join(parts)
            else:
                data[key] = "\n".join(chunk).strip()
            continue
        if value == "":
            i += 1
            nested: dict[str, str] = {}
            while i < len(lines) and lines[i].startswith("  "):
                item = lines[i].strip()
                if ":" not in item:
                    finder.err(f"{where}: bad nested line: {item!r}")
                    i += 1
                    continue
                nested_key, nested_value = item.split(":", 1)
                nested[nested_key.strip()] = nested_value.strip().strip("\"'")
                i += 1
            data[key] = nested
            continue
        data[key] = value.strip("\"'")
        i += 1
    return data, body


def check_skill(skill_dir: Path, finder: Finder) -> str | None:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        finder.err(f"{skill_dir}: missing SKILL.md")
        return None
    text = skill_md.read_text(encoding="utf-8")
    line_count = text.count("\n") + (0 if text.endswith("\n") else 1)
    if line_count > MAX_LINES:
        finder.err(f"{skill_md.relative_to(ROOT)}: {line_count} lines exceeds {MAX_LINES}")
    meta, body = parse_frontmatter(text, str(skill_md.relative_to(ROOT)), finder)
    name = meta.get("name")
    description = meta.get("description")
    if not isinstance(name, str) or not NAME_RE.fullmatch(name):
        finder.err(f"{skill_md.relative_to(ROOT)}: name must match {NAME_RE.pattern}")
    elif name != skill_dir.name:
        finder.err(
            f"{skill_md.relative_to(ROOT)}: name {name!r} does not match directory {skill_dir.name!r}"
        )
    if not isinstance(description, str) or not description.strip():
        finder.err(f"{skill_md.relative_to(ROOT)}: description is required")
    else:
        if len(description) > MAX_DESCRIPTION:
            finder.err(
                f"{skill_md.relative_to(ROOT)}: description is {len(description)} chars "
                f"(max {MAX_DESCRIPTION})"
            )
        if "Use when" not in description:
            finder.err(f"{skill_md.relative_to(ROOT)}: description must say when to use the skill")
    for heading in REQUIRED_HEADINGS:
        if heading not in body:
            finder.err(f"{skill_md.relative_to(ROOT)}: missing heading {heading!r}")
    if "\r" in text:
        finder.err(f"{skill_md.relative_to(ROOT)}: CRLF line endings")
    return name if isinstance(name, str) else None


def check_examples(finder: Finder) -> None:
    if not EXAMPLES.is_dir():
        finder.err("examples/ is missing")
        return
    vulnerable = sorted(EXAMPLES.glob("*/vulnerable.*"))
    if not vulnerable:
        finder.err("examples/: no vulnerable.* fixtures found")
    for path in vulnerable:
        text = path.read_text(encoding="utf-8")
        if "INTENTIONALLY VULNERABLE" not in text.splitlines()[0] and "INTENTIONALLY VULNERABLE" not in text[:400]:
            finder.err(f"{path.relative_to(ROOT)}: missing INTENTIONALLY VULNERABLE banner")
        secure = list(path.parent.glob("secure.*"))
        notes = path.parent / "NOTES.md"
        if not secure:
            finder.err(f"{path.parent.relative_to(ROOT)}: missing secure counterpart")
        if not notes.is_file():
            finder.err(f"{path.parent.relative_to(ROOT)}: missing NOTES.md")


def check_readme_index(names: list[str], finder: Finder) -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    start = readme.find(README_SKILLS_START)
    end = readme.find(README_SKILLS_END)
    if start < 0 or end < 0 or end < start:
        finder.err("README.md: missing skills-table markers")
        return
    block = readme[start:end]
    for name in names:
        if f"`{name}`" not in block:
            finder.err(f"README.md: skills table is missing `{name}`")


def main() -> int:
    finder = Finder()
    if not SKILLS.is_dir():
        finder.err("skills/ is missing")
        print("\n".join(finder.errors), file=sys.stderr)
        return 1
    names: list[str] = []
    for skill_dir in sorted(path for path in SKILLS.iterdir() if path.is_dir()):
        name = check_skill(skill_dir, finder)
        if name:
            names.append(name)
    if len(names) < 8:
        finder.err(f"expected at least 8 skills, found {len(names)}")
    check_examples(finder)
    check_readme_index(names, finder)
    if finder.errors:
        print(f"{len(finder.errors)} check(s) failed:", file=sys.stderr)
        for item in finder.errors:
            print(f"  - {item}", file=sys.stderr)
        return 1
    print(f"ok: {len(names)} skills, examples, and README index")
    return 0


if __name__ == "__main__":
    sys.exit(main())
