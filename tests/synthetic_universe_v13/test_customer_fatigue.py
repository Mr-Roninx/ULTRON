import pytest
from synthetic_payment_universe.world_v13.economy.customer_economy import CustomerEconomyEntity
from synthetic_payment_universe.world_v13.behavior.fatigue import FatigueDynamics

def test_contact_fatigue_penalty():
    fresh_cust = CustomerEconomyEntity(customer_id="c_f1", fatigue_score=0.10)
    fatigued_cust = CustomerEconomyEntity(customer_id="c_f2", fatigue_score=0.85)

    assert FatigueDynamics.calculate_contact_fatigue_penalty(fresh_cust) == 1.0
    assert FatigueDynamics.calculate_contact_fatigue_penalty(fatigued_cust) == 0.25
