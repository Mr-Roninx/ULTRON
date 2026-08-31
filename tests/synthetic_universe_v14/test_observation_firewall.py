import pytest
from synthetic_payment_universe.world_v14.observation.recursive_firewall import RecursiveObservationFirewall
from backend.benchmark.firewall import FutureInformationLeakageError

def test_recursive_firewall_rejection():
    now = 1760000000
    future_data = {"created_at": now + 500, "amount": 10000.0}
    with pytest.raises(FutureInformationLeakageError):
        RecursiveObservationFirewall.sanitize(future_data, now)

def test_recursive_firewall_strips_oracle():
    now = 1760000000
    nested = {
        "created_at": now - 10,
        "true_root_cause": "DATABASE_OVERLOAD",
        "oracle_optimal_action": "RETRY",
        "customer": {
            "cash_reserve": 50000.0,
            "name": "Acme Inc"
        }
    }
    sanitized = RecursiveObservationFirewall.sanitize(nested, now)
    assert "true_root_cause" not in sanitized
    assert "oracle_optimal_action" not in sanitized
    assert "cash_reserve" not in sanitized["customer"]
    assert sanitized["customer"]["name"] == "Acme Inc"
