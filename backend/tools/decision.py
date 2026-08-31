from typing import Dict, Any, List
from financial.feasible_actions import feasible_action_engine
from financial.authority import AuthorityLevel
from backend.economics.engine import economic_engine
from simulator.customer_state import customer_state_engine

class DecisionTools:
    def get_feasible_actions(self, customer_id: str, max_risk: float, current_authority: str, payload_overrides: Dict[str, dict] = None) -> List[str]:
        context = customer_state_engine.get_snapshot(customer_id)
        authority = AuthorityLevel(current_authority)
        return feasible_action_engine.get_feasible_actions(context, max_risk, authority, payload_overrides)

    def calculate_action_value(self, action_type: str, context: Dict[str, Any]) -> Dict[str, float]:
        """
        Uses the economic engine to calculate the Net Expected Value.
        Context needs to include expected_yield and relationship_state, etc.
        """
        return economic_engine.evaluate_action(action_type, context)

decision_tools = DecisionTools()
