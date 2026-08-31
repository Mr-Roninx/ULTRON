import pytest
import os
from backend.evidence.config_truth import config_truth_reporter

@pytest.mark.fixture
def test_llm_truth_honest_classification():
    truth = config_truth_reporter.get_truth()
    if not os.getenv("HF_TOKEN"):
        assert truth["llm_mode"] == "SAFE_DETERMINISTIC_FALLBACK"
    else:
        assert truth["llm_mode"] == "LIVE_HF"
