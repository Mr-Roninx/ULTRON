import pytest
from synthetic_payment_universe.world_v12.entities.customer import Customer
from synthetic_payment_universe.world_v12.behavior.customer_behavior import CustomerBehaviorEngine

def test_customer_fatigue_and_behavior():
    fresh_cust = Customer(customer_id="c_fresh", fatigue_score=0.10, latent_profile="LOYAL_CUSTOMER")
    fatigued_cust = Customer(customer_id="c_fatigued", fatigue_score=0.85, latent_profile="HIGH_FATIGUE")

    # Fresh loyal customer vs Fatigued customer
    _, conv_fresh, _ = CustomerBehaviorEngine.evaluate_communication_response(fresh_cust, "WHATSAPP", subseed=42)
    _, conv_fatigued, _ = CustomerBehaviorEngine.evaluate_communication_response(fatigued_cust, "WHATSAPP", subseed=42)

    assert conv_fresh is True
    assert conv_fatigued is False
