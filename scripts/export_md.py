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
    (
        "risk-register.csv",
        "risks.md",
        "Risk register",
        "Every tracked risk with inherent and residual scoring, "
        "owner, treatment and mapped controls. Generated from "
        "data/risks.yaml. For a visual rollup see the "
        "[risk heat map](risk-heat-map.md).",
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


# Same fill colors as the workbook's Heat Map Matrix sheet, so the
# Pages version and the downloadable workbook look like the same
# artifact, not two different color systems.
HEAT_MAP_COLORS = {
    "High": "#F4CCCC",
    "Medium": "#FCE5CD",
    "Low": "#D9EAD3",
}


def risk_level(score):
    """Same bands as the workbook: High >= 15, Medium >= 8, else Low."""
    if score >= 15:
        return "High"
    if score >= 8:
        return "Medium"
    return "Low"


def render_heat_map(csv_name, out_name, title, intro):
    """Render risk-heat-map.csv as a colored 5x5 Impact x Likelihood grid.

    Every cell is shaded by its score's risk level, whether or not a
    risk currently sits there, so the grid reads as the classic
    red/amber/green zones a reader expects from a heat map. Cells with
    risks in them show the count; a legend below the grid lists which
    risk IDs sit where, so detail moves out of the cells (where it was
    cramped and wrapped) into something scannable on its own line.
    """
    src = ROOT / "exports" / csv_name
    with src.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    # Columns: Impact, Likelihood, Score, Level, Risk Count, Risk IDs
    by_cell = {}
    for impact, likelihood, score, level, count, ids in (
        (r[0], r[1], r[2], r[3], int(r[4]), r[5]) for r in rows[1:]
    ):
        by_cell[(int(impact), int(likelihood))] = (int(score), count, ids)

    total = sum(c for c, _ in ((v[1], v[2]) for v in by_cell.values()))
    lines = [
        "---",
        f"title: {title}",
        "---",
        "",
        f"# {title}",
        "",
        intro,
        "",
        f"*{total} risks plotted by inherent likelihood and impact. "
        f"Source: `exports/{csv_name}`.*",
        "",
        '<table>',
        "<tr><th>Impact \\ Likelihood</th>"
        + "".join(f"<th>{n}</th>" for n in range(1, 6))
        + "</tr>",
    ]
    legend = []
    for impact in range(5, 0, -1):
        row = [f"<th>{impact}</th>"]
        for likelihood in range(1, 6):
            score, count, ids = by_cell[(impact, likelihood)]
            color = HEAT_MAP_COLORS[risk_level(score)]
            label = str(count) if count else ""
            row.append(
                f'<td style="background-color:{color}; '
                f'text-align:center;">{label}</td>'
            )
            if count:
                legend.append((score, impact, likelihood, ids))
        lines.append("<tr>" + "".join(row) + "</tr>")
    lines.append("</table>")

    lines += [
        "",
        "Score = Likelihood x Impact. **High** (score 15 or above), "
        "**Medium** (score 8 to 14), **Low** (below 8): same bands "
        "used in the downloadable workbook's Heat Map Matrix sheet.",
        "",
        "**Where each risk lands:**",
        "",
    ]
    for score, impact, likelihood, ids in sorted(legend, reverse=True):
        lines.append(
            f"- Impact {impact}, Likelihood {likelihood} "
            f"(score {score}): {cell(ids)}"
        )
    lines += [
        "",
        "For treatment plans and residual scoring per risk, see the "
        "[risk register](risks.md).",
    ]
    content = "\n".join(lines) + "\n"
    target = OUT / out_name
    target.write_text(content, encoding="utf-8", newline="\n")
    print(f"wrote docs/{out_name} ({total} risks)")


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
    render_heat_map(
        "risk-heat-map.csv",
        "risk-heat-map.md",
        "Risk heat map",
        "Inherent risk plotted by likelihood and impact. For "
        "residual scoring and treatment status per risk, see the "
        "[risk register](risks.md).",
    )
