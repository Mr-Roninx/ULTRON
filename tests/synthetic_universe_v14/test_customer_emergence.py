import pytest
from synthetic_payment_universe.world_v14.population.customer_cohorts import PopulationCustomerEntity, CustomerCohort, CustomerLifecycleState
from synthetic_payment_universe.world_v14.population.lifecycle import PopulationLifecycleEngine

def test_customer_cohort_emergence():
    c1 = PopulationCustomerEntity(customer_id="c1", cohort=CustomerCohort.HIGHLY_LOYAL, relationship_score=0.95)
    c2 = PopulationCustomerEntity(customer_id="c2", cohort=CustomerCohort.VOLATILE_INCOME_SMB, churn_probability=0.75)

    PopulationLifecycleEngine.evaluate_customer_lifecycle(c1, days_since_last_purchase=5)
    PopulationLifecycleEngine.evaluate_customer_lifecycle(c2, days_since_last_purchase=5)

    assert c1.lifecycle_state == CustomerLifecycleState.ACTIVE
    assert c2.lifecycle_state == CustomerLifecycleState.CHURNED
