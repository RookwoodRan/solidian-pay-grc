# Case Study: Rebuilding a Unified Compliance, Risk & AI Governance Framework as Code

**Rani Rookwood**

## Background

In April 2026 I published a workbook-based GRC portfolio artifact for a fictional fintech company. It mapped eight controls to ISO/IEC 27001 and ISO/IEC 42001, modeled risk, tracked AI systems, and simulated an RFI/RFP vendor-selection lifecycle for an ISO 42001 certification partner. It was a reasonable demonstration of GRC analysis; but it was analysis alone: a static spreadsheet, one control library duplicated across two mapped frameworks, no code, and no way to prove the numbers stayed consistent as the model grew.

Since then I've been building GRC-engineering skill specifically, treating governance artifacts as data and code rather than documents, and working with OPA/Rego, OSCAL, and infrastructure-as-code patterns. This rebuild, "Solidian Pay," is that skill applied back onto the original concept: same fictional-fintech premise, same commitment to realistic depth, but built as a small governance-engineering system instead of a spreadsheet; and anchored on SOC 2, the framework service organizations are most often actually audited against.

## What changed

**Source of truth moved from spreadsheet cells to structured data.** `data/controls.yaml`, `data/assets.yaml`, `data/ai-systems.yaml`, and `data/risks.yaml` are now the only place control status, ownership, and maturity ratings live. The workbook and the OSCAL catalog are both *generated* from these files by scripts in `workbook/` and `oscal/`; so a control's status can never drift between "what the spreadsheet says" and "what the catalog says," because there's only one place it's written.

**SOC 2 became the anchor, mapped across all five categories.** The original mapped SOC 2 opportunistically; whichever criteria happened to fit controls designed around ISO clauses. That is the common failure mode in GRC portfolios: Security criteria get attention and the other four categories get a token reference. Closing those gaps meant designing controls that genuinely did not exist before:

- **Processing Integrity had no controls at all.** For a payments company this is the most consequential gap imaginable; completeness and accuracy of transaction processing is the core service commitment. `CTL-035` now covers input validation and file-completeness checks at ingestion, automated exception queues, daily reconciliation between the processing ledger and settlement records, and authorized output distribution.
- **Competence and accountability (CC1.4/CC1.5)** were unmapped; `CTL-030` covers background screening, competence criteria, role-based security and AI training, and the disciplinary process.
- **The entire CC2 series (communication and information)** was unmapped; `CTL-031` covers internal communication of control responsibilities and external communication of service commitments, processing quality objectives, and the channel for reporting failures.
- **Physical access, secure disposal, malware protection and business-disruption mitigation** (CC6.4, CC6.5, CC6.8, CC9.1) were unmapped; `CTL-032`, `CTL-033`, `CTL-034` and `CTL-037`.
- **Fraud risk (CC3.3)** was unmapped; `CTL-036`, which is also where the AI fraud scoring model appears as both a control and a source of risk.

The control library grew from 8 controls to 39.

**Every mapping was verified against the published standard, and the bad ones were removed.** This is the part I'd want to talk about in an interview, because it's where the first draft was weakest. I wrote the initial crosswalk from knowledge rather than from the source texts, and when I went back through ISO/IEC 42001:2023, ISO/IEC 27001:2022, the Trust Services Criteria, NIST AI RMF 1.0 and NIST CSF 2.0 line by line, the first draft did not survive contact:

- **References that don't exist.** The draft cited an ISO 42001 "clause 6.4" on two controls. There is no clause 6.4; Planning ends at 6.3. It also used `A.6.2` and `A.6.3` as if they were Annex A controls; they're section headings, and the controls beneath them are `A.6.2.2` through `A.6.2.8`.
- **Real references attached to the wrong control.** ISO 42001 clause 8.4 is AI system impact assessment, and it was cited on access control, privileged access, change management and vendor oversight; none of which perform an impact assessment. ISO 27001 `A.5.7` is threat intelligence, and it was doing duty as a risk-assessment control in three places. NIST AI RMF `GOVERN 1.6` is the AI system inventory, and it was mapped to internal audit.
- **Mappings that were simply padding.** Access control and privileged access management carried AI RMF references. Neither control has an AI-specific function. They now carry none.

