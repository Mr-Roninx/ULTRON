import pytest
import hmac
import hashlib
from backend.providers.razorpay.webhook import RazorpayWebhookVerifier

def test_razorpay_webhook_verification():
    secret = "rzp_secret_12345"
    payload = b'{"event":"payment.captured","entity":"payment"}'
    valid_sig = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()

    assert RazorpayWebhookVerifier.verify_signature(payload, valid_sig, secret) is True
    assert RazorpayWebhookVerifier.verify_signature(payload, "invalid_sig", secret) is False
