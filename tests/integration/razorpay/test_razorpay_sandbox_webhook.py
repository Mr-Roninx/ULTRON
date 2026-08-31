import pytest
import hmac
import hashlib
from backend.providers.razorpay.adapter import RazorpayAdapter

@pytest.mark.sandbox
def test_razorpay_sandbox_webhook_processing():
    adapter = RazorpayAdapter(is_sandbox=True)
    secret = adapter.webhook_secret
    raw_body = b'{"event":"payment.captured","payload":{"payment":{"entity":{"id":"pay_sb_101","amount":2470000}}}}'
    sig = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()

    # Webhook verification
    verified = adapter.verify_webhook(raw_body, {"x-razorpay-signature": sig}, secret)
    assert verified is True

    # Normalization
    import json
    evt = adapter.normalize_event(json.loads(raw_body.decode("utf-8")))
    assert evt.event_type == "PAYMENT_SUCCEEDED"
    assert evt.provider_payment_id == "pay_sb_101"
