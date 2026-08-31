import pytest
from backend.evidence.live_provider_experiment import run_live_provider_experiment

def test_live_provider_truth_audit():
    res = run_live_provider_experiment()
    assert "hugging_face_summary" in res
    summary = res["hugging_face_summary"]
    assert "truth_verdict" in summary
    assert summary["truth_verdict"] in ["LIVE_HF_OPERATIONAL", "HF_CREDIT_EXHAUSTED_FALLBACK_ACTIVE", "HF_NOT_AVAILABLE"]
