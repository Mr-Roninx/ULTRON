import pytest
from backend.evidence.hard_case_benchmark import run_hard_case_benchmark

def test_nev_sensitivity_analysis():
    res = run_hard_case_benchmark(seeds=[301, 302, 303])
    assert "sensitivity" in res
    sens = res["sensitivity"]
    assert 0.0 <= sens["within_1_pct_rate"] <= 1.0
    assert 0.0 <= sens["within_5_pct_rate"] <= 1.0
    assert 0.0 <= sens["within_10_pct_rate"] <= 1.0
