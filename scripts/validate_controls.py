#!/usr/bin/env python3
"""Validate the Solidian Pay control library.

Checks, in order:
  1. every framework reference is a real identifier in the published standard
  2. no control is left with zero framework mappings
  3. control IDs are unique and sequential
  4. every asset / AI-system / risk cross-reference resolves to a real control
  5. maturity and status values are within the allowed ranges
  6. no banned marketing or overclaiming language in the repository

Framework identifier sets below are transcribed from:
  ISO/IEC 27001:2022   clauses 4-10 and Annex A (93 controls)
  ISO/IEC 42001:2023   clauses 4-10 and Annex A (38 controls)
  AICPA Trust Services Criteria (2017, 2022 points of focus); 61 criteria
  NIST AI RMF 1.0      72 subcategories
  NIST CSF 2.0         106 subcategories

Only the identifiers are reproduced, not the text of the standards.

Exit code 0 if everything passes, 1 otherwise. Run from anywhere:
    python3 scripts/validate_controls.py
"""
from __future__ import annotations

import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

# --------------------------------------------------------------------------
# Valid identifier sets
# --------------------------------------------------------------------------

SOC2 = (
    {f"CC{group}.{n}" for group, count in
     [(1, 5), (2, 3), (3, 4), (4, 2), (5, 3), (6, 8), (7, 5), (8, 1), (9, 2)]
     for n in range(1, count + 1)}
    | {"A1.1", "A1.2", "A1.3"}
    | {"C1.1", "C1.2"}
    | {f"PI1.{n}" for n in range(1, 6)}
    | {"P1.1", "P2.1", "P3.1", "P3.2", "P4.1", "P4.2", "P4.3", "P5.1", "P5.2"}
    | {f"P6.{n}" for n in range(1, 8)}
    | {"P7.1", "P8.1"}
)

ISO27001_CLAUSES = {
    "4.1", "4.2", "4.3", "4.4", "5.1", "5.2", "5.3",
    "6.1.1", "6.1.2", "6.1.3", "6.2", "6.3",
    "7.1", "7.2", "7.3", "7.4", "7.5",
    "8.1", "8.2", "8.3", "9.1", "9.2", "9.3", "10.1", "10.2",
}
ISO27001_ANNEX = (
    {f"A.5.{n}" for n in range(1, 38)}    # A.5.1  - A.5.37  organizational
    | {f"A.6.{n}" for n in range(1, 9)}   # A.6.1  - A.6.8   people
    | {f"A.7.{n}" for n in range(1, 15)}  # A.7.1  - A.7.14  physical
    | {f"A.8.{n}" for n in range(1, 35)}  # A.8.1  - A.8.34  technological
)

ISO42001_CLAUSES = {
    "4.1", "4.2", "4.3", "4.4", "5.1", "5.2", "5.3",
    "6.1.1", "6.1.2", "6.1.3", "6.1.4", "6.2", "6.3",
    "7.1", "7.2", "7.3", "7.4", "7.5",
    "8.1", "8.2", "8.3", "8.4", "9.1", "9.2", "9.3", "10.1", "10.2",
}
ISO42001_ANNEX = {
    "A.2.2", "A.2.3", "A.2.4",
    "A.3.2", "A.3.3",
    "A.4.2", "A.4.3", "A.4.4", "A.4.5", "A.4.6",
    "A.5.2", "A.5.3", "A.5.4", "A.5.5",
    "A.6.1.2", "A.6.1.3",
    "A.6.2.2", "A.6.2.3", "A.6.2.4", "A.6.2.5", "A.6.2.6", "A.6.2.7", "A.6.2.8",
    "A.7.2", "A.7.3", "A.7.4", "A.7.5", "A.7.6",
    "A.8.2", "A.8.3", "A.8.4", "A.8.5",
    "A.9.2", "A.9.3", "A.9.4",
    "A.10.2", "A.10.3", "A.10.4",
}

