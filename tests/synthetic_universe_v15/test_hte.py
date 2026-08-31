import pytest
from synthetic_payment_universe.world_v15.behavior.customer_heterogeneity import HeterogeneousCustomerEntity, CustomerSensitivityType
from synthetic_payment_universe.world_v15.behavior.intervention_effects import InterventionEffectsEngine

def test_heterogeneous_treatment_effects():
    # Sensitive customer suffers higher fatigue
    eff_sensitive = InterventionEffectsEngine.evaluate_outreach_effect("SEND_PAYMENT_LINK", "VOICE", 0.30)
    eff_standard = InterventionEffectsEngine.evaluate_outreach_effect("SEND_PAYMENT_LINK", "EMAIL", 0.30)

    assert eff_sensitive.fatigue_delta > eff_standard.fatigue_delta
