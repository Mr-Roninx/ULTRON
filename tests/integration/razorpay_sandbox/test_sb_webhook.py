import pytest
import hmac
import hashlib
from backend.providers.razorpay.adapter import RazorpayAdapter

@pytest.mark.sandbox
def test_razorpay_sandbox_webhook():
    adapter = RazorpayAdapter(is_sandbox=True)
    secret = adapter.webhook_secret
    body = b'{"event":"payment_link.paid","payload":{"payment":{"entity":{"id":"pay_sb_paid_01","amount":2470000}}}}'
    sig = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()

    assert adapter.verify_webhook(body, {"x-razorpay-signature": sig}, secret) is True
