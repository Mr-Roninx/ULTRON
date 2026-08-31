import pytest
from simulator.clock import clock
from backend.intelligence.semantic_signal import SemanticSignal
from backend.intelligence.contextual_features import ContextualFeatures
from backend.intelligence.calibration import signal_calibration_engine

def test_signal_calibration_attenuation():
    clock.reset(1760000000)
    features = ContextualFeatures(
        payment_id="pmt_1", customer_id="c_1", failure_code="91",
        rail="CARD", gateway_id="GATEWAY_A", gateway_health=0.95,
        complaints=0, segment="B2B_ENTERPRISE", payment_age_seconds=100
    )

    # High confidence signal -> preserved
    sig_high = SemanticSignal(
        signal_type="failure_is_transient", value=0.90, confidence=0.95,
        evidence_reference="Core banking reboot", observed_timestamp=clock.now()
    )
    cal_high = signal_calibration_engine.calibrate_signal(sig_high, features)
    assert cal_high.calibration_status == "CALIBRATED"
    assert cal_high.value > 0.80

    # Low confidence signal -> dampened towards 0.50
    sig_low = SemanticSignal(
        signal_type="failure_is_transient", value=0.90, confidence=0.20,
        evidence_reference="Uncertain guess", observed_timestamp=clock.now()
    )
    cal_low = signal_calibration_engine.calibrate_signal(sig_low, features)
    assert cal_low.calibration_status == "OOD_CLAMPED"
    assert cal_low.value < 0.60
