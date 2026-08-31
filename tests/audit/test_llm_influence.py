import pytest
from backend.audit.live_llm_trace import execute_llm_influence_experiment

def test_llm_influence_a_b_experiment():
    res = execute_llm_influence_experiment()
    assert "candidates_run_a_llm_on" in res
    assert "candidates_run_b_llm_off" in res
    assert "candidate_novelty_rate" in res
    assert "verdict" in res
    assert res["verdict"] in ["DECISION_INFLUENCE", "CANDIDATE_INFLUENCE_ONLY", "NO_EFFECT"]
    assert 0.0 <= res["candidate_novelty_rate"] <= 1.0
