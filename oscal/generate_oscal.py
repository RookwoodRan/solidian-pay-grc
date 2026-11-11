#!/usr/bin/env python3
"""
Generates OSCAL-format artifacts from data/controls.yaml:
  - oscal/catalog.json      an OSCAL Catalog of Solidian Pay's unified controls
  - oscal/ssp-excerpt.json  a System Security Plan excerpt with
                             implemented-requirements pointing back at the catalog

This is the single generator for both files; do not hand-edit the JSON
outputs; edit data/controls.yaml and re-run this script.

SOC 2 mappings carry an additional 'soc2-category' prop so the catalog is
queryable by Trust Services Criteria category (Security / Availability /
Confidentiality / Processing Integrity / Privacy).

Usage: python3 oscal/generate_oscal.py
"""
import json
import os
import uuid
import datetime
import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTROLS_FILE = ROOT / "data" / "controls.yaml"
CATALOG_OUT = ROOT / "oscal" / "catalog.json"
SSP_OUT = ROOT / "oscal" / "ssp-excerpt.json"

NAMESPACE = "https://github.com/RookwoodRan/solidian-pay-grc"

FRAMEWORK_LABELS = {
    "soc2": "AICPA SOC 2 Trust Services Criteria",
    "iso27001": "ISO/IEC 27001:2022",
    "iso42001": "ISO/IEC 42001:2023",
    "nist_ai_rmf": "NIST AI RMF 1.0",
    "nist_csf": "NIST CSF 2.0",
}


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