The rule I settled on, and applied to every row: **a framework reference is recorded only where the control description itself satisfies that clause, control or criterion.** If I can't point at the sentence, the mapping comes out. That removed coverage in a few places; the AI drift-monitoring control no longer claims a Processing Integrity criterion, and the encryption control no longer claims C1.1; and the crosswalk is more defensible for it.

**Verifying the mappings exposed two missing controls.** Both were real gaps, not bookkeeping:

- **`CTL-038` AI System Impact Assessment.** ISO 42001's Annex A.5 series and clauses 6.1.4/8.4 require assessing an AI system's consequences for individuals, groups and society. Nothing in the library did that; which meant the single requirement that most distinguishes an AI management system from an information security one had no owner. It now has one, and it's linked to every high- and medium-risk AI system in the inventory.
- **`CTL-039` Secure Development Lifecycle.** ISO 27001 `A.8.25`–`A.8.29` cover secure development, application security requirements, secure architecture, secure coding and security testing. For a payments company shipping its own platform, that absence was conspicuous.

**A controls-as-code layer exists.** Four control domains (access control, secure configuration, AI deployment risk-gating, and logging/monitoring) are expressed as OPA/Rego policies with unit test coverage. The AI deployment gate mechanically enforces ISO/IEC 42001 and NIST AI RMF requirements (risk classification present, human oversight defined for medium/high-risk systems, a *current* fairness assessment for high-risk systems, a published model card, documented data lineage) before an AI system is allowed to ship; the admission-control pattern from platform engineering, applied to AI governance.

**An OSCAL catalog and SSP excerpt exist.** `oscal/generate_oscal.py` emits an OSCAL 1.1.2 control catalog with each control carrying its full framework crosswalk as structured props, SOC 2 criteria additionally tagged by Trust Services Criteria category, and a System Security Plan excerpt with one implemented-requirement per control. OSCAL is the machine-readable control format this repository can generate and validate; it is not the structure a SOC 2 attestation takes, and the README says so.

**The RFI/RFP procurement lifecycle was rebuilt under new names and a corrected timeline.** The vendor in the original scenario is now "Epictetus Assurance, Ltd.," headquartered away from my own city to keep the fictional artifact clearly separated from my real identity. The RFI, RFP, and vendor responses preserve the certification-independence reasoning from the original; the part I was proudest of.

## What this demonstrates

- SOC 2 control design across all five Trust Services Criteria categories, including the Processing Integrity controls a payments company actually lives or dies by, rather than Security-only coverage with the rest left thin
- Crosswalk discipline: building a multi-framework mapping against the published standards, removing references that don't survive scrutiny, and treating a gap in the mapping as evidence of a gap in the control set
- Applying GRC-engineering practice (single source of truth, generated artifacts, policy-as-code, OSCAL) to a governance program rather than treating "engineering" and "GRC" as separate skill tracks
- AI governance specifically: risk-tiering, impact assessment, human oversight design, fairness/drift monitoring, transparency requirements, and third-party AI oversight, mapped to both ISO/IEC 42001 and NIST AI RMF
- Realistic procurement governance: RFI/RFP development, evaluation-criteria design, and correctly reasoning through certification-body independence constraints
- Writing governance code that is actually tested (`opa test`, spreadsheet formula recalculation with zero errors) rather than shipped unverified

## What this is not

It models control design and maintenance. It does not test operating effectiveness: there are no sampled populations, no test workpapers, no exception write-ups, and no evidence artifacts. A control-level evidence and testing layer is the natural next iteration, and `CTL-038` was built partly with that in mind. PCI DSS, which a real payments company would carry alongside SOC 2, is out of scope.

## Outcome

The result is a small but complete governance-engineering system: one data layer, three generated artifact types (workbook, OSCAL catalog, policy decisions), and a procurement-governance narrative sitting alongside it. It's still a fictional exercise; but it's built the way I'd actually want to build a real one, and every number in it can be regenerated from the data.
