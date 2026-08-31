from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class EconomicEvent(BaseModel):
    event_id: str
    event_type: str # PAYMENT_CREATED, PAYMENT_FAILED, PAYMENT_SETTLED, SUBSCRIPTION_RENEWAL_DUE, INVOICE_DUE, etc.
    entity_id: str
    timestamp: int
    visibility: str = "OBSERVABLE" # OBSERVABLE, HIDDEN, EVALUATOR_ONLY
    causal_parent_id: Optional[str] = None
    sequence_index: int = 0
    payload: Dict[str, Any] = Field(default_factory=dict)

    def __lt__(self, other: "EconomicEvent") -> bool:
        if self.timestamp != other.timestamp:
            return self.timestamp < other.timestamp
        return self.sequence_index < other.sequence_index
