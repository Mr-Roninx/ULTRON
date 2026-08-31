from typing import List, Dict, Any
import simulator.world
from backend.agent.schemas import AgentIntent
from backend.economics.engine import economic_engine
from simulator.customer_state import customer_state_engine
from financial.feasible_actions import feasible_action_engine
from financial.authority import AuthorityLevel
from backend.tools.registry import registry

class CounterfactualEvaluator:
    def __init__(self):
        pass

    def calculate_regret(self, customer_id: str, chosen_intent: AgentIntent, max_risk: float, authority: str) -> Dict[str, Any]:
        """
        Calculates the regret of the chosen action compared to the optimal feasible action.
        Regret = Max(Alternative NEV) - Chosen NEV
        """
        original_world = simulator.world.world
        context = customer_state_engine.get_snapshot(customer_id)
        
        # Get all feasible actions for the current state
        feasible_actions = feasible_action_engine.get_feasible_actions(context, max_risk, AuthorityLevel(authority))
        
        best_nev = -float('inf')
        best_action = None
        alternative_nevs = {}
        
        # We need a baseline expected yield for actions to calculate NEV.
        # In a full LLM system, we might ask the LLM to predict yield for each, 
        # but for the engine we can use a heuristic or the chosen intent's yield as a baseline.
        baseline_yield = chosen_intent.expected_yield

        forked_context = dict(context)
        forked_context["expected_yield"] = baseline_yield

        for action in feasible_actions:
            calc = economic_engine.evaluate_action(action, forked_context)
            nev = calc["net_expected_value"]
            alternative_nevs[action] = nev
            
            if nev > best_nev:
                best_nev = nev
                best_action = action
                
        # Calculate chosen NEV
        # The chosen intent might have a specific expected yield predicted by LLM
        context["expected_yield"] = chosen_intent.expected_yield
        chosen_calc = economic_engine.evaluate_action(chosen_intent.action_type, context)
        chosen_nev = chosen_calc["net_expected_value"]
        
        regret = max(0.0, best_nev - chosen_nev)
        
        return {
            "regret": regret,
            "chosen_action": chosen_intent.action_type,
            "chosen_nev": chosen_nev,
            "best_alternative": best_action,
            "best_nev": best_nev,
            "all_alternatives": alternative_nevs
        }

counterfactual_evaluator = CounterfactualEvaluator()
