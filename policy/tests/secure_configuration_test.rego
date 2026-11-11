package solidianpay.secure_configuration

import rego.v1

test_allow_encrypted_private_resource if {
	allow with input as {
		"resource_type": "storage_bucket",
		"name": "customer-exports",
		"encrypted_at_rest": true,
		"public_access": false,
		"classification": "Restricted",
		"tls_min_version": "1.2",
	}
}

test_deny_unencrypted_restricted_bucket if {
	not allow with input as {
		"resource_type": "storage_bucket",
		"name": "customer-exports",
		"encrypted_at_rest": false,
		"public_access": false,
		"classification": "Restricted",
	}
}

test_deny_public_confidential_bucket if {
	not allow with input as {
		"resource_type": "storage_bucket",
		"name": "model-artifacts",
		"encrypted_at_rest": true,
		"public_access": true,
		"classification": "Confidential",
	}
}

test_deny_weak_tls if {
	not allow with input as {
		"resource_type": "load_balancer",
		"name": "public-api-lb",
		"encrypted_at_rest": true,
		"public_access": false,
		"classification": "Internal",
		"tls_min_version": "1.0",
	}
}

test_allow_internal_unencrypted_resource if {
	allow with input as {
		"resource_type": "storage_bucket",
		"name": "build-cache",
		"encrypted_at_rest": false,
		"public_access": false,
		"classification": "Internal",
	}
}
