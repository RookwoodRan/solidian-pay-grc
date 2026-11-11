# Solidian Pay — Access Control policy-as-code
# Maps to: CTL-004 (Access Control & Least Privilege), CTL-005 (Privileged Access Management)
# Frameworks: SOC 2 CC6.1-CC6.3 | ISO 27001 A.5.15/A.8.2/A.8.3/A.8.5 | NIST CSF PR.AA-01/PR.AA-03/PR.AA-05
#
# Input shape: a single IAM binding record, e.g.
# {
#   "principal": "user:alice@solidianpay.example",
#   "role": "roles/admin",
#   "privileged": true,
#   "mfa_enforced": true,
#   "resource": "prod-payments-db",
#   "wildcard_scope": false,
#   "justification_ticket": "IAM-4821"
# }

package solidianpay.access_control

import rego.v1

default allow := false

allow if {
	count(deny_reason) == 0
}

# CTL-005: every privileged binding must have MFA enforced
deny_reason contains msg if {
	input.privileged == true
	not input.mfa_enforced == true
	msg := sprintf("privileged principal %s on %s requires MFA enforcement (CTL-005)", [input.principal, input.resource])
}

# CTL-004: no wildcard/blanket scope grants — least privilege
deny_reason contains msg if {
	input.wildcard_scope == true
	msg := sprintf("wildcard-scope grant to %s on %s violates least-privilege (CTL-004)", [input.principal, input.resource])
}

# CTL-005: privileged access requires a documented business justification
deny_reason contains msg if {
	input.privileged == true
	not input.justification_ticket
	msg := sprintf("privileged grant to %s on %s missing justification record (CTL-005)", [input.principal, input.resource])
}

# CTL-004: service accounts must not hold interactive/console roles
deny_reason contains msg if {
	startswith(input.principal, "serviceAccount:")
	input.role == "roles/admin"
	msg := sprintf("service account %s should not hold interactive admin role (CTL-004)", [input.principal])
}
