import pytest
from synthetic_payment_universe.schema.events import UnifiedTemporalEvent
from synthetic_payment_universe.schema.visibility import EventVisibility
from synthetic_payment_universe.validators.leakage_validator import UniverseLeakageValidator

def test_future_leakage_detection():
    now = 1760000000
    
    # Valid past event
    evt_valid = UnifiedTemporalEvent(
        event_id="e_valid",
        event_type="PAYMENT_FAILED",
        entity_id="p_1",
        timestamp=now - 300,
        visibility=EventVisibility.OBSERVABLE,
        payload={"failure_code": "91"}
    )
    is_valid, errs = UniverseLeakageValidator.validate_event_stream([evt_valid], now)
    assert is_valid is True
    assert len(errs) == 0

    # Future timestamp leakage
    evt_future = UnifiedTemporalEvent(
        event_id="e_future",
        event_type="PAYMENT_RECOVERED",
        entity_id="p_1",
        timestamp=now + 3600,
        visibility=EventVisibility.OBSERVABLE,
        payload={"amount": 24700.0}
    )
    is_valid_fut, errs_fut = UniverseLeakageValidator.validate_event_stream([evt_future], now)
    assert is_valid_fut is False
    assert any("Temporal Leakage" in e for e in errs_fut)

    # Oracle key leakage
    evt_oracle = UnifiedTemporalEvent(
        event_id="e_oracle",
        event_type="PAYMENT_FAILED",
        entity_id="p_1",
        timestamp=now,
        visibility=EventVisibility.OBSERVABLE,
        payload={"true_root_cause": "ISSUER_CRASH"}
    )
    is_valid_ora, errs_ora = UniverseLeakageValidator.validate_event_stream([evt_oracle], now)
    assert is_valid_ora is False
    assert any("Data Leakage" in e for e in errs_ora)
