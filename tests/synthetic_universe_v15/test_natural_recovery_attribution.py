import pytest
from synthetic_payment_universe.world_v15.attribution.attribution_tiers import MultiTierAttributionEngine

def test_natural_recovery_attribution_isolation():
    # If customer would have paid naturally, direct incremental must be zero!
    attr = MultiTierAttributionEngine.classify_attribution(
        recovered_amount=45000.0,
        is_natural_recovery=True,
        forward_ltv_delta=0.0,
        externality_cost=0.0,
        operational_cost=18.0
    )
    assert attr.direct_incremental_revenue == 0.0
    assert attr.non_incremental_recovery == 45000.0
    assert attr.net_economic_value == -18.0 # Lost operational cost!
