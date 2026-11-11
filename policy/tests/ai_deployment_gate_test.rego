package solidianpay.ai_deployment_gate

import rego.v1

test_allow_high_risk_system_with_all_controls_met if {
	allow with input as {
		"system_id": "AI-002",
		"risk_level": "High",
		"human_oversight_defined": true,
		"fairness_assessment_completed": true,
		"fairness_assessment_age_days": 45,
		"model_card_published": true,
		"data_lineage_documented": true,
		"impact_assessment_completed": true,
		"impact_assessment_age_days": 30,
		"third_party": false,
	}
}

test_deny_high_risk_missing_fairness_assessment if {
	not allow with input as {
		"system_id": "AI-003",
		"risk_level": "High",
		"human_oversight_defined": true,
		"fairness_assessment_completed": false,
		"model_card_published": true,
		"data_lineage_documented": true,
		"impact_assessment_completed": true,
		"impact_assessment_age_days": 30,
		"third_party": false,
	}
}

test_deny_stale_fairness_assessment if {
	not allow with input as {
		"system_id": "AI-002",
		"risk_level": "High",
		"human_oversight_defined": true,
		"fairness_assessment_completed": true,
		"fairness_assessment_age_days": 220,
		"model_card_published": true,
		"data_lineage_documented": true,
		"impact_assessment_completed": true,
		"impact_assessment_age_days": 30,
		"third_party": false,
	}
}

test_deny_missing_risk_classification if {
	not allow with input as {"system_id": "AI-006", "human_oversight_defined": true}
}

test_deny_medium_risk_without_oversight if {
	not allow with input as {
		"system_id": "AI-004",
		"risk_level": "Medium",
		"human_oversight_defined": false,
	}
}

test_allow_low_risk_third_party_without_lineage if {
	allow with input as {
		"system_id": "AI-005",
		"risk_level": "Low",
		"human_oversight_defined": true,
		"third_party": true,
	}
}

test_deny_high_risk_third_party_missing_model_card if {
	not allow with input as {
		"system_id": "AI-004",
		"risk_level": "High",
		"human_oversight_defined": true,
		"fairness_assessment_completed": true,
		"fairness_assessment_age_days": 10,
		"model_card_published": false,
		"impact_assessment_completed": true,
		"impact_assessment_age_days": 30,
		"third_party": true,
	}
}

# CTL-038: AI system impact assessment gate

test_deny_high_risk_missing_impact_assessment if {
	not allow with input as {
		"system_id": "AI-001",
		"risk_level": "High",
		"human_oversight_defined": true,
		"fairness_assessment_completed": true,
		"fairness_assessment_age_days": 20,
		"model_card_published": true,
		"data_lineage_documented": true,
		"impact_assessment_completed": false,
		"third_party": false,
	}
}

test_deny_medium_risk_missing_impact_assessment if {
	not allow with input as {
		"system_id": "AI-004",
		"risk_level": "Medium",
		"human_oversight_defined": true,
		"third_party": true,
	}
}

test_deny_stale_impact_assessment if {
	not allow with input as {
		"system_id": "AI-002",
		"risk_level": "High",
		"human_oversight_defined": true,
		"fairness_assessment_completed": true,
		"fairness_assessment_age_days": 20,
		"model_card_published": true,
		"data_lineage_documented": true,
		"impact_assessment_completed": true,
		"impact_assessment_age_days": 400,
		"third_party": false,
	}
}

test_allow_medium_risk_with_current_impact_assessment if {
	allow with input as {
		"system_id": "AI-004",
		"risk_level": "Medium",
		"human_oversight_defined": true,
		"impact_assessment_completed": true,
		"impact_assessment_age_days": 90,
		"third_party": true,
	}
}
