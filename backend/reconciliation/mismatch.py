from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from backend.providers.models import CanonicalPaymentState

class ReconciliationMismatch(BaseModel):
    internal_payment_id: str
    provider: str
    provider_payment_id: str
    internal_state: CanonicalPaymentState
    provider_state: CanonicalPaymentState
    amount_discrepancy_minor: int = 0
    reason: str
    detected_at: int
    resolved_at: Optional[int] = None
    resolution_action: Optional[str] = None
