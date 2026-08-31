import pytest
from synthetic_payment_universe.world_v13.counterfactual.fork import CivilizationCounterfactualForkEngine

def test_counterfactual_5_branch_outcomes():
    eng = CivilizationCounterfactualForkEngine(master_seed=444)
    outcomes = eng.evaluate_branches("dp_fork_1", amount=24700.0, failure_code="91", natural_recovery=False)
    assert len(outcomes) == 5
    types = {o.action_type for o in outcomes}
    assert types == {"WAIT", "RETRY", "SEND_PAYMENT_LINK", "SWITCH_GATEWAY", "ESCALATE"}
