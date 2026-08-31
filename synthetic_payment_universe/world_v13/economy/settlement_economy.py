from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class SettlementBatch(BaseModel):
    batch_id: str
    gateway_id: str
    merchant_id: str
    gross_amount: float
    net_amount: float
    fee_amount: float
    currency: str = "INR"
    status: str = "SETTLED" # PENDING, CLEARING, SETTLED, DISPUTED
    settled_at: int

class SettlementEconomyEngine:
    """
    Simulates gateway clearing windows, delayed batch settlements, and net funds transfer.
    """
    @staticmethod
    def create_batch(
        gateway_id: str,
        merchant_id: str,
        payments: List[Any],
        timestamp: int,
        fee_rate: float = 0.015
    ) -> SettlementBatch:
        gross = sum(p.amount for p in payments)
        fees = round(gross * fee_rate, 2)
        net = round(gross - fees, 2)
        return SettlementBatch(
            batch_id=f"stl_{gateway_id}_{merchant_id}_{timestamp}",
            gateway_id=gateway_id,
            merchant_id=merchant_id,
            gross_amount=round(gross, 2),
            net_amount=net,
            fee_amount=fees,
            status="SETTLED",
            settled_at=timestamp
        )
