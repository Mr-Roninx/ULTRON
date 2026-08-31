import pytest
from synthetic_payment_universe.world_v13.counterfactual.fork import CivilizationCounterfactualForkEngine

def test_natural_recovery_isolated_branch():
    fork_eng = CivilizationCounterfactualForkEngine(master_seed=123)
    outcomes = fork_eng.evaluate_branches("dp_nat_1", amount=35000.0, failure_code="91", natural_recovery=True)
    wait_b = next(o for o in outcomes if o.action_type == "WAIT")
    assert wait_b.immediate_recovered_amount == 35000.0
    assert wait_b.net_economic_value == 35000.0
