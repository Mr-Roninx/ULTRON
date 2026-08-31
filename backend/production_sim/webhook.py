import uuid
from typing import Dict, Any, List, Optional
from simulator.clock import clock

class WebhookDeliveryService:
    """
    Simulates webhook event dispatch, network latency, duplicate delivery,
    and out-of-order arrivals in production environments.
    """
    def __init__(self):
        self.delivered_events: List[Dict[str, Any]] = []
        self.seen_event_ids: set = set()

    def dispatch_webhook(
        self,
        event_type: str,
        payload: Dict[str, Any],
        idempotency_key: str,
        delay_seconds: int = 0
    ) -> Dict[str, Any]:
        evt_id = f"evt_{uuid.uuid4().hex[:8]}"
        delivery_record = {
            "event_id": evt_id,
            "event_type": event_type,
            "idempotency_key": idempotency_key,
            "payload": payload,
            "dispatched_at": clock.now(),
            "delivered_at": clock.now() + delay_seconds,
            "is_duplicate": idempotency_key in self.seen_event_ids
        }
        self.seen_event_ids.add(idempotency_key)
        self.delivered_events.append(delivery_record)
        return delivery_record

    def reset(self):
        self.delivered_events.clear()
        self.seen_event_ids.clear()

webhook_service = WebhookDeliveryService()
