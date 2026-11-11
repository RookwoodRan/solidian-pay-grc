# Solidian Pay: Secure Configuration policy-as-code
# Maps to: CTL-008 (Secure Configuration & Boundary Protection), CTL-028 (Encryption & Secure Data Transmission)
# Frameworks: SOC 2 CC5.2/CC6.6/CC6.7/CC7.1 | ISO 27001 A.8.9/A.8.24 | NIST CSF PR.PS-01/PR.DS-01/PR.DS-02
#
# Input shape: a single cloud resource record from a Terraform-plan-style export, e.g.
# {
#   "resource_type": "storage_bucket",
#   "name": "customer-exports",
#   "encrypted_at_rest": true,
#   "public_access": false,
#   "classification": "Restricted",
#   "tls_min_version": "1.2"
# }

package solidianpay.secure_configuration

import rego.v1

default allow := false

allow if {
	count(deny_reason) == 0
}

# CTL-028: Restricted/Confidential data stores must be encrypted at rest
deny_reason contains msg if {
	input.classification in {"Restricted", "Confidential"}
	not input.encrypted_at_rest == true
	msg := sprintf("%s '%s' classified %s must be encrypted at rest (CTL-028)", [input.resource_type, input.name, input.classification])
}

# CTL-008: no resource holding Restricted/Confidential data may be publicly exposed
deny_reason contains msg if {
	input.classification in {"Restricted", "Confidential"}
	input.public_access == true
	msg := sprintf("%s '%s' classified %s must not be publicly accessible (CTL-008)", [input.resource_type, input.name, input.classification])
}

# CTL-028: enforce minimum TLS version where applicable
deny_reason contains msg if {
	input.tls_min_version
	tls_version_below_minimum(input.tls_min_version)
	msg := sprintf("%s '%s' TLS minimum %s is below required 1.2 (CTL-028)", [input.resource_type, input.name, input.tls_min_version])
}

tls_version_below_minimum(v) if {
	v in {"1.0", "1.1"}
}
