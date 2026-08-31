import pytest
from backend.evidence.hard_case_benchmark import HardCaseBenchmarkRunner

def test_hard_case_runner():
    runner = HardCaseBenchmarkRunner(seeds=[301, 302])
    res = runner.run_benchmark()
    assert len(res["hard_cases"]["records"]) == 2
    assert "information_value" in res
