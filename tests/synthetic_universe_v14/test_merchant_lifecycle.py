import pytest
from synthetic_payment_universe.world_v14.population.merchant_cohorts import PopulationMerchantEntity, MerchantLifecycleState
from synthetic_payment_universe.world_v14.population.lifecycle import PopulationLifecycleEngine

def test_merchant_lifecycle_stress():
    m = PopulationMerchantEntity(merchant_id="m_stress", monthly_volume=5000000.0, outstanding_receivables=3000000.0)
    PopulationLifecycleEngine.evaluate_merchant_lifecycle(m)
    assert m.lifecycle_state == MerchantLifecycleState.STRESSED
