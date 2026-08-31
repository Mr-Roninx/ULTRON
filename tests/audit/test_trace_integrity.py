import pytest
from backend.audit.trace import AuditTrace, scrub_trace_payload, SECRET_PATTERNS

def test_trace_scrubbing_removes_secrets():
    raw_payload = {
        "hf_token": "hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
        "nested": {
            "api_key": "secret_key_1234567890",
            "prompt": "You are an agent...",
            "safe_field": "Ananya Textiles"
        }
    }

    scrubbed = scrub_trace_payload(raw_payload)
    assert scrubbed["hf_token"] == "[SCRUBBED_SECRET]"
    assert scrubbed["authorization"] == "[SCRUBBED_SECRET]"
    assert scrubbed["nested"]["api_key"] == "[SCRUBBED_SECRET]"
    assert scrubbed["nested"]["prompt"] == "[SCRUBBED_SECRET]"
    assert scrubbed["nested"]["safe_field"] == "Ananya Textiles"

def test_trace_logs_ordered_events_without_leakage():
    trace = AuditTrace()
    trace.log("RUN_START", {"safe_info": "ok"})
    trace.log("LLM_REQUEST", {"token_attempt": "Bearer 12345678901234567890"})

    exported = trace.to_dict()
    assert exported["event_count"] == 2
    assert exported["events"][0]["event_type"] == "RUN_START"
    assert exported["events"][1]["event_type"] == "LLM_REQUEST"
    assert "Bearer" not in exported["events"][1]["payload"]["token_attempt"] or "[SCRUBBED_CREDENTIAL]" in exported["events"][1]["payload"]["token_attempt"]