AI_RMF = {
    "GOVERN 1.1", "GOVERN 1.2", "GOVERN 1.3", "GOVERN 1.4", "GOVERN 1.5",
    "GOVERN 1.6", "GOVERN 1.7", "GOVERN 2.1", "GOVERN 2.2", "GOVERN 2.3",
    "GOVERN 3.1", "GOVERN 3.2", "GOVERN 4.1", "GOVERN 4.2", "GOVERN 4.3",
    "GOVERN 5.1", "GOVERN 5.2", "GOVERN 6.1", "GOVERN 6.2",
    "MAP 1.1", "MAP 1.2", "MAP 1.3", "MAP 1.4", "MAP 1.5", "MAP 1.6",
    "MAP 2.1", "MAP 2.2", "MAP 2.3", "MAP 3.1", "MAP 3.2", "MAP 3.3",
    "MAP 3.4", "MAP 3.5", "MAP 4.1", "MAP 4.2", "MAP 5.1", "MAP 5.2",
    "MEASURE 1.1", "MEASURE 1.2", "MEASURE 1.3", "MEASURE 2.1", "MEASURE 2.2",
    "MEASURE 2.3", "MEASURE 2.4", "MEASURE 2.5", "MEASURE 2.6", "MEASURE 2.7",
    "MEASURE 2.8", "MEASURE 2.9", "MEASURE 2.10", "MEASURE 2.11",
    "MEASURE 2.12", "MEASURE 2.13", "MEASURE 3.1", "MEASURE 3.2",
    "MEASURE 3.3", "MEASURE 4.1", "MEASURE 4.2", "MEASURE 4.3",
    "MANAGE 1.1", "MANAGE 1.2", "MANAGE 1.3", "MANAGE 1.4", "MANAGE 2.1",
    "MANAGE 2.2", "MANAGE 2.3", "MANAGE 2.4", "MANAGE 3.1", "MANAGE 3.2",
    "MANAGE 4.1", "MANAGE 4.2", "MANAGE 4.3",
}

CSF = {
    "DE.AE-02", "DE.AE-03", "DE.AE-04", "DE.AE-06", "DE.AE-07", "DE.AE-08",
    "DE.CM-01", "DE.CM-02", "DE.CM-03", "DE.CM-06", "DE.CM-09",
    "GV.OC-01", "GV.OC-02", "GV.OC-03", "GV.OC-04", "GV.OC-05",
    "GV.OV-01", "GV.OV-02", "GV.OV-03", "GV.PO-01", "GV.PO-02",
    "GV.RM-01", "GV.RM-02", "GV.RM-03", "GV.RM-04", "GV.RM-05", "GV.RM-06",
    "GV.RM-07", "GV.RR-01", "GV.RR-02", "GV.RR-03", "GV.RR-04",
    "GV.SC-01", "GV.SC-02", "GV.SC-03", "GV.SC-04", "GV.SC-05", "GV.SC-06",
    "GV.SC-07", "GV.SC-08", "GV.SC-09", "GV.SC-10",
    "ID.AM-01", "ID.AM-02", "ID.AM-03", "ID.AM-04", "ID.AM-05", "ID.AM-07",
    "ID.AM-08", "ID.IM-01", "ID.IM-02", "ID.IM-03", "ID.IM-04",
    "ID.RA-01", "ID.RA-02", "ID.RA-03", "ID.RA-04", "ID.RA-05", "ID.RA-06",
    "ID.RA-07", "ID.RA-08", "ID.RA-09", "ID.RA-10",
    "PR.AA-01", "PR.AA-02", "PR.AA-03", "PR.AA-04", "PR.AA-05", "PR.AA-06",
    "PR.AT-01", "PR.AT-02", "PR.DS-01", "PR.DS-02", "PR.DS-10", "PR.DS-11",
    "PR.IR-01", "PR.IR-02", "PR.IR-03", "PR.IR-04",
    "PR.PS-01", "PR.PS-02", "PR.PS-03", "PR.PS-04", "PR.PS-05", "PR.PS-06",
    "RC.CO-03", "RC.CO-04", "RC.RP-01", "RC.RP-02", "RC.RP-03", "RC.RP-04",
    "RC.RP-05", "RC.RP-06",
    "RS.AN-03", "RS.AN-06", "RS.AN-07", "RS.AN-08", "RS.CO-02", "RS.CO-03",
    "RS.MA-01", "RS.MA-02", "RS.MA-03", "RS.MA-04", "RS.MA-05",
    "RS.MI-01", "RS.MI-02",
}

STATUSES = {"Implemented", "In Progress", "Not Started"}
TYPES = {"Preventive", "Detective", "Corrective"}

# Two language checks, deliberately scoped differently.
#
# STALE: artefacts of earlier revisions that must not survive anywhere: a
# dropped framework, an old version label, or a coverage claim the repository
# no longer makes.
STALE = re.compile(
    r"27" r"701|PIMS|v3\.0"
    r"|all 61|every criterion"
    r"|complete (?:SOC ?2|Trust Services|control set|coverage)"
    r"|full (?:SOC ?2|Trust Services) (?:coverage|compliance)"
    r"|consulting[- ]grade|enterprise[- ]grade",
    re.IGNORECASE,
)

# OVERCLAIM: phrases that would misrepresent what this repository is. These are
# only wrong in the project's own voice. Inside docs/rfi-rfp/ the same words are
# fictional procurement content spoken by Solidian Pay or a bidding vendor, and
# in the maturity rubric "audit-ready" is a definition of a maturity level: so
# those paths are scanned for STALE only.
OVERCLAIM = re.compile(
    r"audit[- ]ready|certified (?:to|against)|guarantee[sd]? certification"
    r"|we (?:are|were) certified|passed (?:our|the) (?:SOC ?2|audit)",
    re.IGNORECASE,
)
OWN_VOICE = {"README.md", "CHANGELOG.md", "docs/case-study.md"}

