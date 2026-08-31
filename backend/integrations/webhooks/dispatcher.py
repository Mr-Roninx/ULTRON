from typing import Callable, List
from backend.providers.models import CanonicalPaymentEvent

class WebhookDispatcher:
    """
    Dispatches normalized canonical events to subscribers (Mission Coordinator, Reconciliation, Ledger).
    """
    def __init__(self):
        self._subscribers: List[Callable[[CanonicalPaymentEvent], None]] = []

    def subscribe(self, callback: Callable[[CanonicalPaymentEvent], None]):
        self._subscribers.append(callback)

    def dispatch(self, event: CanonicalPaymentEvent):
        for sub in self._subscribers:
            try:
                sub(event)
            except Exception as e:
                pass

webhook_dispatcher = WebhookDispatcher()
