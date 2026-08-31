import pytest
from backend.evidence.hard_ambiguity import run_hard_ambiguity_benchmark

def test_hard_ambiguity_scenarios():
    res = run_hard_ambiguity_benchmark()
    assert res["scenarios_evaluated"] == 4
    assert 0.0 <= res["divergence_rate"] <= 1.0
    assert len(res["records"]) == 4
