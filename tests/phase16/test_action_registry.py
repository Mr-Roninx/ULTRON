import pytest
from backend.agent.action_registry import action_registry

def test_action_registry_defaults():
    assert action_registry.is_registered("WAIT")
    assert action_registry.is_registered("RETRY_GATEWAY_A")
    assert action_registry.is_registered("SEND_PAYMENT_LINK")
    assert action_registry.is_registered("APPLY_DISCOUNT")
    assert not action_registry.is_registered("UNLIMITED_DISCOUNT")

def test_discount_policy_segment_constraint():
    valid_ent, _ = action_registry.validate_action("APPLY_DISCOUNT", "B2B_ENTERPRISE")
    valid_smb, reason = action_registry.validate_action("APPLY_DISCOUNT", "SMB")
    
    assert valid_ent is True
    assert valid_smb is False
    assert "not authorized for customer segment 'SMB'" in reason
