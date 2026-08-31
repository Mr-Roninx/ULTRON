import pytest
from backend.audit.trace import scrub_trace_payload

def test_trace_scrubbing_removes_secrets():
    payload = {
        "hf_token": "hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
        "api_key": "sk-1234567890abcdef1234567890abcdef",
        "private_prompt": "Confidential internal instructions",
        "chain_of_thought": "Private reasoning steps",
        "safe_data": {"action": "WAIT", "exposure": 24700.0}
    }

    scrubbed = scrub_trace_payload(payload)
    
    assert scrubbed["hf_token"] == "[SCRUBBED_SECRET]"
    assert scrubbed["authorization"] == "[SCRUBBED_SECRET]"
    assert scrubbed["api_key"] == "[SCRUBBED_SECRET]"
    assert scrubbed["chain_of_thought"] == "[SCRUBBED_SECRET]"
    assert scrubbed["safe_data"]["action"] == "WAIT"
