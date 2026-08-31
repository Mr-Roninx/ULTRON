import pytest
from synthetic_payment_universe.world_v15.behavior.intervention_effects import InterventionEffectsEngine

def test_hard_case_natural_recovery_dominates():
    # Customer will recover naturally -> any aggressive outreach causes harm
    res = InterventionEffectsEngine.evaluate_outreach_effect(
        action_type="SEND_PAYMENT_LINK",
        channel="WHATSAPP",
        current_fatigue=0.20,
        is_natural_recovery=True
    )
    assert res.externality_cost > 0.0
    assert res.relationship_delta < 0.0
