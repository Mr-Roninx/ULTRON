from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from backend.intelligence.semantic_signal import SemanticSignal
from backend.intelligence.calibration import signal_calibration_engine

class BoundedEconomicModifier(BaseModel):
    parameter_name: str
    base_parameter: float
    signal_adjustment: float
    bounded_adjustment: float
    final_parameter: float
    governing_signal: str
    impact_bounded: bool = True

class EconomicTranslationEngine:
    """
    Translates calibrated semantic signals into strictly bounded economic parameters.
    Ensures mathematical transparency and deterministic authority invariants.
    """
    MAX_RECOVERABILITY_DELTA = 0.20 # Max ±20% recoverability shift
    MAX_RELATIONSHIP_COST_DELTA = 0.25 # Max ±25% relationship cost shift
    MAX_CONVERSION_DELTA = 0.20 # Max ±20% payment link conversion shift

    @classmethod
    def translate_signals_to_modifiers(
        cls,
        signals: List[SemanticSignal],
        base_recoverability: float = 0.70,
        base_relationship_cost: float = 500.0,
        base_conversion_rate: float = 0.40
    ) -> Dict[str, BoundedEconomicModifier]:
        calibrated_signals = signal_calibration_engine.resolve_conflicting_signals(signals)
        sig_map = {s.signal_type: s for s in calibrated_signals}

        modifiers: Dict[str, BoundedEconomicModifier] = {}

        # 1. Recoverability Adjustment (from failure_is_transient)
        if "failure_is_transient" in sig_map:
            sig = sig_map["failure_is_transient"]
            # Raw shift: (val - 0.50) * 2 * MAX_DELTA
            raw_shift = (sig.value - 0.50) * 2.0 * cls.MAX_RECOVERABILITY_DELTA
            bounded_shift = max(-cls.MAX_RECOVERABILITY_DELTA, min(cls.MAX_RECOVERABILITY_DELTA, raw_shift))
            final_val = max(0.05, min(0.99, base_recoverability + bounded_shift))
            modifiers["recoverability"] = BoundedEconomicModifier(
                parameter_name="recoverability",
                base_parameter=base_recoverability,
                signal_adjustment=round(raw_shift, 4),
                bounded_adjustment=round(bounded_shift, 4),
                final_parameter=round(final_val, 4),
                governing_signal="failure_is_transient"
            )

        # 2. Relationship Cost Adjustment (from customer_fatigue_signal)
        if "customer_fatigue_signal" in sig_map:
            sig = sig_map["customer_fatigue_signal"]
            # Higher fatigue increases relationship cost of aggressive actions
            raw_shift = (sig.value - 0.50) * 2.0 * cls.MAX_RELATIONSHIP_COST_DELTA * base_relationship_cost
            bounded_shift = max(-cls.MAX_RELATIONSHIP_COST_DELTA * base_relationship_cost, min(cls.MAX_RELATIONSHIP_COST_DELTA * base_relationship_cost, raw_shift))
            final_val = max(0.0, base_relationship_cost + bounded_shift)
            modifiers["relationship_cost"] = BoundedEconomicModifier(
                parameter_name="relationship_cost",
                base_parameter=base_relationship_cost,
                signal_adjustment=round(raw_shift, 2),
                bounded_adjustment=round(bounded_shift, 2),
                final_parameter=round(final_val, 2),
                governing_signal="customer_fatigue_signal"
            )

        # 3. Payment Link Conversion Adjustment (from customer_liquidity_likelihood)
        if "customer_liquidity_likelihood" in sig_map:
            sig = sig_map["customer_liquidity_likelihood"]
            raw_shift = (sig.value - 0.50) * 2.0 * cls.MAX_CONVERSION_DELTA
            bounded_shift = max(-cls.MAX_CONVERSION_DELTA, min(cls.MAX_CONVERSION_DELTA, raw_shift))
            final_val = max(0.05, min(0.95, base_conversion_rate + bounded_shift))
            modifiers["link_conversion_rate"] = BoundedEconomicModifier(
                parameter_name="link_conversion_rate",
                base_parameter=base_conversion_rate,
                signal_adjustment=round(raw_shift, 4),
                bounded_adjustment=round(bounded_shift, 4),
                final_parameter=round(final_val, 4),
                governing_signal="customer_liquidity_likelihood"
            )

        return modifiers

economic_translation_engine = EconomicTranslationEngine()
