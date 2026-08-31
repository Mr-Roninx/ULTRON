import pytest
from simulator.clock import clock
from backend.benchmark.firewall import TemporalObservationFirewall, FutureInformationLeakageError

def test_phase18_future_firewall():
    clock.reset(1760000000)
    now = clock.now()

    # Valid past observation
    valid_ctx = {"created_at": now - 3600, "amount": 24700.0}
    sanitized = TemporalObservationFirewall.sanitize_agent_context(valid_ctx)
    assert sanitized["amount"] == 24700.0

    # Future lookahead raises FutureInformationLeakageError
    leak_ctx = {"created_at": now + 3600, "amount": 24700.0}
    with pytest.raises(FutureInformationLeakageError):
        TemporalObservationFirewall.sanitize_agent_context(leak_ctx)
