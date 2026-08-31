import pytest
from simulator.clock import clock
from backend.intelligence.semantic_signal import SemanticSignal, filter_unauthorized_llm_payload

def test_semantic_signal_validation():
    clock.reset(1760000000)
    sig = SemanticSignal(
        signal_type="failure_is_transient",
        value=0.85,
        confidence=0.90,
        evidence_reference="ISO 91 transient outage",
        observed_timestamp=clock.now()
    )
    assert sig.value == 0.85
    assert sig.confidence == 0.90

    # Reject invalid signal type
    with pytest.raises(ValueError):
        SemanticSignal(
            signal_type="unauthorized_random_signal",
            value=0.5,
            confidence=0.5,
            evidence_reference="ref",
            observed_timestamp=clock.now()
        )

    # Reject out-of-range value
    with pytest.raises(ValueError):
        SemanticSignal(
            signal_type="failure_is_transient",
            value=1.5,
            confidence=0.5,
            evidence_reference="ref",
            observed_timestamp=clock.now()
        )

def test_filter_unauthorized_llm_payload():
    malicious = {
        "expected_recovery": 50000.0,
        "discount_amount": 10000.0,
        "nev": 45000.0,
        "valid_reasoning": "Standard observation"
    }
    sanitized = filter_unauthorized_llm_payload(malicious)
    assert "expected_recovery" not in sanitized
    assert "discount_amount" not in sanitized
    assert "nev" not in sanitized
    assert sanitized["valid_reasoning"] == "Standard observation"
