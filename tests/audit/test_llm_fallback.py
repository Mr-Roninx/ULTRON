import pytest
from backend.audit.live_llm_trace import execute_fallback_ladder_experiment
from backend.llm.provider import LLMRouter, HuggingFaceProvider, MockProvider
from backend.agent.schemas import AgentIntent

def test_fallback_ladder_execution():
    res = execute_fallback_ladder_experiment()
    assert res["all_passed"] is True
    assert res["verdict"] == "PROVEN"
    assert "HuggingFace" in res["ladder_sequence"]
    assert "SafeDeterministicFallback" in res["ladder_sequence"]

def test_router_never_crashes_on_provider_error():
    router = LLMRouter(primary=HuggingFaceProvider(api_token="hf_bad_token_testing"), active_provider_name="HF")
    intent = router.generate_intent([{"role": "user", "content": "ping"}], [])
    assert isinstance(intent, AgentIntent)
    assert intent.action_type == "WAIT"
    assert "Safe failure" in intent.reasoning or "failed" in intent.reasoning.lower()
