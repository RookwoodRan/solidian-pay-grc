---
title: Solidian Pay GRC
---

# Solidian Pay: Compliance, Risk and AI Governance

> **Fictional portfolio artifact.** Solidian Pay Financial Technologies, Inc. is a fictional company created to demonstrate GRC and GRC-engineering skills. Nothing here describes a real organization or a real audit.

A unified GRC and AI-governance program for a fictional payments company: 39 controls crosswalked to SOC 2, ISO 27001, ISO 42001, NIST AI RMF and NIST CSF 2.0, all generated from one YAML source of truth and validated in CI.

## Start here (ten minutes)
- [Control library](controls.md): every control, owner, status and maturity
- [Framework crosswalk](crosswalk.md): find any clause and see which control satisfies it, grouped by framework
- [SOC 2 coverage](soc2-coverage.md): coverage per Trust Services category
- [Risk register](risks.md): every risk with inherent/residual scoring, owner and treatment
- [Risk heat map](risk-heat-map.md): inherent risk by likelihood and impact
- [Case study](case-study.md): the narrative write-up
- [Procurement lifecycle](rfi-rfp/index.md): the RFI, RFP and vendor responses for selecting a certification body

## Reference data
- [Asset inventory](assets.md): every tracked asset with owner, classification and mapped controls
- [AI system inventory](ai-systems.md): every AI system with risk level, human oversight and mapped controls
- [Maturity rubric](maturity-rubric.md): what each maturity score (1 to 5) actually means

## What this demonstrates
- Multi-framework crosswalking where every mapping is defensible line by line
- GRC engineering practices at the design layer: one source of truth, generated artifacts, validated references, and CI that fails on drift
- Policy-as-code: OPA/Rego policies with unit tests, plus an OSCAL catalog
- AI governance: risk tiering, human oversight, and a policy-based deployment gate

## Scope
This is a design and mapping artifact, not an audit or a deployed system. See the [case study](case-study.md) for the reasoning.

**Possible next iteration:** deploy a small slice of Solidian Pay with automated evidence collection.

[View the repository](https://github.com/RookwoodRan/solidian-pay-grc) · [More of my work](https://github.com/RookwoodRan)