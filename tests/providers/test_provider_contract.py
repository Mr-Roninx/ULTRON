import pytest
from backend.providers.registry import provider_registry
from backend.providers.capabilities import ProviderCapability

def test_provider_registry_and_contracts():
    providers = provider_registry.list_providers()
    assert "razorpay" in providers

    rzp = provider_registry.get_provider("razorpay")
    assert rzp.capabilities.supports(ProviderCapability.PAYMENT_LINK_CREATION) is True
    assert rzp.capabilities.supports(ProviderCapability.REFUND) is True
