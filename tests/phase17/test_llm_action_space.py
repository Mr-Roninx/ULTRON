import pytest
from backend.evidence.llm_ablation import run_llm_ablation_matrix

def test_action_space_ablation_matrix():
    res = run_llm_ablation_matrix(seeds=[301, 302])
    assert res["configurations_evaluated"] == 7
    assert len(res["matrix"]) == 7
    for row in res["matrix"]:
        assert row["policy_violations"] == 0
        assert row["risk_violations"] == 0
