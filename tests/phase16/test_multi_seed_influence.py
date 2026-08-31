import pytest
from backend.evidence.llm_influence_v2 import execute_llm_influence_multiseed

def test_multi_seed_influence_execution():
    res = execute_llm_influence_multiseed(seeds=list(range(201, 211))) # Test with 10 seeds
    
    assert res["total_seeds"] == 10
    assert "metric_a_candidate_novelty_rate" in res["metrics"]
    assert "metric_b_candidate_pool_influence_rate" in res["metrics"]
    assert "metric_c_preference_influence_rate" in res["metrics"]
    assert "metric_d_final_decision_influence_rate" in res["metrics"]
    assert res["verdict"] in ["CANDIDATE_INFLUENCE_ONLY", "FINAL_DECISION_INFLUENCE", "MINIMAL_INFLUENCE"]
