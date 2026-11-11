#!/usr/bin/env python3
"""
Generates the Solidian Pay Compliance, Risk & AI Governance workbook from the
YAML source-of-truth files in /data. Do not hand-edit the .xlsx; edit the
YAML and re-run this script, then recalculate the output with LibreOffice (see
the README) so the formulas carry cached values.

SOC 2 mappings are broken out per Trust Services Criteria category
(CC/A/C/PI/P) on the dashboard and on the SOC 2 TSC Crosswalk sheet.

Usage: python3 workbook/generate_workbook.py
"""
import datetime
import pathlib

import yaml
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "workbook" / "Solidian_Pay_Compliance_Risk_AI_Governance_Suite.xlsx"

FONT_NAME = "Calibri"
HEADER_FILL = PatternFill("solid", fgColor="1F4E5F")
HEADER_FONT = Font(name=FONT_NAME, bold=True, color="FFFFFF", size=11)
TITLE_FONT = Font(name=FONT_NAME, bold=True, size=16, color="1F4E5F")
SECTION_FONT = Font(name=FONT_NAME, bold=True, size=11, color="1F4E5F")
BODY_FONT = Font(name=FONT_NAME, size=10)
NOTE_FONT = Font(name=FONT_NAME, italic=True, size=9, color="7F7F7F")
THIN = Side(style="thin", color="D9D9D9")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

HIGH_FILL = PatternFill("solid", fgColor="F4CCCC")
MED_FILL = PatternFill("solid", fgColor="FCE5CD")
LOW_FILL = PatternFill("solid", fgColor="D9EAD3")

# SOC 2 Trust Services Criteria categories, keyed by criterion prefix
TSC_CATEGORIES = [
    ("CC", "Security (Common Criteria)"),
    ("A1", "Availability"),
    ("C1", "Confidentiality"),
    ("PI1", "Processing Integrity"),
    ("P", "Privacy"),
]


def tsc_category(criterion: str) -> str:
    """Map a SOC 2 criterion (e.g. 'CC6.1', 'PI1.3', 'P4.2') to its category."""
    for prefix, label in [("CC", "Security (Common Criteria)"),
                          ("PI1", "Processing Integrity"),
                          ("A1", "Availability"),
                          ("C1", "Confidentiality")]:
        if criterion.startswith(prefix):
            return label
    if criterion.startswith("P"):
        return "Privacy"
    return ""


def load(name):
    return yaml.safe_load((DATA / name).read_text())


def style_header_row(ws, row, ncols):
    for col in range(1, ncols + 1):
        c = ws.cell(row=row, column=col)
        c.fill = HEADER_FILL
        c.font = HEADER_FONT
        c.alignment = Alignment(vertical="center", wrap_text=True)
        c.border = BORDER


def autofit(ws, widths):
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w


def write_table(ws, start_row, headers, rows):
    style_header_row(ws, start_row, len(headers))
    for j, h in enumerate(headers, start=1):
        ws.cell(row=start_row, column=j, value=h)
    for i, row in enumerate(rows, start=start_row + 1):
        for j, val in enumerate(row, start=1):
            c = ws.cell(row=i, column=j, value=val)
            c.font = BODY_FONT
            c.border = BORDER
            c.alignment = Alignment(vertical="top", wrap_text=True)
    return start_row + len(rows)


def join_mapping(refs):
    return "; ".join(refs) if refs else "None"


