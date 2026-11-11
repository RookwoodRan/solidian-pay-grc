# Solidian Pay — Logging & Monitoring policy-as-code
# Maps to: CTL-010 (Logging & Security Monitoring)
# Frameworks: SOC 2 CC7.2 | ISO 27001 A.8.15/A.8.16 | ISO 42001 A.6.2.8 | NIST CSF DE.CM-01/DE.CM-09
#
# Input shape: an asset record, e.g.
# {
#   "asset_id": "AS-005",
#   "classification": "Restricted",
#   "logging_enabled": true,
#   "log_forwarded_to_siem": true,
#   "retention_days": 400
# }

package solidianpay.logging_monitoring

import rego.v1

default allow := false

allow if {
	count(deny_reason) == 0
}

# All Confidential/Restricted assets must have logging enabled
deny_reason contains msg if {
	input.classification in {"Restricted", "Confidential"}
	not input.logging_enabled == true
	msg := sprintf("asset %s classified %s must have logging enabled (CTL-010)", [input.asset_id, input.classification])
}

# All Confidential/Restricted assets must forward logs to central SIEM
deny_reason contains msg if {
	input.classification in {"Restricted", "Confidential"}
	not input.log_forwarded_to_siem == true
	msg := sprintf("asset %s classified %s must forward logs to the central SIEM (CTL-010)", [input.asset_id, input.classification])
}

# Minimum 365-day retention for Restricted assets (audit-trail requirement)
deny_reason contains msg if {
	input.classification == "Restricted"
	input.retention_days < 365
	msg := sprintf("asset %s classified Restricted has %d-day retention — minimum is 365 days (CTL-010)", [input.asset_id, input.retention_days])
}
