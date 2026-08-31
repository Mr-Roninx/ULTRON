import pytest
from synthetic_payment_universe.world_v15.observation.blind_firewall import BlindObservationFirewall

def test_oracle_key_filtering():
    data = {
        "created_at": 1760000000,
        "oracle_hidden_optimal_route": "GATEWAY_C",
        "evaluator_future_loss": 500.0,
        "amount": 12000.0
    }
    sanitized = BlindObservationFirewall.sanitize(data, current_time=1760000000)
    assert "oracle_hidden_optimal_route" not in sanitized
    assert "evaluator_future_loss" not in sanitized
    assert sanitized["amount"] == 12000.0
