import pytest
from synthetic_payment_universe.world_v14.population.customer_cohorts import PopulationCustomerEntity
from synthetic_payment_universe.world_v14.behavior.churn_dynamics import PopulationChurnDynamics

def test_churn_risk_dynamics():
    c_safe = PopulationCustomerEntity(customer_id="c1", fatigue_score=0.10, relationship_score=0.90)
    c_risk = PopulationCustomerEntity(customer_id="c2", fatigue_score=0.85, relationship_score=0.20)

    assert PopulationChurnDynamics.calculate_churn_risk(c_safe) < 0.10
    assert PopulationChurnDynamics.calculate_churn_risk(c_risk) > 0.50
