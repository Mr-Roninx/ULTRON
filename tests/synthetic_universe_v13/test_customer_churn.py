import pytest
from synthetic_payment_universe.world_v13.economy.customer_economy import CustomerEconomyEntity
from synthetic_payment_universe.world_v13.behavior.churn import ChurnModel

def test_customer_churn_risk_evaluation():
    cust = CustomerEconomyEntity(customer_id="c_churn", fatigue_score=0.90, relationship_score=0.20)
    risk = ChurnModel.evaluate_churn_risk(cust)
    assert risk > 0.70
