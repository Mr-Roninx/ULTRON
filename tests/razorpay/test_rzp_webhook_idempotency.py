import pytest
import time
from backend.integrations.webhooks.deduplicator import WebhookDeduplicator

@pytest.mark.fixture
def test_razorpay_webhook_idempotency():
    dedup = WebhookDeduplicator()
    payload = b'{"event":"payment.failed","id":"evt_rzp_dedup_01"}'
    now = int(time.time())

    assert dedup.is_duplicate("razorpay", "evt_rzp_dedup_01", payload) is False
    rec = dedup.record_received("razorpay", "evt_rzp_dedup_01", payload, now)
    assert rec.status == "VERIFIED"

    # Replay of identical payload
    assert dedup.is_duplicate("razorpay", "evt_rzp_dedup_01", payload) is True
