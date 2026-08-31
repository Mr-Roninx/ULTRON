import pytest
from backend.benchmark.firewall import firewall, FutureInformationLeakageError
from simulator.clock import clock

def test_future_information_firewall_blocks_lookahead():
    clock.reset(1700000000)
    current_time = clock.now()

    valid_context = {
        "customer_id": "c_1",
        "timestamp": current_time,
        "payment": {"amount": 5000.0, "status": "FAILED", "created_at": current_time}
    }
    # Should pass without error
    firewall.sanitize_agent_context(valid_context)

    future_context = {
        "customer_id": "c_1",
        "timestamp": current_time + 3600, # In the future!
        "payment": {"amount": 5000.0}
    }
    with pytest.raises(FutureInformationLeakageError):
        firewall.sanitize_agent_context(future_context)

    leakage_context = {
        "customer_id": "c_1",
        "actual_recovery": 24700.0 # Prohibited future key!
    }
    with pytest.raises(FutureInformationLeakageError):
        firewall.sanitize_agent_context(leakage_context)
