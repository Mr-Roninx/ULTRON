import time
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from backend.providers.models import CanonicalPaymentFailureClass, CanonicalPaymentState

class RealMissionState(str, Enum):
    NEW = "NEW"
    OBSERVING = "OBSERVING"
    DIAGNOSING = "DIAGNOSING"
    PLANNING = "PLANNING"
    AUTHORIZED = "AUTHORIZED"
    EXECUTING = "EXECUTING"
    AWAITING_PROVIDER = "AWAITING_PROVIDER"
    RECONCILING = "RECONCILING"
    RECOVERED = "RECOVERED"
    FAILED = "FAILED"
    ESCALATED = "ESCALATED"
    STOPPED = "STOPPED"

class RealPaymentMission(BaseModel):
    mission_id: str
    customer_id: str
    merchant_id: str
    internal_payment_id: str
    provider: str
    provider_payment_id: str
    amount_minor: int
    currency: str = "INR"
    failure_class: Optional[CanonicalPaymentFailureClass] = None
    current_state: RealMissionState = RealMissionState.NEW
    payment_state: CanonicalPaymentState = CanonicalPaymentState.CREATED
    attempt_count: int = 0
    communication_count: int = 0
    created_at: int = Field(default_factory=lambda: int(time.time()))
    updated_at: int = Field(default_factory=lambda: int(time.time()))
    next_wakeup: Optional[int] = None
    action_history: List[Dict[str, Any]] = Field(default_factory=list)
    memory_reference_ids: List[str] = Field(default_factory=list)
    active_payment_link_id: Optional[str] = None

    def record_action(self, action_type: str, status: str, payload: Dict[str, Any]):
        self.action_history.append({
            "action_type": action_type,
            "status": status,
            "timestamp": int(time.time()),
            "payload": payload
        })
        self.updated_at = int(time.time())
