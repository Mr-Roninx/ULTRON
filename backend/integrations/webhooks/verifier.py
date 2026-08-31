from typing import Dict, Any
from backend.providers.registry import provider_registry
from backend.providers.errors import WebhookVerificationError

class WebhookVerifierService:
    """
    Validates cryptographic webhook signatures before processing any financial event.
    """
    @staticmethod
    def verify(provider_name: str, raw_payload: bytes, headers: Dict[str, str], secret: str) -> bool:
        if not raw_payload or not headers or not secret:
            raise WebhookVerificationError(f"Missing webhook payload, headers, or secret for '{provider_name}'.")

        adapter = provider_registry.get_provider(provider_name)
        is_valid = adapter.verify_webhook(raw_payload, headers, secret)
        if not is_valid:
            raise WebhookVerificationError(f"Invalid webhook signature for provider '{provider_name}'.")
        return True

webhook_verifier = WebhookVerifierService()
