from enum import Enum
from typing import Set, Dict, Any
from pydantic import BaseModel, Field

class ProviderCapability(str, Enum):
    PAYMENT_RETRIEVAL = "PAYMENT_RETRIEVAL"
    PAYMENT_STATUS_QUERY = "PAYMENT_STATUS_QUERY"
    ORDER_RETRIEVAL = "ORDER_RETRIEVAL"
    PAYMENT_LINK_CREATION = "PAYMENT_LINK_CREATION"
    PAYMENT_LINK_RETRIEVAL = "PAYMENT_LINK_RETRIEVAL"
    PAYMENT_LINK_CANCELLATION = "PAYMENT_LINK_CANCELLATION"
    REFUND = "REFUND"
    CAPTURE = "CAPTURE"
    WEBHOOK_VERIFICATION = "WEBHOOK_VERIFICATION"
    DIRECT_RETRY = "DIRECT_RETRY"
    CUSTOMER_RETRIEVAL = "CUSTOMER_RETRIEVAL"

class ProviderCapabilitySet(BaseModel):
    provider_name: str
    capabilities: Set[ProviderCapability] = Field(default_factory=set)

    def supports(self, capability: ProviderCapability) -> bool:
        return capability in self.capabilities

    def require(self, capability: ProviderCapability):
        if not self.supports(capability):
            from backend.providers.errors import UnsupportedCapabilityError
            raise UnsupportedCapabilityError(f"Provider '{self.provider_name}' does not support '{capability.value}'")
