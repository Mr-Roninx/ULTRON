import pytest
from synthetic_payment_universe.world_v15.counterfactual.shadow_evaluator import ShadowEvaluator

def test_shadow_evaluator_branch_independence():
    ev = ShadowEvaluator(master_seed=111)
    res = ev.evaluate_decision("dec_ind_1", 20000.0, is_natural_recovery=False)
    assert len(res) == 11
    ultron = next(r for r in res if r.policy == "ULTRON_FULL")
    assert ultron.gross_recovery > 0.0
