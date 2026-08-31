from typing import List, Dict, Any
from financial.authority import authority_engine, AuthorityLevel
from financial.policy import policy_engine, PolicyViolationError
from financial.risk import risk_engine, RiskViolationError

class FeasibleActionEngine:
    def __init__(self):
        self.all_actions = [
            "WAIT",
            "RECONCILE",
            "RETRY",
            "RETRY_GATEWAY_A",
            "RETRY_GATEWAY_B",
            "RETRY_GATEWAY_C",
            "SWITCH_PERMITTED_RAIL",
            "REQUEST_CUSTOMER_ACTION",
            "SEND_PAYMENT_LINK",
            "SEND_MESSAGE",
            "REGISTER_PTP",
            "APPLY_DISCOUNT",
            "REFUND_PAYMENT",
            "ESCALATE",
            "STOP"
        ]
        
    def get_feasible_actions(self, context: Dict[str, Any], max_risk: float, current_authority: AuthorityLevel, payload_overrides: Dict[str, dict] = None) -> List[str]:
        feasible = []
        if payload_overrides is None:
            payload_overrides = {}
            
        for action in self.all_actions:
            payload = payload_overrides.get(action, {})
            # 1. Authority Check
            if not authority_engine.is_authorized(action, current_authority):
                continue
                
            # 2. Risk Check
            try:
                risk_engine.validate(action, max_risk, payload)
            except RiskViolationError:
                continue
                
            # 3. Policy Check
            try:
                policy_engine.validate(action, context, payload)
            except PolicyViolationError:
                continue
                
            feasible.append(action)
            
        return feasible

feasible_action_engine = FeasibleActionEngine()
