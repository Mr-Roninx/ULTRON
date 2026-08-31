import pytest
from backend.evidence.intelligence_utility import run_intelligence_utility_benchmark

def test_nev_information_value_metrics():
    res = run_intelligence_utility_benchmark(seeds=[401, 402, 403])
    info = res["information_value"]
    assert "delta_nev_candidate" in info
    assert "delta_nev_signal" in info
    assert "delta_nev_combined" in info
    assert info["delta_nev_signal"]["mean"] >= 0.0
