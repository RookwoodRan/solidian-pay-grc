#!/usr/bin/env python3
"""Render exports/*.csv as Markdown pages for GitHub Pages."""
import csv
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
        "framework-crosswalk.csv",
        "crosswalk.md",
        "Framework crosswalk",
        "Which control satisfies which clause. Use your browser's "
        "find to search any clause ID.",
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


if __name__ == "__main__":
    for page in PAGES:
        render(*page)
