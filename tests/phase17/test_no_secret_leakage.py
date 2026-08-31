import pytest
from backend.audit.trace import scrub_trace_payload

def test_trace_scrub_removes_secrets():
    payload = {
        "HF_TOKEN": "hf_secret_12345",
        "Authorization": "Bearer test_token",
        "nested": {
            "api_key": "secret_key",
            "normal_field": "valid_value"
        }
    }
    
    scrubbed = scrub_trace_payload(payload)
    assert "[SCRUBBED_SECRET]" in str(scrubbed)
    assert "hf_secret_12345" not in str(scrubbed)
    assert scrubbed["nested"]["normal_field"] == "valid_value"
