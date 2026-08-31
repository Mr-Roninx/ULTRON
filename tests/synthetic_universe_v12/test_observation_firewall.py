import pytest
from synthetic_payment_universe.world_v12.observation.firewall import WorldObservationFirewall
from backend.benchmark.firewall import FutureInformationLeakageError

def test_observation_firewall_temporal_and_key_blocks():
    now = 1760000000

    # 1. Future timestamp -> Exception
    future_data = {"created_at": now + 3600, "amount": 25000.0}
    with pytest.raises(FutureInformationLeakageError):
        WorldObservationFirewall.sanitize(future_data, now)

    # 2. Hidden oracle keys stripped
    oracle_data = {
        "created_at": now - 100,
        "amount": 25000.0,
        "true_root_cause": "DATABASE_CRASH",
        "oracle_optimal_action": "RETRY",
        "latent_profile": "SALARY_CYCLE"
    }
    sanitized = WorldObservationFirewall.sanitize(oracle_data, now)
    assert "true_root_cause" not in sanitized
    assert "oracle_optimal_action" not in sanitized
    assert "latent_profile" not in sanitized
    assert sanitized["amount"] == 25000.0
