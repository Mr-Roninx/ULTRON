import pytest
from backend.agent.action_registry import action_registry

@pytest.mark.fixture
def test_razorpay_llm_cannot_bypass_action_registry():
    ok, _ = action_registry.validate_action("INVOKE_RAZORPAY_DIRECT_API")
    assert ok is False
