import pytest
from simulator.clock import clock
from backend.intelligence.semantic_signal import SemanticSignal
from backend.intelligence.economic_translation import economic_translation_engine

def test_economic_translation_bounds():
    clock.reset(1760000000)
    # Extreme transient signal cannot increase recoverability by more than 20%
    extreme_sig = SemanticSignal(
        signal_type="failure_is_transient", value=1.0, confidence=1.0,
        evidence_reference="Extreme claim", observed_timestamp=clock.now()
    )
    modifiers = economic_translation_engine.translate_signals_to_modifiers([extreme_sig], base_recoverability=0.70)
    assert "recoverability" in modifiers
    mod = modifiers["recoverability"]
    assert mod.final_parameter <= 0.90
    assert mod.bounded_adjustment <= 0.20
