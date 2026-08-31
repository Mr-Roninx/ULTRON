import hmac
import hashlib
from typing import Dict, Any

class RazorpayWebhookVerifier:
    """
    Verifies Razorpay webhook payloads using HMAC-SHA256 with the shared webhook secret.
    """
    @staticmethod
    def verify_signature(raw_payload: bytes, signature: str, webhook_secret: str) -> bool:
        if not signature or not webhook_secret or not raw_payload:
            return False

        try:
            expected = hmac.new(
                webhook_secret.encode("utf-8"),
                raw_payload,
                hashlib.sha256
            ).hexdigest()
            return hmac.compare_digest(expected, signature)
        except Exception:
            return False
