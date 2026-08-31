from typing import Dict, Any, Tuple
from backend.intelligence.semantic_signal import SemanticSignal
from backend.intelligence.contextual_features import ContextualFeatures

class UncertaintyEstimator:
    """
    Quantifies semantic signal uncertainty and performs out-of-distribution (OOD) detection.
    """
    CONFIDENCE_THRESHOLD = 0.40

    @classmethod
    def estimate_uncertainty(cls, signal: SemanticSignal, features: ContextualFeatures) -> Tuple[float, bool]:
        """
        Returns (uncertainty_score, is_out_of_distribution)
        """
        # Base uncertainty is inverse of confidence
        base_uncertainty = max(0.0, min(1.0, 1.0 - signal.confidence))

        is_ood = False

        # 1. Low confidence detection
        if signal.confidence < cls.CONFIDENCE_THRESHOLD:
            is_ood = True

        # 2. Semantic conflict detection
        # e.g., signal claims failure is transient, but failure code is permanent (14 - Expired Card)
        if signal.signal_type == "failure_is_transient" and features.failure_code in ["14", "CARD_EXPIRED", "05"]:
            if signal.value > 0.70:
                is_ood = True
                base_uncertainty = min(1.0, base_uncertainty + 0.50)

        # 3. Liquidity signal contradiction
        if signal.signal_type == "customer_liquidity_likelihood" and features.failure_code == "91":
            # 91 is an issuer outage, not liquidity
            base_uncertainty = min(1.0, base_uncertainty + 0.30)

        return round(base_uncertainty, 4), is_ood

uncertainty_estimator = UncertaintyEstimator()
