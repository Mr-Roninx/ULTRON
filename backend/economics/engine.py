from typing import Dict, Any
from backend.economics.relationship import relationship_model, RelationshipState

class EconomicEngine:
    """
    Deterministic Net Expected Value (NEV) calculation:
    NEV = ExpectedRecovery + DownstreamValue - FinancialCost - OperationalCost - RelationshipCost - RiskCost
    """
    def calculate_nev(self, *args, **kwargs) -> float:
        if len(args) == 4:
            expected_recovery, action_cost, relationship_cost, risk_cost = args
            return float(expected_recovery - action_cost - relationship_cost - risk_cost)
        
        expected_recovery = float(kwargs.get("expected_recovery", args[0] if len(args) > 0 else 0.0))
        downstream_value = float(kwargs.get("downstream_value", args[1] if len(args) > 1 else 0.0))
        financial_cost = float(kwargs.get("financial_cost", args[2] if len(args) > 2 else 0.0))
        operational_cost = float(kwargs.get("operational_cost", args[3] if len(args) > 3 else 0.0))
        relationship_cost = float(kwargs.get("relationship_cost", args[4] if len(args) > 4 else 0.0))
        risk_cost = float(kwargs.get("risk_cost", args[5] if len(args) > 5 else 0.0))
        
        return expected_recovery + downstream_value - financial_cost - operational_cost - relationship_cost - risk_cost

    def evaluate_action(self, action_type: str, context: Dict[str, Any]) -> Dict[str, float]:
        expected_recovery = float(context.get("expected_yield", 0.0))
        risk_score = float(context.get("risk_score", 0.0))
        customer_id = context.get("customer_id")
        
        # 1. Action Costs (₹)
        FINANCIAL_COSTS = {
            "WAIT": 0.0,
            "RECONCILE": 0.5,
            "RETRY": 1.0,
            "RETRY_GATEWAY_A": 1.0,
            "RETRY_GATEWAY_B": 1.0,
            "RETRY_GATEWAY_C": 1.0,
            "SWITCH_PERMITTED_RAIL": 2.0,
            "REQUEST_CUSTOMER_ACTION": 2.0,
            "SEND_PAYMENT_LINK": 3.0,
            "SEND_MESSAGE": 1.5,
            "EMAIL": 0.5,
            "SMS": 1.0,
            "REGISTER_PTP": 5.0,
            "APPLY_DISCOUNT": 0.0,
            "REFUND_PAYMENT": 5.0,
            "ESCALATE": 50.0,
            "STOP": 0.0
        }
        financial_cost = FINANCIAL_COSTS.get(action_type, 5.0)

        # 2. Operational Costs (₹)
        OPERATIONAL_COSTS = {
            "WAIT": 0.0,
            "RECONCILE": 0.0,
            "RETRY": 1.0,
            "RETRY_GATEWAY_A": 1.0,
            "RETRY_GATEWAY_B": 1.0,
            "RETRY_GATEWAY_C": 1.0,
            "SWITCH_PERMITTED_RAIL": 3.0,
            "REQUEST_CUSTOMER_ACTION": 5.0,
            "SEND_PAYMENT_LINK": 2.0,
            "SEND_MESSAGE": 1.0,
            "EMAIL": 0.5,
            "SMS": 1.0,
            "REGISTER_PTP": 10.0,
            "APPLY_DISCOUNT": 2.0,
            "ESCALATE": 100.0, # Human escalation requires representative time
            "STOP": 0.0
        }
        operational_cost = OPERATIONAL_COSTS.get(action_type, 2.0)

        # 3. Downstream Value (Preservation of future renewals / LTV retention)
        # e.g., Smooth retry preserves 8% future subscription value; escalation damages it
        total_exposure = float(context.get("total_exposure", expected_recovery))
        if expected_recovery > 0:
            if action_type in ["RETRY", "RETRY_GATEWAY_A", "RETRY_GATEWAY_B", "RETRY_GATEWAY_C", "SWITCH_PERMITTED_RAIL"]:
                downstream_value = total_exposure * 0.08
            elif action_type in ["SEND_PAYMENT_LINK", "REGISTER_PTP"]:
                downstream_value = total_exposure * 0.04
            else:
                downstream_value = 0.0
        else:
            downstream_value = 0.0

        # 4. Relationship Cost
        rel_state: RelationshipState = context.get("relationship_state")
        if not rel_state and customer_id:
            rel_state = relationship_model.get_relationship(customer_id)

        if rel_state:
            relationship_cost = rel_state.calculate_relationship_cost(action_type)
        else:
            relationship_cost = 0.0

        # 5. Risk Cost (Value at Risk * Risk Score)
        risk_cost = expected_recovery * max(0.0, min(1.0, risk_score))

        nev = self.calculate_nev(
            expected_recovery=expected_recovery,
            downstream_value=downstream_value,
            financial_cost=financial_cost,
            operational_cost=operational_cost,
            relationship_cost=relationship_cost,
            risk_cost=risk_cost
        )

        return {
            "net_expected_value": round(nev, 2),
            "expected_recovery": round(expected_recovery, 2),
            "downstream_value": round(downstream_value, 2),
            "financial_cost": round(financial_cost, 2),
            "operational_cost": round(operational_cost, 2),
            "relationship_cost": round(relationship_cost, 2),
            "risk_cost": round(risk_cost, 2),
            "action_cost": round(financial_cost + operational_cost, 2) # For backwards compatibility
        }

economic_engine = EconomicEngine()
