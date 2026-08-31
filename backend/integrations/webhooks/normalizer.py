from typing import Dict, Any
from backend.providers.models import CanonicalPaymentEvent
from backend.providers.registry import provider_registry

class CanonicalEventNormalizer:
    """
    Normalizes provider-specific webhook events into canonical ULTRON domain events.
    """
    @staticmethod
    def normalize(provider_name: str, raw_payload: Dict[str, Any]) -> CanonicalPaymentEvent:
        adapter = provider_registry.get_provider(provider_name)
        return adapter.normalize_event(raw_payload)

canonical_normalizer = CanonicalEventNormalizer()
