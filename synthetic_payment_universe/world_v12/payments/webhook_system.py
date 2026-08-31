import random
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class WebhookDelivery(BaseModel):
    webhook_id: str
    event_type: str
    payload: Dict[str, Any]
    idempotency_key: str
    dispatched_at: int
    delivered_at: Optional[int] = None
    status: str = "DELIVERED" # DELIVERED, DELAYED, DROPPED, DUPLICATE
    attempt_count: int = 1

class SimulatedWebhookSystem:
    """
    Simulates asynchronous webhook deliveries, network dropouts, delays, and duplicates.
    """
    def __init__(self, subseed: int = 12345):
        self.rng = random.Random(subseed)
        self.delivered_keys: Dict[str, int] = {}
        self.deliveries: List[WebhookDelivery] = []

    def dispatch(
        self,
        event_type: str,
        payload: Dict[str, Any],
        idempotency_key: str,
        timestamp: int,
        force_delay_seconds: int = 0,
        force_drop: bool = False
    ) -> WebhookDelivery:
        wid = f"wh_{idempotency_key}_{len(self.deliveries) + 1}"
        is_dup = (idempotency_key in self.delivered_keys)
        self.delivered_keys[idempotency_key] = self.delivered_keys.get(idempotency_key, 0) + 1

        if force_drop:
            status = "DROPPED"
            del_t = None
        elif force_delay_seconds > 0:
            status = "DELAYED"
            del_t = timestamp + force_delay_seconds
        elif is_dup:
            status = "DUPLICATE"
            del_t = timestamp
        else:
            status = "DELIVERED"
            del_t = timestamp

        d = WebhookDelivery(
            webhook_id=wid,
            event_type=event_type,
            payload=payload,
            idempotency_key=idempotency_key,
            dispatched_at=timestamp,
            delivered_at=del_t,
            status=status
        )
        self.deliveries.append(d)
        return d