def now_iso():
    """Timestamp for OSCAL metadata.

    Honours SOURCE_DATE_EPOCH (the reproducible-builds convention) so CI can
    regenerate the catalog and byte-compare it against the committed copy.
    Without it the output would differ on every run purely by timestamp, and a
    drift check could never distinguish a real change from the clock moving.
    """
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if epoch:
        return datetime.datetime.fromtimestamp(int(epoch), datetime.timezone.utc).isoformat()
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def det_uuid(seed: str) -> str:
    """Deterministic UUID5 so re-runs produce stable IDs (diff-friendly)."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{NAMESPACE}/{seed}"))


def load_controls():
    data = yaml.safe_load(CONTROLS_FILE.read_text())
    return data["controls"], data["organization"]


def build_control(c):
    control_id = c["id"].lower()
    props = [
        {"name": "control-type", "ns": NAMESPACE, "value": c["control_type"]},
        {"name": "owner", "ns": NAMESPACE, "value": c["owner"]},
        {"name": "domain", "ns": NAMESPACE, "value": c["domain"]},
        {"name": "implementation-status", "ns": NAMESPACE, "value": c["implementation_status"]},
        {"name": "control-maturity", "ns": NAMESPACE, "value": str(c["control_maturity"])},
        {"name": "evidence-maturity", "ns": NAMESPACE, "value": str(c["evidence_maturity"])},
    ]
    for fw, refs in c["frameworks"].items():
        for ref in refs or []:
            prop = {
                "name": "framework-mapping",
                "ns": NAMESPACE,
                "class": fw,
                "value": ref,
                "remarks": FRAMEWORK_LABELS[fw],
            }
            props.append(prop)
            if fw == "soc2":
                props.append({
                    "name": "soc2-category",
                    "ns": NAMESPACE,
                    "class": "soc2",
                    "value": tsc_category(ref),
                    "remarks": f"Trust Services Criteria category for {ref}",
                })

    control = {
        "id": control_id,
        "class": "solidianpay-control",
        "title": c["name"],
        "props": props,
        "links": [],
        "parts": [
            {
                "id": f"{control_id}_smt",
                "name": "statement",
                "prose": c["description"].strip(),
            },
            {
                "id": f"{control_id}_gdn",
                "name": "guidance",
                "prose": f"Evidence required: {c['evidence_required']}",
            },
        ],
    }
    if c.get("notes"):
        control["parts"].append(
            {"id": f"{control_id}_remarks", "name": "remarks", "prose": c["notes"]}
        )
    return control


def build_catalog(controls, org):
    by_domain = {}
    for c in controls:
        by_domain.setdefault(c["domain"], []).append(c)

    groups = []
    for domain, items in by_domain.items():
        group_id = domain.lower().replace(" ", "-").replace("&", "and").replace("--", "-")
        groups.append(
            {
                "id": group_id,
                "class": "domain",
                "title": domain,
                "controls": [build_control(c) for c in items],
            }
        )

    catalog = {
        "catalog": {
            "uuid": det_uuid("catalog"),
            "metadata": {
                "title": f"{org}: Unified Control Catalog",
                "last-modified": now_iso(),
                "version": "2.0.0",
                "oscal-version": "1.1.2",
                "remarks": (
                    "Fictional portfolio artifact. Controls are crosswalked to the AICPA "
                    "SOC 2 Trust Services Criteria across all five categories (Security, "
                    "Availability, Confidentiality, Processing Integrity, Privacy), and "
                    "to ISO/IEC 27001:2022, ISO/IEC 42001:2023, NIST AI RMF 1.0 and "
                    "NIST CSF 2.0; see props of class 'framework-mapping' on each "
                    "control for the crosswalk, and props named 'soc2-category' for the "
                    "Trust Services Criteria category each SOC 2 criterion belongs to. "
                    "A reference is recorded only where the control itself satisfies it; "
                    "controls are left unmapped against frameworks they do not address."
                ),
                "parties": [
                    {
                        "uuid": det_uuid("party-org"),
                        "type": "organization",
                        "name": org,
                    }
                ],
            },
            "groups": groups,
        }
    }
    return catalog


def build_ssp(controls, org, catalog_uuid):
    implemented_requirements = []
    for c in controls:
        control_id = c["id"].lower()
        implemented_requirements.append(
            {
                "uuid": det_uuid(f"ir-{control_id}"),
                "control-id": control_id,
                "description": c["description"].strip(),
                "props": [
                    {"name": "implementation-status", "ns": NAMESPACE, "value": c["implementation_status"]},
                    {"name": "control-maturity", "ns": NAMESPACE, "value": str(c["control_maturity"])},
                ],
                "responsible-roles": [
                    {"role-id": c["owner"].lower().replace(" ", "-").replace("/", "-")}
                ],
                "remarks": c["notes"] or "",
            }
        )

    ssp = {
        "system-security-plan": {
            "uuid": det_uuid("ssp"),
            "metadata": {
                "title": f"{org}: System Security Plan (Solidian Pay Platform)",
                "last-modified": now_iso(),
                "version": "2.0.0",
                "oscal-version": "1.1.2",
            },
            "import-profile": {"href": f"#{catalog_uuid}"},
            "system-characteristics": {
                "system-name": "Solidian Pay Platform",
                "description": (
                    "Digital payments, merchant risk, embedded finance, and AI-enabled "
                    "operations tooling. Fictional system for portfolio demonstration."
                ),
                "security-sensitivity-level": "moderate",
                "system-information": {
                    "information-types": [
                        {
                            "title": "Payment and Cardholder-Adjacent Data",
                            "confidentiality-impact": {"base": "fips-199-high"},
                            "integrity-impact": {"base": "fips-199-high"},
                            "availability-impact": {"base": "fips-199-high"},
                        },
                        {
                            "title": "AI Training and Inference Data",
                            "confidentiality-impact": {"base": "fips-199-moderate"},
                            "integrity-impact": {"base": "fips-199-moderate"},
                            "availability-impact": {"base": "fips-199-moderate"},
                        },
                        {
                            "title": "Personal Information of Customers and Merchants",
                            "confidentiality-impact": {"base": "fips-199-high"},
                            "integrity-impact": {"base": "fips-199-moderate"},
                            "availability-impact": {"base": "fips-199-moderate"},
                        },
                    ]
                },
                "status": {"state": "operational"},
            },
            "control-implementation": {
                "description": (
                    "Implemented requirements below are generated 1:1 from "
                    "data/controls.yaml and cross-reference the unified catalog."
                ),
                "implemented-requirements": implemented_requirements,
            },
        }
    }
    return ssp


def main():
    controls, org = load_controls()
    catalog = build_catalog(controls, org)
    catalog_uuid = catalog["catalog"]["uuid"]
    ssp = build_ssp(controls, org, catalog_uuid)

    CATALOG_OUT.write_text(json.dumps(catalog, indent=2) + "\n")
    SSP_OUT.write_text(json.dumps(ssp, indent=2) + "\n")

    n_controls = sum(len(g["controls"]) for g in catalog["catalog"]["groups"])
    print(f"Wrote {CATALOG_OUT}; {len(catalog['catalog']['groups'])} groups, {n_controls} controls")
    print(f"Wrote {SSP_OUT}; {len(ssp['system-security-plan']['control-implementation']['implemented-requirements'])} implemented-requirements")


if __name__ == "__main__":
    main()
