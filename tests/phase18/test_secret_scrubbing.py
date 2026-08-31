import pytest
from backend.audit.trace import scrub_trace_payload

def test_phase18_secret_scrubbing():
    payload = {
        "HF_TOKEN": "hf_secret_key_12345",
        "nested": {
            "api_key": "private_key",
            "safe_metric": 42.0
        }
    }
    scrubbed = scrub_trace_payload(payload)
    assert "[SCRUBBED_SECRET]" in str(scrubbed)
    assert "hf_secret_key_12345" not in str(scrubbed)
    assert scrubbed["nested"]["safe_metric"] == 42.0
