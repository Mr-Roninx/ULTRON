import pytest
from backend.evidence.intelligence_utility import run_intelligence_utility_benchmark

def test_regret_reduction_measurement():
    res = run_intelligence_utility_benchmark(seeds=[401, 402, 403])
    reg = res["regret_reduction"]
    assert "baseline_mean_regret" in reg
    assert "calibrated_mean_regret" in reg
    assert reg["percentage_reduction"] >= 0.0
