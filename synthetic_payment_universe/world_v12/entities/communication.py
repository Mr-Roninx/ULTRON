from typing import Dict, Any, Optional
from synthetic_payment_universe.world_v12.entities.base import WorldEntity

class Communication(WorldEntity):
    communication_id: str
    customer_id: str
    channel: str # EMAIL, SMS, WHATSAPP, VOICE, IN_APP, PAYMENT_LINK
    template_id: str
    sent_at: int
    delivered_at: Optional[int] = None
    opened_at: Optional[int] = None
    clicked_at: Optional[int] = None
    responded_at: Optional[int] = None
    customer_response: Optional[str] = None
    fatigue_delta: float = 0.10
    converted: bool = False

class RecoveryAction(WorldEntity):
    action_id: str
    customer_id: str
    payment_id: str
    action_type: str # WAIT, RETRY, SEND_PAYMENT_LINK, SWITCH_GATEWAY, ESCALATE
    channel: Optional[str] = None
    target_gateway: Optional[str] = None
    executed_at: int = 1760000000
    status: str = "EXECUTED"
