import pytest
from synthetic_payment_universe.world_v14.population.merchant_cohorts import PopulationMerchantEntity, MerchantCohort, MerchantLifecycleState
from synthetic_payment_universe.world_v14.population.lifecycle import PopulationLifecycleEngine

def test_merchant_cohort_emergence():
    m1 = PopulationMerchantEntity(merchant_id="m1", growth_rate=0.08)
    m2 = PopulationMerchantEntity(merchant_id="m2", monthly_volume=1000000.0, outstanding_receivables=500000.0)

    PopulationLifecycleEngine.evaluate_merchant_lifecycle(m1)
    PopulationLifecycleEngine.evaluate_merchant_lifecycle(m2)

    assert m1.lifecycle_state == MerchantLifecycleState.GROWING
    assert m2.lifecycle_state == MerchantLifecycleState.STRESSED
