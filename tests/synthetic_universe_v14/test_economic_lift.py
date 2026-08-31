import pytest
from synthetic_payment_universe.world_v14.counterfactual.civilization_fork import CivilizationForkEngine

def test_economic_lift_comparison():
    fork_eng = CivilizationForkEngine(master_seed=123)
    arms = fork_eng.evaluate_arms("lift_dec_1", amount=25000.0, natural_recovery=True)
    control = next(a for a in arms if a.arm_name == "CONTROL_NO_ULTRON")
    ultron = next(a for a in arms if a.arm_name == "ULTRON_FULL")

    assert control.recovered_revenue == 25000.0 # Natural recovery captured
    assert ultron.net_economic_value > 0
