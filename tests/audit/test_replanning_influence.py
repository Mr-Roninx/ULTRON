import pytest
from backend.audit.live_llm_trace import execute_replanning_influence_experiment

def test_chaos_replanning_influence():
    res = execute_replanning_influence_experiment()
    assert res["replan_triggered"] is True
    assert res["action_adapted"] is True
    assert res["verdict"] == "PROVEN"
    assert res["replan_count"] >= 1
