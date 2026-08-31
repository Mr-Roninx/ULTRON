import hashlib
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class WebhookRecord(BaseModel):
    event_id: str
    provider: str
    payload_hash: str
    status: str = "RECEIVED" # RECEIVED, VERIFIED, DUPLICATE, PROCESSING, PROCESSED, FAILED
    received_at: int
    processed_at: Optional[int] = None

class WebhookDeduplicator:
    """
    Guarantees strict idempotency for all incoming provider webhooks.
    """
    def __init__(self):
        self._seen_events: Dict[str, WebhookRecord] = {}

    def is_duplicate(self, provider: str, provider_event_id: str, raw_payload: bytes) -> bool:
        payload_hash = hashlib.sha256(raw_payload).hexdigest()
        key = f"{provider}_{provider_event_id}_{payload_hash}"
        if key in self._seen_events:
            rec = self._seen_events[key]
            rec.status = "DUPLICATE"
            return True
        return False

    def record_received(self, provider: str, provider_event_id: str, raw_payload: bytes, timestamp: int) -> WebhookRecord:
        payload_hash = hashlib.sha256(raw_payload).hexdigest()
        key = f"{provider}_{provider_event_id}_{payload_hash}"
        rec = WebhookRecord(
            event_id=key,
            provider=provider,
            payload_hash=payload_hash,
            status="VERIFIED",
            received_at=timestamp
        )
        self._seen_events[key] = rec
        return rec

    def mark_processed(self, key: str, timestamp: int):
        if key in self._seen_events:
            self._seen_events[key].status = "PROCESSED"
            self._seen_events[key].processed_at = timestamp

webhook_deduplicator = WebhookDeduplicator()
