import pytest
from synthetic_payment_universe.world_v15.behavior.intervention_effects import InterventionEffectsEngine

def test_negative_intervention_consequences():
    # Unnecessary outreach on natural recovery
    effect = InterventionEffectsEngine.evaluate_outreach_effect(
        action_type="AGGRESSIVE_DUNNING",
        channel="WHATSAPP",
        current_fatigue=0.75,
        is_natural_recovery=True
    )
    assert effect.opt_out_triggered is True
    assert effect.churn_triggered is True
    assert effect.externality_cost > 1000.0
    assert effect.relationship_delta < -0.20
