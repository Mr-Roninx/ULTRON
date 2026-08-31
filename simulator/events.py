from pydantic import BaseModel
from typing import Optional, Dict, Any

class DomainEvent(BaseModel):
    event_id: str
    event_type: str
    entity_type: str         # "PAYMENT", "INVOICE", "CHECKOUT", "CUSTOMER"
    entity_id: str
    customer_id: str
    timestamp: int
    previous_state: Optional[str] = None
    new_state: str
    payload: Dict[str, Any]
