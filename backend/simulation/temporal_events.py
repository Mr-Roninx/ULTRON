import uuid
from typing import Any, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class SimulationEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:8]}")
    event_type: str
    scheduled_at: int
    payload: Dict[str, Any] = Field(default_factory=dict)
    source: str = "simulator"
    causal_parent_id: Optional[str] = None
    
    # Optional execution callback if the event has an autonomous effect on the environment
    # Using Any typing to avoid serialization issues, but expected to be Callable[[], None]
    execution_callback: Optional[Any] = Field(default=None, exclude=True)

class WakeupEvent(SimulationEvent):
    event_type: str = "WAKEUP"
    agent_id: str

class PaymentResultEvent(SimulationEvent):
    event_type: str = "PAYMENT_RESULT"
    payment_id: str
    success: bool

class GatewayHealthEvent(SimulationEvent):
    event_type: str = "GATEWAY_HEALTH"
    gateway_id: str
    health: float

class WebhookEvent(SimulationEvent):
    event_type: str = "WEBHOOK_DELAY"
    target_id: str

class CustomerResponseEvent(SimulationEvent):
    event_type: str = "CUSTOMER_RESPONSE"
    customer_id: str
    response_type: str

class PTPEvent(SimulationEvent):
    event_type: str = "PTP"
    customer_id: str
    payment_id: str

class SettlementEvent(SimulationEvent):
    event_type: str = "SETTLEMENT"
    payment_id: str

class RetryDueEvent(SimulationEvent):
    event_type: str = "RETRY_DUE"
    payment_id: str

class ChaosEvent(SimulationEvent):
    event_type: str = "CHAOS"
    chaos_type: str
