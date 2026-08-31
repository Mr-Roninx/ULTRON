import pytest
from backend.providers.razorpay.webhook import RazorpayWebhookVerifier

@pytest.mark.fixture
def test_external_event_authenticity_verification():
    secret = "whsec_test_secret_123"
    payload = b'{"event":"payment_link.paid"}'
    import hmac, hashlib
    sig = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()

    assert RazorpayWebhookVerifier.verify_signature(payload, sig, secret) is True
    assert RazorpayWebhookVerifier.verify_signature(payload, "forged_signature", secret) is False
