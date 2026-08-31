import uuid
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from simulator.clock import clock
from synthetic_payment_universe.schema.visibility import EventVisibility

class UnifiedTemporalEvent(BaseModel):
    """
    Unified Event representation across the entire Synthetic Universe timeline.
    Enforces causal lineage, strict timestamping, and visibility controls.
    """
    event_id: str = Field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:10]}")
    event_type: str
    entity_id: str
    timestamp: int
    source: str = "SIMULATION_WORLD"
    causal_parent_id: Optional[str] = None
    visibility: EventVisibility = EventVisibility.OBSERVABLE
    payload: Dict[str, Any] = Field(default_factory=dict)
