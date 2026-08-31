import pytest
from backend.agent.action_registry import action_registry

def test_action_registry_rejects_unauthorized_proposals():
    raw_candidates = [
        "WAIT",
        "RETRY_GATEWAY_A",
        "TRANSFER_MONEY",
        "DELETE_PAYMENT",
        "EXECUTE_SQL",
        "DROP_TABLE",
        "UPDATE_BALANCE"
    ]

    valid, rejected = action_registry.reject_unauthorized_proposals(raw_candidates, customer_segment="B2B_ENTERPRISE")
    
    assert "WAIT" in valid
    assert "RETRY_GATEWAY_A" in valid
    assert "TRANSFER_MONEY" in rejected
    assert "DELETE_PAYMENT" in rejected
    assert "EXECUTE_SQL" in rejected
    assert "DROP_TABLE" in rejected
    assert "UPDATE_BALANCE" in rejected
