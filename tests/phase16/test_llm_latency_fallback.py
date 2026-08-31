import pytest
from backend.llm.provider import LLMRouter, MockProvider, HuggingFaceProvider
from backend.llm.performance import LLMOperatingMode
from backend.agent.schemas import AgentIntent

def test_llm_router_failover_ladder():
    # Failing primary provider
    failing_primary = HuggingFaceProvider(api_token="bad_token", base_url="http://10.255.255.1", timeout_seconds=0.1)
    
    # Successful mock fallback provider
    fallback_intent = AgentIntent(action_type="WAIT", candidate_actions=["WAIT"], preferred_action="WAIT", reasoning="Fallback success", expected_yield=0.0, payload={})
    mock_fallback = MockProvider([fallback_intent])

    router = LLMRouter(primary=failing_primary, fallback=mock_fallback)
    
    intent = router.generate_intent([{"role": "user", "content": "ping"}], [])
    assert intent.action_type == "WAIT"
    assert "Fallback success" in intent.reasoning

def test_llm_safe_mode_bypasses_remote():
    router = LLMRouter(mode=LLMOperatingMode.SAFE_MODE)
    intent = router.generate_intent([{"role": "user", "content": "ping"}], [])
    assert intent.action_type == "WAIT"
    assert "SAFE_MODE" in intent.reasoning
