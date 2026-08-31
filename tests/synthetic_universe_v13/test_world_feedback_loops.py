import pytest
from synthetic_payment_universe.world_v13.economy.customer_economy import CustomerEconomyEntity, CustomerEconomyEngine
from synthetic_payment_universe.world_v13.economy.relationship_economy import CustomerRelationshipEngine

def test_recovery_to_relationship_feedback():
    cust = CustomerEconomyEntity(customer_id="c_rel_1", relationship_score=0.80, churn_probability=0.08)
    CustomerEconomyEngine.record_successful_recovery(cust, amount=25000.0, timestamp=1760000000)
    assert cust.relationship_score == 0.85
    assert cust.churn_probability < 0.08
