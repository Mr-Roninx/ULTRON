from typing import Dict, Any, List, Optional
from backend.intelligence.semantic_signal import SemanticSignal
from backend.intelligence.contextual_features import ContextualFeatures
from backend.intelligence.uncertainty import uncertainty_estimator

class SignalCalibrationEngine:
    """
    Calibrates and bounds semantic signals.
    Enforces deterministic impact caps, uncertainty damping, and conflict resolution.
    """
    SIGNAL_MIN = 0.0
    SIGNAL_MAX = 1.0
    MAX_ECONOMIC_IMPACT = 0.25 # Max ±25% modifier on base parameters

    @classmethod
    def calibrate_signal(cls, signal: SemanticSignal, features: ContextualFeatures) -> SemanticSignal:
        # 1. Clip raw value
        clipped_val = max(cls.SIGNAL_MIN, min(cls.SIGNAL_MAX, signal.value))
        
        # 2. Estimate uncertainty and OOD
        uncert, is_ood = uncertainty_estimator.estimate_uncertainty(signal, features)
        signal.uncertainty = uncert

        # 3. Confidence & Uncertainty Attenuation
        if is_ood:
            # Dampen out-of-distribution signal towards zero influence (neutral 0.50 or 0.0)
            calibrated_val = 0.50 * (1.0 - uncert)
            status = "OOD_CLAMPED"
        else:
            # Weighted by confidence
            attenuation = signal.confidence * (1.0 - uncert)
            # Center around 0.50 neutral point
            calibrated_val = 0.50 + (clipped_val - 0.50) * attenuation
            status = "CALIBRATED"

        signal.value = round(max(cls.SIGNAL_MIN, min(cls.SIGNAL_MAX, calibrated_val)), 4)
        signal.calibration_status = status
        return signal

    @classmethod
    def resolve_conflicting_signals(cls, signals: List[SemanticSignal]) -> List[SemanticSignal]:
        """
        Deterministically resolves conflicting signals (e.g. transient vs hard permanent).
        """
        type_map = {s.signal_type: s for s in signals}
        
        # If both transient and fatigue signals exist, prioritize conservative relationship preservation
        if "customer_fatigue_signal" in type_map and "urgency_signal" in type_map:
            fatigue = type_map["customer_fatigue_signal"]
            urgency = type_map["urgency_signal"]
            if fatigue.value > 0.60:
                # Fatigue dampens urgency to prevent customer churn
                urgency.value = min(urgency.value, 0.30)
                urgency.calibration_status = "FATIGUE_DAMPED"

        return list(type_map.values())

signal_calibration_engine = SignalCalibrationEngine()
