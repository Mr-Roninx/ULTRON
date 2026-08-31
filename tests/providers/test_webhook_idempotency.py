import pytest
import time
from backend.integrations.webhooks.deduplicator import WebhookDeduplicator

def test_webhook_deduplication():
    dedup = WebhookDeduplicator()
    payload = b'{"event":"payment.captured","id":"evt_123"}'
    now = int(time.time())

    assert dedup.is_duplicate("razorpay", "evt_123", payload) is False
    rec = dedup.record_received("razorpay", "evt_123", payload, now)
    assert rec.status == "VERIFIED"

    # Second arrival of identical payload
    assert dedup.is_duplicate("razorpay", "evt_123", payload) is True
