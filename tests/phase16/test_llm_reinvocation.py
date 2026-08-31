import pytest
from backend.evidence.llm_performance import execute_chaos_replanning_experiment

def test_llm_reinvocation_on_chaos():
    res = execute_chaos_replanning_experiment()
    
    assert res["initial_llm_invocations"] >= 1
    assert res["total_llm_invocations"] >= 2
    assert res["replan_triggered"] is True
    assert res["verdict"] == "PROVEN"
