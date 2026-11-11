# Solidian Pay — Compliance, Risk & AI Governance Suite

[![CI](https://github.com/RookwoodRan/solidian-pay-grc/actions/workflows/ci.yml/badge.svg)](https://github.com/RookwoodRan/solidian-pay-grc/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> **Fictional portfolio artifact.** Solidian Pay Financial Technologies, Inc. and Epictetus Assurance, Ltd. are fictional companies created by [Rani Rookwood](https://github.com/RookwoodRan) to demonstrate GRC and GRC-engineering skills. Nothing in this repository describes a real organization, and no control status, risk score, or evidence claim reflects an actual audit.

This repository models a unified GRC and AI-governance program for a fictional payments company, "Solidian Pay." It pairs a **SOC 2 control set spanning all five Trust Services Criteria categories** with ISO/IEC 27001, ISO/IEC 42001 and NIST mappings, and backs the whole thing with a controls-as-code layer — policy-as-code, an OSCAL catalog, and a generated workbook, all built from one source of truth.

## Review this in ten minutes

Nothing here needs to be cloned or downloaded — every table renders in the browser.

1. Read the fictional-scope note above, then open **[`exports/control-library.csv`](exports/control-library.csv)** — all 39 controls, their owners, status, maturity and full crosswalk, rendered by GitHub as a sortable table.
2. Open **[`exports/framework-crosswalk.csv`](exports/framework-crosswalk.csv)** and use GitHub's search box to find any clause — try `A.6.2.4`, `PI1.2` or `MAP 3.5` — to see which control satisfies it.
3. Skim **[`exports/soc2-tsc-crosswalk.csv`](exports/soc2-tsc-crosswalk.csv)** for coverage and average maturity per Trust Services category.
4. Read Section 7 of **[`docs/rfi-rfp/03-vendor-rfi-response.md`](docs/rfi-rfp/03-vendor-rfi-response.md)** — the certification-body independence reasoning.
5. Skim the `notes:` fields in `data/controls.yaml` for what is deliberately **not** finished: one control is Not Started and fourteen are In Progress.

To go deeper: `data/controls.yaml` is the source of truth, `policy/rego/ai_deployment_gate.rego` is the policy-as-code gate, and the Actions tab shows CI validating every framework reference on each push.

## What's here

| Path | What it is |
|---|---|
| `data/` | Source of truth — YAML files for the control library, asset inventory, AI system inventory, risk register, and maturity rubric. **Every other artifact in this repo is generated from these files.** |
| `exports/` | CSV views of the control library, crosswalk and registers, generated from `data/`. GitHub renders these as sortable tables, so they are the fastest way to read the content in a browser. |
| `scripts/` | `validate_controls.py` (checks every framework reference against the published identifier sets and verifies cross-references) and `export_csv.py` |
| `policy/rego/` | OPA/Rego policies that enforce a subset of controls as executable code (access control, secure configuration, an AI-deployment risk gate, logging/monitoring) |
| `policy/tests/` | `opa test` unit tests for every policy |
| `oscal/` | An OSCAL 1.1.2 control catalog and a System Security Plan excerpt, generated from `data/controls.yaml` |
| `workbook/` | The Excel workbook (asset inventory, AI inventory, control library, risk register, heat map, SOC 2 TSC crosswalk, certification-readiness tracker, live dashboard) — generated from `data/` |
| `docs/rfi-rfp/` | A complete RFI → RFP → vendor-response procurement lifecycle for selecting an ISO/IEC 42001 certification-body partner |
| `docs/case-study.md` | The narrative write-up of this project |
| `.github/workflows/` | CI: validates the crosswalk, runs the policy tests, and fails if the committed generated artifacts are stale |
| `CHANGELOG.md` | What changed between version 1.0 and this version |

## SOC 2: mapped across all five categories

The control library is crosswalked to the AICPA Trust Services Criteria across every category, not just Security:

| TSC category | Example controls |
|---|---|
| **Security (Common Criteria, CC1–CC9)** | Governance & policy, personnel competence, communication of commitments, risk assessment, fraud risk, monitoring & deficiency reporting, logical & physical access, malware protection, change management, vendor risk |
| **Availability (A1)** | Capacity management against committed SLOs, environmental protections, backup and tested recovery |
| **Confidentiality (C1)** | Data classification and confidential-information handling, secure disposal of media |
| **Processing Integrity (PI1)** | Transaction processing integrity & daily reconciliation, input validation, exception queues, output distribution authorization |
| **Privacy (P1–P8)** | Privacy notice & consent, data subject access and correction, PII inventory/minimization/retention, third-party disclosure & cross-border transfer, complaint handling |

Processing Integrity matters disproportionately here: for a payments company, completeness and accuracy of transaction processing *is* the core service commitment, so `CTL-035` (transaction processing integrity & reconciliation) sits alongside the security controls rather than being an afterthought.

## Other frameworks mapped

Alongside SOC 2, each control maps — where genuinely applicable — to:

- **ISO/IEC 27001:2022** (management-system clauses and Annex A controls)
- **ISO/IEC 42001:2023** (AI management system clauses and Annex A controls)
- **NIST AI RMF 1.0** (GOVERN / MAP / MEASURE / MANAGE)
- **NIST CSF 2.0**

39 controls produce 327 crosswalk rows in total — rows in a mapping table, not 327 distinct controls. See the `Certification Readiness Tracker` and `SOC 2 TSC Crosswalk` sheets in the workbook, or `oscal/catalog.json`, for the full crosswalk.

**A reference is recorded only where the control description itself satisfies that clause, control or criterion.** Controls are deliberately left unmapped against frameworks they do not genuinely address — the access-control and vulnerability-management controls carry no ISO 42001 or AI RMF references, because neither has an AI-specific function. Padding a crosswalk is easy; defending one line by line is the actual skill.

## Scope and limitations

- **This is a design and mapping artifact, not an audit.** It models how a control environment would be documented and maintained. It contains no operating-effectiveness testing, no sampled evidence, and no auditor's opinion.
- **The OSCAL SSP excerpt is not a SOC 2 deliverable.** A SOC 2 report comprises management's system description, management's assertion, and a CPA firm's opinion. OSCAL is used here because it is the machine-readable control format this repository can generate and validate; it is not the structure an attestation takes.
- **PCI DSS is out of scope.** Solidian Pay is modelled as a payments company, and a real one would carry PCI DSS obligations alongside SOC 2. Those are not modelled here.
- **Maturity and status values are illustrative.** They are set to reflect a plausible mid-maturity program, including gaps — one control is Not Started and fourteen are In Progress.

## Regenerating the artifacts

Requires Python 3.11+ with `pyyaml` and `openpyxl`, [OPA](https://www.openpolicyagent.org/docs/latest/#running-opa), and LibreOffice for the workbook recalculation step.

```bash
pip install pyyaml openpyxl

# Validate the control library before anything else
python3 scripts/validate_controls.py

# OSCAL catalog + SSP excerpt
python3 oscal/generate_oscal.py

# CSV exports
python3 scripts/export_csv.py

# Workbook, then recalculate so the 78 formulas carry cached values
python3 workbook/generate_workbook.py
soffice --headless --calc --convert-to xlsx:"Calc MS Excel 2007 XML" \
  --outdir workbook/recalc \
  workbook/Solidian_Pay_Compliance_Risk_AI_Governance_Suite.xlsx
mv workbook/recalc/*.xlsx workbook/ && rmdir workbook/recalc

# Policy tests
opa test policy/ -v
```

CI runs the validation, the policy tests, and a check that regenerating from `data/` reproduces exactly what is committed — so a stale export or a hand-edited catalog fails the build.

## Skills demonstrated

- SOC 2 control design across all five Trust Services Criteria categories, including Processing Integrity controls specific to payment processing and reconciliation
- Multi-framework crosswalking (SOC 2, ISO 27001, ISO 42001, NIST AI RMF, NIST CSF) maintained consistently as the control set grows, with every reference traceable to the published text of the standard
- AI governance: risk-tiering, impact assessment, human oversight design, fairness/drift monitoring, transparency, third-party AI oversight
- Controls-as-code with OPA/Rego, including a policy-based AI deployment gate
- OSCAL-formatted control catalog and SSP generation
- Risk modeling and heat-mapping (inherent/residual scoring)
- Vendor risk management and procurement governance (RFI/RFP lifecycle with certification-independence safeguards)
- Spreadsheet/dashboard engineering with live formulas over a structured data layer
- CI that validates governance data the way a build validates code: every framework reference checked against the published identifier sets, policies unit-tested, and generated artifacts proven to match their source

## License

[MIT](LICENSE). The control library, policies and generators are free to reuse. Clause and criterion identifiers from ISO/IEC 27001, ISO/IEC 42001, the AICPA Trust Services Criteria and the NIST frameworks are cited for mapping only; the standards' text is not reproduced here.