SCANNED_SUFFIXES = {".md", ".yaml", ".yml", ".py", ".json", ".rego"}


def load(name: str, key: str):
    return yaml.safe_load((DATA / name).read_text())[key]


def check_framework_refs(controls, fail):
    checks = [
        ("soc2", lambda r: r in SOC2),
        ("iso27001", lambda r: r in (ISO27001_ANNEX if r.startswith("A.") else ISO27001_CLAUSES)),
        ("iso42001", lambda r: r in (ISO42001_ANNEX if r.startswith("A.") else ISO42001_CLAUSES)),
        ("nist_ai_rmf", lambda r: r in AI_RMF),
        ("nist_csf", lambda r: r in CSF),
    ]
    for c in controls:
        for key, valid in checks:
            refs = c["frameworks"].get(key) or []
            if len(refs) != len(set(refs)):
                fail.append(f"{c['id']}: duplicate reference in {key}")
            for ref in refs:
                if not valid(ref):
                    fail.append(f"{c['id']}: '{ref}' is not a valid {key} identifier")
        if not any(c["frameworks"].values()):
            fail.append(f"{c['id']}: no framework mappings at all")


def check_control_shape(controls, fail):
    seen = set()
    for i, c in enumerate(controls, start=1):
        cid = c["id"]
        if cid in seen:
            fail.append(f"{cid}: duplicate control id")
        seen.add(cid)
        if cid != f"CTL-{i:03d}":
            fail.append(f"{cid}: out of sequence (expected CTL-{i:03d})")
        if c["implementation_status"] not in STATUSES:
            fail.append(f"{cid}: bad implementation_status '{c['implementation_status']}'")
        if c["control_type"] not in TYPES:
            fail.append(f"{cid}: bad control_type '{c['control_type']}'")
        for field in ("control_maturity", "evidence_maturity"):
            if not 1 <= c[field] <= 5:
                fail.append(f"{cid}: {field} {c[field]} outside 1-5")
        for field in ("name", "domain", "description", "owner", "evidence_required"):
            if not str(c.get(field, "")).strip():
                fail.append(f"{cid}: empty {field}")


def check_cross_references(controls, fail):
    control_ids = {c["id"] for c in controls}
    assets = load("assets.yaml", "assets")
    ai_systems = load("ai-systems.yaml", "ai_systems")
    risks = load("risks.yaml", "risks")
    asset_ids = {a["id"] for a in assets}
    ai_ids = {s["id"] for s in ai_systems}

    for collection, label in ((assets, "asset"), (ai_systems, "ai system"), (risks, "risk")):
        for item in collection:
            for ref in item.get("controls") or []:
                if ref not in control_ids:
                    fail.append(f"{label} {item['id']} references unknown control {ref}")

    for r in risks:
        linked = r.get("assets") or ([r["asset"]] if isinstance(r.get("asset"), str) else [])
        for ref in linked:
            if ref not in asset_ids | ai_ids:
                fail.append(f"risk {r['id']} references unknown asset/system {ref}")

    return len(assets), len(ai_systems), len(risks)


def check_language(fail):
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path.suffix not in SCANNED_SUFFIXES:
            continue
        if ".git" in path.parts or path.name == pathlib.Path(__file__).name:
            continue
        rel = path.relative_to(ROOT).as_posix()
        own_voice = rel in OWN_VOICE
        for lineno, line in enumerate(path.read_text(errors="ignore").splitlines(), 1):
            stale = STALE.search(line)
            if stale:
                fail.append(f"{rel}:{lineno}: stale wording '{stale.group(0)}'")
            if own_voice:
                over = OVERCLAIM.search(line)
                if over:
                    fail.append(f"{rel}:{lineno}: overclaim '{over.group(0)}'")


def main() -> int:
    controls = load("controls.yaml", "controls")
    fail: list[str] = []

    check_framework_refs(controls, fail)
    check_control_shape(controls, fail)
    n_assets, n_ai, n_risks = check_cross_references(controls, fail)
    check_language(fail)

    rows = sum(len(v or []) for c in controls for v in c["frameworks"].values())
    soc2_used = {r for c in controls for r in c["frameworks"]["soc2"]}
    no_ai = [c["id"] for c in controls
             if not c["frameworks"]["nist_ai_rmf"] and not c["frameworks"]["iso42001"]]

    print(f"controls {len(controls)} | assets {n_assets} | AI systems {n_ai} | risks {n_risks}")
    print(f"crosswalk rows {rows} | SOC 2 criteria referenced {len(soc2_used)}/{len(SOC2)}")
    print(f"controls with no AI-framework mapping: {len(no_ai)} (intentional)")

    if fail:
        print(f"\n{len(fail)} problem(s):", file=sys.stderr)
        for problem in fail:
            print(f"  - {problem}", file=sys.stderr)
        return 1

    print("\nall checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
