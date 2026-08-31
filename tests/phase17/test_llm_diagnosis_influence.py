import pytest
from backend.evidence.diagnosis_ab_test import run_diagnosis_ab_test

def test_semantic_diagnosis_ab_difference():
    res = run_diagnosis_ab_test()
    assert res["total_scenarios"] == 5
    assert "metrics" in res
    assert res["metrics"]["diagnosis_difference_rate"] > 0.0
    assert len(res["scenarios"]) == 5
