import pytest
import hashlib
import json

@pytest.mark.fixture
def test_trace_hash_tamper_protection():
    trace_events = [
        {"stage": "PROVIDER_EVENT", "id": "evt_1"},
        {"stage": "RECONCILIATION", "status": "SETTLED"}
    ]
    raw = json.dumps(trace_events, sort_keys=True)
    trace_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    assert len(trace_hash) == 64

    # Tampering with trace invalidates hash
    tampered = list(trace_events)
    tampered[0]["stage"] = "TAMPERED_EVENT"
    tampered_hash = hashlib.sha256(json.dumps(tampered, sort_keys=True).encode("utf-8")).hexdigest()
    assert trace_hash != tampered_hash
