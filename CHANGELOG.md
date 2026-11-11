# Changelog

## 2.0: October 2026

A full rebuild. Version 1.0 was a single spreadsheet; this version is a small governance-engineering system generated from structured data.

**Structure**

- `data/*.yaml` is now the single source of truth. The workbook and the OSCAL artifacts are generated from it, so control status and maturity cannot drift between artifacts.
- Added a policy-as-code layer: OPA/Rego policies with unit tests for access control, secure configuration, logging/monitoring, and an AI deployment gate.
- Added an OSCAL 1.1.2 control catalog and System Security Plan excerpt, each control carrying its framework crosswalk as structured properties.

**Control library**

- Grew from 8 controls to 39.
- SOC 2 became the anchoring framework, mapped across all five Trust Services Criteria categories rather than Security alone. Closing the gaps added controls for transaction processing integrity and reconciliation, personnel competence, internal and external communication of commitments, physical and environmental security, secure disposal, endpoint and malware protection, fraud risk, and business-disruption mitigation.
- Added `CTL-038` AI System Impact Assessment and `CTL-039` Secure Development Lifecycle, both of which closed real gaps found while verifying the crosswalk.

**Crosswalk accuracy**

- Every framework reference was verified against the published text of ISO/IEC 42001:2023, ISO/IEC 27001:2022, the AICPA Trust Services Criteria, NIST AI RMF 1.0 and NIST CSF 2.0.
- Removed references that do not exist in the standards, references attached to controls that do not satisfy them, and mappings that were padding.
- Adopted the rule that a reference is recorded only where the control description itself satisfies that clause, control or criterion. Controls are left unmapped against frameworks they do not genuinely address.

**Narrative**

- Both fictional companies were renamed, and the certification-body vendor was relocated away from the author's own city.
- The RFI/RFP procurement lifecycle was rebuilt with a corrected timeline, keeping the certification-body independence reasoning from 1.0.
- Added an explicit scope-and-limitations section: this is a control design and mapping artifact, not an audit, and it contains no operating-effectiveness testing.

## 1.0: April 2026

Initial publication. A single Excel workbook for a fictional fintech company: eight controls mapped to ISO/IEC 27001 and ISO/IEC 42001, an asset inventory, an AI system inventory, a risk register with inherent and residual scoring, a certification-readiness tracker, and an RFI/RFP vendor-selection lifecycle for an ISO 42001 certification partner.
