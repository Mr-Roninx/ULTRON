import random
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field

class PaymentCivilizationEntity(BaseModel):
    payment_id: str
    customer_id: str
    merchant_id: str
    amount: float
    currency: str = "INR"
    status: str = "CREATED" # CREATED, AUTHORIZED, SETTLED, FAILED, DISPUTED, REFUNDED
    rail: str = "CARD"
    gateway_id: str = "GATEWAY_A"
    failure_code: Optional[str] = None
    created_at: int = 1760000000
    settled_at: Optional[int] = None
    attempt_count: int = 0

class PaymentEconomyEngine:
    """
    Manages payment authorization, failure code attribution, and settlement state transitions.
    """
    @staticmethod
    def process_authorization(
        payment: PaymentCivilizationEntity,
        gateway_health: float,
        timestamp: int,
        subseed: int = 123
    ) -> Tuple[bool, Optional[str]]:
        rng = random.Random(subseed + payment.attempt_count)
        payment.attempt_count += 1

        # Effective authorization rate influenced by gateway health
        if rng.random() < gateway_health:
            payment.status = "AUTHORIZED"
            payment.failure_code = None
            return True, None
        else:
            payment.status = "FAILED"
            # Realistic ISO / Gateway failure code distribution
            codes = ["91", "51", "14", "TO", "61", "41", "AMBIGUOUS_SETTLEMENT"]
            payment.failure_code = rng.choice(codes)
            return False, payment.failure_code
