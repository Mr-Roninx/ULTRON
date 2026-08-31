import pytest
from synthetic_payment_universe.world_v15.behavior.customer_heterogeneity import HeterogeneousCustomerEntity
from synthetic_payment_universe.world_v15.behavior.ltv_dynamics import CustomerLTVDynamics

def test_long_term_ltv_projection():
    c_loyal = HeterogeneousCustomerEntity(customer_id="c1", tier="SMB", spending_capacity=20000.0, relationship_score=0.95)
    c_churned = HeterogeneousCustomerEntity(customer_id="c2", tier="SMB", spending_capacity=20000.0, relationship_score=0.10, churn_status="CHURNED")

    ltv_365 = CustomerLTVDynamics.project_future_revenue(c_loyal, 365)
    assert ltv_365 > 400000.0

    ltv_churned = CustomerLTVDynamics.project_future_revenue(c_churned, 365)
    assert ltv_churned == 0.0
