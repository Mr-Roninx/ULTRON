import pytest
from backend.evidence.llm_causal_influence import run_llm_causal_influence

def test_causal_influence_evaluation_matrix():
    res = run_llm_causal_influence(seeds=list(range(301, 311))) # 10 seeds test
    
    assert res["total_seeds_evaluated"] == 10
    assert "level_1_candidate_generation" in res
    assert "level_2_semantic_diagnosis" in res
    assert "level_3_action_ranking_and_economic_value" in res
    assert "level_4_final_execution" in res
    
    assert res["level_1_candidate_generation"]["candidate_novelty_rate"] >= 0.0
    assert res["level_2_semantic_diagnosis"]["diagnosis_difference_rate"] >= 0.0
    assert res["level_3_action_ranking_and_economic_value"]["mean_delta_nev"] >= 0.0
