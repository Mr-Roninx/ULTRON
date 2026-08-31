import pytest
from backend.audit.live_llm_trace import execute_memory_influence_experiment

def test_episodic_memory_influence():
    res = execute_memory_influence_experiment()
    assert res["memory_multiplier_applied"] is True
    assert res["verdict"] in ["PROVEN", "PARTIALLY_SUPPORTED"]
    assert res["retry_gateway_a_score_with_memory"] < res["retry_gateway_a_score_without_memory"]
