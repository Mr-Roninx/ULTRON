import pytest
from backend.evidence.intelligence_utility import run_intelligence_utility_benchmark

def test_intelligence_utility_benchmark_runner():
    res = run_intelligence_utility_benchmark(seeds=[401, 402, 403])
    assert res["utility"]["sample_size"] == 3
    assert "delta_nev_signal" in res["information_value"]
    assert "percentage_reduction" in res["regret_reduction"]
