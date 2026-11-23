#!/usr/bin/env python3
"""Render exports/*.csv as Markdown pages for GitHub Pages."""
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs"

PAGES = [
    (
        "control-library.csv",
        "controls.md",
        "Control library",
        "Every control with owner, status, maturity and framework "
        "mappings. Generated from data/controls.yaml.",
    ),
    (
        "soc2-tsc-crosswalk.csv",
        "soc2-coverage.md",
        "SOC 2 coverage",
        "Coverage and average maturity per Trust Services category.",
    ),
]


def cell(value):
    """Escape a CSV value so it is safe inside a Markdown table cell."""
    text = (value or "").replace("\r", " ").replace("\n", " ")
    return text.replace("|", "\\|").strip()


def render(csv_name, out_name, title, intro):
    """Convert one CSV export into a Markdown page with a table."""
    src = ROOT / "exports" / csv_name
    with src.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    header, body = rows[0], rows[1:]
    lines = [
        "---",
        f"title: {title}",
        "---",
        "",
        f"# {title}",
        "",
        intro,
        "",
        f"*{len(body)} rows. Source: `exports/{csv_name}`.*",
        "",
        "| " + " | ".join(cell(h) for h in header) + " |",
        "|" + "|".join("---" for _ in header) + "|",
    ]
    for row in body:
        lines.append("| " + " | ".join(cell(c) for c in row) + " |")
    content = "\n".join(lines) + "\n"
    target = OUT / out_name
    target.write_text(content, encoding="utf-8", newline="\n")
    print(f"wrote docs/{out_name} ({len(body)} rows)")


def slugify(text):
    """Make a kramdown-safe anchor id from a heading, e.g. for jump links."""
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower())
    return slug.strip("-")


def render_crosswalk(csv_name, out_name, title, intro):
    """Render framework-crosswalk.csv as one table per framework.

    The CSV is pre-sorted by framework (export_csv.py puts SOC 2 first,
    matching the column order used in control-library.csv). Splitting
    into sections with a jump list means a reader can go straight to
    one framework instead of scrolling past the others to find it.
    """
    src = ROOT / "exports" / csv_name
    with src.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    header, body = rows[0], rows[1:]
    # Standard is column 0; drop it per-section since every row in a
    # section already shares it.
    section_header = header[1:]

    sections = []
    for row in body:
        standard = row[0]
        if not sections or sections[-1][0] != standard:
            sections.append((standard, []))
        sections[-1][1].append(row[1:])

    jump_links = " · ".join(
        f"[{standard}](#{slugify(standard)})" for standard, _ in sections
    )

    lines = [
        "---",
        f"title: {title}",
        "---",
        "",
        f"# {title}",
        "",
        intro,
        "",
        f"**Jump to:** {jump_links}",
        "",
        f"*{len(body)} rows total across {len(sections)} frameworks. "
        f"Source: `exports/{csv_name}`.*",
    ]
    for standard, section_rows in sections:
        lines += [
            "",
            f"## {standard}",
            f"{{: #{slugify(standard)} }}",
            "",
            f"*{len(section_rows)} rows.*",
            "",
            "| " + " | ".join(cell(h) for h in section_header) + " |",
            "|" + "|".join("---" for _ in section_header) + "|",
        ]
        for row in section_rows:
            lines.append("| " + " | ".join(cell(c) for c in row) + " |")

    content = "\n".join(lines) + "\n"
    target = OUT / out_name
    target.write_text(content, encoding="utf-8", newline="\n")
    print(f"wrote docs/{out_name} ({len(body)} rows, {len(sections)} sections)")


if __name__ == "__main__":
    for page in PAGES:
        render(*page)
    render_crosswalk(
        "framework-crosswalk.csv",
        "crosswalk.md",
        "Framework crosswalk",
        "Which control satisfies which clause, grouped by framework. "
        "Jump to one below, or use your browser's find (Ctrl+F / "
        "Cmd+F) to search any clause ID.",
    )
