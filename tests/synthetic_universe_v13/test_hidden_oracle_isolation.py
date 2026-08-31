import pytest
from synthetic_payment_universe.world_v13.observation.firewall import CivilizationObservationFirewall

def test_hidden_oracle_key_stripping():
    now = 1760000000
    data = {
        "created_at": now - 100,
        "amount": 25000.0,
        "true_root_cause": "DATABASE_CRASH",
        "oracle_optimal_action": "RETRY",
        "next_salary_timestamp": now + 86400,
        "current_cash_reserve": 50000.0
    }
    sanitized = CivilizationObservationFirewall.sanitize(data, now)
    assert "true_root_cause" not in sanitized
    assert "oracle_optimal_action" not in sanitized
    assert "next_salary_timestamp" not in sanitized
    assert "current_cash_reserve" not in sanitized
    assert sanitized["amount"] == 25000.0
