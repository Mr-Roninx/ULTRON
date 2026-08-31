import pytest
from synthetic_payment_universe.world_v14.counterfactual.civilization_fork import CivilizationForkEngine

def test_5_branch_isolation():
    fork_eng = CivilizationForkEngine(master_seed=999)
    branches = fork_eng.evaluate_arms("dec_iso_1", amount=20000.0, natural_recovery=False)
    assert len(branches) == 5
    arm_names = {b.arm_name for b in branches}
    assert arm_names == {"CONTROL_NO_ULTRON", "RULE_BASED", "ULTRON_LLM_OFF", "ULTRON_LLM_ON", "ULTRON_FULL"}

    control = next(b for b in branches if b.arm_name == "CONTROL_NO_ULTRON")
    assert control.recovered_revenue == 0.0
