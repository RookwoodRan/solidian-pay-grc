#!/usr/bin/env python3
"""Export the control library and registers to CSV in exports/.

GitHub renders committed CSV files as a searchable, sortable table in the
browser, so these are the copies a reviewer can read without downloading the
workbook or cloning the repository. They are generated from data/*.yaml, the
same source as the workbook and the OSCAL catalog — not from the .xlsx — so
they cannot drift from it.

Usage: python3 scripts/export_csv.py
"""
from __future__ import annotations

import csv
import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "exports"

FRAMEWORK_LABELS = {
    "soc2": "SOC 2 TSC",
    "iso27001": "ISO/IEC 27001:2022",
    "iso42001": "ISO/IEC 42001:2023",
    "nist_ai_rmf": "NIST AI RMF 1.0",
    "nist_csf": "NIST CSF 2.0",
}

TSC_PREFIXES = [
    ("CC", "Security (Common Criteria)"),
    ("PI1", "Processing Integrity"),
    ("A1", "Availability"),
    ("C1", "Confidentiality"),
]


def tsc_category(criterion: str) -> str:
    for prefix, label in TSC_PREFIXES:
        if criterion.startswith(prefix):
            return label
    return "Privacy" if criterion.startswith("P") else ""


def load(name: str, key: str):
    return yaml.safe_load((DATA / name).read_text())[key]


def write(filename: str, header: list[str], rows: list[list]) -> None:
    path = OUT / filename
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
    print(f"  {path.relative_to(ROOT)} — {len(rows)} rows")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    controls = load("controls.yaml", "controls")
    assets = load("assets.yaml", "assets")
    ai_systems = load("ai-systems.yaml", "ai_systems")
    risks = load("risks.yaml", "risks")

    print("Writing CSV exports:")

    write(
        "control-library.csv",
        ["Control ID", "Name", "Domain", "Type", "Owner", "Status",
         "Control Maturity", "Evidence Maturity", "SOC 2 TSC", "ISO/IEC 27001:2022",
         "ISO/IEC 42001:2023", "NIST AI RMF 1.0", "NIST CSF 2.0",
         "Description", "Evidence Required", "Notes"],
        [[c["id"], c["name"], c["domain"], c["control_type"], c["owner"],
          c["implementation_status"], c["control_maturity"], c["evidence_maturity"],
          "; ".join(c["frameworks"]["soc2"]),
          "; ".join(c["frameworks"]["iso27001"]),
          "; ".join(c["frameworks"]["iso42001"]),
          "; ".join(c["frameworks"]["nist_ai_rmf"]),
          "; ".join(c["frameworks"]["nist_csf"]),
          " ".join(c["description"].split()),
          c["evidence_required"], c.get("notes") or ""]
         for c in controls],
    )

    crosswalk = []
    for c in controls:
        for key, label in FRAMEWORK_LABELS.items():
            for ref in c["frameworks"][key]:
                crosswalk.append([
                    label, ref, tsc_category(ref) if key == "soc2" else "",
                    c["id"], c["name"], c["domain"], c["owner"],
                    c["implementation_status"], c["control_maturity"],
                    c["evidence_maturity"],
                ])
    crosswalk.sort(key=lambda r: (r[0], r[1], r[3]))
    write(
        "framework-crosswalk.csv",
        ["Standard", "Clause / Criterion", "SOC 2 TSC Category", "Control ID",
         "Control Name", "Domain", "Owner", "Status", "Control Maturity",
         "Evidence Maturity"],
        crosswalk,
    )

    soc2_rows = [r for r in crosswalk if r[0] == "SOC 2 TSC"]
    summary = []
    for _, label in TSC_PREFIXES + [("P", "Privacy")]:
        matching = [r for r in soc2_rows if r[2] == label]
        if not matching:
            continue
        maturities = [r[8] for r in matching]
        summary.append([
            label,
            len(matching),
            len({r[1] for r in matching}),
            len({r[3] for r in matching}),
            round(sum(maturities) / len(maturities), 2),
        ])
    write(
        "soc2-tsc-crosswalk.csv",
        ["TSC Category", "Crosswalk Rows", "Distinct Criteria Referenced",
         "Distinct Controls Contributing", "Avg Control Maturity"],
        summary,
    )

    write(
        "risk-register.csv",
        ["Risk ID", "Description", "Linked Asset / System", "Owner",
         "Inherent Likelihood", "Inherent Impact", "Inherent Score",
         "Residual Likelihood", "Residual Impact", "Residual Score",
         "Treatment", "Status", "Due Date", "Controls", "Treatment Actions"],
        [[r["id"], " ".join(str(r.get("description", "")).split()),
          "; ".join(r.get("assets") or ([r["asset"]] if isinstance(r.get("asset"), str) else [])),
          r.get("owner", ""),
          r.get("inherent_likelihood", ""), r.get("inherent_impact", ""),
          r.get("inherent_score", ""), r.get("residual_likelihood", ""),
          r.get("residual_impact", ""), r.get("residual_score", ""),
          r.get("treatment", ""), r.get("status", ""), r.get("due_date", ""),
          "; ".join(r.get("controls") or []),
          "; ".join(r.get("treatment_actions") or [])]
         for r in risks],
    )

    write(
        "ai-system-inventory.csv",
        ["System ID", "Name", "Purpose", "Model Type", "Risk Level",
         "Human Oversight", "Third Party", "Lifecycle Stage", "Owner", "Controls"],
        [[s["id"], s["name"], s.get("purpose", ""), s.get("model_type", ""),
          s.get("risk_level", ""), s.get("human_oversight", ""),
          "Yes" if s.get("third_party") else "No", s.get("lifecycle_stage", ""),
          s.get("owner", ""), "; ".join(s.get("controls") or [])]
         for s in ai_systems],
    )

    write(
        "asset-inventory.csv",
        ["Asset ID", "Name", "Category", "Owner", "Classification",
         "Inherent Risk", "Residual Risk", "Controls"],
        [[a["id"], a["name"], a.get("category", ""), a.get("owner", ""),
          a.get("classification", ""), a.get("inherent_risk", ""),
          a.get("residual_risk", ""), "; ".join(a.get("controls") or [])]
         for a in assets],
    )


if __name__ == "__main__":
    main()
