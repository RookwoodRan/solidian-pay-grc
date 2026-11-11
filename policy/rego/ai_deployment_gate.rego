# Solidian Pay — AI Deployment Gate policy-as-code
# The flagship control-as-code artifact: enforces ISO/IEC 42001 and NIST AI RMF
# requirements as an automated gate before an AI system may ship to production.
#
# Maps to: CTL-014 (AI Inventory & Risk Classification), CTL-015 (AI Risk
# Assessment), CTL-016 (Human Oversight), CTL-017 (Transparency), CTL-020
# (Data Quality & Governance for AI), CTL-038 (AI System Impact Assessment)
# Frameworks: ISO/IEC 42001 6.1.2/6.1.3/6.1.4/8.2/8.4/A.5.2-A.5.5/A.6.2.4/A.7.4/A.7.5/A.8.2
#             NIST AI RMF MAP 1.1/1.5/2.3/3.5/5.1/5.2, MEASURE 2.3/2.6/2.9/2.11, GOVERN 1.6/3.2
#
# Input shape: a proposed AI system deployment record, e.g.
# {
#   "system_id": "AI-002",
#   "risk_level": "High",
#   "human_oversight_defined": true,
#   "fairness_assessment_completed": true,
#   "fairness_assessment_age_days": 45,
#   "model_card_published": true,
#   "data_lineage_documented": true,
#   "third_party": false
# }

package solidianpay.ai_deployment_gate

import rego.v1

default allow := false

allow if {
	count(deny_reason) == 0
}

# CTL-014: every system must carry a risk classification before deployment
deny_reason contains msg if {
	not input.risk_level
	msg := sprintf("AI system %s has no risk classification — deployment blocked (CTL-014)", [input.system_id])
}

# CTL-016: High and Medium risk systems must have human oversight defined
deny_reason contains msg if {
	input.risk_level in {"High", "Medium"}
	not input.human_oversight_defined == true
	msg := sprintf("AI system %s (%s risk) requires a defined human-oversight model before deployment (CTL-016)", [input.system_id, input.risk_level])
}

# CTL-015: High-risk systems must have a completed, current fairness/robustness assessment
deny_reason contains msg if {
	input.risk_level == "High"
	not input.fairness_assessment_completed == true
	msg := sprintf("AI system %s is High risk but has no completed fairness/robustness assessment (CTL-015)", [input.system_id])
}

deny_reason contains msg if {
	input.risk_level == "High"
	input.fairness_assessment_completed == true
	input.fairness_assessment_age_days > 180
	msg := sprintf("AI system %s fairness assessment is %d days old — exceeds 180-day currency window (CTL-015)", [input.system_id, input.fairness_assessment_age_days])
}

# CTL-017: High-risk systems affecting customers must publish a model card
deny_reason contains msg if {
	input.risk_level == "High"
	not input.model_card_published == true
	msg := sprintf("AI system %s is High risk and requires a published model card (CTL-017)", [input.system_id])
}

# CTL-020: High-risk internally-trained systems must have documented data lineage
deny_reason contains msg if {
	input.risk_level == "High"
	not input.third_party == true
	not input.data_lineage_documented == true
	msg := sprintf("AI system %s is High risk and internally trained — data lineage must be documented before deployment (CTL-020)", [input.system_id])
}

# CTL-038: High and Medium risk systems require a current AI system impact
# assessment. ISO/IEC 42001 clause 8.4 requires impact assessments at planned
# intervals and when significant changes are proposed; a deployment is a
# significant change, so a stale assessment does not satisfy the gate.
deny_reason contains msg if {
	input.risk_level in {"High", "Medium"}
	not input.impact_assessment_completed == true
	msg := sprintf("AI system %s (%s risk) requires a completed AI system impact assessment before deployment (CTL-038)", [input.system_id, input.risk_level])
}

deny_reason contains msg if {
	input.risk_level in {"High", "Medium"}
	input.impact_assessment_completed == true
	input.impact_assessment_age_days > 365
	msg := sprintf("AI system %s impact assessment is %d days old — exceeds 365-day currency window (CTL-038)", [input.system_id, input.impact_assessment_age_days])
}
