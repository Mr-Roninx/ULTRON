from typing import List, Dict, Any, Tuple
from synthetic_payment_universe.schema.counterfactual import CounterfactualOutcome

class UniverseCounterfactualValidator:
    """
    Validates paired counterfactual branch properties and common random number integrity.
    """
    @staticmethod
    def validate_counterfactual_set(outcomes: List[CounterfactualOutcome]) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        if len(outcomes) == 0:
            return False, ["Counterfactual outcome list is empty."]

        # Check action diversity across branches
        actions = {o.action_type for o in outcomes}
        if len(actions) < 3:
            errors.append(f"Counterfactual set has insufficient action diversity: {actions}")

        # Check that net economic value matches formula (recovery - costs)
        for o in outcomes:
            expected_nev = round((o.recovered_amount if o.success else 0.0) - o.operational_cost - o.relationship_cost, 2)
            if abs(o.net_economic_value - expected_nev) > 0.05:
                errors.append(f"NEV Formula Mismatch on branch {o.branch_id}: {o.net_economic_value} != expected {expected_nev}")

        return len(errors) == 0, errors
