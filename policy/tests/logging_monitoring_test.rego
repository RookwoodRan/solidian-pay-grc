package solidianpay.logging_monitoring

import rego.v1

test_allow_compliant_restricted_asset if {
	allow with input as {
		"asset_id": "AS-005",
		"classification": "Restricted",
		"logging_enabled": true,
		"log_forwarded_to_siem": true,
		"retention_days": 400,
	}
}

test_deny_logging_disabled_on_confidential if {
	not allow with input as {
		"asset_id": "AS-001",
		"classification": "Confidential",
		"logging_enabled": false,
		"log_forwarded_to_siem": true,
		"retention_days": 400,
	}
}

test_deny_not_forwarded_to_siem if {
	not allow with input as {
		"asset_id": "AS-002",
		"classification": "Confidential",
		"logging_enabled": true,
		"log_forwarded_to_siem": false,
		"retention_days": 400,
	}
}

test_deny_short_retention_on_restricted if {
	not allow with input as {
		"asset_id": "AS-003",
		"classification": "Restricted",
		"logging_enabled": true,
		"log_forwarded_to_siem": true,
		"retention_days": 90,
	}
}

test_allow_internal_asset_without_logging if {
	allow with input as {
		"asset_id": "AS-004",
		"classification": "Internal",
		"logging_enabled": false,
		"log_forwarded_to_siem": false,
		"retention_days": 30,
	}
}
