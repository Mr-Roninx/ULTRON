from typing import List, Dict, Any, Optional
from synthetic_payment_universe.world_v13.counterfactual.fork import CivilizationCounterfactualForkEngine, LongHorizonBranchOutcome

class LongHorizonCounterfactualEvaluator:
    """
    Computes comparative regret, oracle optimal actions, and long-horizon policy evaluation.
    """
    def __init__(self, fork_engine: CivilizationCounterfactualForkEngine):
        self.fork_engine = fork_engine

    def find_optimal_action(self, outcomes: List[LongHorizonBranchOutcome]) -> LongHorizonBranchOutcome:
        return max(outcomes, key=lambda x: x.net_economic_value)

    def calculate_regret(self, chosen_action: str, outcomes: List[LongHorizonBranchOutcome]) -> float:
        optimal = self.find_optimal_action(outcomes)
        chosen = next((o for o in outcomes if o.action_type == chosen_action), None)
        if not chosen:
            return 0.0
        return max(0.0, round(optimal.net_economic_value - chosen.net_economic_value, 2))
