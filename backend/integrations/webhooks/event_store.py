import time
from typing import Dict, List, Optional
from backend.providers.models import CanonicalPaymentEvent

class WebhookEventStore:
    """
    Append-only persistent event store for verified canonical payment events.
    """
    def __init__(self):
        self._events: List[CanonicalPaymentEvent] = []

    def store_event(self, event: CanonicalPaymentEvent) -> CanonicalPaymentEvent:
        self._events.append(event)
        return event

    def get_events_for_payment(self, internal_payment_id: str) -> List[CanonicalPaymentEvent]:
        return [e for e in self._events if e.internal_payment_id == internal_payment_id]

    def get_all_events(self) -> List[CanonicalPaymentEvent]:
        return self._events

webhook_event_store = WebhookEventStore()
