import pytest
from backend.llm.performance import LLMPerformanceController, LatencySLA
from backend.llm.provider import HuggingFaceProvider, MockProvider, LLMRouter
from backend.agent.schemas import AgentIntent

def test_llm_performance_controller_timeout_classification():
    ctrl = LLMPerformanceController(soft_timeout_ms=3000.0, hard_timeout_ms=6000.0)
    
    assert ctrl.classify_latency(1500.0) == LatencySLA.EXCELLENT
    assert ctrl.classify_latency(3500.0) == LatencySLA.ACCEPTABLE
    assert ctrl.classify_latency(5500.0) == LatencySLA.DEGRADED
    assert ctrl.classify_latency(7500.0) == LatencySLA.TIMEOUT_FALLBACK
    assert ctrl.classify_latency(1000.0, timed_out=True) == LatencySLA.TIMEOUT_FALLBACK

def test_hf_provider_timeout_raises_safely():
    # Configure an unreachable provider with 0.1s timeout
    provider = HuggingFaceProvider(api_token="test_token", base_url="http://10.255.255.1", timeout_seconds=0.1)
    
    with pytest.raises((TimeoutError, ConnectionError)):
        provider.generate_intent([{"role": "user", "content": "test"}], [])
