from enum import Enum
from typing import Dict, Any, Optional

class ConfidenceTier(str, Enum):
    HIGH_CONFIDENCE = "HIGH_CONFIDENCE"
    MEDIUM_CONFIDENCE = "MEDIUM_CONFIDENCE"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"

class RiskViolationError(Exception):
    pass

class RiskEngine:
    """
    Calibrated Risk Policy engine ensuring fail-closed, bounded autonomous execution.
    """
    def __init__(self):
        self.base_risk = {
            "WAIT": 0.0,
            "RECONCILE": 0.01,
            "RETRY": 0.08,
            "RETRY_GATEWAY_A": 0.08,
            "RETRY_GATEWAY_B": 0.08,
            "RETRY_GATEWAY_C": 0.08,
            "SWITCH_PERMITTED_RAIL": 0.12,
            "SEND_MESSAGE": 0.05,
            "EMAIL": 0.04,
            "SMS": 0.06,
            "SEND_PAYMENT_LINK": 0.15,
            "REQUEST_CUSTOMER_ACTION": 0.15,
            "REGISTER_PTP": 0.20,
            "APPLY_DISCOUNT": 0.45,
            "REFUND_PAYMENT": 0.80,
            "ESCALATE": 0.0,
            "STOP": 0.0
        }

    def calculate_action_risk(
        self,
        action_type: str,
        payload: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> float:
        payload = payload or {}
        context = context or {}

        risk = self.base_risk.get(action_type, 0.50)

        # 1. Discount amount scaling
        if action_type == "APPLY_DISCOUNT":
            amount = float(payload.get("amount", 0.0))
            if amount > 5000:
                risk *= 1.8
            elif amount > 2000:
                risk *= 1.3

        # 2. Reversibility and customer sensitivity
        customer_segment = context.get("customer", {}).get("segment", "SMB")
        if customer_segment == "B2B_ENTERPRISE" and action_type in ["ESCALATE", "REQUEST_CUSTOMER_ACTION"]:
            risk *= 1.25

        # 3. High contact fatigue
        recent_contacts = context.get("customer", {}).get("recent_contacts", 0)
        if recent_contacts >= 3 and action_type in ["SEND_MESSAGE", "SEND_PAYMENT_LINK", "SMS"]:
            risk *= 1.5

        return round(min(1.0, risk), 4)

    def determine_confidence_tier(self, risk_score: float) -> ConfidenceTier:
        if risk_score <= 0.15:
            return ConfidenceTier.HIGH_CONFIDENCE
        elif risk_score <= 0.40:
            return ConfidenceTier.MEDIUM_CONFIDENCE
        else:
            return ConfidenceTier.LOW_CONFIDENCE

    def validate(
        self,
        action_type: str,
        max_risk: float,
        payload: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        risk = self.calculate_action_risk(action_type, payload, context)
        
        if risk > max_risk:
            raise RiskViolationError(
                f"Action '{action_type}' carries calculated risk {risk:.2f} exceeding maximum allowed risk threshold of {max_risk:.2f} (exceeds mission limit)."
            )
            
        return True

risk_engine = RiskEngine()
