from typing import Dict, Any, Optional, List
from backend.providers.base import PaymentProviderAdapter
from backend.providers.errors import ProviderError

class ProviderRegistry:
    """
    Central registry for all active payment provider adapters.
    """
    def __init__(self):
        self._providers: Dict[str, PaymentProviderAdapter] = {}
        self._register_defaults()

    def _register_defaults(self):
        try:
            from backend.providers.razorpay.adapter import RazorpayAdapter
            self.register(RazorpayAdapter())
        except Exception:
            pass

    def register(self, adapter: PaymentProviderAdapter):
        name = adapter.provider_name.lower()
        self._providers[name] = adapter

    def get_provider(self, name: str) -> PaymentProviderAdapter:
        name_lower = name.lower()
        if name_lower not in self._providers:
            raise ProviderError(f"Payment provider '{name}' is not registered in ProviderRegistry.")
        return self._providers[name_lower]

    def list_providers(self) -> List[str]:
        return list(self._providers.keys())

    def has_provider(self, name: str) -> bool:
        return name.lower() in self._providers

provider_registry = ProviderRegistry()
