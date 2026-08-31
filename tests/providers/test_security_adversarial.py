import pytest
from backend.providers.razorpay.webhook import RazorpayWebhookVerifier
from backend.safety.production_gate import production_gate
from backend.agent.action_registry import action_registry

def test_security_adversarial_invariants():
    # 1. Forged webhook signature fails closed
    assert RazorpayWebhookVerifier.verify_signature(b"malicious_body", "fake_sig", "real_secret") is False

    # 2. Arbitrary balance mutation rejected by ActionRegistry
    valid, err = action_registry.validate_action("SET_BALANCE_999999")
    assert valid is False
    assert "not registered" in err

    # 3. Direct SQL / shell tool execution is not permissioned
    valid_sql, _ = action_registry.validate_action("EXECUTE_RAW_SQL")
    assert valid_sql is False

    # 4. Production gate blocks live execution
    ok, msg = production_gate.validate_execution("razorpay", "REFUND_PAYMENT", 100000, is_live_request=True)
    assert ok is False
