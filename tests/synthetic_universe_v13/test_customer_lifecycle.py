import pytest
from synthetic_payment_universe.world_v13.economy.customer_economy import CustomerEconomyEntity, CustomerEconomyEngine, CustomerEconomicState

def test_customer_lifecycle_transitions():
    cust = CustomerEconomyEntity(customer_id="c_test_1", fatigue_score=0.0)
    # Apply outreach
    CustomerEconomyEngine.apply_contact(cust, "WHATSAPP", 1760000000)
    assert cust.fatigue_score == 0.12

    # High contact -> High fatigue
    for _ in range(6):
        CustomerEconomyEngine.apply_contact(cust, "WHATSAPP", 1760000000)
    assert cust.state == CustomerEconomicState.HIGH_FATIGUE

    # Decay fatigue
    CustomerEconomyEngine.decay_fatigue(cust, days_passed=10)
    assert cust.fatigue_score < 0.40
