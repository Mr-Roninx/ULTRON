from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class MicroEconomicEvent(BaseModel):
    event_id: str
    event_type: str # PAYMENT_INITIATED, PAYMENT_AUTHORIZED, PAYMENT_FAILED, RETRY, PAYMENT_LINK_SENT, etc.
    entity_id: str
    timestamp: int
    visibility: str = "OBSERVABLE"
    causal_parent_id: Optional[str] = None
    sequence_index: int = 0
    payload: Dict[str, Any] = Field(default_factory=dict)

    def __lt__(self, other: "MicroEconomicEvent") -> bool:
        if self.timestamp != other.timestamp:
            return self.timestamp < other.timestamp
        return self.sequence_index < other.sequence_index
