from typing import Optional, Dict, Any
from backend.providers.registry import provider_registry
from backend.providers.models import CanonicalPayment

class ProviderStateFetcher:
    """
    Directly queries payment provider APIs to obtain external truth for reconciliation.
    """
    @staticmethod
    def fetch_provider_state(provider_name: str, provider_payment_id: str) -> CanonicalPayment:
        adapter = provider_registry.get_provider(provider_name)
        return adapter.get_payment(provider_payment_id)

provider_fetcher = ProviderStateFetcher()
