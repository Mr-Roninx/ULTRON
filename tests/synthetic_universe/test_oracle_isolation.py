import pytest
from synthetic_payment_universe.oracle.hidden_oracle import hidden_oracle
from synthetic_payment_universe.observation.firewall import UniverseObservationFirewall
from backend.benchmark.firewall import FutureInformationLeakageError

def test_adversarial_oracle_isolation_attacks():
    now = 1760000000

    # 1. Attack with future timestamp -> must fail closed
    malicious_future = {
        "created_at": now + 7200,
        "amount": 50000.0,
        "customer_id": "c_hack"
    }
    with pytest.raises(FutureInformationLeakageError):
        UniverseObservationFirewall.sanitize_for_agent(malicious_future, now)

    # 2. Attack with oracle keys -> keys must be stripped
    malicious_oracle = {
        "created_at": now - 100,
        "amount": 50000.0,
        "true_root_cause": "CONFIDENTIAL_ROOT_CAUSE",
        "oracle_optimal_action": "RETRY_GATEWAY_B",
        "latent_profile": "PRICE_SENSITIVE"
    }
    sanitized = UniverseObservationFirewall.sanitize_for_agent(malicious_oracle, now)
    assert "true_root_cause" not in sanitized
    assert "oracle_optimal_action" not in sanitized
    assert "latent_profile" not in sanitized
    assert sanitized["amount"] == 50000.0
