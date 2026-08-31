import pytest
from backend.evidence.hard_case_benchmark import run_hard_case_benchmark

def test_llm_regret_computation():
    res = run_hard_case_benchmark(seeds=[301, 302, 303])
    assert "regret" in res
    assert res["regret"]["mean_regret"] >= 0.0
    assert "median_regret" in res["regret"]
