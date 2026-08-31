import pytest
import hmac
import hashlib
from backend.providers.razorpay.webhook import RazorpayWebhookVerifier

@pytest.mark.fixture
def test_webhook_signature_tamper_detection():
    secret = "rzp_wh_secret_998877"
    body = b'{"event":"payment_link.paid","entity":"payment_link"}'
    valid_sig = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()

    assert RazorpayWebhookVerifier.verify_signature(body, valid_sig, secret) is True
    # Tampered body
    tampered_body = b'{"event":"payment_link.paid","entity":"payment_link","hacked":true}'
    assert RazorpayWebhookVerifier.verify_signature(tampered_body, valid_sig, secret) is False
