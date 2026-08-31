import pytest
from backend.benchmark.firewall import TemporalObservationFirewall, FutureInformationLeakageError
from simulator.clock import clock

def test_future_information_scrubbing():
    clock.reset(1750000000)
    current_t = clock.now()
    
    past_payload = {
        "created_at": current_t - 3600,
        "amount": 24700.0
    }
    
    # Valid past context passes
    sanitized = TemporalObservationFirewall.sanitize_agent_context(past_payload)
    assert sanitized["amount"] == 24700.0
    
    # Future timestamp raises FutureInformationLeakageError
    future_payload = {
        "created_at": current_t + 3600,
        "amount": 24700.0
    }
    
    with pytest.raises(FutureInformationLeakageError):
        TemporalObservationFirewall.sanitize_agent_context(future_payload)
