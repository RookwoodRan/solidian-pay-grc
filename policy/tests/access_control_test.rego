package solidianpay.access_control

import rego.v1

test_allow_when_privileged_with_mfa_and_justification if {
	allow with input as {
		"principal": "user:alice@solidianpay.example",
		"role": "roles/admin",
		"privileged": true,
		"mfa_enforced": true,
		"resource": "prod-payments-db",
		"wildcard_scope": false,
		"justification_ticket": "IAM-4821",
	}
}

test_deny_privileged_without_mfa if {
	not allow with input as {
		"principal": "user:bob@solidianpay.example",
		"role": "roles/admin",
		"privileged": true,
		"mfa_enforced": false,
		"resource": "prod-payments-db",
		"wildcard_scope": false,
		"justification_ticket": "IAM-4900",
	}
}

test_deny_wildcard_scope if {
	not allow with input as {
		"principal": "user:carol@solidianpay.example",
		"role": "roles/viewer",
		"privileged": false,
		"mfa_enforced": true,
		"resource": "prod-payments-db",
		"wildcard_scope": true,
	}
}

test_deny_privileged_without_justification if {
	not allow with input as {
		"principal": "user:dave@solidianpay.example",
		"role": "roles/admin",
		"privileged": true,
		"mfa_enforced": true,
		"resource": "prod-payments-db",
		"wildcard_scope": false,
	}
}

test_deny_service_account_admin_role if {
	not allow with input as {
		"principal": "serviceAccount:ci-deploy@solidianpay.example",
		"role": "roles/admin",
		"privileged": true,
		"mfa_enforced": true,
		"resource": "prod-payments-db",
		"wildcard_scope": false,
		"justification_ticket": "IAM-5001",
	}
}
