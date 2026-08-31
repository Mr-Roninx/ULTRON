import pytest
from synthetic_payment_universe.world_v15.counterfactual.shadow_evaluator import ShadowEvaluator

def test_shadow_evaluator_11_policies():
    evaluator = ShadowEvaluator(master_seed=456)
    results = evaluator.evaluate_decision(
        decision_id="dec_fair_1",
        amount=30000.0,
        is_natural_recovery=True,
        customer_fatigue=0.10
    )
    assert len(results) == 11
    policy_names = {r.policy for r in results}
    assert "ALWAYS_RETRY" in policy_names
    assert "AGGRESSIVE_DUNNING" in policy_names
    assert "ALWAYS_WAIT" in policy_names
    assert "ULTRON_FULL" in policy_names
