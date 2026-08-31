import pytest
from synthetic_payment_universe.world_v14.economy.feedback_loops import EconomicFeedbackLoops

def test_gateway_congestion_loop_b():
    base_health = 0.95
    # Normal traffic -> unchanged health
    h_normal = EconomicFeedbackLoops.apply_loop_b_congestion(active_traffic=1000, gateway_capacity=2000, base_health=base_health)
    assert h_normal == 0.95

    # Heavy overload traffic -> degraded health
    h_degraded = EconomicFeedbackLoops.apply_loop_b_congestion(active_traffic=5000, gateway_capacity=2000, base_health=base_health)
    assert h_degraded < 0.95
