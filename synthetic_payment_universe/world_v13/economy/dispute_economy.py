from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class DisputeCivilizationEntity(BaseModel):
    dispute_id: str
    payment_id: str
    dispute_type: str = "CHARGEBACK" # CHARGEBACK, INQUIRY, FRAUD_CLAIM
    status: str = "OPEN" # OPEN, UNDER_REVIEW, WON, LOST
    amount: float
    created_at: int
    resolved_at: Optional[int] = None

class DisputeEconomyEngine:
    """
    Manages customer chargebacks, dispute defense, and refund processing.
    """
    @staticmethod
    def resolve_dispute(dispute: DisputeCivilizationEntity, merchant_won: bool, timestamp: int):
        dispute.status = "WON" if merchant_won else "LOST"
        dispute.resolved_at = timestamp
