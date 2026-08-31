import pytest
from synthetic_payment_universe.world_v15.observation.blind_firewall import BlindObservationFirewall

def test_blind_evaluation_strips_latent_data():
    raw = {
        "created_at": 1760000000,
        "amount": 25000.0,
        "difficulty_category": "HARD",
        "oracle_optimal_action": "WAIT",
        "would_recover_naturally": True
    }
    sanitized = BlindObservationFirewall.sanitize(raw, current_time=1760000000)
    assert "difficulty_category" not in sanitized
    assert "oracle_optimal_action" not in sanitized
    assert "would_recover_naturally" not in sanitized
    assert sanitized["amount"] == 25000.0
