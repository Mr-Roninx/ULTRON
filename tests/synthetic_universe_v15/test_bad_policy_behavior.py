import pytest
from synthetic_payment_universe.world_v15.counterfactual.shadow_evaluator import ShadowEvaluator

def test_bad_policies_underperform():
    evaluator = ShadowEvaluator(master_seed=789)
    results = evaluator.evaluate_decision(
        decision_id="dec_bad_1",
        amount=15000.0,
        is_natural_recovery=True,
        customer_fatigue=0.50
    )
    # Aggressive dunning incurs 150 externality damage + 65 op cost = negative NEV
    dunning = next(r for r in results if r.policy == "AGGRESSIVE_DUNNING")
    assert dunning.net_economic_value < 0.0
