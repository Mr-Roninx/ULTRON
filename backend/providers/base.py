from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from backend.providers.models import (
    CanonicalPayment,
    CanonicalPaymentLink,
    CanonicalPaymentEvent,
    CanonicalRefund,
    CanonicalCustomer,
    CanonicalPaymentState
)
from backend.providers.capabilities import ProviderCapabilitySet, ProviderCapability

class PaymentProviderAdapter(ABC):
    """
    Abstract payment provider adapter representing the execution boundary to real external payment systems.
    """
    def __init__(self, provider_name: str, is_sandbox: bool = True):
        self.provider_name = provider_name
        self.is_sandbox = is_sandbox
        self._capabilities = self._init_capabilities()

    @abstractmethod
    def _init_capabilities(self) -> ProviderCapabilitySet:
        pass

    @property
    def capabilities(self) -> ProviderCapabilitySet:
        return self._capabilities

    @abstractmethod
    def get_payment(self, provider_payment_id: str) -> CanonicalPayment:
        pass

    @abstractmethod
    def get_payment_status(self, provider_payment_id: str) -> CanonicalPaymentState:
        pass

    @abstractmethod
    def create_payment_link(
        self,
        internal_payment_id: str,
        amount_minor: int,
        currency: str,
        customer: CanonicalCustomer,
        description: str,
        expiry_seconds: int = 86400
    ) -> CanonicalPaymentLink:
        pass

    @abstractmethod
    def get_payment_link(self, provider_link_id: str) -> CanonicalPaymentLink:
        pass

    @abstractmethod
    def cancel_payment_link(self, provider_link_id: str) -> bool:
        pass

    @abstractmethod
    def refund(self, provider_payment_id: str, amount_minor: int, reason: Optional[str] = None) -> CanonicalRefund:
        pass

    @abstractmethod
    def capture(self, provider_payment_id: str, amount_minor: int) -> CanonicalPayment:
        pass

    @abstractmethod
    def verify_webhook(self, raw_payload: bytes, headers: Dict[str, str], secret: str) -> bool:
        pass

    @abstractmethod
    def normalize_event(self, raw_payload: Dict[str, Any]) -> CanonicalPaymentEvent:
        pass

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        pass
