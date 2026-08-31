import pytest
import hmac
import hashlib
from backend.providers.razorpay.webhook import RazorpayWebhookVerifier

@pytest.mark.fixture
def test_razorpay_raw_body_webhook_signature():
    secret = "rzp_wh_secret_12345"
    raw_payload = b'{"event":"payment_link.paid","entity":"payment_link"}'
    valid_sig = hmac.new(secret.encode("utf-8"), raw_payload, hashlib.sha256).hexdigest()

    assert RazorpayWebhookVerifier.verify_signature(raw_payload, valid_sig, secret) is True
    assert RazorpayWebhookVerifier.verify_signature(raw_payload, "tampered_signature", secret) is False