def main():
    controls_data = load("controls.yaml")
    controls = controls_data["controls"]
    org = controls_data["organization"]
    assets = load("assets.yaml")["assets"]
    ai_systems = load("ai-systems.yaml")["ai_systems"]
    risks = load("risks.yaml")["risks"]
    rubric = load("maturity-rubric.yaml")

    wb = Workbook()

    # ---------------- Cover Sheet ----------------
    ws = wb.active
    ws.title = "Cover Sheet"
    ws["B2"] = f"{org}"
    ws["B2"].font = TITLE_FONT
    ws["B3"] = "Compliance, Risk & AI Governance Suite"
    ws["B3"].font = Font(name=FONT_NAME, size=13, color="595959")
    ws["B5"] = (
        "**FICTIONAL PORTFOLIO ARTIFACT**; Solidian Pay is a fictional fintech company "
        "created by Rani Rookwood to demonstrate GRC and GRC-engineering skills. It is not "
        "a real organization. All data, personnel, and events in this suite are fictional."
    )
    ws["B5"].font = Font(name=FONT_NAME, italic=True, size=10, color="C00000")
    ws["B5"].alignment = Alignment(wrap_text=True)
    ws.merge_cells("B5:F5")
    ws.row_dimensions[5].height = 40

    fields = [
        ("Author", "Rani Rookwood; AI Trust & Safety / GRC & AI Governance"),
        ("Version", "2.0"),
        ("Date", datetime.date.today().isoformat()),
        ("Frameworks Mapped", "SOC 2 Trust Services Criteria (all five categories), ISO/IEC 27001:2022, ISO/IEC 42001:2023, NIST AI RMF 1.0, NIST CSF 2.0"),
        ("SOC 2 Scope", "Security (CC1-CC9), Availability (A1), Confidentiality (C1), Processing Integrity (PI1), Privacy (P1-P8)"),
        ("Companion Repo Layers", "This workbook is generated from /data; see /policy (OPA/Rego) and /oscal (OSCAL catalog + SSP) for the controls-as-code layer"),
        ("Contents", "Asset Inventory; AI System Inventory; Control Library; Risk Register; Risk Treatment Plan; Heat Map; Maturity Rubric; SOC 2 TSC Crosswalk; Certification Readiness Tracker; Dashboard"),
    ]
    r = 7
    for label, value in fields:
        ws.cell(row=r, column=2, value=label).font = Font(name=FONT_NAME, bold=True, size=10)
        c = ws.cell(row=r, column=3, value=value)
        c.font = BODY_FONT
        c.alignment = Alignment(wrap_text=True)
        ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=7)
        r += 1
    autofit(ws, [3, 18, 16, 16, 16, 16, 16])

    # ---------------- Asset Inventory ----------------
    ws = wb.create_sheet("Asset Inventory")
    headers = ["Asset ID", "Asset Name", "Description", "Category", "Owner", "Classification",
               "Threats", "Vulnerabilities", "Mapped Controls", "Inherent Risk", "Residual Risk"]
    rows = []
    for a in assets:
        rows.append([
            a["id"], a["name"], a["description"], a["category"], a["owner"], a["classification"],
            "; ".join(a["threats"]), "; ".join(a["vulnerabilities"]), ", ".join(a["controls"]),
            a["inherent_risk"], a["residual_risk"],
        ])
    write_table(ws, 1, headers, rows)
    autofit(ws, [10, 22, 40, 16, 16, 14, 30, 30, 22, 14, 14])
    ws.freeze_panes = "A2"

    # ---------------- AI System Inventory ----------------
    ws = wb.create_sheet("AI System Inventory")
    headers = ["AI System ID", "Name", "Purpose", "Model Type", "Risk Level", "Data Inputs",
               "Data Outputs", "Human Oversight", "Monitoring", "Third-Party?", "Lifecycle Stage",
               "Owner", "Mapped Controls", "Evidence Required"]
    rows = []
    for s in ai_systems:
        rows.append([
            s["id"], s["name"], s["purpose"], s["model_type"], s["risk_level"],
            "; ".join(s["data_inputs"]), "; ".join(s["data_outputs"]), s["human_oversight"],
            "; ".join(s["monitoring"]), "Yes" if s.get("third_party") else "No",
            s["lifecycle_stage"], s["owner"], ", ".join(s["controls"]),
            "; ".join(s["evidence_required"]),
        ])
    write_table(ws, 1, headers, rows)
    autofit(ws, [12, 22, 30, 20, 12, 26, 22, 26, 26, 12, 14, 16, 18, 30])
    ws.freeze_panes = "A2"

    # ---------------- Control Library ----------------
    # Columns: A id, B name, C desc, D domain, E type, F soc2, G iso27001,
    #          H iso42001, I ai rmf, J csf, K owner, L status, M ctl maturity,
    #          N evid maturity, O evidence, P notes
    ws = wb.create_sheet("Control Library")
    headers = ["Control ID", "Control Name", "Description", "Domain", "Control Type",
               "SOC 2 TSC", "ISO 27001:2022", "ISO 42001", "NIST AI RMF", "NIST CSF 2.0",
               "Owner", "Implementation Status", "Control Maturity", "Evidence Maturity",
               "Evidence Required", "Notes"]
    rows = []
    for c in controls:
        fw = c["frameworks"]
        rows.append([
            c["id"], c["name"], c["description"].strip(), c["domain"], c["control_type"],
            join_mapping(fw.get("soc2")), join_mapping(fw.get("iso27001")),
            join_mapping(fw.get("iso42001")), join_mapping(fw.get("nist_ai_rmf")),
            join_mapping(fw.get("nist_csf")),
            c["owner"], c["implementation_status"], c["control_maturity"], c["evidence_maturity"],
            c["evidence_required"], c.get("notes", ""),
        ])
    control_last_row = write_table(ws, 1, headers, rows)
    autofit(ws, [11, 28, 40, 18, 12, 20, 18, 16, 18, 16, 18, 16, 12, 12, 32, 28])
    ws.freeze_panes = "A2"

    # ---------------- Maturity Rubric ----------------
    ws = wb.create_sheet("Maturity Rubric")
    ws.cell(row=1, column=1, value="Control Maturity Rubric").font = Font(name=FONT_NAME, bold=True, size=12)
    ws.cell(row=1, column=5, value="Evidence Maturity Rubric").font = Font(name=FONT_NAME, bold=True, size=12)
    headers = ["Level", "Label", "Description"]
    for off, key in [(0, "control_maturity"), (4, "evidence_maturity")]:
        for j, h in enumerate(headers, start=1 + off):
            c = ws.cell(row=2, column=j, value=h)
            c.fill = HEADER_FILL
            c.font = HEADER_FONT
            c.border = BORDER
        for i, (level, info) in enumerate(rubric[key].items(), start=3):
            ws.cell(row=i, column=1 + off, value=level).font = BODY_FONT
            ws.cell(row=i, column=2 + off, value=info["label"]).font = BODY_FONT
            cell = ws.cell(row=i, column=3 + off, value=info["description"])
            cell.font = BODY_FONT
            cell.alignment = Alignment(wrap_text=True)
    autofit(ws, [8, 14, 50, 3, 8, 14, 50])
    for row in range(3, 8):
        ws.row_dimensions[row].height = 45

    # ---------------- Risk Register ----------------
    ws = wb.create_sheet("Risk Register")
    headers = ["Risk ID", "Asset/AI System", "Risk Description", "Inherent Likelihood", "Inherent Impact",
               "Inherent Score", "Residual Likelihood", "Residual Impact", "Residual Score",
               "Owner", "Mapped Controls"]
    rows = []
    for r_ in risks:
        rows.append([
            r_["id"], r_["asset"], r_["description"], r_["inherent_likelihood"], r_["inherent_impact"],
            None,
            r_["residual_likelihood"], r_["residual_impact"], None,
            r_["owner"], ", ".join(r_["controls"]),
        ])
    risk_last_row = write_table(ws, 1, headers, rows)
    for i in range(2, risk_last_row + 1):
        ws.cell(row=i, column=6, value=f"=D{i}*E{i}")
        ws.cell(row=i, column=9, value=f"=G{i}*H{i}")
    autofit(ws, [10, 16, 44, 12, 12, 12, 12, 12, 12, 22, 24])
    ws.freeze_panes = "A2"

    # ---------------- Risk Treatment Plan ----------------
    ws = wb.create_sheet("Risk Treatment Plan")
    headers = ["Risk ID", "Inherent Score", "Treatment Option", "Treatment Actions",
               "Owner", "Due Date", "Status", "Residual Score"]
    rows = []
    for r_ in risks:
        rows.append([
            r_["id"], r_["inherent_score"], r_["treatment"],
            "; ".join(r_["treatment_actions"]), r_["owner"], r_["due_date"], r_["status"],
            r_["residual_score"],
        ])
    write_table(ws, 1, headers, rows)
    autofit(ws, [10, 14, 16, 60, 22, 14, 14, 14])
    ws.freeze_panes = "A2"

    # ---------------- Heat Map Matrix ----------------
    ws = wb.create_sheet("Heat Map Matrix")
    ws.cell(row=1, column=1, value="Inherent Risk Heat Map (Impact x Likelihood)").font = Font(name=FONT_NAME, bold=True, size=12)
    ws.cell(row=2, column=1, value="Impact \\ Likelihood")
    ws.cell(row=2, column=1).font = HEADER_FONT
    ws.cell(row=2, column=1).fill = HEADER_FILL
    for j, lik in enumerate(range(1, 6), start=2):
        c = ws.cell(row=2, column=j, value=lik)
        c.font = HEADER_FONT
        c.fill = HEADER_FILL
    for i, impact in enumerate(range(5, 0, -1), start=3):
        c = ws.cell(row=i, column=1, value=impact)
        c.font = HEADER_FONT
        c.fill = HEADER_FILL
        for j, lik in enumerate(range(1, 6), start=2):
            formula = (f"=COUNTIFS('Risk Register'!D2:D{risk_last_row},{lik},"
                       f"'Risk Register'!E2:E{risk_last_row},{impact})")
            cell = ws.cell(row=i, column=j, value=formula)
            cell.font = BODY_FONT
            cell.border = BORDER
            cell.alignment = Alignment(horizontal="center")
            score = impact * lik
            cell.fill = HIGH_FILL if score >= 15 else (MED_FILL if score >= 8 else LOW_FILL)
    autofit(ws, [18, 8, 8, 8, 8, 8])

    # ---------------- Certification Readiness Tracker ----------------
    # Columns: A standard, B criterion, C tsc category, D control id, E control
    #          name, F evidence, G owner, H status, I ctl maturity, J evid maturity
    ws = wb.create_sheet("Certification Readiness Tracker")
    headers = ["Standard", "Clause/Criterion", "SOC 2 TSC Category", "Control ID", "Control Name",
               "Evidence Required", "Evidence Owner", "Implementation Status",
               "Control Maturity", "Evidence Maturity"]
    fw_names = {
        "soc2": "SOC 2", "iso27001": "ISO/IEC 27001:2022", "iso42001": "ISO/IEC 42001:2023",
        "nist_ai_rmf": "NIST AI RMF 1.0", "nist_csf": "NIST CSF 2.0",
    }
    rows = []
    for c in controls:
        for fw_key, fw_label in fw_names.items():
            for clause in c["frameworks"].get(fw_key) or []:
                rows.append([
                    fw_label, clause,
                    tsc_category(clause) if fw_key == "soc2" else "",
                    c["id"], c["name"], c["evidence_required"],
                    c["owner"], c["implementation_status"],
                    c["control_maturity"], c["evidence_maturity"],
                ])
    rows.sort(key=lambda r: (r[0], r[1], r[3]))
    cert_last_row = write_table(ws, 1, headers, rows)
    autofit(ws, [20, 16, 24, 12, 28, 36, 20, 18, 14, 14])
    ws.freeze_panes = "A2"

    # ---------------- SOC 2 TSC Crosswalk ----------------
    ws = wb.create_sheet("SOC 2 TSC Crosswalk")
    ws.cell(row=1, column=1, value="SOC 2 Trust Services Criteria: Crosswalk by Category").font = TITLE_FONT
    ws.merge_cells("A1:D1")
    ws.cell(row=2, column=1, value=(
        "Counts read live from the Certification Readiness Tracker. One line item = one "
        "criterion mapped to one control; a criterion satisfied by several controls counts once per control."
    )).font = NOTE_FONT
    ws.merge_cells("A2:D2")

    hdrs = ["TSC Category", "Crosswalk Rows", "Distinct Controls Contributing",
            "Avg Control Maturity"]
    for j, h in enumerate(hdrs, start=1):
        c = ws.cell(row=4, column=j, value=h)
        c.fill = HEADER_FILL
        c.font = HEADER_FONT
        c.border = BORDER
        c.alignment = Alignment(wrap_text=True, vertical="center")

    # distinct control counts computed in Python (no spilling array functions in LO)
    distinct_by_cat = {}
    for row in rows:
        if row[0] == "SOC 2":
            distinct_by_cat.setdefault(row[2], set()).add(row[3])

    r = 5
    for _, label in TSC_CATEGORIES:
        ws.cell(row=r, column=1, value=label).font = BODY_FONT
        ws.cell(row=r, column=2,
                value=f"=COUNTIFS('Certification Readiness Tracker'!C2:C{cert_last_row},A{r})"
                ).font = BODY_FONT
        ws.cell(row=r, column=3, value=len(distinct_by_cat.get(label, set()))).font = BODY_FONT
        ws.cell(row=r, column=4,
                value=f"=IFERROR(AVERAGEIFS('Certification Readiness Tracker'!I2:I{cert_last_row},"
                      f"'Certification Readiness Tracker'!C2:C{cert_last_row},A{r}),\"n/a\")"
                ).font = BODY_FONT
        for col in range(1, 5):
            ws.cell(row=r, column=col).border = BORDER
        r += 1
    ws.cell(row=r, column=1, value="TOTAL: SOC 2 crosswalk rows").font = SECTION_FONT
    ws.cell(row=r, column=2,
            value=f"=COUNTIF('Certification Readiness Tracker'!A2:A{cert_last_row},\"SOC 2\")"
            ).font = SECTION_FONT
    ws.cell(row=r, column=3, value=len({c for s in distinct_by_cat.values() for c in s})).font = SECTION_FONT
    autofit(ws, [32, 26, 28, 20])

    # ---------------- Dashboard ----------------
    ws = wb.create_sheet("Dashboard")
    ws.cell(row=1, column=1, value=f"{org}: Governance Posture Dashboard").font = TITLE_FONT
    ws.merge_cells("A1:D1")

    sections = [
        ("Scope", [
            ("Total Assets", f"=COUNTA('Asset Inventory'!A2:A{len(assets)+1})"),
            ("Total AI Systems", f"=COUNTA('AI System Inventory'!A2:A{len(ai_systems)+1})"),
            ("Total Controls", f"=COUNTA('Control Library'!A2:A{control_last_row})"),
            ("Total Risks Tracked", f"=COUNTA('Risk Register'!A2:A{risk_last_row})"),
        ]),
        ("Posture", [
            ("High Inherent Risks (score >= 15)", f"=COUNTIF('Risk Register'!F2:F{risk_last_row},\">=15\")"),
            ("Average Control Maturity", f"=AVERAGE('Control Library'!M2:M{control_last_row})"),
            ("Average Evidence Maturity", f"=AVERAGE('Control Library'!N2:N{control_last_row})"),
            ("Controls Not Yet Started", f"=COUNTIF('Control Library'!L2:L{control_last_row},\"Not Started\")"),
            ("Controls Fully Implemented", f"=COUNTIF('Control Library'!L2:L{control_last_row},\"Implemented\")"),
        ]),
        ("SOC 2 crosswalk by category", [
            (label, f"=COUNTIFS('Certification Readiness Tracker'!C2:C{cert_last_row},\"{label}\")")
            for _, label in TSC_CATEGORIES
        ] + [
            ("SOC 2 crosswalk rows (all categories)", f"=COUNTIF('Certification Readiness Tracker'!A2:A{cert_last_row},\"SOC 2\")"),
        ]),
        ("Other framework crosswalk", [
            ("ISO 27001:2022 crosswalk rows", f"=COUNTIF('Certification Readiness Tracker'!A2:A{cert_last_row},\"ISO/IEC 27001:2022\")"),
            ("ISO 42001:2023 crosswalk rows", f"=COUNTIF('Certification Readiness Tracker'!A2:A{cert_last_row},\"ISO/IEC 42001:2023\")"),
            ("NIST AI RMF 1.0 crosswalk rows", f"=COUNTIF('Certification Readiness Tracker'!A2:A{cert_last_row},\"NIST AI RMF 1.0\")"),
            ("NIST CSF 2.0 crosswalk rows", f"=COUNTIF('Certification Readiness Tracker'!A2:A{cert_last_row},\"NIST CSF 2.0\")"),
            ("Total crosswalk rows (all frameworks)", f"=COUNTA('Certification Readiness Tracker'!A2:A{cert_last_row})"),
        ]),
    ]

    r = 3
    for section_title, metrics in sections:
        ws.cell(row=r, column=1, value=section_title).font = SECTION_FONT
        r += 1
        ws.cell(row=r, column=1, value="Metric").font = HEADER_FONT
        ws.cell(row=r, column=1).fill = HEADER_FILL
        ws.cell(row=r, column=2, value="Value").font = HEADER_FONT
        ws.cell(row=r, column=2).fill = HEADER_FILL
        r += 1
        for label, formula in metrics:
            ws.cell(row=r, column=1, value=label).font = BODY_FONT
            c = ws.cell(row=r, column=2, value=formula)
            c.font = Font(name=FONT_NAME, bold=True, size=11, color="1F4E5F")
            r += 1
        r += 1
    autofit(ws, [40, 16])
    ws.cell(row=r, column=1, value=(
        "Note: this dashboard reads live from the sheets above via formulas; "
        "regenerating the workbook from /data keeps every number in sync."
    )).font = NOTE_FONT

    wb.save(OUT)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
