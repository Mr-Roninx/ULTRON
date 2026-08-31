import pytest
from backend.audit.live_llm_trace import execute_future_information_experiment
from simulator.clock import clock

def test_future_information_firewall():
    res = execute_future_information_experiment()
    assert res["temporal_isolation_verified"] is True
    assert res["verdict"] == "PROVEN"
    assert len(res["observations_checked"]) >= 3
