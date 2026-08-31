import pytest
from synthetic_payment_universe.world_v14.causal.attribution_engine import CausalAttributionEngine

def test_incremental_causal_attribution():
    # Natural recovery: 15,000; ULTRON recovery: 38,000; Cost: 250
    lift = CausalAttributionEngine.calculate_causal_lift(
        ultron_recovery=38000.0,
        control_natural_recovery=15000.0,
        ultron_operational_cost=250.0
    )
    assert lift["incremental_recovery"] == 23000.0
    assert lift["incremental_net_economic_value"] == 22750.0
